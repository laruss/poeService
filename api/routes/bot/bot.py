import logging

from flask import Blueprint, request

from api.controllers.bot.bot import BotController
from api.utils.utils import response

from ..helpers import api_token_is_set_wrapper
from .chat import chat_bp

bot_bp = Blueprint('bot', __name__, url_prefix='/bot')
bot_bp.register_blueprint(chat_bp)


@bot_bp.before_request
@api_token_is_set_wrapper
def before_request():
    """ this is needed to check if the api token is set before every request """
    pass


@bot_bp.route('/<bot_name>', methods=['PUT', 'PATCH', 'GET', 'DELETE'])
def one_bot_actions(bot_name):
    controller = BotController()
    mapper = dict(
        PUT=controller.init_bot,
        PATCH=controller.update_bot_from_api,
        GET=controller.get_bot,
        DELETE=controller.unregister_bot,
    )

    return mapper[request.method](bot_name)


@bot_bp.route('/all', methods=['GET', 'DELETE'])
def all_bots_actions():
    controller = BotController()
    mapper = dict(
        GET=controller.get_all_bots,
        DELETE=controller.unregister_all_bots,
    )

    return mapper[request.method]()


def validate_init_bots(bots):
    error = None
    if bots is None:
        error = 'Bots not provided'
    elif not isinstance(bots, list):
        error = 'Bots must be a list'
    elif len(bots) == 0:
        error = 'Bots list must not be empty'
    elif not all(isinstance(bot, str) for bot in bots):
        error = 'Bots must be a list of strings'

    return error


@bot_bp.route('', methods=['POST'])
def init_many_bots():
    bots = request.json.get('bots')
    if error := validate_init_bots(bots):
        return response({'error': error}, 400)

    return BotController().init_many_bots(bots)


@bot_bp.route('/<bot_name>/prompt', methods=['POST'])
def set_prompt(bot_name):
    prompt = request.json.get('prompt')
    if prompt is None:
        return response({'error': 'Prompt not provided'}, 400)
    if not isinstance(prompt, str):
        return response({'error': 'Prompt must be a string'}, 400)

    return BotController().set_prompt(bot_name, prompt)
