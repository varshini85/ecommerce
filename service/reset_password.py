from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from schema.auth_model import (
    ResetPasswordIn, MessageOut
)
from utils.jwt import (
    get_hashed_password, verify_password, 
)

def svc_reset_password(*, db: Session, current_user, payload: ResetPasswordIn) -> MessageOut:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    if not verify_password(payload.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Old password is incorrect",
        )

    current_user.hashed_password = get_hashed_password(payload.new_password)
    # clear any OTP remnants
    current_user.otp = None
    current_user.otp_time = None

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {"message": "Password changed successfully"}
