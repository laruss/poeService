import json
from os.path import basename
from typing import Union

import flask


import os
import logging

logger = logging.getLogger(__name__)


def ensure_directories_exist(path: str) -> None:
    """ method creates directories if they don't exist """
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            logger.info(f"Directory(s) '{path}' successfully created.")
        except Exception as e:
            logger.error(f"Failed to create directory(s) '{path}'. Error: {e}")
    else:
        logger.info(f"Directory(s) '{path}' already exists.")


def open_json(filepath: str) -> Union[dict, list]:
    """ method opens json file """
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data


def save_json(filepath: str, data: Union[dict, list]):
    """ method saves json file """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_module_name(module: str) -> str:
    """ method returns module name without an extension"""
    return basename(module).split('.')[-1]


def response(
    data: dict = None, status: int = 200, mimetype: str = "application/json"
) -> flask.Response:
    if data is None and status == 204:
        return flask.Response(status=status)
    data = data or {}
    return flask.Response(json.dumps(data), status=status, mimetype=mimetype)


def not_found_response(data: dict = None) -> flask.Response:
    data = data or {"error": "item not found"}

    return response(data, status=404)


def internal_error_response(data: dict = None) -> flask.Response:
    data = data or {"error": "internal server error"}

    return response(data, status=500)


def success_response(
    data: Union[dict, list] = None, message: str = None
) -> flask.Response:
    data = {"message": message} if message else (data or {"success": True})

    return response(data)
