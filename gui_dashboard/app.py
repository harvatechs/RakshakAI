"""
RakshakAI - Streamlit GUI Dashboard
Interactive visualization and control center
"""

import streamlit as st
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="RakshakAI - Scam Defense Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1a237e;
        text-align: center;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .threat-high {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    }
    .threat-medium {
        background: linear-gradient(135deg, #feca57 0%, #ff9f43 100%);
    }
    .threat-low {
        background: linear-gradient(135deg, #1dd1a1 0%, #10ac84 100%);
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .entity-tag {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        margin: 0.25rem;
        border-radius: 5px;
        font-size: 0.75rem;
        background: #e3f2fd;
        color: #1976d2;
        border: 1px solid #bbdefb;
    }
    .log-entry {
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 5px;
        font-family: monospace;
        font-size: 0.85rem;
    }
    .log-info { background: #e3f2fd; }
    .log-warning { background: #fff3e0; }
    .log-error { background: #ffebee; }
    .log-success { background: #e8f5e9; }
</style>
""", unsafe_allow_html=True)

# ==================== MOCK DATA (Replace with real API calls) ====================

MOCK_STATS = {
    "total_calls": 15234,
    "threats_detected": 3421,
    "scams_blocked": 2890,
    "ai_engagements": 1876,
    "intelligence_extracted": 1243,
    "active_monitors": 156,
    "time_saved_minutes": 5624,
}

MOCK_THREAT_TIMELINE = [
    {"time": "00:00", "threats": 12, "safe": 45},
    {"time": "04:00", "threats": 8, "safe": 38},
    {"time": "08:00", "threats": 34, "safe": 89},
    {"time": "12:00", "threats": 56, "safe": 134},
    {"time": "16:00", "threats": 78, "safe": 156},
    {"time": "20:00", "threats": 45, "safe": 98},
]

MOCK_GEO_DATA = [
    {"city": "Mumbai", "state": "Maharashtra", "incidents": 456, "lat": 19.0760, "lon": 72.8777},
    {"city": "Delhi", "state": "Delhi", "incidents": 389, "lat": 28.6139, "lon": 77.2090},
    {"city": "Bangalore", "state": "Karnataka", "incidents": 234, "lat": 12.9716, "lon": 77.5946},
    {"city": "Chennai", "state": "Tamil Nadu", "incidents": 187, "lat": 13.0827, "lon": 80.2707},
    {"city": "Hyderabad", "state": "Telangana", "incidents": 198, "lat": 17.3850, "lon": 78.4867},
    {"city": "Kolkata", "state": "West Bengal", "incidents": 156, "lat": 22.5726, "lon": 88.3639},
]

MOCK_ACTIVE_CALLS = [
    {
        "call_id": "CALL-001",
        "phone": "+91 98765 43210",
        "duration": 180,
        "threat_score": 0.87,
        "threat_level": "HIGH",
        "ai_active": True,
        "entities_found": 3,
        "transcript": [
            {"speaker": "Scammer", "text": "Hello sir, I am calling from RBI..."},
            {"speaker": "AI Agent", "text": "Arre, RBI se? Kya baat kar rahe ho?"},
            {"speaker": "Scammer", "text": "Sir, your account will be frozen..."},
        ]
    },
    {
        "call_id": "CALL-002",
        "phone": "+91 87654 32109",
        "duration": 45,
        "threat_score": 0.34,
        "threat_level": "LOW",
        "ai_active": False,
        "entities_found": 0,
        "transcript": []
    },
]

MOCK_INTELLIGENCE = [
    {
        "id": "INT-001",
        "type": "UPI ID",
        "value": "scammer@paytm",
        "confidence": 0.95,
        "source": "+91 98765 43210",
        "timestamp": datetime.now() - timedelta(minutes=5),
    },
    {
        "id": "INT-002",
        "type": "Phone Number",
        "value": "+91 99999 88888",
        "confidence": 0.88,
        "source": "+91 98765 43210",
        "timestamp": datetime.now() - timedelta(minutes=3),
    },
    {
        "id": "INT-003",
        "type": "Bank Account",
        "value": "XXXXXX1234 (HDFC)",
        "confidence": 0.82,
        "source": "+91 98765 43210",
        "timestamp": datetime.now() - timedelta(minutes=1),
    },
]

# ==================== SESSION STATE ====================

if 'logs' not in st.session_state:
    st.session_state.logs = []

if 'active_calls' not in st.session_state:
    st.session_state.active_calls = MOCK_ACTIVE_CALLS.copy()

if 'threat_history' not in st.session_state:
    st.session_state.threat_history = []

# ==================== HELPER FUNCTIONS ====================

def add_log(message: str, level: str = "info"):
    """Add a log entry"""
    st.session_state.logs.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "message": message,
        "level": level
    })

def get_threat_color(score: float) -> str:
    if score >= 0.8:
        return "#ff6b6b"
    elif score >= 0.6:
        return "#feca57"
    elif score >= 0.3:
        return "#54a0ff"
    return "#1dd1a1"

def get_threat_class(score: float) -> str:
    if score >= 0.8:
        return "threat-high"
    elif score >= 0.6:
        return "threat-medium"
    return "threat-low"

# ==================== SIDEBAR ====================

with st.sidebar:
    st.image("https://img.icons8.com/color/96/shield.png", width=80)
    st.markdown("<h2 style='text-align: center; color: #1a237e;'>RakshakAI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>AI-Powered Scam Defense</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "📞 Live Calls", "🎯 Intelligence", "🗺️ Geographic Map", "📊 Analytics", "⚙️ Settings"]
    )
    
    st.markdown("---")
    
    # System Status
    st.subheader("System Status")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("API Status", "🟢 Online")
    with col2:
        st.metric("Gemini API", "🟢 Ready")
    
    st.markdown("---")
    
    # Quick Actions
    st.subheader("Quick Actions")
    if st.button("🚨 Simulate Threat Call", use_container_width=True):
        add_log("Simulated threat call initiated", "warning")
        st.rerun()
    
    if st.button("🤖 Activate AI Agent", use_container_width=True):
        add_log("AI Bait Agent activated", "success")
        st.rerun()
    
    if st.button("📤 Export Report", use_container_width=True):
        add_log("Evidence report exported", "info")
    
    st.markdown("---")
    
    # Recent Logs
    st.subheader("System Logs")
    for log in st.session_state.logs[-5:]:
        css_class = f"log-{log['level']}"
        st.markdown(f"<div class='log-entry {css_class}'><b>{log['time']}</b> {log['message']}</div>", 
                   unsafe_allow_html=True)

# ==================== MAIN CONTENT ====================

if page == "🏠 Dashboard":
    st.markdown("<h1 class='main-header'>🛡️ RakshakAI Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Real-time Scam Call Defense & Intelligence Platform</p>", 
                unsafe_allow_html=True)
    
    # Key Metrics
    st.subheader("📊 Key Metrics")
    cols = st.columns(4)
    
    metrics = [
        ("Total Calls", MOCK_STATS["total_calls"], "📞"),
        ("Threats Detected", MOCK_STATS["threats_detected"], "⚠️"),
        ("Scams Blocked", MOCK_STATS["scams_blocked"], "🚫"),
        ("AI Engagements", MOCK_STATS["ai_engagements"], "🤖"),
    ]
    
    for col, (label, value, icon) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <h4>{icon} {label}</h4>
                <h2>{value:,}</h2>
            </div>
            """, unsafe_allow_html=True)
    
    # Second row metrics
    cols2 = st.columns(4)
    metrics2 = [
        ("Intelligence", MOCK_STATS["intelligence_extracted"], "📋"),
        ("Active Monitors", MOCK_STATS["active_monitors"], "👁️"),
        ("Time Saved (hrs)", MOCK_STATS["time_saved_minutes"] // 60, "⏱️"),
        ("Success Rate", "94.2%", "📈"),
    ]
    
    for col, (label, value, icon) in zip(cols2, metrics2):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
                <h4>{icon} {label}</h4>
                <h2>{value}</h2>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts Row
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📈 Threat Detection Timeline")
        df_timeline = pd.DataFrame(MOCK_THREAT_TIMELINE)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_timeline["time"], y=df_timeline["threats"],
            mode='lines+markers', name='Threats',
            line=dict(color='#ff6b6b', width=3),
            fill='tozeroy'
        ))
        fig.add_trace(go.Scatter(
            x=df_timeline["time"], y=df_timeline["safe"],
            mode='lines+markers', name='Safe Calls',
            line=dict(color='#1dd1a1', width=3)
        ))
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_chart2:
        st.subheader("🥧 Scam Type Distribution")
        scam_types = {
            "KYC Fraud": 35,
            "Bank Impersonation": 28,
            "Tech Support": 18,
            "Lottery/Prize": 12,
            "Police Impersonation": 7
        }
        fig = px.pie(
            values=list(scam_types.values()),
            names=list(scam_types.keys()),
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    # Active Threats
    st.markdown("---")
    st.subheader("🚨 Active Threats")
    
    for call in st.session_state.active_calls:
        threat_color = get_threat_color(call["threat_score"])
        threat_class = get_threat_class(call["threat_score"])
        
        with st.expander(f"📞 {call['phone']} - Threat Score: {call['threat_score']:.0%}"):
            cols = st.columns([2, 1, 1, 1])
            
            with cols[0]:
                st.markdown(f"**Call ID:** `{call['call_id']}`")
                st.markdown(f"**Duration:** {call['duration'] // 60}m {call['duration'] % 60}s")
                st.markdown(f"**Threat Level:** <span style='color:{threat_color};font-weight:bold;'>{call['threat_level']}</span>", 
                           unsafe_allow_html=True)
            
            with cols[1]:
                st.markdown(f"**AI Active:** {'🟢 Yes' if call['ai_active'] else '🔴 No'}")
                st.markdown(f"**Entities:** {call['entities_found']}")
            
            with cols[2]:
                if call["ai_active"]:
                    st.button("⏹️ Stop AI", key=f"stop_{call['call_id']}")
                else:
                    st.button("▶️ Start AI", key=f"start_{call['call_id']}")
            
            with cols[3]:
                st.button("📋 View Details", key=f"view_{call['call_id']}")
            
            # Transcript
            if call["transcript"]:
                st.markdown("**Live Transcript:**")
                for entry in call["transcript"]:
                    speaker_color = "#ff6b6b" if entry["speaker"] == "Scammer" else "#54a0ff"
                    st.markdown(f"<span style='color:{speaker_color};font-weight:bold;'>{entry['speaker']}:</span> {entry['text']}",
                               unsafe_allow_html=True)

elif page == "📞 Live Calls":
    st.markdown("<h1 class='main-header'>📞 Live Call Monitor</h1>", unsafe_allow_html=True)
    
    # Call controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.text_input("Phone Number to Monitor", placeholder="+91 XXXXX XXXXX")
    with col2:
        st.selectbox("AI Persona", ["Confused Senior (Ramesh)", "Cautious Professional", "Trusting Homemaker"])
    with col3:
        st.button("📱 Start Monitoring", use_container_width=True)
    
    st.markdown("---")
    
    # Real-time visualization
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("🎙️ Audio Visualization")
        
        # Simulated audio waveform
        import numpy as np
        audio_data = np.random.randn(100) * 0.5
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=audio_data,
            mode='lines',
            line=dict(color='#667eea', width=1),
            fill='tozeroy'
        ))
        fig.update_layout(
            height=200,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False, range=[-2, 2])
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Threat gauge
        st.subheader("⚡ Real-time Threat Score")
        threat_score = 0.75  # Simulated
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=threat_score * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Threat Score"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': get_threat_color(threat_score)},
                'steps': [
                    {'range': [0, 30], 'color': '#e8f5e9'},
                    {'range': [30, 60], 'color': '#fff3e0'},
                    {'range': [60, 80], 'color': '#ffebee'},
                    {'range': [80, 100], 'color': '#ffcdd2'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 85
                }
            }
        ))
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.subheader("📝 Live Transcript")
        st.markdown("""
        <div style="background: #f5f5f5; padding: 1rem; border-radius: 10px; height: 400px; overflow-y: auto;">
            <p><span style="color: #ff6b6b; font-weight: bold;">Scammer:</span> Hello sir, I am calling from RBI...</p>
            <p><span style="color: #54a0ff; font-weight: bold;">AI Agent:</span> Arre, RBI se? Kya baat kar rahe ho?</p>
            <p><span style="color: #ff6b6b; font-weight: bold;">Scammer:</span> Sir, your account has suspicious activity...</p>
            <p><span style="color: #54a0ff; font-weight: bold;">AI Agent:</span> Account? Kaunsa account? Mujhe samajh nahi aaya...</p>
            <p><span style="color: #ff6b6b; font-weight: bold;">Scammer:</span> Your bank account sir, we need to verify...</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("🎯 Detected Indicators")
        indicators = ["Urgency", "Authority Claim", "Financial Request", "Threat"]
        for ind in indicators:
            st.markdown(f"<span class='entity-tag'>⚠️ {ind}</span>", unsafe_allow_html=True)

elif page == "🎯 Intelligence":
    st.markdown("<h1 class='main-header'>🎯 Intelligence Center</h1>", unsafe_allow_html=True)
    
    # Search
    st.text_input("🔍 Search Intelligence", placeholder="Search by phone, UPI, bank account, case ID...")
    
    # Intelligence feed
    st.subheader("📊 Latest Intelligence")
    
    for intel in MOCK_INTELLIGENCE:
        with st.container():
            cols = st.columns([1, 2, 1, 1, 1])
            
            with cols[0]:
                type_colors = {
                    "UPI ID": "#4caf50",
                    "Phone Number": "#2196f3",
                    "Bank Account": "#ff9800"
                }
                color = type_colors.get(intel["type"], "#9e9e9e")
                st.markdown(f"<span style='background: {color}; color: white; padding: 0.25rem 0.5rem; border-radius: 5px; font-size: 0.8rem;'>{intel['type']}</span>",
                           unsafe_allow_html=True)
            
            with cols[1]:
                st.markdown(f"**{intel['value']}**")
            
            with cols[2]:
                confidence_color = "#4caf50" if intel["confidence"] > 0.8 else "#ff9800" if intel["confidence"] > 0.5 else "#f44336"
                st.markdown(f"Confidence: <span style='color: {confidence_color}; font-weight: bold;'>{intel['confidence']:.0%}</span>",
                           unsafe_allow_html=True)
            
            with cols[3]:
                st.markdown(f"Source: `{intel['source']}`")
            
            with cols[4]:
                time_ago = (datetime.now() - intel["timestamp"]).seconds // 60
                st.markdown(f"{time_ago} min ago")
            
            st.markdown("---")
    
    # OSINT Tools
    st.subheader("🔍 OSINT Investigation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Phone Number Lookup")
        phone = st.text_input("Enter phone number", placeholder="+91 XXXXX XXXXX", key="osint_phone")
        if st.button("🔎 Investigate Phone", use_container_width=True):
            with st.spinner("Investigating..."):
                time.sleep(2)
                st.success("Investigation complete!")
                st.json({
                    "carrier": "Airtel",
                    "circle": "Mumbai",
                    "spam_reports": 12,
                    "risk_score": 0.78
                })
    
    with col2:
        st.markdown("#### UPI ID Lookup")
        upi = st.text_input("Enter UPI ID", placeholder="username@paytm", key="osint_upi")
        if st.button("🔎 Investigate UPI", use_container_width=True):
            with st.spinner("Investigating..."):
                time.sleep(2)
                st.success("Investigation complete!")
                st.json({
                    "bank": "Paytm Payments Bank",
                    "username": "scammer123",
                    "risk_indicators": ["Suspicious username pattern"],
                    "risk_score": 0.85
                })

elif page == "🗺️ Geographic Map":
    st.markdown("<h1 class='main-header'>🗺️ Geographic Threat Map</h1>", unsafe_allow_html=True)
    
    # Map visualization
    df_geo = pd.DataFrame(MOCK_GEO_DATA)
    
    fig = px.scatter_mapbox(
        df_geo,
        lat="lat",
        lon="lon",
        size="incidents",
        color="incidents",
        hover_name="city",
        hover_data=["state", "incidents"],
        color_continuous_scale="Reds",
        size_max=50,
        zoom=4,
        center={"lat": 20.5937, "lon": 78.9629}
    )
    fig.update_layout(
        mapbox_style="carto-positron",
        height=600,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Hotspots table
    st.subheader("🔥 Top Hotspots")
    df_hotspots = pd.DataFrame(MOCK_GEO_DATA).sort_values("incidents", ascending=False)
    st.dataframe(df_hotspots[["city", "state", "incidents"]], use_container_width=True)

elif page == "📊 Analytics":
    st.markdown("<h1 class='main-header'>📊 Advanced Analytics</h1>", unsafe_allow_html=True)
    
    # Time series
    st.subheader("📈 Threat Detection Over Time")
    dates = pd.date_range(start="2024-01-01", periods=30, freq='D')
    threats = np.random.poisson(50, 30) + np.linspace(0, 20, 30)
    df_ts = pd.DataFrame({"date": dates, "threats": threats})
    
    fig = px.line(df_ts, x="date", y="threats", title="Daily Threat Detections")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Model performance
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Model Performance")
        metrics = {
            "Accuracy": 0.942,
            "Precision": 0.938,
            "Recall": 0.951,
            "F1 Score": 0.944
        }
        
        for metric, value in metrics.items():
            st.progress(value, text=f"{metric}: {value:.1%}")
    
    with col2:
        st.subheader("⚡ Response Times")
        st.metric("Avg Detection Latency", "287ms", "-12ms")
        st.metric("AI Response Time", "1.2s", "-0.3s")
        st.metric("Transcription Speed", "0.8x realtime", "+0.1x")

elif page == "⚙️ Settings":
    st.markdown("<h1 class='main-header'>⚙️ System Settings</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔑 API Configuration")
        st.text_input("Gemini API Key", type="password", value="AIzaSy...")
        st.text_input("Backend URL", value="http://localhost:8000")
        
        st.subheader("🎚️ Thresholds")
        st.slider("Threat Alert Threshold", 0.0, 1.0, 0.7)
        st.slider("Auto AI Handoff Threshold", 0.0, 1.0, 0.85)
        st.slider("Auto Report Threshold", 0.0, 1.0, 0.95)
    
    with col2:
        st.subheader("🔔 Notifications")
        st.toggle("Enable Push Notifications", value=True)
        st.toggle("Enable Email Alerts", value=False)
        st.toggle("Sound Alerts", value=True)
        
        st.subheader("💾 Storage")
        st.toggle("Auto-save Recordings", value=True)
        st.number_input("Retention Days", value=30, min_value=1, max_value=365)
        st.toggle("Encrypt Recordings", value=True)
    
    st.markdown("---")
    
    if st.button("💾 Save Settings", type="primary", use_container_width=True):
        st.success("Settings saved successfully!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🛡️ <b>RakshakAI</b> - AI-Powered Scam Defense System</p>
    <p style="font-size: 0.8rem;">Powered by Google Gemini API | Built for Hackathon Excellence</p>
</div>
""", unsafe_allow_html=True)
