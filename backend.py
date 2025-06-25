from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from wallet import get_wallet_balances_async
from agent_tools import TOOLS
from main import app as langgraph_app
import openai
import os
from nodes.planner import plan_tasks
from tools.ipfs import retrieve_referrals_by_wallet

app = FastAPI(title="AI Agent Wallet API", version="1.0.0")

# Allow CORS for Streamlit running locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentRequest(BaseModel):
    input: str = None
    user_input: str = None
    referrer_wallet: str = None

@app.post("/agent")
async def run_agent(request: AgentRequest):
    try:
        # Handle both 'input' and 'user_input' fields for backward compatibility
        user_input = request.input or request.user_input
        referrer_wallet = request.referrer_wallet
        if not user_input:
            return {
                "status": "error",
                "response": "No input provided",
                "error": "Missing required input field"
            }
        # Pass referrer_wallet to the agent state if provided
        agent_input = {"input": user_input}
        if referrer_wallet:
            agent_input["referrer_wallet"] = referrer_wallet
        output_state = langgraph_app.invoke(input=agent_input)
        response_text = output_state.get('response', "Done.")
        return {
            "status": "success",
            "response": response_text
        }
    except Exception as e:
        import traceback
        error_str = traceback.format_exc()
        print(f"[backend.py] Agent error: {error_str}")
        return {
            "status": "error",
            "response": "An error occurred while processing your request.",
            "error": str(e)
        }

@app.get("/wallet-balance")
async def wallet_balance():
    try:
        # For demo, use the mainnet account address
        class DummyAccount:
            def __init__(self, address):
                self.address = "0xE132d512FC35Bf91aD0C1098031CE09A9BA95241"
        account = DummyAccount("0xE132d512FC35Bf91aD0C1098031CE09A9BA95241")
        balances = await get_wallet_balances_async(account)
        
        # Try to extract the first token balance and format it
        if balances and isinstance(balances, list) and len(balances) > 0:
            balance = balances[0]
            if hasattr(balance, 'token') and hasattr(balance, 'amount'):
                symbol = getattr(balance.token, 'symbol', 'UNKNOWN')
                raw_amount = getattr(balance.amount, 'amount', 0)
                decimals = getattr(balance.amount, 'decimals', 18)
                try:
                    human_amount = int(raw_amount) / (10 ** int(decimals))
                    formatted = f"{human_amount:.4f} {symbol}"
                except Exception:
                    formatted = f"{raw_amount} {symbol}"
                return {
                    "status": "success",
                    "response": f"Wallet balance: {formatted}"
                }
        
        return {
            "status": "success",
            "response": "No balance found"
        }
    except Exception as e:
        import traceback
        error_str = traceback.format_exc()
        print(f"[backend.py] Wallet balance error: {error_str}")
        return {
            "status": "error",
            "response": "An error occurred while fetching wallet balance.",
            "error": str(e)
        }

@app.post("/ipfs-upload")
async def ipfs_upload(request: dict):
    try:
        content = request.get("content", "")
        if not content:
            return {
                "status": "error",
                "response": "No content provided for IPFS upload",
                "error": "Missing content field"
            }
        
        # Import the IPFS upload function
        from tools.ipfs import upload_to_ipfs
        
        # Upload to IPFS
        ipfs_hash = upload_to_ipfs({"content": content})
        
        return {
            "status": "success",
            "response": f"Content uploaded to IPFS successfully. Hash: {ipfs_hash}"
        }
    except Exception as e:
        import traceback
        error_str = traceback.format_exc()
        print(f"[backend.py] IPFS upload error: {error_str}")
        return {
            "status": "error",
            "response": "An error occurred while uploading to IPFS.",
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    return {
        "status": "success",
        "response": "AI Agent Wallet API is running"
    }

@app.get("/referrals/{wallet_address}")
async def get_referrals(wallet_address: str):
    try:
        records = retrieve_referrals_by_wallet(wallet_address)
        return {"status": "success", "response": records}
    except Exception as e:
        import traceback
        error_str = traceback.format_exc()
        print(f"[backend.py] Referral retrieval error: {error_str}")
        return {"status": "error", "response": "Failed to retrieve referrals.", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True, loop="asyncio") 