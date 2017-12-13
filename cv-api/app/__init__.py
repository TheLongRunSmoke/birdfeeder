import os
import subprocess

from flask import Flask
from celery import Celery
from celery.bin import worker

# app initialize.
app = Flask(__name__)
app.config.from_object('config')
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)

# import parts with initialized context.
from app import index,cv
from app.cv import CV
app.cam0 = CV()


if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler

    os.makedirs('tmp', exist_ok=True)
    file_handler = RotatingFileHandler('tmp/cp-api.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('iss-app startup')
