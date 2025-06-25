#!/usr/bin/env python3
"""
Test script for Amadeus API tools
"""

from dotenv import load_dotenv
import os
from tools import search_flights, get_airport_info, get_travel_recommendations, get_weather, get_todo_list

# Load environment variables
load_dotenv()

def test_amadeus_credentials():
    """Test if Amadeus credentials are loaded"""
    api_key = os.getenv('AMADEUS_API_KEY')
    api_secret = os.getenv('AMADEUS_API_SECRET')
    
    print("🔑 Testing Amadeus Credentials:")
    print(f"   API Key: {'✓ Set' if api_key else '✗ Missing'}")
    print(f"   API Secret: {'✓ Set' if api_secret else '✗ Missing'}")
    print()

def test_flight_search():
    """Test flight search functionality"""
    print("✈️ Testing Flight Search:")
    try:
        result = search_flights.invoke({
            'origin': 'LAX', 
            'destination': 'JFK', 
            'departure_date': '2025-07-15'
        })
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    print()

def test_airport_info():
    """Test airport information functionality"""
    print("🏢 Testing Airport Information:")
    try:
        result = get_airport_info.invoke({'airport_code': 'LAX'})
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    print()

def test_travel_recommendations():
    """Test travel recommendations functionality"""
    print("🏛️ Testing Travel Recommendations:")
    try:
        result = get_travel_recommendations.invoke({'city': 'Paris'})
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    print()

def test_existing_tools():
    """Test existing tools (weather, todo)"""
    print("🌤️ Testing Weather Tool:")
    try:
        result = get_weather.invoke({'location': 'San Francisco'})
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    print("📝 Testing Todo List Tool:")
    try:
        result = get_todo_list.invoke({})
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    print()

if __name__ == "__main__":
    print("🧪 Testing Amadeus API Integration\n")
    
    test_amadeus_credentials()
    test_flight_search()
    test_airport_info()
    test_travel_recommendations()
    test_existing_tools()
    
    print("✅ Testing complete!") 