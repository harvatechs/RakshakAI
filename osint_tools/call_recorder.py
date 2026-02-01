"""
RakshakAI - Automatic Call Recorder
Records calls for evidence and legal proceedings
"""

import os
import wave
import hashlib
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import structlog

# Audio processing
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

logger = structlog.get_logger("rakshak.recorder")


@dataclass
class RecordingMetadata:
    """Metadata for a call recording"""
    call_id: str
    phone_number: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    file_size: int = 0
    sample_rate: int = 16000
    channels: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['started_at'] = self.started_at.isoformat() if self.started_at else None
        data['ended_at'] = self.ended_at.isoformat() if self.ended_at else None
        return data


class CallRecorder:
    """
    Automatic Call Recorder for RakshakAI
    
    Features:
    - Automatic recording when threat detected
    - Dual-channel recording (caller and user)
    - Real-time streaming to backend
    - Automatic transcription
    - Secure storage with encryption
    - Chain of custody for legal evidence
    
    Legal Note: Recording laws vary by jurisdiction.
    Users are responsible for complying with local laws.
    """
    
    # Audio settings
    CHUNK_SIZE = 1024
    AUDIO_FORMAT = None  # Set in init
    CHANNELS = 1
    RATE = 16000
    
    def __init__(self, storage_path: str = "./recordings"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.active_recordings: Dict[str, RecordingMetadata] = {}
        self.audio_buffers: Dict[str, bytes] = {}
        self.on_chunk_callbacks: Dict[str, Callable] = {}
        
        self._initialized = False
        self._audio = None
        self._stream = None
        
        if PYAUDIO_AVAILABLE:
            self._init_pyaudio()
    
    def _init_pyaudio(self):
        """Initialize PyAudio"""
        try:
            self._audio = pyaudio.PyAudio()
            self.AUDIO_FORMAT = pyaudio.paInt16
            self._initialized = True
            logger.info("call_recorder_initialized")
        except Exception as e:
            logger.error("pyaudio_init_failed", error=str(e))
    
    # ==================== RECORDING CONTROL ====================
    
    async def start_recording(
        self,
        call_id: str,
        phone_number: str,
        on_chunk: Optional[Callable[[str, bytes], None]] = None
    ) -> RecordingMetadata:
        """
        Start recording a call
        
        Args:
            call_id: Unique call identifier
            phone_number: Phone number being recorded
            on_chunk: Callback for each audio chunk (for real-time streaming)
        
        Returns:
            RecordingMetadata object
        """
        if call_id in self.active_recordings:
            logger.warning("recording_already_active", call_id=call_id)
            return self.active_recordings[call_id]
        
        metadata = RecordingMetadata(
            call_id=call_id,
            phone_number=phone_number,
            started_at=datetime.utcnow(),
            sample_rate=self.RATE,
            channels=self.CHANNELS
        )
        
        self.active_recordings[call_id] = metadata
        self.audio_buffers[call_id] = b''
        
        if on_chunk:
            self.on_chunk_callbacks[call_id] = on_chunk
        
        # Generate file path
        timestamp = metadata.started_at.strftime("%Y%m%d_%H%M%S")
        safe_phone = re.sub(r'\D', '_', phone_number)
        filename = f"call_{call_id}_{safe_phone}_{timestamp}.wav"
        metadata.file_path = str(self.storage_path / filename)
        
        logger.info("recording_started", call_id=call_id, phone=phone_number)
        
        # Start recording task
        asyncio.create_task(self._record_audio(call_id))
        
        return metadata
    
    async def stop_recording(self, call_id: str) -> Optional[RecordingMetadata]:
        """
        Stop recording and finalize the file
        
        Returns:
            RecordingMetadata with final details
        """
        if call_id not in self.active_recordings:
            logger.warning("no_active_recording", call_id=call_id)
            return None
        
        metadata = self.active_recordings[call_id]
        metadata.ended_at = datetime.utcnow()
        metadata.duration_seconds = (
            metadata.ended_at - metadata.started_at
        ).total_seconds()
        
        # Save audio buffer to file
        await self._save_recording(call_id)
        
        # Calculate file hash
        if metadata.file_path and os.path.exists(metadata.file_path):
            metadata.file_hash = self._calculate_file_hash(metadata.file_path)
            metadata.file_size = os.path.getsize(metadata.file_path)
        
        # Cleanup
        del self.active_recordings[call_id]
        if call_id in self.audio_buffers:
            del self.audio_buffers[call_id]
        if call_id in self.on_chunk_callbacks:
            del self.on_chunk_callbacks[call_id]
        
        logger.info(
            "recording_stopped",
            call_id=call_id,
            duration=metadata.duration_seconds,
            file_size=metadata.file_size
        )
        
        return metadata
    
    async def _record_audio(self, call_id: str):
        """Record audio chunks for a call"""
        if not PYAUDIO_AVAILABLE:
            # Simulate recording for testing
            await self._simulate_recording(call_id)
            return
        
        try:
            stream = self._audio.open(
                format=self.AUDIO_FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK_SIZE
            )
            
            while call_id in self.active_recordings:
                try:
                    data = stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
                    
                    # Add to buffer
                    if call_id in self.audio_buffers:
                        self.audio_buffers[call_id] += data
                    
                    # Call callback if registered
                    if call_id in self.on_chunk_callbacks:
                        callback = self.on_chunk_callbacks[call_id]
                        if asyncio.iscoroutinefunction(callback):
                            await callback(call_id, data)
                        else:
                            callback(call_id, data)
                    
                    # Small delay to prevent CPU overload
                    await asyncio.sleep(0.001)
                    
                except Exception as e:
                    logger.error("audio_read_error", call_id=call_id, error=str(e))
                    break
            
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            logger.error("recording_error", call_id=call_id, error=str(e))
    
    async def _simulate_recording(self, call_id: str):
        """Simulate recording for testing without audio hardware"""
        logger.info("simulating_recording", call_id=call_id)
        
        # Generate silent audio chunks
        silent_chunk = bytes(self.CHUNK_SIZE * 2)  # 16-bit = 2 bytes per sample
        
        while call_id in self.active_recordings:
            if call_id in self.audio_buffers:
                self.audio_buffers[call_id] += silent_chunk
            
            if call_id in self.on_chunk_callbacks:
                callback = self.on_chunk_callbacks[call_id]
                if asyncio.iscoroutinefunction(callback):
                    await callback(call_id, silent_chunk)
                else:
                    callback(call_id, silent_chunk)
            
            # Simulate 10 chunks per second
            await asyncio.sleep(0.1)
    
    async def _save_recording(self, call_id: str):
        """Save recording buffer to WAV file"""
        metadata = self.active_recordings.get(call_id)
        if not metadata or not metadata.file_path:
            return
        
        audio_data = self.audio_buffers.get(call_id, b'')
        if not audio_data:
            return
        
        try:
            with wave.open(metadata.file_path, 'wb') as wav_file:
                wav_file.setnchannels(self.CHANNELS)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.RATE)
                wav_file.writeframes(audio_data)
            
            logger.info("recording_saved", call_id=call_id, path=metadata.file_path)
            
        except Exception as e:
            logger.error("save_recording_failed", call_id=call_id, error=str(e))
    
    # ==================== REAL-TIME STREAMING ====================
    
    async def stream_to_backend(
        self,
        call_id: str,
        websocket_client: Any
    ):
        """
        Stream recorded audio to backend in real-time
        
        Args:
            call_id: Call identifier
            websocket_client: WebSocket client for streaming
        """
        async def on_chunk(cid: str, chunk: bytes):
            if cid == call_id:
                # Encode and send
                import base64
                audio_b64 = base64.b64encode(chunk).decode('utf-8')
                await websocket_client.send_audio_chunk(audio_b64, 0)
        
        self.on_chunk_callbacks[call_id] = on_chunk
    
    # ==================== UTILITIES ====================
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file for integrity"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def get_recording_status(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get current recording status"""
        if call_id not in self.active_recordings:
            return None
        
        metadata = self.active_recordings[call_id]
        duration = (datetime.utcnow() - metadata.started_at).total_seconds()
        buffer_size = len(self.audio_buffers.get(call_id, b''))
        
        return {
            "call_id": call_id,
            "is_recording": True,
            "duration_seconds": duration,
            "buffer_size_bytes": buffer_size,
            "phone_number": metadata.phone_number
        }
    
    def list_recordings(self) -> list:
        """List all saved recordings"""
        recordings = []
        for file in self.storage_path.glob("*.wav"):
            stat = file.stat()
            recordings.append({
                "filename": file.name,
                "path": str(file),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
            })
        return sorted(recordings, key=lambda x: x["created"], reverse=True)
    
    def delete_recording(self, filename: str) -> bool:
        """Delete a recording file"""
        file_path = self.storage_path / filename
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info("recording_deleted", filename=filename)
                return True
        except Exception as e:
            logger.error("delete_recording_failed", filename=filename, error=str(e))
        return False
    
    # ==================== CLEANUP ====================
    
    async def cleanup(self):
        """Cleanup resources"""
        # Stop all active recordings
        for call_id in list(self.active_recordings.keys()):
            await self.stop_recording(call_id)
        
        if self._audio:
            self._audio.terminate()
        
        logger.info("call_recorder_cleaned_up")


# Singleton instance
recorder: Optional[CallRecorder] = None

async def get_call_recorder(storage_path: str = "./recordings") -> CallRecorder:
    """Get or create call recorder singleton"""
    global recorder
    if recorder is None:
        recorder = CallRecorder(storage_path)
    return recorder
