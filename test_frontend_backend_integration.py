#!/usr/bin/env python3
"""
Frontend-Backend Integration Test
Tests the complete user journey from frontend to backend
"""

import requests
import json
import time
from typing import Dict, Any

def test_backend_health():
    """Test backend health endpoint"""
    print("🔍 Testing Backend Health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy: {data}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def test_frontend_access():
    """Test frontend accessibility"""
    print("\n🌐 Testing Frontend Access...")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend access failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend access error: {e}")
        return False

def test_travel_plan_generation():
    """Test travel plan generation API"""
    print("\n✈️ Testing Travel Plan Generation...")
    try:
        payload = {
            "destination": "Paris",
            "budget": 3000,
            "user_wallet": "0x1234567890abcdef"
        }
        
        response = requests.post(
            "http://localhost:8000/generate_plan",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                plan = data.get("plan", {})
                print(f"✅ Travel plan generated successfully!")
                print(f"   Destination: {plan.get('destination')}")
                print(f"   Total Cost: ${plan.get('grand_total')}")
                print(f"   Plan ID: {plan.get('plan_id')}")
                return True
            else:
                print(f"❌ Plan generation failed: {data.get('error')}")
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Plan generation error: {e}")
        return False

def test_plan_confirmation():
    """Test plan confirmation API"""
    print("\n✅ Testing Plan Confirmation...")
    try:
        # First generate a plan
        payload = {
            "destination": "Tokyo",
            "budget": 5000,
            "user_wallet": "0xabcdef1234567890"
        }
        
        response = requests.post(
            "http://localhost:8000/generate_plan",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        
        if response.status_code != 200:
            print("❌ Could not generate plan for confirmation test")
            return False
            
        data = response.json()
        if data.get("status") != "success":
            print("❌ Plan generation failed for confirmation test")
            return False
            
        plan_id = data["plan"]["plan_id"]
        
        # Now confirm the plan
        confirm_payload = {
            "plan_id": plan_id,
            "user_wallet": "0xabcdef1234567890"
        }
        
        confirm_response = requests.post(
            "http://localhost:8000/confirm_plan",
            headers={"Content-Type": "application/json"},
            json=confirm_payload,
            timeout=10
        )
        
        if confirm_response.status_code == 200:
            confirm_data = confirm_response.json()
            if confirm_data.get("status") == "success":
                print("✅ Plan confirmation successful!")
                return True
            else:
                print(f"❌ Plan confirmation failed: {confirm_data.get('error')}")
                return False
        else:
            print(f"❌ Confirmation API request failed: {confirm_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Plan confirmation error: {e}")
        return False

def test_cors_headers():
    """Test CORS headers for frontend-backend communication"""
    print("\n🌐 Testing CORS Headers...")
    try:
        # Test preflight request
        response = requests.options(
            "http://localhost:8000/generate_plan",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=5
        )
        
        if response.status_code in [200, 204]:
            cors_headers = response.headers
            print("✅ CORS preflight request successful")
            print(f"   Access-Control-Allow-Origin: {cors_headers.get('Access-Control-Allow-Origin', 'Not set')}")
            print(f"   Access-Control-Allow-Methods: {cors_headers.get('Access-Control-Allow-Methods', 'Not set')}")
            return True
        else:
            print(f"❌ CORS preflight failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ CORS test error: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Starting Frontend-Backend Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Frontend Access", test_frontend_access),
        ("Travel Plan Generation", test_travel_plan_generation),
        ("Plan Confirmation", test_plan_confirmation),
        ("CORS Headers", test_cors_headers),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Frontend-Backend integration is working perfectly!")
        print("\n📝 Next Steps:")
        print("1. Open http://localhost:3000 in your browser")
        print("2. Try generating a travel plan")
        print("3. Check browser Developer Tools → Network tab for API calls")
        print("4. Verify successful communication between frontend and backend")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure backend is running: uvicorn backend:app --reload --host 0.0.0.0 --port 8000")
        print("2. Ensure frontend is running: cd travel-frontend && npm run dev")
        print("3. Check that .env.local exists in travel-frontend with NEXT_PUBLIC_API_URL=http://localhost:8000")

if __name__ == "__main__":
    main() 