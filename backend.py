from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
from wallet import get_wallet_balances_async
from agent_tools import TOOLS, book_flight, get_booking_status, confirm_booking_payment, calculate_travel_cost
from main import app as langgraph_app
import openai
import os
from nodes.planner import plan_tasks
from tools.ipfs import retrieve_referrals_by_wallet
from travel_graph import travel_app
import uuid
from datetime import datetime
import json
from sqlalchemy.orm import Session
from database import get_db, init_db
from db_service import PlanService
from x402_middleware import X402Middleware, TravelBookingPaymentService, setup_x402_payments

app = FastAPI(title="AI Agent Wallet API", version="1.0.0")

# Global variables
travel_agent = None
x402_payment_service = None

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    global travel_agent, x402_payment_service
    
    # Initialize database
    init_db()
    
    # Initialize travel agent
    try:
        travel_agent = travel_app
        print("✅ Travel agent initialized successfully")
    except Exception as e:
        print(f"⚠️ Travel agent initialization failed: {e}")
    
    # Initialize x402 payment system
    try:
        x402_payment_service = await setup_x402_payments()
        x402_middleware = x402_payment_service.get_middleware()
        app.add_middleware(BaseHTTPMiddleware, dispatch=x402_middleware)
        print("✅ x402 payment system initialized successfully")
    except Exception as e:
        print(f"⚠️ x402 payment system initialization failed: {e}")
        print("Continuing without payment system...")

# Allow CORS for modern frontend frameworks
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Streamlit
        "http://localhost:3000",  # React/Next.js
        "http://localhost:5173",  # Vite
        "http://localhost:8080",  # Vue
        "http://localhost:4200",  # Angular
        "*"  # For development - restrict in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Pydantic Models for API Schemas
# ============================================================================

class GeneratePlanRequest(BaseModel):
    destination: str = Field(..., description="Travel destination")
    budget: float = Field(..., gt=0, description="Budget in USD")
    user_wallet: Optional[str] = Field(None, description="User's wallet address")
    session_id: Optional[str] = Field(None, description="Session identifier")

class FlightInfo(BaseModel):
    from_location: str
    to_location: str
    airline: str
    dates: str
    price: float

class HotelInfo(BaseModel):
    name: str
    location: str
    price_per_night: float
    nights: int
    total: float

class TravelPlan(BaseModel):
    destination: str
    flights: List[FlightInfo]
    hotels: List[HotelInfo]
    activities: List[str]
    total_cost: float
    platform_fee: float
    grand_total: float
    plan_id: str
    created_at: str

class GeneratePlanResponse(BaseModel):
    status: str
    plan: Optional[TravelPlan] = None
    formatted_plan: Optional[str] = None
    error: Optional[str] = None

class ConfirmPlanRequest(BaseModel):
    plan_id: str = Field(..., description="Plan ID to confirm")
    user_wallet: str = Field(..., description="User's wallet address")
    payment_method: Optional[str] = Field("cdp", description="Payment method")
    session_id: Optional[str] = Field(None, description="Session identifier")

class BookingStatus(BaseModel):
    flights: str
    hotels: str
    activities: str

class ConfirmPlanResponse(BaseModel):
    status: str
    booking_status: Optional[BookingStatus] = None
    payment_status: str
    confirmation_message: str
    error: Optional[str] = None

class UserPlan(BaseModel):
    plan_id: str
    destination: str
    total_cost: float
    created_at: str
    status: str

class GetUserPlansResponse(BaseModel):
    status: str
    plans: List[UserPlan]
    error: Optional[str] = None

class AgentRequest(BaseModel):
    input: str = None
    user_input: str = None
    referrer_wallet: str = None

class TravelRequest(BaseModel):
    destination: str
    budget: int
    user_wallet: str

class TravelResponse(BaseModel):
    plan_id: str
    destination: str
    plan_data: Dict[str, Any]
    status: str

class BookingRequest(BaseModel):
    flight_id: str
    passenger_name: str
    passenger_email: str
    payment_method: str = "crypto"
    plan_id: Optional[str] = None

