"""
Pinata IPFS Service for storing travel bookings, plans, and reputation records
"""
import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests
from dotenv import load_dotenv
from reputation_models import ReputationRecord, ReputationSummary, IPFSStorageUtils

load_dotenv()

class PinataIPFSService:
    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None):
        """
        Initialize Pinata IPFS service
        
        Args:
            api_key: Pinata API key (defaults to PINATA_API_KEY env var)
            secret_key: Pinata secret key (defaults to PINATA_SECRET_KEY env var)
        """
        self.api_key = api_key or os.getenv("PINATA_API_KEY")
        self.secret_key = secret_key or os.getenv("PINATA_SECRET_KEY")
        self.base_url = "https://api.pinata.cloud"
        
        if not self.api_key or not self.secret_key:
            print("⚠️  Warning: Pinata credentials not found. IPFS storage will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Pinata API"""
        if not self.enabled:
            return {"error": "Pinata service not enabled"}
        
        headers = {
            "pinata_api_key": self.api_key,
            "pinata_secret_api_key": self.secret_key,
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                response = requests.get(url, headers=headers)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Pinata API error: {e}")
            return {"error": str(e)}
    
    def store_booking_data(self, booking_data: Dict[str, Any]) -> str:
        """
        Store booking confirmation on IPFS via Pinata
        
        Args:
            booking_data: Booking information to store
            
        Returns:
            IPFS hash of the stored data
        """
        if not self.enabled:
            return "ipfs://disabled"
        
        # Add metadata
        metadata = {
            "name": f"travel-booking-{datetime.now().isoformat()}",
            "description": "Travel booking confirmation stored on IPFS",
            "type": "travel-booking",
            "timestamp": datetime.now().isoformat(),
            "data": booking_data
        }
        
        result = self._make_request("/pinning/pinJSONToIPFS", method="POST", data=metadata)
        
        if "error" in result:
            print(f"❌ Failed to store booking on IPFS: {result['error']}")
            return "ipfs://error"
        
        ipfs_hash = result.get("IpfsHash")
        print(f"✅ Booking stored on IPFS: ipfs://{ipfs_hash}")
        return f"ipfs://{ipfs_hash}"
    
    def store_travel_plan(self, plan_data: Dict[str, Any]) -> str:
        """
        Store travel plan on IPFS via Pinata
        
        Args:
            plan_data: Travel plan information to store
            
        Returns:
            IPFS hash of the stored data
        """
        if not self.enabled:
            return "ipfs://disabled"
        
        # Add metadata
        metadata = {
            "name": f"travel-plan-{datetime.now().isoformat()}",
            "description": "Travel plan stored on IPFS",
            "type": "travel-plan",
            "timestamp": datetime.now().isoformat(),
            "data": plan_data
        }
        
        result = self._make_request("/pinning/pinJSONToIPFS", method="POST", data=metadata)
        
        if "error" in result:
            print(f"❌ Failed to store travel plan on IPFS: {result['error']}")
            return "ipfs://error"
        
        ipfs_hash = result.get("IpfsHash")
        print(f"✅ Travel plan stored on IPFS: ipfs://{ipfs_hash}")
        return f"ipfs://{ipfs_hash}"
    
    def store_travel_documents(self, documents_data: Dict[str, Any]) -> str:
        """
        Store travel documents on IPFS via Pinata
        
        Args:
            documents_data: Travel documents to store
            
        Returns:
            IPFS hash of the stored data
        """
        if not self.enabled:
            return "ipfs://disabled"
        
        # Add metadata
        metadata = {
            "name": f"travel-documents-{datetime.now().isoformat()}",
            "description": "Travel documents stored on IPFS",
            "type": "travel-documents",
            "timestamp": datetime.now().isoformat(),
            "data": documents_data
        }
        
        result = self._make_request("/pinning/pinJSONToIPFS", method="POST", data=metadata)
        
        if "error" in result:
            print(f"❌ Failed to store travel documents on IPFS: {result['error']}")
            return "ipfs://error"
        
        ipfs_hash = result.get("IpfsHash")
        print(f"✅ Travel documents stored on IPFS: ipfs://{ipfs_hash}")
        return f"ipfs://{ipfs_hash}"
    
    def store_reputation_record(self, record: ReputationRecord) -> str:
        """
        Store reputation record on IPFS via Pinata
        
        Args:
            record: ReputationRecord to store
            
        Returns:
            IPFS hash of the stored record
        """
        if not self.enabled:
            return "ipfs://disabled"
        
        # Convert record to JSON
        record_json = record.to_ipfs_json()
        
        # Generate IPFS path and filename
        year = record.event_timestamp.year
        month = record.event_timestamp.month
        ipfs_path = IPFSStorageUtils.generate_ipfs_path(record.traveler_wallet, year, month)
        filename = IPFSStorageUtils.generate_record_filename(record)
        
        # Add metadata
        metadata = {
            "name": filename,
            "description": f"Reputation record for {record.traveler_wallet} - {record.event_type}",
            "type": "reputation-record",
            "timestamp": record.event_timestamp.isoformat(),
            "ipfs_path": ipfs_path,
            "data": json.loads(record_json)
        }
        
        result = self._make_request("/pinning/pinJSONToIPFS", method="POST", data=metadata)
        
        if "error" in result:
            print(f"❌ Failed to store reputation record on IPFS: {result['error']}")
            return "ipfs://error"
        
        ipfs_hash = result.get("IpfsHash")
        print(f"✅ Reputation record stored on IPFS: ipfs://{ipfs_hash}")
        return f"ipfs://{ipfs_hash}"
    
    def get_reputation_record(self, ipfs_hash: str) -> Optional[ReputationRecord]:
        """
        Retrieve reputation record from IPFS
        
        Args:
            ipfs_hash: IPFS hash of the reputation record
            
        Returns:
            ReputationRecord object or None if failed
        """
        if not self.enabled:
            return None
        
        # Remove ipfs:// prefix if present
        if ipfs_hash.startswith("ipfs://"):
            ipfs_hash = ipfs_hash[7:]
        
        try:
            # Use Pinata's public gateway
            url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract the actual record data from metadata
            if "data" in data:
                record_data = data["data"]
            else:
                record_data = data
            
            # Create ReputationRecord from JSON
            return ReputationRecord(**record_data)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to retrieve reputation record: {e}")
            return None
        except Exception as e:
            print(f"❌ Failed to parse reputation record: {e}")
            return None
    
    def update_reputation_summary(self, summary: ReputationSummary) -> str:
        """
        Store or update reputation summary on IPFS
        
        Args:
            summary: ReputationSummary to store
            
        Returns:
            IPFS hash of the stored summary
        """
        if not self.enabled:
            return "ipfs://disabled"
        
        # Convert summary to JSON
        summary_json = json.dumps(summary.model_dump(exclude_none=True), indent=2)
        
        # Generate IPFS path
        ipfs_path = IPFSStorageUtils.generate_summary_path(summary.wallet_address)
        
        # Add metadata
        metadata = {
            "name": "reputation-summary.json",
            "description": f"Reputation summary for {summary.wallet_address}",
            "type": "reputation-summary",
            "timestamp": summary.last_updated.isoformat(),
            "ipfs_path": ipfs_path,
            "data": json.loads(summary_json)
        }
        
        result = self._make_request("/pinning/pinJSONToIPFS", method="POST", data=metadata)
        
        if "error" in result:
            print(f"❌ Failed to store reputation summary on IPFS: {result['error']}")
            return "ipfs://error"
        
        ipfs_hash = result.get("IpfsHash")
        print(f"✅ Reputation summary stored on IPFS: ipfs://{ipfs_hash}")
        return f"ipfs://{ipfs_hash}"
    
    def get_wallet_reputation(self, wallet_address: str, limit: int = 50) -> Dict[str, Any]:
        """
        Get wallet reputation data including summary and recent records
        
        Args:
            wallet_address: Wallet address to get reputation for
            limit: Maximum number of recent records to retrieve
            
        Returns:
            Dictionary containing reputation summary and recent records
        """
        if not self.enabled:
            return {"error": "Pinata service not enabled"}
        
        try:
            # Get reputation summary
            summary_path = IPFSStorageUtils.generate_summary_path(wallet_address)
            
            # For now, we'll return a basic structure
            # In a full implementation, you'd query IPFS for the actual summary
            result = {
                "wallet_address": wallet_address,
                "summary": None,
                "recent_records": [],
                "total_records": 0
            }
            
            # Try to get summary from IPFS (this would need to be implemented
            # with actual IPFS querying based on your storage structure)
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to get wallet reputation: {e}")
            return {"error": str(e)}
    
    def get_ipfs_data(self, ipfs_hash: str) -> Optional[Dict]:
        """
        Retrieve data from IPFS via Pinata gateway
        
        Args:
            ipfs_hash: IPFS hash to retrieve
            
        Returns:
            Retrieved data or None if failed
        """
        if not self.enabled:
            return None
        
        # Remove ipfs:// prefix if present
        if ipfs_hash.startswith("ipfs://"):
            ipfs_hash = ipfs_hash[7:]
        
        try:
            # Use Pinata's public gateway
            url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to retrieve IPFS data: {e}")
            return None

# Global instance
pinata_service = PinataIPFSService() 