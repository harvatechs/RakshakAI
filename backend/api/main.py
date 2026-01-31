"""
RakshakAI - FastAPI Main Application
Production-grade backend for real-time scam call defense system.
"""

import asyncio
import hashlib
import json
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from fastapi import (
    FastAPI, 
    WebSocket, 
    WebSocketDisconnect, 
    HTTPException, 
    Depends, 
    BackgroundTasks,
    status
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Import core modules
from core.config import settings
from models.pydantic_schemas import (
    CallInitiateRequest,
    CallResponse,
    CallEndRequest,
    CallSummary,
    ThreatAnalysisRequest,
    ThreatAnalysisResponse,
    ThreatLevel,
    CallStatus,
    BaitAgentHandoffRequest,
    BaitAgentResponse,
    BaitAgentState,
    EvidencePackageRequest,
    EvidencePackage,
    DashboardStats,
    WebSocketMessage,
    AudioStreamMessage,
    ThreatAlertMessage,
    RealTimeThreatUpdate
)

# Import services
from services.audio_processor import AudioProcessor
from services.threat_analyzer import ThreatAnalyzer
from services.bait_agent import BaitAgent
from services.intelligence_extractor import IntelligenceExtractor
from services.evidence_packager import EvidencePackager

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("rakshak.api")

# Prometheus metrics
REQUEST_COUNT = Counter(
    'rakshak_requests_total', 
    'Total requests', 
    ['method', 'endpoint', 'status']
)
REQUEST_LATENCY = Histogram(
    'rakshak_request_duration_seconds', 
    'Request latency'
)
WEBSOCKET_CONNECTIONS = Counter(
    'rakshak_websocket_connections_total',
    'Total WebSocket connections',
    ['status']
)
THREATS_DETECTED = Counter(
    'rakshak_threats_detected_total',
    'Total threats detected',
    ['threat_level']
)


class ConnectionManager:
    """Manages WebSocket connections for real-time call monitoring."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.call_sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, call_id: str):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        async with self._lock:
            self.active_connections[call_id] = websocket
            self.call_sessions[call_id] = {
                "connected_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "audio_chunks_received": 0,
                "threat_score": 0.0,
                "status": CallStatus.CONNECTED,
                "ai_handoff": False
            }
        WEBSOCKET_CONNECTIONS.labels(status="connected").inc()
        logger.info("websocket_connected", call_id=call_id)
    
    async def disconnect(self, call_id: str):
        """Remove a WebSocket connection."""
        async with self._lock:
            if call_id in self.active_connections:
                del self.active_connections[call_id]
            if call_id in self.call_sessions:
                del self.call_sessions[call_id]
        WEBSOCKET_CONNECTIONS.labels(status="disconnected").inc()
        logger.info("websocket_disconnected", call_id=call_id)
    
    async def send_message(self, call_id: str, message: Dict[str, Any]):
        """Send a message to a specific connection."""
        if call_id in self.active_connections:
            await self.active_connections[call_id].send_json(message)
    
    async def broadcast_alert(self, alert: ThreatAlertMessage):
        """Broadcast threat alert to all connections monitoring a call."""
        message = {
            "type": "threat_alert",
            "payload": alert.dict()
        }
        await self.send_message(alert.call_id, message)
    
    def get_session(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get session data for a call."""
        return self.call_sessions.get(call_id)
    
    def update_session(self, call_id: str, updates: Dict[str, Any]):
        """Update session data for a call."""
        if call_id in self.call_sessions:
            self.call_sessions[call_id].update(updates)


# Global connection manager
manager = ConnectionManager()

# Service instances
audio_processor: Optional[AudioProcessor] = None
threat_analyzer: Optional[ThreatAnalyzer] = None
bait_agent: Optional[BaitAgent] = None
intelligence_extractor: Optional[IntelligenceExtractor] = None
evidence_packager: Optional[EvidencePackager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    logger.info("rakshak_startup", version="1.0.0", environment=settings.environment)
    
    global audio_processor, threat_analyzer, bait_agent, intelligence_extractor, evidence_packager
    
    # Initialize services
    audio_processor = AudioProcessor()
    threat_analyzer = ThreatAnalyzer()
    bait_agent = BaitAgent()
    intelligence_extractor = IntelligenceExtractor()
    evidence_packager = EvidencePackager()
    
    logger.info("services_initialized")
    
    yield
    
    # Shutdown
    logger.info("rakshak_shutdown")
    
    # Cleanup
    if audio_processor:
        await audio_processor.cleanup()
    if threat_analyzer:
        await threat_analyzer.cleanup()
    if bait_agent:
        await bait_agent.cleanup()


# Create FastAPI application
app = FastAPI(
    title="RakshakAI API",
    description="AI-powered real-time scam call defense system",
    version="1.0.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else ["https://rakshak.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# HEALTH & MONITORING ENDPOINTS
# ==========================================
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for load balancers."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "audio_processor": audio_processor is not None,
            "threat_analyzer": threat_analyzer is not None,
            "bait_agent": bait_agent is not None
        }
    }


@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrics endpoint."""
    return JSONResponse(
        content=generate_latest().decode("utf-8"),
        media_type=CONTENT_TYPE_LATEST
    )


# ==========================================
# CALL MANAGEMENT ENDPOINTS
# ==========================================
@app.post("/api/v1/calls/initiate", response_model=CallResponse, tags=["Calls"])
async def initiate_call(request: CallInitiateRequest):
    """Initialize a new call monitoring session."""
    call_id = request.call_id or str(uuid.uuid4())
    
    logger.info(
        "call_initiated",
        call_id=call_id,
        phone_number=request.phone_number,
        device_id=request.device_id
    )
    
    return CallResponse(
        call_id=call_id,
        status=CallStatus.CONNECTED,
        started_at=datetime.utcnow(),
        threat_level=ThreatLevel.SAFE,
        threat_score=0.0,
        user_id=request.user_id,
        device_id=request.device_id
    )


@app.post("/api/v1/calls/{call_id}/end", response_model=BaseResponse, tags=["Calls"])
async def end_call(call_id: str, request: CallEndRequest):
    """End a call monitoring session."""
    logger.info(
        "call_ended",
        call_id=call_id,
        duration=request.duration_seconds,
        reason=request.ended_reason
    )
    
    # Cleanup session
    await manager.disconnect(call_id)
    
    return BaseResponse(
        success=True,
        message=f"Call {call_id} ended successfully"
    )


@app.get("/api/v1/calls/{call_id}/summary", response_model=CallSummary, tags=["Calls"])
async def get_call_summary(call_id: str):
    """Get summary of a completed call."""
    # This would fetch from database in production
    raise HTTPException(status_code=501, detail="Not yet implemented")


# ==========================================
# THREAT ANALYSIS ENDPOINTS
# ==========================================
@app.post("/api/v1/threat/analyze", response_model=ThreatAnalysisResponse, tags=["Threat"])
async def analyze_threat(request: ThreatAnalysisRequest):
    """Analyze transcript and audio for threat indicators."""
    if not threat_analyzer:
        raise HTTPException(status_code=503, detail="Threat analyzer not available")
    
    start_time = time.time()
    
    # Perform threat analysis
    result = await threat_analyzer.analyze(
        transcript=request.transcript,
        audio_features=request.audio_features
    )
    
    processing_time = time.time() - start_time
    
    # Update metrics
    THREATS_DETECTED.labels(threat_level=result["threat_level"]).inc()
    
    logger.info(
        "threat_analysis_complete",
        call_id=request.call_id,
        threat_score=result["threat_score"],
        threat_level=result["threat_level"],
        processing_time_ms=processing_time * 1000
    )
    
    return ThreatAnalysisResponse(
        call_id=request.call_id,
        threat_score=result["threat_score"],
        threat_level=ThreatLevel(result["threat_level"]),
        confidence=result["confidence"],
        indicators=result.get("indicators", []),
        keywords_detected=result.get("keywords", []),
        behavioral_flags=result.get("behavioral_flags", []),
        recommended_action=result.get("recommended_action", "continue_monitoring"),
        include_audio_evidence=result["threat_score"] > settings.threat_threshold_medium
    )


# ==========================================
# BAIT AGENT ENDPOINTS
# ==========================================
@app.post("/api/v1/bait/handoff", response_model=BaitAgentResponse, tags=["Bait Agent"])
async def handoff_to_bait_agent(
    request: BaitAgentHandoffRequest,
    background_tasks: BackgroundTasks
):
    """Hand off call control to the AI bait agent."""
    if not bait_agent:
        raise HTTPException(status_code=503, detail="Bait agent not available")
    
    logger.info(
        "bait_agent_handoff",
        call_id=request.call_id,
        persona=request.persona or settings.bait_agent_persona
    )
    
    # Update session
    manager.update_session(
        request.call_id,
        {"ai_handoff": True, "status": CallStatus.AI_HANDOFF}
    )
    
    # Start bait agent in background
    background_tasks.add_task(
        bait_agent.start_engagement,
        call_id=request.call_id,
        persona=request.persona,
        extraction_enabled=request.extraction_enabled
    )
    
    return BaitAgentResponse(
        call_id=request.call_id,
        agent_state=BaitAgentState.ENGAGING,
        persona_name=settings.bait_agent_name,
        message="AI agent is taking over the call. Please remain silent."
    )


@app.post("/api/v1/bait/{call_id}/terminate", response_model=BaitAgentResponse, tags=["Bait Agent"])
async def terminate_bait_agent(call_id: str):
    """Terminate the bait agent and return control to user."""
    if bait_agent:
        await bait_agent.terminate_engagement(call_id)
    
    manager.update_session(call_id, {"ai_handoff": False})
    
    return BaitAgentResponse(
        call_id=call_id,
        agent_state=BaitAgentState.COMPLETED,
        persona_name=settings.bait_agent_name,
        message="AI agent has been terminated. You have control of the call."
    )


# ==========================================
# INTELLIGENCE & EVIDENCE ENDPOINTS
# ==========================================
@app.post("/api/v1/evidence/package", response_model=EvidencePackage, tags=["Evidence"])
async def create_evidence_package(request: EvidencePackageRequest):
    """Create a forensic evidence package for law enforcement."""
    if not evidence_packager:
        raise HTTPException(status_code=503, detail="Evidence packager not available")
    
    logger.info(
        "evidence_package_requested",
        call_id=request.call_id,
        include_audio=request.include_audio
    )
    
    package = await evidence_packager.create_package(
        call_id=request.call_id,
        include_audio=request.include_audio,
        include_transcript=request.include_transcript,
        include_intelligence=request.include_intelligence,
        sign_package=request.sign_package
    )
    
    return package


@app.get("/api/v1/dashboard/stats", response_model=DashboardStats, tags=["Dashboard"])
async def get_dashboard_stats():
    """Get statistics for the law enforcement dashboard."""
    # This would aggregate from database in production
    return DashboardStats(
        total_calls_monitored=0,
        threats_detected=0,
        scams_prevented=0,
        ai_engagements=0,
        intelligence_packages=0,
        average_threat_score=0.0,
        top_scam_types=[],
        geographic_hotspots=[]
    )


# ==========================================
# WEBSOCKET ENDPOINT - REAL-TIME AUDIO STREAMING
# ==========================================
@app.websocket("/ws/call/{call_id}")
async def websocket_endpoint(websocket: WebSocket, call_id: str):
    """
    WebSocket endpoint for real-time bidirectional audio streaming.
    
    This is the core endpoint that:
    1. Receives audio chunks from the mobile app
    2. Performs VAD (Voice Activity Detection)
    3. Routes audio to the Threat Engine
    4. If "Hand Off" is active, routes audio to OpenAI Realtime API
    5. Sends threat alerts and AI responses back to the client
    """
    await manager.connect(websocket, call_id)
    
    try:
        while True:
            # Receive message from client
            message = await websocket.receive_json()
            msg_type = message.get("type")
            payload = message.get("payload", {})
            
            if msg_type == "audio_chunk":
                # Process audio chunk
                await handle_audio_chunk(call_id, payload, websocket)
                
            elif msg_type == "handoff_request":
                # Handle handoff to AI agent
                await handle_handoff_request(call_id, payload, websocket)
                
            elif msg_type == "terminate_bait":
                # Terminate bait agent
                await handle_terminate_bait(call_id, websocket)
                
            elif msg_type == "ping":
                # Keep-alive ping
                await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})
                
            else:
                logger.warning("unknown_websocket_message_type", type=msg_type, call_id=call_id)
                
    except WebSocketDisconnect:
        logger.info("websocket_client_disconnected", call_id=call_id)
        await manager.disconnect(call_id)
    except Exception as e:
        logger.error("websocket_error", call_id=call_id, error=str(e))
        await manager.disconnect(call_id)
        raise


async def handle_audio_chunk(call_id: str, payload: Dict[str, Any], websocket: WebSocket):
    """
    Process incoming audio chunk from mobile app.
    
    PRIVACY FILTER: Audio is only processed and stored if threat score exceeds threshold.
    Low-risk audio chunks are discarded after processing.
    """
    session = manager.get_session(call_id)
    if not session:
        return
    
    try:
        # Decode audio data
        audio_data = payload.get("audio_data", "")
        sequence = payload.get("sequence_number", 0)
        
        # Step 1: Voice Activity Detection
        vad_result = await audio_processor.detect_voice_activity(audio_data)
        
        if not vad_result["is_speech"]:
            # No speech detected, skip processing
            return
        
        # Step 2: Speech-to-Text (if speech detected)
        transcript = await audio_processor.transcribe(audio_data)
        
        # Step 3: Check if AI handoff is active
        if session.get("ai_handoff") and bait_agent:
            # Route to OpenAI Realtime API
            ai_response = await bait_agent.process_caller_input(
                call_id=call_id,
                transcript=transcript
            )
            
            # Send AI response back to client
            await websocket.send_json({
                "type": "ai_response",
                "payload": {
                    "call_id": call_id,
                    "response_text": ai_response.get("text"),
                    "response_audio": ai_response.get("audio_base64"),
                    "intelligence_extracted": ai_response.get("intelligence", [])
                }
            })
            return
        
        # Step 4: Threat Analysis (only if not in handoff mode)
        threat_result = await threat_analyzer.analyze_realtime(
            call_id=call_id,
            transcript=transcript,
            audio_features=vad_result.get("features")
        )
        
        # Update session with threat score
        manager.update_session(call_id, {
            "threat_score": threat_result["threat_score"],
            "status": CallStatus.THREAT_DETECTED if threat_result["threat_score"] > settings.threat_threshold_medium else CallStatus.MONITORING
        })
        
        # Step 5: Send threat update to client
        threat_update = RealTimeThreatUpdate(
            call_id=call_id,
            timestamp=datetime.utcnow(),
            threat_score=threat_result["threat_score"],
            threat_level=ThreatLevel(threat_result["threat_level"]),
            current_transcript=transcript,
            alert_triggered=threat_result["threat_score"] > settings.threat_threshold_high
        )
        
        await websocket.send_json({
            "type": "threat_update",
            "payload": threat_update.dict()
        })
        
        # Step 6: Trigger high-threat alert if threshold exceeded
        if threat_result["threat_score"] > settings.threat_threshold_high:
            alert = ThreatAlertMessage(
                call_id=call_id,
                alert_type="high_risk",
                threat_score=threat_result["threat_score"],
                threat_level=ThreatLevel.HIGH,
                message="High-risk scam pattern detected!",
                recommended_action="handoff_to_ai"
            )
            await manager.broadcast_alert(alert)
        
        # PRIVACY FILTER: Only store audio if threat is significant
        if threat_result["threat_score"] > settings.threat_threshold_low:
            # Store for evidence (encrypted)
            await audio_processor.store_audio_chunk(
                call_id=call_id,
                sequence=sequence,
                audio_data=audio_data,
                transcript=transcript,
                threat_score=threat_result["threat_score"]
            )
        
    except Exception as e:
        logger.error("audio_chunk_processing_error", call_id=call_id, error=str(e))
        await websocket.send_json({
            "type": "error",
            "payload": {"message": "Failed to process audio chunk", "error": str(e)}
        })


async def handle_handoff_request(call_id: str, payload: Dict[str, Any], websocket: WebSocket):
    """Handle request to hand off call to AI bait agent."""
    logger.info("handoff_request_received", call_id=call_id)
    
    # Update session
    manager.update_session(call_id, {
        "ai_handoff": True,
        "status": CallStatus.AI_HANDOFF
    })
    
    # Initialize bait agent
    if bait_agent:
        await bait_agent.start_engagement(
            call_id=call_id,
            persona=payload.get("persona"),
            extraction_enabled=payload.get("extraction_enabled", True)
        )
    
    # Confirm handoff to client
    await websocket.send_json({
        "type": "handoff_confirmed",
        "payload": {
            "call_id": call_id,
            "agent_name": settings.bait_agent_name,
            "message": "AI agent is now handling the call. Please remain silent."
        }
    })


async def handle_terminate_bait(call_id: str, websocket: WebSocket):
    """Handle request to terminate bait agent."""
    logger.info("terminate_bait_request", call_id=call_id)
    
    if bait_agent:
        await bait_agent.terminate_engagement(call_id)
    
    manager.update_session(call_id, {
        "ai_handoff": False,
        "status": CallStatus.MONITORING
    })
    
    await websocket.send_json({
        "type": "bait_terminated",
        "payload": {
            "call_id": call_id,
            "message": "AI agent terminated. You have control of the call."
        }
    })


# ==========================================
# ERROR HANDLERS
# ==========================================
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.error(
        "http_exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.exception("unexpected_error", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "error": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        workers=1 if settings.is_development else 4
    )
