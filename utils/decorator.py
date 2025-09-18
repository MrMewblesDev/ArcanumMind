import functools
from errors import RepositoryError
import logging
from sqlalchemy.exc import SQLAlchemyError 

log = logging.getLogger(__name__)

def db_error_handler(func):
    """A decorator that wraps repository methods to handle SQLAlchemy errors and raise a custom RepositoryError instead."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError as e:

            repo_name = args[0].__class__.__name__
            func_name = func.__name__

            log.error("Database error occured when calling %s.%s: %s", repo_name, func_name, e, exc_info=True)
            raise RepositoryError(f"Database error in {repo_name}.{func_name}") from e
    return wrapper