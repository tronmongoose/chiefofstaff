#!/usr/bin/env python3
"""
Test script for x402 split payment functionality
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

async def test_split_payment_functionality():
    """Test the split payment functionality"""
    
    print("🧪 Testing x402 Split Payment Functionality")
    print("=" * 50)
    
    try:
        # Import the payment service
        from x402_middleware import TravelBookingPaymentService, get_split_payment_info
        
        print("✅ Successfully imported payment service")
        
        # Test 1: Create payment service instance
        print("\n1. Testing payment service initialization...")
        payment_service = TravelBookingPaymentService()
        print(f"   Platform fee percentage: {payment_service.platform_fee_percentage}%")
        print(f"   Platform wallet: {payment_service.platform_wallet}")
        print(f"   Main wallet: {payment_service.wallet_address}")
        
        # Test 2: Calculate split payment
        print("\n2. Testing split payment calculation...")
        test_amounts = [0.01, 0.10, 1.00, 10.00]
        
        for amount in test_amounts:
            split = payment_service.calculate_split_payment(amount)
            print(f"   Amount: ${amount}")
            print(f"     Merchant receives: ${split['merchant_amount']}")
            print(f"     Platform fee: ${split['platform_fee']}")
            print(f"     Total: ${split['total_amount']}")
            print()
        
        # Test 3: Test split payment info endpoint
        print("3. Testing split payment info function...")
        for amount in test_amounts:
            result = get_split_payment_info(amount)
            if result["status"] == "success":
                split = result["split_payment"]
                print(f"   ${amount} → Merchant: ${split['merchant_amount']}, Platform: ${split['platform_fee']}")
            else:
                print(f"   Error for ${amount}: {result['error']}")
        
        # Test 4: Test split payment processing (simulated)
        print("\n4. Testing split payment processing...")
        mock_payment_data = {
            "transactionHash": "0x1234567890abcdef",
            "amount": "0.10",
            "recipient": payment_service.wallet_address
        }
        
        result = await payment_service.process_split_payment(mock_payment_data, 0.10)
        print(f"   Processing result: {result}")
        
        # Test 5: Test with different platform fee percentages
        print("\n5. Testing different platform fee percentages...")
        original_fee = payment_service.platform_fee_percentage
        
        for fee_percentage in [5.0, 10.0, 15.0, 20.0]:
            payment_service.platform_fee_percentage = fee_percentage
            split = payment_service.calculate_split_payment(1.00)
            print(f"   {fee_percentage}% fee: Merchant gets ${split['merchant_amount']}, Platform gets ${split['platform_fee']}")
        
        # Restore original fee
        payment_service.platform_fee_percentage = original_fee
        
        print("\n✅ All split payment tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def test_api_endpoints():
    """Test the API endpoints for split payment functionality"""
    
    print("\n🌐 Testing API Endpoints")
    print("=" * 30)
    
    try:
        import httpx
        
        # Test split payment info endpoint
        base_url = "http://localhost:8000"
        
        print("1. Testing split payment info endpoint...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/payments/split-info/0.10")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success: {data}")
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text}")
        
        print("2. Testing payment pricing endpoint...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/payments/pricing")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success: {data}")
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"❌ API test failed: {e}")

async def main():
    """Main test function"""
    
    print("🚀 Starting x402 Split Payment Tests")
    print("=" * 50)
    
    # Test core functionality
    success = await test_split_payment_functionality()
    
    if success:
        # Test API endpoints if backend is running
        try:
            await test_api_endpoints()
        except Exception as e:
            print(f"⚠️  API tests skipped (backend may not be running): {e}")
    
    print("\n🎉 Test suite completed!")

if __name__ == "__main__":
    asyncio.run(main()) 