class PaymentConfirmation(BaseModel):
    payment_transaction_hash: Optional[str] = None

# ============================================================================
# Helper Functions
# ============================================================================

def format_travel_plan(state):
    """Format the travel plan state into a clean, professional travel itinerary."""
    if state.get('error'):
        return f"❌ **Error:** {state['error']}"
    
    plan = state.get('plan', {})
    if not plan:
        return "❌ **No plan generated.** Please try again with different parameters."
    
    destination = state.get('destination', 'Unknown Destination')
    flights = plan.get('flights', [])
    hotels = plan.get('hotels', [])
    activities = plan.get('activities', [])
    total_cost = plan.get('total_cost', 0)
    platform_fee = plan.get('platform_fee', 0)
    grand_total = total_cost + platform_fee
    
    # Format currency
    def format_currency(amount):
        return f"${amount:,.2f}"
    
    # Build the itinerary
    itinerary = f"""
# 🗺️ **Travel Itinerary for {destination}**

---

## ✈️ **Flight Details**
"""
    
    if flights:
        for i, flight in enumerate(flights, 1):
            itinerary += f"""
**Flight {i}:**
• **Route:** {flight.get('from', 'Unknown')} → {flight.get('to', 'Unknown')}
• **Airline:** {flight.get('airline', 'Unknown')}
• **Dates:** {flight.get('dates', 'TBD')}
• **Price:** {format_currency(flight.get('price', 0))}
"""
    else:
        itinerary += "• No flights selected\n"
    
    itinerary += f"""
---

## 🏨 **Accommodation**
"""
    
    if hotels:
        for i, hotel in enumerate(hotels, 1):
            itinerary += f"""
**Hotel {i}:**
• **Name:** {hotel.get('name', 'Unknown Hotel')}
• **Location:** {hotel.get('location', 'Unknown')}
• **Rate:** {format_currency(hotel.get('price_per_night', 0))} per night
• **Duration:** {hotel.get('nights', 0)} nights
• **Total:** {format_currency(hotel.get('total', 0))}
"""
    else:
        itinerary += "• No hotels selected\n"
    
    itinerary += f"""
---

## 🎯 **Activities & Experiences**
"""
    
    if activities:
        for i, activity in enumerate(activities, 1):
            itinerary += f"• **{activity}**\n"
    else:
        itinerary += "• No activities selected\n"
    
    itinerary += f"""
---

## 💰 **Cost Breakdown**

| Item | Amount |
|------|--------|
| **Flights** | {format_currency(sum(f.get('price', 0) for f in flights))} |
| **Accommodation** | {format_currency(sum(h.get('total', 0) for h in hotels))} |
| **Activities** | {format_currency(200)} |
| **Subtotal** | {format_currency(total_cost)} |
| **Platform Fee** | {format_currency(platform_fee)} |
| **---** | **---** |
| **🎯 Grand Total** | **{format_currency(grand_total)}** |

---

## 📋 **Booking Status**
• **Payment Status:** {state.get('payment_status', 'Pending')}
• **Booking Status:** {state.get('booking_status', {}).get('flights', 'Pending') if state.get('booking_status') else 'Pending'}

---
*Generated by AI Travel Assistant*
"""
    
    return itinerary.strip()

# ============================================================================
# API Endpoints
# ============================================================================

