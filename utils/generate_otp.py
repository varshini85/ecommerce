from random import randint
from fastapi.exceptions import HTTPException


def generate_otp():
    try:
        otp = randint(100000, 999999)
        return otp
    except Exception as e:
        raise HTTPException(status_code=400, detail='Not able to generate OTP')