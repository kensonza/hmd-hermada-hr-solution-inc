# app/views/__init__.py
from flask import Blueprint, render_template

# Flask Blueprint 
# Public and Templates Linked Route
pubroute = Blueprintroute = Blueprint('public_route', __name__, template_folder='templates/public')       # public route
tmproute = Blueprintroute = Blueprint('public_tmp_route', __name__, template_folder='templates/public')   # templates linked route

# Admin Route
admroute = Blueprintroute = Blueprint('admin_route', __name__, template_folder='templates/admin')         # admin route

# Blueprint import statements
from app.views import public_route, public_tmp_route  # public route
from app.views import admin_route                     # admin_route.py