from __future__ import annotations

from typing import Optional, List

from poeagent.agent import MessageGenerator  # type: ignore
from poeagent.models.chat_messages_data import MessageData  # type: ignore

from api.extensions import poe
from api.models.base import BaseAppModel
from api.utils.exceptions import PoeBotError


class Chat(BaseAppModel):
    __collection_name__ = "chats"

    isDeleted: bool
    title: str
    id: str
    chatId: int
    botId: int
    chatCode: str
    messages: Optional[List[MessageData]] = []

    @classmethod
    def get_by_chat_code(cls, chat_code: str) -> Chat:
        return cls.get_by_filter(chat_code=chat_code) or cls.get_from_api(chat_code)

    @classmethod
    def get_from_api(cls, chat_code: str) -> Chat:
        chat_info = cls.request_with_retries(
            lambda: poe.agent.get_one_chat_data(chat_code)
        )
        if not chat_info:
            raise PoeBotError(f"Chat {chat_code} not found in API")
        chat = chat_info.data.chatOfCode
        kwargs = dict(
            isDeleted=chat.isDeleted,
            title=chat.title,
            id=chat.id,
            chatId=chat.chatId,
            botId=chat.botId,
            chatCode=chat_code
        )
        if instance := cls.get_by_filter(chat_code=chat_info.chatCode):
            return instance.update(**kwargs)
        else:
            return cls(**kwargs).save()

    @classmethod
    def get_all_from_api(cls, bot_name: str) -> List[Chat]:
        chats_history = cls.request_with_retries(
            lambda: poe.agent.get_chats_history(bot_name)
        )
        codes = [chat.chatCode for chat in chats_history]

        return [cls.get_from_api(chat_code) for chat_code in codes]

    def delete_from_api(self) -> None:
        if self.request_with_retries(lambda: poe.agent.delete_chat(self.chatId)):
            self.delete()

    def get_messages(self, offset: int = 0, count: int = 25) -> List[MessageData]:
        if not self.messages:
            self.get_messages_from_api(200)
        if not self.messages:
            return []

        messages = self.messages[::-1]
        messages = messages[offset:offset + count]
        return messages[::-1]

    def get_messages_from_api(self, count: int = 25) -> List[MessageData]:
        messages = self.request_with_retries(lambda: poe.agent.get_chat_messages(self.chatCode, count))
        if not self.messages:
            self.messages = messages

        stored_messages_ids = [mes.messageId for mes in self.messages]  # type: ignore
        if messages[0].messageId in stored_messages_ids:
            stored_message_i = stored_messages_ids.index(messages[0].messageId)
            stored_messages = self.messages[:stored_message_i]  # type: ignore
            self.messages = stored_messages + messages
        else:
            setattr(self, 'messages', self.messages + messages) if len(messages) <= 2 \
                else setattr(self, 'messages', messages)

        self.save()
        return messages

    def delete_messages_from_api(self, *message_ids: int) -> None:
        result = self.request_with_retries(lambda: poe.agent.delete_messages(self.chatCode, *message_ids))
        if result:
            self.messages = [mes for mes in self.messages if mes.messageId not in message_ids]  # type: ignore
            self.save()

    @classmethod
    def send_message(cls, bot_name: str, message: str, chat_code: Optional[str] = None) -> MessageGenerator:
        chat = cls.get_by_chat_code(chat_code) if chat_code else None

        for chunk in poe.agent.send_message(bot_name, message, chat.chatId if chat else None):
            yield chunk

            if chunk.humanMessage is not None:
                chat = cls.get_from_api(chunk.chat.chatCode) if not chat else chat
                chat.messages = [chunk.humanMessage]
                chat.messages.append(MessageData(**chunk.model_dump(by_alias=True, exclude={'humanMessage', 'chat'})))
                chat.save()

    def regenerate_message(self) -> MessageGenerator:
        if not self.get_messages_from_api(1):
            raise PoeBotError("No messages to retry")

        chunk_ = None
        for chunk in poe.agent.regenerate_message(self.chatId):
            chunk_ = chunk
            yield chunk

        if self.messages and chunk_:
            data = MessageData(**chunk_.model_dump(by_alias=True, exclude={'humanMessage', 'chat'}))
            if self.messages[-1].messageId == chunk_.messageId:
                self.messages[-1] = data
            else:
                self.messages.append(data)
