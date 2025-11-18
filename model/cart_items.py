from model import Base
from sqlalchemy.orm import relationship 
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint, Boolean
from datetime import datetime

ACTIVE = "ACTIVE"
CONVERTED = "CONVERTED"
WISHLIST = "WISHLIST"

class CartItem(Base):
    __tablename__ = "cart_item"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)

    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)
    line_total = Column(Float, nullable=False)

    status = Column(String, default="ACTIVE", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    product = relationship("Product", backref="cart_items")

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", "status", name="unique_cart_item"),
    )
