from pathlib import Path


basedir = Path(__file__).parent.parent


class BaseConfig:
    SECRET_KEY = 'asdfasdf98as7df97sd9f7s97f9'
    WTF_CSRF_SECRET_KEY = 'sd09f80sa98d0f8s0f0s0df8'


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
