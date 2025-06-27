#!/usr/bin/env python3
"""
Test script for the new Travel Planning API endpoints.
Run this script to verify all endpoints are working correctly.
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_generate_plan() -> Dict[str, Any]:
    """Test the generate_plan endpoint."""
    print("🧪 Testing /generate_plan endpoint...")
    
    payload = {
        "destination": "Tokyo",
        "budget": 3000.0,
        "user_wallet": "0xabcdef1234567890",
        "session_id": "test-session-123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate_plan", json=payload)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Status: {data['status']}")
        if data['status'] == 'success':
            plan = data['plan']
            print(f"   📍 Destination: {plan['destination']}")
            print(f"   💰 Total Cost: ${plan['grand_total']:.2f}")
            print(f"   🆔 Plan ID: {plan['plan_id']}")
            print(f"   ✈️ Flights: {len(plan['flights'])}")
            print(f"   🏨 Hotels: {len(plan['hotels'])}")
            print(f"   🎯 Activities: {len(plan['activities'])}")
            return data
        else:
            print(f"❌ Error: {data.get('error', 'Unknown error')}")
            return data
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return {"status": "error", "error": str(e)}

def test_confirm_plan(plan_id: str) -> Dict[str, Any]:
    """Test the confirm_plan endpoint."""
    print(f"\n🧪 Testing /confirm_plan endpoint with plan_id: {plan_id}...")
    
    payload = {
        "plan_id": plan_id,
        "user_wallet": "0xabcdef1234567890",
        "payment_method": "cdp",
        "session_id": "test-session-123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/confirm_plan", json=payload)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Status: {data['status']}")
        if data['status'] == 'success':
            print(f"   💳 Payment Status: {data['payment_status']}")
            if data.get('booking_status'):
                booking = data['booking_status']
                print(f"   ✈️ Flights: {booking['flights']}")
                print(f"   🏨 Hotels: {booking['hotels']}")
                print(f"   🎯 Activities: {booking['activities']}")
            print(f"   📝 Confirmation: {data['confirmation_message'][:100]}...")
            return data
        else:
            print(f"❌ Error: {data.get('error', 'Unknown error')}")
            return data
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return {"status": "error", "error": str(e)}

def test_get_user_plans(user_wallet: str) -> Dict[str, Any]:
    """Test the get_user_plans endpoint."""
    print(f"\n🧪 Testing /get_user_plans/{user_wallet} endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/get_user_plans/{user_wallet}")
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Status: {data['status']}")
        if data['status'] == 'success':
            plans = data['plans']
            print(f"   📋 Found {len(plans)} plans")
            for i, plan in enumerate(plans, 1):
                print(f"   Plan {i}:")
                print(f"     🆔 ID: {plan['plan_id']}")
                print(f"     📍 Destination: {plan['destination']}")
                print(f"     💰 Cost: ${plan['total_cost']:.2f}")
                print(f"     📅 Created: {plan['created_at']}")
                print(f"     ✅ Status: {plan['status']}")
            return data
        else:
            print(f"❌ Error: {data.get('error', 'Unknown error')}")
            return data
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return {"status": "error", "error": str(e)}

def test_error_cases():
    """Test error cases for the API endpoints."""
    print("\n🧪 Testing error cases...")
    
    # Test invalid plan ID
    print("   Testing invalid plan ID...")
    try:
        response = requests.post(f"{BASE_URL}/confirm_plan", json={
            "plan_id": "invalid-plan-id",
            "user_wallet": "0xabcdef1234567890"
        })
        data = response.json()
        if data['status'] == 'error':
            print("   ✅ Correctly handled invalid plan ID")
        else:
            print("   ❌ Should have returned error for invalid plan ID")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test missing required fields
    print("   Testing missing required fields...")
    try:
        response = requests.post(f"{BASE_URL}/generate_plan", json={
            "destination": "Paris"
            # Missing budget
        })
        data = response.json()
        if 'error' in data or response.status_code == 422:
            print("   ✅ Correctly handled missing required fields")
        else:
            print("   ❌ Should have returned error for missing fields")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")

def main():
    """Run all API tests."""
    print("🚀 Starting Travel Planning API Tests")
    print("=" * 50)
    
    # Test 1: Generate a plan
    result1 = test_generate_plan()
    
    if result1.get('status') == 'success' and result1.get('plan'):
        plan_id = result1['plan']['plan_id']
        user_wallet = "0xabcdef1234567890"
        
        # Test 2: Confirm the plan
        result2 = test_confirm_plan(plan_id)
        
        # Test 3: Get user plans
        result3 = test_get_user_plans(user_wallet)
        
        # Test 4: Error cases
        test_error_cases()
        
        print("\n" + "=" * 50)
        print("📊 Test Summary:")
        print(f"   ✅ Generate Plan: {'PASS' if result1['status'] == 'success' else 'FAIL'}")
        print(f"   ✅ Confirm Plan: {'PASS' if result2['status'] == 'success' else 'FAIL'}")
        print(f"   ✅ Get User Plans: {'PASS' if result3['status'] == 'success' else 'FAIL'}")
        
        if all(r['status'] == 'success' for r in [result1, result2, result3]):
            print("\n🎉 All tests passed! The API is working correctly.")
        else:
            print("\n❌ Some tests failed. Check the output above for details.")
    else:
        print("\n❌ Cannot proceed with other tests - plan generation failed.")
        print("Make sure the backend is running on http://localhost:8000")

if __name__ == "__main__":
    main() 