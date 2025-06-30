from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from models import Plan, Booking
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

class PlanService:
    @staticmethod
    def create_plan(
        db: Session, 
        user_wallet: str, 
        destination: str, 
        budget: int, 
        plan_data: Dict[str, Any],
        status: str = "generated"
    ) -> Plan:
        """Create a new travel plan"""
        plan = Plan(
            user_wallet=user_wallet,
            destination=destination,
            budget=budget,
            plan_data=plan_data,
            status=status
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan
    
    @staticmethod
    def get_plan_by_id(db: Session, plan_id: str) -> Optional[Plan]:
        """Get plan by ID"""
        try:
            plan_uuid = uuid.UUID(plan_id)
            return db.query(Plan).filter(Plan.id == plan_uuid).first()
        except ValueError:
            return None
    
    @staticmethod
    def get_user_plans(db: Session, user_wallet: str) -> List[Plan]:
        """Get all plans for a user wallet"""
        return db.query(Plan).filter(
            Plan.user_wallet == user_wallet
        ).order_by(desc(Plan.created_at)).all()
    
    @staticmethod
    def update_plan_status(db: Session, plan_id: str, status: str) -> Optional[Plan]:
        """Update plan status"""
        plan = PlanService.get_plan_by_id(db, plan_id)
        if plan:
            plan.status = status
            db.commit()
            db.refresh(plan)
        return plan
    
    @staticmethod
    def update_plan_data(db: Session, plan_id: str, plan_data: Dict[str, Any]) -> Optional[Plan]:
        """Update plan data"""
        plan = PlanService.get_plan_by_id(db, plan_id)
        if plan:
            plan.plan_data = plan_data
            db.commit()
            db.refresh(plan)
        return plan
    
    @staticmethod
    def delete_plan(db: Session, plan_id: str) -> bool:
        """Delete a plan"""
        plan = PlanService.get_plan_by_id(db, plan_id)
        if plan:
            db.delete(plan)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_plans_by_status(db: Session, status: str) -> List[Plan]:
        """Get all plans by status"""
        return db.query(Plan).filter(Plan.status == status).all()
    
    @staticmethod
    def get_recent_plans(db: Session, limit: int = 10) -> List[Plan]:
        """Get recent plans"""
        return db.query(Plan).order_by(desc(Plan.created_at)).limit(limit).all()

# Booking-related functions
def create_booking(
    db: Session,
    flight_id: str,
    passenger_name: str,
    passenger_email: str,
    payment_method: str = "crypto",
    payment_amount: float = 0.10,
    flight_details: str = None,
    plan_id: str = None
) -> Booking:
    """Create a new booking record"""
    booking_id = f"TRV-{uuid.uuid4().hex[:8].upper()}"
    
    booking = Booking(
        booking_id=booking_id,
        plan_id=uuid.UUID(plan_id) if plan_id else None,
        flight_id=flight_id,
        passenger_name=passenger_name,
        passenger_email=passenger_email,
        payment_method=payment_method,
        payment_amount=payment_amount,
        flight_details=flight_details,
        status="pending_payment",
        payment_status="pending"
    )
    
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

def get_booking_by_id(db: Session, booking_id: str) -> Optional[Booking]:
    """Get booking by booking ID (TRV-XXXXX format)"""
    return db.query(Booking).filter(Booking.booking_id == booking_id).first()

def get_booking_by_db_id(db: Session, booking_db_id: int) -> Optional[Booking]:
    """Get booking by database ID"""
    return db.query(Booking).filter(Booking.id == booking_db_id).first()

def get_bookings_by_plan(db: Session, plan_id: str) -> List[Booking]:
    """Get all bookings for a specific plan"""
    return db.query(Booking).filter(Booking.plan_id == uuid.UUID(plan_id)).all()

def get_bookings_by_user(db: Session, user_wallet: str) -> List[Booking]:
    """Get all bookings for a user (via their plans)"""
    return db.query(Booking).join(Plan).filter(Plan.user_wallet == user_wallet).all()

def update_booking_status(
    db: Session,
    booking_id: str,
    status: str,
    payment_status: str = None
) -> Optional[Booking]:
    """Update booking status and optionally payment status"""
    booking = get_booking_by_id(db, booking_id)
    if booking:
        booking.status = status
        if payment_status:
            booking.payment_status = payment_status
        booking.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(booking)
    return booking

def update_booking_payment_status(
    db: Session,
    booking_id: str,
    payment_status: str
) -> Optional[Booking]:
    """Update only the payment status of a booking"""
    booking = get_booking_by_id(db, booking_id)
    if booking:
        booking.payment_status = payment_status
        booking.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(booking)
    return booking

def delete_booking(db: Session, booking_id: str) -> bool:
    """Delete a booking by booking ID"""
    booking = get_booking_by_id(db, booking_id)
    if booking:
        db.delete(booking)
        db.commit()
        return True
    return False

def get_pending_payments(db: Session) -> List[Booking]:
    """Get all bookings with pending payments"""
    return db.query(Booking).filter(
        and_(
            Booking.payment_status == "pending",
            Booking.status == "pending_payment"
        )
    ).all()

def get_confirmed_bookings(db: Session) -> List[Booking]:
    """Get all confirmed bookings"""
    return db.query(Booking).filter(Booking.status == "confirmed").all() 