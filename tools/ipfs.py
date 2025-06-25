import os
import requests
from dotenv import load_dotenv

load_dotenv()

PINATA_JWT = os.getenv("PINATA_JWT")


def upload_to_ipfs(json_payload):
    """
    Uploads a JSON payload to IPFS via Pinata and returns the IPFS hash.
    Args:
        json_payload (dict): The JSON data to upload.
    Returns:
        str: The IPFS hash from Pinata's response.
    Raises:
        Exception: If the upload fails or the response is invalid.
    """
    if not PINATA_JWT:
        raise ValueError("PINATA_JWT not found in environment variables.")

    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    headers = {
        "Authorization": f"Bearer {PINATA_JWT}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=json_payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    if "IpfsHash" not in data:
        raise Exception(f"Unexpected response from Pinata: {data}")
    return data["IpfsHash"]

def retrieve_referrals_by_wallet(wallet_address: str, gateway_url: str = "https://gateway.pinata.cloud/ipfs/"):
    """
    Retrieve referral records from IPFS by wallet address. This is a demo implementation that expects a list of known IPFS hashes.
    Args:
        wallet_address (str): The wallet address to search for (referrer or referee).
        gateway_url (str): The IPFS gateway URL to use for fetching records.
    Returns:
        list: List of matching referral records.
    """
    # In a real system, you would index or search IPFS. For demo, scan a known list of hashes.
    known_hashes = os.getenv("REFERRAL_IPFS_HASHES", "").split(",")
    matches = []
    for ipfs_hash in known_hashes:
        ipfs_hash = ipfs_hash.strip()
        if not ipfs_hash:
            continue
        try:
            url = f"{gateway_url}{ipfs_hash}"
            resp = requests.get(url)
            resp.raise_for_status()
            record = resp.json()
            if wallet_address.lower() in (str(record.get("referrer_wallet", "")).lower(), str(record.get("referee_wallet", "")).lower()):
                matches.append({"ipfs_hash": ipfs_hash, **record})
        except Exception as e:
            print(f"[ipfs.py] Error fetching {ipfs_hash}: {e}")
    return matches 