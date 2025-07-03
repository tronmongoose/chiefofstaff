#!/usr/bin/env python3
"""
Test script for the reputation dashboard frontend integration.
Tests the API endpoints and verifies the frontend components work correctly.
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"

def test_backend_health():
    """Test if the backend is running and healthy."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and healthy")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend is not accessible: {e}")
        return False

def test_frontend_health():
    """Test if the frontend is running."""
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running")
            return True
        else:
            print(f"❌ Frontend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend is not accessible: {e}")
        return False

def test_reputation_api_endpoints():
    """Test the reputation API endpoints."""
    test_wallet = "0x1234567890abcdef1234567890abcdef1234567890"
    
    endpoints = [
        f"/api/reputation/{test_wallet}",
        "/api/reputation/leaderboard?limit=5",
        "/api/reputation/levels"
    ]
    
    print("\n🔍 Testing Reputation API Endpoints:")
    
    for endpoint in endpoints:
        try:
            url = f"{FRONTEND_URL}{endpoint}"
            print(f"\nTesting: {endpoint}")
            
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: {data.get('status', 'unknown')}")
                if 'data' in data:
                    print(f"   Data keys: {list(data['data'].keys()) if isinstance(data['data'], dict) else 'N/A'}")
            else:
                print(f"❌ Failed: {response.text[:100]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")

def test_reputation_page():
    """Test if the reputation page loads correctly."""
    try:
        url = f"{FRONTEND_URL}/reputation"
        print(f"\n🔍 Testing Reputation Page: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            if "Reputation Dashboard" in content:
                print("✅ Reputation page loads correctly")
                return True
            else:
                print("❌ Reputation page content not found")
                return False
        else:
            print(f"❌ Reputation page failed to load: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_reputation_page_with_wallet():
    """Test reputation page with a specific wallet parameter."""
    test_wallet = "0x1234567890abcdef1234567890abcdef1234567890"
    try:
        url = f"{FRONTEND_URL}/reputation?wallet={test_wallet}"
        print(f"\n🔍 Testing Reputation Page with Wallet: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            if test_wallet[:6] in content or "Reputation Dashboard" in content:
                print("✅ Reputation page with wallet parameter loads correctly")
                return True
            else:
                print("❌ Reputation page with wallet parameter content not found")
                return False
        else:
            print(f"❌ Reputation page with wallet parameter failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_navigation():
    """Test if the reputation link is in the navigation."""
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            content = response.text
            if "Reputation" in content:
                print("✅ Reputation navigation link found")
                return True
            else:
                print("❌ Reputation navigation link not found")
                return False
        else:
            print(f"❌ Navigation test failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Reputation Dashboard Frontend Integration")
    print("=" * 60)
    
    # Test basic health
    backend_ok = test_backend_health()
    frontend_ok = test_frontend_health()
    
    if not backend_ok or not frontend_ok:
        print("\n❌ Basic health checks failed. Please ensure both services are running:")
        print("   Backend: python main.py")
        print("   Frontend: cd travel-frontend && npm run dev")
        return
    
    # Test API endpoints
    test_reputation_api_endpoints()
    
    # Test pages
    test_reputation_page()
    test_reputation_page_with_wallet()
    test_navigation()
    
    print("\n" + "=" * 60)
    print("🎉 Reputation Dashboard Frontend Integration Test Complete!")
    print("\n📋 Next Steps:")
    print("1. Visit http://localhost:3000/reputation to see the dashboard")
    print("2. Try different wallet addresses: ?wallet=0x...")
    print("3. Test the interactive components and navigation")
    print("4. Check the browser console for any JavaScript errors")

if __name__ == "__main__":
    main() 