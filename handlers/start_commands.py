from aiogram import types, Router
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.exceptions import AiogramError

import logging

router = Router()

@router.message(CommandStart())
async def send_welcome(message: types.Message):
    """
    Send a welcome message when the command /start is issued.

    This function will send a welcome message to the user when the command /start is used.
    """
    text = (
        "<b>Привет</b>! Меня зовут <u>ArcanumMind</u> (сокращенно Арканум). \nВведи /help для большей информации."
    )
    try:
        # Send the welcome message
        await message.answer(
            text,
            parse_mode=ParseMode.HTML
        )
    except AiogramError as e:
        # Log any errors that occur while sending the message
        logging.error(f"Failed to send welcome message (user_id={message.from_user.id}): {e}")

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