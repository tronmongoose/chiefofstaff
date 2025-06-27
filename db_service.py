from sqlalchemy.orm import Session
from sqlalchemy import desc
from models import Plan
from typing import List, Optional, Dict, Any
import uuid

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