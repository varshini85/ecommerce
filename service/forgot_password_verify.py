# services/password_service.py
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from model.user import User


def svc_forgot_password_verify(*, db: Session, payload):
    email = payload.email.strip().lower()

    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user or not user.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    return {"message": "OTP verified successfully"}