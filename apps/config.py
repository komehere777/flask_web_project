from pathlib import Path


basedir = Path(__file__).parent.parent


class BaseConfig:
    SECRET_KEY = '32dsldglkalsdgjslgslg'
    WTF_CSRF_SECRET_KEY = 'ASLsglslk23lksglkslg'


class LocalConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'local.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True


class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'testing.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False


config = {
    'local': LocalConfig,
    'testing': TestingConfig
}
