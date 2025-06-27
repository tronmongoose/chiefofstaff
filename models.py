from sqlalchemy import Column, String, Integer, DateTime, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

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