import flask
from flask_cors import CORS  # type: ignore

from api.openapi import swaggerui_blueprint

# do not remove poe import
from api.extensions import mongo, poe
from api.routes.bot import bot_bp
from api.utils.errorhandlers import register_errorhandlers
from api.routes import *
from config import openapi_path


def create_app(config):
    app = flask.Flask(__name__)
    app.static_folder = openapi_path
    app.static_url_path = '/static'
    app.config.from_object(config)
    CORS(app)
    mongo.init_app(app)

    [app.register_blueprint(blueprint) for blueprint in (settings_bp, bot_bp, swaggerui_blueprint)]

    register_errorhandlers(app)

    return app
