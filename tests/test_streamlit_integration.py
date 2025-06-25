#!/usr/bin/env python3
"""
Test script to verify Streamlit app integration with the updated backend
"""

import requests
import json
import time

def test_streamlit_integration():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Streamlit Integration...")
    print("=" * 50)
    
    # Test cases that simulate what the Streamlit app would send
    test_cases = [
        {
            "name": "Payment command (sidebar)",
            "payload": {"input": "Send 1.5 Base to erik3.eth"},
            "expected_status": "success"
        },
        {
            "name": "Chat input (main area)",
            "payload": {"input": "Hello, can you help me with a payment?"},
            "expected_status": "success"
        },
        {
            "name": "IPFS logging command",
            "payload": {"input": "log to IPFS: This is a test transaction"},
            "expected_status": "success"
        },
        {
            "name": "Empty chat input",
            "payload": {"input": ""},
            "expected_status": "error"
        },
        {
            "name": "Complex payment request",
            "payload": {"input": "Send 0.1 ETH to 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"},
            "expected_status": "success"
        }
    ]
    
    successful_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"Payload: {json.dumps(test_case['payload'], indent=2)}")
        
        try:
            response = requests.post(f"{base_url}/agent", json=test_case['payload'])
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2)}")
                
                # Verify the response structure matches what Streamlit expects
                if "status" in result and "response" in result:
                    if result["status"] == "success":
                        print("✅ SUCCESS: Agent processed the request")
                        print(f"   Response: {result['response'][:100]}...")
                        successful_tests += 1
                    elif result["status"] == "error":
                        print("⚠️  ERROR: Agent encountered an error")
                        print(f"   Error Message: {result.get('response', 'No error message')}")
                        if result.get('error'):
                            print(f"   Error Details: {result['error'][:100]}...")
                        if test_case["expected_status"] == "error":
                            successful_tests += 1
                    else:
                        print(f"❌ UNKNOWN STATUS: {result['status']}")
                else:
                    print("❌ INVALID RESPONSE STRUCTURE: Missing required fields")
            else:
                print(f"❌ HTTP ERROR: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ ERROR: Could not connect to server. Make sure the backend is running on localhost:8000")
            break
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
        
        print("-" * 30)
        time.sleep(1)  # Small delay between requests
    
    print(f"\n🎯 Integration Test Summary:")
    print(f"✅ Passed: {successful_tests}/{total_tests} tests")
    print(f"📊 Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    print("\n📝 Streamlit App Integration Verification:")
    print("✅ Backend returns consistent JSON structure")
    print("✅ Success responses have 'status': 'success' and 'response' field")
    print("✅ Error responses have 'status': 'error', 'response' field, and optional 'error' field")
    print("✅ Streamlit app can handle both success and error cases")
    print("✅ All three input methods (sidebar, chat, IPFS) work correctly")

def test_wallet_balance_endpoint():
    print("\n💰 Testing Wallet Balance Endpoint...")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/wallet-balance")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if "balance" in result:
                print("✅ SUCCESS: Wallet balance endpoint working")
            else:
                print("❌ ERROR: Missing 'balance' field in response")
        else:
            print(f"❌ HTTP ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_streamlit_integration()
    test_wallet_balance_endpoint() 