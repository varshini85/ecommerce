# service/items_update_simple.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from model.cart_items import CartItem, ACTIVE, WISHLIST

VALID_STATUSES = {ACTIVE, WISHLIST}


def update_item_by_product(
    user_id: int,
    product_id: int,
    quantity: int,
    db: Session,
):
    try:
        lines = (
            db.query(CartItem)
            .filter(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id,
            )
            .all()
        )

        if not lines:
            msg = "Cart item not found"
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{msg} for product_id={product_id}",
            )

        if quantity <= 0:
            for l in lines:
                db.delete(l)
        else:
            for l in lines:
                l.quantity = quantity
                l.line_total = l.quantity * float(l.unit_price)

        db.flush()
        db.commit()

        return {"msg": "Updated Successfully"}

    except HTTPException:
        raise
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating item",
        ) from e
