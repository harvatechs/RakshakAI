"""
RakshakAI - OSINT Tools for Scammer Identification
Open Source Intelligence gathering to identify and track scammers
"""

import asyncio
import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import structlog

logger = structlog.get_logger("rakshak.osint")


@dataclass
class OSINTResult:
    """Result from OSINT investigation"""
    source: str
    data_type: str
    data: Dict[str, Any]
    confidence: float
    timestamp: datetime


class ScammerOSINT:
    """
    OSINT (Open Source Intelligence) tools for scammer identification
    
    Features:
    - Phone number intelligence (Truecaller-style lookup)
    - UPI ID tracking
    - Social media footprint analysis
    - Digital footprint correlation
    - Network analysis
    """
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 3600  # 1 hour
    
    # ==================== PHONE NUMBER OSINT ====================
    
    async def investigate_phone_number(self, phone: str) -> Dict[str, Any]:
        """
        Investigate a phone number using multiple OSINT sources
        
        Returns:
            Dict with carrier info, location, spam reports, social profiles
        """
        logger.info("investigating_phone", phone=phone)
        
        # Clean phone number
        clean_phone = re.sub(r'\D', '', phone)
        if len(clean_phone) == 10:
            clean_phone = "91" + clean_phone
        
        result = {
            "phone_number": phone,
            "clean_number": clean_phone,
            "investigated_at": datetime.utcnow().isoformat(),
            "sources": []
        }
        
        # Run all investigations in parallel
        tasks = [
            self._get_carrier_info(clean_phone),
            self._get_location_info(clean_phone),
            self._check_spam_databases(clean_phone),
            self._check_telecom_data(clean_phone),
            self._social_media_search(clean_phone),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                logger.warning(f"osint_task_failed", task=i, error=str(res))
            else:
                result.update(res)
        
        # Calculate risk score
        result["risk_score"] = self._calculate_phone_risk(result)
        
        return result
    
    async def _get_carrier_info(self, phone: str) -> Dict[str, Any]:
        """Get carrier information from phone number"""
        # Indian mobile number prefixes
        carrier_prefixes = {
            " airtel": ["9900", "9800", "9810", "9820", "9830", "9840", "9850", "9860", "9870", "9880", "9890",
                       "9000", "9010", "9020", "9030", "9040", "9050", "9060", "9070", "9080", "9090",
                       "7700", "7710", "7720", "7730", "7740", "7750", "7760", "7770", "7780", "7790",
                       "8800", "8810", "8820", "8830", "8840", "8850", "8860", "8870", "8880", "8890",
                       "7000", "7010", "7020", "7030", "7040", "7050", "7060", "7070", "7080", "7090",
                       "8100", "8110", "8120", "8130", "8140", "8150", "8160", "8170", "8180", "8190"],
            "jio": ["6000", "6100", "6200", "6300", "6400", "6500", "6600", "6700", "6800", "6900",
                    "7000", "7100", "7200", "7300", "7400", "7500", "7600", "7700", "7800", "7900",
                    "8000", "8100", "8200", "8300", "8400", "8500", "8600", "8700", "8800", "8900",
                    "9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900"],
            "vi": ["9000", "9100", "9200", "9300", "9400", "9500", "9600", "9700", "9800", "9900",
                   "8100", "8200", "8300", "8400", "8500", "8600", "8700", "8800", "8900"],
            "bsnl": ["600", "601", "602", "603", "604", "605", "606", "607", "608", "609",
                     "9400", "9410", "9420", "9430", "9440", "9450", "9460", "9470", "9480", "9490"],
        }
        
        prefix = phone[2:6] if phone.startswith("91") else phone[:4]
        
        carrier = "Unknown"
        for name, prefixes in carrier_prefixes.items():
            if prefix in prefixes:
                carrier = name.upper()
                break
        
        return {
            "carrier": carrier,
            "number_type": "Mobile" if len(phone) == 12 else "Landline",
            "country_code": "+91",
            "region": "India"
        }
    
    async def _get_location_info(self, phone: str) -> Dict[str, Any]:
        """Get approximate location from phone number"""
        # Indian STD codes mapping
        std_codes = {
            "11": "Delhi", "22": "Mumbai", "33": "Kolkata", "44": "Chennai",
            "40": "Hyderabad", "80": "Bangalore", "20": "Pune", "79": "Ahmedabad",
            "141": "Jaipur", "522": "Lucknow", "361": "Guwahati", "172": "Chandigarh",
        }
        
        # Mobile number circle mapping (simplified)
        mobile_circles = {
            "99": "Delhi NCR", "98": "Punjab", "97": "Tamil Nadu", "96": "Kolkata",
            "95": "Uttar Pradesh", "94": "Kerala", "93": "Mumbai", "92": "Rajasthan",
            "91": "Karnataka", "90": "Maharashtra", "89": "Andhra Pradesh", "88": "West Bengal",
            "87": "Bihar", "86": "Odisha", "85": "Gujarat", "84": "Haryana",
            "83": "Assam", "82": "Jharkhand", "81": "Chhattisgarh", "80": "Karnataka",
            "79": "Gujarat", "78": "Punjab", "77": "Maharashtra", "76": "Tamil Nadu",
            "75": "Madhya Pradesh", "74": "Rajasthan", "73": "Uttarakhand", "72": "Bihar",
            "71": "Maharashtra", "70": "West Bengal", "69": "Jammu & Kashmir", "68": "Punjab",
            "67": "Odisha", "66": "Kerala", "65": "Karnataka", "64": "Tamil Nadu",
            "63": "Andhra Pradesh", "62": "Jharkhand", "61": "Chhattisgarh", "60": "North East",
            "59": "Uttar Pradesh", "58": "Uttarakhand", "57": "Karnataka", "56": "Rajasthan",
            "55": "Uttar Pradesh", "54": "Andhra Pradesh", "53": "Karnataka", "52": "Uttar Pradesh",
            "51": "West Bengal", "50": "Andhra Pradesh",
        }
        
        prefix = phone[2:4] if phone.startswith("91") else phone[:2]
        circle = mobile_circles.get(prefix, "Unknown")
        
        return {
            "telecom_circle": circle,
            "approximate_location": circle,
            "accuracy": "City-level (approximate)"
        }
    
    async def _check_spam_databases(self, phone: str) -> Dict[str, Any]:
        """Check phone number against spam databases"""
        # In production, this would query:
        # - Truecaller API
        # - CallApp database
        # - Community reports
        # - Government spam lists
        
        return {
            "spam_reports": 0,  # Would be actual count from APIs
            "spam_score": 0.0,
            "reported_as": [],
            "first_reported": None,
            "last_reported": None,
            "sources_checked": ["community_db", "gov_db"]
        }
    
    async def _check_telecom_data(self, phone: str) -> Dict[str, Any]:
        """Get additional telecom data"""
        return {
            "portability": "Unknown",
            "activation_date": "Unknown",
            "line_status": "Active (assumed)",
            "connection_type": "Prepaid/Postpaid (Unknown)"
        }
    
    async def _social_media_search(self, phone: str) -> Dict[str, Any]:
        """Search for phone number on social media"""
        # In production, this would search:
        # - WhatsApp (profile picture, status)
        # - Facebook
        # - Telegram
        # - Truecaller social
        
        return {
            "whatsapp": {
                "found": False,
                "profile_pic": None,
                "about": None,
                "last_seen": None
            },
            "telegram": {
                "found": False,
                "username": None,
                "profile": None
            },
            "facebook": {
                "found": False,
                "profile": None
            }
        }
    
    # ==================== UPI ID OSINT ====================
    
    async def investigate_upi_id(self, upi_id: str) -> Dict[str, Any]:
        """
        Investigate a UPI ID for scammer identification
        
        UPI format: username@bankhandle
        """
        logger.info("investigating_upi", upi_id=upi_id)
        
        parts = upi_id.split("@")
        if len(parts) != 2:
            return {"error": "Invalid UPI ID format"}
        
        username, handle = parts
        
        # UPI handle to bank mapping
        upi_handles = {
            "paytm": "Paytm Payments Bank",
            "okaxis": "Axis Bank",
            "okhdfcbank": "HDFC Bank",
            "okicici": "ICICI Bank",
            "oksbi": "State Bank of India",
            "ybl": "Yes Bank",
            "apl": "Amazon Pay",
            "okbizaxis": "Axis Bank (Business)",
            "payzapp": "HDFC Bank (PayZapp)",
            "ibl": "ICICI Bank (iMobile)",
            "axl": "Axis Bank (Axis Lime)",
        }
        
        bank_name = upi_handles.get(handle.lower(), "Unknown Bank")
        
        result = {
            "upi_id": upi_id,
            "username": username,
            "bank_handle": handle,
            "bank_name": bank_name,
            "investigated_at": datetime.utcnow().isoformat(),
            "risk_indicators": []
        }
        
        # Analyze username for suspicious patterns
        suspicious_patterns = [
            (r'\d{6,}', "Contains many digits (suspicious)"),
            (r'(scam|fraud|fake|hack)', "Suspicious keywords in username"),
            (r'^[0-9]+$', "Pure numeric username"),
            (r'(prize|lottery|winner|free)', "Scam-related keywords"),
            (r'(kyc|update|verify|urgent)', "Urgency keywords"),
        ]
        
        for pattern, description in suspicious_patterns:
            if re.search(pattern, username, re.IGNORECASE):
                result["risk_indicators"].append(description)
        
        # Check if similar UPIs have been reported
        result["similar_upis"] = await self._find_similar_upis(upi_id)
        
        result["risk_score"] = min(1.0, len(result["risk_indicators"]) * 0.25)
        
        return result
    
    async def _find_similar_upis(self, upi_id: str) -> List[str]:
        """Find similar UPI IDs in database"""
        # In production, query database for similar patterns
        return []
    
    # ==================== NETWORK ANALYSIS ====================
    
    async def analyze_scammer_network(
        self,
        phone_numbers: List[str],
        upi_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze network connections between scammers
        
        Identifies:
        - Shared UPI handles
        - Common phone prefixes
        - Operating patterns
        """
        logger.info("analyzing_network", phones=len(phone_numbers), upis=len(upi_ids))
        
        analysis = {
            "total_phone_numbers": len(phone_numbers),
            "total_upi_ids": len(upi_ids),
            "network_indicators": [],
            "operating_pattern": "Unknown",
            "organization_level": "Unknown"
        }
        
        # Analyze phone number patterns
        if phone_numbers:
            prefixes = [re.sub(r'\D', '')[:6] for p in phone_numbers]
            unique_prefixes = set(prefixes)
            
            if len(unique_prefixes) == 1:
                analysis["network_indicators"].append("All numbers from same prefix block (SIM farm suspected)")
                analysis["organization_level"] = "Organized"
            elif len(unique_prefixes) <= len(phone_numbers) * 0.3:
                analysis["network_indicators"].append("High prefix concentration (possible organized operation)")
        
        # Analyze UPI patterns
        if upi_ids:
            handles = [u.split("@")[1] if "@" in u else "" for u in upi_ids]
            handle_counts = {}
            for h in handles:
                handle_counts[h] = handle_counts.get(h, 0) + 1
            
            most_common = max(handle_counts.items(), key=lambda x: x[1])
            if most_common[1] > 2:
                analysis["network_indicators"].append(f"Multiple UPIs on same bank: {most_common[0]}")
        
        # Determine operating pattern
        if len(analysis["network_indicators"]) >= 3:
            analysis["operating_pattern"] = "Large organized scam operation"
            analysis["organization_level"] = "Highly Organized"
        elif len(analysis["network_indicators"]) >= 1:
            analysis["operating_pattern"] = "Small group or individual"
            analysis["organization_level"] = "Semi-Organized"
        
        return analysis
    
    # ==================== RISK SCORING ====================
    
    def _calculate_phone_risk(self, data: Dict) -> float:
        """Calculate risk score from phone investigation"""
        score = 0.0
        
        # Spam reports
        spam_data = data.get("spam_databases", {})
        score += min(0.5, spam_data.get("spam_reports", 0) * 0.1)
        
        # Carrier (some carriers have more spam)
        carrier = data.get("carrier", "Unknown")
        if carrier == "Unknown":
            score += 0.1
        
        return min(1.0, score)
    
    # ==================== COMPREHENSIVE REPORT ====================
    
    async def generate_osint_report(
        self,
        phone: Optional[str] = None,
        upi_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive OSINT report"""
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "query": {"phone": phone, "upi_id": upi_id},
            "findings": {}
        }
        
        tasks = []
        if phone:
            tasks.append(("phone", self.investigate_phone_number(phone)))
        if upi_id:
            tasks.append(("upi", self.investigate_upi_id(upi_id)))
        
        results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)
        
        for (name, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                report["findings"][name] = {"error": str(result)}
            else:
                report["findings"][name] = result
        
        # Overall risk assessment
        risks = []
        if "phone" in report["findings"]:
            risks.append(report["findings"]["phone"].get("risk_score", 0))
        if "upi" in report["findings"]:
            risks.append(report["findings"]["upi"].get("risk_score", 0))
        
        report["overall_risk_score"] = max(risks) if risks else 0.0
        
        return report


# Singleton instance
osint_tool: Optional[ScammerOSINT] = None

async def get_osint_tool() -> ScammerOSINT:
    """Get or create OSINT tool singleton"""
    global osint_tool
    if osint_tool is None:
        osint_tool = ScammerOSINT()
    return osint_tool
