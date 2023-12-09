from typing import Optional

from flask import Blueprint, request

from api.controllers.bot.chat import ChatController
from api.utils.utils import response

chat_bp = Blueprint('chat', __name__)

BASE_PATH = '/<bot_name>/chats'


@chat_bp.route(f'{BASE_PATH}', methods=['GET', 'PATCH'])
def all_chats_actions(bot_name):
    controller = ChatController()
    mapper = dict(
        GET=controller.get_all_local_chats,
        PATCH=controller.update_all_chats_from_api,
    )
    return mapper[request.method](bot_name)


@chat_bp.route(f'{BASE_PATH}/<chat_code>', methods=['GET', 'PATCH', 'DELETE', 'POST', 'PUT'])
def chat_methods(bot_name: str, chat_code: Optional[str]):
    controller = ChatController()

    if request.method == 'PATCH':
        """ update chat from api """
        return controller.update_chat_from_api(bot_name, chat_code)
    elif request.method == 'DELETE':
        """ delete chat """
        return controller.delete_chat(bot_name, chat_code)
    elif request.method == 'POST':
        """ send message """
        if chat_code == 'new':
            chat_code = None
        return controller.send_message(bot_name, request.json, chat_code)
    elif request.method == 'PUT':
        """ regenerate last message """
        return controller.regenerate_message(bot_name, chat_code)
    elif request.method == 'GET':
        """ get chat info """
        return controller.get_chat(bot_name, chat_code)
    else:
        return response({"error": "Method not allowed"}, 405)


@chat_bp.route(f'{BASE_PATH}/<chat_code>/messages', methods=['GET', 'PATCH', 'DELETE'])
def get_chat_messages(bot_name: str, chat_code: str):
    controller = ChatController()

    limit = request.args.get('limit', 1000, type=int)
    offset = request.args.get('offset', 0, type=int)

    if request.method == "GET":
        """ get chat messages from db """
        return controller.get_messages(bot_name, chat_code, limit, offset)
    elif request.method == "PATCH":
        """ update chat messages from api """
        return controller.update_messages(bot_name, chat_code, limit)
    elif request.method == "DELETE":
        """ delete chat messages """
        return controller.delete_messages(bot_name, chat_code, request.json)
