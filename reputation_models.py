"""
Reputation Record Data Model System for Travel Bookings

This module provides comprehensive Pydantic models for tracking travel bookings
and building decentralized trust through IPFS-stored reputation records.
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, model_validator
import re
import hashlib
import json
import uuid
from pydantic.json import pydantic_encoder


class EventType(str, Enum):
    """Enumeration of reputation event types"""
    BOOKING_CREATED = "booking_created"
    BOOKING_PAID = "booking_paid"
    TRIP_STARTED = "trip_started"
    TRIP_COMPLETED = "trip_completed"
    TRIP_CANCELLED = "trip_cancelled"
    TRIP_REVIEWED = "trip_reviewed"
    DISPUTE_RAISED = "dispute_raised"
    DISPUTE_RESOLVED = "dispute_resolved"
    REFERRAL_MADE = "referral_made"
    REFERRAL_BONUS_PAID = "referral_bonus_paid"
    REFUND_ISSUED = "refund_issued"
    PLATFORM_FEE_PAID = "platform_fee_paid"


class TripStatus(str, Enum):
    """Enumeration of trip statuses"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    REFUNDED = "refunded"


class DisputeStatus(str, Enum):
    """Enumeration of dispute statuses"""
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    RESOLVED_FAVOR_TRAVELER = "resolved_favor_traveler"
    RESOLVED_FAVOR_PLATFORM = "resolved_favor_platform"
    CLOSED = "closed"


class ReputationLevel(str, Enum):
    """Enumeration of reputation levels"""
    NEW = "new"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class TripData(BaseModel):
    """Trip information for reputation records"""
    destination: str = Field(..., description="Trip destination")
    cost_usd: Decimal = Field(..., ge=0, decimal_places=2, description="Total trip cost in USD")
    cost_usdc: Decimal = Field(..., ge=0, decimal_places=6, description="Total trip cost in USDC")
    duration_days: int = Field(..., ge=1, description="Trip duration in days")
    start_date: date = Field(..., description="Trip start date")
    end_date: date = Field(..., description="Trip end date")
    booking_id: str = Field(..., description="Unique booking identifier")
    plan_id: str = Field(..., description="Travel plan identifier")
    
    @model_validator(mode='after')
    def validate_dates(self):
        """Validate date consistency"""
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValueError("Start date must be before end date")
            
            calculated_duration = (self.end_date - self.start_date).days
            if self.duration_days and calculated_duration != self.duration_days:
                raise ValueError("Duration days must match start and end dates")
        
        return self


class OutcomeData(BaseModel):
    """Trip outcome and feedback data"""
    status: TripStatus = Field(..., description="Final trip status")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Trip rating (1-5 stars)")
    feedback: Optional[str] = Field(None, max_length=1000, description="Trip feedback")
    refund_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Refund amount if applicable")
    dispute_status: Optional[DisputeStatus] = Field(None, description="Dispute status if applicable")
    dispute_reason: Optional[str] = Field(None, max_length=500, description="Reason for dispute")
    completion_verified: bool = Field(False, description="Whether trip completion was verified")
    
    @validator('rating')
    def validate_rating(cls, v):
        """Validate rating is within valid range"""
        if v is not None and (v < 1 or v > 5):
            raise ValueError("Rating must be between 1 and 5")
        return v


class VerificationData(BaseModel):
    """Blockchain and IPFS verification data"""
    payment_tx_hash: str = Field(..., description="x402 payment transaction hash")
    ipfs_hash: str = Field(..., description="IPFS hash of this reputation record")
    previous_record_hash: Optional[str] = Field(None, description="IPFS hash of previous record in chain")
    block_number: Optional[int] = Field(None, ge=0, description="Block number of payment transaction")
    verification_timestamp: datetime = Field(default_factory=datetime.utcnow, description="When verification occurred")
    
    @validator('payment_tx_hash')
    def validate_tx_hash(cls, v):
        """Validate transaction hash format"""
        if not re.match(r'^0x[a-fA-F0-9]{64}$', v):
            raise ValueError("Transaction hash must be 0x followed by 64 hex characters")
        return v
    
    @validator('ipfs_hash')
    def validate_ipfs_hash(cls, v):
        """Validate IPFS hash format"""
        if not re.match(r'^Qm[a-zA-Z0-9]{44}$', v):
            raise ValueError("IPFS hash must be Qm followed by 44 base58 characters")
        return v


