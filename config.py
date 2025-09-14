import dotenv
import os
import logging
import errors as err

dotenv.load_dotenv()

async def load_config():
    try:
        config = {
            "BOT_TOKEN": os.getenv("BOT_TOKEN"),
            "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
            "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO").upper(),
            "GEMINI_MODEL": os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            "SHOW_TIME_IN_PROMPT": os.getenv("SHOW_TIME_IN_PROMPT", "False").lower() == "true",
            "DB_URL": os.getenv("DB_URL", "sqlite+aiosqlite:///./arcanum.db")
        }
    except os.error as e:
        print(f"Error: Failed to load configuration: {e}")
        return None 
    
    if not config:
        raise err.ConfigError("Configuration is empty or invalid.")
    elif not config["BOT_TOKEN"]:
        raise err.ConfigError("Environment variable BOT_TOKEN is missing. Bot cannot start without it.")
    elif not config["GEMINI_API_KEY"]:
        raise err.ConfigError("Environment variable GEMINI_API_KEY is missing. AI functions won't be available.")
    elif config["LOG_LEVEL"] not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] or not config["LOG_LEVEL"]:
        raise err.ConfigError("Environment variable LOG_LEVEL is invalid or missing. Logging will be disabled.")
    elif not config["GEMINI_MODEL"]:
        raise err.ConfigError("Environment variable GEMINI_MODEL is missing. AI functions won't be available.")
    elif config["SHOW_TIME_IN_PROMPT"] is None:
        raise err.ConfigError("Environment variable SHOW_TIME_IN_PROMPT is missing. AI functions won't be available.")
    elif config["DB_URL"] is None:
        raise err.ConfigError("Environment variable DB_URL is missing. Database won't be available.")
    return config

async def load_logging(log_level: str):
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logging.info(f"Initialized logging at {log_level} level.")


