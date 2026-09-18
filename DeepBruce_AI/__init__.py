from flask import Flask, render_template
from flask_cors import CORS

from .config import Settings

def create_app():
    app = Flask(
        __name__,
        static_folder="../static",
        template_folder="../templates"
    )
    settings = Settings.from_env()
    app.config["SETTINGS"] = settings

    cors_origins = settings.cors_origins
    if cors_origins:
        CORS(app, origins=[origin.strip() for origin in cors_origins.split(",") if origin.strip()])

    # Blueprints do chat (two-step + single)
    from .POST.chat_endpoints import bp as chat_bp
    app.register_blueprint(chat_bp)

    from .routes.chat import bp as api_chat_bp
    from .routes.health import bp as health_bp
    app.register_blueprint(api_chat_bp)
    app.register_blueprint(health_bp)

    @app.get("/")
    def home():
        return render_template("index.html")

    return app
