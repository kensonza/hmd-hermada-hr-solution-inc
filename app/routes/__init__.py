# app/routes/__init__.py
from .public_routes import pubroute
from .admin_routes import admroute

# Blueprint Registration (Public, Template Link, Admin)
def register_blueprints_routes(app):
    for routes_bp in [pubroute, admroute]:
        app.register_blueprint(routes_bp)