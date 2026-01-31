"""
RakshakAI - Synthetic Dataset Generator
Generates realistic scam and legitimate call transcripts for training.
"""

import json
import random
from typing import List, Dict
from dataclasses import dataclass, asdict

import structlog

logger = structlog.get_logger("rakshak.dataset")


@dataclass
class CallTranscript:
    """Represents a call transcript with metadata."""
    id: str
    label: str  # "scam" or "legitimate"
    category: str  # e.g., "kyc_fraud", "tech_support", "normal_call"
    transcript: str
    scam_type: str = None
    indicators: List[str] = None
    entities: Dict[str, List[str]] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class SyntheticDatasetGenerator:
    """
    Generates synthetic call transcripts for training the scam classifier.
    
    Creates realistic Indian context scam calls including:
    - KYC verification scams
    - Police/Authority impersonation
    - Tech support scams
    - Lottery/prize scams
    - Bank fraud scams
    """
    
    # Indian names for realistic transcripts
    INDIAN_NAMES = [
        "Ramesh Kumar", "Suresh Patel", "Amit Sharma", "Priya Singh",
        "Vikram Reddy", "Anita Desai", "Rajesh Gupta", "Sunita Verma",
        "Kiran Rao", "Deepak Mishra", "Lakshmi Iyer", "Arun Nair",
        "Pooja Shah", "Manoj Joshi", "Geeta Menon", "Sanjay Khanna"
    ]
    
    BANK_NAMES = [
        "State Bank of India", "HDFC Bank", "ICICI Bank", "Axis Bank",
        "Punjab National Bank", "Bank of Baroda", "Canara Bank",
        "Union Bank", "Kotak Mahindra Bank", "IndusInd Bank"
    ]
    
    UPI_HANDLES = ["paytm", "okaxis", "okhdfcbank", "okicici", "oksbi", "ybl", "apl"]
    
    def __init__(self):
        self.transcripts: List[CallTranscript] = []
    
    def generate_scam_transcript_kyc(self, index: int) -> CallTranscript:
        """Generate KYC verification scam transcript."""
        victim_name = random.choice(self.INDIAN_NAMES)
        scammer_name = random.choice(["Rahul", "Ajay", "Vijay", "Neha", "Pooja"])
        bank_name = random.choice(self.BANK_NAMES)
        
        openings = [
            f"Hello, am I speaking with {victim_name}?",
            f"Good morning sir, this is {scammer_name} calling from {bank_name} head office.",
            f"Sir, this is an urgent call regarding your {bank_name} account.",
        ]
        
        scripts = [
            f"""Scammer: {random.choice(openings)}
Scammer: Sir, your KYC verification has expired and your account will be frozen within 24 hours.
Victim: What? I don't remember any KYC expiry.
Scammer: Yes sir, RBI has made new rules. You need to update immediately or your account will be blocked.
Victim: Okay, what do I need to do?
Scammer: Sir, I will send you a link. You need to fill in your account details, ATM card number, CVV, and OTP that you will receive.
Victim: Why do you need my ATM details?
Scammer: Sir, this is for verification purpose only. RBI mandate hai. Your account will be unblocked immediately.
Victim: I am not comfortable sharing this.
Scammer: Sir, this is very urgent. If you don't do this now, your account will be permanently frozen and legal action will be taken.""",
            
            f"""Scammer: Hello, is this {victim_name}?
Victim: Yes, speaking.
Scammer: Sir, I am calling from RBI cyber security department. There are suspicious transactions from your account.
Victim: What transactions? I didn't do anything.
Scammer: Sir, someone is trying to transfer 50,000 rupees from your account. To stop this, you need to verify your identity immediately.
Victim: How do I verify?
Scammer: Sir, please tell me your account number and ATM PIN so I can block the transaction.
Victim: You want my PIN? That's not right.
Scammer: Sir, I am from RBI. This is official procedure. Give me quickly before money is gone!"""
        ]
        
        return CallTranscript(
            id=f"scam_kyc_{index:03d}",
            label="scam",
            category="kyc_fraud",
            transcript=random.choice(scripts),
            scam_type="KYC Verification Fraud",
            indicators=["urgent_kyc", "account_freeze_threat", "request_sensitive_info", "impersonation"],
            entities={"bank_names": [bank_name]}
        )
    
    def generate_scam_transcript_police(self, index: int) -> CallTranscript:
        """Generate police impersonation scam transcript."""
        victim_name = random.choice(self.INDIAN_NAMES)
        
        scripts = [
            f"""Scammer: Hello, is this {victim_name}?
Victim: Yes, who is this?
Scammer: This is Inspector Sharma from Mumbai Cyber Crime Branch. There is a serious matter regarding your name.
Victim: What matter? I haven't done anything wrong.
Scammer: Sir, we have found a parcel in your name containing illegal drugs and fake passports. This is a very serious offense.
Victim: What? I didn't send any parcel!
Scammer: Sir, the parcel was sent from Mumbai to Thailand using your Aadhaar and PAN card copies. You are the main suspect.
Victim: This is a mistake! I am innocent!
Scammer: Sir, an arrest warrant has been issued in your name. You will be arrested within 2 hours unless you cooperate.
Victim: Please, what should I do?
Scammer: Sir, you need to pay a security deposit of 2 lakhs to the court to stop the arrest warrant. Pay immediately through UPI.
Victim: 2 lakhs? I don't have that much.
Scammer: Sir, this is your only chance. Pay now or go to jail for 10 years!""",
            
            f"""Scammer: Am I speaking with {victim_name}?
Victim: Yes, tell me.
Scammer: Sir, this is Sub-Inspector Kumar from Delhi Police Narcotics Cell. Your mobile number has been linked to a drug trafficking case.
Victim: What nonsense! I am a common man.
Scammer: Sir, we have evidence. Your number was used to coordinate drug deals. CBI is also involved now.
Victim: This must be some mistake.
Scammer: Sir, we are sending a team to arrest you. But if you want to settle this matter quietly, you can pay a penalty.
Victim: What penalty?
Scammer: 5 lakh rupees. Pay through Google Pay to this number and we will close the case. Otherwise, you will be in jail tonight."""
        ]
        
        return CallTranscript(
            id=f"scam_police_{index:03d}",
            label="scam",
            category="police_impersonation",
            transcript=random.choice(scripts),
            scam_type="Police/Authority Impersonation",
            indicators=["impersonation", "arrest_threat", "drug_case", "demand_money", "urgent"],
            entities={}
        )
    
    def generate_scam_transcript_tech_support(self, index: int) -> CallTranscript:
        """Generate tech support scam transcript."""
        victim_name = random.choice(self.INDIAN_NAMES)
        
        scripts = [
            f"""Scammer: Hello, this is Microsoft Technical Support. Am I speaking with {victim_name}?
Victim: Yes, what is this about?
Scammer: Sir, we have detected a virus on your computer that is stealing your banking information.
Victim: Oh no! How did this happen?
Scammer: Sir, hackers have accessed your system. We need to fix this immediately or you will lose all your money.
Victim: Please help me!
Scammer: Sir, I need you to install AnyDesk so I can access your computer and remove the virus.
Victim: Okay, I will install it.
Scammer: Good. Once installed, give me the access code. Also, keep your ATM card ready for verification.
Victim: Why do you need my ATM card?
Scammer: Sir, this is to verify your identity with the bank. We need to make sure the virus hasn't stolen your money.""",
            
            f"""Scammer: Hello sir, this is calling from Airtel technical department.
Victim: Yes, tell me.
Scammer: Sir, your mobile number will be disconnected in 1 hour due to KYC issues.
Victim: But I did my KYC recently.
Scammer: Sir, there is a problem with your documents. To avoid disconnection, you need to download a verification app.
Victim: Which app?
Scammer: Sir, I will send you a link. Download the app and allow all permissions. It will verify your identity.
Victim: Okay, I downloaded it.
Scammer: Good sir. Now the app needs access to your SMS to verify OTP. Allow it. Also, your screen will be shared with our server for verification."""
        ]
        
        return CallTranscript(
            id=f"scam_tech_{index:03d}",
            label="scam",
            category="tech_support",
            transcript=random.choice(scripts),
            scam_type="Tech Support Scam",
            indicators=["remote_access_request", "virus_threat", "urgent", "impersonation"],
            entities={}
        )
    
    def generate_scam_transcript_lottery(self, index: int) -> CallTranscript:
        """Generate lottery/prize scam transcript."""
        victim_name = random.choice(self.INDIAN_NAMES)
        
        scripts = [
            f"""Scammer: Congratulations! Am I speaking with {victim_name}?
Victim: Yes, who is this?
Scammer: Sir, I am calling from Kaun Banega Crorepati head office. You have won 25 lakh rupees in lucky draw!
Victim: Really? I didn't participate in any draw.
Scammer: Sir, your mobile number was randomly selected from all Airtel users. This is your lucky day!
Victim: That's amazing! How do I claim?
Scammer: Sir, to claim your prize, you need to pay a processing fee of 15,000 rupees first.
Victim: Why do I need to pay?
Scammer: Sir, this is for GST and transfer charges. Once paid, the 25 lakhs will be transferred to your account within 2 hours.
Victim: Okay, where should I send?
Scammer: Sir, send through UPI to this ID: kbcprize@paytm. Hurry, offer expires today!""",
            
            f"""Scammer: Hello, congratulations from Amazon India!
Victim: What is this about?
Scammer: Sir, you have won an iPhone 15 Pro Max in our customer appreciation lucky draw!
Victim: I didn't enter any draw.
Scammer: Sir, as a regular Amazon customer, you were automatically entered. You are one of 10 lucky winners!
Victim: Great! When will I get it?
Scammer: Sir, to process your prize, we need a refundable security deposit of 5,000 rupees. This will be returned with your prize.
Victim: Okay, how do I pay?
Scammer: Sir, pay to amazonprizes@ybl through PhonePe or Google Pay. Send screenshot after payment."""
        ]
        
        return CallTranscript(
            id=f"scam_lottery_{index:03d}",
            label="scam",
            category="lottery_scam",
            transcript=random.choice(scripts),
            scam_type="Lottery/Prize Scam",
            indicators=["prize_offer", "processing_fee", "urgent", "too_good_to_be_true"],
            entities={"upi_ids": ["kbcprize@paytm", "amazonprizes@ybl"]}
        )
    
    def generate_scam_transcript_bank(self, index: int) -> CallTranscript:
        """Generate bank fraud scam transcript."""
        victim_name = random.choice(self.INDIAN_NAMES)
        bank_name = random.choice(self.BANK_NAMES)
        
        scripts = [
            f"""Scammer: Hello, am I speaking with {victim_name}?
Victim: Yes, who is this?
Scammer: Sir, I am calling from {bank_name} fraud department. There is suspicious activity on your account.
Victim: What kind of activity?
Scammer: Sir, someone tried to withdraw 1 lakh rupees from your account using net banking. The transaction was blocked.
Victim: Thank god! What should I do?
Scammer: Sir, to secure your account, I need to verify your details. Please tell me your debit card number and expiry date.
Victim: Why do you need that?
Scammer: Sir, this is to verify you are the real account holder. Also, you will receive an OTP - tell me that as well.
Victim: I am not comfortable sharing OTP.
Scammer: Sir, if you don't verify now, the hackers will try again and your money will be gone! This is urgent!""",
            
            f"""Scammer: Sir, this is {bank_name} customer care. Your account has been flagged for unusual transactions.
Victim: What transactions?
Scammer: Sir, 50,000 rupees was transferred to an unknown account 10 minutes ago. Did you authorize this?
Victim: No! I didn't do any transfer!
Scammer: Sir, then this is fraud. To reverse the transaction, I need your UPI PIN and the OTP you will receive.
Victim: You need my UPI PIN?
Scammer: Yes sir, this is to verify the reversal request. Without this, we cannot get your money back. Hurry, before it's too late!"""
        ]
        
        return CallTranscript(
            id=f"scam_bank_{index:03d}",
            label="scam",
            category="bank_fraud",
            transcript=random.choice(scripts),
            scam_type="Bank Fraud Scam",
            indicators=["suspicious_activity", "request_otp", "urgent", "impersonation"],
            entities={"bank_names": [bank_name]}
        )
    
    def generate_legitimate_transcript(self, index: int) -> CallTranscript:
        """Generate legitimate call transcript."""
        victim_name = random.choice(self.INDIAN_NAMES)
        
        legitimate_scenarios = [
            f"""Caller: Hello, is this {victim_name}?
Victim: Yes, speaking.
Caller: Sir, this is Raj from Swiggy. Your order for biryani has been confirmed. Delivery in 30 minutes.
Victim: Okay, thank you.
Caller: You're welcome sir. Have a good day!""",
            
            f"""Caller: Hello, am I speaking with {victim_name}?
Victim: Yes, tell me.
Caller: Sir, this is Dr. Sharma's clinic. Your appointment is confirmed for tomorrow at 3 PM.
Victim: Okay, I will be there.
Caller: Thank you sir. Please bring your previous reports.""",
            
            f"""Caller: Hi, is this {victim_name}?
Victim: Yes, who is this?
Caller: Sir, this is Amit from Amazon. Your order for the mobile phone has been shipped. Tracking ID is 123456789.
Victim: Okay, when will it arrive?
Caller: Expected delivery is day after tomorrow. You'll receive updates via SMS.""",
            
            f"""Caller: Hello sir, this is calling from Airtel.
Victim: Yes, tell me.
Caller: Sir, your postpaid bill of 899 rupees is due. Please pay by 5th of this month to avoid late charges.
Victim: Okay, I will pay today.
Caller: Thank you sir. You can pay through Airtel Thanks app or any UPI app.""",
            
            f"""Caller: Hello, may I speak with {victim_name}?
Victim: Yes, speaking.
Caller: Sir, I am Rahul from your bank. You had applied for a credit card. Your application is approved.
Victim: That's good news.
Caller: Sir, please visit your nearest branch with ID proof and address proof to collect your card.""",
            
            f"""Caller: Hi {victim_name}, this is Priya from your child's school.
Victim: Yes, tell me.
Caller: Sir, just reminding you that parent-teacher meeting is on Saturday at 10 AM.
Victim: Okay, I will be there.
Caller: Thank you sir.""",
            
            f"""Caller: Hello, is this {victim_name}?
Victim: Yes.
Caller: Sir, this is your cab driver. I have reached your pickup location.
Victim: Okay, I am coming down in 2 minutes.
Caller: Sure sir, I am waiting. White Swift, number DL 01 AB 1234.""",
            
            f"""Caller: Hello sir, this is Vijay from Urban Company.
Victim: Yes, tell me.
Caller: Sir, your AC service appointment is confirmed for tomorrow between 2-4 PM.
Victim: Okay, please come on time.
Caller: Sure sir. Our technician will call you 30 minutes before arrival."""
        ]
        
        return CallTranscript(
            id=f"legit_{index:03d}",
            label="legitimate",
            category="normal_call",
            transcript=legitimate_scenarios[index % len(legitimate_scenarios)],
            scam_type=None,
            indicators=[],
            entities={}
        )
    
    def generate_dataset(
        self,
        num_scam: int = 50,
        num_legitimate: int = 50,
        output_path: str = "synthetic_dataset.json"
    ) -> List[CallTranscript]:
        """Generate complete synthetic dataset."""
        logger.info("generating_dataset", scam=num_scam, legitimate=num_legitimate)
        
        transcripts = []
        
        # Generate scam transcripts
        scam_generators = [
            self.generate_scam_transcript_kyc,
            self.generate_scam_transcript_police,
            self.generate_scam_transcript_tech_support,
            self.generate_scam_transcript_lottery,
            self.generate_scam_transcript_bank
        ]
        
        for i in range(num_scam):
            generator = scam_generators[i % len(scam_generators)]
            transcript = generator(i)
            transcripts.append(transcript)
        
        # Generate legitimate transcripts
        for i in range(num_legitimate):
            transcript = self.generate_legitimate_transcript(i)
            transcripts.append(transcript)
        
        # Shuffle
        random.shuffle(transcripts)
        
        # Save to file
        data = [t.to_dict() for t in transcripts]
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info("dataset_generated", total=len(transcripts), path=output_path)
        
        return transcripts


def main():
    """Generate synthetic dataset."""
    generator = SyntheticDatasetGenerator()
    generator.generate_dataset(
        num_scam=50,
        num_legitimate=50,
        output_path="/mnt/okcomputer/output/rakshak-ai/ml_pipeline/datasets/synthetic/synthetic_dataset.json"
    )


if __name__ == "__main__":
    main()
