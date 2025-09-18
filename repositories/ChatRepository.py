import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database import Chat
from utils.decorator import db_error_handler

from errors import ChatNotFoundError

log = logging.getLogger(__name__)

class ChatRepository():
    def __init__(self, session: AsyncSession):
        self.session = session
    
    @db_error_handler
    async def create(self, user_id: int, chat_name: str, is_active: bool = True) -> Chat:
        """
        Creates a new chat and ADDS it to the session.
        Does NOT commit the transaction.

        Returns:
            Chat: The created chat object.
        """
        log.info("Creating chat for user with ID: %s", user_id)
        new_chat = Chat(user_id=user_id, chat_name=chat_name, is_active=is_active)
        self.session.add(new_chat)
        log.debug("Chat for user with ID %s added to the session.", new_chat.user_id)
        return new_chat
    @db_error_handler
    async def delete(self, chat: Chat) -> None:
        """
        Marks a chat object for deletion.
        Does NOT commit the transaction.
        """
        log.info("Marking chat for deletion: %s", chat)
        self.session.delete(chat)
        log.debug("Chat %s marked for deletion in the session.", chat)
    @db_error_handler
    async def get_chat_list(self, user_id: int) -> list[Chat]:
        """
        Returns a list of chats for a specific user.
        Returns an empty list if no chats are found.
        """
        log.info("Getting chat list for user with ID: %s", user_id)
        stmt = select(Chat).where(Chat.user_id == user_id)
        return await self.session.scalars(stmt).all()
    @db_error_handler
    async def get_by_id(self, chat_id: int) -> Chat:
        """Gets a chat by its database ID.

        Returns:
            Chat: The chat object if found.
        Raises:
            ChatNotFoundError: If the chat is not found.
        """
        log.info("Getting chat with ID: %s", chat_id)

        stmt = select(Chat).where(Chat.id == chat_id)
        result = await self.session.execute(stmt)
        chat = result.scalar_one_or_none()

        if not chat:
            log.error("Chat with ID %s not found.", chat_id)
            raise ChatNotFoundError(f"Chat with ID {chat_id} not found.")

        log.debug("Chat with ID %s found (ID: %s).", chat_id, chat.id)
        return chat
    @db_error_handler
    async def deactivate_chats(self, user_id: int) -> None:
        """Deactivates all chats for a specific user.
        Does NOT commit the transaction."""
        log.debug("Deactivating all chats for user with ID: %s", user_id)
        stmt = update(Chat).where(Chat.user_id == user_id, Chat.is_active).values(is_active=False)
        await self.session.execute(stmt)
            
    @db_error_handler
    async def get_active_chats(self, user_id: int) -> list[Chat]:
        """Returns a list of active chats for a specific user.
        
        Args:
            user_id (int): The ID of the user.

        Returns:
            list[Chat]: A list of Chat objects.
        """
        log.debug("Getting active chat list for user with ID: %s", user_id)
        stmt = select(Chat).where(Chat.user_id == user_id, Chat.is_active)
        active_chat_list = await self.session.scalars(stmt).all()
        return active_chat_list