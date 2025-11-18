from datetime import datetime
from fastapi import HTTPException
from model.product import Product
from sqlalchemy.exc import SQLAlchemyError

def add_product_service(request, current_user, session):
    try:
        # Create new product instance with data from request
        new_product = Product(
            name=request.name,
            sku_id=request.sku_id,
            hsn_code=request.hsn_code,
            category=request.category,
            coupon_code=request.coupon_code,
            coupon_exp_days=request.coupon_exp_days,
            discount_percentage=request.discount_percentage,
            coupon_created_at= datetime.now() if request.coupon_code else None,
            mrp_price=request.mrp_price,
            selling_price=request.selling_price,
            key_features=request.key_features,
            net_quantity=request.net_quantity,
            colour=request.colour,
            size=request.size,
            height=request.height,
            weight=request.weight,
            width=request.width,
            description=request.description,
            images=request.images,
        )
        
        # Add to session and commit
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
            }
        }
        
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Error occurred: {str(e)}")
