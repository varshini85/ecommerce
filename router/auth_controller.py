from fastapi import APIRouter, Depends
from database.db_session import db_session, get_session
from schema.auth_model import (
    AuthRequestDetails, AuthLoginDetails, AuthResponseDetails, 
    Token, SignupIn, LoginIn, TokenOut, ForgotPasswordVerify,
    ForgotPasswordIn, NewPasswordIn, ResetPasswordIn, MessageOut)
from service.get_otp_for_email import get_otp_for_email
from service.verify_otp_for_email import verify_otp_for_email
from service.signup import svc_signup
from service.login import svc_login
from service.forgot_password import svc_forgot_password
from service.forgot_password_verify import svc_forgot_password_verify
from service.new_password import svc_new_password
from service.reset_password import svc_reset_password
from utils.jwt import get_current_user

router = APIRouter(tags=["auth"])

#Lovio marketing page signup
@router.post("/signup", status_code=201)
def signup(payload: SignupIn, db: db_session = Depends(get_session)):
    return svc_signup(payload,db)

#Lovio marketing page login
@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: db_session = Depends(get_session)):
    return svc_login(db=db, payload=payload)

#Lovio marketing page forget password
@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordIn, db: db_session = Depends(get_session)):
    return svc_forgot_password(db=db, payload=payload)

#Lovio marketing page otp verification
@router.post("/verify-otp")
def forgot_password_verify(payload: ForgotPasswordVerify, db: db_session = Depends(get_session)):
    return svc_forgot_password_verify(db=db, payload=payload)

#Lovio marketing page change new password
@router.post("/new-password")
def new_password(
    payload: NewPasswordIn,
    db: db_session = Depends(get_session),
):
    return svc_new_password(db=db, payload=payload)

#Lovio marketing page reset password
@router.post("/reset-password", response_model=MessageOut)
def reset_password(
    payload: ResetPasswordIn,
    db: db_session = Depends(get_session),
    current_user = Depends(get_current_user),
):
    return svc_reset_password(db=db, current_user=current_user, payload=payload)
