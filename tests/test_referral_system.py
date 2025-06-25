#!/usr/bin/env python3
"""
Test script for decentralized referral system
"""

import requests
import json
import time

def test_referral_system():
    print("🎯 Testing Decentralized Referral System")
    print("=" * 60)
    
    # Test 1: Agent request with referrer_wallet
    print("\n1️⃣ Testing Agent Request with Referrer Wallet...")
    test_cases = [
        {
            "input": "Plan a trip to Paris for next week",
            "referrer_wallet": "0x1234567890123456789012345678901234567890"
        },
        {
            "input": "Pay 10 USDC to 0xE132d512FC35Bf91aD0C1098031CE09A9BA95241",
            "referrer_wallet": "0x9876543210987654321098765432109876543210"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test {i}: '{test_case['input']}' with referrer {test_case['referrer_wallet'][:10]}...")
        try:
            payload = {
                "input": test_case["input"],
                "referrer_wallet": test_case["referrer_wallet"]
            }
            response = requests.post("http://localhost:8000/agent", json=payload)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Status: {result.get('status')}")
                print(f"   Response: {result.get('response', '')[:100]}...")
                
                if result.get('status') == 'success':
                    print("   ✅ Agent processed request with referrer successfully")
                else:
                    print("   ⚠️  Agent encountered an error")
                    if result.get('error'):
                        print(f"   Error details: {result['error'][:100]}...")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
        
        time.sleep(2)  # Delay between requests
    
    # Test 2: Direct referral retrieval endpoint
    print("\n2️⃣ Testing Referral Retrieval Endpoint...")
    test_wallets = [
        "0x1234567890123456789012345678901234567890",
        "0x9876543210987654321098765432109876543210",
        "0xE132d512FC35Bf91aD0C1098031CE09A9BA95241"
    ]
    
    for wallet in test_wallets:
        print(f"\n   Testing wallet: {wallet[:10]}...")
        try:
            response = requests.get(f"http://localhost:8000/referrals/{wallet}")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Status: {result.get('status')}")
                if result.get('status') == 'success':
                    records = result.get('response', [])
                    print(f"   Found {len(records)} referral records")
                    for j, record in enumerate(records):
                        print(f"     Record {j+1}: {record.get('ipfs_hash', 'N/A')[:10]}...")
                else:
                    print(f"   Error: {result.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
        
        time.sleep(1)
    
    # Test 3: Agent with referral retrieval request
    print("\n3️⃣ Testing Agent with Referral Retrieval Request...")
    retrieval_queries = [
        "Show me referrals for 0x1234567890123456789012345678901234567890",
        "Get referral records for wallet 0x9876543210987654321098765432109876543210",
        "What referrals do I have for 0xE132d512FC35Bf91aD0C1098031CE09A9BA95241"
    ]
    
    for i, query in enumerate(retrieval_queries, 1):
        print(f"\n   Test {i}: '{query}'")
        try:
            payload = {"input": query}
            response = requests.post("http://localhost:8000/agent", json=payload)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Status: {result.get('status')}")
                print(f"   Response: {result.get('response', '')[:150]}...")
                
                if result.get('status') == 'success':
                    print("   ✅ Agent processed referral retrieval request successfully")
                else:
                    print("   ⚠️  Agent encountered an error")
                    if result.get('error'):
                        print(f"   Error details: {result['error'][:100]}...")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
        
        time.sleep(1)
    
    # Test 4: Payment split verification
    print("\n4️⃣ Testing Payment Split with Referrer...")
    payment_test = {
        "input": "Pay 5 USDC to 0xE132d512FC35Bf91aD0C1098031CE09A9BA95241",
        "referrer_wallet": "0x1234567890123456789012345678901234567890"
    }
    
    print(f"   Testing payment: {payment_test['input']} with referrer {payment_test['referrer_wallet'][:10]}...")
    try:
        response = requests.post("http://localhost:8000/agent", json=payment_test)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Status: {result.get('status')}")
            print(f"   Response: {result.get('response', '')[:200]}...")
            
            if result.get('status') == 'success':
                print("   ✅ Payment with referrer processed successfully")
                # Check if response mentions split or referral
                response_text = result.get('response', '').lower()
                if any(word in response_text for word in ['split', 'referral', '80%', '20%', 'agent', 'referrer']):
                    print("   ✅ Payment split mentioned in response")
                else:
                    print("   ⚠️  Payment split not clearly mentioned in response")
            else:
                print("   ⚠️  Payment encountered an error")
                if result.get('error'):
                    print(f"   Error details: {result['error'][:100]}...")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Referral System Test Summary:")
    print("✅ Agent should accept referrer_wallet parameter")
    print("✅ Payment should split between agent and referrer")
    print("✅ Referral records should be posted to IPFS")
    print("✅ Referral retrieval endpoint should work")
    print("✅ Agent should handle referral retrieval requests")

if __name__ == "__main__":
    test_referral_system() 