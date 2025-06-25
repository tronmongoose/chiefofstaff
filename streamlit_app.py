# streamlit_app.py

import streamlit as st
import requests
import time
import json
import re

# Page configuration
st.set_page_config(
    page_title="AI Agent Wallet Demo",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling and theme compatibility
st.markdown("""
<style>
    :root {
        --box-bg-light: #fff;
        --box-bg-dark: #23272f;
        --box-text-light: #111;
        --box-text-dark: #f5f5f5;
        --border-color-light: #e0e0e0;
        --border-color-dark: #444;
        --shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: #1f77b4;
    }
    .success-box, .info-box {
        background: var(--box-bg-light);
        color: var(--box-text-light);
        border: 1px solid var(--border-color-light);
        border-radius: 7px;
        box-shadow: var(--shadow);
        padding: 1.2rem;
        margin: 1rem 0;
        transition: background 0.2s, color 0.2s;
    }
    .error-box {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
        border-radius: 7px;
        box-shadow: var(--shadow);
        padding: 1.2rem;
        margin: 1rem 0;
    }
    @media (prefers-color-scheme: dark) {
        .success-box, .info-box {
            background: var(--box-bg-dark);
            color: var(--box-text-dark);
            border: 1px solid var(--border-color-dark);
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("assistant.png", width=150)
    st.markdown("<h3 style='text-align: center;'>🤖 AI Agent Wallet Assistant</h3>", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>💸 AI Agent Wallet Demo</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem;'>LangGraph Agent + Wallet + IPFS Integration</p>", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("## 🎛️ Quick Actions")
st.sidebar.markdown("Use these quick actions to test the system:")

# Quick action buttons in sidebar
if st.sidebar.button("🔍 Check Wallet Balance", use_container_width=True):
    with st.spinner('Fetching wallet balance...'):
        try:
            response = requests.get("http://localhost:8000/wallet-balance")
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    st.sidebar.success(f"💰 {result['response']}")
                else:
                    st.sidebar.error(f"❌ {result.get('response', 'Error fetching balance')}")
            else:
                st.sidebar.error(f"❌ HTTP Error: {response.status_code}")
        except Exception as e:
            st.sidebar.error(f"❌ Connection failed: {str(e)}")

if st.sidebar.button("🌤️ Check Weather", use_container_width=True):
    with st.spinner('Getting weather information...'):
        try:
            payload = {"input": "What is the weather in San Francisco?"}
            response = requests.post("http://localhost:8000/agent", json=payload)
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    st.sidebar.success(f"🌤️ {result['response'][:100]}...")
                else:
                    st.sidebar.error(f"❌ {result.get('response', 'Error getting weather')}")
            else:
                st.sidebar.error(f"❌ HTTP Error: {response.status_code}")
        except Exception as e:
            st.sidebar.error(f"❌ Connection failed: {str(e)}")

if st.sidebar.button("📝 Test IPFS Upload", use_container_width=True):
    with st.spinner('Uploading to IPFS...'):
        try:
            payload = {"input": "log to IPFS: Demo test upload from Streamlit"}
            response = requests.post("http://localhost:8000/agent", json=payload)
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    st.sidebar.success(f"📝 {result['response'][:100]}...")
                else:
                    st.sidebar.error(f"❌ {result.get('response', 'Error uploading to IPFS')}")
            else:
                st.sidebar.error(f"❌ HTTP Error: {response.status_code}")
        except Exception as e:
            st.sidebar.error(f"❌ Connection failed: {str(e)}")

# Main content area
st.markdown("<h2 class='section-header'>🎯 Demo Instructions</h2>", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <h4 style="margin-top:0;">🚀 How to Use This Demo:</h4>
    <ol>
        <li><b>Check Wallet Balance:</b> Use the sidebar button or type "What's my wallet balance?"</li>
        <li><b>Plan a Trip:</b> Type "Plan a trip to Paris" to see trip planning capabilities</li>
        <li><b>Check Weather:</b> Type "What's the weather in Tokyo?" for weather information</li>
        <li><b>Upload to IPFS:</b> Type "log to IPFS: Your message here" to upload content</li>
        <li><b>Make Payments:</b> Type "Send 0.1 ETH to alice.eth" to test payments</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# Chat interface
st.markdown("<h2 class='section-header'>💬 AI Agent Chat</h2>", unsafe_allow_html=True)

# Chat input
chat_input = st.text_input(
    "Ask me anything:",
    placeholder="Try: 'What's my wallet balance?' or 'Plan a trip to Paris' or 'What's the weather in Tokyo?'",
    key="chat_input"
)

# Send button
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    send_button = st.button("🚀 Send to Agent", use_container_width=True)

if send_button and chat_input:
    with st.spinner('🤖 Processing your request...'):
        try:
            payload = {"input": chat_input}
            response = requests.post("http://localhost:8000/agent", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("status") == "success":
                    # Add to transaction history
                    st.session_state.transactions.append({
                        "command": chat_input,
                        "response": result['response'],
                        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                    })

                    # Display split payment confirmation if present
                    split_msg = None
                    ipfs_hash = None
                    if "successfully split between the agent and the referring wallet" in result['response']:
                        split_msg = "The payment has been successfully split between the agent and the referring wallet as part of our decentralized referral system."
                    ipfs_match = re.search(r'(Qm[1-9A-HJ-NP-Za-km-z]{44,})', result['response'])
                    if ipfs_match:
                        ipfs_hash = ipfs_match.group(1)

                    # Display success response
                    st.markdown(f"""
                    <div class="success-box">
                        <h4 style='margin-top:0;'>✅ Agent Response:</h4>
                        <p style='font-size:1.1rem;'>{result['response']}</p>
                        {f'<div style="margin-top:1em;"><b>🔗 Referral Record:</b> <a href="https://gateway.pinata.cloud/ipfs/{ipfs_hash}" target="_blank">View on IPFS</a></div>' if ipfs_hash else ''}
                        {f'<div style="margin-top:1em; color:#1f77b4; font-weight:bold;">{split_msg}</div>' if split_msg else ''}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Display error response
                    st.markdown(f"""
                    <div class="error-box">
                        <h4>❌ Error:</h4>
                        <p>{result.get('response', 'An error occurred.')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if result.get('error'):
                        with st.expander("🔍 Show Error Details"):
                            st.code(result['error'])
            else:
                st.error(f"❌ HTTP Error: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Connection failed: {str(e)}")

# Transaction History
st.markdown("<h2 class='section-header'>📋 Transaction History</h2>", unsafe_allow_html=True)

if st.session_state.transactions:
    # Show last 5 transactions
    for i, tx in enumerate(reversed(st.session_state.transactions[-5:]), 1):
        with st.expander(f"📝 {i}. {tx['timestamp']} - {tx['command'][:50]}..."):
            st.markdown(f"**Command:** {tx['command']}")
            st.markdown(f"**Response:** {tx['response']}")
            
            # Add a copy button for the response
            if st.button(f"📋 Copy Response {i}", key=f"copy_{i}"):
                st.write("Response copied to clipboard!")
else:
    st.info("📝 No transactions yet. Try asking the agent something!")

# System Status
st.markdown("<h2 class='section-header'>🔧 System Status</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏥 Health Check", use_container_width=True):
        with st.spinner('Checking system health...'):
            try:
                response = requests.get("http://localhost:8000/health")
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "success":
                        st.success("✅ System Healthy")
                    else:
                        st.error("❌ System Error")
                else:
                    st.error(f"❌ HTTP Error: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")

with col2:
    if st.button("💰 Test Wallet", use_container_width=True):
        with st.spinner('Testing wallet connection...'):
            try:
                response = requests.get("http://localhost:8000/wallet-balance")
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "success":
                        st.success("✅ Wallet Connected")
                    else:
                        st.error("❌ Wallet Error")
                else:
                    st.error(f"❌ HTTP Error: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")

with col3:
    if st.button("🌐 Test Agent", use_container_width=True):
        with st.spinner('Testing agent...'):
            try:
                payload = {"input": "Hello"}
                response = requests.post("http://localhost:8000/agent", json=payload)
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "success":
                        st.success("✅ Agent Working")
                    else:
                        st.error("❌ Agent Error")
                else:
                    st.error(f"❌ HTTP Error: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #666;'>AI Agent Wallet Demo - Built with LangGraph, FastAPI, and Streamlit</p>", unsafe_allow_html=True)

# Success animation
if st.session_state.transactions:
    st.balloons()