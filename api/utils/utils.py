import json
from typing import Union, Optional

import flask

import logging

logger = logging.getLogger(__name__)

OptionalDataType = Union[dict, list, None]


def response(
    data: OptionalDataType = None, status: int = 200, mimetype: str = "application/json"
) -> flask.Response:
    if data is None and status == 204:
        return flask.Response(status=status)
    data = data or {}
    return flask.Response(json.dumps(data), status=status, mimetype=mimetype)


def not_found_response(data: OptionalDataType = None) -> flask.Response:
    data = data or {"error": "item not found"}

    return response(data, status=404)


def internal_error_response(data: OptionalDataType = None) -> flask.Response:
    data = data or {"error": "internal server error"}

    return response(data, status=500)


def success_response(data: OptionalDataType = None, message: Optional[str] = None) -> flask.Response:
    data = {"message": message} if message else (data or {"success": True})

    return response(data)
