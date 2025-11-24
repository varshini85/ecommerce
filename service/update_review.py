from sqlalchemy.orm import Session
from model.review import Review 
from schema.review_schema import ReviewUpdate

def update_review(db: Session, review: Review, updates: ReviewUpdate) -> Review:
    changed = False
    if updates.title is not None:
        review.title = updates.title
        changed = True
    if updates.comment is not None:
        review.comment = updates.comment
        changed = True
    if updates.rating is not None:
        review.rating = updates.rating
        changed = True
    if updates.images is not None:
        review.images = updates.images
        changed = True

    if changed:
        db.add(review)
        db.commit()
        db.refresh(review)
    return review
