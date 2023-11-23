import flask
from flask_cors import CORS

from api.openapi import swaggerui_blueprint
# do not remove this import
from api.poe_agent import agent

from api.extensions import mongo
from api.routes.bot import bot_bp
from api.utils.errorhandlers import register_errorhandlers
from api.routes import *
from config import root_path


def create_app(config):
    app = flask.Flask(__name__)
    app.static_folder = root_path / 'api' / 'openapi'
    app.static_url_path = '/static'
    app.config.from_object(config)
    CORS(app)
    mongo.init_app(app)

    [app.register_blueprint(blueprint) for blueprint in (settings_bp, agent_bp, bot_bp, swaggerui_blueprint)]

    register_errorhandlers(app)

    return app
