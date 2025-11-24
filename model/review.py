# app/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, func, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import expression
from model import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    product_id = Column(String, nullable=False)
    title = Column(String(255), nullable=True)
    comment = Column(Text, nullable=True)
    rating = Column(Numeric, nullable=False)  # 1 - 5
    images = Column(JSONB, nullable=True, server_default=expression.text("'[]'::jsonb"))
    is_verified_purchase = Column(Boolean, nullable=False, default=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    