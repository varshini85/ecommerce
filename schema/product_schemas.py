from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProductResponse(BaseModel):
    amazon: dict
    flipkart: dict
    meesho: None
    myntra: dict

class CreateProduct(BaseModel):
    name: str
    sku_id: str
    hsn_code: str
    category: str
    coupon_code: Optional[str] = None
    coupon_exp_days: Optional[int] = None
    discount_percentage: Optional[int] = None
    mrp_price: float
    selling_price: float
    key_features: list
    description: str
    net_quantity: str
    colour: str
    size: str
    height:str
    weight:str
    width:str
    images: list

class UpdateProduct(BaseModel):
    name: Optional[str] = None
    sku_id: Optional[str] = None
    hsn_code: Optional[str] = None
    category: Optional[str] = None
    mrp_price: Optional[float] = None
    coupon_code: Optional[str] = None
    coupon_exp_days: Optional[int] = None
    discount_percentage: Optional[int] = None
    selling_price: Optional[float] = None
    key_features: Optional[list] = None
    description: Optional[str] = None
    net_quantity: Optional[str] = None
    colour: Optional[str] = None
    size: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    width: Optional[str] = None
    images: Optional[list] = None
    existing_images: Optional[list] = None,

class ProductData(BaseModel):
    id: int
    name: str
    description: str

class AddProductResponse(BaseModel):
    status: str
    message: str
    product_id: int
    data: ProductData

# New schemas for product list functionality
class ProductItem(BaseModel):
    id: int
    name: str
    mrp_price: float
    selling_price: float
    category: str
    images: str
    description: str
    coupon_code: Optional[str] = None
    coupon_exp_days: Optional[int] = None
    discount_percentage: Optional[int] = None
    discounted_price: Optional[float] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ProductListData(BaseModel):
    products: List[ProductItem]
    total_count: int
    limit: int
    offset: int
    has_more: bool

class ProductListResponse(BaseModel):
    status: str
    message: str
    data: ProductListData

class ProductDetail(BaseModel):
    id: int
    name: Optional[str] = None
    sku_id: Optional[str] = None
    hsn_code: Optional[str] = None
    category: Optional[str] = None
    mrp_price: Optional[float] = None
    selling_price: Optional[float] = None
    key_features: Optional[list] = None
    description: Optional[str] = None
    net_quantity: Optional[str] = None
    colour: Optional[str] = None
    size: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    width: Optional[str] = None
    images: Optional[list] = None
    coupon_code: Optional[str] = None
    coupon_exp_days: Optional[int] = None
    discount_percentage: Optional[int] = None

class SingleProductResponse(BaseModel):
    status: str
    message: str
    data: ProductDetail

class UpdateProductResponse(BaseModel):
    status: str
    message: str
    product_id: int
    data: ProductData

class DeleteProductResponse(BaseModel):
    status: str
    message: str
    product_id: int