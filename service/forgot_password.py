from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from model.user import User
from schema.auth_model import (
    ForgotPasswordIn, ForgotPasswordVerify, NewPasswordIn, ResetPasswordIn, MessageOut
)
from utils.jwt import (
    get_hashed_password, verify_password, 
)
from utils.send_mail import send_email
from utils.generate_otp import generate_otp
from service.otp_temp import otp_email_template

from datetime import datetime, timedelta

def svc_forgot_password(*, db: Session, payload):
    email_norm = payload.email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == email_norm).first()
    if not user:
        return {"message": "If the email exists, a reset OTP has been sent"}

    otp = generate_otp()
    user.otp = otp
    user.otp_time = None  
    db.commit()

    subject = "Your Password Reset Code"
    html_content = otp_email_template(otp=otp,
    brand_name="ECOM",  
    expires_minutes=10)
    send_email(to_email_id=user.email, subject=subject, content_to_be_sent=html_content)

    return {"message": "OTP sent to email"}