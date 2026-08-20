from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Session
from datetime import datetime
from database import Base, get_db
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

PLAN_LIMITS = {
    "FREE": {"monthly_searches": 15, "monitored_stores": 2, "api_access": False},
    "PRO": {"monthly_searches": 200, "monitored_stores": 15, "api_access": False},
    "GROWTH": {"monthly_searches": 1000, "monitored_stores": 50, "api_access": True},
    "AGENCY": {"monthly_searches": 10000, "monitored_stores": 500, "api_access": True}
}

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    plan_tier = Column(String, default="FREE") # FREE, PRO, GROWTH, AGENCY
    searches_used = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="subscription")

def check_user_limit(user_id: int, action: str, db: Session):
    sub = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
    if not sub:
        sub = UserSubscription(user_id=user_id, plan_tier="FREE")
        db.add(sub)
        db.commit()
        db.refresh(sub)
        
    limits = PLAN_LIMITS.get(sub.plan_tier, PLAN_LIMITS["FREE"])
    
    if action == "search":
        if sub.searches_used >= limits["monthly_searches"]:
            raise HTTPException(
                status_code=403, 
                detail=f"Plan limit reached! Upgrade your plan for more searches. Current tier: {sub.plan_tier}"
            )
        sub.searches_used += 1
        db.commit()

@router.get("/my-plan")
def get_user_plan_status(user_id: int, db: Session = Depends(get_db)):
    sub = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
    tier = sub.plan_tier if sub else "FREE"
    limits = PLAN_LIMITS.get(tier, PLAN_LIMITS["FREE"])
    
    return {
        "plan_tier": tier,
        "searches_used": sub.searches_used if sub else 0,
        "max_searches": limits["monthly_searches"],
        "monitored_stores_limit": limits["monitored_stores"],
        "api_access": limits["api_access"]
    }