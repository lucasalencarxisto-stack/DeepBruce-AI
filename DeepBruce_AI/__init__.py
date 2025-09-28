from flask import Flask, render_template
from flask_cors import CORS
import os

# se usar .env no dev local, descomente:
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

def create_app():
    app = Flask(
        __name__,
        static_folder="../static",
        template_folder="../templates"
    )
    CORS(app)

    app.config["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
    app.config["OQS_NAMESPACE"] = os.getenv("OQS_NAMESPACE", "default")

    # Blueprints do chat (two-step + single)
    from .POST.chat_endpoints import bp as chat_bp
    app.register_blueprint(chat_bp)

    @app.get("/")
    def home():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return {"status": "ok", "namespace": app.config["OQS_NAMESPACE"]}

    return app
