#!/usr/bin/env python3
"""
Comprehensive endpoint testing script
Tests all FastAPI endpoints for consistent JSON structure and functionality
"""

import requests
import json
import time

def test_health_endpoint():
    """Test the health check endpoint"""
    print("🏥 Testing Health Endpoint")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Verify JSON structure
            if "status" in result and "response" in result:
                if result["status"] == "success":
                    print("✅ Health endpoint working correctly")
                    return True
                else:
                    print("❌ Health endpoint returned error status")
                    return False
            else:
                print("❌ Health endpoint missing required fields")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def test_wallet_balance_endpoint():
    """Test the wallet balance endpoint"""
    print("\n💰 Testing Wallet Balance Endpoint")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8000/wallet-balance")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Verify JSON structure
            if "status" in result and "response" in result:
                if result["status"] == "success":
                    print("✅ Wallet balance endpoint working correctly")
                    return True
                else:
                    print("❌ Wallet balance endpoint returned error status")
                    if "error" in result:
                        print(f"Error details: {result['error']}")
                    return False
            else:
                print("❌ Wallet balance endpoint missing required fields")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Wallet balance endpoint test failed: {e}")
        return False

def test_agent_endpoint():
    """Test the agent endpoint with various inputs"""
    print("\n🤖 Testing Agent Endpoint")
    print("=" * 40)
    
    test_cases = [
        {
            "name": "Simple greeting",
            "input": "Hello",
            "expected_status": "success"
        },
        {
            "name": "Weather query",
            "input": "What is the weather in Tokyo?",
            "expected_status": "success"
        },
        {
            "name": "Wallet balance query",
            "input": "What is my wallet balance?",
            "expected_status": "success"
        },
        {
            "name": "Trip planning",
            "input": "Plan a trip to Paris",
            "expected_status": "success"
        },
        {
            "name": "IPFS upload",
            "input": "log to IPFS: Test upload",
            "expected_status": "success"
        },
        {
            "name": "Empty input",
            "input": "",
            "expected_status": "error"
        }
    ]
    
    successful_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"Input: '{test_case['input']}'")
        
        try:
            payload = {"input": test_case['input']}
            response = requests.post("http://localhost:8000/agent", json=payload)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2)}")
                
                # Verify JSON structure
                if "status" in result and "response" in result:
                    if result["status"] == test_case["expected_status"]:
                        print(f"✅ Test {i} passed")
                        successful_tests += 1
                    else:
                        print(f"❌ Test {i} failed - expected {test_case['expected_status']}, got {result['status']}")
                    
                    # Check for error details if it's an error
                    if result["status"] == "error" and "error" in result:
                        print(f"Error details: {result['error']}")
                else:
                    print(f"❌ Test {i} failed - missing required fields")
            else:
                print(f"❌ Test {i} failed - HTTP Error: {response.status_code}")
        except Exception as e:
            print(f"❌ Test {i} failed - Exception: {e}")
        
        time.sleep(1)  # Small delay between requests
    
    print(f"\n📊 Agent Endpoint Results:")
    print(f"✅ Successful: {successful_tests}/{total_tests}")
    print(f"📈 Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    return successful_tests == total_tests

def test_ipfs_upload_endpoint():
    """Test the IPFS upload endpoint"""
    print("\n📝 Testing IPFS Upload Endpoint")
    print("=" * 40)
    
    test_cases = [
        {
            "name": "Valid content",
            "content": "Test content for IPFS upload",
            "expected_status": "success"
        },
        {
            "name": "Empty content",
            "content": "",
            "expected_status": "error"
        }
    ]
    
    successful_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"Content: '{test_case['content']}'")
        
        try:
            payload = {"content": test_case['content']}
            response = requests.post("http://localhost:8000/ipfs-upload", json=payload)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2)}")
                
                # Verify JSON structure
                if "status" in result and "response" in result:
                    if result["status"] == test_case["expected_status"]:
                        print(f"✅ Test {i} passed")
                        successful_tests += 1
                    else:
                        print(f"❌ Test {i} failed - expected {test_case['expected_status']}, got {result['status']}")
                    
                    # Check for error details if it's an error
                    if result["status"] == "error" and "error" in result:
                        print(f"Error details: {result['error']}")
                else:
                    print(f"❌ Test {i} failed - missing required fields")
            else:
                print(f"❌ Test {i} failed - HTTP Error: {response.status_code}")
        except Exception as e:
            print(f"❌ Test {i} failed - Exception: {e}")
        
        time.sleep(1)  # Small delay between requests
    
    print(f"\n📊 IPFS Upload Endpoint Results:")
    print(f"✅ Successful: {successful_tests}/{total_tests}")
    print(f"📈 Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    return successful_tests == total_tests

def test_error_handling():
    """Test error handling for malformed requests"""
    print("\n🔧 Testing Error Handling")
    print("=" * 40)
    
    # Test malformed JSON
    try:
        response = requests.post("http://localhost:8000/agent", data="invalid json")
        print(f"Malformed JSON test - Status Code: {response.status_code}")
        if response.status_code == 422:  # Unprocessable Entity
            print("✅ Properly handles malformed JSON")
        else:
            print("❌ Unexpected response for malformed JSON")
    except Exception as e:
        print(f"❌ Malformed JSON test failed: {e}")
    
    # Test missing fields
    try:
        payload = {}  # Missing input field
        response = requests.post("http://localhost:8000/agent", json=payload)
        print(f"Missing fields test - Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "error":
                print("✅ Properly handles missing fields")
            else:
                print("❌ Unexpected response for missing fields")
        else:
            print("❌ Unexpected status code for missing fields")
    except Exception as e:
        print(f"❌ Missing fields test failed: {e}")

def main():
    """Run all endpoint tests"""
    print("🧪 Comprehensive Endpoint Testing")
    print("=" * 60)
    
    # Test all endpoints
    health_ok = test_health_endpoint()
    wallet_ok = test_wallet_balance_endpoint()
    agent_ok = test_agent_endpoint()
    ipfs_ok = test_ipfs_upload_endpoint()
    
    # Test error handling
    test_error_handling()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 Endpoint Testing Summary:")
    print(f"🏥 Health Endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"💰 Wallet Balance: {'✅ PASS' if wallet_ok else '❌ FAIL'}")
    print(f"🤖 Agent Endpoint: {'✅ PASS' if agent_ok else '❌ FAIL'}")
    print(f"📝 IPFS Upload: {'✅ PASS' if ipfs_ok else '❌ FAIL'}")
    
    all_passed = health_ok and wallet_ok and agent_ok and ipfs_ok
    print(f"\n🚀 Overall Status: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 All endpoints are working correctly with consistent JSON structure!")
    else:
        print("\n⚠️  Some endpoints need attention. Check the logs above.")

if __name__ == "__main__":
    main() 