from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func

from model.product import Product
from model.cart_items import CartItem, ACTIVE, WISHLIST, CONVERTED
from model.orders import Order
from model.cart_items import CartItem as CartItemModel
from service.cart import _fetch_active_items
from service.discount import is_first_time_user, _product_coupon_valid, _apply_discounted_price

VALID_STATUSES = {ACTIVE, WISHLIST, CONVERTED}


def get_items_by_status(user_id: int, db: Session, status_str: str = ACTIVE, coupon_code: Optional[str] = None) -> dict:
    status_norm = (status_str or ACTIVE).upper()
    if status_norm not in VALID_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")

    first_time = is_first_time_user(db, user_id)

    if status_norm == ACTIVE:
        items = _fetch_active_items(db, user_id)
    else:
        items = (
            db.query(CartItem)
            .options(selectinload(CartItem.product))
            .filter(CartItem.user_id == user_id, CartItem.status == status_norm)
            .order_by(CartItem.created_at.desc())
            .all()
        )

    out_items = []
    for it in items:
        prod = it.product
        qty = int(it.quantity or 0)

        item_out = {
            "id": it.id,
            "product_id": it.product_id,
            "name": prod.name if prod else None,
            "image": (prod.images[0] if prod and getattr(prod, "images", None) else None),
            "quantity": qty,
            "selling_price": prod.selling_price,
            "discounted_price": None,
        }

        try:
            if prod and first_time and _product_coupon_valid(prod):
                discount_pct = int(getattr(prod, "discount_percentage", 0) or 0)
                if discount_pct > 0:
                    discounted_unit = _apply_discounted_price(prod.selling_price, discount_pct)
                    item_out["discounted_price"] = round(discounted_unit, 2)
        except Exception:
         
            pass

        if status_norm != WISHLIST:
            line_total = (prod.selling_price * qty) if prod else 0
            item_out["line_total"] = line_total
            item_out["discounted_line_total"] = None

            if item_out.get("discounted_price") is not None:
                item_out["discounted_line_total"] = round(item_out["discounted_price"] * qty, 2)

        out_items.append(item_out)

    if status_norm != WISHLIST:
        grand_total = round(sum(i.get("line_total", 0.0) for i in out_items), 2)
        grand_after_discount = round(
            sum(
                float(
                    i.get("discounted_line_total")
                    if i.get("discounted_line_total") is not None
                    else i.get("line_total", 0.0)
                )
                for i in out_items
            ),
            2,
        )
    else:
        grand_total = None
        grand_after_discount = None

    response = {
        "user_id": user_id,
        "status": status_norm,
        "items": out_items,
    }

    if status_norm != WISHLIST:
        response["grand_total"] = grand_total
        response["grand_total_after_discount"] = grand_after_discount

    return response
