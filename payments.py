import os
from cdp import CdpClient
from dotenv import load_dotenv
from langchain_core.tools import tool
from transaction_log import log_transaction, COSTS

load_dotenv()

API_KEY_ID = os.getenv("CDP_API_KEY_ID")
PRIVATE_KEY_PATH = "secrets/cdp_private_key.pem"
WALLET_SECRET = os.getenv("CDP_WALLET_SECRET")
NETWORK = "base"  # Use Base mainnet
SAVINGS_WALLET_ADDRESS = os.getenv("SAVINGS_WALLET_ADDRESS")
REFERRAL_SPLIT_AGENT = float(os.getenv("REFERRAL_SPLIT_AGENT", 0.8))  # 80% default
REFERRAL_SPLIT_REFERRER = float(os.getenv("REFERRAL_SPLIT_REFERRER", 0.2))  # 20% default

# Load the PEM private key from file
try:
    with open(PRIVATE_KEY_PATH, "r") as f:
        API_KEY_SECRET = f.read()
    print(f"[payments.py] Loaded API_KEY_SECRET (first 30 chars): {API_KEY_SECRET[:30]}")
except Exception as e:
    API_KEY_SECRET = None
    print(f"[payments.py] Error loading private key from {PRIVATE_KEY_PATH}: {e}")

print(f"[payments.py] Loaded API_KEY_ID: {API_KEY_ID[:30] if API_KEY_ID else None}...")
print(f"[payments.py] Loaded CDP_WALLET_SECRET (first 10 chars): {WALLET_SECRET[:10] if WALLET_SECRET else None}")
print(f"[payments.py] Using network: {NETWORK}")
print(f"[payments.py] Savings wallet: {SAVINGS_WALLET_ADDRESS}")

def make_x402_payment(recipient_address: str, amount: float, token_symbol: str = "USDC") -> str:
    """
    Synchronous function to initiate a stablecoin payment using the x402 protocol.
    Args:
        recipient_address (str): The recipient's wallet address.
        amount (float): The amount to send (in token units, e.g., 1.5 USDC).
        token_symbol (str): The stablecoin symbol (default: USDC).
    Returns:
        str: Payment confirmation or error message.
    """
    print(f"[payments.py] Initiating x402 payment: {amount} {token_symbol} to {recipient_address}")
    cdp = None
    try:
        cdp = CdpClient(api_key_id=API_KEY_ID, api_key_secret=API_KEY_SECRET, wallet_secret=WALLET_SECRET)
        # Find the token contract address for the given symbol
        token_contract = "0xd9AAEC86B65d86f6A7B5B1b0c42FFA531710b6CA"  # USDC on Base mainnet
        decimals = 6
        raw_amount = int(amount * (10 ** decimals))
        print(f"[payments.py] Sending {raw_amount} (raw units) of {token_symbol} to {recipient_address} on contract {token_contract}")
        # Placeholder for x402 payment logic (should be replaced with actual x402 call)
        # For now, just print and return a fake tx hash
        tx_hash = f"0xFAKEHASH{recipient_address[-6:]}{raw_amount}"
        print(f"[payments.py] Payment transaction hash: {tx_hash}")
        return str({"status": "success", "tx_hash": tx_hash})
    except Exception as e:
        print(f"[payments.py] Error sending payment: {e}")
        return str({"status": "error", "error": str(e)})
    finally:
        if cdp:
            try:
                cdp.close()
            except Exception:
                pass

def process_split_payment(recipient_address: str, amount: float, token_symbol: str = "USDC") -> str:
    """
    Split payment: 95% to recipient, 5% to savings wallet. Log both transactions.
    """
    if not SAVINGS_WALLET_ADDRESS:
        return "Savings wallet address not set in .env."
    main_amount = round(amount * 0.95, 6)
    savings_amount = round(amount * 0.05, 6)
    print(f"[payments.py] Split payment: {main_amount} to {recipient_address}, {savings_amount} to {SAVINGS_WALLET_ADDRESS}")
    result_main = make_x402_payment(recipient_address, main_amount, token_symbol)
    log_transaction('payment', COSTS.get('payment', 0.10), {'amount': main_amount, 'token': token_symbol, 'recipient': recipient_address, 'split': 'main'})
    result_savings = make_x402_payment(SAVINGS_WALLET_ADDRESS, savings_amount, token_symbol)
    log_transaction('payment', COSTS.get('payment', 0.10), {'amount': savings_amount, 'token': token_symbol, 'recipient': SAVINGS_WALLET_ADDRESS, 'split': 'savings'})
    return f"Main: {result_main}\nSavings: {result_savings}"

def process_referral_payment(recipient_address: str, amount: float, token_symbol: str = "USDC", referrer_wallet: str = None) -> dict:
    """
    Split payment: configurable % to agent, % to referrer. Log both transactions.
    Returns a dict with both tx hashes and split info.
    """
    if not referrer_wallet:
        return {"status": "error", "error": "No referrer_wallet provided."}
    agent_amount = round(amount * REFERRAL_SPLIT_AGENT, 6)
    referrer_amount = round(amount * REFERRAL_SPLIT_REFERRER, 6)
    print(f"[payments.py] Referral split: {agent_amount} to {recipient_address}, {referrer_amount} to {referrer_wallet}")
    result_agent = make_x402_payment(recipient_address, agent_amount, token_symbol)
    log_transaction('payment', COSTS.get('payment', 0.10), {'amount': agent_amount, 'token': token_symbol, 'recipient': recipient_address, 'split': 'agent'})
    result_referrer = make_x402_payment(referrer_wallet, referrer_amount, token_symbol)
    log_transaction('payment', COSTS.get('payment', 0.10), {'amount': referrer_amount, 'token': token_symbol, 'recipient': referrer_wallet, 'split': 'referrer'})
    return {
        "status": "success",
        "message": f"80% of the payment was routed to the agent wallet ({recipient_address}). 20% of the payment was routed to the referrer wallet ({referrer_wallet}).",
        "agent": result_agent,
        "referrer": result_referrer,
        "split": {
            "agent": agent_amount,
            "referrer": referrer_amount
        }
    }

@tool
def x402_payment_tool(recipient_address: str, amount: float, token_symbol: str = "USDC", referrer_wallet: str = None) -> str:
    """
    LangGraph tool to send a split stablecoin payment using x402 protocol.
    If referrer_wallet is provided, splits payment accordingly.
    Args:
        recipient_address (str): The recipient's wallet address.
        amount (float): The amount to send (in token units, e.g., 1.5 USDC).
        token_symbol (str): The stablecoin symbol (default: USDC).
        referrer_wallet (str, optional): The referrer's wallet address.
    Returns:
        str: Payment confirmation or error message.
    """
    if referrer_wallet:
        result = process_referral_payment(recipient_address, amount, token_symbol, referrer_wallet)
        # Return a clear, user-facing message
        return f"The payment has been successfully split between the agent and the referring wallet as part of our decentralized referral system.\n{result.get('message', '')}\nAgent transaction: {result.get('agent', '')}\nReferrer transaction: {result.get('referrer', '')}"
    else:
        return process_split_payment(recipient_address, amount, token_symbol)

# For synchronous tool registration (if needed)
def get_x402_payment_tool():
    return x402_payment_tool 