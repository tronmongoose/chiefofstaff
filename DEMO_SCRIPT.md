# 🎬 Final Demo Script - Decentralized Travel Referral Agent

## Demo Overview
**Duration:** 3:30 minutes  
**Key Message:** "We've built a decentralized travel referral agent that autonomously splits crypto payments and posts referral records to decentralized storage via IPFS."

---

## 📋 Demo Flow & Talking Points

### 0:00 - Project Introduction
**Tool:** Cursor (Code View)  
**Screen:** Show project structure  
**Demo Step:** Project Intro  
**Talking Points:**
- "We've built a decentralized travel referral agent that autonomously splits crypto payments and posts referral records to decentralized storage via IPFS."
- "This is a trustless, self-funding referral system that respects user privacy while enabling revenue sharing."
- "The entire system is modular, composable, and demo-ready for real-world crypto use."

**Files to Show:**
- `main.py` - LangGraph agent setup
- `payments.py` - Payment split logic
- `tools/ipfs.py` - Decentralized storage
- `streamlit_app.py` - User interface

---

### 0:30 - Payment Split Code Walkthrough
**Tool:** Cursor (Code View)  
**Screen:** Show payment split implementation  
**Demo Step:** Show Payment Split Code  
**Talking Points:**
- "Here's where our agent verifies payments and automatically splits revenue between the agent and a referrer wallet—fully configurable and composable."
- "The split is 80% to agent, 20% to referrer by default, but completely configurable via environment variables."
- "This creates a trustless revenue sharing mechanism without centralized intermediaries."

**Key Code Sections:**
```python
# payments.py - process_referral_payment function
def process_referral_payment(recipient_address: str, amount: float, token_symbol: str = "USDC", referrer_wallet: str = None):
    agent_amount = round(amount * REFERRAL_SPLIT_AGENT, 6)  # 80%
    referrer_amount = round(amount * REFERRAL_SPLIT_REFERRER, 6)  # 20%
```

---

### 1:00 - Streamlit App UI
**Tool:** Streamlit App  
**Screen:** Show clean, modern interface  
**Demo Step:** Show App UI  
**Talking Points:**
- "Let's plan a trip. We'll include a referral wallet so the agent knows to split the payment."
- "The interface is intuitive and handles both simple queries and complex payment flows."
- "Notice the sidebar quick actions for common tasks like checking wallet balance."

**UI Elements to Highlight:**
- Clean, modern design
- Sidebar quick actions
- Chat interface
- Success/error handling

---

### 1:30 - Submit Trip Request with Referral
**Tool:** Streamlit App  
**Screen:** Submit payment request  
**Demo Step:** Submit Trip Request  
**Talking Points:**
- "The agent confirms the payment split: 80% to the agent wallet, 20% to the referrer."
- "The referral record is also posted to IPFS automatically."
- "This creates a permanent, immutable record of the referral relationship."

**Demo Input:**
```
Pay 5 USDC to 0xE132d512FC35Bf91aD0C1098031CE09A9BA95241
```
**With referrer_wallet:** `0x1234567890123456789012345678901234567890`

---

### 2:00 - Payment Confirmation & IPFS Link
**Tool:** Streamlit App / Backend Logs  
**Screen:** Show payment confirmation  
**Demo Step:** Show Payment Confirmation & IPFS Link  
**Talking Points:**
- "You can see the IPFS link here—it's a permanent, decentralized record of the referral."
- "The payment has been successfully split between the agent and the referring wallet as part of our decentralized referral system."
- "This IPFS hash is immutable and can be used to verify the referral relationship."

**Expected Response Elements:**
- ✅ Split payment confirmation
- 🔗 IPFS referral record link
- 📊 Transaction details

---

### 2:30 - Referral Retrieval Tool
**Tool:** Streamlit App  
**Screen:** Show retrieval functionality  
**Demo Step:** Show Retrieval Tool  
**Talking Points:**
- "Let's use our retrieval tool to find this referral record by wallet address."
- "This is a decentralized, pseudonymous reputation system without centralized gatekeepers."
- "Anyone can query the referral history of any wallet address."

**Demo Query:**
```
Show me referrals for 0x1234567890123456789012345678901234567890
```

---

### 3:00 - GitHub Repository Overview
**Tool:** GitHub Repo (Optional)  
**Screen:** Show project structure  
**Demo Step:** Project Recap  
**Talking Points:**
- "The project is fully modular and open-source."
- "All payment logic, referral flows, and retrieval tools are reusable for future agents or other micro-SaaS builds."
- "The codebase is well-organized with comprehensive tests and documentation."

**Repository Highlights:**
- `/tools/` - Reusable payment and IPFS tools
- `/tests/` - Comprehensive test suite
- `/docs/` - Documentation and status reports
- `streamlit_app.py` - Production-ready UI

---

### 3:30 - Final Pitch & Wrap Up
**Tool:** Any screen  
**Screen:** Summary view  
**Demo Step:** Final Pitch  
**Talking Points:**
- "This is a trustless, self-funding referral system that respects user privacy while enabling revenue sharing."
- "It's decentralized, composable, and demo-ready for real-world crypto use."
- "The system can be extended to any agent or application that needs referral tracking and revenue sharing."

**Key Benefits to Emphasize:**
- 🔒 **Trustless** - No centralized intermediaries
- 💰 **Self-funding** - Automatic revenue sharing
- 🛡️ **Privacy-respecting** - Pseudonymous records
- 🔗 **Composable** - Reusable across applications
- 🌐 **Decentralized** - IPFS-based storage

---

## 🎯 Demo Success Metrics

### Technical Achievements
- ✅ Payment split working correctly
- ✅ IPFS referral records posted successfully
- ✅ Retrieval tool functioning
- ✅ Clean UI with clear feedback
- ✅ All endpoints returning consistent JSON

### Business Value
- ✅ Trustless revenue sharing
- ✅ Decentralized reputation system
- ✅ Composable architecture
- ✅ Production-ready codebase

---

## 🚨 Demo Day Checklist

### Pre-Demo Setup
- [ ] Backend running (`python backend.py`)
- [ ] Streamlit app running (`streamlit run streamlit_app.py`)
- [ ] Environment variables configured
- [ ] Test wallet balance endpoint
- [ ] Have demo wallet addresses ready

### During Demo
- [ ] Show code structure first (30s)
- [ ] Demonstrate payment with referral (1:30)
- [ ] Show IPFS link and confirmation (30s)
- [ ] Demonstrate retrieval tool (30s)
- [ ] Wrap up with benefits (30s)

### Post-Demo
- [ ] Be ready for technical questions
- [ ] Have GitHub repo open for code review
- [ ] Know the architecture decisions
- [ ] Understand the business model

---

## 💡 Pro Tips for Demo Day

1. **Keep it Simple:** Focus on the core value proposition
2. **Show, Don't Tell:** Let the working system speak for itself
3. **Highlight Innovation:** Emphasize the decentralized, trustless nature
4. **Be Prepared:** Have backup demo scenarios ready
5. **Engage Audience:** Ask for questions about specific aspects

**Good luck with your demo! 🚀** 