import dotenv
import os
import sys
import logging
from errors import ConfigError
from typing import Final 

dotenv.load_dotenv()

class Config():
    """Config class for storing environment variables."""
    def __init__(self):
        """Initializes and validates environment variables."""

        # Required environment variables
        self.BOT_TOKEN: Final[str] = self._get_required_env("BOT_TOKEN")
        self.GEMINI_API_KEY: Final[str] = self._get_required_env("GEMINI_API_KEY")

        # Optional environment variables
        self.LOG_LEVEL: Final[str] = os.getenv("LOG_LEVEL", "INFO").upper()
        self.GEMINI_MODEL: Final[str] = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.SHOW_TIME_IN_PROMPT: Final[bool] = os.getenv("SHOW_TIME_IN_PROMPT", "True").upper() == "TRUE"
        self.DB_URL: Final[str] = os.getenv("DB_URL", "sqlite+aiosqlite:///./arcanum.db")
        
        # Logging levels for third-party libraries
        self.AIOGRAM_LOG_LEVEL: Final[str] = os.getenv("AIOGRAM_LOG_LEVEL", "WARNING").upper()
        self.AIOSQLITE_LOG_LEVEL: Final[str] = os.getenv("AIOSQLITE_LOG_LEVEL", "WARNING").upper()

        self._validate()

    def _get_required_env(self, key: str) -> str:
        """Retrieves environment variables that are required for the application."""
        value = os.getenv(key)
        if not value:
            raise ConfigError(f"Environment variable {key} is missing or empty.")
        return value
    
    def _validate(self):
        """Performs validation checks on environment variables."""

        VALID_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.LOG_LEVEL not in VALID_LOG_LEVELS:
            raise ConfigError(f"Invalid log level: {self.LOG_LEVEL}. It must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL.")
        if self.AIOGRAM_LOG_LEVEL not in VALID_LOG_LEVELS:
            raise ConfigError(f"Invalid log level: {self.AIOGRAM_LOG_LEVEL}. It must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL.")
        if self.AIOSQLITE_LOG_LEVEL not in VALID_LOG_LEVELS:
            raise ConfigError(f"Invalid log level: {self.AIOSQLITE_LOG_LEVEL}. It must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL.")

    def setup_logging(self):
        """Sets up logging."""
        logging.basicConfig(
            level=self.LOG_LEVEL,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        # Set up logging
        log = logging.getLogger(__name__)

        logging.getLogger("aiogram").setLevel(self.AIOGRAM_LOG_LEVEL)
        log.info(f"Aiogram logging initialized at {self.AIOGRAM_LOG_LEVEL} level.")
        logging.getLogger("aiosqlite").setLevel(self.AIOSQLITE_LOG_LEVEL)
        log.info(f"Aiosqlite logging initialized at {self.AIOSQLITE_LOG_LEVEL} level.")
        
        log.info(f"Initialized logging at {self.LOG_LEVEL} level.")

try:
    config = Config()
except ConfigError as e:
    logging.basicConfig(
        level="CRITICAL",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logging.critical("ConfigError: %s", e)
    sys.exit(1)