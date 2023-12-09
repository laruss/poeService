import functools
import logging

from flask import session, request, g
from typing import Callable

from api.utils.utils import response

logger = logging.getLogger(__name__)

API_TOKEN = 'api_token'


def api_token_is_set_wrapper(func: Callable):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not (session_id := request.headers.get('session-id')):
            return response({"error": "session-id is not set"}, 403)
        g.session_id = session_id

        return func(*args, **kwargs)

    return wrapper
