from pydantic import BaseModel
from typing import Optional, List, Literal, Any
from datetime import datetime
from pydantic import BaseModel, Field

class AddItemIn(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: Optional[int] = Field(None, gt=0, description="Optional quantity must be > 0 if provided")

class UpdateItemIn(BaseModel):
    quantity: int = Field(..., ge=0) 

class CartItemOut(BaseModel):
    id: int
    product_id: int
    name: str                
    image: Optional[str] = None 
    quantity: int
    selling_price: Optional[float] = None
    line_total: Optional[float] = None
    discounted_price: Optional[float] = None
    discounted_line_total: Optional[float] = None

class CartOut(BaseModel):
    user_id: int
    status: str = "ACTIVE"
    items: List[CartItemOut]
    grand_total: Optional[float] = None
    grand_total_after_discount: Optional[float] = None

class CartOutWithMessage(CartOut):
    message: str

class CheckoutResponse(BaseModel):
    message: Literal["checked out"]
    items_converted: int = Field(..., ge=0)
    grand_total: float
    grand_total_after_discount: Optional[float] = None

class WishlistItem(BaseModel):
    id: int
    product_id: int

class WishlistOut(BaseModel):
    count: int
    items: List[WishlistItem]

class WishlistActionResponse(BaseModel):
    message: str
    product_id: int
