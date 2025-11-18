# model/orders.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from model import Base

CREATED = "CREATED"
PAID = "PAID"
FAILED = "FAILED"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(String, nullable=False)
    product_id = Column(String, nullable=False)   
    quantity = Column(String, nullable=False)     
    total_amount = Column(Float, nullable=False)
    currency = Column(String(8), nullable=False, default="INR")  
    payment_id = Column(String, nullable=True)
    status = Column(String(16), nullable=False, default=CREATED)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
