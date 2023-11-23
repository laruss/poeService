import functools
from typing import Optional, List, TypeVar

import flask
from bson import ObjectId
from bson.errors import InvalidId
from pydantic_mongo.extensions import ValidationError
from pydantic import ValidationError as PydanticValidationError
from pymongo.errors import DuplicateKeyError

from api.utils.errorhandlers import handle_errors
from api.utils.utils import response, not_found_response
from api.models.base import BaseAppModel


T = TypeVar("T")


class BC:
    model = BaseAppModel

    def _get_by_id(self, _id: str) -> BaseAppModel:
        instance = self.model.get_by_id(_id)
        if not instance:
            raise KeyError(f"{self.model.__name__} with id {_id}")

        return instance

    @staticmethod
    def _get_object_by_id(Model: type[T], _id: str) -> T:
        obj_id = ObjectId(_id)
        instance = Model.get_by_id(obj_id)
        if not instance:
            raise KeyError(f"{Model.__name__} with id {_id}")

        return instance

    @handle_errors
    def delete(self, _id: str):
        instance = self._get_object_by_id(self.model, _id)
        instance.delete()

        return self.response200()

    @staticmethod
    def response(data: dict | list, status: int = 200) -> flask.Response:
        if status < 100 or status > 599:
            raise ValueError("Status code must be between 100 and 599")
        return response(data, status)

    @staticmethod
    def response404(caption: str = "not found", data: dict = None) -> flask.Response:
        """ Not Found """
        data = data or {"error": f"{caption} not found"}
        return not_found_response(data)

    @staticmethod
    def response400(caption: str) -> flask.Response:
        """ Bad Request """
        return response({"error": f"{caption}"}, status=400)

    def response200(self, data: dict | list = None) -> flask.Response:
        """ OK """
        if data is None:
            data = {"success": True}
        return self.response(data, status=200)

    def response201(self, data: dict | list = None) -> flask.Response:
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
    def _check_has_references(instance: BaseAppModel) -> Optional[List[Optional[BaseAppModel]]]:
        return instance.get_ref_objects()

    @handle_errors
    def get_all(self, **filters):
        fields_to_get = BaseAppModel.model_fields.keys()
        result = []

        for instance in self.model.objects(**filters):
            dump = instance.model_dump()
            result.append({field: dump[field] for field in fields_to_get})

        return self.response(result)

    @handle_errors
    def get_one_by_id(self, _id: str, simplified: bool = False):
        result = self._get_by_id(_id)
        result = result.model_dump(True)
        result = self._get_simplified(result) if simplified else result

        return self.response(result)

    @staticmethod
    def _get_simplified(dump: dict) -> dict:
        fields_to_get = BaseAppModel.model_fields.keys()
        return {field: dump[field] for field in fields_to_get}

    @handle_errors
    def create_one(self, data: dict):
        instance = self.model.get_with_parse_db_refs(data).save()

        return self.response(instance.model_dump(), 201)

    @handle_errors
    def delete_one_by_id(self, _id: str):
        instance = self._get_by_id(_id)
        result = instance.get_ref_objects()
        if result:
            for inst in result:
                if inst.id:
                    raise ValidationError(
                        f"Can't delete {self.model.__class__.__name__} with id {_id} because it has references "
                        f"('{instance.__class__.__name__}' with id '{instance.id}')"
                    )

        instance.delete()
        return self.response204()

    @handle_errors
    def update_one_by_id(self, _id: str, data: dict):
        data.pop('id', None)
        instance = self.model.get_with_parse_db_refs(data)
        instance.id = _id
        instance.save()

        return self.response204()
