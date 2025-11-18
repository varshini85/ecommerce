# service/verify_payment.py
from dotenv import load_dotenv
load_dotenv(override=True)

import os
from datetime import datetime
import razorpay
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from model.orders import Order, CREATED, PAID, FAILED
from service.converted import convert_cart_items_for_user,parse_int_list

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
    raise RuntimeError("Razorpay keys are not configured. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET.")

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


def verify_payment(
    db: Session,
    *,
    user_id: int,
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
) -> dict:
    
    payment = (
        db.query(Order)
        .filter(Order.order_id == razorpay_order_id, Order.user_id == user_id)
        .first()
    )
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment record not found")

    if payment.status in (PAID, FAILED):
        return {
            "id": payment.id,
            "user_id": payment.user_id,
            "order_id": payment.order_id,
            "payment_id": payment.payment_id,
            "amount": payment.total_amount,
            "currency": payment.currency,
            "status": payment.status,
            "created_at": payment.created_at,
            "updated_at": payment.updated_at,
        }

    try:
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        })
    except razorpay.errors.SignatureVerificationError:
        try:
            payment.status = FAILED
            payment.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(payment)
        except SQLAlchemyError:
            db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Signature verification failed")

    try:
        rp_payment = razorpay_client.payment.fetch(razorpay_payment_id)
        rp_status = (rp_payment or {}).get("status", "").lower()
    except razorpay.errors.BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Razorpay: {e}")
    except razorpay.errors.ServerError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Razorpay server error: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Payment fetch error: {e}")

    if rp_status in {"captured", "authorized"}:
        final_status = PAID
    elif rp_status == "failed":
        final_status = FAILED
    else:
        final_status = CREATED  

    try:
        payment.payment_id = razorpay_payment_id
        payment.status = final_status
        payment.updated_at = datetime.utcnow()

        converted_ids: list[int] = []
        if final_status == PAID:
            paid_pids = parse_int_list(getattr(payment, "product_id", "") or "")
            if paid_pids:
                converted_ids = convert_cart_items_for_user(db, user_id, paid_pids)

        db.commit()
        db.refresh(payment)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB error: {e}")

    resp = {
        "id": payment.id,
        "user_id": payment.user_id,
        "order_id": payment.order_id,
        "payment_id": payment.payment_id,
        "amount": payment.total_amount,
        "currency": payment.currency,
        "signature": razorpay_signature,
        "status": payment.status,
        "created_at": payment.created_at,
        "updated_at": payment.updated_at,
    }
    if converted_ids:
        resp["converted_cart_item_ids"] = converted_ids
    return resp