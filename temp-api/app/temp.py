from datetime import datetime

from flask import jsonify, request
from flask_sqlalchemy import get_debug_queries

from app import app
from config import DATABASE_QUERY_TIMEOUT
from .basicauth import *


@app.route('/api/v1.0/temp', methods=['GET'])
@auth.login_required
def get_temperature():
    """
    Main point of API. Extract list of data from database.
    :return: API data in JSON serialization.
    """

    now = datetime.utcnow()
    authorizer = Auth()
    if authorizer.is_authenticate(auth.username(), request.headers.get('iss-key')):
        result = get_from_db(now.timestamp())
        return jsonify(result)
    else:
        abort(403)


def get_from_db(timestamp):
    """
    Return db row with all actual timestamp.
    :param timestamp: now timestamp
    :return: tle dict
    """
    result = {}
    # TODO: think about optimization for this
    actual = models.Temperature.query.filter(models.Temperature.timestamp < str(timestamp)) \
        .order_by(models.Temperature.timestamp.desc()).first()
    query = models.Temperature.query.filter(models.Temperature.timestamp >= actual.timestamp) \
        .order_by(models.Temperature.timestamp.asc()).all()
    if query is not None:
        try:
            for row in query:
                result[row.timestamp] = row.tle
        except TypeError:
            result[query.timestamp] = query.tle
    return result


@app.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= DATABASE_QUERY_TIMEOUT:
            app.logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (
                query.statement, query.parameters, query.duration, query.context))
    return response
