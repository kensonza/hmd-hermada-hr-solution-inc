from flask import Blueprint, render_template
#from app.extension import db
#from app.models import Users, PhotoSlider, NewsFeed, YouTube, Gallery, GalleryAlbum
#import feedparser

# Flask Blueprint (Public Route)
pubroute = Blueprint('public_route', __name__, template_folder='templates/public')    

# Index (Home Page)
@pubroute.route('/')
def index():
    return render_template('public/index.html', nav_active='index')

# About Us
@pubroute.route('/about')
def about():
    return render_template('public/about.html', nav_active='about')

# Our Services
@pubroute.route('/our-services')
def services():
    return render_template('public/our-services.html', nav_active='our-services')

# Careers
@pubroute.route('/careers')
def careers():
    return render_template('public/careers.html', nav_active='careers')

# Contact
@pubroute.route('/contact')
def contact():

    return render_template('public/contact.html', nav_active='contact')