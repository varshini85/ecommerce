# services/items_add_merged.py
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from model.product import Product
from model.cart_items import CartItem, ACTIVE, WISHLIST
from service.cart import _find_active_line

VALID_STATUSES = {ACTIVE, WISHLIST}

def add_item_or_wishlist(
    user_id: int,
    product_id: int,
    db: Session,
    status_str: str = ACTIVE,
    quantity: Optional[int] = None,
) -> dict:
    status_norm = (status_str or ACTIVE).upper()
    if status_norm not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status",
        )

    if status_norm == ACTIVE:
        if quantity is None or quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be > 0",
            )

        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        unit_price = float(product.selling_price)

        existing = _find_active_line(db, user_id, product_id)
        if existing:
            return {
                "message": "already in cart",
                "status": ACTIVE,
                "item": {
                    "id": existing.id,
                    "product_id": existing.product_id,
                    "quantity": existing.quantity,
                    "unit_price": float(existing.unit_price),
                    "line_total": float(existing.line_total),
                },
            }

        target_line = CartItem(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            line_total=unit_price * quantity,
            status=ACTIVE,
        )
        db.add(target_line)

        db.flush()
        try:
            db.commit()
        except Exception as e:
            try:
                db.rollback()
            except Exception:
                pass
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add item to cart",
            ) from e

        db.refresh(target_line)
        return {
            "message": "added to cart",
            "status": ACTIVE,
            "item": {
                "id": target_line.id,
                "product_id": target_line.product_id,
                "quantity": target_line.quantity,
                "unit_price": float(target_line.unit_price),
                "line_total": float(target_line.line_total),
            },
        }

    # WISHLIST flow
    existing_w = (
        db.query(CartItem)
        .filter(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id,
            CartItem.status == WISHLIST,
        )
        .first()
    )
    if existing_w:
        return {
            "message": "already in wishlist",
            "status": WISHLIST,
            "item": {
                "id": existing_w.id,
                "product_id": existing_w.product_id,
                "quantity": existing_w.quantity,
                "unit_price": float(existing_w.unit_price or 0.0),
                "line_total": float(existing_w.line_total or 0.0),
            },
        }

    item = CartItem(
        user_id=user_id,
        product_id=product_id,
        quantity=1,
        unit_price=0.0,
        line_total=0.0,
        status=WISHLIST,
    )
    db.add(item)
    db.flush()
    try:
        db.commit()
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to wishlist",
        ) from e

    db.refresh(item)

    return {
        "message": "added to wishlist",
        "status": WISHLIST,
        "item": {
            "id": item.id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": 0.0,
            "line_total": 0.0,
        },
    }
