from app import app, celery
from flask import Response,stream_with_context
from .utils import *
from .cv import CV

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(app.cam0.get(), mimetype='multipart/x-mixed-replace; boundary=frame')

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

