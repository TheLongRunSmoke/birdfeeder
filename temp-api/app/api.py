from datetime import datetime

from flask import Response, jsonify, request
from flask_sqlalchemy import get_debug_queries

from app import app, models
from config import DATABASE_QUERY_TIMEOUT
from .basicauth import *


@app.route('/api/v1.0/temp', methods=['GET', 'OPTIONS'])
@auth.login_required
def get_temperature_for_period():
    """
    Main point of API. Extract list of data from database.
    :return: API data in JSON serialization.
    """
    try:
        seconds = int(request.args.get('seconds'))
    except TypeError:
        seconds = 43200  # 12 hours
    if seconds > 43200:
        seconds = 43200
    time = datetime.utcnow().timestamp() - seconds
    result = get_from_db(time)
    resp = jsonify(result)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Authorization, content-type'
    return resp


@app.route('/api/v1.0/temp/change', methods=['GET', 'OPTIONS'])
@auth.login_required
def get_temperature_change():
    """
    Return external temperature change in last hour.
    :return: API data in JSON serialization.
    """
    time = datetime.utcnow().timestamp() - 60 * 60
    result = get_change(time)
    resp = jsonify(result)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Authorization, content-type'
    return resp


def get_from_db(timestamp):
    """
    Return db row with all actual temperatures.
    :param timestamp: form timestamp
    :return: list
    """
    result = [[], [], [], []]
    query = models.Temperature.query.filter(models.Temperature.timestamp >= timestamp) \
        .order_by(models.Temperature.timestamp.asc()).all()
    if query is not None:
        if len(query) > 1:
            for row in query:
                result[0].append(row.timestamp)
                result[1].append(row.external)
                result[2].append(row.internal)
                result[3].append(row.cpu)
    return result


def get_change(timestamp):
    """
    Look up db, and calculate temperature change.
    :param timestamp: form timestamp
    :return: dict
    """
    result = {'current': 0, 'change': 0}
    query = models.Temperature.query \
        .with_entities(models.Temperature.external) \
        .filter(models.Temperature.timestamp >= timestamp) \
        .order_by(models.Temperature.timestamp.asc()).all()
    if query is not None:
        if len(query) > 1:
            result['current'] = query[-1].external
            result['change'] = query[-1].external - query[0].external
    return result


@app.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= DATABASE_QUERY_TIMEOUT:
            app.logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (
                query.statement, query.parameters, query.duration, query.context))
    return response
