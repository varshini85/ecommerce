import time
from database.user import get_user_details
from utils.jwt import create_access_token
from schema.auth_model import Token
from fastapi import HTTPException

def verify_otp_for_email(email,otp,session):
    user_details = get_user_details(session, {'email': email.lower(), 'otp': otp})
    if user_details:

        # check otp_generated time is within 5 mins
        if round(time.time()) - user_details.otp_time <= 360:
            jwt_token = create_access_token({'id': user_details.id, 'email': user_details.email})
            Token.is_verified = True
            Token.jwt_token = jwt_token
            Token.user_id = user_details.id
            Token.name = user_details.name
            Token.email = user_details.email
            return Token
        else:
            Token.is_verified = False
            Token.jwt_token = ''
            Token.user_id = None
            Token.name = ''
            Token.email = ''
            return Token
    else:
        session.close()
        raise HTTPException(status_code=400,detail="Please enter the correct OTP")
