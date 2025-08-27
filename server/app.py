
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Set
import json

from db import init_db, get_session
from sqlmodel import Session
from auth import create_access_token, get_current_user_ws, get_current_user_http, verify_password
from crud import create_user, get_user_by_username, get_or_create_1to1_conversation, save_message, list_messages, list_conversations
from schemas import UserCreate, TokenResponse, MessageCreate
from models import User

app = FastAPI(title="Soluna Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

@app.on_event("startup")
def startup():
    init_db()

# Auth
@app.post("/auth/register", response_model=TokenResponse)
def register(payload: UserCreate, session: Session = Depends(get_session)):
    if get_user_by_username(session, payload.username):
        raise HTTPException(400, "Username already taken")
    user = create_user(session, payload.username, payload.password)
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)

@app.post("/auth/login", response_model=TokenResponse)
def login(payload: UserCreate, session: Session = Depends(get_session)):
    user = get_user_by_username(session, payload.username)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)

# REST chat
@app.get("/conversations")
def my_conversations(current: User = Depends(get_current_user_http), session: Session = Depends(get_session)):
    return list_conversations(session, current.id)

@app.get("/conversations/{peer}/history")
def history(peer: str, current: User = Depends(get_current_user_http), session: Session = Depends(get_session)):
    conv = get_or_create_1to1_conversation(session, current.username, peer)
    return {"conversation_id": conv.id, "messages": list_messages(session, conv.id)}

@app.post("/conversations/{peer}/send")
def send_http(peer: str, msg: MessageCreate, current: User = Depends(get_current_user_http), session: Session = Depends(get_session)):
    conv = get_or_create_1to1_conversation(session, current.username, peer)
    m = save_message(session, conv.id, current.id, msg.content)
    return {"ok": True, "id": m.id}

# WebSocket
room_connections: Dict[int, Set[WebSocket]] = {}

@app.websocket("/ws/{conversation_id}")
async def ws_endpoint(websocket: WebSocket, conversation_id: int):
    user = await get_current_user_ws(websocket)
    await websocket.accept()

    room = room_connections.setdefault(conversation_id, set())
    room.add(websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            content = data.get("content", "")
            with next(get_session()) as session:
                msg = save_message(session, conversation_id, user.id, content)
            payload = {"id": msg.id, "from": user.username, "content": msg.content, "ts": msg.created_at.isoformat()}
            dead = []
            for conn in list(room):
                try:
                    await conn.send_text(json.dumps(payload))
                except:
                    dead.append(conn)
            for d in dead:
                room.discard(d)
    except WebSocketDisconnect:
        room.discard(websocket)
