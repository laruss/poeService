from typing import Optional, List

from api.models.base import BaseAppModel
from api.models.bot.chat import Chat


class Bot(BaseAppModel):
    poe_id: str
    bot_id: int
    handle: str
    prompt: str = ""
