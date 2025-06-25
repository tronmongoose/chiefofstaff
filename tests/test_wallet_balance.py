#!/usr/bin/env python3
"""
Test script to verify wallet balance functionality
"""

import requests
import json
import time

def test_wallet_balance():
    print("🧪 Testing Wallet Balance Functionality")
    print("=" * 50)
    
    # Test 1: Direct wallet balance endpoint
    print("\n1️⃣ Testing Direct Wallet Balance Endpoint...")
    try:
        response = requests.get("http://localhost:8000/wallet-balance")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Direct endpoint working: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Direct endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Direct endpoint error: {e}")
    
    # Test 2: Agent with wallet balance request
    print("\n2️⃣ Testing Agent with Wallet Balance Request...")
    test_cases = [
        "What is my wallet balance?",
        "Check my wallet balance",
        "Show me my current balance",
        "How much money do I have?"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n   Test {i}: '{test_input}'")
        try:
            payload = {"input": test_input}
            response = requests.post("http://localhost:8000/agent", json=payload)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Status: {result.get('status')}")
                print(f"   Response: {result.get('response', '')[:100]}...")
                
                if result.get('status') == 'success':
                    print("   ✅ Agent processed wallet balance request successfully")
                else:
                    print("   ⚠️  Agent encountered an error")
                    if result.get('error'):
                        print(f"   Error details: {result['error'][:100]}...")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
        
        time.sleep(1)  # Small delay between requests
    
    print("\n" + "=" * 50)
    print("🎯 Wallet Balance Test Summary:")
    print("✅ Direct endpoint should return wallet balance")
    print("✅ Agent should be able to check wallet balance")
    print("✅ Both success and error cases should be handled properly")

if __name__ == "__main__":
    test_wallet_balance() 