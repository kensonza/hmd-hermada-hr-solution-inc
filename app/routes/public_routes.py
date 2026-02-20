from flask import Blueprint, render_template
from app.controller.maintenance import maintenance
#from app.extension import db
#from app.models import Users, PhotoSlider, NewsFeed, YouTube, Gallery, GalleryAlbum
#import feedparser

# Flask Blueprint (Public Route)
pubroute = Blueprint('public_route', __name__, template_folder='templates/public')    

# Index (Home Page)
@pubroute.route('/')
@maintenance
def index():
    return render_template('public/index.html', nav_active='index')

# About Us
@pubroute.route('/about')
@maintenance
def about():
    return render_template('public/about.html', nav_active='about', page='about')

# Our Services
@pubroute.route('/our-services')
@maintenance
def services():
    return render_template('public/our-services.html', nav_active='our-services', page='services')

# Careers
@pubroute.route('/careers')
@maintenance
def careers():
    return render_template('public/careers.html', nav_active='careers', page='careers')

# Contact
@pubroute.route('/contact')
@maintenance
def contact():

    return render_template('public/contact.html', nav_active='contact', page='contact')

# Maintenance
@pubroute.route('/maintenance')
@maintenance
def maintenance_page():

    return render_template('public/maintenance.html', nav_active='maintenance', page='maintenance')