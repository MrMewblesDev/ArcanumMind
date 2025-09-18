import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import User
from utils.decorator import db_error_handler

log = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, session: AsyncSession):
        """Initializes the UserRepository with a database session."""
        self.session = session

    @db_error_handler
    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Gets a user by their Telegram ID.
        
        Returns:
            User: The user object if found, None otherwise.
        """
        log.debug("Getting user with Telegram ID: %s", telegram_id)

        stmt = select(User).where(User.telegram_id == telegram_id)
        user = await self.session.scalar(stmt)

        if user:
            log.debug("User with Telegram ID %s found (ID: %s).", telegram_id, user.id)
        else:
            log.debug("User with Telegram ID %s not found.", telegram_id)
        return user
    @db_error_handler
    async def create(self, telegram_id: int, full_name: str, username: str | None = None) -> User:
        """
        Creates a new user and ADDS them to the session.
        Does NOT commit the transaction.

        Returns:
            User: The created user object.
        """
        log.debug("Creating user with Telegram ID: %s", telegram_id)
        new_user = User(telegram_id=telegram_id, full_name=full_name, username=username)
        self.session.add(new_user)
        log.debug("User with Telegram ID %s added to the session.", new_user.telegram_id)
        return new_user
    @db_error_handler
    async def delete(self, user: User) -> None:
        """
        Marks a user object for deletion.
        Does NOT commit the transaction.
        """
        log.info("Marking user for deletion: %s", user)

        self.session.delete(user)
        
        log.debug("User %s marked for deletion in the session.", user)