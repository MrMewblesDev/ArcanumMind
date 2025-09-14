# "create_async_engine" is a function needed for the database connection
# "AsyncSession" is a class needed for the database session, which is used to interact with the database
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Here we import all the necessary classes and functions from the "sqlalchemy" library
from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, func
)
# "declarative_base" is a function that creates a base class for declarative models
# "relationship" is a function that creates a relationship between two models
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    telegram_id = Column(Integer, unique=True, nullable=False)

    def __repr__(self):
        return f"User(id={self.id}, telegram_id={self.telegram_id})"
    
# class Chat(Base):
#     __tablename__ = "chats"

#     chat_id = Column(Integer, primary_key=True)

async def async_main(engine):
    """An asynchronous function that creates all tables in the database.

    Args:
        engine (AsyncEngine): The engine used to connect to the database.
    """

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)