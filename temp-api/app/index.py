from app import app, db
from .utils import *


@app.route('/', methods=['GET', 'POST'])
def index():
    resp = make_response(render_template("index.html"))
    return resp


@app.errorhandler(403)
def not_found_error(error):
    return make_error('403.html', 403)


@app.errorhandler(404)
def not_found_error(error):
    return make_error('404.html', 404)


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return make_error('500.html', 500)

