from typing import Optional, List, Dict

from api.models.base import BaseAppModel


class Chat(BaseAppModel):
    chat_id: Optional[int] = None
    chat_code: Optional[str] = None
    poe_id: Optional[str] = None
    title: Optional[str] = None
    bot_id: Optional[str] = None
    messages: Optional[List[dict]] = []

    def as_json(self) -> dict:
        return dict(
            chat_id=self.chat_id,
            chat_code=self.chat_code,
            poe_id=self.poe_id,
            title=self.title,
            bot_id=self.bot_id
        )
