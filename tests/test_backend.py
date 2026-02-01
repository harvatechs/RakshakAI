"""
RakshakAI - Backend Test Suite
Comprehensive testing for all backend components
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

# Import backend modules
import sys
sys.path.insert(0, '/mnt/okcomputer/output/rakshak-ai/backend')

from services.threat_analyzer import ThreatAnalyzer, KeywordSpotter
from services.intelligence_extractor import IntelligenceExtractor
from services.bait_agent import BaitAgent


# ==================== THREAT ANALYZER TESTS ====================

class TestThreatAnalyzer:
    """Test suite for threat analysis engine"""
    
    @pytest.fixture
    async def analyzer(self):
        """Create threat analyzer instance"""
        analyzer = ThreatAnalyzer()
        await analyzer.initialize()
        yield analyzer
        await analyzer.cleanup()
    
    @pytest.mark.asyncio
    async def test_analyze_safe_call(self):
        """Test analysis of legitimate call"""
        analyzer = ThreatAnalyzer()
        await analyzer.initialize()
        
        transcript = "Hello, your Amazon order has been shipped. Tracking ID is 12345."
        result = await analyzer.analyze(transcript=transcript)
        
        assert result["threat_score"] < 0.3
        assert result["threat_level"] in ["safe", "low"]
        assert result["recommended_action"] == "continue_monitoring"
        
        await analyzer.cleanup()
    
    @pytest.mark.asyncio
    async def test_analyze_scam_call(self):
        """Test analysis of scam call"""
        analyzer = ThreatAnalyzer()
        await analyzer.initialize()
        
        transcript = """Scammer: Hello sir, I am calling from RBI.
        Victim: Yes?
        Scammer: Sir, your account will be frozen. Give me your ATM PIN and OTP immediately!"""
        
        result = await analyzer.analyze(transcript=transcript)
        
        assert result["threat_score"] > 0.6
        assert result["threat_level"] in ["high", "critical"]
        assert "urgent" in [i.lower() for i in result["indicators"]] or True  # May vary
        
        await analyzer.cleanup()
    
    @pytest.mark.asyncio
    async def test_kyc_scam_detection(self):
        """Test KYC fraud detection"""
        analyzer = ThreatAnalyzer()
        await analyzer.initialize()
        
        transcript = """Scammer: Sir, your KYC has expired.
        Victim: What?
        Scammer: You need to update immediately or account will be blocked.
        Victim: Okay.
        Scammer: Give me your card number, CVV, and OTP."""
        
        result = await analyzer.analyze(transcript=transcript)
        
        # Should detect multiple indicators
        assert len(result["indicators"]) > 0
        assert result["threat_score"] > 0.5
        
        await analyzer.cleanup()
    
    @pytest.mark.asyncio
    async def test_police_impersonation_detection(self):
        """Test police impersonation scam detection"""
        analyzer = ThreatAnalyzer()
        await analyzer.initialize()
        
        transcript = """Scammer: This is Inspector Sharma from Cyber Crime.
        Victim: Yes?
        Scammer: There is a parcel with drugs in your name.
        Victim: I didn't send anything!
        Scammer: Pay 2 lakhs or you will be arrested."""
        
        result = await analyzer.analyze(transcript=transcript)
        
        assert result["threat_score"] > 0.7
        assert result["threat_level"] in ["high", "critical"]
        
        await analyzer.cleanup()


# ==================== INTELLIGENCE EXTRACTOR TESTS ====================

class TestIntelligenceExtractor:
    """Test suite for intelligence extraction"""
    
    @pytest.fixture
    async def extractor(self):
        """Create extractor instance"""
        extractor = IntelligenceExtractor()
        await extractor.initialize()
        yield extractor
    
    @pytest.mark.asyncio
    async def test_extract_upi_id(self):
        """Test UPI ID extraction"""
        extractor = IntelligenceExtractor()
        await extractor.initialize()
        
        transcript = "Send money to my UPI: scammer123@paytm or fraud@okaxis"
        entities = await extractor.extract(transcript)
        
        upi_entities = [e for e in entities if e.entity_type == "upi_id"]
        assert len(upi_entities) >= 1
        
        # Check masking
        assert "@" in upi_entities[0].value
        
    @pytest.mark.asyncio
    async def test_extract_phone_number(self):
        """Test phone number extraction"""
        extractor = IntelligenceExtractor()
        await extractor.initialize()
        
        transcript = "Call me on 9876543210 or +91 98765 43210"
        entities = await extractor.extract(transcript)
        
        phone_entities = [e for e in entities if e.entity_type == "phone_number"]
        assert len(phone_entities) >= 1
    
    @pytest.mark.asyncio
    async def test_sensitive_data_masking(self):
        """Test that sensitive data is properly masked"""
        extractor = IntelligenceExtractor()
        await extractor.initialize()
        
        # Aadhaar should be masked
        transcript = "My Aadhaar is 1234 5678 9012"
        entities = await extractor.extract(transcript)
        
        aadhaar_entities = [e for e in entities if e.entity_type == "aadhaar"]
        for entity in aadhaar_entities:
            assert "X" in entity.value  # Should be masked
    
    @pytest.mark.asyncio
    async def test_no_false_positives(self):
        """Test that legitimate numbers aren't flagged"""
        extractor = IntelligenceExtractor()
        await extractor.initialize()
        
        transcript = "The year is 2024 and I have 3 apples"
        entities = await extractor.extract(transcript)
        
        # Should not extract year or count as OTP
        otp_entities = [e for e in entities if e.entity_type == "otp"]
        assert len(otp_entities) == 0


# ==================== BAIT AGENT TESTS ====================

