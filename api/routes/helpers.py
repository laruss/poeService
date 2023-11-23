import functools
from typing import Callable

from api.models.settings import Settings
from api.utils.utils import response


def api_token_is_set_wrapper(func: Callable):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not bool(Settings.get().api_token):
            return response({"error": "poe api token is not set"}, 403)

        return func(*args, **kwargs)

    return wrapper
