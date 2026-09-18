import json

from flask import Blueprint, Response, request, stream_with_context

from DeepBruce_AI.services.ollama import (
    OllamaServiceError,
    stream_chat,
)


bp = Blueprint("api_chat", __name__, url_prefix="/api")


@bp.post("/chat")
def chat():
    body = request.get_json(silent=True)

    if not isinstance(body, dict):
        return {
            "error": {
                "code": "invalid_json",
                "message": "O corpo da requisição deve ser um JSON válido.",
            }
        }, 400

    message = body.get("message")

    if not isinstance(message, str) or not message.strip():
        return {
            "error": {
                "code": "invalid_message",
                "message": "O campo 'message' é obrigatório.",
            }
        }, 400

    message = message.strip()

    def generate():
        try:
            for token in stream_chat(message):
                payload = json.dumps(
                    {"content": token},
                    ensure_ascii=False,
                )

                yield f"event: token\ndata: {payload}\n\n"

            yield "event: done\ndata: {}\n\n"

        except OllamaServiceError as exc:
            payload = json.dumps(
                {
                    "code": exc.code,
                    "message": exc.message,
                },
                ensure_ascii=False,
            )

            yield f"event: error\ndata: {payload}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )