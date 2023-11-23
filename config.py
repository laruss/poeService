import logging
import pathlib
from decouple import Config, RepositoryEnv

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

root_path = pathlib.Path(__file__).parent.resolve()
env_config = Config(RepositoryEnv(root_path / ".env"))


class DbConfig:
    DB_NAME = env_config.get("DB_NAME")
    HOST = env_config.get("DB_HOST")
    PORT = int(env_config.get("DB_PORT"))


class AppConfig:
    TESTING = True
    DEBUG = bool(env_config.get("DEBUG"))
    HOST = env_config.get("FLASK_APP_HOST")
    PORT = int(env_config.get("FLASK_APP_PORT"))
    MONGO_URI = f"mongodb://{DbConfig.HOST}:{DbConfig.PORT}/{DbConfig.DB_NAME}"
    MONGODB_SETTING = dict(
        db=DbConfig.DB_NAME,
        host=DbConfig.HOST,
        port=DbConfig.PORT
    )
