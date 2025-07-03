#!/usr/bin/env python3
"""
Debug script to test x402 payment system initialization
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_payment_initialization():
    """Test the payment system initialization step by step"""
    
    print("🔍 Testing x402 Payment System Initialization")
    print("=" * 50)
    
    # Step 1: Test import
    try:
        print("1. Testing import...")
        from x402_middleware import payment_service, setup_x402_payments
        print("   ✅ Import successful")
        print(f"   Payment service type: {type(payment_service)}")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return
    
    # Step 2: Test payment service initialization
    try:
        print("\n2. Testing payment service initialization...")
        print(f"   Wallet address before: {payment_service.wallet_address}")
        
        await payment_service.initialize_wallet()
        print(f"   ✅ Wallet initialization successful")
        print(f"   Wallet address after: {payment_service.wallet_address}")
    except Exception as e:
        print(f"   ❌ Wallet initialization failed: {e}")
        return
    
    # Step 3: Test middleware setup
    try:
        print("\n3. Testing middleware setup...")
        middleware = await setup_x402_payments()
        print(f"   ✅ Middleware setup successful")
        print(f"   Middleware type: {type(middleware)}")
    except Exception as e:
        print(f"   ❌ Middleware setup failed: {e}")
        return
    
    # Step 4: Test pricing
    try:
        print("\n4. Testing pricing...")
        pricing = payment_service.pricing
        print(f"   ✅ Pricing retrieved successfully")
        print(f"   Pricing: {pricing}")
    except Exception as e:
        print(f"   ❌ Pricing retrieval failed: {e}")
        return
    
    print("\n🎉 All tests passed! Payment system should work correctly.")

if __name__ == "__main__":
    asyncio.run(test_payment_initialization()) 