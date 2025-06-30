from sqlalchemy import Column, String, Integer, DateTime, Text, CheckConstraint, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

Base = declarative_base()

class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_wallet = Column(String(42), nullable=False, index=True)
    destination = Column(String(255), nullable=False)
    budget = Column(Integer, nullable=False)
    plan_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    status = Column(
        String(20), 
        nullable=False, 
        default='generated',
        index=True
    )
    
    __table_args__ = (
        CheckConstraint(
            status.in_(['generated', 'confirmed', 'cancelled']),
            name='valid_status'
        ),
    )
    
    # Relationship to bookings
    bookings = relationship("Booking", back_populates="plan")
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': str(self.id),
            'user_wallet': self.user_wallet,
            'destination': self.destination,
            'budget': self.budget,
            'plan_data': self.plan_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'status': self.status
        }

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(String, unique=True, index=True)  # TRV-XXXXX format
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=True)
    flight_id = Column(String)  # Amadeus flight offer ID
    passenger_name = Column(String)
    passenger_email = Column(String)
    payment_method = Column(String, default="crypto")  # crypto, card
    status = Column(String, default="pending_payment")  # pending_payment, confirmed, cancelled
    payment_amount = Column(Float)
    payment_currency = Column(String, default="USDC")
    payment_status = Column(String, default="pending")  # pending, completed, failed
    flight_details = Column(Text)  # JSON string of flight information
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to plan
    plan = relationship("Plan", back_populates="bookings")
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'plan_id': str(self.plan_id) if self.plan_id else None,
            'flight_id': self.flight_id,
            'passenger_name': self.passenger_name,
            'passenger_email': self.passenger_email,
            'payment_method': self.payment_method,
            'status': self.status,
            'payment_amount': self.payment_amount,
            'payment_currency': self.payment_currency,
            'payment_status': self.payment_status,
            'flight_details': self.flight_details,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 