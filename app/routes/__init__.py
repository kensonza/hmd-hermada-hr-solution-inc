# app/routes/__init__.py
from .public_routes import pubroute
from .public_tmp_routes import tmproute
from .admin_routes import admroute

# Blueprint Registration (Public, Template Link, Admin)
def register_blueprints_routes(app):
    for routes_bp in [pubroute, tmproute, admroute]:
        app.register_blueprint(routes_bp)