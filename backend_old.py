from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
from wallet import get_wallet_balances_async
from agent_tools import TOOLS, book_flight, get_booking_status, confirm_booking_payment, calculate_travel_cost
import openai
import os
from tools.ipfs import retrieve_referrals_by_wallet
from pinata_service import pinata_service
import uuid
from datetime import datetime
import json
from sqlalchemy.orm import Session
from database import get_db, init_db
from db_service import PlanService
from x402_middleware import X402Middleware, TravelBookingPaymentService, setup_x402_payments
from reputation_models import (
    ReputationRecord, ReputationSummary, EventType, TripStatus,
    TripData, OutcomeData, VerificationData, ReferralData,
    create_booking_record, create_completion_record, IPFSStorageUtils
)
from transaction_log import log_transaction
from reputation_models import ReputationLevel

# --- x402 payment system initialization (TOP-LEVEL) ---
x402_payment_service = None
x402_middleware = None
try:
    print("🔧 [BOOT] Initializing x402 payment system before app creation...")
    from x402_middleware import payment_service, setup_x402_payments
    x402_payment_service = payment_service
    # Initialize the payment service wallet (sync workaround for startup)
    import asyncio
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # If running in a notebook or async context, create a new loop
        import nest_asyncio
        nest_asyncio.apply()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(payment_service.initialize_wallet())
    x402_middleware = loop.run_until_complete(setup_x402_payments())
    print(f"✅ [BOOT] x402 payment system initialized. Wallet: {payment_service.wallet_address}")
except Exception as e:
    print(f"⚠️ [BOOT] x402 payment system failed to initialize: {e}")
    x402_payment_service = None
    x402_middleware = None

# --- FastAPI app creation ---
app = FastAPI(title="AI Agent Wallet API", version="1.0.0")

# Register x402 middleware BEFORE app starts
if x402_middleware:
    app.add_middleware(BaseHTTPMiddleware, dispatch=x402_middleware)
    print("✅ [BOOT] x402 middleware registered with FastAPI app")
else:
    print("⚠️ [BOOT] x402 middleware not registered (payment system unavailable)")

# Global variables
travel_agent = None

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    global travel_agent
    print("🚀 Starting backend initialization...")
    # Initialize database
    init_db()
    print("✅ Database initialized")
    # Initialize travel agent (simplified - no LangGraph dependency)
    try:
        travel_agent = None  # Simplified architecture - no LangGraph agent
        print("✅ Travel agent initialization skipped (simplified architecture)")
    except Exception as e:
        print(f"⚠️ Travel agent initialization failed: {e}")

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
# Reputation API Endpoints
# ============================================================================

class ReputationEventRequest(BaseModel):
    """Request model for creating reputation events"""
    wallet_address: str = Field(..., description="Wallet address")
    event_type: EventType = Field(..., description="Type of reputation event")
    trip_data: Optional[TripData] = Field(None, description="Trip data for the event")
    outcome_data: Optional[OutcomeData] = Field(None, description="Outcome data for the event")
    payment_tx_hash: Optional[str] = Field(None, description="Payment transaction hash")
    referrer_wallet: Optional[str] = Field(None, description="Referrer wallet address")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ReputationResponse(BaseModel):
    """Response model for reputation data"""
    status: str
    wallet_address: str
    reputation_summary: Optional[ReputationSummary] = None
    recent_records: Optional[List[ReputationRecord]] = None
    total_records: int = 0
    error: Optional[str] = None

class ReputationEventResponse(BaseModel):
    """Response model for reputation event creation"""
    status: str
    record_id: Optional[str] = None
    ipfs_hash: Optional[str] = None
    error: Optional[str] = None

class LeaderboardEntry(BaseModel):
    """Model for leaderboard entries"""
    wallet_address: str
    reputation_score: Decimal
    reputation_level: ReputationLevel
    total_bookings: int
    completed_bookings: int
    average_rating: Optional[Decimal]
    countries_visited: int

