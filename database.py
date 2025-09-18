from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, func, Enum
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.asyncio import AsyncEngine # for type hinting
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text

import enum
import logging as log

Base = declarative_base()

async def configure_db_component(DB_URL: str):
    """Configures a database engine and session maker for SQLAlchemy.

    Args:
        DB_URL (str): The connection string for the database.
        echo_mode (bool, optional): Sets the echo mode for the database. Defaults to False.

    Returns:
        tuple (AsyncEngine, async_sessionmaker): A tuple containing the database engine and session maker.
    """
    log.info("Initializing database engine and session maker...")
    if "sqlite" in DB_URL:
        engine = create_async_engine(DB_URL, 
                                    echo = False,
                                    connect_args={"check_same_thread": False})
        log.debug("Successfully configured SQLite database engine. Database URL: %s", DB_URL)
    else:
        engine = create_async_engine(DB_URL, echo = False)
        log.debug("Successfully configured non-SQLite database engine. Database URL: %s", DB_URL)

    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    log.debug("Successfully configured session maker")
    log.info("Successfully configured database engine and session maker with DB URL: %s", DB_URL)

    return engine, session_maker

async def check_db_connection(engine: AsyncEngine) -> bool:
    """Checks the database connection and returns True if successful, False otherwise."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except OperationalError as e:
        log.error("Database connection failed. Please check your credentials, hostname and server status.")
        log.error("Underlying error details: %s", e)
        return False
    except Exception as e:
        log.error("Unexpected error while checking database connection: %s", e)
        return False

# Enum for Message roles, ensuring data integrity.
class MessageRole(enum.Enum):
    USER = "user"
    MODEL = "model"

class User(Base):
    """
    Represents a unique individual interacting with the bot.

    This table stores the user's core information from Telegram and acts as
    the central anchor for all their associated data, like chats and messages.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    username = Column(String, default=None, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"User(id={self.id}, telegram_id={self.telegram_id}, full_name={self.full_name}, username={self.username})"
    
class Chat(Base):
    """
    Represents a single, logical conversation thread with the AI.

    Each user can have multiple chat sessions, allowing for different
    context-aware conversations to happen in parallel.
    """
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Chat(id={self.id}, chat_name={self.chat_name}, is_active={self.is_active}, created_at={self.created_at})"

class Message(Base):
    """
    Represents a single message within a Chat session.

    This stores the turn-by-turn history of a conversation, capturing both
    the user's prompts and the AI's responses via the 'role' column.
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    telegram_message_id = Column(Integer, unique=True, nullable=False)
    role = Column(Enum(MessageRole, name="message_role_enum"), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    user = relationship("User", back_populates="messages")
    chat = relationship("Chat", back_populates="messages")


    def __repr__(self):
        truncated_content = (self.content[:30] + '...') if len(self.content) > 30 else self.content
        return f"Message(id={self.id}, role='{self.role.value}', chat_id={self.chat_id}, telegram_message_id={self.telegram_message_id}, content='{truncated_content}')"
    
async def create_tables(engine):
    """An asynchronous function that creates all tables in the database.

    Args:
        engine (AsyncEngine): The engine used to connect to the database.
    """
    log.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("Successfully created database tables.")