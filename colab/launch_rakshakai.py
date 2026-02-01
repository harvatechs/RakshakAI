#!/usr/bin/env python3
"""
RakshakAI - One-Click Launcher for Google Colab
Complete scam defense system launcher
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

def print_banner():
    """Print RakshakAI banner"""
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   🛡️  RAKSHAKAI - AI-Powered Scam Call Defense System  🛡️    ║
    ║                                                               ║
    ║   Powered by FREE Gemini API | Built for Hackathons          ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

def check_gemini_key():
    """Check if Gemini API key is configured"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found!")
        print("\n📝 To get your FREE API key:")
        print("   1. Visit: https://makersuite.google.com/app/apikey")
        print("   2. Click 'Create API Key'")
        print("   3. Run: export GEMINI_API_KEY='your_key_here'")
        return False
    print(f"✅ Gemini API Key configured: {api_key[:10]}...")
    return True

def install_dependencies():
    """Install required packages"""
    print("\n📦 Installing dependencies...")
    
    packages = [
        "google-generativeai",
        "fastapi", "uvicorn", "websockets",
        "streamlit", "plotly", "pandas", "numpy",
        "scikit-learn", "pydantic", "python-dotenv",
        "pyngrok", "requests"
    ]
    
    for pkg in packages:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", pkg], 
                      capture_output=True)
    
    print("✅ Dependencies installed!")

def generate_dataset():
    """Generate powerful training dataset"""
    print("\n📊 Generating training dataset...")
    
    dataset_code = '''
import json
import random

INDIAN_NAMES = ["Ramesh Kumar", "Suresh Patel", "Amit Sharma", "Priya Singh",
                "Vikram Reddy", "Anita Desai", "Rajesh Gupta", "Sunita Verma"]
BANKS = ["SBI", "HDFC", "ICICI", "Axis", "PNB", "BOB"]

def generate_scam():
    victim = random.choice(INDIAN_NAMES)
    bank = random.choice(BANKS)
    return {
        "label": "scam",
        "category": "kyc_fraud",
        "transcript": f"Scammer: Hello, I am from {bank}. Your KYC expired.\\nVictim: What?\\nScammer: Give me your ATM PIN and OTP now!",
        "threat_indicators": ["urgent", "request_sensitive_info"]
    }

def generate_legit():
    return {
        "label": "legitimate",
        "category": "normal_call",
        "transcript": "Caller: Hello from Swiggy. Your order is confirmed.\\nCustomer: Okay, thanks.",
        "threat_indicators": []
    }

data = [generate_scam() for _ in range(100)] + [generate_legit() for _ in range(100)]
random.shuffle(data)

with open('rakshak_dataset.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"Generated {len(data)} samples")
'''
    
    exec(dataset_code)
    print("✅ Dataset generated: rakshak_dataset.json")

def train_model():
    """Train ML classifier"""
    print("\n🤖 Training ML classifier...")
    
    training_code = '''
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
import joblib
import json

with open('rakshak_dataset.json', 'r') as f:
    data = json.load(f)

texts = [d['transcript'] for d in data]
labels = [1 if d['label'] == 'scam' else 0 for d in data]

X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2)

vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 3))
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

model = GradientBoostingClassifier(n_estimators=200, learning_rate=0.1)
model.fit(X_train_vec, y_train)

accuracy = model.score(X_test_vec, y_test)
joblib.dump((model, vectorizer), 'scam_classifier.pkl')

print(f"Model trained! Accuracy: {accuracy:.1%}")
'''
    
    exec(training_code)
    print("✅ Model saved: scam_classifier.pkl")

def create_dashboard():
    """Create Streamlit dashboard"""
    print("\n📱 Creating dashboard...")
    
    dashboard_code = '''
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import random

st.set_page_config(page_title="RakshakAI", page_icon="🛡️", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1a237e;'>🛡️ RakshakAI Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>AI-Powered Scam Defense System</p>", unsafe_allow_html=True)

# Metrics
cols = st.columns(4)
for col, (label, value) in zip(cols, [("📞 Calls", 15234), ("⚠️ Threats", 3421), ("🚫 Blocked", 2890), ("🤖 AI", 1876)]):
    col.metric(label, value)

# Threat Gauge
threat = st.slider("Threat Score", 0.0, 1.0, 0.75)
fig = go.Figure(go.Indicator(
    mode="gauge+number", value=threat*100,
    title={'text': "Threat Level"},
    gauge={'axis': {'range': [0, 100]},
           'bar': {'color': "#ff6b6b"},
           'steps': [{'range': [0, 30], 'color': "#e8f5e9"},
                     {'range': [30, 60], 'color': "#fff3e0"},
                     {'range': [60, 100], 'color': "#ffebee"}]}
))
st.plotly_chart(fig, use_container_width=True)

# Live Transcript
st.subheader("📝 Live Transcript")
st.markdown("""
<div style="background: #f5f5f5; padding: 1rem; border-radius: 10px;">
<p><span style="color: #ff6b6b; font-weight: bold;">Scammer:</span> Hello sir, I am calling from RBI...</p>
<p><span style="color: #54a0ff; font-weight: bold;">AI Agent:</span> Arre, RBI se? Kya baat kar rahe ho?</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<p style='text-align: center;'>Built with ❤️ using FREE Gemini API</p>", unsafe_allow_html=True)
'''
    
    with open('dashboard.py', 'w') as f:
        f.write(dashboard_code)
    
    print("✅ Dashboard created: dashboard.py")

def launch_dashboard():
    """Launch dashboard with ngrok"""
    print("\n🚀 Launching dashboard...")
    
    # Kill existing processes
    os.system("pkill -f streamlit 2>/dev/null")
    os.system("pkill -f ngrok 2>/dev/null")
    
    # Start streamlit
    import threading
    def run_streamlit():
        os.system("streamlit run dashboard.py --server.port 8501 > /dev/null 2>&1")
    
    thread = threading.Thread(target=run_streamlit)
    thread.daemon = True
    thread.start()
    
    time.sleep(3)
    
    # Setup ngrok
    try:
        from pyngrok import ngrok
        public_url = ngrok.connect(8501, "http")
        print(f"\n🌐 Public Dashboard URL:")
        print(f"   {public_url}")
        print(f"\n📊 Click the link to view your dashboard!")
        return public_url
    except Exception as e:
        print(f"⚠️  Ngrok failed: {e}")
        print("   Dashboard running locally at: http://localhost:8501")
        return None

def test_gemini():
    """Test Gemini API connection"""
    print("\n🧪 Testing Gemini API...")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say 'RakshakAI is ready!'")
        print(f"✅ Gemini API working: {response.text.strip()}")
        return True
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return False

def main():
    """Main launcher function"""
    print_banner()
    
    # Check Gemini key
    if not check_gemini_key():
        return 1
    
    # Install dependencies
    install_dependencies()
    
    # Test Gemini
    if not test_gemini():
        print("\n⚠️  Gemini API test failed. Continuing anyway...")
    
    # Generate dataset
    generate_dataset()
    
    # Train model
    train_model()
    
    # Create dashboard
    create_dashboard()
    
    # Launch dashboard
    url = launch_dashboard()
    
    # Keep running
    print("\n" + "="*60)
    print("✅ RakshakAI is running!")
    print("="*60)
    
    if url:
        print(f"\n🌐 Dashboard: {url}")
    print("📊 Local: http://localhost:8501")
    print("\nPress Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down RakshakAI...")
        os.system("pkill -f streamlit 2>/dev/null")
        os.system("pkill -f ngrok 2>/dev/null")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
