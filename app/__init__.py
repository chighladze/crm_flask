from flask import Flask, session
from flask_session import Session
from .extensions import db, migrate, login_manager
from .config import Config
from datetime import datetime

from .routes.users import users
from .routes.dashboard import dashboard
from .routes.map import map
from .routes.error import error


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация сессии
    Session(app)

    app.jinja_env.globals['now'] = datetime.now

    app.register_blueprint(users)
    app.register_blueprint(dashboard)
    app.register_blueprint(map)
    app.register_blueprint(error)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # LOGIN MANAGER
    login_manager.login_view = 'users.login'

    with app.app_context():
        db.create_all()

    return app
