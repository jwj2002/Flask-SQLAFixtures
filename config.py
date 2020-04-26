import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "secret_key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = None  # added to supress warning during testing.
    SQLAFIXTURES_DIRECTORY = os.path.join(basedir, 'sqlafixtures')
    SQLAFIXTURES_FILENAME = 'fixtures_file.xlsx'
    SQLAFIXTURES_MODULES = ['app.users.models']


class ProdConfig(Config):
    """Production configuration."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")


class DevConfig(Config):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app_dev.db")
    SQLAFIXTURES_MODE = 'development'


class TestConfig(Config):
    """Testing configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    WTF_CSRF_ENABLED = False
    SQLAFIXTURES_MODE = 'testing'
