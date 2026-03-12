from flask import Flask

from app_core.config import SECRET_KEY
from app_core.routes.admin import admin_bp
from app_core.routes.main import main_bp
from app_core.storage import init_storage


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.secret_key = SECRET_KEY
    init_storage()

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app
