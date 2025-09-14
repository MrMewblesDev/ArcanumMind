import asyncio
import logging as log

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


from handlers import start_commands, ai_commands
from config import load_config, load_logging
from services import gemini_service
import errors as err
from database import async_main as async_db_main
from middlewares.db_session_middleware import DbSessionMiddleware

async def main():

    """
    Main entry point of the bot.

    Loads configuration, initializes logging, sets up the bot and dispatcher, and starts polling.

    Raises:
        err.ConfigError: If the configuration is invalid.
    """

    # Load configuration and initialize logging
    config = await load_config()
    await load_logging(config["LOG_LEVEL"])
    log.info("Logging initialized.")

    # Initialize bot for polling
    log.debug("Initializing bot...")
    bot = Bot(token=config["BOT_TOKEN"])
    log.debug("Bot initialized.")

    # Initialize dispatcher for handling updates
    log.debug("Setting up dispatcher...")
    dp = Dispatcher()
    dp["config"] = config
    log.debug("Dispatcher initialized.")
    log.info("Dispatcher and bot initialized.")

    log.debug("Initializing database...")
    engine = create_async_engine(config["DB_URL"])
    session_pool = async_sessionmaker(engine, expire_on_commit=False)
    dp.update.middleware(DbSessionMiddleware(session_pool=session_pool))
    dp["engine"] = engine
    await async_db_main(engine)
    log.info("Database initialized.")

    log.debug("Initializing gemini...")
    gemini_client, gemini_model = await gemini_service.initialize_gemini(config)
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
    log.info("Bot started.")

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
        log.critical(f"Unexpected error: {e}")
        raise err.BotInitializationError(f"Bot failed to start due to an unexpected error: {e}")