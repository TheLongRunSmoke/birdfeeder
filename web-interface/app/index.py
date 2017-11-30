import os

from flask import send_from_directory
from app import app
from .utils import *


@app.route('/', methods=['GET'])
@maintenance
def index():
    return render_template("index.html")


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.errorhandler(403)
def not_found_error(error):
    return make_error('403.html', 403)


@app.errorhandler(404)
def not_found_error(error):
    return make_error('404.html', 404)


@app.errorhandler(500)
def internal_error(error):
    return make_error('500.html', 500)
