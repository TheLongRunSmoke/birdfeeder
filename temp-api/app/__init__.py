import os

from flask import Flask
from flask_apscheduler import APScheduler
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

# app initialize.
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
mail = Mail(app)
# import parts with initialized context.
from app import index, api, models
# prepare scheduler.
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
# obtain some data from config.

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler

    os.makedirs('tmp', exist_ok=True)
    file_handler = RotatingFileHandler('tmp/iss-app.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('iss-app startup')
