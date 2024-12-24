# crm_flask/app/config.py
import os
from dotenv import load_dotenv
import redis

# Load environment variables from .env file
load_dotenv('.env')


class Config:
    """Base configuration"""
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False
    PROPAGATE_EXCEPTIONS = True
    APPNAME = 'app'
    ROOT = os.path.abspath(APPNAME)
    UPLOAD_PATH = '/static/upload/'
    SERVER_PATH = os.path.join(ROOT, UPLOAD_PATH)

    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', 'qwerty12345')

    # MySQL database configuration
    USER = os.environ.get('MYSQL_USER', 'test')
    PASSWORD = os.environ.get('MYSQL_PASSWORD', 'test')
    HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
    PORT = os.environ.get('MYSQL_PORT', '3306')
    DB = os.environ.get('MYSQL_DB', 'jinetdb')
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key for Flask application
    SECRET_KEY = os.environ.get('SECRET_KEY', 'qwerty123456')

    # Session management configuration
    SESSION_TYPE = os.environ.get('SESSION_TYPE', 'filesystem')
    SESSION_PERMANENT = os.environ.get('SESSION_PERMANENT', 'False').lower() == 'true'
    SESSION_USE_SIGNER = os.environ.get('SESSION_USE_SIGNER', 'True').lower() == 'true'
    SESSION_KEY_PREFIX = os.environ.get('SESSION_KEY_PREFIX', 'session')
    PERMANENT_SESSION_LIFETIME = int(os.environ.get('PERMANENT_SESSION_LIFETIME', 86400))  # Default: 24 hours

    # Redis configuration for sessions
    SESSION_REDIS_HOST = os.environ.get('SESSION_REDIS_HOST', '127.0.0.1')
    SESSION_REDIS_PORT = os.environ.get('SESSION_REDIS_PORT', '6379')
    SESSION_REDIS = redis.StrictRedis(
        host=SESSION_REDIS_HOST,
        port=SESSION_REDIS_PORT,
        password=os.environ.get('SESSION_REDIS_PASSWORD')
    )

    # Logging level
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING').upper()


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Log all SQL queries
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'WARNING'
    SESSION_TYPE = 'redis'  # Use Redis for session storage in production
