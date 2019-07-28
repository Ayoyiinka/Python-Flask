import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from elasticsearch import Elasticsearch

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
mail = Mail(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
babel = Babel(app)
login.login_view = 'login'
login.login_message = _l('Please log in to access this page.')
app.elasticsearch =  Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
                    if app.config['ELASTICSEARCH_URL'] else None

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None #for authentication
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None #for encryption
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
                                    mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                                    fromaddr='no_reply@' + app.config['MAIL_SERVER'],
                                    toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                                    credentials=auth, secure=secure
                                    )
        mail_handler.setLevel(logging.ERROR) #logging only error messages, remember there are 5 logging levels each one indicating the severity of events
        app.logger.addHandler(mail_handler)
#If app.logger is accessed before logging is configured, it will add a default handler.
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10) #writes logs to files and in order to prevent those log files from filling up the disk
    file_handler.setFormatter(logging.Formatter(                                             #we keep deleting old logs as new ones are added. - logfile size = 10KB and keep only 10 logged files at a time
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))              #setformatter configures the format of each log line
    file_handler.setLevel(logging.INFO) #unlike with the email handler where we wanted only severe logs such as errors, here we want everything that is logged to be written to the file
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)    #this ensures that all the messages are passed down to the handlers (mail and file), then each handler will pick the ones that it has been set to take
    app.logger.info('Microblog startup') #This is an example of writing to the log: so this writes Microblog startup everytime the server starts
    #When this application runs on a production server, the log directly above will tell us when the server was restarted.

@babel.localeselector #This decorator tells Flask babel to invoke the function get_locale for every request to select the language that we are going to use for every given request.
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])

from flasky import routes, models, errors
#These imports brings all the code from the modules back to this module like they have been written here.
