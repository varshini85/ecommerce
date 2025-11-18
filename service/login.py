# services/login_service.py
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from model.user import User
from schema.auth_model import LoginIn
from utils.jwt import create_access_token, verify_password


def svc_login(*, db: Session, payload: LoginIn):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not verified")

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")

    # Include role info in JWT so downstream can authorize quickly (optional but handy)
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
