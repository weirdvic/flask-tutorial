import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    ADMINS = ['your-email@example.com']
    LANGUAGES = ['en', 'ru']
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    POSTS_PER_PAGE = 25
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    YANDEX_FOLDER_ID = os.environ.get('YANDEX_FOLDER_ID')
    YANDEX_TRANSLATE_KEY = os.environ.get('YANDEX_TRANSLATE_KEY')
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    ELASTICSEARCH_USER = os.environ.get('ELASTICSEARCH_USER')
    ELASTICSEARCH_PASS = os.environ.get('ELASTICSEARCH_PASS')
