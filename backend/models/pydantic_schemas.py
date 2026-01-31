"""
RakshakAI - Pydantic Schemas
Request and response models for API validation.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from pydantic import BaseModel, Field, validator


# ==========================================
# ENUMERATIONS
# ==========================================
class ThreatLevel(str, Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CallStatus(str, Enum):
    INCOMING = "incoming"
    CONNECTED = "connected"
    MONITORING = "monitoring"
    THREAT_DETECTED = "threat_detected"
    AI_HANDOFF = "ai_handoff"
    ENDED = "ended"
    REPORTED = "reported"


class BaitAgentState(str, Enum):
    IDLE = "idle"
    ENGAGING = "engaging"
    EXTRACTING = "extracting"
    TERMINATING = "terminating"
    COMPLETED = "completed"


class EntityType(str, Enum):
    UPI_ID = "upi_id"
    BANK_ACCOUNT = "bank_account"
    PHONE_NUMBER = "phone_number"
    EMAIL = "email"
    AADHAAR = "aadhaar"
    PAN = "pan"
    CREDIT_CARD = "credit_card"
    OTP = "otp"
    NAME = "name"
    LOCATION = "location"


# ==========================================
# BASE MODELS
# ==========================================
class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


# ==========================================
# CALL MANAGEMENT SCHEMAS
# ==========================================
class CallInitiateRequest(BaseModel):
    phone_number: str = Field(..., description="Caller phone number")
    call_id: Optional[str] = None
    device_id: str = Field(..., description="User device identifier")
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator("phone_number")
    def validate_phone(cls, v):
        # Basic phone validation - can be enhanced
        cleaned = "".join(c for c in v if c.isdigit() or c == "+")
        if len(cleaned) < 10:
            raise ValueError("Invalid phone number")
        return cleaned


class CallResponse(BaseModel):
    call_id: str
    status: CallStatus
    started_at: datetime
    threat_level: ThreatLevel = ThreatLevel.SAFE
    threat_score: float = Field(default=0.0, ge=0.0, le=1.0)
    user_id: Optional[str] = None
    device_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class CallEndRequest(BaseModel):
    call_id: str
    ended_reason: Optional[str] = "user_ended"
    duration_seconds: Optional[int] = None


class CallSummary(BaseModel):
    call_id: str
    phone_number: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: int
    threat_level: ThreatLevel
    max_threat_score: float
    was_scam: bool
    ai_engaged: bool
    intelligence_extracted: bool
    entities_found: List[Dict[str, Any]]


# ==========================================
# THREAT ANALYSIS SCHEMAS
# ==========================================
class ThreatAnalysisRequest(BaseModel):
    call_id: str
    transcript: Optional[str] = None
    audio_features: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ThreatAnalysisResponse(BaseResponse):
    call_id: str
    threat_score: float = Field(..., ge=0.0, le=1.0)
    threat_level: ThreatLevel
    confidence: float = Field(..., ge=0.0, le=1.0)
    indicators: List[str] = []
    keywords_detected: List[str] = []
    behavioral_flags: List[str] = []
    recommended_action: str
    
    # Privacy filter: Only include raw audio if threat is significant
    include_audio_evidence: bool = False


class RealTimeThreatUpdate(BaseModel):
    call_id: str
    timestamp: datetime
    threat_score: float
    threat_level: ThreatLevel
    current_transcript: str
    alert_triggered: bool = False


# ==========================================
# AUDIO PROCESSING SCHEMAS
# ==========================================
class AudioChunk(BaseModel):
    call_id: str
    chunk_id: int
    timestamp: datetime
    audio_data: bytes  # Base64 encoded audio
    sample_rate: int = 16000
    channels: int = 1
    encoding: str = "pcm_s16le"
    
    class Config:
        arbitrary_types_allowed = True


class AudioProcessingResult(BaseModel):
    call_id: str
    chunk_id: int
    transcript: Optional[str] = None
    is_speech: bool = False
    speech_duration_ms: int = 0
    processing_time_ms: int = 0


# ==========================================
# BAIT AGENT SCHEMAS
# ==========================================
class BaitAgentHandoffRequest(BaseModel):
    call_id: str
    user_id: Optional[str] = None
    persona: Optional[str] = None
    extraction_enabled: bool = True
    max_duration_seconds: Optional[int] = 1800


class BaitAgentResponse(BaseResponse):
    call_id: str
    agent_state: BaitAgentState
    persona_name: str
    message: Optional[str] = None
    audio_response: Optional[str] = None  # Base64 encoded TTS


class BaitAgentUpdate(BaseModel):
    call_id: str
    timestamp: datetime
    agent_state: BaitAgentState
    current_transcript: str
    scamer_response: Optional[str] = None
    agent_response: Optional[str] = None
    intelligence_extracted: List[Dict[str, Any]] = []
    call_duration_seconds: int


# ==========================================
# INTELLIGENCE EXTRACTION SCHEMAS
# ==========================================
class ExtractedEntity(BaseModel):
    entity_type: EntityType
    value: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    context: Optional[str] = None
    position_in_transcript: Optional[int] = None
    verified: bool = False


class IntelligenceExtractionRequest(BaseModel):
    call_id: str
    transcript: str
    extract_all: bool = True
    entity_types: Optional[List[EntityType]] = None


class IntelligenceExtractionResponse(BaseResponse):
    call_id: str
    entities: List[ExtractedEntity]
    extraction_confidence: float
    fraud_indicators: List[str] = []
    risk_assessment: Optional[str] = None


# ==========================================
# EVIDENCE PACKAGING SCHEMAS
# ==========================================
class EvidencePackageRequest(BaseModel):
    call_id: str
    include_audio: bool = True
    include_transcript: bool = True
    include_intelligence: bool = True
    sign_package: bool = True


class EvidenceSignature(BaseModel):
    algorithm: str = "SHA256"
    hash_value: str
    timestamp: datetime
    signed_by: str


class EvidencePackage(BaseModel):
    package_id: str
    call_id: str
    created_at: datetime
    
    # Call metadata
    phone_number: str
    call_duration_seconds: int
    threat_level: ThreatLevel
    
    # Evidence content
    audio_file_hash: Optional[str] = None
    transcript: Optional[str] = None
    entities: List[ExtractedEntity] = []
    threat_timeline: List[Dict[str, Any]] = []
    
    # Forensic integrity
    signature: Optional[EvidenceSignature] = None
    chain_of_custody: List[Dict[str, Any]] = []
    
    # Law enforcement fields
    case_id: Optional[str] = None
    reported_at: Optional[datetime] = None
    report_status: Optional[str] = None


# ==========================================
# WEBSOCKET SCHEMAS
# ==========================================
class WebSocketMessage(BaseModel):
    type: str  # "audio_chunk", "threat_update", "handoff", "ping", etc.
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AudioStreamMessage(BaseModel):
    call_id: str
    audio_base64: str
    sequence_number: int
    is_final: bool = False


class ThreatAlertMessage(BaseModel):
    call_id: str
    alert_type: str  # "threat_detected", "high_risk", "scam_confirmed"
    threat_score: float
    threat_level: ThreatLevel
    message: str
    recommended_action: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ==========================================
# USER & DEVICE SCHEMAS
# ==========================================
class DeviceRegistration(BaseModel):
    device_id: str
    device_type: str  # "android", "ios"
    push_token: Optional[str] = None
    app_version: str
    os_version: str


class UserPreferences(BaseModel):
    auto_handoff_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    enable_ai_baiting: bool = True
    alert_sounds: bool = True
    vibration_alerts: bool = True
    auto_report_to_authorities: bool = False
    privacy_level: str = "standard"  # "strict", "standard", "permissive"


# ==========================================
# DASHBOARD & ANALYTICS SCHEMAS
# ==========================================
class DashboardStats(BaseModel):
    total_calls_monitored: int
    threats_detected: int
    scams_prevented: int
    ai_engagements: int
    intelligence_packages: int
    average_threat_score: float
    top_scam_types: List[Dict[str, Any]]
    geographic_hotspots: List[Dict[str, Any]]


class ScammerProfile(BaseModel):
    profile_id: str
    phone_numbers: List[str]
    upi_ids: List[str]
    bank_accounts: List[str]
    first_seen: datetime
    last_seen: datetime
    call_count: int
    success_rate: float
    associated_network: Optional[str] = None
    risk_level: ThreatLevel


class SearchQuery(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    entity_types: Optional[List[EntityType]] = None
    date_range: Optional[Dict[str, datetime]] = None
    pagination: PaginationParams = Field(default_factory=PaginationParams)


class SearchResult(BaseResponse):
    results: List[Dict[str, Any]]
    total_count: int
    page: int
    limit: int
