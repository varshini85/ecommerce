from datetime import datetime
from fastapi.staticfiles import StaticFiles
from fastapi import APIRouter, Query, Depends, status, Path, File, UploadFile, HTTPException, Form
from database.db_session import db_session, get_session
from sqlalchemy.exc import SQLAlchemyError
from schema.product_schemas import (
    ProductResponse, CreateProduct, AddProductResponse, 
    ProductListResponse, SingleProductResponse, UpdateProduct,
    UpdateProductResponse, DeleteProductResponse
)
from model.product import Product
from service.product_list import product_list_service
from service.add_product import add_product_service
from service.get_products import get_products_service, get_product_by_id_service
from service.update_product import update_product_service
from service.delete_product import delete_product_service
from utils.jwt import get_current_user, get_current_user_optional
from typing import List, Optional
from model.user import User
import os
import shutil
import uuid

router = APIRouter(tags=["product"])

@router.get("/product_list", response_model=ProductResponse)
def product_list(search_term: str = Query(...)):
    return product_list_service(search_term)

# Database product endpoints (new functionality)
@router.get("/list", response_model=ProductListResponse)
def get_products(
    search_term: Optional[str] = Query(None, description="Search term to filter products by name or description"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of products to return"),
    offset: int = Query(0, ge=0, description="Number of products to skip"),
    session: db_session = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    return get_products_service(session, search_term, limit, offset, current_user)

@router.get("/{product_id}", response_model=SingleProductResponse)
def get_product(
    product_id: int = Path(..., description="ID of the product to retrieve"),
    session: db_session = Depends(get_session)
):
    return get_product_by_id_service(session, product_id)

@router.delete("/{product_id}", response_model=DeleteProductResponse)
def delete_product(
    product_id: int = Path(..., description="ID of the product to delete"),
    current_user=Depends(get_current_user),
    session: db_session = Depends(get_session)
):
    return delete_product_service(session, current_user, product_id)

@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=AddProductResponse)
async def add_product(
    name: str = Form(...),
    sku_id: str = Form(...),
    hsn_code: str = Form(...),
    category: str = Form(...),
    coupon_code: Optional[str] = Form(None),
    coupon_exp_days: Optional[int] = Form(None),
    discount_percentage: Optional[int] = Form(None),
    mrp_price: float = Form(...),
    selling_price: float = Form(...),
    key_features: list = Form(...),
    description: str = Form(...),
    net_quantity: str = Form(...),
    colour: str = Form(...),
    size: str = Form(...),
    height: str = Form(...),
    weight: str = Form(...),
    width: str = Form(...),
    images: List[UploadFile] = File(...),
    current_user=Depends(get_current_user),
    session=Depends(get_session)
):
    try:
        os.makedirs("static", exist_ok=True)
        image_urls = []
        for image in images:
            file_path = os.path.join("static", image.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            image_url = f"https://api.marketmeter.lovio.store/images/{image.filename}"
            image_urls.append(image_url)

        new_product = Product(
            name=name,
            sku_id=sku_id,
            hsn_code=hsn_code,
            category=category,
            coupon_code=coupon_code,
            coupon_exp_days=coupon_exp_days,
            discount_percentage=discount_percentage,
            coupon_created_at=datetime.now() if coupon_code else None,
            mrp_price=mrp_price,
            selling_price=selling_price,
            key_features=key_features,
            net_quantity=net_quantity,
            colour=colour,
            size=size,
            height=height,
            weight=weight,
            width=width,
            description=description,
            images=image_urls, 
        )

        session.add(new_product)
        session.commit()
        session.refresh(new_product)

        return {
            "status": "success",
            "message": "Product added successfully",
            "product_id": new_product.id,
            "data": {
                "id": new_product.id,
                "name": new_product.name,
                "description": new_product.description,
                "images": image_urls,
            }
        }

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Error occurred: {str(e)}")
    
@router.put("/{product_id}", response_model=UpdateProductResponse)
def update_product(
    product_id: int = Path(..., description="ID of the product to update"),
    name: Optional[str] = Form(None),
    sku_id: Optional[str] = Form(None),
    hsn_code: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    mrp_price: Optional[float] = Form(None),
    coupon_code: Optional[str] = Form(None),
    coupon_exp_days: Optional[int] = Form(None),
    discount_percentage: Optional[int] = Form(None),
    selling_price: Optional[float] = Form(None),
    key_features: Optional[list] = None,
    description: Optional[str] = Form(None),
    net_quantity: Optional[str] = Form(None),
    colour: Optional[str] = Form(None),
    size: Optional[str] = Form(None),
    height: Optional[str] = Form(None),
    weight: Optional[str] = Form(None),
    width: Optional[str] = Form(None),
    images: Optional[List[UploadFile]] = File(None),
    existing_images: Optional[list] = None,
    current_user=Depends(get_current_user),
    session: db_session = Depends(get_session)
):
    os.makedirs("static", exist_ok=True)
    image_urls = []
    for image in images:
        file_path = os.path.join("static", image.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = f"https://api.marketmeter.lovio.store/images/{image.filename}"
        image_urls.append(image_url)

    request = UpdateProduct(
        name=name,
        sku_id=sku_id,
        hsn_code=hsn_code,
        category=category,
        mrp_price=mrp_price,
        coupon_code=coupon_code,
        coupon_exp_days=coupon_exp_days,
        discount_percentage=discount_percentage,
        selling_price=selling_price,
        key_features=key_features,
        description=description,
        net_quantity=net_quantity,
        colour=colour,
        size=size,
        height=height,
        weight=weight,
        width=width,
        images=image_urls,
        existing_images=existing_images
    )
    return update_product_service(session, product_id, request, current_user)