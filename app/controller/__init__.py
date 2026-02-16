# app/controller/__init__.py
from .auth import auth
from .admin_controller import admcontroller
from .public_controller import pubcontroller

# Blueprint Registration (Public, Admin Controller)
def register_blueprints_controller(app):
    for controller_bp in [auth, pubcontroller, admcontroller]:
        app.register_blueprint(controller_bp)