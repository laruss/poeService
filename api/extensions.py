import functools
import logging

from pydantic_mongo import PydanticMongo

mongo = PydanticMongo()


def autolog(custom_text: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logging.info(f"{custom_text}: enter in {func.__name__}")
            result = func(*args, **kwargs)
            logging.info(f"{custom_text}: exit from {func.__name__}")
            return result
        return wrapper
    return decorator
