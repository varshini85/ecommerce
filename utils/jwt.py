# load env
from dotenv import load_dotenv
load_dotenv(override=True)

import os
import json
from datetime import datetime,timedelta
from typing import Union,Any, Dict, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database.db_session import get_session
from model.user import User

token_expiry_minutes=os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
algorithm=os.getenv('ALGORITHM')
secret_key=os.getenv('JWT_SECRET_KEY')
security = HTTPBearer(auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(subject:Union[str,Any],expires_delta:int=None)->str:
    if expires_delta is not None:
        expires_delta=datetime.utcnow()+expires_delta

    else:
        expires_delta=datetime.utcnow()+timedelta(minutes=int(token_expiry_minutes))

    to_encode={"exp":expires_delta,"sub":str(subject)}
    encoded_jwt=jwt.encode(to_encode,secret_key,algorithm)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token or expired")

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_session),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = credentials.credentials
    payload = decode_token(token)
    if payload:
            payload_data = payload.get('sub', '')
            data = json.loads(payload_data.replace("'", "\""))

    # if data.get('type') != "access":
    #     raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = data.get('id')
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_session),
) -> Optional[User]:
    if credentials is None:
        return None
    try:
        token = credentials.credentials
        payload = decode_token(token)
        if not payload:
            return None
        data = json.loads(payload.get("sub", "{}").replace("'", '"'))
        user_id = data.get("id")
        if not user_id:
            return None
        return db.query(User).filter(User.id == int(user_id)).first()
    except Exception:
        return None