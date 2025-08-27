
from sqlmodel import Session, select
from models import User, Conversation, ConversationMember, Message
from auth import hash_password
from typing import Optional

def get_user_by_username(session: Session, username: str) -> Optional[User]:
    return session.exec(select(User).where(User.username == username)).first()

def create_user(session: Session, username: str, password: str) -> User:
    user = User(username=username, password_hash=hash_password(password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_or_create_1to1_conversation(session: Session, username_a: str, username_b: str) -> Conversation:
    a = get_user_by_username(session, username_a)
    b = get_user_by_username(session, username_b)
    if not a or not b:
        raise ValueError("Both users must exist")
    # Buscar conversación con ambos miembros (exactamente dos)
    member_rows = session.exec(select(ConversationMember)).all()
    by_conv = {}
    for m in member_rows:
        by_conv.setdefault(m.conversation_id, set()).add(m.user_id)
    for cid, members in by_conv.items():
        if members == {a.id, b.id}:
            return session.get(Conversation, cid)
    # crear
    conv = Conversation()
    session.add(conv)
    session.commit()
    session.refresh(conv)
    session.add(ConversationMember(conversation_id=conv.id, user_id=a.id))
    session.add(ConversationMember(conversation_id=conv.id, user_id=b.id))
    session.commit()
    return conv

def save_message(session: Session, conversation_id: int, sender_id: int, content: str) -> Message:
    msg = Message(conversation_id=conversation_id, sender_id=sender_id, content=content)
    session.add(msg)
    session.commit()
    session.refresh(msg)
    return msg

def list_messages(session: Session, conversation_id: int, limit: int = 50):
    msgs = session.exec(select(Message).where(Message.conversation_id == conversation_id).order_by(Message.id.desc()).limit(limit)).all()
    msgs = list(reversed(msgs))
    users = {u.id: u.username for u in session.exec(select(User)).all()}
    out = []
    for m in msgs:
        out.append({
            "id": m.id,
            "conversation_id": m.conversation_id,
            "sender_username": users.get(m.sender_id, f"u{m.sender_id}"),
            "content": m.content,
            "created_at": m.created_at.isoformat()
        })
    return out

def list_conversations(session: Session, user_id: int):
    member_rows = session.exec(select(ConversationMember)).all()
    my_convs = [m.conversation_id for m in member_rows if m.user_id == user_id]
    users = {u.id: u.username for u in session.exec(select(User)).all()}
    out = []
    for cid in my_convs:
        members = [m.user_id for m in member_rows if m.conversation_id == cid]
        peer_ids = [i for i in members if i != user_id]
        peer = users.get(peer_ids[0]) if peer_ids else None
        last = session.exec(select(Message).where(Message.conversation_id == cid).order_by(Message.id.desc()).limit(1)).first()
        out.append({
            "conversation_id": cid,
            "peer": peer,
            "last": last.content if last else None,
            "last_at": last.created_at.isoformat() if last else None
        })
    return out
