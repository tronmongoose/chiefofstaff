import asyncio
from cdp import CdpClient
from dotenv import load_dotenv

load_dotenv()

async def main():
    cdp = CdpClient()
    account = await cdp.evm.create_account()
    print(f"Created EVM account: {account.address}")
    await cdp.close()

if __name__ == "__main__":
    asyncio.run(main()) 