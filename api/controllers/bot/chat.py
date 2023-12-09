from typing import Optional

from flask import Response

from api.controllers.base import BC
from api.models.bot import Bot
from api.models.bot.chat import Chat
from api.utils.errorhandlers import handle_errors
from api.validators import DeleteMessagesValidator, SendMessageValidator


class ChatController(BC[Chat]):
    model = Chat

    @handle_errors
    def get_all_local_chats(self, bot_name: str):
        bot = Bot.get_by_bot_name(bot_name)
        chats = Chat.objects(botId=bot.botId)

        return self.response200([chat.model_dump(exclude={"messages"}) for chat in chats])

    @handle_errors
    def update_all_chats_from_api(self, bot_name: str):
        bot = Bot.get_by_bot_name(bot_name)
        return self.response200([chat.model_dump(exclude={"messages"}) for chat in Chat.get_all_from_api(bot.handle)])

    @handle_errors
    def get_chat(self, bot_name: str, chat_code: str):
        Bot.get_by_bot_name(bot_name)
        chat = Chat.get_by_chat_code(chat_code)

        return self.response200(chat.model_dump(exclude={"messages"}))

    @handle_errors
    def update_chat_from_api(self, bot_name: str, chat_code: str):
        Bot.get_by_bot_name(bot_name)
        return self.response200(Chat.get_from_api(chat_code).model_dump(exclude={"messages"}))

    @handle_errors
    def delete_chat(self, bot_name: str, chat_code: str):
        Bot.get_by_bot_name(bot_name)
        Chat.get_by_chat_code(chat_code).delete_from_api()

        return self.response204()

    @staticmethod
    def _reverse_slice(list_: list, offset: int, limit: int):
        r_list = list_[::-1]
        slice_ = r_list[offset:offset + limit]
        return slice_[::-1]

    @handle_errors
    def get_messages(self, bot_name: str, chat_code: str, count: int = 100, offset: int = 0):
        Bot.get_by_bot_name(bot_name)
        chat = Chat.get_by_chat_code(chat_code)
        messages = chat.get_messages(offset, count)

        return self.response200([mes.model_dump(by_alias=True) for mes in messages])

    @handle_errors
    def update_messages(self, bot_name: str, chat_code: str, limit: int):
        Bot.get_by_bot_name(bot_name)
        chat = Chat.get_by_chat_code(chat_code)
        messages = chat.get_messages_from_api(limit)

        return self.response200([mes.model_dump(by_alias=True) for mes in messages])

    @staticmethod
    def _send_message(bot_name: str, message: str, chat_code: Optional[str] = None):
        for chunk in Chat.send_message(bot_name, message, chat_code):
            yield chunk.model_dump(by_alias=True)

    @handle_errors
    def send_message(self, bot_name: str, data: Optional[dict], chat_code: Optional[str] = None):
        Bot.get_by_bot_name(bot_name)
        if not data:
            return self.response400("No message provided")
        model = SendMessageValidator(**data)
        if chat_code:
            Chat.get_by_chat_code(chat_code)

        return self.stream_response(self._send_message(bot_name, model.message, chat_code))

    @staticmethod
    def _regen_message(chat: Chat):
        for chunk in chat.regenerate_message():
            yield chunk.model_dump(by_alias=True)

    @handle_errors
    def regenerate_message(self, bot_name: str, chat_code: str):
        Bot.get_by_bot_name(bot_name)
        chat = Chat.get_by_chat_code(chat_code)

        return self.stream_response(self._regen_message(chat))

    @handle_errors
    def delete_messages(self, bot_name: str, chat_code: str, data: Optional[dict]):
        if not data:
            return self.response400("No message_ids provided")
        model = DeleteMessagesValidator(**data)
        Bot.get_by_bot_name(bot_name)
        Chat.get_by_chat_code(chat_code).delete_messages_from_api(*model.message_ids)

        return self.response204()
