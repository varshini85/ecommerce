from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from model.product import Product
from schema.product_schemas import UpdateProduct
from datetime import datetime

def update_product_service(session, product_id, request, current_user):
    try:
        # Find the product by ID
        product = session.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        existing_db_images = []
        if product.images:
            if isinstance(product.images, list):
                existing_db_images = product.images
        # Update only the fields that are provided (not None)
        update_data = request.dict(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No data provided for update")
        
        kept_existing_images = []
        if request.existing_images:
            if isinstance(request.existing_images, list):
                if len(request.existing_images) == 1 and isinstance(request.existing_images[0], str):
                    kept_existing_images = [
                        img.strip() for img in request.existing_images[0].split(",") if img.strip()
                    ]
                else:
                    kept_existing_images = request.existing_images

        new_uploaded_images = request.images or []
        added_images = [img for img in new_uploaded_images if img not in existing_db_images]
        final_image_list = kept_existing_images + added_images
        update_data["images"] = final_image_list
        coupon_changed = False
        coupon_fields = ["coupon_code", "coupon_exp_days"]

        for field in coupon_fields:
            if field in update_data and getattr(product, field) != update_data[field]:
                coupon_changed = True
                break  # no need to check further if one changed

        # Update the product fields
        for field, value in update_data.items():
            if hasattr(product, field):
                setattr(product, field, value)
        
        if coupon_changed:
            product.coupon_created_at = datetime.utcnow()
        # Update the updated_at timestamp
        product.updated_at = datetime.utcnow()
        
        # Commit the changes
        session.commit()
        session.refresh(product)
        
        return {
            "status": "success",
            "message": "Product updated successfully",
            "product_id": product.id,
            "data": {
                "id": product.id,
                "name": product.name,
                "description": product.description
            }
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Error occurred: {str(e)}")