class ReferralData(BaseModel):
    """Referral and commission tracking data"""
    referrer_wallet: Optional[str] = Field(None, description="Referrer wallet address")
    commission_rate: Optional[Decimal] = Field(None, ge=0, le=1, decimal_places=4, description="Commission rate (0-1)")
    commission_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=6, description="Commission amount in USDC")
    bonus_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=6, description="Bonus amount in USDC")
    referral_code: Optional[str] = Field(None, description="Referral code used")
    referral_tier: Optional[str] = Field(None, description="Referral tier level")
    
    @validator('referrer_wallet')
    def validate_referrer_wallet(cls, v):
        """Validate wallet address format"""
        if v is not None:
            if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
                raise ValueError("Wallet address must be 0x followed by 40 hex characters")
        return v


class ReputationRecord(BaseModel):
    """Main reputation record stored on IPFS"""
    # Core identifiers
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()).replace('-', ''), description="Unique record identifier")
    traveler_wallet: str = Field(..., description="Traveler wallet address")
    platform_wallet: str = Field(..., description="Platform wallet address")
    
    # Event information
    event_type: EventType = Field(..., description="Type of reputation event")
    event_timestamp: datetime = Field(default_factory=datetime.utcnow, description="When event occurred")
    
    # Trip and outcome data
    trip_data: TripData = Field(..., description="Trip information")
    outcome_data: OutcomeData = Field(..., description="Trip outcome and feedback")
    
    # Verification and referral data
    verification_data: VerificationData = Field(..., description="Blockchain and IPFS verification")
    referral_data: ReferralData = Field(..., description="Referral and commission data")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    version: str = Field("1.0.0", description="Record version")
    
    @validator('traveler_wallet', 'platform_wallet')
    def validate_wallet_addresses(cls, v):
        """Validate wallet address format"""
        if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError("Wallet address must be 0x followed by 40 hex characters")
        return v
    
    @validator('record_id')
    def validate_record_id(cls, v):
        """Validate record ID format"""
        if not re.match(r'^[a-zA-Z0-9_-]{20,50}$', v):
            raise ValueError("Record ID must be 20-50 alphanumeric characters, hyphens, or underscores")
        return v
    
    def generate_record_id(self) -> str:
        """Generate a unique record ID based on content"""
        content = f"{self.traveler_wallet}_{self.event_type}_{self.event_timestamp.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]
    
    def to_ipfs_json(self) -> str:
        """Convert record to JSON for IPFS storage"""
        return json.dumps(self.model_dump(exclude_none=True), indent=2, default=pydantic_encoder)
    
    def calculate_hash(self) -> str:
        """Calculate hash of record content"""
        content = self.to_ipfs_json()
        return hashlib.sha256(content.encode()).hexdigest()


