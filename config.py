import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #configure an email server that the application can use to send emails
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25) #all the environment variables are strings; 25 is the default port for email
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None #flag that determines if I am using an encrypted connection to the email server or not; True if it is defined in environment or else set to False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['ayoyinkaobisesan@gmail.com'] #recipient of the emails from 500 error
    POSTS_PER_PAGE = 25
    LANGUAGES = ['en', 'es', 'yor'] #'es' is the language code for spanish
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
