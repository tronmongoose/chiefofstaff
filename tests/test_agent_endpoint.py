#!/usr/bin/env python3
"""
Test script for the /agent endpoint to verify consistent JSON structure
"""

import requests
import json
import time

def test_agent_endpoint():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing /agent endpoint...")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Valid input with 'input' field",
            "payload": {"input": "Hello, how are you?"},
            "expected_status": "success"
        },
        {
            "name": "Valid input with 'user_input' field (backward compatibility)",
            "payload": {"user_input": "What's the weather like?"},
            "expected_status": "success"
        },
        {
            "name": "Empty input",
            "payload": {"input": ""},
            "expected_status": "error"
        },
        {
            "name": "Missing input field",
            "payload": {},
            "expected_status": "error"
        },
        {
            "name": "Invalid input type",
            "payload": {"input": None},
            "expected_status": "error"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"Payload: {json.dumps(test_case['payload'], indent=2)}")
        
        try:
            response = requests.post(f"{base_url}/agent", json=test_case['payload'])
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2)}")
                
                # Verify JSON structure
                if "status" not in result:
                    print("❌ ERROR: Missing 'status' field")
                elif "response" not in result:
                    print("❌ ERROR: Missing 'response' field")
                elif result["status"] == "error" and "error" not in result:
                    print("❌ ERROR: Error status but missing 'error' field")
                elif result["status"] == test_case["expected_status"]:
                    print(f"✅ PASS: Expected status '{test_case['expected_status']}' received")
                else:
                    print(f"❌ FAIL: Expected status '{test_case['expected_status']}' but got '{result['status']}'")
            else:
                print(f"❌ ERROR: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ ERROR: Could not connect to server. Make sure the backend is running on localhost:8000")
            break
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
        
        print("-" * 30)
        time.sleep(1)  # Small delay between requests
    
    print("\n🎯 Test Summary:")
    print("✅ Backend should return consistent JSON structure with 'status' and 'response' fields")
    print("✅ Error responses should include an 'error' field")
    print("✅ Both 'input' and 'user_input' fields should work for backward compatibility")

if __name__ == "__main__":
    test_agent_endpoint() 