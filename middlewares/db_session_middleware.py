from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker
import logging

log = logging.getLogger(__name__)

class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_maker: async_sessionmaker):
        """
        Initialize the middleware with a session factory.

        Args:
            session_maker (async_session_maker): A factory for creating asynchronous database sessions.

        """
        self.session_maker = session_maker
        log.info("Database session middleware initialized.")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Calls the given handler with the given event and data after creating a database session.

        The session is added to the data dictionary under the key "session". The handler is then called with the event and the updated data.

        Exception handling:
            If an exception occurs during the execution of the handler, the session is rolled back.

        Args:
            handler (Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]]): The handler to call.
            event (TelegramObject): The event to pass to the handler.
            data (Dict[str, Any]]): The data to pass to the handler.

        Returns:
            Any: The result of calling the handler.
        """
        update_id = data["update_id"]

        log.info("Creating database session for update ID %s...", update_id)
        # Create a database session
        async with self.session_maker() as session:
            # Add the session to the data
            data["session"] = session
            try: 
                result = await handler(event, data)
                log.debug("Successfully executed handler with update ID %s.", update_id)
                return result
            except Exception as e:
                log.critical("Failed to commit session (update_id=%s): %s", update_id, e, exc_info=True)
                await session.rollback()
                raise