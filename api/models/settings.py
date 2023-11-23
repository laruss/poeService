from __future__ import annotations

from typing import Optional

from api.models.base import BaseAppModel


class Settings(BaseAppModel):
    __collection_name__ = 'settings'

    api_token: Optional[str] = None

    @classmethod
    def get(cls) -> Settings:
        return cls.get_by_filter({}) or cls().save()
