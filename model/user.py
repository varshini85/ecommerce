from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,String,Boolean,DateTime
from datetime import datetime
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.postgresql import JSONB

from model import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    role = Column(Integer, nullable=True)
    email = Column(String, nullable=False,unique=True)
    phone = Column(String, nullable=True, unique=True, index=True)
    hashed_password = Column(String, nullable=True)
    otp = Column(Integer,nullable=True)
    otp_time = Column(Integer,nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer)
    created_email = Column(String)
    updated_by = Column(Integer)
    updated_email = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    addresses = Column(MutableList.as_mutable(JSONB), nullable=True, server_default='[]')
