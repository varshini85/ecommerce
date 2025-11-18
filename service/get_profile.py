# services/get_profile_service.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from model.user import User

def get_user_profile(db: Session, user_id: int) -> User:
  
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:    
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")

        if getattr(user, "addresses", None) is None:
            user.addresses = []

        return user

    except SQLAlchemyError as sqle:
        try:
            db.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while fetching profile") from sqle
   