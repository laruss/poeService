import json
from typing import Optional, TypeVar, Union, Type, Generic, Generator

import flask

from api.utils.utils import response, not_found_response
from api.models.base import BaseAppModel

T = TypeVar('T', bound='BaseAppModel')
DataType = Union[dict, list]
OptionalDataType = Optional[DataType]


class BC(Generic[T]):
    model: Type[T]

    def _get_by_id(self, _id: str) -> BaseAppModel:
        instance = self.model.get_by_id(_id)
        if not instance:
            raise KeyError(f"{self.model.__name__} with id {_id}")

        return instance

    @staticmethod
    def response(data: DataType, status: int = 200) -> flask.Response:
        if status < 100 or status > 599:
            raise ValueError("Status code must be between 100 and 599")
        return response(data, status)

    @staticmethod
    def response404(caption: str = "not found", data: OptionalDataType = None) -> flask.Response:
        """ Not Found """
        data = data or {"error": f"{caption} not found"}
        return not_found_response(data)

    @staticmethod
    def response400(caption: str) -> flask.Response:
        """ Bad Request """
        return response({"error": f"{caption}"}, status=400)

    def response200(self, data: OptionalDataType = None) -> flask.Response:
        """ OK """
        if data is None:
            data = {"success": True}
        return self.response(data, status=200)

    def response201(self, data: OptionalDataType = None) -> flask.Response:
        """ Created """
        data = data or {"success": True}
        return self.response(data, status=201)

    def response204(self):
        """ No Content """
        return self.response({"success": True}, status=204)

    def response409(self, caption: str) -> flask.Response:
        """ Conflict """
        return self.response({"error": f"{caption}"}, status=409)

    @staticmethod
    def stream_response(data: Generator[DataType, None, None]) -> flask.Response:
        """ text/event-stream """
        return flask.Response(json.dumps(data), mimetype='text/event-stream', status=200)
