"""
RakshakAI - Intelligence Extractor Service
Extracts actionable intelligence from scammer conversations for law enforcement.
"""

import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

import structlog

logger = structlog.get_logger("rakshak.intel")


@dataclass
class ExtractedEntity:
    """Represents an extracted entity with metadata."""
    entity_type: str
    value: str
    confidence: float
    context: str
    position: int
    verified: bool = False


class IntelligenceExtractor:
    """
    Extracts intelligence from scammer transcripts.
    
    Extracts:
    - UPI IDs (e.g., name@paytm, name@okaxis)
    - Indian mobile numbers
    - Bank account numbers
    - Email addresses
    - Aadhaar numbers (masked)
    - PAN numbers (masked)
    - OTP patterns
    - Names and locations
    """
    
    # Regex patterns for entity extraction
    PATTERNS = {
        "upi_id": re.compile(
            r'\b[A-Za-z0-9._-]+@(paytm|okaxis|okhdfcbank|okicici|oksbi|ybl|apl|okbizaxis|payzapp|ibl|axl)\b',
            re.IGNORECASE
        ),
        "phone_number": re.compile(
            r'\b(\+91[-\s]?)?[6-9]\d{9}\b'
        ),
        "email": re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        ),
        "bank_account": re.compile(
            r'\b\d{9,18}\b'  # Basic pattern - can be refined
        ),
        "ifsc_code": re.compile(
            r'\b[A-Z]{4}0[A-Z0-9]{6}\b',
            re.IGNORECASE
        ),
        "aadhaar": re.compile(
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        ),
        "pan": re.compile(
            r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',
            re.IGNORECASE
        ),
        "otp": re.compile(
            r'\b\d{4,6}\b',
            re.IGNORECASE
        ),
        "credit_card": re.compile(
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        ),
        "cvv": re.compile(
            r'\b\d{3,4}\b',
            re.IGNORECASE
        ),
        "amount": re.compile(
            r'\b(\d{1,3}(,\d{2,3})*|\d+)(\s)?(lakh|crore|thousand|hundred|rupees|rs\.?)?\b',
            re.IGNORECASE
        )
    }
    
    # Context keywords that increase confidence
    CONTEXT_KEYWORDS = {
        "upi_id": ["upi", "pay", "google pay", "phonepe", "paytm", "send money", "transfer"],
        "phone_number": ["call", "phone", "mobile", "number", "contact", "whatsapp"],
        "email": ["email", "mail", "send", "id"],
        "bank_account": ["account", "bank", "transfer", "deposit", "ifsc"],
        "ifsc_code": ["ifsc", "branch", "bank code"],
        "aadhaar": ["aadhaar", "uid", "identity", "verification"],
        "pan": ["pan", "permanent account number", "tax"],
        "otp": ["otp", "password", "code", "verification code", "pin"],
        "credit_card": ["card", "credit", "debit", "atm", "cvv"],
        "cvv": ["cvv", "security code", "back of card", "three digit"],
        "amount": ["rupees", "rs", "amount", "money", "payment", "fee", "charge"]
    }
    
    def __init__(self):
        self.extraction_stats = {
            "total_extractions": 0,
            "by_type": {}
        }
        self._initialized = False
    
    async def initialize(self):
        """Initialize the extractor."""
        if self._initialized:
            return
        
        self._initialized = True
        logger.info("intelligence_extractor_initialized")
    
    async def extract(self, transcript: str) -> List[ExtractedEntity]:
        """
        Extract all entities from a transcript.
        
        Args:
            transcript: The conversation transcript
        
        Returns:
            List of extracted entities with confidence scores
        """
        if not transcript:
            return []
        
        entities = []
        
        # Extract each entity type
        for entity_type, pattern in self.PATTERNS.items():
            matches = pattern.finditer(transcript)
            
            for match in matches:
                value = match.group()
                position = match.start()
                
                # Get context (50 chars before and after)
                context_start = max(0, position - 50)
                context_end = min(len(transcript), position + len(value) + 50)
                context = transcript[context_start:context_end]
                
                # Calculate confidence
                confidence = self._calculate_confidence(
                    entity_type, value, context, transcript
                )
                
                # Filter low-confidence extractions
                if confidence < 0.3:
                    continue
                
                # Mask sensitive data
                masked_value = self._mask_sensitive(entity_type, value)
                
                entity = ExtractedEntity(
                    entity_type=entity_type,
                    value=masked_value,
                    confidence=confidence,
                    context=context,
                    position=position,
                    verified=False  # Requires manual verification
                )
                
                entities.append(entity)
                
                # Update stats
                self.extraction_stats["total_extractions"] += 1
                self.extraction_stats["by_type"][entity_type] = \
                    self.extraction_stats["by_type"].get(entity_type, 0) + 1
        
        # Remove duplicates (same type and similar value)
        entities = self._deduplicate(entities)
        
        logger.debug(
            "entities_extracted",
            count=len(entities),
            types=[e.entity_type for e in entities]
        )
        
        return entities
    
    async def extract_specific(
        self,
        transcript: str,
        entity_types: List[str]
    ) -> List[ExtractedEntity]:
        """Extract only specific entity types."""
        all_entities = await self.extract(transcript)
        return [e for e in all_entities if e.entity_type in entity_types]
    
    def _calculate_confidence(
        self,
        entity_type: str,
        value: str,
        context: str,
        full_transcript: str
    ) -> float:
        """Calculate confidence score for an extraction."""
        confidence = 0.5  # Base confidence
        
        # Check context keywords
        context_lower = context.lower()
        keywords = self.CONTEXT_KEYWORDS.get(entity_type, [])
        keyword_matches = sum(1 for kw in keywords if kw in context_lower)
        confidence += min(0.3, keyword_matches * 0.1)
        
        # Validate format
        if entity_type == "upi_id":
            if self._validate_upi(value):
                confidence += 0.2
        elif entity_type == "phone_number":
            if self._validate_phone(value):
                confidence += 0.2
        elif entity_type == "email":
            if self._validate_email(value):
                confidence += 0.2
        
        # Check for suspicious patterns that might indicate false positive
        if self._is_likely_false_positive(entity_type, value, context):
            confidence -= 0.3
        
        return min(1.0, max(0.0, confidence))
    
    def _validate_upi(self, upi_id: str) -> bool:
        """Validate UPI ID format."""
        parts = upi_id.split("@")
        if len(parts) != 2:
            return False
        
        handle = parts[1].lower()
        valid_handles = [
            "paytm", "okaxis", "okhdfcbank", "okicici", "oksbi",
            "ybl", "apl", "okbizaxis", "payzapp", "ibl", "axl"
        ]
        
        return handle in valid_handles
    
    def _validate_phone(self, phone: str) -> bool:
        """Validate Indian phone number."""
        # Remove non-digits
        digits = re.sub(r'\D', '', phone)
        
        # Check length and starting digit
        if len(digits) == 10 and digits[0] in "6789":
            return True
        if len(digits) == 12 and digits.startswith("91"):
            return True
        
        return False
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = re.compile(
            r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        )
        return bool(pattern.match(email))
    
    def _is_likely_false_positive(
        self,
        entity_type: str,
        value: str,
        context: str
    ) -> bool:
        """Check if extraction is likely a false positive."""
        context_lower = context.lower()
        
        # OTP false positives (dates, random numbers)
        if entity_type == "otp":
            # If surrounded by date-related words
            if any(word in context_lower for word in ["date", "year", "jan", "feb", "mar"]):
                return True
            # If it's a year-like number
            if value in ["2023", "2024", "2025", "2026"]:
                return True
        
        # Phone number false positives
        if entity_type == "phone_number":
            # If part of a larger number (account number, etc.)
            if len(re.sub(r'\D', '', value)) < 10:
                return True
        
        return False
    
    def _mask_sensitive(self, entity_type: str, value: str) -> str:
        """Mask sensitive data for privacy."""
        if entity_type == "aadhaar":
            # Mask all but last 4 digits
            digits = re.sub(r'\D', '', value)
            return f"XXXX-XXXX-{digits[-4:]}" if len(digits) >= 4 else "XXXX-XXXX-XXXX"
        
        elif entity_type == "pan":
            # Mask middle digits
            return f"{value[:2]}XXXX{value[-2:]}" if len(value) >= 4 else "XXXXX0000X"
        
        elif entity_type == "credit_card":
            # Mask all but last 4
            digits = re.sub(r'\D', '', value)
            return f"XXXX-XXXX-XXXX-{digits[-4:]}" if len(digits) >= 4 else "XXXX-XXXX-XXXX-XXXX"
        
        elif entity_type == "bank_account":
            # Mask all but last 4
            return f"XXXXXX{value[-4:]}" if len(value) >= 4 else "XXXXXXXX"
        
        elif entity_type == "otp":
            # Fully mask OTPs
            return "XXXX"
        
        elif entity_type == "cvv":
            # Fully mask CVV
            return "XXX"
        
        return value
    
    def _deduplicate(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """Remove duplicate entities."""
        seen = set()
        unique = []
        
        for entity in entities:
            # Create a key for deduplication
            key = (entity.entity_type, entity.value.lower())
            
            if key not in seen:
                seen.add(key)
                unique.append(entity)
        
        return unique
    
    async def generate_intelligence_report(
        self,
        call_id: str,
        entities: List[ExtractedEntity],
        transcript: str
    ) -> Dict[str, Any]:
        """Generate a comprehensive intelligence report."""
        # Group entities by type
        by_type = {}
        for entity in entities:
            if entity.entity_type not in by_type:
                by_type[entity.entity_type] = []
            by_type[entity.entity_type].append({
                "value": entity.value,
                "confidence": entity.confidence,
                "context": entity.context[:100]  # Truncate context
            })
        
        # Extract fraud indicators
        fraud_indicators = self._extract_fraud_indicators(transcript)
        
        # Calculate overall risk
        risk_score = self._calculate_risk_score(entities, fraud_indicators)
        
        report = {
            "call_id": call_id,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_entities": len(entities),
                "high_confidence_entities": sum(1 for e in entities if e.confidence > 0.7),
                "risk_score": risk_score,
                "risk_level": self._risk_level(risk_score)
            },
            "entities_by_type": by_type,
            "fraud_indicators": fraud_indicators,
            "recommended_actions": self._recommend_actions(risk_score, by_type)
        }
        
        return report
    
    def _extract_fraud_indicators(self, transcript: str) -> List[str]:
        """Extract fraud indicators from transcript."""
        indicators = []
        transcript_lower = transcript.lower()
        
        indicator_patterns = {
            "request_otp": ["otp bataiye", "otp do", "code batao", "password batao"],
            "request_upi_pin": ["upi pin", "pin batao", "pin do"],
            "request_card_details": ["card number", "cvv", "expiry date", "atm card"],
            "urgency_pressure": ["jaldi", "abhi", "immediately", "urgent", "time kam hai"],
            "secrecy": ["kisi ko mat batana", "secret", "confidential", "chupke se"],
            "remote_access": ["anydesk", "teamviewer", "screen share", "remote", "download app"],
            "threats": ["arrest", "jail", "police", "case", "court", "legal action"],
            "advance_fee": ["processing fee", "security deposit", "tax pehle", "advance mein"]
        }
        
        for indicator, patterns in indicator_patterns.items():
            if any(pattern in transcript_lower for pattern in patterns):
                indicators.append(indicator)
        
        return indicators
    
    def _calculate_risk_score(
        self,
        entities: List[ExtractedEntity],
        fraud_indicators: List[str]
    ) -> float:
        """Calculate overall risk score."""
        score = 0.0
        
        # Entity-based scoring
        high_risk_entities = ["upi_id", "phone_number", "bank_account", "ifsc_code"]
        for entity in entities:
            if entity.entity_type in high_risk_entities and entity.confidence > 0.5:
                score += 0.15
        
        # Fraud indicator scoring
        score += len(fraud_indicators) * 0.1
        
        return min(1.0, score)
    
    def _risk_level(self, score: float) -> str:
        """Convert risk score to level."""
        if score >= 0.8:
            return "critical"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        elif score > 0:
            return "low"
        return "none"
    
    def _recommend_actions(
        self,
        risk_score: float,
        entities: Dict[str, List[Dict]]
    ) -> List[str]:
        """Generate recommended actions based on findings."""
        actions = []
        
        if risk_score >= 0.8:
            actions.append("immediate_report_to_authorities")
        
        if "upi_id" in entities:
            actions.append("flag_upi_ids")
        
        if "phone_number" in entities:
            actions.append("trace_phone_numbers")
        
        if "bank_account" in entities or "ifsc_code" in entities:
            actions.append("notify_banks")
        
        if not actions:
            actions.append("continue_monitoring")
        
        return actions
