# schema/pay_schema.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CreateOrderIn(BaseModel):
    product_ids: List[int]
    quantities: List[int]
    amount: float
    currency: Optional[str] = "INR"

class OrderOut(BaseModel):
    order_id: str
    amount: float
    currency: str
    products: List[int]
    quantities: List[int]
    rzp_key_id: str

class VerifyPaymentIn(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class VerifyPaymentOut(BaseModel):
    id: int
    user_id: int
    order_id: str
    payment_id: Optional[str]
    amount: float
    currency: str
    signature: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime