from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from model.user import User
from schema.auth_model import (
    NewPasswordIn
)
from utils.jwt import (
    get_hashed_password 
)

def svc_new_password(*, db: Session, payload: NewPasswordIn):
   
    email_norm = payload.email.strip().lower()
    user: User | None = db.query(User).filter(func.lower(User.email) == email_norm).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

   
    user.hashed_password = get_hashed_password(payload.new_password)
    user.otp = None
    user.otp_time = None

    db.commit()

    return {"message": "Password changed successfully"}
