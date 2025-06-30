import os
import requests
import json
import uuid
import re
from datetime import datetime, timedelta
from langchain_core.tools import tool
from dotenv import load_dotenv
from amadeus import Client, ResponseError
from tools.payment import WALLET_TOOLS
from tools.ipfs import retrieve_referrals_by_wallet
from typing import Dict, Any, Optional
from database import get_db
from db_service import create_booking, get_booking_by_id, update_booking_status, update_booking_payment_status

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")

# Initialize Amadeus client
amadeus = None
if AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET:
    try:
        amadeus = Client(
            client_id=AMADEUS_CLIENT_ID,
            client_secret=AMADEUS_CLIENT_SECRET
        )
    except Exception as e:
        print(f"Failed to initialize Amadeus client: {e}")

@tool
def get_weather(location: str) -> str:
    """
    Use this tool for any weather, forecast, temperature, or climate request.
    """
    if not OPENWEATHER_API_KEY:
        return "Weather API key not set."

    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=imperial"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Failed to get weather for {location}."

    data = response.json()
    temp = data['main']['temp']
    description = data['weather'][0]['description']
    return f"The weather in {location} is {temp}°F with {description}."

@tool
def search_flights(origin: str, destination: str, departure_date: str) -> str:
    """
    Search for flights between two airports on a specific date.
    Use IATA airport codes (e.g., 'LAX', 'JFK', 'LHR').
    Date format should be YYYY-MM-DD.
    """
    if not amadeus:
        return "Amadeus API credentials not configured."
    
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            adults=1
        )
        
        if not response.data:
            return f"No flights found from {origin} to {destination} on {departure_date}."
        
        flights = []
        for i, flight in enumerate(response.data[:5]):  # Limit to 5 results
            try:
                # Handle different pricing structures
                if 'pricing_options' in flight and flight['pricing_options']:
                    price = flight['pricing_options'][0]['price']['total']
                elif 'price' in flight:
                    price = flight['price']['total']
                else:
                    price = "Price not available"
                
                # Handle different airline structures
                if 'validatingAirlineCodes' in flight and flight['validatingAirlineCodes']:
                    airline = flight['validatingAirlineCodes'][0]
                elif 'airlines' in flight and flight['airlines']:
                    airline = flight['airlines'][0]
                else:
                    airline = "Airline not specified"
                
                flights.append(f"{i+1}. {airline} - ${price}")
            except (KeyError, IndexError) as e:
                # If we can't parse this flight, skip it
                continue
        
        if not flights:
            return f"Found flights from {origin} to {destination} on {departure_date}, but couldn't parse pricing information."
        
        return f"Found {len(response.data)} flights from {origin} to {destination} on {departure_date}:\n" + "\n".join(flights)
    
    except ResponseError as error:
        return f"Error searching flights: {error}"
    except Exception as e:
        return f"Unexpected error searching flights: {str(e)}"

@tool
def get_airport_info(airport_code: str) -> str:
    """
    Get information about an airport using its IATA code.
    """
    if not amadeus:
        return "Amadeus API credentials not configured."
    
    try:
        response = amadeus.reference_data.locations.get(
            keyword=airport_code,
            subType="AIRPORT"
        )
        
        if not response.data:
            return f"No airport found with code {airport_code}."
        
        airport = response.data[0]
        return f"Airport: {airport['name']} ({airport['iataCode']})\nLocation: {airport['address']['cityName']}, {airport['address']['countryName']}"
    
    except ResponseError as error:
        return f"Error getting airport info: {error}"

