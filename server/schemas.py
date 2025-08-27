
from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MessageCreate(BaseModel):
    content: str

class MessageOut(BaseModel):
    id: int
    conversation_id: int
    sender_username: str
    content: str
    created_at: datetime
