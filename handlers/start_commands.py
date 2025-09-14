from aiogram import types, Router
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.exceptions import AiogramError

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import User

import logging

router = Router()

@router.message(CommandStart())
async def send_welcome(message: types.Message, session: AsyncSession):
    """
    Handler for the /start command.
    
    Checks if the user exists in the database. If not, adds the user.
    Sends a welcome message.
    """
    # Check if user exists
    stmt = select(User).where(User.telegram_id == message.from_user.id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    # If user does not exist, create a new one
    if user is None:
        new_user = User(telegram_id=message.from_user.id)
        session.add(new_user)
        await session.commit()
        await message.answer(
            f"<b>Привет</b>, {message.from_user.full_name}! Меня зовут <u>ArcanumMind</u> (сокращенно Арканум). \nВведи /help для большей информации.",
            parse_mode=ParseMode.HTML
        )
    else:
        await message.answer(
            f"<b>С возвращением</b>, {message.from_user.full_name}! Чем могу помочь?",
            parse_mode=ParseMode.HTML
        )
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
        logging.error(f"Failed to send help message (user_id={message.from_user.id}): {e}")