@tool
def get_travel_recommendations(city: str) -> str:
    """
    Get travel recommendations and points of interest for a city.
    Note: This tool provides general travel information for popular cities.
    """
    if not amadeus:
        return "Amadeus API credentials not configured."
    
    # For now, provide general travel information since the activities API requires coordinates
    popular_cities = {
        "paris": "Popular attractions in Paris: Eiffel Tower, Louvre Museum, Notre-Dame Cathedral, Champs-Élysées, Arc de Triomphe, Seine River Cruise, Palace of Versailles",
        "london": "Popular attractions in London: Big Ben, Buckingham Palace, Tower of London, British Museum, Westminster Abbey, London Eye, Tower Bridge",
        "new york": "Popular attractions in New York: Statue of Liberty, Times Square, Central Park, Empire State Building, Broadway, Metropolitan Museum of Art, Brooklyn Bridge",
        "tokyo": "Popular attractions in Tokyo: Tokyo Tower, Senso-ji Temple, Shibuya Crossing, Tokyo Skytree, Imperial Palace, Meiji Shrine, Tsukiji Fish Market",
        "rome": "Popular attractions in Rome: Colosseum, Vatican City, Trevi Fountain, Pantheon, Roman Forum, Sistine Chapel, Spanish Steps"
    }
    
    city_lower = city.lower()
    if city_lower in popular_cities:
        return f"Travel recommendations for {city}:\n{popular_cities[city_lower]}"
    else:
        return f"Travel recommendations for {city}: This is a great city to explore! Consider visiting local museums, restaurants, and cultural sites. For specific activities, you may want to check local tourism websites or travel guides."

@tool
def get_todo_list() -> str:
    """Returns Erik's current todo list."""
    return "Erik's todo list:\n1) Build agent\n2) Test LangGraph\n3) Deploy system"

@tool
def retrieve_referrals_by_wallet_tool(wallet_address: str) -> str:
    """
    Retrieve referral records from IPFS by wallet address.
    Args:
        wallet_address (str): The wallet address to search for (referrer or referee).
    Returns:
        str: JSON string of matching referral records.
    """
    try:
        records = retrieve_referrals_by_wallet(wallet_address)
        return str(records)
    except Exception as e:
        return f"Error retrieving referrals: {str(e)}"

@tool
def book_flight(flight_id: str, passenger_name: str, passenger_email: str, payment_method: str = "crypto", plan_id: str = None) -> str:
    """
    Book a specific flight with cryptocurrency payment.

    Args:
        flight_id: The flight offer ID from search results
        passenger_name: Full name of the passenger
        passenger_email: Email address for booking confirmation
        payment_method: Payment method ("crypto" for x402, "card" for traditional)
        plan_id: Optional plan ID to associate with this booking

    Returns:
        str: Booking confirmation details including payment requirements
    """
    if not amadeus:
        return "Amadeus API credentials not configured."
    
    try:
        # Get database session
        db = next(get_db())
        
        # Create booking in database
        booking = create_booking(
            db=db,
            flight_id=flight_id,
            passenger_name=passenger_name,
            passenger_email=passenger_email,
            payment_method=payment_method,
            payment_amount=0.10,  # 10 cents in USDC for booking fee
            plan_id=plan_id
        )
        
        if payment_method == "crypto":
            return json.dumps({
                "status": "success",
                "booking_id": booking.booking_id,
                "message": f"Booking created for {passenger_name}. Please complete payment of 0.10 USDC to confirm.",
                "payment_required": True,
                "payment_amount": "0.10",
                "payment_currency": "USDC",
                "next_step": "Complete payment via x402 to confirm booking"
            })
        else:
            return json.dumps({
                "status": "success",
                "booking_id": booking.booking_id,
                "message": f"Booking created for {passenger_name}. Traditional payment processing not yet implemented.",
                "payment_required": True,
                "next_step": "Contact support for traditional payment options"
            })
    
    except Exception as e:
        return f"Error creating flight booking: {str(e)}"

@tool
def get_booking_status(booking_id: str) -> str:
    """
    Check the status of a travel booking.

    Args:
        booking_id: The booking reference ID

    Returns:
        str: Current booking status and details
    """
    try:
        # Get database session
        db = next(get_db())
        
        # Get booking from database
        booking = get_booking_by_id(db, booking_id)
        
        if booking:
            return json.dumps({
                "booking_id": booking.booking_id,
                "status": booking.status,
                "payment_status": booking.payment_status,
                "passenger_name": booking.passenger_name,
                "passenger_email": booking.passenger_email,
                "payment_amount": booking.payment_amount,
                "payment_currency": booking.payment_currency,
                "created_at": booking.created_at.isoformat() if booking.created_at else None,
                "message": "Your booking details retrieved successfully."
            })
        else:
            return json.dumps({
                "error": "Booking not found",
                "message": "Please provide a valid booking reference starting with TRV-"
            })
    
    except Exception as e:
        return f"Error checking booking status: {str(e)}"

