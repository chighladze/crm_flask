import os
from dotenv import load_dotenv
import redis

load_dotenv('.env')


class Config(object):
    APPNAME = 'app'
    ROOT = os.path.abspath(APPNAME)
    UPLOAD_PATH = '/static/upload/'
    SERVER_PATH = os.path.join(ROOT, UPLOAD_PATH)

    USER = os.environ.get('MYSQL_USER', 'test')
    PASSWORD = os.environ.get('MYSQL_PASSWORD', 'test')
    HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
    PORT = os.environ.get('MYSQL_PORT', '3306')
    DB = os.environ.get('MYSQL_DB', 'jinetdb')

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'qwerty123456')

    SESSION_TYPE = os.environ.get('SESSION_TYPE', 'filesystem')
    SESSION_PERMANENT = os.environ.get('SESSION_PERMANENT') == 'True'
    SESSION_USE_SIGNER = os.environ.get('SESSION_USE_SIGNER') == 'True'
    SESSION_KEY_PREFIX = os.environ.get('SESSION_KEY_PREFIX', 'session')

    # Настройка подключения к Redis
    SESSION_REDIS_HOST = os.environ.get('SESSION_REDIS_HOST', '127.0.0.1')
    SESSION_REDIS_PORT = os.environ.get('SESSION_REDIS_PORT', '6379')
    SESSION_REDIS = redis.StrictRedis(host=SESSION_REDIS_HOST, port=SESSION_REDIS_PORT)

    # Добавление Redis в конфигурацию сессий
    SESSION_REDIS = SESSION_REDIS