@app.post("/generate_plan", response_model=GeneratePlanResponse)
async def generate_plan(request: GeneratePlanRequest, db: Session = Depends(get_db)):
    """
    Generate a travel plan based on destination and budget.
    Returns both structured data and formatted plan.
    """
    try:
        # Create initial state
        state = {
            "destination": request.destination,
            "budget": request.budget,
            "flights": None,
            "hotels": None,
            "activities": None,
            "plan": None,
            "total_estimated_cost": 0.0,
            "platform_fee": 0.0,
            "payment_status": "",
            "booking_status": None,
            "user_wallet": request.user_wallet or "",
            "error": "",
            "session_id": request.session_id or ""
        }
        
        # Generate plan using LangGraph
        output_state = travel_app.invoke(input=state)
        
        if output_state.get('error'):
            return GeneratePlanResponse(
                status="error",
                error=output_state['error']
            )
        
        plan = output_state.get('plan', {})
        if not plan:
            return GeneratePlanResponse(
                status="error",
                error="No plan could be generated with the given parameters."
            )
        
        # Convert to structured format
        flights = [
            FlightInfo(
                from_location=f.get('from', 'Unknown'),
                to_location=f.get('to', 'Unknown'),
                airline=f.get('airline', 'Unknown'),
                dates=f.get('dates', 'TBD'),
                price=f.get('price', 0)
            ) for f in plan.get('flights', [])
        ]
        
        hotels = [
            HotelInfo(
                name=h.get('name', 'Unknown Hotel'),
                location=h.get('location', 'Unknown'),
                price_per_night=h.get('price_per_night', 0),
                nights=h.get('nights', 0),
                total=h.get('total', 0)
            ) for h in plan.get('hotels', [])
        ]
        
        activities = plan.get('activities', [])
        total_cost = plan.get('total_cost', 0)
        platform_fee = plan.get('platform_fee', 0)
        grand_total = total_cost + platform_fee
        
        # Create structured plan
        structured_plan = TravelPlan(
            destination=request.destination,
            flights=flights,
            hotels=hotels,
            activities=activities,
            total_cost=total_cost,
            platform_fee=platform_fee,
            grand_total=grand_total,
            plan_id="",  # Will be set after database save
            created_at=""  # Will be set after database save
        )
        
        # Save to database
        db_plan = PlanService.create_plan(
            db=db,
            user_wallet=request.user_wallet or "",
            destination=request.destination,
            budget=int(request.budget),
            plan_data=plan,
            status="generated"
        )
        
        # Update structured plan with database values
        structured_plan.plan_id = str(db_plan.id)
        structured_plan.created_at = db_plan.created_at.isoformat() if db_plan.created_at else ""
        
        # Generate formatted plan
        formatted_plan = format_travel_plan(output_state)
        
        return GeneratePlanResponse(
            status="success",
            plan=structured_plan,
            formatted_plan=formatted_plan
        )
        
    except Exception as e:
        return GeneratePlanResponse(
            status="error",
            error=f"Failed to generate plan: {str(e)}"
        )

@app.post("/confirm_plan", response_model=ConfirmPlanResponse)
async def confirm_plan(request: ConfirmPlanRequest, db: Session = Depends(get_db)):
    """
    Confirm a travel plan and process payment/booking.
    """
    try:
        # Retrieve the plan from database
        plan = PlanService.get_plan_by_id(db, request.plan_id)
        if not plan:
            return ConfirmPlanResponse(
                status="error",
                payment_status="failed",
                confirmation_message="Plan not found",
                error="Invalid plan ID"
            )
        
        # Update plan status to confirmed
        updated_plan = PlanService.update_plan_status(db, request.plan_id, "confirmed")
        if not updated_plan:
            return ConfirmPlanResponse(
                status="error",
                payment_status="failed",
                confirmation_message="Failed to update plan status",
                error="Database update failed"
            )
        
        # Simulate payment processing
        payment_status = "success"
        
        # Simulate booking confirmation
        booking_status = BookingStatus(
            flights="confirmed",
            hotels="confirmed",
            activities="confirmed"
        )
        
        confirmation_message = f"""
✅ **Travel Plan Confirmed!**

Your trip to {plan.destination} has been successfully booked.

**Booking Details:**
• Plan ID: {request.plan_id}
• Payment Status: {payment_status}
• Flights: {booking_status.flights}
• Hotels: {booking_status.hotels}
• Activities: {booking_status.activities}

You will receive confirmation emails for each booking component.
        """.strip()
        
        return ConfirmPlanResponse(
            status="success",
            booking_status=booking_status,
            payment_status=payment_status,
            confirmation_message=confirmation_message
        )
        
    except Exception as e:
        return ConfirmPlanResponse(
            status="error",
            payment_status="failed",
            confirmation_message="Failed to confirm plan",
            error=f"Confirmation failed: {str(e)}"
        )

