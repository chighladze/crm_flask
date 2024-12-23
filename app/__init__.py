import os
import logging
from flask import Flask, session
from flask_session import Session
from flask_login import current_user
from logging.handlers import RotatingFileHandler
from datetime import datetime
import pytz

from .extensions import db, migrate, login_manager, csrf
from .routes import register_routes
from .config import DevelopmentConfig, ProductionConfig


def create_app():
    """Создание экземпляра приложения Flask"""
    app = Flask(__name__)

    # Определяем конфигурацию
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Логирование
    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=5)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    file_handler.setLevel(app.config['LOG_LEVEL'])
    app.logger.addHandler(file_handler)

    app.logger.setLevel(app.config['LOG_LEVEL'])
    app.logger.info(f"Application started in {env} mode")

    # Перенаправление ошибок в лог
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unhandled Exception: {e}", exc_info=True)
        return "Internal Server Error", 500

    @app.before_request
    def update_last_activity():
        if current_user.is_authenticated:
            tz_tbilisi = pytz.timezone('Asia/Tbilisi')
            current_user.last_activity = datetime.now(tz_tbilisi)
            db.session.commit()

    # Инициализация расширений
    csrf.init_app(app)
    Session(app)
    register_routes(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = 'users.login'
    login_manager.login_message = False

    return app
