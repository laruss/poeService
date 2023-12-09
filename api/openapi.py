from flask_swagger_ui import get_swaggerui_blueprint  # type: ignore

SWAGGER_URL = "/openapi"
API_URL = "/static/openapi.json"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        "app_name": "POE Agent"
    }
)
