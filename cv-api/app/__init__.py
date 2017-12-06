import os

from flask import Flask, Response

# app initialize.
app = Flask(__name__)
app.config.from_object('config')
# import parts with initialized context.
from app import index
import cv2

vc = cv2.VideoCapture(0)

def gen():
    """Video streaming generator function."""
    while True:
        rval, frame = vc.read()
        cv2.imwrite('t.jpg', frame)
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

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
