from flask import Flask
from flask_session import Session
from .config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Убедитесь, что SESSION_TYPE задан правильно
session_type = app.config.get('SESSION_TYPE', 'filesystem')
if session_type not in ['redis', 'filesystem', 'sqlalchemy', 'memcached', 'mongodb']:
    raise ValueError(f"Unrecognized value for SESSION_TYPE: {session_type}")

# Инициализация сессии
Session(app)
