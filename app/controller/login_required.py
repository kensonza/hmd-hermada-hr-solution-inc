import urllib.parse
from flask import session, redirect, url_for, request
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("loggedin") is None:
            message = "Please log in to access this page."
            encoded_message = urllib.parse.quote(message)
            return redirect(url_for('auth.login') + f'?message={encoded_message}')
        return f(*args, **kwargs)
    return decorated_function