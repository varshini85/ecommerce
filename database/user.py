from model.user import User
from fastapi.exceptions import HTTPException
from sqlalchemy import update,select
from sqlalchemy import Table
from sqlalchemy import *
from sqlalchemy.orm import *

def get_user_details(session,filters):
    # fetch user details
    try:
        user_details = session.query(User).filter_by(**filters).first()
        session.close()
        return user_details
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error Occurred")

def get_all_user_details(session,filters):
    # fetch user details
    try:
        user_details = session.query(User).filter_by(**filters).all()
        session.close()
        return user_details
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error Occurred")

def update_user_details(session,filters,data_to_be_updated):
    # update user details
    try:
        user_details=session.query(User).filter_by(**filters).update(data_to_be_updated)
        session.commit()
        session.close()
        return user_details
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error Occurred")
    
def get_user_info(session,user_id,filters):
    # verifing contact details
    try:
        user_details = session.query(User).filter(User.id != user_id).filter_by(**filters).first()
        session.close()
        return user_details
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error Occurred")

def get_user_email(session,filters):
    # fetch user details
    try:
        user_details = session.query(User.email).filter_by(**filters).first()
        session.close()
        if user_details:
            return user_details[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error Occured")
