"""
RakshakAI - Configuration Management
Centralized configuration with environment variable support and validation.
"""

import os
from functools import lru_cache
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable loading."""
    
    # ==========================================
    # APPLICATION SETTINGS
    # ==========================================
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    secret_key: str = Field(default="change-me-in-production", env="SECRET_KEY")
    api_version: str = Field(default="v1", env="API_VERSION")
    
    # ==========================================
    # OPENAI CONFIGURATION
    # ==========================================
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_org_id: Optional[str] = Field(default=None, env="OPENAI_ORG_ID")
    openai_realtime_model: str = Field(
        default="gpt-4o-realtime-preview-2024-10-01", 
        env="OPENAI_REALTIME_MODEL"
    )
    openai_whisper_model: str = Field(default="whisper-1", env="OPENAI_WHISPER_MODEL")
    
    # ==========================================
    # TWILIO CONFIGURATION
    # ==========================================
    twilio_account_sid: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    twilio_phone_number: Optional[str] = Field(default=None, env="TWILIO_PHONE_NUMBER")
    twilio_webhook_url: Optional[str] = Field(default=None, env="TWILIO_WEBHOOK_URL")
    
    # ==========================================
    # ELEVENLABS CONFIGURATION
    # ==========================================
    elevenlabs_api_key: Optional[str] = Field(default=None, env="ELEVENLABS_API_KEY")
    elevenlabs_voice_id: Optional[str] = Field(default=None, env="ELEVENLABS_VOICE_ID")
    
    # ==========================================
    # DATABASE CONFIGURATION
    # ==========================================
    postgres_user: str = Field(default="rakshak", env="POSTGRES_USER")
    postgres_password: str = Field(default="rakshak", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="rakshak_db", env="POSTGRES_DB")
    database_url: str = Field(
        default="postgresql://rakshak:rakshak@localhost:5432/rakshak_db",
        env="DATABASE_URL"
    )
    
    # ==========================================
    # REDIS CONFIGURATION
    # ==========================================
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # ==========================================
    # MILVUS CONFIGURATION
    # ==========================================
    milvus_host: str = Field(default="localhost", env="MILVUS_HOST")
    milvus_port: int = Field(default=19530, env="MILVUS_PORT")
    milvus_collection: str = Field(default="call_embeddings", env="MILVUS_COLLECTION")
    
    # ==========================================
    # SECURITY SETTINGS
    # ==========================================
    jwt_secret_key: str = Field(default="your-secret-key", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    encryption_key: Optional[str] = Field(default=None, env="ENCRYPTION_KEY")
    
    # ==========================================
    # AUDIO PROCESSING
    # ==========================================
    audio_sample_rate: int = Field(default=16000, env="AUDIO_SAMPLE_RATE")
    audio_chunk_size: int = Field(default=1024, env="AUDIO_CHUNK_SIZE")
    vad_aggressiveness: int = Field(default=3, env="VAD_AGGRESSIVENESS")
    max_audio_duration: int = Field(default=3600, env="MAX_AUDIO_DURATION")
    
    # ==========================================
    # ML MODEL SETTINGS
    # ==========================================
    model_path: str = Field(default="./ml_pipeline/saved_models", env="MODEL_PATH")
    threat_threshold_low: float = Field(default=0.3, env="THREAT_THRESHOLD_LOW")
    threat_threshold_medium: float = Field(default=0.6, env="THREAT_THRESHOLD_MEDIUM")
    threat_threshold_high: float = Field(default=0.85, env="THREAT_THRESHOLD_HIGH")
    enable_on_device_ml: bool = Field(default=True, env="ENABLE_ON_DEVICE_ML")
    
    # ==========================================
    # BAIT AGENT SETTINGS
    # ==========================================
    bait_agent_name: str = Field(default="Ramesh Kumar", env="BAIT_AGENT_NAME")
    bait_agent_persona: str = Field(default="confused_senior", env="BAIT_AGENT_PERSONA")
    max_bait_duration: int = Field(default=1800, env="MAX_BAIT_DURATION")
    intelligence_extraction_enabled: bool = Field(
        default=True, 
        env="INTELLIGENCE_EXTRACTION_ENABLED"
    )
    
    # ==========================================
    # LAW ENFORCEMENT INTEGRATION
    # ==========================================
    law_enforcement_api_url: Optional[str] = Field(
        default=None, 
        env="LAW_ENFORCEMENT_API_URL"
    )
    law_enforcement_api_key: Optional[str] = Field(
        default=None, 
        env="LAW_ENFORCEMENT_API_KEY"
    )
    auto_report_threshold: float = Field(default=0.95, env="AUTO_REPORT_THRESHOLD")
    
    # ==========================================
    # MONITORING & ANALYTICS
    # ==========================================
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    grafana_password: str = Field(default="admin", env="GRAFANA_PASSWORD")
    
    # ==========================================
    # RATE LIMITING
    # ==========================================
    rate_limit_calls_per_minute: int = Field(
        default=60, 
        env="RATE_LIMIT_CALLS_PER_MINUTE"
    )
    rate_limit_websocket_connections: int = Field(
        default=10, 
        env="RATE_LIMIT_WEBSOCKET_CONNECTIONS"
    )
    
    # ==========================================
    # PRIVACY SETTINGS
    # ==========================================
    audio_retention_days: int = Field(default=30, env="AUDIO_RETENTION_DAYS")
    enable_audio_encryption: bool = Field(default=True, env="ENABLE_AUDIO_ENCRYPTION")
    gdpr_compliance_mode: bool = Field(default=True, env="GDPR_COMPLIANCE_MODE")
    anonymize_personal_data: bool = Field(default=True, env="ANONYMIZE_PERSONAL_DATA")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"
    
    @validator("environment")
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production"]
        if v.lower() not in allowed:
            raise ValueError(f"environment must be one of {allowed}")
        return v.lower()
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def threat_thresholds(self) -> dict:
        return {
            "low": self.threat_threshold_low,
            "medium": self.threat_threshold_medium,
            "high": self.threat_threshold_high
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