@app.get("/get_user_plans/{user_wallet}", response_model=GetUserPlansResponse)
async def get_user_plans(user_wallet: str, db: Session = Depends(get_db)):
    """
    Retrieve all plans associated with a user wallet.
    """
    try:
        # Get plans from database
        db_plans = PlanService.get_user_plans(db, user_wallet)
        
        plans = []
        for db_plan in db_plans:
            # Extract total cost from plan_data
            plan_data = db_plan.plan_data
            total_cost = plan_data.get('grand_total', 0) if plan_data else 0
            
            user_plan = UserPlan(
                plan_id=str(db_plan.id),
                destination=db_plan.destination,
                total_cost=total_cost,
                created_at=db_plan.created_at.isoformat() if db_plan.created_at else "",
                status=db_plan.status
            )
            plans.append(user_plan)
        
        return GetUserPlansResponse(
            status="success",
            plans=plans
        )
        
    except Exception as e:
        return GetUserPlansResponse(
            status="error",
            plans=[],
            error=f"Failed to retrieve plans: {str(e)}"
        )

# ============================================================================
# Legacy Endpoints (for backward compatibility)
# ============================================================================

@app.post("/agent")
async def run_agent(request: Request):
    data = await request.json()
    # New travel planner flow
    if "destination" in data and "budget" in data:
        # Provide complete initial state with all required fields
        state = {
            "destination": data["destination"],
            "budget": float(data["budget"]),
            "flights": None,
            "hotels": None,
            "activities": None,
            "plan": None,
            "total_estimated_cost": 0.0,
            "platform_fee": 0.0,
            "payment_status": "",
            "booking_status": None,
            "user_wallet": data.get("user_wallet", ""),
            "error": "",
            "session_id": data.get("session_id", "")
        }
        output_state = travel_app.invoke(input=state)
        return {
            "status": "success",
            "response": format_travel_plan(output_state)
        }
    # Old chat flow (fallback)
    user_input = data.get("input") or data.get("user_input")
    if not user_input:
        return {
            "status": "error",
            "response": "No input provided",
            "error": "Missing required input field"
        }
    # Pass referrer_wallet to the agent state if provided
    agent_input = {"input": user_input}
    referrer_wallet = data.get("referrer_wallet")
    if referrer_wallet:
        agent_input["referrer_wallet"] = referrer_wallet
    output_state = langgraph_app.invoke(input=agent_input)
    response_text = output_state.get('response', "Done.")
    return {
        "status": "success",
        "response": response_text
    }

@app.get("/wallet-balance")
async def wallet_balance():
    try:
        # For demo, use the mainnet account address
        class DummyAccount:
            def __init__(self, address):
                self.address = "0xE132d512FC35Bf91aD0C1098031CE09A9BA95241"
        account = DummyAccount("0xE132d512FC35Bf91aD0C1098031CE09A9BA95241")
        balances = await get_wallet_balances_async(account)
        
        # Try to extract the first token balance and format it
        if balances and isinstance(balances, list) and len(balances) > 0:
            balance = balances[0]
            if hasattr(balance, 'token') and hasattr(balance, 'amount'):
                symbol = getattr(balance.token, 'symbol', 'UNKNOWN')
                raw_amount = getattr(balance.amount, 'amount', 0)
                decimals = getattr(balance.amount, 'decimals', 18)
                try:
                    human_amount = int(raw_amount) / (10 ** int(decimals))
                    formatted = f"{human_amount:.4f} {symbol}"
                except Exception:
                    formatted = f"{raw_amount} {symbol}"
                return {
                    "status": "success",
                    "response": f"Wallet balance: {formatted}"
                }
        
        return {
            "status": "success",
            "response": "No balance found"
        }
    except Exception as e:
        import traceback
        error_str = traceback.format_exc()
        print(f"[backend.py] Wallet balance error: {error_str}")
        return {
            "status": "error",
            "response": "An error occurred while fetching wallet balance.",
            "error": str(e)
        }

