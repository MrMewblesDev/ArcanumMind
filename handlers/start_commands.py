import logging
from aiogram import types, Router
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.exceptions import AiogramError

from sqlalchemy.ext.asyncio import AsyncSession # for type hinting
from sqlalchemy.exc import OperationalError

from repositories.UserRepository import UserRepository

log = logging.getLogger(__name__)

router = Router()

@router.message(CommandStart())
async def send_welcome(message: types.Message, session: AsyncSession):
    """
    Handler for the /start command.
    
    Checks if the user exists in the database. If not, adds the user.
    Sends a welcome message.
    """
    log.debug("Handling /start command from user %s", message.from_user.id)
    # Check if user exists
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)

    # If user does not exist, create a new one
    if user is None:
        await user_repo.create(
            telegram_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username
        )
        welcome_answer = (
            f"<b>Привет</b>, {message.from_user.full_name}! \n"
            "Меня зовут <u>ArcanumMind</u> (сокращенно Арканум). \n"
            "Введи /help для большей информации.")
    else: # User exists
        welcome_answer = (f"<b>С возвращением</b>, {message.from_user.full_name}! Чем могу помочь?")
    try:
        await session.commit()
        await message.answer(welcome_answer, parse_mode=ParseMode.HTML)
    except AiogramError as e:
        log.error("Failed to send welcome message (user_id=%s): %s", 
                  message.from_user.id, e, exc_info=True)
        await message.answer("Произошла ошибка при отправке приветственного сообщения. Пожалуйста, попробуйте ещё раз.")
        return
    except (OperationalError, Exception) as e:
        log.critical("Failed to commit session (user_id=%s): %s", message.from_user.id, e, exc_info=True)
        await message.answer("Произошла ошибка при работе с базой данных. Пожалуйста, попробуйте ещё раз.")
        return

@router.message(Command("help"))
async def send_help(message: types.Message):
    """Send a help message when the command /help is used."""
    text = (
        "<b>Доступные команды:</b>\n"
        "/start - Запустить бота и получить приветственное сообщение.\n"
        "/help - Показать это сообщение помощи.\n"
        "/ask &ltтекст&gt - Задать вопрос боту.\n\n"
        "<i>Пример:</i> /ask Какой сегодня день?"
    )
    try:
        # Send the help message
        await message.answer(
            text,
            parse_mode=ParseMode.HTML
        )
    except AiogramError as e:
        # Log any errors that occur while sending the message
        log.error("Failed to send help message (user_id=%s): %s", 
                  message.from_user.id, e, exc_info=True)
        await message.answer("Произошла ошибка при отправке помощи. Пожалуйста, попробуйте ещё раз.")
    except Exception as e:
        log.critical("Unexpected error when sending help message (user_id=%s): %s", 
                     message.from_user.id, e, exc_info=True)
        await message.answer("Произошла непредвиденная ошибка при отправке помощи. Мы уже работаем над её устранением. "
                             "Пожалуйста, попробуйте ещё раз.")
