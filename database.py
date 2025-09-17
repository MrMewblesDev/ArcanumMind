from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, func
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.asyncio import AsyncEngine # for type hinting
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text

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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    telegram_id = Column(Integer, unique=True, nullable=False)

    def __repr__(self):
        return f"User(id={self.id}, telegram_id={self.telegram_id})"
    
# class Chat(Base):
#     __tablename__ = "chats"

async def create_tables(engine):
    """An asynchronous function that creates all tables in the database.

    Args:
        engine (AsyncEngine): The engine used to connect to the database.
    """
    log.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("Successfully created database tables.")