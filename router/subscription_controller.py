# router/subscription_router.py
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from schema.subscription_schema import SubscriptionCreate
from database.db_session import get_session 
from service.subscription import subscription

router = APIRouter()

@router.post("/subscribe")
def subscribe(payload: SubscriptionCreate, session: Session = Depends(get_session)):
    return subscription(db=session, payload=payload)
