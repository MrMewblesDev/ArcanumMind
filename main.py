import asyncio
import logging
import sys
from functools import partial

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from handlers import start_commands, ai_commands
from config import config
from services import gemini_service
import errors as err
from database import configure_db_component, check_db_connection, create_tables
from middlewares.db_session_middleware import DbSessionMiddleware

log = logging.getLogger(__name__)

async def on_shutdown(dp: Dispatcher):
    """
    Shutdown handler for the bot. Disposes the database engine.

    Args:
        dp (Dispatcher): The dispatcher for the bot.
    """
    log.info("Shutting down bot...")
    engine = dp["engine"]
    if engine:
        await engine.dispose()
        log.info("Successfully disposed database engine.")

async def main():

    """
    Main entry point of the bot.
    Loads configuration, initializes logging, sets up the bot and dispatcher, and starts polling.
    """

    # Load configuration and initialize logging
    config.setup_logging()
    log.info("Logging initialized successfully.")

    # Initialize bot for polling
    log.debug("Initializing bot...")
    bot = Bot(token=config.BOT_TOKEN)
    log.debug("Bot initialized.")

    # Initialize dispatcher for handling updates
    log.debug("Setting up dispatcher...")
    dp = Dispatcher()
    dp["config"] = config
    dp.shutdown.register(partial(on_shutdown, dp))
    log.debug("Dispatcher initialized.")
    log.info("Dispatcher and bot initialized.")

    log.debug("Initializing database...")
    engine, session_maker = await configure_db_component(config.DB_URL)
    if not await check_db_connection(engine): # Making sure the database connection is working
        log.critical("Database connection failed. Check previous logs for details.")
        sys.exit(1)
    dp.update.middleware(DbSessionMiddleware(session_maker=session_maker))
    dp["engine"] = engine
    await create_tables(engine)
    log.info("Database initialized.")

    log.debug("Initializing gemini...")
    gemini_client, gemini_model = await gemini_service.initialize_gemini(config.GEMINI_API_KEY, config.GEMINI_MODEL)
    dp["gemini_client"] = gemini_client
    dp["gemini_model"] = gemini_model
    log.debug("Gemini initialized.")
    log.info("Depencies initialized and passed to Dispatcher.")

    log.debug("Setting up routers...")
    dp.include_router(start_commands.router)
    dp.include_router(ai_commands.router)
    log.info("Routers set up.")

    # Start polling
    log.debug("Deleting webhook...")
    await bot.delete_webhook(drop_pending_updates=True)
    log.debug("Webhook deleted.")

    log.debug("Setting default commands...")
    await set_default_commands(bot)
    log.debug("Default commands set.")

    log.debug("Starting polling bot...")
    await dp.start_polling(bot)

    log.info("Bot is shutting down...")

async def set_default_commands(bot: Bot):
    """
    Set default bot commands.

    Sets the default commands of the bot, which will be displayed in the Telegram chat.

    Args:
        bot (Bot): The bot instance.
    """
    # Define the default commands
    commands = [
        BotCommand(command="/start", description="Запустить бота."),
        BotCommand(command="/help", description="Показать помощь."),
        BotCommand(command="/ask", description="Спросите у ИИ любой вопрос.")
    ]

    # Set the default commands
    await bot.set_my_commands(commands)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        log.error(f"Bot stopped by user: {e}")
    except Exception as e:
        log.critical(f"Unexpected error: {e}", exc_info=True)
        raise err.BotInitializationError(f"Bot failed to start due to an unexpected error: {e}")