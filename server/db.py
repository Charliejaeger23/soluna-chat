
from sqlmodel import SQLModel, create_engine, Session
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///soluna.db"

settings = Settings()
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

def init_db():
    from models import User, Conversation, ConversationMember, Message
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
