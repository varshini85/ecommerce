# schemas/review.py
from typing import List, Optional
from pydantic import BaseModel, Field, confloat
from datetime import datetime

class ReviewBase(BaseModel):
    product_id: str = Field(..., description="Product identifier (string as in your model)")
    title: Optional[str] = None
    comment: Optional[str] = None
    images: Optional[List[str]] = []  

class ReviewCreate(ReviewBase):
    rating: confloat(ge=1, le=5)

class ReviewUpdate(BaseModel):
    title: Optional[str] = None
    comment: Optional[str] = None
    rating: Optional[confloat(ge=1, le=5)] = None
    images: Optional[List[str]] = None

class ReviewOut(BaseModel):
    id: int
    user_id: int
    product_id: str
    title: Optional[str]
    comment: Optional[str]
    rating: int
    images: List[str]
    is_verified_purchase: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
