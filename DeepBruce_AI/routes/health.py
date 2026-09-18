from flask import Blueprint, current_app


bp = Blueprint("health", __name__)


@bp.get("/health")
def health():
    return {
        "status": "ok",
        "namespace": current_app.config["SETTINGS"].oqs_namespace,
    }