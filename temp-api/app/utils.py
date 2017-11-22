from datetime import datetime

from flask import make_response
from flask import render_template


def get_year():
    now = datetime.utcnow()
    return now.year


def make_error(page, number):
    resp = make_response(render_template(page, title=number), number)
    return resp
