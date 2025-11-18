from dotenv import load_dotenv
load_dotenv(override=True)

import os
from decimal import Decimal, ROUND_HALF_UP

import razorpay
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from model.orders import Order, CREATED

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
    raise RuntimeError("Razorpay keys are not configured. Please set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in .env")

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


def _to_paise(amount_rupees: float) -> int:
    return int((Decimal(str(amount_rupees)) * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def create_order(
    db: Session,
    *,
    user_id: int,
    product_ids: list[int],      
    quantities: list[int],     
    amount: float,          
    currency: str = "INR",
):
    try:
        if not product_ids or not quantities or len(product_ids) != len(quantities):
            raise HTTPException(status_code=400, detail="Invalid product or quantity list")

        currency = (currency or "INR").strip().upper()
        if currency != "INR":
            currency = "INR"

        amount_paise = _to_paise(amount)

        order_data = {
            "amount": amount_paise,
            "currency": currency,
            "receipt": f"user-{user_id}-{amount_paise}",
            "payment_capture": 1,
        }
        
        rzp_order = razorpay_client.order.create(order_data)
        order_id = rzp_order.get("id")
        if not order_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid response from Razorpay")

        product_csv = ",".join(str(p) for p in product_ids)
        quantity_csv = ",".join(str(q) for q in quantities)

        order = Order(
            user_id=user_id,
            order_id=order_id,
            product_id=product_csv,
            quantity=quantity_csv,
            total_amount=float(amount),
            currency=currency,
            status=CREATED,
            
        )

        db.add(order)
        db.commit()
        db.refresh(order)

        return {
            "order_id": order_id,
            "amount": order.total_amount,
            "currency": order.currency,
            "products": product_ids,
            "quantities": quantities,
            "rzp_key_id": RAZORPAY_KEY_ID
        }

    except razorpay.errors.BadRequestError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Razorpay: {e}. payload={order_data}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating Razorpay order: {e}")
