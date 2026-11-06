from src.views.task_routes import task_bp
from src.views.user_routes import user_bp
from src.views.report_routes import report_bp
from src.middlewares.auth import admin_blueprint_guard


def register_routes(app):
    admin_blueprint_guard(task_bp)
    admin_blueprint_guard(report_bp)
    admin_blueprint_guard(user_bp, {"users.login"})
    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)
