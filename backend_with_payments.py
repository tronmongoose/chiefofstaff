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
from datetime import datetime, date
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
from decimal import Decimal

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

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting backend initialization...")
    # Initialize database
    init_db()
    print("✅ Database initialized")
    print("✅ Simplified architecture initialized (no LangGraph dependency)")

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
    """Format travel plan for display"""
    plan = state.get('plan', {})
    if not plan:
        return "No plan available."
    
    def format_currency(amount):
        return f"${amount:,.2f}"
    
    flights = plan.get('flights', [])
    hotels = plan.get('hotels', [])
    activities = plan.get('activities', [])
    total_cost = plan.get('total_cost', 0)
    platform_fee = plan.get('platform_fee', 0)
    grand_total = total_cost + platform_fee
    
    formatted = f"""
# Travel Plan Summary

## Flights
"""
    
    for flight in flights:
        formatted += f"""
- **{flight.get('airline', 'Unknown')}**
  - From: {flight.get('from', 'Unknown')} → To: {flight.get('to', 'Unknown')}
  - Dates: {flight.get('dates', 'TBD')}
  - Price: {format_currency(flight.get('price', 0))}
"""
    
    formatted += f"""
## Hotels
"""
    
    for hotel in hotels:
        formatted += f"""
- **{hotel.get('name', 'Unknown Hotel')}**
  - Location: {hotel.get('location', 'Unknown')}
  - {hotel.get('nights', 0)} nights @ {format_currency(hotel.get('price_per_night', 0))}/night
  - Total: {format_currency(hotel.get('total', 0))}
"""
    
    formatted += f"""
## Activities
"""
    
    for activity in activities:
        formatted += f"- {activity}\n"
    
    formatted += f"""
## Cost Breakdown
- Base Cost: {format_currency(total_cost)}
- Platform Fee: {format_currency(platform_fee)}
- **Grand Total: {format_currency(grand_total)}**

*This plan is ready for booking with x402 crypto payments!*
"""
    
    return formatted

def generate_mock_plan(destination: str, budget: float):
    """Generate a mock travel plan for demonstration"""
    return {
        "flights": [
            {
                "from": "New York",
                "to": destination,
                "airline": "Demo Airlines",
                "dates": "2024-01-15 to 2024-01-22",
                "price": budget * 0.4
            }
        ],
        "hotels": [
            {
                "name": f"Demo Hotel {destination}",
                "location": destination,
                "price_per_night": budget * 0.1,
                "nights": 7,
                "total": budget * 0.7
            }
        ],
        "activities": [
            f"Explore {destination}",
            "Local cuisine tour",
            "Cultural experience"
        ],
        "total_cost": budget * 0.9,
        "platform_fee": budget * 0.1
    }

# ============================================================================
# API Endpoints
# ============================================================================

@app.post("/generate_plan", response_model=GeneratePlanResponse)
async def generate_plan(request: GeneratePlanRequest, db: Session = Depends(get_db)):
    """
    Generate a travel plan using simplified architecture (no LangGraph).
    """
    try:
        # Generate mock plan
        plan = generate_mock_plan(request.destination, request.budget)
        
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
            print(f"✅ Travel plan stored on IPFS: {ipfs_hash}")
            
        except Exception as ipfs_error:
            print(f"⚠️ IPFS storage failed: {ipfs_error}")
        
        # Generate formatted plan
        mock_state = {"plan": plan}
        formatted_plan = format_travel_plan(mock_state)
        
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
            confirmation_message="An error occurred",
            error=f"Failed to confirm plan: {str(e)}"
        )

@app.get("/get_user_plans/{user_wallet}", response_model=GetUserPlansResponse)
async def get_user_plans(user_wallet: str, db: Session = Depends(get_db)):
    """
    Get all plans for a specific user wallet.
    """
    try:
        plans = PlanService.get_plans_by_wallet(db, user_wallet)
        
        user_plans = []
        for plan in plans:
            plan_data = plan.plan_data or {}
            user_plans.append(UserPlan(
                plan_id=str(plan.id),
                destination=plan.destination,
                total_cost=plan_data.get('grand_total', 0),
                created_at=plan.created_at.isoformat() if plan.created_at else "",
                status=plan.status
            ))
        
        return GetUserPlansResponse(
            status="success",
            plans=user_plans
        )
        
    except Exception as e:
        return GetUserPlansResponse(
            status="error",
            plans=[],
            error=f"Failed to get user plans: {str(e)}"
        )

