# routers/profile_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from model.user import User
from schema.profile_schema import UserProfileOut, UserProfileUpdate, AddressOut
from service.get_profile import get_user_profile
from service.update_profile import update_user_profile
from database.db_session import get_session      
from utils.jwt import get_current_user 

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/", response_model=UserProfileOut)
def read_profile(db: Session = Depends(get_session), current_user=Depends(get_current_user)):
    return get_user_profile(db=db, user_id=current_user.id)

@router.patch("/", response_model=UserProfileOut)
def update_my_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user: User = update_user_profile(db=db, user_id=current_user.id, payload=payload)
    return UserProfileOut(
        id=user.id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        addresses=[AddressOut(**a) for a in (user.addresses or [])],
    )