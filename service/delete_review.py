from sqlalchemy.orm import Session
from model.review import Review 

def delete_review(db: Session, review: Review) -> None:
    review.is_deleted = True
    db.add(review)
    db.commit()