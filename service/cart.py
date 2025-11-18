from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from model.product import Product        
from model.cart_items import CartItem, ACTIVE, CONVERTED, WISHLIST

def _fetch_active_items(db: Session, user_id: int):
    return (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id, CartItem.status == ACTIVE)
        .order_by(CartItem.id.asc())
        .all()
    )

def _find_active_line(db: Session, user_id: int, product_id: int):
    return (
        db.query(CartItem)
        .filter(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id,
            CartItem.status == ACTIVE,
        )
        .first()
    )

def _find_item_by_id(db: Session, user_id: int, item_id: int):
    return (
        db.query(CartItem)
        .filter(
            CartItem.id == item_id,
            CartItem.user_id == user_id,
            CartItem.status == ACTIVE,
        )
        .first()
    )

def _to_cart_out(user_id: int, items):
    return {
        "user_id": user_id,
        "status": "ACTIVE",
        "items": [
            {
                "id": i.id,
                "product_id": i.product_id,
                "name": i.product.name,
                "image": i.product.images[0],
                "quantity": i.quantity,
                "selling_price": i.unit_price,
                "line_total": i.line_total,
            }
            for i in items
        ],
        "grand_total": float(sum(float(i.line_total or 0.0) for i in items)),
    }