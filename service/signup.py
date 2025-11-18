# services/signup_service.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from model.user import User
from schema.auth_model import SignupIn
from utils.jwt import create_access_token, get_hashed_password

def svc_signup(payload,db):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed = get_hashed_password(payload.password)
    user = User(
        name=payload.name,
        email=payload.email,
        phone = payload.phone,
        hashed_password=hashed,
        is_active=True,
        role=2
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    
    token_payload = {
        "type": "access",
        "id": user.id,
        "role_id": user.role,
        "email": user.email,
    }
    access_token = create_access_token(token_payload)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "role_id": user.role,
        "message": "You have logged in successfully!",
    }
