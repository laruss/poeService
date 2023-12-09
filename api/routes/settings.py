import flask
from flask import Blueprint

from ..controllers.settings import SettingsController
from .helpers import api_token_is_set_wrapper
from ..extensions import poe

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


@settings_bp.before_request
@api_token_is_set_wrapper
def before_request():
    poe.connect(flask.g.get('session_id')) if not poe.is_connected else ...


@settings_bp.route('', methods=['GET'])
@api_token_is_set_wrapper
def get_limits():
    return SettingsController().get_limits()
