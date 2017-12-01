import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_RECORD_QUERIES = True
DATABASE_QUERY_TIMEOUT = 0.5

JOBS = [
    {
        'id': 'job1',
        'func': 'jobs.get_temperature:run',
        'args': (),
        'trigger': 'interval',
        'minutes': 10
    }
]

MAINTENANCE_MODE = False

INTERNAL_ROM = "28-000003fb12c7"
EXTERNAL_ROM = "28-000003fb05b5"
