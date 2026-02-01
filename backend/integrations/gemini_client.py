"""
RakshakAI - Gemini API Integration
FREE Google Gemini API for LLM capabilities
"""

import os
import json
import asyncio
from typing import AsyncGenerator, Dict, Any, List, Optional
from dataclasses import dataclass
import structlog

# Try to import google.generativeai, fallback to requests if not available
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

import aiohttp

logger = structlog.get_logger("rakshak.gemini")


@dataclass
class GeminiResponse:
    """Structured response from Gemini API"""
    text: str
    safety_ratings: Dict[str, Any]
    token_count: int
    finish_reason: str


class GeminiClient:
    """
    FREE Gemini API Client for RakshakAI
    
    Features:
    - Scam transcript analysis
    - AI Bait Agent responses
    - Intelligence extraction
    - Threat assessment
    - Real-time streaming responses
    
    Get FREE API Key: https://makersuite.google.com/app/apikey
    """
    
    # Gemini API Configuration
    API_KEY: str = ""
    MODEL_NAME: str = "gemini-1.5-flash"  # FREE tier - fast & capable
    API_URL: str = "https://generativelanguage.googleapis.com/v1beta/models"
    
    # Safety settings to allow scam-related content for analysis
    SAFETY_SETTINGS = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    
    # Generation config for optimal responses
    GENERATION_CONFIG = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 2048,
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.session: Optional[aiohttp.ClientSession] = None
        self._initialized = False
        
        if GENAI_AVAILABLE and self.api_key:
            self._init_genai()
    
    def _init_genai(self):
        """Initialize the official Google Generative AI library"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name=self.MODEL_NAME,
                safety_settings=self.SAFETY_SETTINGS,
                generation_config=self.GENERATION_CONFIG
            )
            logger.info("gemini_client_initialized", model=self.MODEL_NAME)
            self._initialized = True
        except Exception as e:
            logger.error("gemini_init_failed", error=str(e))
    
    async def initialize(self):
        """Initialize async HTTP session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60)
            )
    
    # ==================== SCAM ANALYSIS ====================
    
    async def analyze_scam_transcript(self, transcript: str) -> Dict[str, Any]:
        """
        Analyze a call transcript for scam indicators using Gemini
        
        Returns:
            Dict with threat_score, indicators, scam_type, confidence
        """
        prompt = f"""You are an expert fraud detection analyst. Analyze the following phone call transcript and determine if it's a scam.

TRANSCRIPT:
{transcript}

Provide your analysis in this EXACT JSON format:
{{
    "is_scam": true/false,
    "threat_score": 0.0-1.0,
    "scam_type": "KYC Fraud|Bank Impersonation|Tech Support|Lottery|Prize|Police Impersonation|None",
    "confidence": 0.0-1.0,
    "indicators": ["list", "of", "detected", "indicators"],
    "urgency_level": "low|medium|high|critical",
    "financial_requests": ["any", "financial", "info", "requested"],
    "red_flags": ["behavioral", "red", "flags"],
    "recommended_action": "continue_monitoring|alert_user|handoff_to_ai|terminate_call",
    "explanation": "brief explanation of analysis"
}}

Respond ONLY with the JSON, no other text."""

        try:
            response = await self._generate_content(prompt)
            # Extract JSON from response
            json_str = self._extract_json(response.text)
            result = json.loads(json_str)
            logger.info("scam_analysis_complete", threat_score=result.get("threat_score"))
            return result
        except Exception as e:
            logger.error("scam_analysis_failed", error=str(e))
            return self._default_analysis()
    
    async def extract_entities(self, transcript: str) -> List[Dict[str, Any]]:
        """
        Extract financial entities from transcript using Gemini
        
        Extracts: UPI IDs, phone numbers, bank accounts, IFSC codes, emails, amounts
        """
        prompt = f"""Extract all financial entities from this transcript. Be thorough and accurate.

TRANSCRIPT:
{transcript}

Return ONLY a JSON array in this format:
[
    {{
        "type": "upi_id|phone_number|bank_account|ifsc_code|email|amount|otp|card_number|cvv",
        "value": "extracted value",
        "confidence": 0.0-1.0,
        "context": "surrounding text"
    }}
]

If no entities found, return empty array []. Respond ONLY with the JSON array."""

        try:
            response = await self._generate_content(prompt)
            json_str = self._extract_json(response.text)
            entities = json.loads(json_str)
            
            # Validate and filter entities
            validated = []
            for entity in entities:
                if self._validate_entity(entity):
                    validated.append(entity)
            
            logger.info("entities_extracted", count=len(validated))
            return validated
        except Exception as e:
            logger.error("entity_extraction_failed", error=str(e))
            return []
    
    # ==================== AI BAIT AGENT ====================
    
    async def generate_bait_response(
        self,
        scammer_message: str,
        persona: str = "confused_senior",
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Generate AI bait agent response using Gemini
        
        Personas:
        - confused_senior: Elderly, not tech-savvy, asks questions
        - cautious_professional: Business owner, asks for verification
        - trusting_homemaker: Family-oriented, polite
        """
        
        persona_prompts = {
            "confused_senior": """You are Ramesh Kumar, a 68-year-old retired government employee from India.
Characteristics:
- Speak in Hinglish (mix of Hindi and English)
- Get confused by technology terms
- Trust authority figures (bank, police)
- Ask questions repeatedly
- Speak slowly and politely
- Sometimes hard of hearing
- Use phrases like "beta", "ji", "samajh nahi aaya"
- NEVER reveal you are an AI
- Keep the scammer engaged as long as possible
- Don't agree to send money or share OTP/card details""",

            "cautious_professional": """You are Suresh Patel, a 45-year-old business owner.
Characteristics:
- Professional tone
- Ask for documentation
- Question authority claims
- Want to verify everything
- Busy and sometimes distracted
- Mention consulting lawyer/accountant
- NEVER reveal you are an AI
- Keep the scammer engaged as long as possible
- Don't agree to send money or share OTP/card details""",

            "trusting_homemaker": """You are Lakshmi Devi, a 55-year-old homemaker.
Characteristics:
- Soft-spoken and polite
- Use "beta" to address caller
- Family-oriented concerns
- Not familiar with banking procedures
- Respectful but cautious
- Mention husband/son handles finances
- NEVER reveal you are an AI
- Keep the scammer engaged as long as possible
- Don't agree to send money or share OTP/card details"""
        }
        
        persona_prompt = persona_prompts.get(persona, persona_prompts["confused_senior"])
        
        history_str = ""
        if conversation_history:
            for entry in conversation_history[-5:]:  # Last 5 exchanges
                speaker = "Scammer" if entry.get("speaker") == "scammer" else "You"
                history_str += f"{speaker}: {entry.get('text', '')}\n"
        
        prompt = f"""{persona_prompt}

CONVERSATION HISTORY:
{history_str}

SCAMMER JUST SAID:
{scammer_message}

Respond as your character would. Keep it natural, engage the scammer, waste their time.
Respond in 1-3 sentences maximum. Use Hinglish if appropriate."""

        try:
            response = await self._generate_content(prompt)
            logger.info("bait_response_generated", persona=persona)
            return response.text.strip()
        except Exception as e:
            logger.error("bait_response_failed", error=str(e))
            return self._fallback_bait_response(persona)
    
    # ==================== REAL-TIME STREAMING ====================
    
    async def stream_bait_response(
        self,
        scammer_message: str,
        persona: str = "confused_senior",
        conversation_history: List[Dict] = None
    ) -> AsyncGenerator[str, None]:
        """Stream bait agent response in real-time"""
        
        persona_prompts = {
            "confused_senior": "You are Ramesh Kumar, a confused 68-year-old Indian senior. Respond naturally in Hinglish.",
            "cautious_professional": "You are Suresh Patel, a cautious business owner. Ask questions, verify claims.",
            "trusting_homemaker": "You are Lakshmi Devi, a trusting homemaker. Be polite but cautious."
        }
        
        history_str = ""
        if conversation_history:
            for entry in conversation_history[-3:]:
                speaker = "Scammer" if entry.get("speaker") == "scammer" else "You"
                history_str += f"{speaker}: {entry.get('text', '')}\n"
        
        prompt = f"""{persona_prompts.get(persona, persona_prompts["confused_senior"])}

Previous conversation:
{history_str}

Scammer: {scammer_message}

You (respond naturally, waste their time, 1-2 sentences):"""

        try:
            if GENAI_AVAILABLE and self._initialized:
                # Use streaming with official SDK
                response = self.model.generate_content(prompt, stream=True)
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
            else:
                # Fallback to non-streaming
                response = await self._generate_content(prompt)
                yield response.text
        except Exception as e:
            logger.error("streaming_failed", error=str(e))
            yield self._fallback_bait_response(persona)
    
    # ==================== INTELLIGENCE ANALYSIS ====================
    
    async def analyze_scammer_profile(
        self,
        phone_numbers: List[str],
        upi_ids: List[str],
        transcripts: List[str]
    ) -> Dict[str, Any]:
        """Build comprehensive scammer profile using Gemini"""
        
        prompt = f"""Analyze this scammer's profile based on collected intelligence:

PHONE NUMBERS: {phone_numbers}
UPI IDs: {upi_ids}
SAMPLE TRANSCRIPTS:
{chr(10).join(transcripts[:3])}

Provide analysis in JSON format:
{{
    "scam_type": "primary scam methodology",
    "sophistication": "low|medium|high",
    "operating_hours": "likely operating times",
    "target_demographic": "who they target",
    "script_quality": "how polished are their scripts",
    "risk_assessment": "how dangerous",
    "recommended_countermeasures": ["list", "of", "actions"],
    "network_indicators": "signs of organized operation"
}}"""

        try:
            response = await self._generate_content(prompt)
            json_str = self._extract_json(response.text)
            return json.loads(json_str)
        except Exception as e:
            logger.error("profile_analysis_failed", error=str(e))
            return {"error": "Analysis failed"}
    
    # ==================== PRIVATE METHODS ====================
    
    async def _generate_content(self, prompt: str) -> GeminiResponse:
        """Generate content using Gemini API"""
        await self.initialize()
        
        if GENAI_AVAILABLE and self._initialized:
            # Use official SDK
            response = self.model.generate_content(prompt)
            return GeminiResponse(
                text=response.text,
                safety_ratings={},
                token_count=len(prompt.split()),
                finish_reason="STOP"
            )
        else:
            # Use REST API directly
            return await self._generate_via_api(prompt)
    
    async def _generate_via_api(self, prompt: str) -> GeminiResponse:
        """Generate content via REST API (fallback)"""
        url = f"{self.API_URL}/{self.MODEL_NAME}:generateContent"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "safetySettings": self.SAFETY_SETTINGS,
            "generationConfig": self.GENERATION_CONFIG
        }
        
        params = {"key": self.api_key}
        
        async with self.session.post(url, params=params, json=payload) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(f"Gemini API error: {resp.status} - {error_text}")
            
            data = await resp.json()
            
            # Extract text from response
            candidates = data.get("candidates", [])
            if not candidates:
                raise Exception("No response from Gemini")
            
            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            return GeminiResponse(
                text=text,
                safety_ratings=candidates[0].get("safetyRatings", {}),
                token_count=data.get("usageMetadata", {}).get("totalTokenCount", 0),
                finish_reason=candidates[0].get("finishReason", "UNKNOWN")
            )
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from Gemini response"""
        # Find JSON between curly braces
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return text[start:end+1]
        
        # Try finding array
        start = text.find('[')
        end = text.rfind(']')
        if start != -1 and end != -1:
            return text[start:end+1]
        
        return text
    
    def _validate_entity(self, entity: Dict) -> bool:
        """Validate extracted entity"""
        required = ["type", "value", "confidence"]
        if not all(k in entity for k in required):
            return False
        
        # Validate confidence
        if not 0 <= entity.get("confidence", 0) <= 1:
            return False
        
        # Validate entity type
        valid_types = ["upi_id", "phone_number", "bank_account", "ifsc_code", 
                       "email", "amount", "otp", "card_number", "cvv"]
        if entity.get("type") not in valid_types:
            return False
        
        return True
    
    def _default_analysis(self) -> Dict[str, Any]:
        """Default analysis when Gemini fails"""
        return {
            "is_scam": False,
            "threat_score": 0.0,
            "scam_type": "None",
            "confidence": 0.0,
            "indicators": [],
            "urgency_level": "low",
            "financial_requests": [],
            "red_flags": [],
            "recommended_action": "continue_monitoring",
            "explanation": "Analysis failed, defaulting to safe"
        }
    
    def _fallback_bait_response(self, persona: str) -> str:
        """Fallback response when Gemini fails"""
        fallbacks = {
            "confused_senior": "Arre, kya bol rahe hain aap? Thoda dheere boliye, samajh nahi aaya.",
            "cautious_professional": "I need to verify this. Can you send me official documentation?",
            "trusting_homemaker": "Beta, mujhe yeh sab samajh nahi aata. Mere pati se baat karein?"
        }
        return fallbacks.get(persona, fallbacks["confused_senior"])
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            self.session = None


# Singleton instance
gemini_client: Optional[GeminiClient] = None

async def get_gemini_client() -> GeminiClient:
    """Get or create Gemini client singleton"""
    global gemini_client
    if gemini_client is None:
        gemini_client = GeminiClient()
        await gemini_client.initialize()
    return gemini_client
