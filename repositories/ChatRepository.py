import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from database import Chat

from errors import RepositoryError, ChatNotFoundError

log = logging.getLogger(__name__)

class ChatRepository():
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user_id: int, chat_name: str, is_active: bool = True) -> Chat:
        """
        Creates a new chat and ADDS it to the session.
        Does NOT commit the transaction.

        Returns:
            Chat: The created chat object.
        """
        log.debug("Creating chat for user with ID: %s", user_id)
        new_chat = Chat(user_id=user_id, chat_name=chat_name, is_active=is_active)
        self.session.add(new_chat)
        log.debug("Chat for user with ID %s added to the session.", new_chat.user_id)
        return new_chat
    async def delete(self, chat: Chat) -> None:
        """
        Marks a chat object for deletion.
        Does NOT commit the transaction.
        """
        log.debug("Marking chat for deletion: %s", chat)

        await self.session.delete(chat)
        
        log.debug("Chat %s marked for deletion in the session.", chat)
    async def get_chat_list(self, user_id: int) -> list[Chat]:
        """
        Returns a list of chats for a specific user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list[Chat]: A list of Chat objects.
        """
        log.debug("Getting chat list for user with ID: %s", user_id)
        stmt = select(Chat).where(Chat.user_id == user_id)
        return await self.session.scalars(stmt).all()
    async def get_by_id(self, chat_id: int) -> Chat | None:
        """Gets a chat by its database ID.

        Returns:
            Chat | None: The chat object if found, None otherwise.
        """
        log.debug("Getting chat with ID: %s", chat_id)

        stmt = select(Chat).where(Chat.id == chat_id)
        chat = await self.session.scalar(stmt).one_or_none()

        if chat:
            log.debug("Chat with ID %s found (ID: %s).", chat_id, chat.id)
        else:
            log.debug("Chat with ID %s not found.", chat_id)
        return chat
    async def deactivate_chats(self, user_id: int):
        """Deactivates all chats for a specific user.
        
        Args:
            user_id (int): The ID of the user.
        Returns:
            Bool: True if successful, False otherwise."""
        log.debug("Deactivating all chats for user with ID: %s", user_id)
        stmt = update(Chat).where(Chat.user_id == user_id, Chat.is_active).values(is_active=False)
        await self.session.execute(stmt)
            
    async def get_active_chats(self, user_id: int) -> list[Chat]:
        """Returns a list of active chats for a specific user.
        
        Args:
            user_id (int): The ID of the user.

        Returns:
            list[Chat]: A list of Chat objects.
        """
        log.debug("Getting active chat list for user with ID: %s", user_id)
        stmt = select(Chat).where(Chat.user_id == user_id, Chat.is_active)
        try:
            active_chat_list = await self.session.scalars(stmt).all()
            return active_chat_list
        except SQLAlchemyError as e:
            log.error("Error while fetching active chat list for user with ID %s: %s", user_id, e)
            raise RepositoryError("Error while fetching active chat list for user with ID %s:", user_id) from e
