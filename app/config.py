import os
from dotenv import load_dotenv

load_dotenv()


class Config(object):
    APPNAME = 'app'
    ROOT = os.path.abspath(APPNAME)
    UPLOAD_PATH = '/static/upload/'
    SERVER_PATH = ROOT + UPLOAD_PATH

    USER = os.environ.get('MYSQL_USER', 'test')
    PASSWORD = os.environ.get('MYSQL_PASSWORD', 'test')
    HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
    PORT = os.environ.get('MYSQL_PORT', '3306')
    DB = os.environ.get('MYSQL_DB', 'jinetdb')

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'qwerty123456')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
