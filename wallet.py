import asyncio
import os
from cdp import CdpClient
from dotenv import load_dotenv

load_dotenv()

API_KEY_ID = os.getenv("CDP_API_KEY_ID")
PRIVATE_KEY_PATH = "secrets/cdp_private_key.pem"
WALLET_SECRET = os.getenv("CDP_WALLET_SECRET")
NETWORK = "base"  # Use Base mainnet

# Load the PEM private key from file
try:
    with open(PRIVATE_KEY_PATH, "r") as f:
        API_KEY_SECRET = f.read()
    print(f"[wallet.py] Loaded API_KEY_SECRET (first 30 chars): {API_KEY_SECRET[:30]}")
except Exception as e:
    API_KEY_SECRET = None
    print(f"[wallet.py] Error loading private key from {PRIVATE_KEY_PATH}: {e}")

print(f"[wallet.py] Loaded API_KEY_ID: {API_KEY_ID[:30] if API_KEY_ID else None}...")
print(f"[wallet.py] Loaded CDP_WALLET_SECRET (first 10 chars): {WALLET_SECRET[:10] if WALLET_SECRET else None}")
print(f"[wallet.py] Using network: {NETWORK}")

async def create_wallet():
    """Create a new on-chain wallet using CDP"""
    print("[wallet.py] Creating new EVM account...")
    cdp = None
    try:
        cdp = CdpClient(api_key_id=API_KEY_ID, api_key_secret=API_KEY_SECRET, wallet_secret=WALLET_SECRET)
        account = await cdp.evm.create_account()
        print(f"[wallet.py] Created EVM account: {account.address}")
        return account
    except Exception as e:
        print(f"[wallet.py] Error creating wallet: {e}")
        return None
    finally:
        if cdp:
            await cdp.close()

async def get_wallet_balances(account):
    """Get wallet balances using CDP client and print all asset symbols and amounts."""
    print(f"[wallet.py] Fetching wallet balances for address: {account.address} on network: {NETWORK}")
    cdp = None
    try:
        cdp = CdpClient(api_key_id=API_KEY_ID, api_key_secret=API_KEY_SECRET, wallet_secret=WALLET_SECRET)
        result = await cdp.evm.list_token_balances(account.address, NETWORK)
        print(f"[wallet.py] list_token_balances result type: {type(result)}")
        print(f"[wallet.py] list_token_balances result: {result}")
        # Try to access balances attribute or unpack tuple
        balances = None
        if hasattr(result, 'balances'):
            balances = result.balances
            print(f"[wallet.py] result.balances: {balances}")
        elif isinstance(result, tuple) and len(result) > 0:
            balances = result[0]
            print(f"[wallet.py] tuple[0] as balances: {balances}")
        else:
            print(f"[wallet.py] Unexpected result structure: {result}")
        if balances:
            for i, balance in enumerate(balances):
                if hasattr(balance, 'token') and hasattr(balance, 'amount'):
                    symbol = getattr(balance.token, 'symbol', 'UNKNOWN')
                    raw_amount = getattr(balance.amount, 'amount', 0)
                    decimals = getattr(balance.amount, 'decimals', 18)
                    try:
                        eth_amount = int(raw_amount) / (10 ** int(decimals))
                    except Exception:
                        eth_amount = raw_amount
                    print(f"[wallet.py] {symbol}: {eth_amount}")
                elif hasattr(balance, 'asset_symbol') and hasattr(balance, 'amount'):
                    print(f"[wallet.py] {balance.asset_symbol}: {balance.amount}")
                elif isinstance(balance, dict):
                    print(f"[wallet.py] {balance.get('asset_symbol', 'UNKNOWN')}: {balance.get('amount', '0')}")
                else:
                    print(f"[wallet.py] Unexpected balance format at index {i}: {balance} (type: {type(balance)})")
        else:
            print("[wallet.py] No balances found.")
        return balances
    except Exception as e:
        print(f"[wallet.py] Error fetching balances: {e}")
        return f"Error fetching wallet balances: {str(e)}"
    finally:
        if cdp:
            await cdp.close()

async def get_wallet_balances_async(account):
    """Async version of get_wallet_balances for use in FastAPI endpoints"""
    return await get_wallet_balances(account)

def get_wallet_balances_sync(account):
    """Synchronous wrapper for get_wallet_balances"""
    try:
        # Try to get the current event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an event loop, create a task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, get_wallet_balances(account))
                return future.result()
        else:
            # If no event loop is running, we can use asyncio.run
            return asyncio.run(get_wallet_balances(account))
    except RuntimeError:
        # Fallback: create a new event loop in a separate thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, get_wallet_balances(account))
            return future.result()

async def main():
    print("[wallet.py] Checking balance for existing account...")
    address = "0xE132d512FC35Bf91aD0C1098031CE09A9BA95241"
    class DummyAccount:
        def __init__(self, address):
            self.address = address
    account = DummyAccount(address)
    balances = await get_wallet_balances(account)
    print(f"[wallet.py] Final result: {balances}")

if __name__ == "__main__":
    asyncio.run(main())
