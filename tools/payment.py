from langchain_core.tools import tool
from wallet import get_wallet_balances_async
from payments import x402_payment_tool
from tools.ipfs import upload_to_ipfs
import asyncio
import concurrent.futures
import threading

@tool
def check_wallet_balance() -> str:
    """
    Check wallet balance from Coinbase CDP API.
    """
    print("[payment.py] Invoking check_wallet_balance tool...")
    # For demo, use the mainnet account address
    class DummyAccount:
        def __init__(self, address):
            self.address = "0xE132d512FC35Bf91aD0C1098031CE09A9BA95241"
    account = DummyAccount("0xE132d512FC35Bf91aD0C1098031CE09A9BA95241")
    
    def run_async_balance_check():
        """Run the async balance check in a separate thread with its own event loop"""
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(get_wallet_balances_async(account))
                return result
            finally:
                loop.close()
        except Exception as e:
            return f"Error: {str(e)}"
    
    try:
        # Use ThreadPoolExecutor to run the async function in a separate thread
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_async_balance_check)
            result = future.result(timeout=30)  # 30 second timeout
            print(f"[payment.py] Tool result: {result}")
            return str(result)
    except concurrent.futures.TimeoutError:
        return "Wallet balance check timed out. Please try again."
    except Exception as e:
        print(f"[payment.py] Error checking wallet balance: {e}")
        return f"Error checking wallet balance: {str(e)}"

@tool
def upload_to_ipfs_tool(json_payload: dict) -> str:
    """
    Upload a JSON payload to IPFS via Pinata and return the IPFS hash.
    """
    return upload_to_ipfs(json_payload)

# Export the tool for use in the main application
WALLET_TOOLS = [check_wallet_balance, x402_payment_tool, upload_to_ipfs_tool] 