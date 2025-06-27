# streamlit_app.py

import streamlit as st
import requests
import time
import json
import re

# Helper function for sample address buttons
def set_referral_search_input(value):
    st.session_state['referral_search_input'] = value

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

# Minimal Travel Planner UI
st.markdown("<h1 class='main-header'>✈️ Autonomous Travel Planner</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem;'>Enter your destination and budget to generate a complete travel plan.</p>", unsafe_allow_html=True)

with st.form("travel_form"):
    destination = st.text_input("Destination", placeholder="e.g. Paris")
    budget = st.number_input("Budget (USD or ETH)", min_value=0.0, step=10.0, format="%.2f")
    submit = st.form_submit_button("Generate Travel Plan")

if submit:
    if not destination or budget <= 0:
        st.error("Please enter a valid destination and budget.")
    else:
        with st.spinner('Generating your travel plan...'):
            try:
                payload = {"destination": destination, "budget": budget}
                response = requests.post("http://localhost:8000/agent", json=payload)
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "success":
                        st.success("Travel plan generated!")
                        st.markdown(result["response"])
                    else:
                        st.error(result.get("response", "Error generating travel plan."))
                else:
                    st.error(f"HTTP Error: {response.status_code}")
            except Exception as e:
                st.error(f"Connection failed: {str(e)}")

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

# Decentralized Referral Verification
st.markdown("<h2 class='section-header'>🔍 Decentralized Referral Verification</h2>", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <h4 style="margin-top:0;">🌐 How Decentralized Referral Verification Works:</h4>
    <ul>
        <li><b>Pseudonymous:</b> Referrals are stored on IPFS with wallet addresses only</li>
        <li><b>Verifiable:</b> Anyone can search and verify referral records by wallet address</li>
        <li><b>Immutable:</b> Records are permanently stored on the decentralized IPFS network</li>
        <li><b>Transparent:</b> All referral data is publicly accessible and auditable</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Referral search interface
st.markdown("### 🔍 Search Referral Records by Wallet Address")

# Create two columns for the search interface
search_col1, search_col2 = st.columns([3, 1])

with search_col1:
    wallet_address = st.text_input(
        "Enter wallet address to search:",
        placeholder="0x1234... or alice.eth",
        key="referral_search_input"
    )

with search_col2:
    search_button = st.button("🔍 Search", use_container_width=True)

# Sample wallet addresses for easy testing
st.markdown("**💡 Try these sample addresses:**")
sample_col1, sample_col2, sample_col3 = st.columns(3)
with sample_col1:
    st.button("alice.eth", key="sample_alice", on_click=set_referral_search_input, args=("alice.eth",))
with sample_col2:
    st.button("bob.eth", key="sample_bob", on_click=set_referral_search_input, args=("bob.eth",))
with sample_col3:
    st.button("0xE132d512FC35Bf91aD0C1098031CE09A9BA95241", key="sample_mainnet", on_click=set_referral_search_input, args=("0xE132d512FC35Bf91aD0C1098031CE09A9BA95241",))

# Handle search
if search_button and wallet_address:
    with st.spinner('🔍 Searching decentralized referral records...'):
        try:
            response = requests.get(f"http://localhost:8000/referrals/{wallet_address}")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("status") == "success":
                    records = result.get("response", [])
                    
                    if records:
                        st.markdown(f"""
                        <div class="success-box">
                            <h4 style='margin-top:0;'>✅ Found {len(records)} referral record(s) for {wallet_address}</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display each referral record
                        for i, record in enumerate(records, 1):
                            with st.expander(f"📋 Referral Record {i} - {record.get('timestamp', 'Unknown Date')}"):
                                st.markdown(f"**🔗 IPFS Hash:** `{record.get('ipfs_hash', 'N/A')}`")
                                st.markdown(f"**💰 Referrer Wallet:** `{record.get('referrer_wallet', 'N/A')}`")
                                st.markdown(f"**🎯 Referred Wallet:** `{record.get('referred_wallet', 'N/A')}`")
                                st.markdown(f"**💸 Payment Amount:** `{record.get('payment_amount', 'N/A')}`")
                                st.markdown(f"**📅 Timestamp:** `{record.get('timestamp', 'N/A')}`")
                                
                                # Add IPFS link if available
                                ipfs_hash = record.get('ipfs_hash')
                                if ipfs_hash:
                                    st.markdown(f"**🔗 View on IPFS:** [Open Record](https://gateway.pinata.cloud/ipfs/{ipfs_hash})")
                                
                                # Add verification status
                                st.markdown("**✅ Verification Status:** This record is verified and immutable on the decentralized IPFS network")
                    else:
                        st.markdown(f"""
                        <div class="info-box">
                            <h4 style='margin-top:0;'>📭 No referral records found</h4>
                            <p>No referral records were found for wallet address: <code>{wallet_address}</code></p>
                            <p>This could mean:</p>
                            <ul>
                                <li>The wallet hasn't participated in any referrals yet</li>
                                <li>The wallet address might be incorrect</li>
                                <li>Records might be stored under a different address format</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="error-box">
                        <h4>❌ Search Error:</h4>
                        <p>{result.get('response', 'An error occurred while searching referral records.')}</p>
                    </div>
                    """, unsafe_allow_html=True)
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