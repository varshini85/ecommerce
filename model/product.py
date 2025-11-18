from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,String,Boolean,DateTime, Float
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from model import Base

class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    sku_id = Column(String, nullable=False)
    hsn_code = Column(String, nullable=False)
    category = Column(String, nullable=False)
    coupon_code = Column(String, nullable=True)
    coupon_exp_days = Column(Integer, nullable=True)
    discount_percentage = Column(Integer, nullable=True)
    coupon_created_at = Column(DateTime)
    mrp_price = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    key_features = Column(JSONB, nullable=False)
    description = Column(String, nullable=False)
    net_quantity = Column(String, nullable=False)
    colour = Column(String, nullable=False)
    size  = Column(String, nullable=False)
    height = Column(String, nullable=True)
    weight = Column(String, nullable=True)
    width = Column(String, nullable=True)
    images = Column(JSONB, nullable=False)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
