from state import TravelAgentState

# --- Node Functions for Autonomous Travel Planner ---

def search_flights_node(state: TravelAgentState) -> TravelAgentState:
    """Search for flights to the destination within the budget."""
    # Example: Use your existing search_flights tool or a mock
    flights = [{
        "from": "JFK",
        "to": state.get('destination', 'Unknown'),
        "price": 500,
        "airline": "DemoAir",
        "dates": "2024-08-01 to 2024-08-10"
    }]
    return {**state, 'flights': flights}

def search_hotels_node(state: TravelAgentState) -> TravelAgentState:
    """Search for hotels in the destination within the budget."""
    hotels = [{
        "name": "Hotel Demo",
        "location": state.get('destination', 'Unknown'),
        "price_per_night": 150,
        "nights": 7,
        "total": 1050
    }]
    return {**state, 'hotels': hotels}

def get_activities_node(state: TravelAgentState) -> TravelAgentState:
    """Get recommended activities for the destination."""
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