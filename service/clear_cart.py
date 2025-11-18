# service/items_delete_simple.py
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from model.cart_items import CartItem, ACTIVE, WISHLIST
from service.cart import _fetch_active_items, _to_cart_out

VALID_STATUSES = {"ACTIVE", "WISHLIST", "CLEAR"}


def delete_or_clear_items(
    user_id: int,
    db: Session,
    status_str: Optional[str] = None,
    product_id: Optional[int] = None,
):
    try:

        status_norm = (status_str or ACTIVE).upper()
        if status_norm not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # ---------- CASE 1: CLEAR ----------
        if status_norm == "CLEAR":
            if product_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CLEAR cannot be used with product_id."
                )

            deleted = (
                db.query(CartItem)
                .filter(CartItem.user_id == user_id, CartItem.status == ACTIVE)
                .delete(synchronize_session=False)
            )

            if deleted == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No active cart items found to clear"
                )

            try:
                db.commit()
            except Exception:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to clear cart"
                )

            active_items = _fetch_active_items(db, user_id)
            return _to_cart_out(user_id, active_items)

        if product_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing product_id for status={status_norm}. To clear all, use status=CLEAR."
            )

        deleted_count = (
            db.query(CartItem)
            .filter(
                CartItem.user_id == user_id,
                CartItem.status == status_norm,
                CartItem.product_id == product_id,
            )
            .delete(synchronize_session=False)
        )

        if deleted_count == 0:
            not_found = "Cart item not found" if status_norm == ACTIVE else "Wishlist item not found"
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{not_found} for product_id={product_id}."
            )

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete item(s) from {status_norm.lower()}"
            )

        return {"msg" : "Deleted Successfully"}

    except HTTPException:
        raise
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while deleting/clearing items"
        ) from e
