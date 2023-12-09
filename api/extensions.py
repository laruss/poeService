from __future__ import annotations

import functools
import logging

from flask_pymongo import PyMongo
from poeagent.agent import PoeAgent

from api.utils.exceptions import PoeConnectionError

mongo = PyMongo()


class Poe:
    _agent: PoeAgent = None
    _token: str = None

    @property
    def agent(self) -> PoeAgent:
        if not self._agent:
            if not self._token:
                raise PoeConnectionError("Token is not set")
            self._agent = PoeAgent(self._token)

        return self._agent

    @property
    def is_connected(self) -> bool:
        return self._agent and self._agent.is_connected

    def connect(self, token: str = None) -> Poe:
        self._token = token or self._token
        if not self._token:
            raise PoeConnectionError("Token is not set")
        self._agent = PoeAgent(token)

        return self


poe = Poe()


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
