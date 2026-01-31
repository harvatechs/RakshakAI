"""
RakshakAI - Evidence Packager Service
Creates forensic evidence packages for law enforcement with chain of custody.
"""

import hashlib
import json
import time
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict

import structlog

from core.config import settings
from models.pydantic_schemas import EvidencePackage, EvidenceSignature, ExtractedEntity

logger = structlog.get_logger("rakshak.evidence")


@dataclass
class ChainOfCustodyEntry:
    """Single entry in the chain of custody."""
    timestamp: str
    action: str
    actor: str
    description: str
    hash_before: Optional[str] = None
    hash_after: Optional[str] = None


class EvidencePackager:
    """
    Creates forensic evidence packages for law enforcement.
    
    Features:
    - Cryptographic hashing for integrity
    - Chain of custody tracking
    - Digital signatures
    - Standardized format for legal proceedings
    """
    
    def __init__(self):
        self._initialized = False
    
    async def initialize(self):
        """Initialize the evidence packager."""
        if self._initialized:
            return
        
        self._initialized = True
        logger.info("evidence_packager_initialized")
    
    async def create_package(
        self,
        call_id: str,
        include_audio: bool = True,
        include_transcript: bool = True,
        include_intelligence: bool = True,
        sign_package: bool = True
    ) -> EvidencePackage:
        """
        Create a forensic evidence package.
        
        Args:
            call_id: Unique call identifier
            include_audio: Whether to include audio evidence
            include_transcript: Whether to include transcript
            include_intelligence: Whether to include extracted intelligence
            sign_package: Whether to cryptographically sign the package
        
        Returns:
            EvidencePackage with all forensic data
        """
        await self.initialize()
        
        logger.info(
            "creating_evidence_package",
            call_id=call_id,
            include_audio=include_audio,
            include_transcript=include_transcript
        )
        
        # Initialize chain of custody
        chain_of_custody = [
            ChainOfCustodyEntry(
                timestamp=datetime.utcnow().isoformat(),
                action="package_created",
                actor="rakshak_system",
                description="Evidence package creation initiated"
            )
        ]
        
        # Gather evidence data (would fetch from database in production)
        evidence_data = await self._gather_evidence_data(call_id)
        
        # Calculate audio hash if included
        audio_hash = None
        if include_audio and evidence_data.get("audio_data"):
            audio_hash = self._calculate_hash(evidence_data["audio_data"])
            chain_of_custody.append(
                ChainOfCustodyEntry(
                    timestamp=datetime.utcnow().isoformat(),
                    action="audio_hashed",
                    actor="rakshak_system",
                    description="Audio evidence hashed for integrity verification",
                    hash_after=audio_hash
                )
            )
        
        # Create package
        package = EvidencePackage(
            package_id=self._generate_package_id(),
            call_id=call_id,
            created_at=datetime.utcnow(),
            phone_number=evidence_data.get("phone_number", "unknown"),
            call_duration_seconds=evidence_data.get("duration_seconds", 0),
            threat_level=evidence_data.get("threat_level", "unknown"),
            audio_file_hash=audio_hash,
            transcript=evidence_data.get("transcript") if include_transcript else None,
            entities=evidence_data.get("entities", []) if include_intelligence else [],
            threat_timeline=evidence_data.get("threat_timeline", []),
            signature=None,  # Will be added if sign_package is True
            chain_of_custody=[asdict(entry) for entry in chain_of_custody]
        )
        
        # Sign package if requested
        if sign_package:
            signature = self._sign_package(package)
            package.signature = signature
        
        logger.info(
            "evidence_package_created",
            package_id=package.package_id,
            call_id=call_id,
            entities_count=len(package.entities)
        )
        
        return package
    
    async def _gather_evidence_data(self, call_id: str) -> Dict[str, Any]:
        """Gather all evidence data for a call."""
        # In production, this would fetch from database
        # For now, return mock data structure
        
        return {
            "phone_number": "+91XXXXXXXXXX",
            "duration_seconds": 300,
            "threat_level": "high",
            "audio_data": None,  # Would be actual audio bytes
            "transcript": "Sample transcript for evidence...",
            "entities": [],
            "threat_timeline": []
        }
    
    def _generate_package_id(self) -> str:
        """Generate unique package ID."""
        timestamp = str(int(time.time()))
        random_component = hashlib.sha256(
            f"{time.time()}{timestamp}".encode()
        ).hexdigest()[:8]
        return f"RAK-{timestamp}-{random_component}"
    
    def _calculate_hash(self, data: Any) -> str:
        """Calculate SHA-256 hash of data."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        elif isinstance(data, dict):
            data = json.dumps(data, sort_keys=True).encode('utf-8')
        
        return hashlib.sha256(data).hexdigest()
    
    def _sign_package(self, package: EvidencePackage) -> EvidenceSignature:
        """Cryptographically sign the evidence package."""
        # Create canonical representation for signing
        package_dict = {
            "package_id": package.package_id,
            "call_id": package.call_id,
            "created_at": package.created_at.isoformat(),
            "phone_number": package.phone_number,
            "call_duration_seconds": package.call_duration_seconds,
            "threat_level": package.threat_level,
            "audio_file_hash": package.audio_file_hash,
            "transcript_hash": self._calculate_hash(package.transcript) if package.transcript else None,
            "entities_count": len(package.entities)
        }
        
        # Calculate hash
        package_hash = self._calculate_hash(package_dict)
        
        # In production, this would use proper digital signature
        # For now, we create a simple signed hash
        signature_value = hashlib.sha256(
            f"{package_hash}{settings.secret_key}".encode()
        ).hexdigest()
        
        return EvidenceSignature(
            algorithm="SHA256",
            hash_value=signature_value,
            timestamp=datetime.utcnow(),
            signed_by="rakshak_system"
        )
    
    def verify_package(self, package: EvidencePackage) -> bool:
        """Verify the integrity of an evidence package."""
        if not package.signature:
            logger.warning("package_not_signed", package_id=package.package_id)
            return False
        
        # Recalculate expected signature
        expected_package = EvidencePackage(
            package_id=package.package_id,
            call_id=package.call_id,
            created_at=package.created_at,
            phone_number=package.phone_number,
            call_duration_seconds=package.call_duration_seconds,
            threat_level=package.threat_level,
            audio_file_hash=package.audio_file_hash,
            transcript=package.transcript,
            entities=package.entities,
            threat_timeline=package.threat_timeline,
            signature=None,  # Don't include signature in verification
            chain_of_custody=package.chain_of_custody
        )
        
        expected_signature = self._sign_package(expected_package)
        
        is_valid = expected_signature.hash_value == package.signature.hash_value
        
        logger.info(
            "package_verification",
            package_id=package.package_id,
            valid=is_valid
        )
        
        return is_valid
    
    async def add_custody_entry(
        self,
        package: EvidencePackage,
        action: str,
        actor: str,
        description: str
    ) -> EvidencePackage:
        """Add a new entry to the chain of custody."""
        entry = ChainOfCustodyEntry(
            timestamp=datetime.utcnow().isoformat(),
            action=action,
            actor=actor,
            description=description
        )
        
        package.chain_of_custody.append(asdict(entry))
        
        logger.info(
            "custody_entry_added",
            package_id=package.package_id,
            action=action,
            actor=actor
        )
        
        return package
    
    async def export_for_submission(
        self,
        package: EvidencePackage,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Export package in format suitable for law enforcement submission."""
        if format == "json":
            return {
                "case_reference": package.package_id,
                "submission_date": datetime.utcnow().isoformat(),
                "evidence_type": "telephonic_fraud",
                "suspect_information": {
                    "phone_number": package.phone_number,
                    "call_duration": package.call_duration_seconds
                },
                "threat_assessment": {
                    "level": package.threat_level,
                    "timeline": package.threat_timeline
                },
                "extracted_intelligence": [
                    {
                        "type": e.entity_type,
                        "value": e.value,
                        "confidence": e.confidence,
                        "context": e.context
                    }
                    for e in package.entities
                ],
                "integrity_verification": {
                    "audio_hash": package.audio_file_hash,
                    "signature_algorithm": package.signature.algorithm if package.signature else None,
                    "signature_hash": package.signature.hash_value if package.signature else None,
                    "signed_at": package.signature.timestamp.isoformat() if package.signature else None
                },
                "chain_of_custody": package.chain_of_custody
            }
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("evidence_packager_cleaned_up")
