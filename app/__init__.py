import os
from app.extension import db
from flask import Flask, request, render_template
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_mail import Mail

# Absolute import after db is initialized
from app.models import Users
from app.models import Contact
from app.models import Newsletter
from app.models import NewsletterSubscribers

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

# ReCAPTCHA Secret Key
app.config['RECAPTCHA_SECRET_KEY'] = os.getenv('RECAPTCHA_SECRET_KEY')

# Configure Flask-Mail
# Hostinger
app.config.update(
    MAIL_SERVER='smtp.hostinger.ph',             # Gmail SMTP server
    MAIL_PORT=587,
    MAIL_USE_SSL=False,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv('EMAIL'),         # Your email
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD')  # Your email password or app-specific password
)
app.config['MAIL_DEBUG'] = True

mail = Mail(app)

# Security Key
app.secret_key = os.urandom(32)
csrf = CSRFProtect(app)

# Route for robots.txt
@app.route('/robots.txt')
def robots_txt():
    return app.send_static_file('robots.txt')

# Route for sitemap.xml (static folder)
@app.route('/sitemap.xml')
def sitemap():
    return app.send_static_file('sitemap.xml')

# Checking Invalid Route
@app.errorhandler(404)
def invalid_route(e):
    print("404 path:", request.path)
    
    if request.path.startswith('/hidden/admin-panel'):
        
        return render_template('admin/404.html'), 404

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