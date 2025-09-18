class ConfigError(Exception):
    """Base exception for configuration-related errors."""
    pass

class BotInitializationError(Exception):
    """Base exception for bot initialization errors."""
    pass

class RepositoryError(Exception):
    """Base exception for repository-related errors."""
    pass

class ChatNotFoundError(RepositoryError):
    """Raises when a specific chat is not found."""
    pass