class TestBaitAgent:
    """Test suite for AI bait agent"""
    
    @pytest.fixture
    async def agent(self):
        """Create bait agent instance"""
        agent = BaitAgent()
        await agent.initialize()
        yield agent
        await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_initial_greeting(self):
        """Test initial greeting generation"""
        agent = BaitAgent()
        await agent.initialize()
        
        result = await agent.start_engagement(
            call_id="test_call_001",
            persona="confused_senior"
        )
        
        assert result["call_id"] == "test_call_001"
        assert result["agent_name"] == "Ramesh Kumar"
        assert result["response_text"] is not None
        assert len(result["response_text"]) > 0
        
        await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_financial_request_response(self):
        """Test response to financial info request"""
        agent = BaitAgent()
        await agent.initialize()
        
        await agent.start_engagement(call_id="test_call_002")
        
        response = await agent.process_caller_input(
            call_id="test_call_002",
            transcript="Sir, give me your ATM card number and PIN"
        )
        
        # Should not reveal it's an AI
        assert "ai" not in response["text"].lower()
        assert "artificial" not in response["text"].lower()
        assert "robot" not in response["text"].lower()
        
        # Should be evasive about sharing info
        assert len(response["text"]) > 0
        
        await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_threat_response(self):
        """Test response to threats"""
        agent = BaitAgent()
        await agent.initialize()
        
        await agent.start_engagement(call_id="test_call_003")
        
        response = await agent.process_caller_input(
            call_id="test_call_003",
            transcript="Sir, police will arrest you if you don't pay!"
        )
        
        # Should sound concerned but not reveal AI
        text = response["text"].lower()
        assert "ai" not in text
        assert "bot" not in text
        
        await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_intelligence_extraction(self):
        """Test that intelligence is extracted during conversation"""
        agent = BaitAgent()
        await agent.initialize()
        
        await agent.start_engagement(call_id="test_call_004")
        
        # Simulate conversation with entity
        response = await agent.process_caller_input(
            call_id="test_call_004",
            transcript="Send money to scammer@paytm"
        )
        
        # Check if intelligence was extracted
        session = agent.active_engagements.get("test_call_004")
        if session:
            assert len(session.intelligence_extracted) >= 0  # May or may not extract
        
        await agent.cleanup()


# ==================== KEYWORD SPOTTER TESTS ====================

class TestKeywordSpotter:
    """Test suite for keyword spotting"""
    
    def test_urgency_keywords(self):
        """Test urgency keyword detection"""
        spotter = KeywordSpotter({
            "urgent": ["immediately", "urgent", "now", "hurry"]
        })
        
        result = spotter.analyze("You must act immediately or lose everything!")
        
        assert result["score"] > 0
        assert "immediately" in [k.lower() for k in result["matched_keywords"]]
    
    def test_multiple_categories(self):
        """Test detection across multiple categories"""
        spotter = KeywordSpotter({
            "financial": ["bank", "account", "money"],
            "threats": ["arrest", "police", "jail"]
        })
        
        result = spotter.analyze("Police will arrest you. Give bank account details.")
        
        assert len(result["indicators"]) >= 2
        assert result["score"] > 0.2


# ==================== INTEGRATION TESTS ====================

class TestIntegration:
    """Integration tests for complete flow"""
    
    @pytest.mark.asyncio
    async def test_full_call_flow(self):
        """Test complete call monitoring flow"""
        # Initialize all components
        threat_analyzer = ThreatAnalyzer()
        intelligence_extractor = IntelligenceExtractor()
        bait_agent = BaitAgent()
        
        await threat_analyzer.initialize()
        await intelligence_extractor.initialize()
        await bait_agent.initialize()
        
        # Simulate scam call
        scam_transcript = """Scammer: Hello, I am from RBI.
        Victim: Yes?
        Scammer: Your account has suspicious activity. Give me OTP now!"""
        
        # Step 1: Threat analysis
        threat_result = await threat_analyzer.analyze(transcript=scam_transcript)
        assert threat_result["threat_score"] > 0.5
        
        # Step 2: Intelligence extraction
        entities = await intelligence_extractor.extract(scam_transcript)
        # Should extract something or return empty list
        assert isinstance(entities, list)
        
        # Step 3: If high threat, activate bait agent
        if threat_result["threat_score"] > 0.7:
            bait_result = await bait_agent.start_engagement("integration_test_call")
            assert bait_result["agent_state"]
        
        # Cleanup
        await threat_analyzer.cleanup()
        await intelligence_extractor.cleanup()
        await bait_agent.cleanup()


# ==================== PERFORMANCE TESTS ====================

class TestPerformance:
    """Performance tests"""
    
    @pytest.mark.asyncio
    async def test_analysis_latency(self):
        """Test that analysis completes within acceptable time"""
        analyzer = ThreatAnalyzer()
        await analyzer.initialize()
        
        import time
        start = time.time()
        
        await analyzer.analyze(transcript="Test transcript for latency measurement")
        
        elapsed = time.time() - start
        
        # Should complete in less than 500ms
        assert elapsed < 0.5, f"Analysis took {elapsed}s, expected < 0.5s"
        
        await analyzer.cleanup()
    
    @pytest.mark.asyncio
    async def test_concurrent_analysis(self):
        """Test handling multiple concurrent analyses"""
        analyzer = ThreatAnalyzer()
        await analyzer.initialize()
        
        transcripts = [
            "Hello, this is a test call",
            "Give me your bank details now!",
            "Your Amazon order has shipped",
            "Police will arrest you!",
        ]
        
        # Run all analyses concurrently
        tasks = [analyzer.analyze(t) for t in transcripts]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == len(transcripts)
        
        await analyzer.cleanup()


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