class LeaderboardResponse(BaseModel):
    """Response model for reputation leaderboard"""
    status: str
    leaderboard: List[LeaderboardEntry]
    total_participants: int
    error: Optional[str] = None

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
        # Generate plan using simplified architecture (no LangGraph)
        # Mock response for demonstration
        output_state = {
            "plan": {
                "flights": [
                    {
                        "from": "New York",
                        "to": request.destination,
                        "airline": "Demo Airlines",
                        "dates": "2024-01-15 to 2024-01-22",
                        "price": request.budget * 0.4
                    }
                ],
                "hotels": [
                    {
                        "name": f"Demo Hotel {request.destination}",
                        "location": request.destination,
                        "price_per_night": request.budget * 0.1,
                        "nights": 7,
                        "total": request.budget * 0.7
                    }
                ],
                "activities": [
                    f"Explore {request.destination}",
                    "Local cuisine tour",
                    "Cultural experience"
                ],
                "total_cost": request.budget * 0.9,
                "platform_fee": request.budget * 0.1
            },
            "error": None
        }
        
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
        
        # Store travel plan on IPFS
        try:
            plan_data_for_ipfs = {
                "plan_id": str(db_plan.id),
                "destination": request.destination,
                "budget": request.budget,
                "user_wallet": request.user_wallet or "",
                "plan_data": plan,
                "structured_plan": structured_plan.dict(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            ipfs_hash = pinata_service.store_travel_plan(plan_data_for_ipfs)
            
            # Add IPFS hash to the response
            structured_plan.plan_id = str(db_plan.id)
            structured_plan.created_at = db_plan.created_at.isoformat() if db_plan.created_at else ""
            
            print(f"✅ Travel plan stored on IPFS: {ipfs_hash}")
            
        except Exception as ipfs_error:
            print(f"⚠️ IPFS storage failed: {ipfs_error}")
        
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
        
        # Create reputation record for booking creation
        try:
            # Extract plan data for reputation record
            plan_data = plan.plan_data or {}
            
            # Create TripData for reputation record
            trip_data = TripData(
                destination=plan.destination,
                cost_usd=Decimal(str(plan_data.get('grand_total', 0))),
                cost_usdc=Decimal(str(plan_data.get('grand_total', 0))),  # 1:1 for demo
                duration_days=7,  # Default duration
                start_date=date.today(),  # Default start date
                end_date=date.today(),  # Will be updated with actual dates
                booking_id=f"BK{request.plan_id}",
                plan_id=request.plan_id
            )
            
            # Get platform wallet from x402 service
            platform_wallet = x402_payment_service.wallet_address if x402_payment_service else "0x" + "0" * 40
            
            # Create reputation record
            reputation_record = await create_reputation_record(
                traveler_wallet=request.user_wallet,
                platform_wallet=platform_wallet,
                event_type=EventType.BOOKING_CREATED,
                trip_data=trip_data,
                referrer_wallet=request.referrer_wallet if hasattr(request, 'referrer_wallet') else None
            )
            
            if reputation_record:
                # Update reputation summary
                await update_reputation_summary(request.user_wallet, reputation_record)
                print(f"✅ Reputation record created for booking: {reputation_record.record_id}")
            
        except Exception as rep_error:
            print(f"⚠️ Reputation tracking failed: {rep_error}")
        
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
        output_state = {
            "plan": {
                "flights": [
                    {
                        "from": "New York",
                        "to": data["destination"],
                        "airline": "Demo Airlines",
                        "dates": "2024-01-15 to 2024-01-22",
                        "price": data["budget"] * 0.4
                    }
                ],
                "hotels": [
                    {
                        "name": f"Demo Hotel {data['destination']}",
                        "location": data["destination"],
                        "price_per_night": data["budget"] * 0.1,
                        "nights": 7,
                        "total": data["budget"] * 0.7
                    }
                ],
                "activities": [
                    f"Explore {data['destination']}",
                    "Local cuisine tour",
                    "Cultural experience"
                ],
                "total_cost": data["budget"] * 0.9,
                "platform_fee": data["budget"] * 0.1
            },
            "error": None
        }
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
            # Store booking confirmation on IPFS
            try:
                booking_data_for_ipfs = {
                    "booking_id": booking_id,
                    "confirmation_data": confirmation_data,
                    "payment_transaction_hash": payment_data.payment_transaction_hash,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                ipfs_hash = pinata_service.store_booking_data(booking_data_for_ipfs)
                
                # Add IPFS hash to the response
                confirmation_data["ipfs_hash"] = ipfs_hash
                confirmation_data["ipfs_url"] = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash.replace('ipfs://', '')}"
                
                print(f"✅ Booking confirmation stored on IPFS: {ipfs_hash}")
                
                # Create reputation record for payment confirmation
                try:
                    # Get booking details (in a real implementation, you'd fetch this from database)
                    # For now, we'll create a basic trip data structure
                    trip_data = TripData(
                        destination="Unknown",  # Would be fetched from booking
                        cost_usd=Decimal("0"),  # Would be fetched from booking
                        cost_usdc=Decimal("0"),  # Would be fetched from booking
                        duration_days=1,
                        start_date=date.today(),
                        end_date=date.today(),
                        booking_id=booking_id,
                        plan_id="unknown"
                    )
                    
                    # Get platform wallet from x402 service
                    platform_wallet = x402_payment_service.wallet_address if x402_payment_service else "0x" + "0" * 40
                    
                    # Create reputation record for payment
                    reputation_record = await create_reputation_record(
                        traveler_wallet="0x" + "0" * 40,  # Would be fetched from booking
                        platform_wallet=platform_wallet,
                        event_type=EventType.BOOKING_PAID,
                        trip_data=trip_data,
                        payment_tx_hash=payment_data.payment_transaction_hash
                    )
                    
                    if reputation_record:
                        print(f"✅ Payment reputation record created: {reputation_record.record_id}")
                        confirmation_data["reputation_record_id"] = reputation_record.record_id
                    
                except Exception as rep_error:
                    print(f"⚠️ Payment reputation tracking failed: {rep_error}")
                
            except Exception as ipfs_error:
                print(f"⚠️ IPFS storage failed: {ipfs_error}")
                confirmation_data["ipfs_error"] = str(ipfs_error)
            
            return confirmation_data
        else:
            raise HTTPException(status_code=400, detail=confirmation_data.get("message", "Payment confirmation failed"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/payments/pricing")
async def get_payment_pricing():
    """Get x402 payment pricing structure"""
    try:
        print(f"🔍 Payment pricing endpoint called")
        print(f"   Global x402_payment_service: {x402_payment_service}")
        print(f"   Type: {type(x402_payment_service)}")
        
        if x402_payment_service:
            print(f"   ✅ Payment service is available")
            print(f"   Wallet address: {x402_payment_service.wallet_address}")
            print(f"   Pricing: {x402_payment_service.pricing}")
            
            return {
                "status": "success",
                "pricing": x402_payment_service.pricing,
                "wallet_address": x402_payment_service.wallet_address,
                "network": "base-mainnet",
                "currency": "USDC"
            }
        else:
            print(f"   ❌ Payment service is None")
            return {
                "status": "error",
                "message": "Payment system not initialized"
            }
    except Exception as e:
        print(f"   ❌ Exception in payment pricing: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/payments/split-info/{amount}")
async def get_split_payment_info(amount: float):
    """Get split payment information for a given amount"""
    try:
        from x402_middleware import get_split_payment_info as get_split_info
        
        result = get_split_info(amount)
        
        if result["status"] == "success":
            return {
                "status": "success",
                "split_payment": result["split_payment"],
                "platform_wallet": result["platform_wallet"],
                "platform_fee_percentage": result["platform_fee_percentage"],
                "message": f"Split payment calculated with {result['platform_fee_percentage']}% platform fee"
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/travel/cost-calculation")
async def calculate_travel_cost_api(request: Dict[str, Any]):
    """Calculate travel costs including x402 fees"""
    try:
        # Import the direct function to avoid tool wrapper issues
        from agent_tools import calculate_travel_cost_direct
        
        # Call the function directly with the parameters
        result = calculate_travel_cost_direct(
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

# Reputation service functions
async def create_reputation_record(
    traveler_wallet: str,
    platform_wallet: str,
    event_type: EventType,
    trip_data: TripData,
    payment_tx_hash: str = None,
    referrer_wallet: str = None,
    previous_record_hash: str = None
) -> ReputationRecord:
    """Create and store a reputation record"""
    try:
        # Generate a temporary IPFS hash for the record
        temp_ipfs_hash = "Qm" + "temp" + "0" * 40
        
        # Create the reputation record
        record = create_booking_record(
            traveler_wallet=traveler_wallet,
            platform_wallet=platform_wallet,
            trip_data=trip_data,
            payment_tx_hash=payment_tx_hash or "0x" + "0" * 64,
            ipfs_hash=temp_ipfs_hash,
            referrer_wallet=referrer_wallet
        )
        
        # Update event type if needed
        if event_type != EventType.BOOKING_CREATED:
            record.event_type = event_type
        
        # Update previous record hash if provided
        if previous_record_hash:
            record.verification_data.previous_record_hash = previous_record_hash
        
        # Store on IPFS
        actual_ipfs_hash = pinata_service.store_reputation_record(record)
        
        # Update record with actual IPFS hash
        if actual_ipfs_hash and not actual_ipfs_hash.startswith("ipfs://error"):
            record.verification_data.ipfs_hash = actual_ipfs_hash.replace("ipfs://", "")
            print(f"✅ Reputation record stored: {actual_ipfs_hash}")
        else:
            print(f"⚠️ Failed to store reputation record on IPFS")
        
        return record
        
    except Exception as e:
        print(f"❌ Error creating reputation record: {e}")
        return None

async def update_reputation_summary(wallet_address: str, new_record: ReputationRecord) -> ReputationSummary:
    """Update reputation summary for a wallet"""
    try:
        # For now, create a basic summary
        # In a full implementation, you'd aggregate all records for the wallet
        summary = ReputationSummary(wallet_address=wallet_address)
        
        # Update based on the new record
        if new_record.event_type == EventType.BOOKING_CREATED:
            summary.total_bookings += 1
            summary.total_spent_usd += new_record.trip_data.cost_usd
            summary.total_spent_usdc += new_record.trip_data.cost_usdc
            
            if not summary.first_booking_date:
                summary.first_booking_date = new_record.trip_data.start_date
            summary.last_booking_date = new_record.trip_data.start_date
            
        elif new_record.event_type == EventType.TRIP_COMPLETED:
            summary.completed_bookings += 1
            if new_record.outcome_data.rating:
                # Update average rating
                if summary.average_rating:
                    total_rating = summary.average_rating * (summary.completed_bookings - 1) + new_record.outcome_data.rating
                    summary.average_rating = Decimal(str(total_rating / summary.completed_bookings))
                else:
                    summary.average_rating = Decimal(str(new_record.outcome_data.rating))
        
        # Update countries visited
        if new_record.trip_data.destination not in summary.countries_visited:
            summary.countries_visited.append(new_record.trip_data.destination)
        
        # Update referral statistics
        if new_record.referral_data.referrer_wallet:
            summary.total_referrals += 1
            if new_record.event_type == EventType.TRIP_COMPLETED:
                summary.successful_referrals += 1
            if new_record.referral_data.commission_amount:
                summary.total_commission_earned += new_record.referral_data.commission_amount
            if new_record.referral_data.bonus_amount:
                summary.total_bonus_earned += new_record.referral_data.bonus_amount
        
        # Calculate metrics
        if summary.total_bookings > 0:
            summary.completion_rate = Decimal(str(summary.completed_bookings / summary.total_bookings))
            summary.dispute_rate = Decimal(str(summary.disputed_bookings / summary.total_bookings))
        
        # Calculate reputation score and level
        summary.reputation_score = summary.calculate_reputation_score()
        summary.update_reputation_level()
        
        # Store updated summary on IPFS
        ipfs_hash = pinata_service.update_reputation_summary(summary)
        if ipfs_hash and not ipfs_hash.startswith("ipfs://error"):
            print(f"✅ Reputation summary updated: {ipfs_hash}")
        
        return summary
        
    except Exception as e:
        print(f"❌ Error updating reputation summary: {e}")
        return None

@app.get("/api/reputation/{wallet_address}", response_model=ReputationResponse)
async def get_wallet_reputation_api(wallet_address: str):
    """Get wallet reputation data including summary and recent records"""
    try:
        # Validate wallet address format
        if not wallet_address.startswith("0x") or len(wallet_address) != 42:
            raise HTTPException(status_code=400, detail="Invalid wallet address format")
        
        # Get reputation data from Pinata service
        reputation_data = pinata_service.get_wallet_reputation(wallet_address, limit=10)
        
        if "error" in reputation_data:
            # Return empty reputation data for new wallets
            return ReputationResponse(
                status="success",
                wallet_address=wallet_address,
                reputation_summary=ReputationSummary(wallet_address=wallet_address),
                recent_records=[],
                total_records=0
            )
        
        # For now, return basic structure
        # In a full implementation, you'd aggregate actual records from IPFS
        summary = ReputationSummary(wallet_address=wallet_address)
        
        return ReputationResponse(
            status="success",
            wallet_address=wallet_address,
            reputation_summary=summary,
            recent_records=[],
            total_records=0
        )
        
    except Exception as e:
        return ReputationResponse(
            status="error",
            wallet_address=wallet_address,
            error=f"Failed to get reputation: {str(e)}"
        )

@app.post("/api/reputation/event", response_model=ReputationEventResponse)
async def create_reputation_event_api(event_request: ReputationEventRequest):
    """Create a manual reputation event"""
    try:
        # Validate wallet address format
        if not event_request.wallet_address.startswith("0x") or len(event_request.wallet_address) != 42:
            raise HTTPException(status_code=400, detail="Invalid wallet address format")
        
        # Get platform wallet from x402 service
        platform_wallet = x402_payment_service.wallet_address if x402_payment_service else "0x" + "0" * 40
        
        # Create trip data if not provided
        if not event_request.trip_data:
            event_request.trip_data = TripData(
                destination="Manual Event",
                cost_usd=Decimal("0"),
                cost_usdc=Decimal("0"),
                duration_days=1,
                start_date=date.today(),
                end_date=date.today(),
                booking_id="MANUAL",
                plan_id="MANUAL"
            )
        
        # Create reputation record
        reputation_record = await create_reputation_record(
            traveler_wallet=event_request.wallet_address,
            platform_wallet=platform_wallet,
            event_type=event_request.event_type,
            trip_data=event_request.trip_data,
            payment_tx_hash=event_request.payment_tx_hash,
            referrer_wallet=event_request.referrer_wallet
        )
        
        if not reputation_record:
            return ReputationEventResponse(
                status="error",
                error="Failed to create reputation record"
            )
        
        # Update reputation summary
        await update_reputation_summary(event_request.wallet_address, reputation_record)
        
        return ReputationEventResponse(
            status="success",
            record_id=reputation_record.record_id,
            ipfs_hash=f"ipfs://{reputation_record.verification_data.ipfs_hash}"
        )
        
    except Exception as e:
        return ReputationEventResponse(
            status="error",
            error=f"Failed to create reputation event: {str(e)}"
        )

@app.get("/api/reputation/records/{wallet_address}", response_model=ReputationResponse)
async def get_reputation_records_api(wallet_address: str, limit: int = 20):
    """Get recent reputation records for a wallet"""
    try:
        # Validate wallet address format
        if not wallet_address.startswith("0x") or len(wallet_address) != 42:
            raise HTTPException(status_code=400, detail="Invalid wallet address format")
        
        # Validate limit
        if limit < 1 or limit > 100:
            limit = 20
        
        # For now, return empty records
        # In a full implementation, you'd query IPFS for actual records
        return ReputationResponse(
            status="success",
            wallet_address=wallet_address,
            recent_records=[],
            total_records=0
        )
        
    except Exception as e:
        return ReputationResponse(
            status="error",
            wallet_address=wallet_address,
            error=f"Failed to get reputation records: {str(e)}"
        )

@app.get("/api/reputation/leaderboard", response_model=LeaderboardResponse)
async def get_reputation_leaderboard_api(limit: int = 10):
    """Get reputation leaderboard with top holders"""
    try:
        # Validate limit
        if limit < 1 or limit > 50:
            limit = 10
        
        # For now, return empty leaderboard
        # In a full implementation, you'd aggregate reputation data from IPFS
        leaderboard = []
        
        # Example leaderboard entry (for demonstration)
        if limit > 0:
            leaderboard.append(LeaderboardEntry(
                wallet_address="0x" + "1" * 40,
                reputation_score=Decimal("500"),
                reputation_level=ReputationLevel.DIAMOND,
                total_bookings=10,
                completed_bookings=9,
                average_rating=Decimal("4.8"),
                countries_visited=5
            ))
        
        return LeaderboardResponse(
            status="success",
            leaderboard=leaderboard,
            total_participants=len(leaderboard)
        )
        
    except Exception as e:
        return LeaderboardResponse(
            status="error",
            leaderboard=[],
            total_participants=0,
            error=f"Failed to get leaderboard: {str(e)}"
        )

@app.get("/api/reputation/levels")
async def get_reputation_levels_api():
    """Get information about reputation levels and requirements"""
    try:
        levels_info = {
            "levels": [
                {
                    "level": ReputationLevel.NEW.value,
                    "name": "New Traveler",
                    "min_score": 0,
                    "max_score": 24,
                    "benefits": ["Basic booking access"]
                },
                {
                    "level": ReputationLevel.BRONZE.value,
                    "name": "Bronze Traveler",
                    "min_score": 25,
                    "max_score": 74,
                    "benefits": ["Priority support", "Basic rewards"]
                },
                {
                    "level": ReputationLevel.SILVER.value,
                    "name": "Silver Traveler",
                    "min_score": 75,
                    "max_score": 149,
                    "benefits": ["Enhanced rewards", "Referral bonuses"]
                },
                {
                    "level": ReputationLevel.GOLD.value,
                    "name": "Gold Traveler",
                    "min_score": 150,
                    "max_score": 299,
                    "benefits": ["Premium support", "Exclusive deals", "Higher referral rates"]
                },
                {
                    "level": ReputationLevel.PLATINUM.value,
                    "name": "Platinum Traveler",
                    "min_score": 300,
                    "max_score": 499,
                    "benefits": ["VIP support", "Exclusive experiences", "Maximum referral rates"]
                },
                {
                    "level": ReputationLevel.DIAMOND.value,
                    "name": "Diamond Traveler",
                    "min_score": 500,
                    "max_score": 1000,
                    "benefits": ["Concierge service", "Exclusive events", "Platform governance rights"]
                }
            ],
            "scoring_factors": {
                "completed_bookings": "10 points per booking",
                "high_completion_rate": "Up to 50 bonus points",
                "high_ratings": "Up to 100 bonus points",
                "disputes": "-20 points per dispute",
                "referrals": "5 points per successful referral",
                "travel_diversity": "5 points per country visited"
            }
        }
        
        return {
            "status": "success",
            "levels_info": levels_info
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to get reputation levels: {str(e)}"
        }

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True, loop="asyncio") 