class ReputationSummary(BaseModel):
    """Aggregated wallet reputation summary"""
    # Wallet information
    wallet_address: str = Field(..., description="Wallet address")
    reputation_level: ReputationLevel = Field(ReputationLevel.NEW, description="Current reputation level")
    
    # Booking statistics
    total_bookings: int = Field(0, ge=0, description="Total number of bookings")
    completed_bookings: int = Field(0, ge=0, description="Number of completed bookings")
    cancelled_bookings: int = Field(0, ge=0, description="Number of cancelled bookings")
    disputed_bookings: int = Field(0, ge=0, description="Number of disputed bookings")
    
    # Financial statistics
    total_spent_usd: Decimal = Field(Decimal('0'), ge=0, decimal_places=2, description="Total spent in USD")
    total_spent_usdc: Decimal = Field(Decimal('0'), ge=0, decimal_places=6, description="Total spent in USDC")
    total_refunds: Decimal = Field(Decimal('0'), ge=0, decimal_places=2, description="Total refunds received")
    
    # Quality metrics
    average_rating: Optional[Decimal] = Field(None, ge=1, le=5, decimal_places=2, description="Average trip rating")
    completion_rate: Decimal = Field(Decimal('0'), ge=0, le=1, decimal_places=4, description="Booking completion rate")
    dispute_rate: Decimal = Field(Decimal('0'), ge=0, le=1, decimal_places=4, description="Dispute rate")
    
    # Travel statistics
    countries_visited: List[str] = Field(default_factory=list, description="List of countries visited")
    total_travel_days: int = Field(0, ge=0, description="Total days traveled")
    
    # Referral statistics (for referrers)
    total_referrals: int = Field(0, ge=0, description="Total referrals made")
    successful_referrals: int = Field(0, ge=0, description="Successful referrals")
    total_commission_earned: Decimal = Field(Decimal('0'), ge=0, decimal_places=6, description="Total commission earned")
    total_bonus_earned: Decimal = Field(Decimal('0'), ge=0, decimal_places=6, description="Total bonus earned")
    
    # Calculated reputation score
    reputation_score: Decimal = Field(Decimal('0'), ge=0, le=1000, decimal_places=2, description="Calculated reputation score")
    
    # Timestamps
    first_booking_date: Optional[date] = Field(None, description="Date of first booking")
    last_booking_date: Optional[date] = Field(None, description="Date of last booking")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    @validator('wallet_address')
    def validate_wallet_address(cls, v):
        """Validate wallet address format"""
        if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError("Wallet address must be 0x followed by 40 hex characters")
        return v
    
    def calculate_reputation_score(self) -> Decimal:
        """Calculate reputation score based on various factors"""
        score = Decimal('0')
        
        # Base score from completed bookings
        score += self.completed_bookings * 10
        
        # Bonus for high completion rate
        if self.completion_rate > Decimal('0.95'):
            score += 50
        elif self.completion_rate > Decimal('0.90'):
            score += 30
        elif self.completion_rate > Decimal('0.80'):
            score += 10
        
        # Bonus for high average rating
        if self.average_rating:
            if self.average_rating >= Decimal('4.5'):
                score += 100
            elif self.average_rating >= Decimal('4.0'):
                score += 50
            elif self.average_rating >= Decimal('3.5'):
                score += 20
        
        # Penalty for disputes
        score -= self.disputed_bookings * 20
        
        # Bonus for referral activity
        score += self.successful_referrals * 5
        
        # Bonus for travel diversity
        score += len(self.countries_visited) * 5
        
        return max(Decimal('0'), min(Decimal('1000'), score))
    
    def update_reputation_level(self):
        """Update reputation level based on score"""
        score = self.reputation_score
        
        if score >= 500:
            self.reputation_level = ReputationLevel.DIAMOND
        elif score >= 300:
            self.reputation_level = ReputationLevel.PLATINUM
        elif score >= 150:
            self.reputation_level = ReputationLevel.GOLD
        elif score >= 75:
            self.reputation_level = ReputationLevel.SILVER
        elif score >= 25:
            self.reputation_level = ReputationLevel.BRONZE
        else:
            self.reputation_level = ReputationLevel.NEW


class IPFSStorageUtils:
    """Utilities for IPFS storage structure and path management"""
    
    @staticmethod
    def generate_ipfs_path(wallet_address: str, year: int, month: int) -> str:
        """Generate IPFS path for reputation records"""
        return f"/reputation/{wallet_address}/{year}/{month:02d}"
    
    @staticmethod
    def generate_record_filename(record: ReputationRecord) -> str:
        """Generate filename for reputation record"""
        timestamp = record.event_timestamp.strftime("%Y%m%d_%H%M%S")
        return f"{record.event_type}_{timestamp}_{record.record_id[:8]}.json"
    
    @staticmethod
    def generate_summary_path(wallet_address: str) -> str:
        """Generate IPFS path for reputation summary"""
        return f"/reputation/{wallet_address}/summary.json"
    
    @staticmethod
    def generate_chain_index_path(wallet_address: str) -> str:
        """Generate IPFS path for record chain index"""
        return f"/reputation/{wallet_address}/chain_index.json"
    
    @staticmethod
    def create_chain_link(record: ReputationRecord, previous_hash: Optional[str] = None) -> Dict[str, Any]:
        """Create chain link for chronological record linking"""
        return {
            "record_hash": record.verification_data.ipfs_hash,
            "previous_hash": previous_hash,
            "timestamp": record.event_timestamp.isoformat(),
            "event_type": record.event_type,
            "record_id": record.record_id
        }


