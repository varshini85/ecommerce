from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from model.product import Product

def delete_product_service(session, current_user, product_id):
    """
    Delete a product by ID.
    
    Args:
        session: Database session
        product_id: ID of the product to delete
    
    Returns:
        Dictionary containing deletion confirmation
    """
    try:
        # Find the product by ID
        product = session.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Store product ID before deletion
        deleted_product_id = product.id
        
        # Delete the product
        session.delete(product)
        session.commit()
        
        return {
            "status": "success",
            "message": "Product deleted successfully",
            "product_id": deleted_product_id
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Error occurred: {str(e)}")