import logging
import asyncio

from aiogram import Router
from aiogram import types
from aiogram.filters import Command, CommandObject
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter

from services.gemini_service import ask_gemini, GEMINI_ERROR_FLAG

from utils.split_message import split_message

# for type hinting:
from google import genai

router = Router()


async def loading_animation(message: types.Message):
    """Display a loading animation while the AI generates a response."""
    base_text = "Пожалуйста, подождите, генерируется ответ"
    dots = 1
    while True:
        try:
            dots = (dots + 1) % 4
            await message.edit_text(base_text + "." * dots)
            await asyncio.sleep(0.7)
        except Exception:
            break

@router.message(Command("ask"))
async def ask(message: types.Message, command: CommandObject, gemini_client: genai.Client, gemini_model: str):
    """
    Send a question to the AI and get the response. Does not have memory of previous questions."""
    
    if not command.args:
        await message.reply("Пожалуйста, введите вопрос после команды.")
        return

    question = command.args
    TELEGRAM_SAFE_LIMIT = 4000
    edit_time = 0.8

    # Initialization
    text_in_current_msg = ""
    full_text_for_db = ""
    active_message = None
    animation_task = None 

    response_stream = ask_gemini(question, gemini_client, gemini_model)
    is_first_chunk = True

    # Main loop
    try:
        active_message = await message.reply("Пожалуйста, подождите...")
        animation_task = asyncio.create_task(loading_animation(active_message))

        async for chunk in response_stream:
            if is_first_chunk:
                animation_task.cancel()
                is_first_chunk = False

            if chunk == GEMINI_ERROR_FLAG:
                await active_message.edit_text("Произошла ошибка...")
                break

            full_text_for_db += chunk

            # Logic for splitting
            if len(text_in_current_msg) + len(chunk) > TELEGRAM_SAFE_LIMIT:

                parts = split_message(text_in_current_msg + chunk, TELEGRAM_SAFE_LIMIT)
                final_text_for_old_msg = parts[0]
                start_text_for_new_msg = parts[1]

                await active_message.edit_text(final_text_for_old_msg)

                active_message = await message.answer(start_text_for_new_msg)
                text_in_current_msg = start_text_for_new_msg
            else:
                text_in_current_msg += chunk
                if text_in_current_msg.strip() != active_message.text.strip():
                    await active_message.edit_text(text_in_current_msg)

            await asyncio.sleep(edit_time)
            
    except TelegramRetryAfter as e:
        logging.warning(f"Flood limit. Sleeping for {e.retry_after}s.")
        await asyncio.sleep(e.retry_after)
    except TelegramBadRequest as e:
        logging.warning(f"Ignoring bad request: {e}")
    except Exception as e:
        logging.error(f"Critical error in stream loop: {e}", exc_info=True)
        if animation_task and not animation_task.done():
            animation_task.cancel()
        if active_message:
            await active_message.edit_text("Произошла критическая ошибка.")
    
    # Saving into db in the future