class ReputationValidator:
    """Validation utilities for reputation records"""
    
    @staticmethod
    def validate_wallet_address(address: str) -> bool:
        """Validate wallet address format"""
        return bool(re.match(r'^0x[a-fA-F0-9]{40}$', address))
    
    @staticmethod
    def validate_rating(rating: int) -> bool:
        """Validate rating is within valid range"""
        return 1 <= rating <= 5
    
    @staticmethod
    def validate_amount(amount: Decimal) -> bool:
        """Validate financial amount is non-negative"""
        return amount >= 0
    
    @staticmethod
    def validate_date_consistency(start_date: date, end_date: date, duration_days: int) -> bool:
        """Validate date consistency"""
        if start_date >= end_date:
            return False
        
        calculated_duration = (end_date - start_date).days
        return calculated_duration == duration_days
    
    @staticmethod
    def validate_record_chain(records: List[ReputationRecord]) -> bool:
        """Validate chronological chain of records"""
        for i in range(1, len(records)):
            current = records[i]
            previous = records[i-1]
            
            # Check chronological order
            if current.event_timestamp <= previous.event_timestamp:
                return False
            
            # Check chain links
            if current.verification_data.previous_record_hash != previous.verification_data.ipfs_hash:
                return False
        
        return True


# Example usage and utility functions
def create_booking_record(
    traveler_wallet: str,
    platform_wallet: str,
    trip_data: TripData,
    payment_tx_hash: str,
    ipfs_hash: str,
    referrer_wallet: Optional[str] = None
) -> ReputationRecord:
    """Create a new booking record"""
    
    record = ReputationRecord(
        traveler_wallet=traveler_wallet,
        platform_wallet=platform_wallet,
        event_type=EventType.BOOKING_CREATED,
        trip_data=trip_data,
        outcome_data=OutcomeData(status=TripStatus.PENDING),
        verification_data=VerificationData(
            payment_tx_hash=payment_tx_hash,
            ipfs_hash=ipfs_hash
        ),
        referral_data=ReferralData(referrer_wallet=referrer_wallet)
    )
    
    # Generate record ID using the custom method
    record.record_id = record.generate_record_id()
    
    return record


def update_record_with_ipfs_hash(record: ReputationRecord, ipfs_hash: str) -> ReputationRecord:
    """Update record with IPFS hash after upload"""
    record.verification_data.ipfs_hash = ipfs_hash
    return record


def create_completion_record(
    original_record: ReputationRecord,
    rating: int,
    feedback: Optional[str] = None,
    ipfs_hash: str = None
) -> ReputationRecord:
    """Create a trip completion record"""
    
    # Use a default IPFS hash if none provided
    if ipfs_hash is None:
        ipfs_hash = "Qm" + "e"*44
    
    completion_record = ReputationRecord(
        traveler_wallet=original_record.traveler_wallet,
        platform_wallet=original_record.platform_wallet,
        event_type=EventType.TRIP_COMPLETED,
        trip_data=original_record.trip_data,
        outcome_data=OutcomeData(
            status=TripStatus.COMPLETED,
            rating=rating,
            feedback=feedback,
            completion_verified=True
        ),
        verification_data=VerificationData(
            payment_tx_hash=original_record.verification_data.payment_tx_hash,
            ipfs_hash=ipfs_hash,
            previous_record_hash=original_record.verification_data.ipfs_hash
        ),
        referral_data=original_record.referral_data
    )
    
    completion_record.record_id = completion_record.generate_record_id()
    
    return completion_record 