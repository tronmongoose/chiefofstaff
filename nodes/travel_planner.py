from state import TravelAgentState
from agent_tools import search_flights_direct, search_hotels_direct, search_activities_direct, parse_flight_results, parse_hotel_results, parse_activity_results

# --- Node Functions for Autonomous Travel Planner ---

def search_flights_node(state: TravelAgentState) -> TravelAgentState:
    """Search for flights to the destination within the budget."""
    try:
        # Get destination from state
        destination = state.get('destination', 'Paris')
        departure_date = state.get('departure_date', '2024-08-01')
        
        # Convert destination to airport code (simplified)
        airport_codes = {
            'paris': 'CDG',
            'london': 'LHR', 
            'new york': 'JFK',
            'tokyo': 'NRT',
            'rome': 'FCO'
        }
        dest_airport = airport_codes.get(destination.lower(), 'CDG')
        
        # Use real Amadeus API with direct function
        flight_response = search_flights_direct("JFK", dest_airport, departure_date)
        
        # Check if API credentials are not configured
        if "Amadeus API credentials not configured" in flight_response:
            print("⚠️  Amadeus API credentials not configured. Using demo data.")
            # Use realistic demo data based on destination
            demo_airlines = {
                'paris': ['Air France', 'Delta Airlines', 'United Airlines'],
                'london': ['British Airways', 'American Airlines', 'Virgin Atlantic'],
                'new york': ['American Airlines', 'Delta Airlines', 'United Airlines'],
                'tokyo': ['Japan Airlines', 'ANA', 'United Airlines'],
                'rome': ['Alitalia', 'American Airlines', 'Delta Airlines']
            }
            airlines = demo_airlines.get(destination.lower(), ['DemoAir'])
            
            flights = [{
                "from": "JFK",
                "to": destination,
                "price": 450 + (hash(destination) % 200),  # Varied pricing
                "airline": airlines[0],
                "dates": f"{departure_date} to 2024-08-10"
            }]
        else:
            # Parse the real API response
            flights = parse_flight_results(flight_response)
            
            # Update destination and dates in flight data
            for flight in flights:
                flight['to'] = destination
                flight['dates'] = f"{departure_date} to 2024-08-10"
        
        return {**state, 'flights': flights}
    except Exception as e:
        print(f"Error in search_flights_node: {e}")
        # Fallback to demo data
        flights = [{
            "from": "JFK",
            "to": state.get('destination', 'Paris'),
            "price": 500,
            "airline": "DemoAir",
            "dates": "2024-08-01 to 2024-08-10"
        }]
        return {**state, 'flights': flights}

def search_hotels_node(state: TravelAgentState) -> TravelAgentState:
    """Search for hotels in the destination within the budget."""
    try:
        # Get destination and dates from state
        destination = state.get('destination', 'Paris')
        check_in_date = state.get('departure_date', '2024-08-01')
        check_out_date = '2024-08-08'  # 7 nights later
        
        # Use real Amadeus API with direct function
        hotel_response = search_hotels_direct(destination, check_in_date, check_out_date)
        
        # Check if API credentials are not configured
        if "Amadeus API credentials not configured" in hotel_response:
            print("⚠️  Amadeus API credentials not configured. Using demo data.")
            # Use realistic demo data based on destination
            demo_hotels = {
                'paris': ['Hotel Ritz Paris', 'Le Meurice', 'Four Seasons Hotel George V'],
                'london': ['The Ritz London', 'Claridge\'s', 'The Savoy'],
                'new york': ['The Plaza Hotel', 'Waldorf Astoria', 'The St. Regis'],
                'tokyo': ['The Peninsula Tokyo', 'Park Hyatt Tokyo', 'Aman Tokyo'],
                'rome': ['Hotel de Russie', 'The Hassler Roma', 'Hotel Eden']
            }
            hotels_list = demo_hotels.get(destination.lower(), ['Hotel Demo'])
            
            hotels = [{
                "name": hotels_list[0],
                "location": destination,
                "price_per_night": 120 + (hash(destination) % 80),  # Varied pricing
                "nights": 7,
                "total": (120 + (hash(destination) % 80)) * 7
            }]
        else:
            # Parse the real API response
            hotels = parse_hotel_results(hotel_response)
            
            # Update location in hotel data
            for hotel in hotels:
                hotel['location'] = destination
        
        return {**state, 'hotels': hotels}
    except Exception as e:
        print(f"Error in search_hotels_node: {e}")
        # Fallback to demo data
        hotels = [{
            "name": "Hotel Demo",
            "location": state.get('destination', 'Paris'),
            "price_per_night": 150,
            "nights": 7,
            "total": 1050
        }]
        return {**state, 'hotels': hotels}

