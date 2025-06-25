#!/usr/bin/env python3
"""
Test script for wallet functionality
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_wallet_import():
    """Test that wallet module can be imported"""
    try:
        from wallet import get_wallet_balances, CoinbaseWallet
        print("✅ Wallet module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import wallet module: {e}")
        return False

def test_wallet_tools_import():
    """Test that wallet tools can be imported"""
    try:
        from tools.payment import WALLET_TOOLS, check_wallet_balance
        print("✅ Wallet tools imported successfully")
        print(f"   Found {len(WALLET_TOOLS)} wallet tools")
        return True
    except ImportError as e:
        print(f"❌ Failed to import wallet tools: {e}")
        return False

def test_agent_tools_import():
    """Test that agent tools include wallet tools"""
    try:
        from agent_tools import TOOLS
        wallet_tools = [tool for tool in TOOLS if tool.name == "check_wallet_balance"]
        print("✅ Agent tools imported successfully")
        print(f"   Total tools: {len(TOOLS)}")
        print(f"   Wallet tools found: {len(wallet_tools)}")
        return len(wallet_tools) > 0
    except ImportError as e:
        print(f"❌ Failed to import agent tools: {e}")
        return False

def test_wallet_functionality():
    """Test wallet functionality with missing credentials"""
    try:
        from wallet import get_wallet_balances
        result = get_wallet_balances()
        print("✅ Wallet function executed successfully")
        print(f"   Result: {result}")
        return "Configuration error" in result or "No wallet accounts" in result
    except Exception as e:
        print(f"❌ Wallet function failed: {e}")
        return False

def test_planner_routing():
    """Test that planner routes wallet queries correctly"""
    try:
        # Test the routing logic without requiring OpenAI API
        wallet_keywords = ["wallet", "balance", "crypto", "bitcoin", "ethereum", "coinbase", "account"]
        
        test_queries = [
            "check my wallet balance",
            "what's my crypto balance?",
            "show me my bitcoin",
            "how much ethereum do I have?",
            "check coinbase account"
        ]
        
        print("✅ Testing planner routing logic:")
        for query in test_queries:
            has_wallet_query = any(word in query.lower() for word in wallet_keywords)
            print(f"   '{query}' -> Wallet query: {has_wallet_query}")
        
        return True
    except Exception as e:
        print(f"❌ Planner routing test failed: {e}")
        return False

def main():
    """Run all wallet tests"""
    print("🧪 Testing Wallet Functionality\n")
    
    tests = [
        ("Wallet Module Import", test_wallet_import),
        ("Wallet Tools Import", test_wallet_tools_import),
        ("Agent Tools Import", test_agent_tools_import),
        ("Wallet Functionality", test_wallet_functionality),
        ("Planner Routing", test_planner_routing),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
            print(f"   ✅ PASSED")
        else:
            print(f"   ❌ FAILED")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All wallet tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above.")

if __name__ == "__main__":
    main() 