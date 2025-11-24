# services/create_reviews.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from fastapi import HTTPException, status
from model.review import Review 
from model.orders import Order 
import schema.review_schema as schemas

def has_purchased(db: Session, user_id: int, product_id: str) -> bool:
    prod_id = str(product_id).strip()

    q = (
        db.query(func.count())
        .filter(
            Order.user_id == user_id,
            func.upper(Order.status) == "PAID",
            func.concat(",", Order.product_id, ",").like(f"%,{prod_id},%")
        )
    )

    return q.scalar() > 0


def create_review(db: Session, user_id: int, review_in: schemas.ReviewCreate) -> Review:
   
    if not has_purchased(db, user_id, review_in.product_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot review this product.")

    exists = db.query(Review).filter(
        Review.user_id == user_id,
        Review.product_id == review_in.product_id,
        Review.is_deleted == False
    ).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already reviewed this product.")

    review = Review(
        user_id=user_id,
        product_id=review_in.product_id,
        title=review_in.title,
        comment=review_in.comment,
        rating=review_in.rating,
        images=review_in.images or [],
        is_verified_purchase=True  
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review



def delete_review(db: Session, review: Review) -> None:
    review.is_deleted = True
    db.add(review)
    db.commit()


def get_review_by_id(db: Session, review_id: int) -> Optional[Review]:
    return db.query(Review).filter(Review.id == review_id).first()