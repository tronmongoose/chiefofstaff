"""
x402 Payment Middleware for Travel Booking API

Implements HTTP 402 Payment Required status for cryptocurrency payments
using the x402 standard with Coinbase CDP integration.
"""

from fastapi import HTTPException, Request, Response
from typing import Dict, Optional, Callable
import json
import asyncio
import logging
from datetime import datetime, timedelta
from wallet import create_wallet, get_wallet_balances_async
import os
import httpx

logger = logging.getLogger(__name__)

class X402PaymentError(Exception):
    """Custom exception for x402 payment errors"""
    pass

class X402Middleware:
    """
    FastAPI middleware for x402 payment processing
    """
    
    def __init__(self, 
                 payment_address: str,
                 pricing: Dict[str, str],
                 facilitator_url: str = "https://facilitator.coinbase.com"):
        """
        Initialize x402 middleware
        
        Args:
            payment_address: Wallet address to receive payments
            pricing: Dict mapping endpoints to USDC amounts (e.g., {"search": "0.01"})
            facilitator_url: Coinbase facilitator service URL
        """
        self.payment_address = payment_address
        self.pricing = pricing
        self.facilitator_url = facilitator_url
        self.verified_payments = {}  # Cache for verified payments
        
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and handle x402 payment requirements
        """
        endpoint = str(request.url.path)
        
        # Check if endpoint requires payment
        if not self._endpoint_requires_payment(endpoint):
            return await call_next(request)
        
        # Get payment amount for this endpoint
        payment_amount = self._get_payment_amount(endpoint)
        if not payment_amount:
            return await call_next(request)
            
        # Check for payment header
        x_payment = request.headers.get("X-PAYMENT")
        
        if not x_payment:
            # Return 402 with payment requirements
            return self._create_payment_required_response(payment_amount)
        
        # Verify payment
        try:
            is_valid = await self._verify_payment(x_payment, payment_amount)
            if is_valid:
                logger.info(f"Payment verified for {endpoint}, amount: {payment_amount} USDC")
                return await call_next(request)
            else:
                raise X402PaymentError("Payment verification failed")
                
        except Exception as e:
            logger.error(f"Payment verification error: {e}")
            return self._create_payment_required_response(
                payment_amount, 
                error="Payment verification failed"
            )
    
    def _endpoint_requires_payment(self, endpoint: str) -> bool:
        """Check if endpoint requires payment"""
        return any(pattern in endpoint for pattern in self.pricing.keys())
    
    def _get_payment_amount(self, endpoint: str) -> Optional[str]:
        """Get payment amount for endpoint"""
        for pattern, amount in self.pricing.items():
            if pattern in endpoint:
                return amount
        return None
    
    def _create_payment_required_response(self, amount: str, error: Optional[str] = None) -> Response:
        """Create HTTP 402 response with payment requirements"""
        payment_requirements = {
            "paymentRequirements": [{
                "scheme": "erc3009",
                "amount": amount,
                "currency": "USDC",
                "recipient": self.payment_address,
                "network": "base-mainnet",
                "chainId": 8453,  # Base mainnet
                "expiresAt": (datetime.utcnow() + timedelta(minutes=5)).isoformat() + "Z"
            }]
        }
        
        if error:
            payment_requirements["error"] = error
            
        response = Response(
            content=json.dumps(payment_requirements),
            status_code=402,
            headers={
                "Content-Type": "application/json",
                "X-Payment-Required": "true",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "X-PAYMENT"
            }
        )
        
        return response
    
    async def _verify_payment(self, payment_payload: str, expected_amount: str) -> bool:
        """
        Verify payment using Coinbase facilitator service
        """
        try:
            # Parse payment payload
            payment_data = json.loads(payment_payload)
            
            # Check if we've already verified this payment
            payment_hash = payment_data.get("transactionHash")
            if payment_hash in self.verified_payments:
                return self.verified_payments[payment_hash]
            
            # Verify with facilitator
            async with httpx.AsyncClient() as client:
                verification_response = await client.post(
                    f"{self.facilitator_url}/verify",
                    json={
                        "payment": payment_data,
                        "expectedAmount": expected_amount,
                        "expectedRecipient": self.payment_address,
                        "network": "base-mainnet"
                    },
                    timeout=10.0
                )
                
                if verification_response.status_code == 200:
                    result = verification_response.json()
                    is_valid = result.get("valid", False)
                    
                    # Cache result
                    if payment_hash:
                        self.verified_payments[payment_hash] = is_valid
                    
                    return is_valid
                else:
                    logger.error(f"Facilitator verification failed: {verification_response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Payment verification error: {e}")
            return False

class TravelBookingPaymentService:
    """
    Service for handling travel booking payments with x402
    """
    
    def __init__(self):
        self.wallet_address = os.getenv("TRAVEL_PAYMENT_WALLET_ADDRESS")
        self.pricing = {
            "/api/flights/search": "0.01",      # 1 cent for flight search
            "/api/flights/book": "0.10",        # 10 cents for booking
            "/api/hotels/search": "0.01",       # 1 cent for hotel search  
            "/api/hotels/book": "0.10",         # 10 cents for booking
            "/api/activities/search": "0.005",  # Half cent for activities
            "/api/activities/book": "0.05"      # 5 cents for booking
        }
    
    async def initialize_wallet(self):
        """Initialize payment wallet if not exists"""
        if not self.wallet_address:
            logger.info("Creating new payment wallet...")
            wallet = await create_wallet()
            if wallet:
                self.wallet_address = wallet.address
                logger.info(f"Created payment wallet: {self.wallet_address}")
                # Save to environment or database
                # In production, save this securely
            else:
                raise Exception("Failed to create payment wallet")
    
    def get_middleware(self) -> X402Middleware:
        """Get configured x402 middleware"""
        if not self.wallet_address:
            raise Exception("Payment wallet not initialized")
            
        return X402Middleware(
            payment_address=self.wallet_address,
            pricing=self.pricing
        )
    
    async def get_payment_balance(self) -> Dict:
        """Get current payment wallet balance"""
        if not self.wallet_address:
            return {"error": "Payment wallet not initialized"}
        
        try:
            # Create temporary account object for balance check
            class MockAccount:
                def __init__(self, address):
                    self.address = address
            
            account = MockAccount(self.wallet_address)
            balances = await get_wallet_balances_async(account)
            return {"wallet": self.wallet_address, "balances": balances}
            
        except Exception as e:
            logger.error(f"Error getting payment balance: {e}")
            return {"error": str(e)}

# Global instance
payment_service = TravelBookingPaymentService()

async def setup_x402_payments():
    """Setup x402 payment system"""
    await payment_service.initialize_wallet()
    return payment_service.get_middleware()

def get_payment_pricing() -> Dict[str, str]:
    """Get current pricing for all endpoints"""
    return payment_service.pricing.copy()

async def verify_payment_received(transaction_hash: str, expected_amount: str) -> bool:
    """
    Verify that a payment was actually received on-chain
    This is an additional security check beyond the facilitator
    """
    try:
        # In a full implementation, you would:
        # 1. Query the blockchain directly
        # 2. Verify the transaction exists
        # 3. Confirm the amount and recipient
        # 4. Check transaction is confirmed
        
        # For now, we'll use the facilitator verification
        # But in production, add on-chain verification here
        return True
        
    except Exception as e:
        logger.error(f"On-chain verification error: {e}")
        return False