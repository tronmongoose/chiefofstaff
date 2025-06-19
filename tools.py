import os
import requests
from langchain_core.tools import tool
from dotenv import load_dotenv
from amadeus import Client, ResponseError

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")

# Initialize Amadeus client
amadeus = None
if AMADEUS_API_KEY and AMADEUS_API_SECRET:
    amadeus = Client(
        client_id=AMADEUS_API_KEY,
        client_secret=AMADEUS_API_SECRET
    )

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

TOOLS = [get_weather, search_flights, get_airport_info, get_travel_recommendations, get_todo_list] 