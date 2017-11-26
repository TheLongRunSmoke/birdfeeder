from hashlib import md5

from flask import abort
from flask_httpauth import HTTPBasicAuth

from .clients import CLIENTS

# clients.py must contain dictionary named CLIENTS look like this:
# CLIENTS = {
#    "<login>" : {"password": "<password md5 hash>"}
# }

auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    if username is not None:
        if username in CLIENTS.keys():
            user = CLIENTS[username]
            return user["password"]
    return None


@auth.error_handler
def unauthorized():
    abort(403)


@auth.hash_password
def hash_pw(password):
    return md5(password.encode('utf-8')).hexdigest()
