from __future__ import annotations

import logging
from typing import Optional, List

from poeagent.models.settings_data import Limits
from pydantic import BaseModel

from .base import BaseAppModel
from ..extensions import poe

logger = logging.getLogger(__name__)


class ApiRefreshPeriod(BaseModel):
    pass


class Settings(BaseAppModel):
    __collection_name__ = 'settings'

    api_refresh_period: ApiRefreshPeriod = ApiRefreshPeriod()

    @classmethod
    def get(cls) -> Settings:
        return cls.get_by_filter(**{}) or cls().save()

    def get_limits(self) -> List[Limits]:
        settings = self.request_with_retries(poe.agent.get_settings)
        return [edge.node for edge in settings.data.viewer.messageLimitsConnection.edges]
