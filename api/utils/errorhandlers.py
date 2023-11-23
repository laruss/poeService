import functools

import flask

from .exceptions import PoeConnectionError, PoeBotError
from .utils import not_found_response, response


def register_errorhandlers(app: flask.Flask):
    exc = 500 if app.config["DEBUG"] else Exception

    @app.errorhandler(404)
    def page_not_found(e):
        return not_found_response({"error": "route not found"})

    @app.errorhandler(exc)
    def internal_server_error(e):
        return response({"error": str(e)}, status=500)

    @app.errorhandler(415)
    def unsupported_media_type(e):
        return response({"error": "unsupported media type"}, status=415)


def handle_errors(func):
    @functools.wraps(func)
    def wrapper_error_handler(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PoeConnectionError as e:
            return response({"error": str(e)}, status=500)
        except PoeBotError as e:
            return response({"error": str(e)}, status=400)

    return wrapper_error_handler
