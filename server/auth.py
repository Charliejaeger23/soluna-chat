
from fastapi import Depends, HTTPException, WebSocket, Header
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import Optional
from sqlmodel import Session

from db import get_session
from models import User

load_dotenv()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Settings(BaseSettings):
    JWT_SECRET: str = "changeme_supersecret"
    JWT_EXPIRE_MIN: int = 60 * 24 * 7
    ALLOWED_ORIGINS: str = "*"

settings = Settings()

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def hash_password(p):
    return pwd_context.hash(p)

def create_access_token(data: dict, expires_minutes: Optional[int] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes or settings.JWT_EXPIRE_MIN)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")

def decode_token(token: str):
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(401, "Invalid token")

def get_current_user_http(
    authorization:str = Header(default=None), 
    session: Session = Depends(get_session)
) -> User:
       if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Not authenticated")
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    user_id = int(payload.get("sub"))
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(401, "User not found")
    return user

async def get_current_user_ws(websocket: WebSocket, session: Session = Depends(get_session)) -> User:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401)
        raise HTTPException(401, "No token")
    payload = decode_token(token)
    user_id = int(payload.get("sub"))
    user = session.get(User, user_id)
    if not user:
        await websocket.close(code=4401)
        raise HTTPException(401, "User not found")
    return user
