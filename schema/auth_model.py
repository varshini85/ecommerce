from pydantic import BaseModel,EmailStr
from typing import Optional

class AuthRequestDetails(BaseModel):
    email : EmailStr

class AuthLoginDetails(AuthRequestDetails):
    otp : int

class AuthResponseDetails(BaseModel):
    message : str

class Token(BaseModel):
    is_verified : bool
    jwt_token : str
    user_id: int | None = None
    name : str
    email: str

class AuthResponse(BaseModel):
    message: str
    access_token: Optional[str] = None

class SignupIn(BaseModel):
    email: EmailStr
    name: str
    phone : str
    password: str
    
class LoginIn(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordIn(BaseModel):
    email: EmailStr

class ForgotPasswordVerify(BaseModel):
    email: EmailStr
    otp: str
    
class NewPasswordIn(BaseModel):
    email: EmailStr
    new_password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    email: str
    message: str

class ResetPasswordIn(BaseModel):
    old_password: str
    new_password: str

class MessageOut(BaseModel):
    message: str