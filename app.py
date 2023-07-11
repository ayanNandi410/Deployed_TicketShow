from main.constants import BASE_URL
from flask import Flask, render_template
from flask_login import LoginManager
from main.config import LocalDevConfig
from blueprints.authentication import authn as userAuth
from blueprints.admin import admin as adminProfile
from blueprints.user import user as userProfile
from models.users import User
from main.init_api import getConfiguredApi
from main.testData import generateTestData
from main.db import db
import os, logging

#template_dir = os.path.abspath(os.getcwd())
#static_dir =  os.path.abspath(os.getcwd())
#print(static_dir)

def create_app():
    app = Flask(__name__)

    # Local Development Configuration
    app.config.from_object(LocalDevConfig)

    gunicorn_error_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers.extend(gunicorn_error_logger.handlers)
    app.logger.setLevel(logging.DEBUG)

    # blueprint for authentication routes
    app.register_blueprint(userAuth)

    # blueprint for admin routes
    app.register_blueprint(adminProfile)

    # blueprint for user routes
    app.register_blueprint(userProfile)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'authn.userLogin'
    login_manager.login_message = "You need to login first!!"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('NotFound.html',errorMessage=e), 404

    generateTestData(app,db)

    api = getConfiguredApi(app)
    return app, api

app,api = create_app()

if __name__ == '__main__':
    app.run()
