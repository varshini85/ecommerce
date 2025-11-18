from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload
from datetime import datetime, timedelta
from typing import Optional
from model.orders import Order, PAID
from model.product import Product


def is_first_time_user(db: Session, user_id: int) -> bool:
        count_paid = db.query(func.count(Order.id)).filter(
            Order.user_id == user_id,
            Order.status == PAID,
        ).scalar() or 0
        return count_paid == 0

def _product_coupon_valid(product: Product) -> bool:

    if product.coupon_created_at is None or product.coupon_exp_days is None:
        return False

    try:
        exp_days = int(product.coupon_exp_days)
    except (TypeError, ValueError):
        return False
    
    expiry_time = product.coupon_created_at + timedelta(days=exp_days)

    return expiry_time > datetime.utcnow()

def _apply_discounted_price(selling_price: float, discount_percentage: int) -> float:

    try:
        discount_pct = float(discount_percentage or 0)
    except Exception:
        discount_pct = 0.0
    discounted = selling_price * (1 - (discount_pct / 100.0))
    return round(discounted, 2)

