from datetime import datetime
from typing import Iterable, List
from sqlalchemy.orm import Session
from model.cart_items import CartItem, ACTIVE, CONVERTED

from typing import List

def parse_int_list(values_str: str) -> List[int]:
    result: List[int] = []

    if not values_str:
        return result

    for token in str(values_str).split(","):
        token = token.strip()
        if not token:
            continue

        try:
            result.append(int(token))
        except ValueError:
            continue

    return result


def convert_cart_items_for_user(
    db: Session,
    user_id: int,
    paid_product_ids: Iterable[int]
) -> List[int]:

    updated_item_ids: List[int] = []

    if not paid_product_ids:
        return updated_item_ids

    product_ids = [int(pid) for pid in set(paid_product_ids) if pid is not None]

    if not product_ids:
        return updated_item_ids

    cart_items = (
        db.query(CartItem)
        .filter(
            CartItem.user_id == user_id,
            CartItem.status == ACTIVE,
            CartItem.product_id.in_(product_ids),
        )
        .all()
    )

    now = datetime.utcnow()

    for item in cart_items:
        item.status = CONVERTED
        item.updated_at = now
        updated_item_ids.append(item.id)

    return updated_item_ids
