# schemas.py
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

class AddressBase(BaseModel):
    id: Optional[str] = None
    label: Optional[str] = None
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    is_default: Optional[bool] = False

class AddressOut(AddressBase):
    id: str

class UserProfileOut(BaseModel):
    id: int
    name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    addresses: List[AddressOut] = Field(default_factory=list)

class UserProfileUpdate(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    addresses: Optional[List[AddressBase]] = None
