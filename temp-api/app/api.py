from datetime import datetime

from flask import jsonify, request
from flask_sqlalchemy import get_debug_queries

from app import app, models
from config import DATABASE_QUERY_TIMEOUT
from .basicauth import *


@app.route('/api/v1.0/temp', methods=['GET'])
@auth.login_required
def get_temperature_for_period():
    """
    Main point of API. Extract list of data from database.
    :return: API data in JSON serialization.
    """
    try:
        sensor = int(request.args.get('sensor'))
        seconds = int(request.args.get('seconds'))
        time = datetime.utcnow().timestamp()-seconds
        result = get_from_db(time, sensor)
    except TypeError:
        result = {"Error" : "No senconds and/or sensor specifed."}
    return jsonify(result)


def get_from_db(timestamp, sensor):
    """
    Return db row with all actual timestamp.
    :param timestamp: now timestamp
    :return: tle dict
    """
    result = {}
    query = models.Temperature.query.filter(models.Temperature.timestamp >= timestamp) \
        .order_by(models.Temperature.timestamp.asc()).all()
    if query is not None:
        if len(query) > 1:
            for row in query:
                if sensor == 0:
                    result[row.timestamp] = row.external
                else:
                    result[row.timestamp] = row.internal
    return result


@app.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= DATABASE_QUERY_TIMEOUT:
            app.logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (
                query.statement, query.parameters, query.duration, query.context))
    return response
