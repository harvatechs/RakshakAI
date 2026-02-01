"""
RakshakAI - Gemini API Routes
FastAPI endpoints for Gemini-powered features
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from pydantic import BaseModel

from integrations.gemini_client import GeminiClient, get_gemini_client

router = APIRouter(prefix="/api/v1/gemini", tags=["Gemini AI"])


# ==================== REQUEST/RESPONSE MODELS ====================

class AnalyzeRequest(BaseModel):
    transcript: str
    include_entities: bool = True


class AnalyzeResponse(BaseModel):
    is_scam: bool
    threat_score: float
    scam_type: str
    confidence: float
    indicators: List[str]
    urgency_level: str
    financial_requests: List[str]
    red_flags: List[str]
    recommended_action: str
    explanation: str
    entities: Optional[List[Dict]] = None


class BaitRequest(BaseModel):
    scammer_message: str
    persona: str = "confused_senior"
    conversation_history: Optional[List[Dict]] = None


class BaitResponse(BaseModel):
    response_text: str
    persona_used: str
    estimated_delay_ms: int


class OSINTRequest(BaseModel):
    phone: Optional[str] = None
    upi_id: Optional[str] = None


class OSINTResponse(BaseModel):
    phone_data: Optional[Dict] = None
    upi_data: Optional[Dict] = None
    overall_risk_score: float


# ==================== ROUTES ====================

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_transcript(request: AnalyzeRequest):
    """
    Analyze a call transcript for scam indicators using Gemini API
    
    - **transcript**: The conversation text to analyze
    - **include_entities**: Whether to extract financial entities
    
    Returns threat analysis with scores and recommendations
    """
    try:
        client = await get_gemini_client()
        
        # Get scam analysis
        result = await client.analyze_scam_transcript(request.transcript)
        
        # Extract entities if requested
        if request.include_entities:
            entities = await client.extract_entities(request.transcript)
            result["entities"] = entities
        
        return AnalyzeResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/bait", response_model=BaitResponse)
async def generate_bait_response(request: BaitRequest):
    """
    Generate AI bait agent response to scammer message
    
    - **scammer_message**: What the scammer said
    - **persona**: Which persona to use (confused_senior, cautious_professional, trusting_homemaker)
    - **conversation_history**: Previous conversation for context
    
    Returns AI response that wastes scammer's time
    """
    try:
        client = await get_gemini_client()
        
        response_text = await client.generate_bait_response(
            scammer_message=request.scammer_message,
            persona=request.persona,
            conversation_history=request.conversation_history or []
        )
        
        # Simulate human-like delay
        import random
        delay = random.randint(800, 2500)
        
        return BaitResponse(
            response_text=response_text,
            persona_used=request.persona,
            estimated_delay_ms=delay
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bait generation failed: {str(e)}")


@router.post("/bait/stream")
async def stream_bait_response(request: BaitRequest):
    """
    Stream AI bait agent response in real-time
    
    Returns Server-Sent Events (SSE) stream of response chunks
    """
    from fastapi.responses import StreamingResponse
    
    async def generate_stream():
        client = await get_gemini_client()
        
        async for chunk in client.stream_bait_response(
            scammer_message=request.scammer_message,
            persona=request.persona,
            conversation_history=request.conversation_history or []
        ):
            yield f"data: {chunk}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )


@router.post("/extract-entities")
async def extract_entities(request: AnalyzeRequest):
    """
    Extract financial entities from transcript
    
    Returns: UPI IDs, phone numbers, bank accounts, IFSC codes, etc.
    """
    try:
        client = await get_gemini_client()
        
        entities = await client.extract_entities(request.transcript)
        
        return {
            "entities": entities,
            "count": len(entities),
            "types_found": list(set(e.get("type") for e in entities))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Entity extraction failed: {str(e)}")


@router.post("/osint", response_model=OSINTResponse)
async def osint_investigation(request: OSINTRequest):
    """
    Perform OSINT investigation on phone number or UPI ID
    
    - **phone**: Phone number to investigate
    - **upi_id**: UPI ID to investigate
    
    Returns carrier info, location, risk score, and more
    """
    from osint_tools.scammer_osint import get_osint_tool
    
    try:
        osint = await get_osint_tool()
        
        report = await osint.generate_osint_report(
            phone=request.phone,
            upi_id=request.upi_id
        )
        
        return OSINTResponse(
            phone_data=report.get("findings", {}).get("phone"),
            upi_data=report.get("findings", {}).get("upi"),
            overall_risk_score=report.get("overall_risk_score", 0.0)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OSINT investigation failed: {str(e)}")


@router.post("/analyze-scammer-profile")
async def analyze_scammer_profile(
    phone_numbers: List[str],
    upi_ids: List[str],
    transcripts: List[str]
):
    """
    Build comprehensive scammer profile using Gemini
    
    Analyzes patterns, sophistication, and network indicators
    """
    try:
        client = await get_gemini_client()
        
        profile = await client.analyze_scammer_profile(
            phone_numbers=phone_numbers,
            upi_ids=upi_ids,
            transcripts=transcripts
        )
        
        return profile
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile analysis failed: {str(e)}")


@router.get("/health")
async def gemini_health_check():
    """Check Gemini API connectivity"""
    try:
        client = await get_gemini_client()
        
        # Test with simple prompt
        response = await client._generate_content("Say 'OK'")
        
        return {
            "status": "healthy",
            "api_key_configured": bool(client.api_key),
            "model": client.MODEL_NAME,
            "test_response": response.text.strip() if response.text else "No response"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "api_key_configured": False
        }
