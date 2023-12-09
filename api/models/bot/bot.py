from __future__ import annotations

from typing import Optional, List

from poeagent.models.bot import FullBotData  # type: ignore

from api.extensions import poe
from api.models.base import BaseAppModel
from api.utils.exceptions import PoeBotError
from api.validators import CreateBotValidator, EditBotValidator


class Bot(BaseAppModel, FullBotData):
    __collection_name__ = "bots"

    @classmethod
    def get_by_bot_name(cls, bot_name: str) -> Bot:
        return cls.get_by_filter(handle=bot_name) or cls.get_from_api(bot_name)

    @classmethod
    def get_from_api(cls, chat_code: Optional[str] = None, bot_name: Optional[str] = None,
                     bot_id: Optional[int] = None) -> Bot:
        bot_info = cls.request_with_retries(
            lambda: poe.agent.get_bot_data(chat_code, bot_name, bot_id)
        )
        if not bot_info:
            raise PoeBotError(f"Bot {bot_name} not found in API")
        if instance := cls.get_by_filter(handle=bot_info.handle):
            return instance.update(**bot_info)
        else:
            return cls(**bot_info.model_dump(by_alias=True)).save()

    @classmethod
    def get_base_models(cls) -> dict:
        creation_bots = cls.request_with_retries(poe.agent.get_available_creation_bots)
        return {bot.model: bot.displayName for bot in creation_bots}

    @classmethod
    def create(cls, bot_data: CreateBotValidator) -> Bot:
        created_bot = cls.request_with_retries(
            lambda: poe.agent.create_bot(**bot_data.model_dump(by_alias=True))
        )
        return cls.get_from_api(bot_name=created_bot.handle)

    @classmethod
    def edit_in_api(cls, bot_data: EditBotValidator) -> Bot:
        response = cls.request_with_retries(
            lambda: poe.agent.edit_bot(**bot_data.model_dump(by_alias=True))
        )
        return cls.get_from_api(bot_name=response.handle)

    @classmethod
    def delete_in_api(cls, bot_name: str) -> None:
        bot = cls.get_by_bot_name(bot_name)
        result = cls.request_with_retries(lambda: poe.agent.delete_bot(bot.botId))
        if result:
            bot.delete()
