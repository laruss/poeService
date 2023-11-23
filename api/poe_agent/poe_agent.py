import logging

from .poe_api import AppPoeApi
from ..extensions import autolog
from ..models.bot.bot import Bot
from api.models.bot.chat import Chat
from ..utils.exceptions import PoeConnectionError, PoeBotError


class __PoeAgent:
    def __init__(self):
        self.client: AppPoeApi = None

    @property
    def is_connected(self):
        return self.client and self.client.ws_connected

    @property
    def status(self):
        return "connected" if self.is_connected else "disconnected"

    @autolog("Connecting to POE API")
    def connect(self):
        from api.models.settings import Settings

        token = Settings.get().api_token

        self.client = self.client or AppPoeApi(token)
        if not self.is_connected:
            try:
                self.client.connect_ws()
            except Exception as e:
                raise PoeConnectionError(e)

    @autolog("Disconnecting from POE API")
    def disconnect(self):
        if self.is_connected:
            self.client.disconnect_ws()

    @autolog("Initializing bot")
    def init_bot(self, bot_name: str) -> Bot:
        self.connect()

        if bot := Bot.get_by_filter({"handle": bot_name}):
            logging.info(f"Bot {bot_name} already exists in DB, won't be initialized again")
            return bot

        data = self.client.get_bot_data(bot_name=bot_name)
        bot_data = data.get("bot")

        if not bot_data:
            raise PoeBotError(f"Bot {bot_name} doesn't exist in POE API")

        bot = Bot(poe_id=bot_data["id"], bot_id=bot_data["botId"], handle=bot_data["handle"],
                  prompt=bot_data["promptPlaintext"]).save()

        return bot

    @autolog("Updating bot from POE API")
    def update_bot_from_api(self, bot_name: str) -> Bot:
        self.connect()

        bot = Bot.get_by_filter({"handle": bot_name})
        if not bot:
            logging.warning(f"Bot {bot_name} doesn't exist in DB, will be initialized")
            return self.init_bot(bot_name)

        data = self.client.get_bot_data(bot_name=bot_name)
        bot_data = data.get("bot")

        if not bot_data:
            raise PoeBotError(f"Bot {bot_name} doesn't exist in POE API")

        bot.update(poe_id=bot_data["id"], bot_id=bot_data["botId"], handle=bot_data["handle"],
                   prompt=bot_data["promptPlaintext"])

        return bot

    @autolog("Setting bot prompt")
    def set_bot_prompt(self, bot_name: str, prompt: str):
        self.connect()
        self.client.edit_bot(bot_name, prompt=prompt)
        self.update_bot_from_api(bot_name)

    @autolog("Initializing chats")
    def init_chats(self, bot_name: str, update_if_exists: bool = False) -> list[Chat]:
        self.connect()

        bot = Bot.get_by_filter({"handle": bot_name})
        if not bot:
            logging.warning(f"Bot {bot_name} doesn't exist in DB, will be initialized")
            bot = self.init_bot(bot_name)

        response = self.client.get_chat_history(bot_name)
        chats_data = response["data"][bot_name.lower()]
        chats = []
        for chat_data in chats_data:
            chat = Chat.get_by_filter({"chat_code": chat_data["chatCode"]})

            data = dict(chat_id=chat_data["chatId"], chat_code=chat_data["chatCode"], poe_id=chat_data["id"],
                        title=chat_data["title"], bot_id=bot.id)

            if not chat:
                chat = Chat(**data).save()
            elif update_if_exists:
                chat.update(**data)
            chats.append(chat)

        return chats

    @autolog("Deleting chat")
    def delete_chat(self, bot_name: str, chat_id: int):
        self.connect()
        self.client.delete_chat(bot=bot_name, chatId=chat_id)

    @autolog("Getting chat messages")
    def get_chat_messages(self, chat_id: int, count: int = 50, get_all: bool = False) -> list[dict]:
        self.connect()
        chat = Chat.get_by_filter({"chat_id": chat_id})
        if not chat:
            raise PoeBotError(f"Chat {chat_id} doesn't exist in DB, you need to initialize it first")
        bot = Bot.get_by_id(chat.bot_id)
        if not bot:
            raise PoeBotError(f"Somehow chat {chat_id} doesn't have bot in DB, you need to initialize it first")

        return self.client.get_previous_messages(bot=bot.handle, chatId=chat_id, count=count, get_all=get_all)

    @autolog("Sending message")
    def send_message(self, bot_name: str, message: str, chat_id: int = None):
        """ if chat_id is not provided, will send a message to a new chat """
        self.connect()

        for chunk in self.client.send_message(bot=bot_name, message=message, chatId=chat_id):
            if chunk["state"] == 'complete':
                logging.info(f"Response: {chunk}")
            yield chunk["response"]

    @autolog("Retrying message")
    def retry_message(self, chat_code: str):
        self.connect()

        for chunk in self.client.retry_message(chat_code):
            if chunk["state"] == 'complete':
                logging.info(f"Response: {chunk}")
            yield chunk["response"]

    @autolog("Deleting messages")
    def delete_messages(self, *message_ids: int):
        self.connect()
        self.client.delete_message(message_ids)


agent = __PoeAgent()
