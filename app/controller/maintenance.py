import os
from flask import render_template

def maintenance(f):
    def wrapper(*args, **kwargs):
        if os.environ.get("MAINTENANCE_MODE") == "ON":
            return render_template("public/maintenance.html"), 503
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper