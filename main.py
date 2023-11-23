from api.fabric import create_app
from config import AppConfig

app = create_app(config=AppConfig)

if __name__ == "__main__":
    app.run(
        debug=app.config["DEBUG"],
        host=app.config["HOST"],
        port=app.config["PORT"]
    )
