from fastapi import HTTPException, Depends, status
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_
from model.product import Product
from typing import List, Optional
from utils.jwt import get_current_user_optional
from model.user import User
from service.discount import is_first_time_user, _product_coupon_valid, _apply_discounted_price

def get_products_service(
    session: Session,
    search_term: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    try:
        query = session.query(Product)

        if search_term:
            search_filter = or_(
                Product.name.ilike(f"%{search_term}%"),
                Product.description.ilike(f"%{search_term}%"),
                Product.category.ilike(f"%{search_term}%")
            )
            query = query.filter(search_filter)

        total_count = query.count()
        products = query.order_by(Product.updated_at.desc()).offset(offset).limit(limit).all()

        is_first_time = False
        if current_user:
            try:
                is_first_time = is_first_time_user(session, current_user.id)
            except Exception:
                is_first_time = False

        products_list = []
        for product in products:
            product_dict = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "selling_price": product.selling_price,
                "mrp_price": product.mrp_price,
                "category": product.category,
                "images": product.images[0] if product.images else None,
                "coupon_code": None,
                "coupon_exp_days": None,
                "discount_percentage": None,
                "discounted_price": None,
                "coupon_expires_at": None,
                "created_by": product.created_by,
                "updated_by": product.updated_by,
                "created_at": product.created_at.isoformat() if product.created_at else None,
                "updated_at": product.updated_at.isoformat() if product.updated_at else None
            }

            if current_user and is_first_time and _product_coupon_valid(product):
                try:
                    discount_pct = int(getattr(product, "discount_percentage", 0) or 0)
                    if discount_pct > 0:
                        discounted_unit = _apply_discounted_price(float(product.selling_price), discount_pct)
                        product_dict["discounted_price"] = round(discounted_unit, 2)
                        product_dict["coupon_code"] = product.coupon_code
                        product_dict["coupon_exp_days"] = product.coupon_exp_days
                        product_dict["discount_percentage"] = product.discount_percentage

                        if product.coupon_created_at and product.coupon_exp_days:
                            expires_at = product.coupon_created_at + timedelta(days=int(product.coupon_exp_days))
                            product_dict["coupon_expires_at"] = expires_at.isoformat()
                except Exception:
                    pass

            products_list.append(product_dict)

        return {
            "status": "success",
            "message": f"Retrieved {len(products_list)} products",
            "data": {
                "products": products_list,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total_count
            },
        }

    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving products: {str(e)}")

def get_product_by_id_service(session: Session, product_id: int):
    """
    Retrieve a single product by ID.
    
    Args:
        session: Database session
        product_id: ID of the product to retrieve
    
    Returns:
        Dictionary containing product data
    """
    try:
        product = session.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {
            "status": "success",
            "message": "Product retrieved successfully",
            "data": {
                "id": product.id,
                "name": product.name,
                "sku_id": product.sku_id,
                "hsn_code": product.hsn_code,
                "category": product.category,
                "mrp_price": product.mrp_price,
                "selling_price": product.selling_price,
                "key_features": product.key_features,
                "description": product.description,
                "images": product.images,
                "net_quantity": product.net_quantity,
                "colour": product.colour,
                "size": product.size,
                "height": product.height,
                "weight": product.weight,
                "width": product.width,
                "coupon_code": product.coupon_code,
                "coupon_exp_days": product.coupon_exp_days,
                "discount_percentage": product.discount_percentage,
                "created_by": product.created_by,
                "updated_by": product.updated_by,
                "created_at": product.created_at.isoformat() if product.created_at else None,
                "updated_at": product.updated_at.isoformat() if product.updated_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving product: {str(e)}")