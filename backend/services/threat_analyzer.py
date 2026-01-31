"""
RakshakAI - Threat Analyzer Service
ML-based threat detection using keyword spotting, behavioral analysis, and deep learning.
"""

import asyncio
import pickle
import re
from collections import deque
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

import numpy as np
import structlog
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import GradientBoostingClassifier

from core.config import settings

logger = structlog.get_logger("rakshak.threat")


class ThreatAnalyzer:
    """
    Real-time threat analysis engine for scam call detection.
    
    Uses multiple detection layers:
    1. Keyword/Pattern matching (fast, rule-based)
    2. Behavioral analysis (speech patterns, urgency)
    3. ML classification (deep learning model)
    4. Contextual analysis (conversation flow)
    """
    
    # High-risk keywords and phrases for Indian scam patterns
    SCAM_KEYWORDS = {
        "urgent": [
            "immediate action required",
            "act now",
            "limited time",
            "urgent",
            "emergency",
            "last chance",
            "today only",
            "right now"
        ],
        "financial": [
            "bank account",
            "credit card",
            "debit card",
            "upi",
            "paytm",
            "google pay",
            "phonepe",
            "otp",
            "pin",
            "password",
            "cvv",
            "expiry date",
            "account number",
            "ifsc code"
        ],
        "impersonation": [
            "reserve bank of india",
            "rbi",
            "income tax department",
            "cyber crime",
            "police department",
            "cbi",
            "enforcement directorate",
            "customs department",
            "narcotics bureau",
            "your bank",
            "your insurance company"
        ],
        "threats": [
            "arrest warrant",
            "legal action",
            "court case",
            "fir",
            "police complaint",
            "account frozen",
            "account blocked",
            "sim card blocked",
            "pan card blocked"
        ],
        "remote_access": [
            "anydesk",
            "teamviewer",
            "quick support",
            "screen sharing",
            "remote access",
            "install app",
            "download software"
        ],
        "verification": [
            "kyc verification",
            "kyc update",
            "aadhaar verification",
            "pan verification",
            "document verification",
            "verify your identity"
        ],
        "prize": [
            "you have won",
            "lottery",
            "lucky draw",
            "prize money",
            "cash prize",
            "free gift",
            "congratulations"
        ]
    }
    
    # Behavioral indicators
    BEHAVIORAL_FLAGS = {
        "high_pressure": ["must", "immediately", "now", "urgent", "hurry"],
        "secrecy": ["don't tell anyone", "keep it secret", "confidential", "don't discuss"],
        "isolation": ["don't contact bank", "don't call police", "don't tell family"],
        "unprofessional": ["sir/madam repeatedly", "heavy accent mismatch", "background noise"]
    }
    
    def __init__(self):
        self.keyword_model = None
        self.ml_model = None
        self.vectorizer = None
        self.call_contexts: Dict[str, Dict[str, Any]] = {}
        self._initialized = False
        
    async def initialize(self):
        """Initialize threat analysis models."""
        if self._initialized:
            return
        
        # Load or create keyword-based model
        self.keyword_model = KeywordSpotter(self.SCAM_KEYWORDS)
        
        # Try to load pre-trained ML model
        try:
            model_path = f"{settings.model_path}/scam_classifier.pkl"
            with open(model_path, 'rb') as f:
                self.ml_model, self.vectorizer = pickle.load(f)
            logger.info("ml_model_loaded", path=model_path)
        except FileNotFoundError:
            logger.warning("ml_model_not_found_using_keyword_fallback")
            self.ml_model = None
            self.vectorizer = None
        
        self._initialized = True
    
    async def analyze(
        self,
        transcript: Optional[str],
        audio_features: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive threat analysis.
        
        Returns:
            Dict with threat_score, threat_level, confidence, indicators
        """
        await self.initialize()
        
        scores = []
        indicators = []
        keywords = []
        behavioral_flags = []
        
        # Layer 1: Keyword Analysis
        if transcript:
            keyword_result = self.keyword_model.analyze(transcript)
            scores.append(keyword_result["score"])
            indicators.extend(keyword_result["indicators"])
            keywords.extend(keyword_result["matched_keywords"])
        
        # Layer 2: Behavioral Analysis
        if transcript:
            behavioral_result = self._analyze_behavior(transcript)
            scores.append(behavioral_result["score"])
            behavioral_flags.extend(behavioral_result["flags"])
        
        # Layer 3: ML Classification
        if self.ml_model and transcript:
            ml_result = self._ml_classify(transcript)
            scores.append(ml_result["score"])
            indicators.extend(ml_result["indicators"])
        
        # Layer 4: Audio Feature Analysis
        if audio_features:
            audio_result = self._analyze_audio_features(audio_features)
            scores.append(audio_result["score"])
        
        # Combine scores (weighted average)
        if scores:
            # Weight keyword detection higher for immediate response
            weights = [0.4, 0.2, 0.3, 0.1][:len(scores)]
            weights = [w / sum(weights) for w in weights]
            threat_score = sum(s * w for s, w in zip(scores, weights))
        else:
            threat_score = 0.0
        
        # Determine threat level
        threat_level = self._get_threat_level(threat_score)
        
        # Determine recommended action
        recommended_action = self._get_recommended_action(threat_score, threat_level)
        
        return {
            "threat_score": round(threat_score, 3),
            "threat_level": threat_level,
            "confidence": round(min(1.0, len(scores) * 0.25 + 0.5), 3),
            "indicators": list(set(indicators)),
            "keywords": list(set(keywords)),
            "behavioral_flags": list(set(behavioral_flags)),
            "recommended_action": recommended_action
        }
    
    async def analyze_realtime(
        self,
        call_id: str,
        transcript: str,
        audio_features: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Real-time threat analysis with context tracking.
        
        Maintains conversation context to detect patterns over time.
        """
        # Initialize call context if needed
        if call_id not in self.call_contexts:
            self.call_contexts[call_id] = {
                "transcripts": deque(maxlen=20),
                "threat_scores": deque(maxlen=10),
                "keywords_seen": set(),
                "start_time": datetime.utcnow(),
                "escalation_count": 0
            }
        
        context = self.call_contexts[call_id]
        
        # Add to transcript history
        context["transcripts"].append(transcript)
        
        # Analyze current transcript
        result = await self.analyze(transcript, audio_features)
        
        # Track threat score history
        context["threat_scores"].append(result["threat_score"])
        context["keywords_seen"].update(result.get("keywords", []))
        
        # Adjust score based on context
        adjusted_score = self._adjust_for_context(result["threat_score"], context)
        result["threat_score"] = round(adjusted_score, 3)
        result["threat_level"] = self._get_threat_level(adjusted_score)
        
        # Check for escalation pattern
        if len(context["threat_scores"]) >= 3:
            recent_scores = list(context["threat_scores"])[-3:]
            if all(s > settings.threat_threshold_medium for s in recent_scores):
                result["escalation_detected"] = True
                result["recommended_action"] = "handoff_to_ai"
        
        return result
    
    def _analyze_behavior(self, transcript: str) -> Dict[str, Any]:
        """Analyze behavioral patterns in transcript."""
        transcript_lower = transcript.lower()
        flags = []
        score = 0.0
        
        for flag_type, patterns in self.BEHAVIORAL_FLAGS.items():
            for pattern in patterns:
                if pattern in transcript_lower:
                    flags.append(flag_type)
                    score += 0.15
        
        # Check for repetitive patterns (pressure tactic)
        words = transcript_lower.split()
        if len(words) > 10:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.4:  # High repetition
                flags.append("repetitive_speech")
                score += 0.1
        
        return {"score": min(1.0, score), "flags": list(set(flags))}
    
    def _ml_classify(self, transcript: str) -> Dict[str, Any]:
        """Classify using ML model."""
        try:
            # Vectorize transcript
            X = self.vectorizer.transform([transcript])
            
            # Predict
            proba = self.ml_model.predict_proba(X)[0]
            prediction = self.ml_model.predict(X)[0]
            
            # Scam is typically class 1
            scam_prob = proba[1] if len(proba) > 1 else proba[0]
            
            indicators = []
            if prediction == 1:
                indicators.append("ml_classification_scam")
            
            return {
                "score": float(scam_prob),
                "indicators": indicators
            }
        except Exception as e:
            logger.error("ml_classification_error", error=str(e))
            return {"score": 0.0, "indicators": []}
    
    def _analyze_audio_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze audio features for stress/deception indicators."""
        score = 0.0
        
        # High energy variance can indicate stress
        if "rms_energy" in features:
            energy = features["rms_energy"]
            if energy > 0.5:  # Very loud
                score += 0.1
        
        # High zero crossing rate can indicate agitation
        if "zero_crossing_rate" in features:
            zcr = features["zero_crossing_rate"]
            if zcr > 0.1:
                score += 0.05
        
        return {"score": min(1.0, score)}
    
    def _adjust_for_context(self, score: float, context: Dict[str, Any]) -> float:
        """Adjust threat score based on conversation context."""
        adjusted = score
        
        # Increase score if multiple threat keywords seen
        keyword_diversity = len(context["keywords_seen"])
        if keyword_diversity > 3:
            adjusted += 0.1
        
        # Increase score if sustained high threat
        if len(context["threat_scores"]) >= 5:
            avg_recent = sum(context["threat_scores"]) / len(context["threat_scores"])
            if avg_recent > settings.threat_threshold_medium:
                adjusted += 0.1
        
        return min(1.0, adjusted)
    
    def _get_threat_level(self, score: float) -> str:
        """Convert threat score to threat level."""
        if score >= settings.threat_threshold_high:
            return "critical"
        elif score >= settings.threat_threshold_medium:
            return "high"
        elif score >= settings.threat_threshold_low:
            return "medium"
        elif score > 0.1:
            return "low"
        else:
            return "safe"
    
    def _get_recommended_action(self, score: float, level: str) -> str:
        """Get recommended action based on threat."""
        if score >= settings.threat_threshold_high:
            return "handoff_to_ai"
        elif score >= settings.threat_threshold_medium:
            return "alert_user"
        elif score >= settings.threat_threshold_low:
            return "increase_monitoring"
        else:
            return "continue_monitoring"
    
    async def cleanup(self):
        """Cleanup resources."""
        self.call_contexts.clear()
        self._initialized = False
        logger.info("threat_analyzer_cleaned_up")


class KeywordSpotter:
    """Rule-based keyword spotting for scam detection."""
    
    def __init__(self, keyword_dict: Dict[str, List[str]]):
        self.keywords = keyword_dict
        self.compiled_patterns = {}
        
        # Compile regex patterns for efficiency
        for category, words in keyword_dict.items():
            patterns = [re.escape(word) for word in words]
            self.compiled_patterns[category] = re.compile(
                '|'.join(patterns),
                re.IGNORECASE
            )
    
    def analyze(self, transcript: str) -> Dict[str, Any]:
        """Analyze transcript for scam keywords."""
        transcript_lower = transcript.lower()
        matched_keywords = []
        indicators = []
        score = 0.0
        
        # Check each category
        category_scores = {
            "urgent": 0.15,
            "financial": 0.20,
            "impersonation": 0.25,
            "threats": 0.25,
            "remote_access": 0.20,
            "verification": 0.15,
            "prize": 0.20
        }
        
        for category, pattern in self.compiled_patterns.items():
            matches = pattern.findall(transcript)
            if matches:
                matched_keywords.extend(matches)
                indicators.append(f"{category}_keywords_detected")
                score += category_scores.get(category, 0.1) * len(matches)
        
        # Bonus for multiple categories
        unique_categories = len(set(
            ind.replace("_keywords_detected", "") 
            for ind in indicators
        ))
        if unique_categories >= 2:
            score += 0.1 * unique_categories
            indicators.append("multiple_threat_categories")
        
        return {
            "score": min(1.0, score),
            "matched_keywords": list(set(matched_keywords)),
            "indicators": indicators
        }
