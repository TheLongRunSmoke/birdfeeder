from functools import wraps

from flask import make_response
from flask import render_template

from config import MAINTENANCE_MODE


def maintenance(func):
    """
    Decorator. Return maintenance page if needed.
    :return: response.
    """
    @wraps(func)
    def decorated_function():
        if MAINTENANCE_MODE:
            resp = make_response(render_template("maintenance.html"))
        else:
            resp = func()
        return resp
    return decorated_function


def make_error(page, number):
    resp = make_response(render_template(page, title=number), number)
    return resp