@app.post("/ipfs-upload")
async def ipfs_upload(request: dict):
    try:
        content = request.get("content", "")
        if not content:
            return {
                "status": "error",
                "response": "No content provided for IPFS upload",
                "error": "Missing content field"
            }
        
        # Import the IPFS upload function
        from tools.ipfs import upload_to_ipfs
        
        # Upload to IPFS
        ipfs_hash = upload_to_ipfs({"content": content})
        
        return {
            "status": "success",
            "response": f"Content uploaded to IPFS successfully. Hash: {ipfs_hash}"
        }
    except Exception as e:
        import traceback
        error_str = traceback.format_exc()
        print(f"[backend.py] IPFS upload error: {error_str}")
        return {
            "status": "error",
            "response": "An error occurred while uploading to IPFS.",
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/referrals/{wallet_address}")
async def get_referrals(wallet_address: str):
    try:
        records = retrieve_referrals_by_wallet(wallet_address)
        return {"status": "success", "response": records}
    except Exception as e:
        import traceback
        error_str = traceback.format_exc()
        print(f"[backend.py] Referral retrieval error: {error_str}")
        return {"status": "error", "response": "Failed to retrieve referrals.", "error": str(e)}

# New x402-integrated booking endpoints
@app.post("/api/flights/book")
async def book_flight_api(booking_request: BookingRequest):
    """Book a flight with x402 payment integration"""
    try:
        # Use the book_flight tool from agent_tools
        result = book_flight(
            flight_id=booking_request.flight_id,
            passenger_name=booking_request.passenger_name,
            passenger_email=booking_request.passenger_email,
            payment_method=booking_request.payment_method,
            plan_id=booking_request.plan_id
        )
        
        # Parse the result
        booking_data = json.loads(result)
        
        if booking_data.get("status") == "success":
            return {
                "status": "success",
                "booking_id": booking_data["booking_id"],
                "message": booking_data["message"],
                "payment_required": booking_data.get("payment_required", False),
                "payment_amount": booking_data.get("payment_amount"),
                "payment_currency": booking_data.get("payment_currency"),
                "next_step": booking_data.get("next_step")
            }
        else:
            raise HTTPException(status_code=400, detail=booking_data.get("message", "Booking failed"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bookings/{booking_id}")
async def get_booking_api(booking_id: str):
    """Get booking status and details"""
    try:
        # Use the get_booking_status tool from agent_tools
        result = get_booking_status(booking_id)
        
        # Parse the result
        booking_data = json.loads(result)
        
        if "error" in booking_data:
            raise HTTPException(status_code=404, detail=booking_data["message"])
        
        return booking_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bookings/{booking_id}/payment")
async def confirm_payment_api(booking_id: str, payment_data: PaymentConfirmation):
    """Confirm payment for a booking"""
    try:
        # Use the confirm_booking_payment tool from agent_tools
        result = confirm_booking_payment(
            booking_id=booking_id,
            payment_transaction_hash=payment_data.payment_transaction_hash
        )
        
        # Parse the result
        confirmation_data = json.loads(result)
        
        if confirmation_data.get("status") == "success":
            return confirmation_data
        else:
            raise HTTPException(status_code=400, detail=confirmation_data.get("message", "Payment confirmation failed"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/payments/pricing")
async def get_payment_pricing():
    """Get x402 payment pricing structure"""
    try:
        if x402_payment_service:
            return {
                "status": "success",
                "pricing": x402_payment_service.pricing,
                "wallet_address": x402_payment_service.wallet_address,
                "network": "base-mainnet",
                "currency": "USDC"
            }
        else:
            return {
                "status": "error",
                "message": "Payment system not initialized"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/travel/cost-calculation")
async def calculate_travel_cost_api(request: Dict[str, Any]):
    """Calculate travel costs including x402 fees"""
    try:
        result = calculate_travel_cost(
            flights=request.get("flights", ""),
            hotels=request.get("hotels"),
            activities=request.get("activities")
        )
        
        # Parse the result
        cost_data = json.loads(result)
        
        if cost_data.get("status") == "success":
            return cost_data
        else:
            raise HTTPException(status_code=400, detail="Cost calculation failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True, loop="asyncio") 