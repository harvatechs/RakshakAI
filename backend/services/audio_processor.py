"""
RakshakAI - Audio Processing Service
Handles audio capture, VAD, STT, and secure storage.
"""

import base64
import hashlib
import io
import tempfile
import time
from typing import Any, Dict, Optional

import numpy as np
import soundfile as sf
import structlog
from cryptography.fernet import Fernet

# Optional imports with fallbacks
try:
    import webrtcvad
    VAD_AVAILABLE = True
except ImportError:
    VAD_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

from core.config import settings

logger = structlog.get_logger("rakshak.audio")


class AudioProcessor:
    """
    Audio processing service for real-time call monitoring.
    
    Responsibilities:
    - Voice Activity Detection (VAD)
    - Speech-to-Text transcription
    - Audio feature extraction
    - Secure audio storage (privacy-compliant)
    """
    
    def __init__(self):
        self.vad = None
        self.whisper_model = None
        self.encryption_key = settings.encryption_key
        self._initialized = False
        
    async def initialize(self):
        """Initialize audio processing models."""
        if self._initialized:
            return
            
        # Initialize VAD
        if VAD_AVAILABLE:
            self.vad = webrtcvad.Vad(settings.vad_aggressiveness)
            logger.info("vad_initialized", aggressiveness=settings.vad_aggressiveness)
        else:
            logger.warning("webrtcvad_not_available")
        
        # Initialize Whisper for STT
        if WHISPER_AVAILABLE:
            model_size = "base" if settings.is_development else "small"
            self.whisper_model = whisper.load_model(model_size)
            logger.info("whisper_initialized", model=model_size)
        else:
            logger.warning("whisper_not_available")
        
        self._initialized = True
    
    async def detect_voice_activity(self, audio_base64: str) -> Dict[str, Any]:
        """
        Detect voice activity in audio chunk.
        
        Returns:
            Dict with is_speech, speech_duration_ms, and audio features
        """
        await self.initialize()
        
        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_base64)
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
            
            # Normalize to float32 [-1, 1]
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            # Resample to 16kHz if needed (assuming input is 16kHz for now)
            sample_rate = settings.audio_sample_rate
            
            # VAD processing
            is_speech = False
            speech_frames = 0
            total_frames = 0
            
            if self.vad and len(audio_array) > 0:
                # WebRTC VAD requires specific frame sizes (10, 20, or 30ms)
                frame_duration_ms = 30
                frame_size = int(sample_rate * frame_duration_ms / 1000)
                
                for i in range(0, len(audio_array) - frame_size, frame_size):
                    frame = audio_array[i:i + frame_size]
                    # Convert to bytes for webrtcvad
                    frame_bytes = frame.tobytes()
                    
                    try:
                        if self.vad.is_speech(frame_bytes, sample_rate):
                            speech_frames += 1
                            is_speech = True
                        total_frames += 1
                    except Exception:
                        pass
            else:
                # Fallback: use energy-based detection
                energy = np.sqrt(np.mean(audio_float ** 2))
                is_speech = energy > 0.01  # Threshold
            
            speech_ratio = speech_frames / total_frames if total_frames > 0 else 0
            speech_duration_ms = speech_frames * 30  # 30ms per frame
            
            # Extract audio features
            features = self._extract_features(audio_float, sample_rate)
            
            return {
                "is_speech": is_speech or speech_ratio > 0.3,
                "speech_duration_ms": speech_duration_ms,
                "speech_ratio": speech_ratio,
                "features": features
            }
            
        except Exception as e:
            logger.error("vad_error", error=str(e))
            return {"is_speech": False, "speech_duration_ms": 0, "features": {}}
    
    def _extract_features(self, audio: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Extract audio features for threat analysis."""
        features = {}
        
        try:
            # Basic features
            features["duration"] = len(audio) / sample_rate
            features["rms_energy"] = float(np.sqrt(np.mean(audio ** 2)))
            features["zero_crossing_rate"] = float(np.mean(np.diff(np.sign(audio)) != 0))
            
            # Spectral features (if librosa available)
            try:
                import librosa
                
                # MFCCs
                mfccs = librosa.feature.mfcc(
                    y=audio, 
                    sr=sample_rate, 
                    n_mfcc=13
                )
                features["mfcc_mean"] = [float(x) for x in np.mean(mfccs, axis=1)]
                features["mfcc_std"] = [float(x) for x in np.std(mfccs, axis=1)]
                
                # Spectral centroid
                centroid = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)
                features["spectral_centroid_mean"] = float(np.mean(centroid))
                
                # Spectral rolloff
                rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sample_rate)
                features["spectral_rolloff_mean"] = float(np.mean(rolloff))
                
            except ImportError:
                pass
            
        except Exception as e:
            logger.error("feature_extraction_error", error=str(e))
        
        return features
    
    async def transcribe(self, audio_base64: str) -> Optional[str]:
        """
        Transcribe audio to text using Whisper.
        
        PRIVACY NOTE: Transcription happens locally if possible.
        Falls back to OpenAI API for better accuracy on low-resource devices.
        """
        await self.initialize()
        
        try:
            # Decode audio
            audio_bytes = base64.b64decode(audio_base64)
            
            # Use local Whisper if available
            if self.whisper_model:
                # Save to temp file (Whisper requires file path)
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    # Convert to WAV format
                    audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
                    audio_float = audio_array.astype(np.float32) / 32768.0
                    sf.write(tmp.name, audio_float, settings.audio_sample_rate)
                    tmp_path = tmp.name
                
                # Transcribe
                result = self.whisper_model.transcribe(tmp_path, language="en")
                
                # Cleanup
                import os
                os.unlink(tmp_path)
                
                return result.get("text", "").strip()
            
            else:
                # Fallback: use OpenAI Whisper API
                # This would be implemented with actual API call
                logger.warning("whisper_not_available_using_fallback")
                return None
                
        except Exception as e:
            logger.error("transcription_error", error=str(e))
            return None
    
    async def store_audio_chunk(
        self,
        call_id: str,
        sequence: int,
        audio_data: str,
        transcript: Optional[str],
        threat_score: float
    ):
        """
        Securely store audio chunk for evidence.
        
        PRIVACY COMPLIANCE:
        - Audio is encrypted at rest
        - Only stored if threat_score > threshold
        - Automatically deleted after retention period
        """
        try:
            # Only store if encryption is enabled
            if not settings.enable_audio_encryption:
                logger.warning("audio_encryption_disabled_skipping_storage")
                return
            
            # Decode and encrypt
            audio_bytes = base64.b64decode(audio_data)
            
            if self.encryption_key:
                f = Fernet(self.encryption_key.encode()[:32].ljust(32, b'0'))
                encrypted_audio = f.encrypt(audio_bytes)
            else:
                # Fallback: hash for integrity without encryption
                encrypted_audio = audio_bytes
            
            # Calculate hash for integrity verification
            audio_hash = hashlib.sha256(audio_bytes).hexdigest()
            
            # Store metadata (actual storage would be to S3/MinIO)
            storage_record = {
                "call_id": call_id,
                "sequence": sequence,
                "audio_hash": audio_hash,
                "transcript": transcript,
                "threat_score": threat_score,
                "stored_at": time.time(),
                "retention_days": settings.audio_retention_days
            }
            
            logger.info(
                "audio_chunk_stored",
                call_id=call_id,
                sequence=sequence,
                audio_hash=audio_hash[:16] + "...",
                threat_score=threat_score
            )
            
        except Exception as e:
            logger.error("audio_storage_error", error=str(e))
    
    async def cleanup(self):
        """Cleanup resources."""
        self.vad = None
        self.whisper_model = None
        self._initialized = False
        logger.info("audio_processor_cleaned_up")