def get_activities_node(state: TravelAgentState) -> TravelAgentState:
    """Get recommended activities for the destination."""
    try:
        # Get destination from state
        destination = state.get('destination', 'Paris')
        
        # Use real Amadeus API with direct function
        activity_response = search_activities_direct(destination)
        
        # Check if API credentials are not configured
        if "Amadeus API credentials not configured" in activity_response:
            print("⚠️  Amadeus API credentials not configured. Using demo data.")
            # Use realistic demo data based on destination
            demo_activities = {
                'paris': [
                    "Eiffel Tower visit",
                    "Louvre Museum tour", 
                    "Seine River cruise",
                    "Notre-Dame Cathedral",
                    "Champs-Élysées walk"
                ],
                'london': [
                    "Big Ben and Westminster",
                    "Buckingham Palace tour",
                    "Tower of London visit",
                    "British Museum exploration",
                    "London Eye ride"
                ],
                'new york': [
                    "Statue of Liberty visit",
                    "Times Square exploration",
                    "Central Park walk",
                    "Empire State Building",
                    "Broadway show"
                ],
                'tokyo': [
                    "Tokyo Tower visit",
                    "Senso-ji Temple",
                    "Shibuya Crossing",
                    "Tokyo Skytree",
                    "Tsukiji Fish Market"
                ],
                'rome': [
                    "Colosseum tour",
                    "Vatican City visit",
                    "Trevi Fountain",
                    "Roman Forum",
                    "Pantheon exploration"
                ]
            }
            activities = demo_activities.get(destination.lower(), [
                "Eiffel Tower visit",
                "Louvre Museum tour", 
                "Seine River cruise"
            ])
        else:
            # Parse the real API response
            activities = parse_activity_results(activity_response)
        
        return {**state, 'activities': activities}
    except Exception as e:
        print(f"Error in get_activities_node: {e}")
        # Fallback to demo data
        activities = [
            "Eiffel Tower visit",
            "Louvre Museum tour",
            "Seine River cruise"
        ]
        return {**state, 'activities': activities}

def assemble_plan_node(state: TravelAgentState) -> TravelAgentState:
    """Combine flights, hotels, and activities into a plan. Estimate total cost and platform fee."""
    flights = state.get('flights', [])
    hotels = state.get('hotels', [])
    activities = state.get('activities', [])
    
    flight_cost = flights[0]['price'] if flights else 0
    hotel_cost = hotels[0]['total'] if hotels else 0
    activities_cost = 200  # Example: flat cost for activities
    total_cost = flight_cost + hotel_cost + activities_cost
    platform_fee = round(total_cost * 0.02, 2)
    
    plan = {
        "flights": flights,
        "hotels": hotels,
        "activities": activities,
        "total_cost": total_cost,
        "platform_fee": platform_fee
    }
    
    return {
        **state,
        'plan': plan,
        'total_estimated_cost': total_cost,
        'platform_fee': platform_fee
    }

def budget_branch_node(state: TravelAgentState) -> TravelAgentState:
    """Check if the plan is within budget. Suggest alternatives if needed."""
    total_cost = state.get('total_estimated_cost', 0)
    platform_fee = state.get('platform_fee', 0)
    budget = state.get('budget', 0)
    
    if total_cost + platform_fee > budget:
        return {**state, 'error': "Plan exceeds budget. Please increase your budget or try a different destination."}
    return state

def wait_for_confirmation_node(state: TravelAgentState) -> TravelAgentState:
    """Pause and wait for user confirmation. Persist session if needed."""
    # In a real app, persist state/session here and wait for user input
    # For now, just pass through
    return state

def process_payment_node(state: TravelAgentState) -> TravelAgentState:
    """Process payment using Coinbase x402. Handle payment errors."""
    # Example: Simulate payment success
    return {**state, 'payment_status': "success"}

def confirm_bookings_node(state: TravelAgentState) -> TravelAgentState:
    """Confirm bookings for flights, hotels, and activities. Track each confirmation."""
    booking_status = {
        "flights": "confirmed",
        "hotels": "confirmed",
        "activities": "confirmed"
    }
    return {**state, 'booking_status': booking_status}

def store_platform_fee_node(state: TravelAgentState) -> TravelAgentState:
    """Store/log the platform fee for reporting and analytics."""
    platform_fee = state.get('platform_fee', 0)
    user_wallet = state.get('user_wallet', 'unknown')
    print(f"Platform fee logged: {platform_fee} for user {user_wallet}")
    return state

def error_handler_node(state: TravelAgentState) -> TravelAgentState:
    """Handle errors, offer retry options, and provide user-friendly messages."""
    error = state.get('error', 'Unknown error occurred')
    print(f"Error encountered: {error}")
    return state 