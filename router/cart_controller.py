from fastapi import APIRouter, Depends, Query
from typing import Literal, Optional
from sqlalchemy.orm import Session
from database.db_session import get_session as get_db
from utils.jwt import get_current_user
from schema.cart_schema import CartOut, AddItemIn, UpdateItemIn, CheckoutResponse
from service.add_cart import add_item_or_wishlist
from service.clear_cart import delete_or_clear_items
from service.get_cart import get_items_by_status
from service.update_cart import update_item_by_product
from model.cart_items import ACTIVE, WISHLIST, CONVERTED

router = APIRouter(tags=["cart"])

@router.get("/getitems",response_model=CartOut,  response_model_exclude_none=True)
def get_items(
    status: Literal["ACTIVE", "WISHLIST", "CONVERTED"] = Query(default=ACTIVE, description=f"{ACTIVE} | {WISHLIST} | {CONVERTED}"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_items_by_status(current_user.id, db, status)

@router.post("/add")
def add_item(payload: AddItemIn,status_param: Literal["ACTIVE", "WISHLIST"] = ACTIVE,db: Session = Depends(get_db),current_user=Depends(get_current_user),):
    return add_item_or_wishlist(
        user_id=current_user.id,
        product_id=payload.product_id,
        db=db,
        status_str=status_param,
        quantity=payload.quantity,
    )

@router.patch("/updateitems")
def update_items(quantity: int, product_id: Optional[int] = Query(None, description="Product id (updates all ACTIVE rows for that product)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return update_item_by_product(
        db=db,
        user_id=current_user.id,
        product_id=product_id,
        quantity=quantity,
        )

@router.delete("/removeorclear")
def delete_items(
    status: Literal["ACTIVE", "WISHLIST", "CLEAR"] = Query(
        default=ACTIVE,
        description=f"{ACTIVE} | {WISHLIST} | CLEAR"
    ),
    product_id: Optional[int] = Query(
        None,
        description="Product ID to remove. Omit for CLEAR."
    ),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return delete_or_clear_items(
        user_id=current_user.id,
        db=db,
        status_str=status,
        product_id=product_id,
    )