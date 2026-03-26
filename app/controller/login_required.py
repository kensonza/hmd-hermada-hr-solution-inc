import urllib.parse
from flask import session, redirect, url_for, request, jsonify
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if session.get("loggedin") is None:

            # Check if API request
            if request.path.startswith('/api/'):
                return jsonify({"msg": "Unauthorized"}), 401

            message = "Please log in to access this page."
            encoded_message = urllib.parse.quote(message)
            return redirect(url_for('auth.login') + f'?message={encoded_message}')

        return f(*args, **kwargs)

    return decorated_function