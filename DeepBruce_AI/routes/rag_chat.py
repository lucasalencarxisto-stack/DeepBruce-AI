import json

from flask import (
    Blueprint,
    Response,
    current_app,
    request,
    stream_with_context,
)

from DeepBruce_AI.services import ollama
from DeepBruce_AI.services.rag import stream_rag_answer


bp = Blueprint(
    "api_rag_chat",
    __name__,
    url_prefix="/api/rag",
)


@bp.post("/chat")
def rag_chat():
    body = request.get_json(silent=True)

    if not isinstance(body, dict):
        return {
            "error": {
                "code": "invalid_json",
                "message": (
                    "O corpo da requisição deve ser "
                    "um JSON válido."
                ),
            }
        }, 400

    message = body.get("message")

    if (
        not isinstance(message, str)
        or not message.strip()
    ):
        return {
            "error": {
                "code": "invalid_message",
                "message": (
                    "O campo 'message' é obrigatório."
                ),
            }
        }, 400

    message = message.strip()

    max_message_length = current_app.config[
        "SETTINGS"
    ].max_message_length

    if len(message) > max_message_length:
        return {
            "error": {
                "code": "message_too_long",
                "message": (
                    "A mensagem excede o limite de "
                    f"{max_message_length} caracteres."
                ),
            }
        }, 400

    def generate():
        try:
            for item in stream_rag_answer(
                message,
                current_app.config["SETTINGS"],
            ):
                if item["type"] == "sources":
                    payload = json.dumps(
                        {
                            "sources": item["sources"],
                        },
                        ensure_ascii=False,
                    )

                    yield (
                        "event: sources\n"
                        f"data: {payload}\n\n"
                    )

                elif item["type"] == "token":
                    payload = json.dumps(
                        {
                            "content": item["content"],
                        },
                        ensure_ascii=False,
                    )

                    yield (
                        "event: token\n"
                        f"data: {payload}\n\n"
                    )

            yield (
                "event: done\n"
                "data: {}\n\n"
            )

        except ollama.OllamaServiceError as exc:
            payload = json.dumps(
                {
                    "code": exc.code,
                    "message": exc.message,
                },
                ensure_ascii=False,
            )

            yield (
                "event: error\n"
                f"data: {payload}\n\n"
            )

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )