import os
from app.extension import db
from flask import Flask, request, render_template, redirect, session, jsonify
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from dotenv import load_dotenv
#from flask_socketio import SocketIO

# SocketIO Initialization
# socketio = SocketIO(cors_allowed_origins="*")

# Absolute import after db is initialized
from app.models import Users
from app.models import Contact

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# To avoid iframe embedding
@app.after_request
def add_security_headers(response):
    # Block all iframe embedding
    # response.headers['X-Frame-Options'] = 'DENY'
    # Or you can be more flexible:
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response

# SQLAlachemy Connection
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Database Migration
migrate = Migrate(app, db)

# Security Key
app.secret_key = os.urandom(32)
csrf = CSRFProtect(app)

# SocketIO
# socketio.init_app(app)

# Checking Invalid Route
@app.errorhandler(404)
def invalid_route(e):
    print("404 path:", request.path)
    
    # If admin path starts with /hidden/admin-panel
    if request.path.startswith('/hidden/admin-panel'):
        
        return render_template('admin/404.html'), 404

    # Otherwise public
    return render_template('public/404.html'), 404


# Import blueprints (Controller, Routes)
from app.controller import register_blueprints_controller
from app.routes import register_blueprints_routes

# Blueprint Registration (Public, Template Link, Admin)
register_blueprints_controller(app)

# Blueprint Registration (Public, Template Link, Admin)
register_blueprints_routes(app)

if __name__ == '__main__':
    #socketio.run(app, debug=True, host="127.0.0.1")
    app.run(debug=True, host="127.0.0.1")