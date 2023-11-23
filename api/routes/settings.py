from flask import Blueprint, request

from api.controllers.settings import SettingsController
from api.utils.utils import success_response

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


@settings_bp.route('', methods=['GET'])
def get_settings():
    return SettingsController().get_settings()


@settings_bp.route('', methods=['PUT'])
def set_settings():
    return SettingsController().set_settings(request.json)
