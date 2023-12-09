import logging

import flask
from flask import Blueprint, request

from api.controllers.bot.bot import BotController
from api.utils.utils import response

from .chat import chat_bp
from ..helpers import api_token_is_set_wrapper
from ...extensions import poe

bot_bp = Blueprint('bots', __name__, url_prefix='/bots')
bot_bp.register_blueprint(chat_bp)


@bot_bp.before_request
@api_token_is_set_wrapper
def before_request():
    poe.connect(flask.g.get('session_id')) if not poe.is_connected else ...


@bot_bp.route('/base-models', methods=['GET'])
def get_base_models():
    return BotController().get_base_models()


@bot_bp.route('/<bot_name>', methods=['PATCH', 'GET', 'DELETE'])
def one_bot_actions(bot_name):
    controller = BotController()

    if request.method == 'PATCH':
        return controller.edit_bot(bot_name, request.json) if request.json else controller.update_bot_from_api(bot_name)

    mapper = dict(GET=controller.get_bot, DELETE=controller.delete_bot)
    return mapper[request.method](bot_name)


@bot_bp.route('', methods=['GET', 'POST'])
def all_bots_actions():
    controller = BotController()
    if request.method == 'POST':
        return controller.create_bot(request.json)
    elif request.method == 'GET':
        return controller.get_all_bots()
    else:
        return response({"error": "Method not allowed"}, 405)
