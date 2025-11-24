from typing import List, Optional
from sqlalchemy.orm import Session
from model.review import Review 

def get_reviews(db: Session, product_id: Optional[str] = None, skip: int = 0, limit: int = 50, include_deleted: bool = False) -> List[Review]:
    q = db.query(Review)
    if product_id:
        q = q.filter(Review.product_id == product_id)
    if not include_deleted:
        q = q.filter(Review.is_deleted == False)
    q = q.order_by(Review.created_at.desc()).offset(skip).limit(limit)
    return q.all()