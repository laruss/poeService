import logging

from flask import Blueprint, request

from api.controllers.bot.chat import ChatController
from api.models.bot.chat import Chat
from api.utils.utils import response

chat_bp = Blueprint('chat', __name__)


def get_chat_id(chat_id):
    if chat_id == 'current':
        chat = Chat.get_by_filter({})
        if not chat:
            return response({"error": "No current chat is found"}, 404)
        chat_id = chat.chat_id
    return chat_id


@chat_bp.route('/<bot_name>/chat/all', methods=['GET', 'PUT', 'PATCH'])
def all_chats_actions(bot_name):
    controller = ChatController()
    mapper = dict(
        PUT=controller.init_all_chats,
        GET=controller.get_all_chats,
        PATCH=controller.update_all_chats_from_poe,
    )
    return mapper[request.method](bot_name)


@chat_bp.route('/<bot_name>/chat/all', methods=['DELETE'])
def delete_all_chats(bot_name):
    in_poe = request.args.get('in_poe', False, type=bool)
    return ChatController().delete_all_chats(bot_name, not in_poe)


@chat_bp.route('/<bot_name>/chat/<chat_id>', methods=['GET', 'PATCH'])
def chat_methods(bot_name, chat_id):
    logging.info(f"chat_id: {chat_id}")
    chat_id = get_chat_id(chat_id)

    controller = ChatController()
    mapper = dict(
        GET=controller.get_one_chat,
        PATCH=controller.update_one_chat_from_poe,
    )

    return mapper[request.method](bot_name, chat_id)


@chat_bp.route('/<bot_name>/chat/<chat_id>', methods=['DELETE'])
def chat_delete(bot_name, chat_id):
    chat_id = get_chat_id(chat_id)
    in_poe = request.args.get('in_poe', False, type=bool)
    return ChatController().delete_one_chat(bot_name, chat_id, not in_poe)


@chat_bp.route('/<bot_name>/chat/<chat_id>/messages', methods=['GET'])
def get_chat_messages(bot_name, chat_id):
    """ gets len of chat messages from db or poe api """
    chat_id = get_chat_id(chat_id)
    limit = request.args.get('limit', 1000, type=int)
    offset = request.args.get('offset', 0, type=int)

    return ChatController().get_messages(bot_name, chat_id, limit, offset)


@chat_bp.route('/<bot_name>/chat/<chat_id>/messages', methods=['PATCH'])
def update_chat_messages(bot_name, chat_id):
    """ gets len of chat messages from db or poe api """
    chat_id = get_chat_id(chat_id)
    limit = request.args.get('limit', 50, type=int)

    return ChatController().update_chat_messages(bot_name, chat_id, limit)


@chat_bp.route('/<bot_name>/chat/<chat_id>/messages', methods=['PUT'])
def init_chat_messages(bot_name, chat_id):
    """ gets all the chat messages from poe api and saves them to db """
    chat_id = get_chat_id(chat_id)
    return ChatController().init_chat_messages(bot_name, chat_id)


@chat_bp.route('/<bot_name>/chat/<chat_id>', methods=['POST'])
def chat_send_message(bot_name, chat_id):
    chat_id = None if chat_id == 'new' else get_chat_id(chat_id)

    message = request.json.get('message')
    if not message:
        return response({'error': 'Message not provided'}, 400)

    return ChatController().send_message(bot_name=bot_name, message=message, chat_id=chat_id)


@chat_bp.route('/<bot_name>/chat/<chat_id>', methods=['PUT'])
def retry_message(bot_name, chat_id):
    chat_id = get_chat_id(chat_id)

    return ChatController().retry_message(bot_name, chat_id)


@chat_bp.route('/<bot_name>/chat/<chat_id>/messages/<message_id>', methods=['DELETE'])
def chat_one_message(bot_name, chat_id, message_id):
    chat_id = get_chat_id(chat_id)

    return ChatController().delete_message(chat_id, int(message_id))
