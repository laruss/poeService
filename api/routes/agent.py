from flask import Blueprint

from api.models.bot import Bot
from api.models.settings import Settings
from api.poe_agent import agent
from api.routes.helpers import api_token_is_set_wrapper
from api.utils.utils import success_response, response

agent_bp = Blueprint('agent', __name__, url_prefix='/agent')


@agent_bp.route('', methods=['GET'])
def get_agent():
    is_api_token_set = bool(Settings.get().api_token)

    return success_response(dict(
        status=agent.status,
        is_api_token_set=is_api_token_set,
        registered_bots=[bot.handle for bot in Bot.objects()]
    ))


@agent_bp.route('/connect', methods=['POST'])
@api_token_is_set_wrapper
def connect_agent():
    agent.connect()
    return response(status=204)


@agent_bp.route('/disconnect', methods=['POST'])
@api_token_is_set_wrapper
def disconnect_agent():
    agent.disconnect()
    return response(status=204)


@agent_bp.route('/reconnect', methods=['POST'])
@api_token_is_set_wrapper
def reconnect_agent():
    agent.disconnect()
    agent.connect()
    return response(status=204)
