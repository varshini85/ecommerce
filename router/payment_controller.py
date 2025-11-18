# router/payments.py
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from database.db_session import get_session
from schema.pay_schema import OrderOut, CreateOrderIn, VerifyPaymentIn, VerifyPaymentOut
from utils.jwt import get_current_user 
from model.user import User
from service.verify_payment import verify_payment
from service.create_order import create_order

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/order", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_pay(
    payload: CreateOrderIn,      
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return create_order(
        db=db,
        user_id=current_user.id,
        product_ids=payload.product_ids,  
        quantities=payload.quantities,   
        amount=payload.amount,          
        currency=payload.currency,     
    )

@router.post(
    "/verify-payment",
    response_model=VerifyPaymentOut,
    status_code=status.HTTP_200_OK
)
def verify_payment_route(
    payload: VerifyPaymentIn,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return verify_payment(
        db=db,
        user_id=current_user.id,
        razorpay_order_id=payload.razorpay_order_id,
        razorpay_payment_id=payload.razorpay_payment_id,
        razorpay_signature=payload.razorpay_signature,
    )