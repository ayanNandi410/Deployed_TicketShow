 import os
import secrets
import logging

baseDir = os.path.abspath(os.getcwd())

class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevConfig():
    SQLITE_DB_DIR = os.path.join(baseDir, "./dbDir")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    #"sqlite:///" + os.path.join(SQLITE_DB_DIR, "ticketdb.sqlite")
    SECRET_KEY = secrets.token_hex(26)
    DEBUG=True

    if app.config['LOG_WITH_GUNICORN']:
        gunicorn_error_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers.extend(gunicorn_error_logger.handlers)
        app.logger.setLevel(logging.DEBUG)

