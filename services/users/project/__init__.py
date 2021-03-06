# services/users/project/__init__.py
import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()
cors = CORS()
migrate = Migrate()
toolbar = DebugToolbarExtension()


def create_app(script_info=None):
    app = Flask(__name__)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    bcrypt.init_app(app)
    db.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)
    toolbar.init_app(app)

    from project.api.users import users_blueprint
    app.register_blueprint(users_blueprint)

    from project.api.auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app