@tool
def confirm_booking_payment(booking_id: str, payment_transaction_hash: str = None) -> str:
    """
    Confirm payment for a booking and update its status.

    Args:
        booking_id: The booking reference ID
        payment_transaction_hash: Optional transaction hash for crypto payments

    Returns:
        str: Confirmation status and updated booking details
    """
    try:
        # Get database session
        db = next(get_db())
        
        # Update booking status
        booking = update_booking_status(
            db=db,
            booking_id=booking_id,
            status="confirmed",
            payment_status="completed"
        )
        
        if booking:
            return json.dumps({
                "status": "success",
                "booking_id": booking.booking_id,
                "message": "Payment confirmed! Your booking is now active.",
                "booking_status": "confirmed",
                "payment_status": "completed",
                "transaction_hash": payment_transaction_hash
            })
        else:
            return json.dumps({
                "error": "Booking not found",
                "message": "Please provide a valid booking reference"
            })
    
    except Exception as e:
        return f"Error confirming booking payment: {str(e)}"

@tool
def calculate_travel_cost(flights: str, hotels: str = None, activities: str = None) -> str:
    """
    Calculate total travel cost including x402 payment fees.

    Args:
        flights: Flight pricing information
        hotels: Hotel pricing (optional)
        activities: Activity pricing (optional)

    Returns:
        str: Detailed cost breakdown including crypto payment fees
    """
    try:
        total_cost = 0.0
        cost_breakdown = {
            "flights": 0.0,
            "hotels": 0.0,
            "activities": 0.0,
            "booking_fees": {
                "flight_search": 0.01,
                "flight_booking": 0.10,
                "hotel_search": 0.01,
                "hotel_booking": 0.10,
                "activity_search": 0.005,
                "activity_booking": 0.05
            },
            "total_fees": 0.0,
            "grand_total": 0.0
        }

        # Parse flight costs
        if flights and "$" in flights:
            flight_prices = re.findall(r'\$([0-9,]+\.?[0-9]*)', flights)
            if flight_prices:
                cost_breakdown["flights"] = float(flight_prices[0].replace(',', ''))
                total_cost += cost_breakdown["flights"]
                cost_breakdown["total_fees"] += 0.11  # Search + booking

        # Add hotel costs if provided
        if hotels and "$" in hotels:
            hotel_prices = re.findall(r'\$([0-9,]+\.?[0-9]*)', hotels)
            if hotel_prices:
                cost_breakdown["hotels"] = float(hotel_prices[0].replace(',', ''))
                total_cost += cost_breakdown["hotels"]
                cost_breakdown["total_fees"] += 0.11  # Search + booking

        # Add activity costs if provided
        if activities and "$" in activities:
            activity_prices = re.findall(r'\$([0-9,]+\.?[0-9]*)', activities)
            if activity_prices:
                cost_breakdown["activities"] = float(activity_prices[0].replace(',', ''))
                total_cost += cost_breakdown["activities"]
                cost_breakdown["total_fees"] += 0.055  # Search + booking

        cost_breakdown["grand_total"] = total_cost + cost_breakdown["total_fees"]

        return json.dumps({
            "status": "success",
            "breakdown": cost_breakdown,
            "summary": f"Total travel cost: ${total_cost:.2f} + ${cost_breakdown['total_fees']:.3f} USDC in booking fees = ${cost_breakdown['grand_total']:.2f} total",
            "payment_note": "Booking fees are paid in USDC via x402 standard for instant, secure transactions"
        })

    except Exception as e:
        return f"Error calculating travel costs: {str(e)}"

TOOLS = [
    get_weather,
    search_flights,
    book_flight,
    get_booking_status,
    confirm_booking_payment,
    calculate_travel_cost,
    get_airport_info,
    get_travel_recommendations,
    get_todo_list,
    retrieve_referrals_by_wallet_tool
] + WALLET_TOOLS 