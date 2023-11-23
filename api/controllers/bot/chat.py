from flask import Response

from api.controllers.base import BC
from api.models.bot import Bot
from api.models.bot.chat import Chat
from api.poe_agent import agent
from api.utils.errorhandlers import handle_errors


class ChatController(BC):
    model = Chat

    @handle_errors
    def init_all_chats(self, bot_name: str):
        chats = agent.init_chats(bot_name)

        return self.response200([chat.as_json() for chat in chats])

    @handle_errors
    def get_all_chats(self, bot_name: str):
        bot = Bot.get_by_filter({"handle": bot_name})
        if not bot:
            return self.response404(data={"error": f"Bot {bot_name} doesn't exist in DB"})
        chats = Chat.objects({"bot_id": bot.id})

        return self.response200([chat.as_json() for chat in chats])

    @handle_errors
    def update_all_chats_from_poe(self, bot_name: str):
        return self.update_one_chat_from_poe(bot_name)

    @handle_errors
    def delete_all_chats(self, bot_name: str, locally: bool = True):
        bot = Bot.get_by_filter({"handle": bot_name})
        if not bot:
            return self.response404(data={"error": f"Bot {bot_name} doesn't exist in DB"})
        chats = Chat.objects({"bot_id": bot.id})
        for chat in chats:
            if not locally:
                agent.delete_chat(bot_name, chat.chat_id)
            chat.delete()

        return self.response200(data={"message": f"All chats for bot {bot_name} were deleted"
                                                 f"{' locally' if locally else ''}"})

    @handle_errors
    def get_one_chat(self, bot_name: str, chat_id: int):
        bot = Bot.get_by_filter({"handle": bot_name})
        if not bot:
            return self.response404(data={"error": f"Bot {bot_name} doesn't exist in DB"})
        chat = Chat.get_by_filter({"chat_id": chat_id})
        if not chat:
            return self.response404(data={"error": f"Chat {chat_id} doesn't exist in DB"})

        return self.response200(data=chat.as_json())

    @handle_errors
    def update_one_chat_from_poe(self, bot_name: str, chat_id: int = None):
        bot = Bot.get_by_filter({"handle": bot_name})
        if not bot:
            return self.response404(data={"error": f"Bot {bot_name} doesn't exist in DB"})

        chats = agent.init_chats(bot_name, update_if_exists=True)

        if chat_id:
            chat = next((chat for chat in chats if chat.chat_id == chat_id), None)
            return self.response200(data=chat.as_json())

        return self.response200(data=[chat.as_json() for chat in chats])

    @handle_errors
    def delete_one_chat(self, bot_name: str, chat_id: int, locally: bool = True):
        bot = Bot.get_by_filter({"handle": bot_name})
        if not bot:
            return self.response404(data={"error": f"Bot {bot_name} doesn't exist in DB"})
        chat = Chat.get_by_filter({"chat_id": chat_id})
        if not chat:
            return self.response404(data={"error": f"Chat {chat_id} doesn't exist in DB"})
        if not locally:
            agent.delete_chat(bot_name, chat.chat_id)
        chat.delete()

        return self.response200(data={"message": f"Chat {chat_id} for bot {bot_name} was deleted"
                                                 f"{' locally' if locally else ''}"})
    
    @handle_errors
    def init_chat_messages(self, bot_name: str, chat_id: int):
        chat = Chat.get_by_filter({"chat_id": chat_id})
        if not chat:
            return self.response404(data={"error": f"Chat {chat_id} doesn't exist in DB"})
        
        messages = agent.get_chat_messages(chat_id, get_all=True)
        chat.update(messages=messages)
        
        return self.response204()

    @staticmethod
    def _reverse_slice(list_: list, offset: int, limit: int):
        r_list = list_[::-1]
        slice_ = r_list[offset:offset + limit]
        return slice_[::-1]

    @handle_errors
    def get_messages(self, bot_name: str, chat_id: int, limit: int = 1000, offset: int = 0):
        chat = Chat.get_by_filter({"chat_id": chat_id})
        if not chat:
            return self.response404(data={"error": f"Chat {chat_id} doesn't exist in DB"})

        if not chat.messages:
            self.init_chat_messages(bot_name, chat_id)

        return self.response200(data={"messages": self._reverse_slice(chat.messages, offset, limit)})

    def internal_update_chat_messages(self, bot_name: str, chat_id: int, limit: int):
        chat = Chat.get_by_filter({"chat_id": chat_id})
        if not chat:
            return self.response404(data={"error": f"Chat {chat_id} doesn't exist in DB"})

        if not chat.messages:
            return self.init_chat_messages(bot_name, chat_id)

        poe_messages = agent.get_chat_messages(chat_id, count=limit)
        poe_messages_ids = [mes["messageId"] for mes in poe_messages]
        chat_messages_ids = [mes["messageId"] for mes in chat.messages]
        for i, mes_id in enumerate(chat_messages_ids):
            if mes_id not in poe_messages_ids:
                chat.messages.pop(i)
            else:
                poe_message = poe_messages[poe_messages_ids.index(mes_id)]
                chat.messages[i].update(**poe_message)
        for i, mes_id in enumerate(poe_messages_ids):
            if mes_id not in chat_messages_ids:
                chat.messages.append(poe_messages[i])

        chat.save()

    @handle_errors
    def update_chat_messages(self, bot_name: str, chat_id: int, limit: int):
        self.internal_update_chat_messages(bot_name, chat_id, limit)
        return self.response204()

    @handle_errors
    def send_message(self, bot_name: str, message: str, chat_id: int = None):
        if chat_id is not None:
            chat = Chat.get_by_filter({"chat_id": chat_id})
            if not chat:
                return self.response404(data={"error": f"Chat {chat_id} doesn't exist in DB"})

        return Response(agent.send_message(bot_name=bot_name, message=message, chat_id=chat_id), mimetype='text/plain')

    def retry_message(self, bot_name: str, chat_id: int):
        chat = Chat.get_by_filter({"chat_id": chat_id})
        if not chat:
            return self.response404(data={"error": f"Chat {chat_id} doesn't exist in DB"})

        return Response(agent.retry_message(chat.chat_code), mimetype='text/plain')

    def delete_message(self, chat_id: int, message_id: int):
        chat = Chat.get_by_filter({"chat_id": chat_id})
        if not chat:
            return self.response404(data={"error": f"Chat {chat_id} doesn't exist in DB"})

        agent.delete_messages(message_id)

        return self.response204()