@app.post("/agent")
async def run_agent(request: Request):
    """
    Simplified agent endpoint without LangGraph dependency.
    """
    try:
        data = await request.json()
        
        # Check if this is a travel plan request
        if "destination" in data and "budget" in data:
            # Generate mock plan
            plan = generate_mock_plan(data.get("destination"), data.get("budget", 1000))
            mock_state = {"plan": plan}
            return {
                "status": "success",
                "response": format_travel_plan(mock_state)
            }
        
        # Simple chat response
        user_input = data.get("input") or data.get("user_input", "Hello")
        response_text = f"I'm a simplified travel assistant. You said: '{user_input}'. I can help you plan trips with x402 crypto payments!"
        
        return {
            "status": "success",
            "response": response_text
        }
        
    except Exception as e:
        return {
            "status": "error",
            "response": f"An error occurred: {str(e)}",
            "error": str(e)
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

# ============================================================================
# Reputation System Functions
# ============================================================================

async def create_reputation_record(
    traveler_wallet: str,
    platform_wallet: str,
    event_type: EventType,
    trip_data: TripData,
    payment_tx_hash: str = None,
    referrer_wallet: str = None,
    previous_record_hash: str = None
) -> ReputationRecord:
    """Create a new reputation record and store it on IPFS"""
    try:
        # Create the reputation record
        record = ReputationRecord(
            record_id=str(uuid.uuid4()),
            wallet_address=traveler_wallet,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            trip_data=trip_data,
            payment_tx_hash=payment_tx_hash,
            referrer_wallet=referrer_wallet,
            previous_record_hash=previous_record_hash,
            ipfs_hash="",  # Will be set after storage
            metadata={
                "platform_wallet": platform_wallet,
                "created_at": datetime.utcnow().isoformat()
            }
        )
        
        # Store on IPFS
        ipfs_hash = await IPFSStorageUtils.store_reputation_record(record)
        record.ipfs_hash = ipfs_hash
        
        print(f"✅ Reputation record created and stored on IPFS: {ipfs_hash}")
        return record
        
    except Exception as e:
        print(f"❌ Failed to create reputation record: {e}")
        return None

async def update_reputation_summary(wallet_address: str, new_record: ReputationRecord) -> ReputationSummary:
    """Update or create reputation summary for a wallet"""
    try:
        # Get existing summary or create new one
        existing_summary = await IPFSStorageUtils.get_reputation_summary(wallet_address)
        
        if existing_summary:
            # Update existing summary
            summary = existing_summary
            summary.total_records += 1
            summary.last_updated = datetime.utcnow()
            
            # Update based on event type
            if new_record.event_type == EventType.BOOKING_CREATED:
                summary.total_bookings += 1
                if new_record.trip_data:
                    summary.total_spent_usd += new_record.trip_data.cost_usd
                    if new_record.trip_data.destination not in summary.countries_visited:
                        summary.countries_visited.append(new_record.trip_data.destination)
            
            elif new_record.event_type == EventType.BOOKING_COMPLETED:
                summary.completed_bookings += 1
                summary.completion_rate = summary.completed_bookings / summary.total_bookings if summary.total_bookings > 0 else 0
            
            elif new_record.event_type == EventType.BOOKING_CANCELLED:
                summary.cancelled_bookings += 1
            
            elif new_record.event_type == EventType.DISPUTE_OPENED:
                summary.disputed_bookings += 1
                summary.dispute_rate = summary.disputed_bookings / summary.total_bookings if summary.total_bookings > 0 else 0
            
            elif new_record.event_type == EventType.REFERRAL_BONUS:
                summary.total_referrals += 1
                summary.total_bonus_earned += Decimal('10.00')  # Fixed bonus amount
            
            # Recalculate reputation score
            summary.reputation_score = calculate_reputation_score(summary)
            summary.reputation_level = get_reputation_level(summary.reputation_score)
            
        else:
            # Create new summary
            summary = ReputationSummary(
                wallet_address=wallet_address,
                reputation_score=Decimal('10.00'),  # Starting score
                reputation_level=ReputationLevel.NEW,
                total_bookings=1 if new_record.event_type == EventType.BOOKING_CREATED else 0,
                completed_bookings=0,
                cancelled_bookings=0,
                disputed_bookings=0,
                total_spent_usd=Decimal('0.00'),
                average_rating=Decimal('0.00'),
                completion_rate=Decimal('0.00'),
                dispute_rate=Decimal('0.00'),
                countries_visited=[new_record.trip_data.destination] if new_record.trip_data else [],
                total_travel_days=0,
                total_referrals=0,
                successful_referrals=0,
                total_commission_earned=Decimal('0.00'),
                total_bonus_earned=Decimal('0.00'),
                first_booking_date=datetime.utcnow(),
                last_booking_date=datetime.utcnow(),
                last_updated=datetime.utcnow()
            )
            
            # Update based on event type
            if new_record.event_type == EventType.BOOKING_CREATED and new_record.trip_data:
                summary.total_spent_usd = new_record.trip_data.cost_usd
                summary.first_booking_date = datetime.utcnow()
                summary.last_booking_date = datetime.utcnow()
        
        # Store updated summary on IPFS
        await IPFSStorageUtils.store_reputation_summary(summary)
        
        return summary
        
    except Exception as e:
        print(f"❌ Failed to update reputation summary: {e}")
        return None

def calculate_reputation_score(summary: ReputationSummary) -> Decimal:
    """Calculate reputation score based on various factors"""
    score = Decimal('10.00')  # Base score
    
    # Booking completion bonus
    if summary.total_bookings > 0:
        completion_bonus = (summary.completed_bookings / summary.total_bookings) * 50
        score += Decimal(str(completion_bonus))
    
    # Spending bonus (1 point per $100 spent)
    spending_bonus = summary.total_spent_usd / Decimal('100.00')
    score += spending_bonus
    
    # Referral bonus
    referral_bonus = summary.successful_referrals * 5
    score += Decimal(str(referral_bonus))
    
    # Dispute penalty
    if summary.total_bookings > 0:
        dispute_penalty = (summary.disputed_bookings / summary.total_bookings) * 100
        score -= Decimal(str(dispute_penalty))
    
    # Ensure minimum score
    return max(score, Decimal('0.00'))

def get_reputation_level(score: Decimal) -> ReputationLevel:
    """Get reputation level based on score"""
    score_int = int(score)
    
    if score_int >= 1000:
        return ReputationLevel.DIAMOND
    elif score_int >= 500:
        return ReputationLevel.PLATINUM
    elif score_int >= 200:
        return ReputationLevel.GOLD
    elif score_int >= 100:
        return ReputationLevel.SILVER
    elif score_int >= 50:
        return ReputationLevel.BRONZE
    else:
        return ReputationLevel.NEW

# ============================================================================
# Reputation API Endpoints
# ============================================================================

@app.get("/api/reputation/{wallet_address}", response_model=ReputationResponse)
async def get_wallet_reputation_api(wallet_address: str):
    """Get reputation data for a specific wallet"""
    try:
        # Get reputation summary
        summary = await IPFSStorageUtils.get_reputation_summary(wallet_address)
        
        if not summary:
            # Create default summary for new wallet
            summary = ReputationSummary(
                wallet_address=wallet_address,
                reputation_score=Decimal('0.00'),
                reputation_level=ReputationLevel.NEW,
                total_bookings=0,
                completed_bookings=0,
                cancelled_bookings=0,
                disputed_bookings=0,
                total_spent_usd=Decimal('0.00'),
                average_rating=Decimal('0.00'),
                completion_rate=Decimal('0.00'),
                dispute_rate=Decimal('0.00'),
                countries_visited=[],
                total_travel_days=0,
                total_referrals=0,
                successful_referrals=0,
                total_commission_earned=Decimal('0.00'),
                total_bonus_earned=Decimal('0.00'),
                first_booking_date=datetime.utcnow(),
                last_booking_date=datetime.utcnow(),
                last_updated=datetime.utcnow()
            )
        
        # Get recent records (mock data for now)
        recent_records = []
        
        return ReputationResponse(
            status="success",
            wallet_address=wallet_address,
            reputation_summary=summary,
            recent_records=recent_records,
            total_records=summary.total_bookings
        )
        
    except Exception as e:
        return ReputationResponse(
            status="error",
            wallet_address=wallet_address,
            error=f"Failed to get reputation data: {str(e)}"
        )

@app.post("/api/reputation/event", response_model=ReputationEventResponse)
async def create_reputation_event_api(event_request: ReputationEventRequest):
    """Create a new reputation event"""
    try:
        # Get platform wallet
        platform_wallet = x402_payment_service.wallet_address if x402_payment_service else "0x" + "0" * 40
        
        # Create reputation record
        record = await create_reputation_record(
            traveler_wallet=event_request.wallet_address,
            platform_wallet=platform_wallet,
            event_type=event_request.event_type,
            trip_data=event_request.trip_data,
            payment_tx_hash=event_request.payment_tx_hash,
            referrer_wallet=event_request.referrer_wallet
        )
        
        if record:
            # Update reputation summary
            await update_reputation_summary(event_request.wallet_address, record)
            
            return ReputationEventResponse(
                status="success",
                record_id=record.record_id,
                ipfs_hash=record.ipfs_hash
            )
        else:
            return ReputationEventResponse(
                status="error",
                error="Failed to create reputation record"
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
        # Get reputation summary
        summary = await IPFSStorageUtils.get_reputation_summary(wallet_address)
        
        if not summary:
            return ReputationResponse(
                status="error",
                wallet_address=wallet_address,
                error="No reputation data found"
            )
        
        # Mock recent records for now
        recent_records = []
        
        return ReputationResponse(
            status="success",
            wallet_address=wallet_address,
            reputation_summary=summary,
            recent_records=recent_records,
            total_records=summary.total_bookings
        )
        
    except Exception as e:
        return ReputationResponse(
            status="error",
            wallet_address=wallet_address,
            error=f"Failed to get reputation records: {str(e)}"
        )

@app.get("/api/reputation/leaderboard", response_model=LeaderboardResponse)
async def get_reputation_leaderboard_api(limit: int = 10):
    """Get reputation leaderboard"""
    try:
        # Mock leaderboard data for now
        leaderboard = [
            LeaderboardEntry(
                wallet_address="0x1234567890abcdef1234567890abcdef1234567890",
                reputation_score=Decimal('850.00'),
                reputation_level=ReputationLevel.PLATINUM,
                total_bookings=25,
                completed_bookings=24,
                average_rating=Decimal('4.8'),
                countries_visited=8
            ),
            LeaderboardEntry(
                wallet_address="0xabcdef1234567890abcdef1234567890abcdef1234",
                reputation_score=Decimal('650.00'),
                reputation_level=ReputationLevel.GOLD,
                total_bookings=18,
                completed_bookings=17,
                average_rating=Decimal('4.6'),
                countries_visited=6
            ),
            LeaderboardEntry(
                wallet_address="0x9876543210fedcba9876543210fedcba9876543210",
                reputation_score=Decimal('450.00'),
                reputation_level=ReputationLevel.SILVER,
                total_bookings=12,
                completed_bookings=11,
                average_rating=Decimal('4.4'),
                countries_visited=4
            )
        ]
        
        return LeaderboardResponse(
            status="success",
            leaderboard=leaderboard[:limit],
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
    """Get reputation levels information"""
    try:
        levels_info = {
            "levels": [
                {
                    "level": "NEW",
                    "name": "New Traveler",
                    "min_score": 0,
                    "max_score": 24,
                    "benefits": [
                        "Basic booking access",
                        "Standard customer support"
                    ]
                },
                {
                    "level": "BRONZE",
                    "name": "Bronze Traveler",
                    "min_score": 25,
                    "max_score": 99,
                    "benefits": [
                        "Priority booking",
                        "Enhanced customer support",
                        "5% referral bonus"
                    ]
                },
                {
                    "level": "SILVER",
                    "name": "Silver Traveler",
                    "min_score": 100,
                    "max_score": 199,
                    "benefits": [
                        "VIP booking access",
                        "24/7 customer support",
                        "10% referral bonus",
                        "Exclusive travel deals"
                    ]
                },
                {
                    "level": "GOLD",
                    "name": "Gold Traveler",
                    "min_score": 200,
                    "max_score": 499,
                    "benefits": [
                        "Premium booking access",
                        "Personal travel concierge",
                        "15% referral bonus",
                        "Exclusive travel deals",
                        "Priority dispute resolution"
                    ]
                },
                {
                    "level": "PLATINUM",
                    "name": "Platinum Traveler",
                    "min_score": 500,
                    "max_score": 999,
                    "benefits": [
                        "Luxury booking access",
                        "Dedicated travel manager",
                        "20% referral bonus",
                        "Exclusive travel deals",
                        "Priority dispute resolution",
                        "Custom travel packages"
                    ]
                },
                {
                    "level": "DIAMOND",
                    "name": "Diamond Traveler",
                    "min_score": 1000,
                    "max_score": 9999,
                    "benefits": [
                        "Ultimate booking access",
                        "Personal travel assistant",
                        "25% referral bonus",
                        "Exclusive travel deals",
                        "Priority dispute resolution",
                        "Custom travel packages",
                        "VIP airport services"
                    ]
                }
            ],
            "scoring_factors": {
                "booking_completion": "Points for completing bookings successfully",
                "spending_amount": "Points based on total amount spent on travel",
                "referral_bonus": "Points for successful referrals",
                "dispute_penalty": "Points deducted for disputes"
            }
        }
        
        return {
            "status": "success",
            "levels_info": levels_info
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to get levels info: {str(e)}"
        }

# ============================================================================
# x402 Payment Endpoints
# ============================================================================

@app.get("/api/payments/pricing")
async def get_payment_pricing():
    """Get x402 payment pricing information"""
    return {
        "status": "success",
        "pricing": {
            "platform_fee_percentage": 15,
            "minimum_fee_usdc": "0.10",
            "maximum_fee_usdc": "50.00",
            "supported_currencies": ["USDC"],
            "payment_methods": ["x402", "cdp"]
        }
    }

@app.get("/api/payments/split-info/{amount}")
async def get_split_payment_info(amount: float):
    """Get split payment information for a given amount"""
    try:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Calculate split payment
        platform_fee_percentage = 15  # 15% platform fee
        platform_fee = amount * (platform_fee_percentage / 100)
        user_amount = amount - platform_fee
        
        return {
            "status": "success",
            "split_info": {
                "total_amount": amount,
                "user_amount": round(user_amount, 2),
                "platform_fee": round(platform_fee, 2),
                "platform_fee_percentage": platform_fee_percentage,
                "platform_wallet": x402_payment_service.wallet_address if x402_payment_service else "0x" + "0" * 40
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to calculate split payment: {str(e)}"
        }

@app.post("/api/travel/cost-calculation")
async def calculate_travel_cost_api(request: Dict[str, Any]):
    """Calculate travel costs"""
    try:
        destination = request.get("destination", "Unknown")
        budget = request.get("budget", 1000)
        
        # Mock cost calculation
        flight_cost = budget * 0.4
        hotel_cost = budget * 0.5
        activities_cost = budget * 0.1
        
        return {
            "status": "success",
            "cost_breakdown": {
                "destination": destination,
                "total_budget": budget,
                "flight_cost": round(flight_cost, 2),
                "hotel_cost": round(hotel_cost, 2),
                "activities_cost": round(activities_cost, 2),
                "platform_fee": round(budget * 0.15, 2),
                "grand_total": round(budget * 1.15, 2)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to calculate travel costs: {str(e)}"
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 