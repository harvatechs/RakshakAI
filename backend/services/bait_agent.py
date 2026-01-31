"""
RakshakAI - Bait Agent Service
AI-powered conversational agent that engages scammers to waste their time
and extract intelligence for law enforcement.
"""

import asyncio
import json
import re
import time
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

import structlog

from core.config import settings
from services.intelligence_extractor import IntelligenceExtractor

logger = structlog.get_logger("rakshak.bait")


@dataclass
class ConversationState:
    """Tracks the state of a bait conversation."""
    call_id: str
    started_at: datetime
    persona: str
    transcript_history: List[Dict[str, str]] = field(default_factory=list)
    intelligence_extracted: List[Dict[str, Any]] = field(default_factory=list)
    scammer_patience_level: float = 1.0  # Decreases as conversation continues
    engagement_stage: str = "initial"  # initial, building_trust, extracting, terminating
    total_responses: int = 0
    last_activity: datetime = field(default_factory=datetime.utcnow)


class BaitAgent:
    """
    AI Bait Agent that engages scammers with a convincing persona.
    
    The agent:
    1. Maintains a consistent persona (confused senior citizen)
    2. Asks questions to prolong the conversation
    3. Extracts intelligence (UPI IDs, bank accounts, phone numbers)
    4. Never reveals it is an AI
    5. Provides realistic human-like responses with delays and imperfections
    """
    
    # Persona definitions
    PERSONAS = {
        "confused_senior": {
            "name": "Ramesh Kumar",
            "age": 68,
            "background": "Retired government employee, not tech-savvy",
            "speech_patterns": [
                "speaks slowly", "uses formal Hindi-English mix",
                "often asks for repetition", "gets confused by technical terms",
                "trusts authority figures", "polite and respectful"
            ],
            "personality_traits": [
                "confused by technology", "worried about legal issues",
                "wants to do the right thing", "easily intimidated",
                "hard of hearing sometimes", "speaks loudly"
            ]
        },
        "cautious_professional": {
            "name": "Suresh Patel",
            "age": 45,
            "background": "Business owner, somewhat tech-aware",
            "speech_patterns": [
                "professional tone", "asks probing questions",
                "takes time to verify", "suspicious but polite"
            ],
            "personality_traits": [
                "cautious", "detail-oriented", "questions authority",
                "wants documentation", "busy and distracted"
            ]
        },
        "trusting_homemaker": {
            "name": "Lakshmi Devi",
            "age": 55,
            "background": "Homemaker, uses basic smartphone",
            "speech_patterns": [
                "soft spoken", "uses 'beta' to address",
                "asks family-related questions", "concerned about safety"
            ],
            "personality_traits": [
                "trusting", "family-oriented", "worried about security",
                "not familiar with banking procedures", "respectful"
            ]
        }
    }
    
    def __init__(self):
        self.active_engagements: Dict[str, ConversationState] = {}
        self.intelligence_extractor = IntelligenceExtractor()
        self._initialized = False
        
    async def initialize(self):
        """Initialize the bait agent."""
        if self._initialized:
            return
            
        await self.intelligence_extractor.initialize()
        self._initialized = True
        logger.info("bait_agent_initialized")
    
    async def start_engagement(
        self,
        call_id: str,
        persona: Optional[str] = None,
        extraction_enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Start a new bait engagement.
        
        Args:
            call_id: Unique call identifier
            persona: Persona to use (confused_senior, cautious_professional, trusting_homemaker)
            extraction_enabled: Whether to extract intelligence
        
        Returns:
            Initial response from the agent
        """
        await self.initialize()
        
        persona_key = persona or settings.bait_agent_persona
        if persona_key not in self.PERSONAS:
            persona_key = "confused_senior"
        
        # Create conversation state
        state = ConversationState(
            call_id=call_id,
            started_at=datetime.utcnow(),
            persona=persona_key
        )
        
        self.active_engagements[call_id] = state
        
        persona_data = self.PERSONAS[persona_key]
        
        logger.info(
            "bait_engagement_started",
            call_id=call_id,
            persona=persona_key,
            name=persona_data["name"]
        )
        
        # Generate initial response
        initial_response = await self._generate_initial_greeting(state)
        
        return {
            "call_id": call_id,
            "agent_name": persona_data["name"],
            "response_text": initial_response,
            "state": "engaging"
        }
    
    async def process_caller_input(
        self,
        call_id: str,
        transcript: str
    ) -> Dict[str, Any]:
        """
        Process input from the scammer and generate response.
        
        This is the main interaction loop that:
        1. Analyzes scammer input for intelligence
        2. Generates appropriate persona-based response
        3. Tracks conversation state
        """
        if call_id not in self.active_engagements:
            logger.warning("engagement_not_found", call_id=call_id)
            return {"error": "Engagement not found"}
        
        state = self.active_engagements[call_id]
        state.total_responses += 1
        state.last_activity = datetime.utcnow()
        
        # Add to transcript history
        state.transcript_history.append({
            "speaker": "scammer",
            "text": transcript,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Extract intelligence from scammer input
        intelligence = await self.intelligence_extractor.extract(transcript)
        if intelligence:
            state.intelligence_extracted.extend(intelligence)
            logger.info(
                "intelligence_extracted",
                call_id=call_id,
                entities=len(intelligence)
            )
        
        # Update engagement stage
        self._update_engagement_stage(state)
        
        # Generate response
        response_text = await self._generate_response(state, transcript)
        
        # Add response to history
        state.transcript_history.append({
            "speaker": "agent",
            "text": response_text,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Simulate human-like delay
        await asyncio.sleep(self._calculate_response_delay(state))
        
        return {
            "call_id": call_id,
            "text": response_text,
            "intelligence": intelligence,
            "engagement_stage": state.engagement_stage,
            "conversation_duration": (datetime.utcnow() - state.started_at).seconds
        }
    
    async def terminate_engagement(self, call_id: str) -> Dict[str, Any]:
        """Terminate the bait engagement and return summary."""
        if call_id not in self.active_engagements:
            return {"error": "Engagement not found"}
        
        state = self.active_engagements[call_id]
        
        duration = (datetime.utcnow() - state.started_at).seconds
        
        summary = {
            "call_id": call_id,
            "duration_seconds": duration,
            "total_exchanges": state.total_responses,
            "intelligence_extracted": state.intelligence_extracted,
            "engagement_stage": state.engagement_stage,
            "transcript_summary": self._summarize_transcript(state.transcript_history)
        }
        
        # Cleanup
        del self.active_engagements[call_id]
        
        logger.info(
            "bait_engagement_terminated",
            call_id=call_id,
            duration=duration,
            intelligence_count=len(state.intelligence_extracted)
        )
        
        return summary
    
    async def _generate_initial_greeting(self, state: ConversationState) -> str:
        """Generate initial greeting based on persona."""
        persona = self.PERSONAS[state.persona]
        
        greetings = {
            "confused_senior": [
                "Hello? Kaun bol rahe hain? Thoda zor se boliye, meri hearing theek nahi hai.",
                "Haanji, main Ramesh Kumar bol raha hoon. Kaun hai aap?",
                "Hello? Kya bol rahe hain? Network thoda weak hai...",
                "Ji boliye? Maine phone utha liya hai. Kaun bol rahe hain aap?"
            ],
            "cautious_professional": [
                "Yes, this is Suresh Patel speaking. Who is this and how can I help you?",
                "Hello, Suresh here. May I know who is calling and regarding what matter?",
                "Yes, speaking. Can you please identify yourself first?"
            ],
            "trusting_homemaker": [
                "Haanji, Lakshmi bol rahi hoon. Kaun hai beta?",
                "Hello? Ji bataiye? Main sun rahi hoon.",
                "Haanji namaste. Kaun bol rahe hain aap?"
            ]
        }
        
        import random
        return random.choice(greetings.get(state.persona, greetings["confused_senior"]))
    
    async def _generate_response(
        self,
        state: ConversationState,
        scammer_input: str
    ) -> str:
        """Generate persona-appropriate response to scammer."""
        persona = self.PERSONAS[state.persona]
        
        # Analyze scammer input for intent
        scammer_lower = scammer_input.lower()
        
        # Determine response strategy based on input type
        if any(word in scammer_lower for word in ["bank", "account", "card", "otp", "pin"]):
            return await self._handle_financial_request(state, scammer_input)
        
        elif any(word in scammer_lower for word in ["police", "arrest", "case", "court", "jail", "fir"]):
            return await self._handle_threat(state, scammer_input)
        
        elif any(word in scammer_lower for word in ["urgent", "immediately", "now", "hurry", "fast"]):
            return await self._handle_urgency(state, scammer_input)
        
        elif any(word in scammer_lower for word in ["download", "install", "app", "anydesk", "link"]):
            return await self._handle_tech_request(state, scammer_input)
        
        elif any(word in scammer_lower for word in ["aadhaar", "pan", "kyc", "document"]):
            return await self._handle_verification_request(state, scammer_input)
        
        elif any(word in scammer_lower for word in ["won", "prize", "lottery", "cash", "gift"]):
            return await self._handle_prize_offer(state, scammer_input)
        
        else:
            return await self._handle_general(state, scammer_input)
    
    async def _handle_financial_request(self, state: ConversationState, input_text: str) -> str:
        """Handle requests for financial information."""
        import random
        
        responses = {
            "confused_senior": [
                "Arre, ATM card ka number? Woh toh mere chashme ke neeche likha hai... ek minute, main dhoondhta hoon... aap rukiye...",
                "OTP? Woh kya hota hai beta? Mujhe toh yeh sab nahi aata. Aap seedha seedha bataiye kya karna hai?",
                "Account number? Haan haan, passbook kahan rakhi hai... arre Biwi ji! Meri passbook kahan hai? ...aap rukiye main pooch ke aata hoon...",
                "UPI PIN? Woh toh mera beta banata hai. Woh abhi office mein hai. Main usko phone karoon?",
                "CVV number? Woh card ke peeche hota hai na? Haan haan... par mera toh chashma bhi nahi dikh raha... thoda wait kijiye..."
            ],
            "cautious_professional": [
                "Why do you need my card details? Shouldn't you already have this information if you're from the bank?",
                "I don't feel comfortable sharing OTP. Can you send me an official email or letter instead?",
                "Before I share any financial information, I need to verify your identity. Can you provide me with a reference number?",
                "My bank has always told me never to share OTP with anyone. How do I know you're really from the bank?"
            ],
            "trusting_homemaker": [
                "Beta, mujhe yeh sab samajh nahi aata. Aap mere bete se baat karoge? Woh sab sambhalta hai.",
                "OTP? Mujhe toh message aate hain par main padh nahi paati chashme ke bina... thoda rukiye...",
                "Card number batana hai? Theek hai par pehle aap apna naam bataiye? Aap kahan se bol rahe hain?"
            ]
        }
        
        return random.choice(responses.get(state.persona, responses["confused_senior"]))
    
    async def _handle_threat(self, state: ConversationState, input_text: str) -> str:
        """Handle threats and intimidation."""
        import random
        
        responses = {
            "confused_senior": [
                "Arre baap re! Arrest warrant? Maine toh kuch galat nahi kiya! Main toh imaandaar aadmi hoon! Aap meri madad kariye please!",
                "Police station? Par main toh chal bhi nahi paata itni dur... kya karoon main? Bachaiye mujhe!",
                "Case file ho gaya? Par maine toh kuch kiya hi nahi! Aapko koi galat fehmi hui hai!",
                "Jail? Nahi nahi! Mujhe mat bhejiye jail! Main poora zindagi imaandaari se jiya hoon!",
                "FIR? Woh kya hota hai? Mujhe kuch samajh nahi aa raha... main kya karoon?"
            ],
            "cautious_professional": [
                "If there's a genuine legal case, I should receive official notice. Can you provide the case number and court details?",
                "I will consult my lawyer before taking any action. Please send all documents to my registered address.",
                "Threats won't work on me. If this is legitimate, follow proper legal procedure.",
                "I need to verify this with the local police station. Can you give me your badge number and station?"
            ],
            "trusting_homemaker": [
                "Nahi nahi! Mujhe mat pakadiye! Maine kuch nahi kiya! Bhagwan kasam!",
                "Police? Par main toh ghar ki aurat hoon... main kya jaanoon? Mere pati se baat kijiye!",
                "Court case? Mujhe toh dar lag raha hai... main kya karoon? Aap bataiye na beta?"
            ]
        }
        
        return random.choice(responses.get(state.persona, responses["confused_senior"]))
    
    async def _handle_urgency(self, state: ConversationState, input_text: str) -> str:
        """Handle urgency pressure tactics."""
        import random
        
        responses = {
            "confused_senior": [
                "Abhi? Par main toh bathroom mein tha... ek minute aane dijiye...",
                "Jaldi? Haan haan par mera chashma kahan hai... bina uske kuch dikh nahi raha...",
                "24 ghante? Theek hai theek hai... par pehle mujhe chai pee leni hai... aap rukiye...",
                "Arre itni jaldi? Main toh dawai khaane ja raha tha... baad mein baat karein?",
                "Immediate? Woh kya hota hai? Hindi mein samjhaiye na?"
            ],
            "cautious_professional": [
                "I need time to verify this. Nothing is so urgent that it can't wait for proper verification.",
                "I'm currently in a meeting. I can call back in 2 hours after I've verified your credentials.",
                "Urgency is a red flag for scams. I'll contact my bank directly through their official number.",
                "If it's truly urgent, send me official documentation. I won't act based on a phone call."
            ],
            "trusting_homemaker": [
                "Beta, itni jaldi nahi hoti. Pehle main apne pati se pooch loon?",
                "Abhi? Par main toh khana bana rahi hoon... thodi der baad phone karein?",
                "Jaldi? Theek hai par pehle aap apna poora naam bataiye?"
            ]
        }
        
        return random.choice(responses.get(state.persona, responses["confused_senior"]))
    
    async def _handle_tech_request(self, state: ConversationState, input_text: str) -> str:
        """Handle requests to install apps or download software."""
        import random
        
        responses = {
            "confused_senior": [
                "App download? Mujhe toh yeh sab nahi aata beta. Mera phone toh bas call karne ke liye hai.",
                "AnyDesk? Woh kya hai? Khaane ki cheez hai? Mujhe samajh nahi aa raha...",
                "Link pe click karna hai? Kaunsa link? Mujhe dikh nahi raha... kahan hai?",
                "Install karna hai? Par main toh button daba bhi nahi paata dhang se... aap samjha sakte hain?",
                "Screen sharing? Woh kya hota hai? Mera TV wala screen? Ya phone wala?"
            ],
            "cautious_professional": [
                "I never install software from unknown sources. This is a security risk.",
                "Remote access? Absolutely not. That's how accounts get compromised.",
                "I'll need to consult my IT department before installing anything.",
                "Send me the official app name from Play Store. I'll download it myself."
            ],
            "trusting_homemaker": [
                "Beta, mujhe phone mein yeh sab nahi aata. Aap mere bete ko phone karein?",
                "Download? Woh kaise karte hain? Mujhe toh bas WhatsApp chalana aata hai...",
                "Link? Kaunsa link? Mujhe kuch samajh nahi aa raha... aap aake kar doge?"
            ]
        }
        
        return random.choice(responses.get(state.persona, responses["confused_senior"]))
    
    async def _handle_verification_request(self, state: ConversationState, input_text: str) -> str:
        """Handle KYC/verification requests."""
        import random
        
        responses = {
            "confused_senior": [
                "KYC? Woh kya hota hai? Kuch saal pehle toh bank mein karwaya tha... phir se karna hai?",
                "Aadhaar card? Haan hai mere paas... par woh toh locker mein hai... abhi nikaaloon?",
                "PAN card? Haan haan... par number yaad nahi hai... card kahan rakha hai... dhoondhna padega...",
                "Document upload? Woh kaise karte hain? Mujhe toh photo kheenchana bhi nahi aata phone se...",
                "Verification? Theek hai par pehle aap apna ID toh dikhaiye?"
            ],
            "cautious_professional": [
                "KYC updates are done at the branch. I don't do this over phone.",
                "I'll visit my bank branch for any KYC related matters. Thank you.",
                "Send me official notification letter. I'll respond through proper channels.",
                "My KYC was updated recently. There must be some mistake."
            ],
            "trusting_homemaker": [
                "KYC? Mujhe nahi pata beta. Mera sab pati sambhalte hain.",
                "Aadhaar? Haan hai par main kyun doon aapko? Aap kaun hain?",
                "Document? Mere paas toh bas rashan card hai... woh chalega?"
            ]
        }
        
        return random.choice(responses.get(state.persona, responses["confused_senior"]))
    
    async def _handle_prize_offer(self, state: ConversationState, input_text: str) -> str:
        """Handle lottery/prize offers."""
        import random
        
        responses = {
            "confused_senior": [
                "25 lakh? Sach mein? Arre waah! Main toh ameer ho gaya! Kaise milega?",
                "iPhone jeeta? Mujhe? Par maine toh kuch kharida hi nahi Amazon se...",
                "Lucky draw? Meri kismat khul gayi! Bhagwan ka lakh lakh shukar hai!",
                "Cash prize? Itna saara paisa? Main kya karunga? Mere bachon ko de doon?",
                "Congratulations? Haan haan thank you! Ab paisa kaise aayega?"
            ],
            "cautious_professional": [
                "I didn't enter any lucky draw. This sounds suspicious.",
                "If I've won something, send me official documentation. No advance fees.",
                "This is a common scam pattern. I won't be paying any processing fees.",
                "I'll contact KBC/Amazon directly through their official channels to verify."
            ],
            "trusting_homemaker": [
                "Itna paisa? Sach bol rahe hain na beta? Dhoka toh nahi hai na?",
                "Jeet gayi? Main? Bhagwan ki kripa hai! Par pehle processing fee kyun?",
                "Prize? Achha hai! Par mujhe paise dene hain pehle? Woh toh theek nahi hai na?"
            ]
        }
        
        return random.choice(responses.get(state.persona, responses["confused_senior"]))
    
    async def _handle_general(self, state: ConversationState, input_text: str) -> str:
        """Handle general conversation."""
        import random
        
        responses = {
            "confused_senior": [
                "Haanji? Kuch samajh nahi aaya... aap dobara boliye?",
                "Arre? Kya bola aapne? Network weak hai... zor se boliye...",
                "Ji? Main sun raha hoon... aage bataiye...",
                "Theek hai theek hai... par thoda dheere boliye...",
                "Haan haan... samajh gaya... matlab? Woh kya hota hai?"
            ],
            "cautious_professional": [
                "I see. Can you provide more details about this?",
                "I need to understand this better. Please explain.",
                "I'm taking notes. Please continue.",
                "Let me verify this information. One moment."
            ],
            "trusting_homemaker": [
                "Achha? Phir? Aage kya hua?",
                "Haanji beta, main sun rahi hoon...",
                "Theek hai... aap bataiye main kya karoon?",
                "Samajh gayi... par mujhe dar lag raha hai..."
            ]
        }
        
        return random.choice(responses.get(state.persona, responses["confused_senior"]))
    
    def _update_engagement_stage(self, state: ConversationState):
        """Update the engagement stage based on conversation progress."""
        if state.total_responses < 3:
            state.engagement_stage = "initial"
        elif state.total_responses < 8:
            state.engagement_stage = "building_trust"
        elif state.total_responses < 15:
            state.engagement_stage = "extracting"
        else:
            state.engagement_stage = "terminating"
    
    def _calculate_response_delay(self, state: ConversationState) -> float:
        """Calculate human-like response delay."""
        import random
        
        # Base delay: 1-3 seconds
        base_delay = random.uniform(1.0, 3.0)
        
        # Add delay for "confused" persona
        if state.persona == "confused_senior":
            base_delay += random.uniform(0.5, 2.0)
        
        # Add delay for longer conversations (simulating fatigue)
        if state.total_responses > 10:
            base_delay += random.uniform(0.5, 1.5)
        
        return min(base_delay, 5.0)  # Cap at 5 seconds
    
    def _summarize_transcript(self, history: List[Dict[str, str]]) -> str:
        """Create a summary of the conversation."""
        scammer_messages = [h["text"] for h in history if h["speaker"] == "scammer"]
        agent_messages = [h["text"] for h in history if h["speaker"] == "agent"]
        
        return f"Conversation with {len(scammer_messages)} scammer messages and {len(agent_messages)} agent responses."
    
    async def cleanup(self):
        """Cleanup resources."""
        self.active_engagements.clear()
        logger.info("bait_agent_cleaned_up")
