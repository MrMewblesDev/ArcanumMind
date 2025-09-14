from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker

class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        """
        Initialize the middleware with a session factory.

        Args:
            session_pool (async_session_maker): A factory for creating asynchronous database sessions.

        """
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Calls the given handler with the given event and data after creating a database session.

        The session is added to the data dictionary under the key "session". The handler is then called with the event and the updated data.

        Args:
            handler (Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]]): The handler to call.
            event (TelegramObject): The event to pass to the handler.
            data (Dict[str, Any]]): The data to pass to the handler.

        Returns:
            Any: The result of calling the handler.
        """
        # Create a database session
        async with self.session_pool() as session:
            # Add the session to the data
            data["session"] = session
            return await handler(event, data)