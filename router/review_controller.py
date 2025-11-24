# routers/reviews.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from schema.review_schema import ReviewCreate, ReviewOut, ReviewUpdate
from service.create_review import (
    create_review,
    get_review_by_id
)
from service.get_review import get_reviews
from service.update_review import update_review
from service.delete_review import delete_review
from database.db_session import get_session
from utils.jwt import get_current_user 
from model.user import User  

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create(
    review_in: ReviewCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return create_review(db, current_user.id, review_in)
    


@router.get("/", response_model=List[ReviewOut])
def list_reviews(
    product_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    include_deleted: bool = Query(False),
    db: Session = Depends(get_session),
):
    return get_reviews(db, product_id=product_id, skip=skip, limit=limit, include_deleted=include_deleted)


@router.put("/{review_id}", response_model=ReviewOut)
def update(
    review_id: int,
    updates: ReviewUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    review = get_review_by_id(db, review_id)
    if not review or review.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    if review.user_id != current_user.id and not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this review.")

    return update_review(db, review, updates) 


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    review_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    review = get_review_by_id(db, review_id)
    if not review or review.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    if review.user_id != current_user.id and not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this review.")

    return delete_review(db, review)
    
