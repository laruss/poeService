from __future__ import annotations

import logging
from typing import Optional, Union, TypeVar, Type, Callable

from bson import ObjectId
from pydantic import BaseModel
from pymongo.collection import Collection
from pymongo.database import Database

from api.extensions import mongo, poe
from api.utils.exceptions import MongoConnectionError, PoeBotError

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='BaseAppModel')
Response = TypeVar('Response')


class BaseAppModel(BaseModel):
    __collection_name__: str
    _id: Optional[ObjectId] = None

    @classmethod
    def collection(cls) -> Collection:
        try:
            database: Database = mongo.db
        except NotImplementedError:
            raise MongoConnectionError('Mongo is not configured')
        if not getattr(cls, '__collection_name__', None):
            raise MongoConnectionError('Collection name is not defined')
        if (collection := database.get_collection(cls.__collection_name__)) is None:
            raise MongoConnectionError(f'Collection {cls.__collection_name__} is not found')

        return collection

    @classmethod
    def get_by_id(cls: Type[T], _id: Union[str, ObjectId]) -> Optional[T]:
        return cls.get_by_filter(_id=ObjectId(_id))

    @classmethod
    def get_by_filter(cls: Type[T], **filters) -> Optional[T]:
        result = cls.collection().find_one(filters)
        if not result:
            return None

        result_as_dict = dict(result)
        _id: ObjectId = result_as_dict.pop('_id')

        return cls(_id=_id, **result_as_dict)

    @classmethod
    def objects(cls: Type[T], **filters) -> list[T]:
        return [cls(**item) for item in cls.collection().find(filter=filters)]

    @classmethod
    def request_with_retries(cls, request_method: Callable[[], Response], retries: int = 3) -> Response:
        for i in range(retries):
            try:
                return request_method()
            except Exception as e:
                logger.warning(f'Error while getting settings from api: {e}')
                if i == retries - 1:
                    raise PoeBotError(f'Error while getting settings from api: {e}')
                poe.connect()

        return request_method()

    def save(self):
        data = self.model_dump(by_alias=True)
        if self._id:
            self.collection().update_one({'_id': self._id}, {'$set': data})
        else:
            self._id = self.collection().insert_one(data).inserted_id

        return self

    def delete(self):
        self.collection().delete_one({'_id': self._id}) if self._id else ...

    def update(self, **kwargs):
        self.collection().update_one({'_id': self._id}, {'$set': kwargs})
        [setattr(self, key, value) for key, value in kwargs.items()]  # type: ignore

        return self
