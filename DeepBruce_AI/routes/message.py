import json
from uuid import uuid4

from flask import (
    Blueprint,
    Response,
    current_app,
    request,
    stream_with_context,
)

from DeepBruce_AI.config import Settings
from DeepBruce_AI.services import ollama
from DeepBruce_AI.services.orchestrator import (
    DeepBruceOrchestrator,
)


api_message_bp = Blueprint(
    "api_message",
    __name__,
    url_prefix="/api",
)

# Alias mantido por compatibilidade com create_app().
# Compatibilidade com:
# from .routes.message import bp as api_message_bp
bp = api_message_bp

orchestrator = DeepBruceOrchestrator()


def _sse_event(
    event_name: str,
    payload: dict,
) -> str:
    data = json.dumps(
        payload,
        ensure_ascii=False,
    )

    return (
        f"event: {event_name}\n"
        f"data: {data}\n\n"
    )


@api_message_bp.post("/message")
def message():
    payload = request.get_json(
        silent=True
    )

    if not isinstance(payload, dict):
        return {
            "error": "invalid_json",
            "message": (
                "O corpo da requisição deve ser JSON."
            ),
        }, 400

    user_message = (
        payload.get("message")
        or ""
    ).strip()

    if not user_message:
        return {
            "error": "empty_message",
            "message": (
                "O campo message é obrigatório."
            ),
        }, 400

    raw_conversation_id = payload.get(
        "conversation_id"
    )

    if raw_conversation_id is None:
        conversation_id = str(
            uuid4()
        )

    elif isinstance(
        raw_conversation_id,
        str,
    ):
        conversation_id = (
            raw_conversation_id.strip()
            or str(uuid4())
        )

    else:
        return {
            "error": (
                "invalid_conversation_id"
            ),
            "message": (
                "conversation_id deve ser "
                "uma string."
            ),
        }, 400

    settings = current_app.config["SETTINGS"]

    @stream_with_context
    def generate():
        try:
            for event in (
                orchestrator.stream_message(
                    user_message,
                    settings,
                    conversation_id=(
                        conversation_id
                    ),
                )
            ):
                event_type = event.get(
                    "type",
                    "message",
                )

                event_payload = {
                    key: value
                    for key, value
                    in event.items()
                    if key != "type"
                }

                yield _sse_event(
                    event_type,
                    event_payload,
                )

            yield _sse_event(
                "done",
                {},
            )

        except ollama.OllamaServiceError as exc:
            current_app.logger.exception(
                "Ollama error in /api/message"
            )

            yield _sse_event(
                "error",
                {
                    "code": "ollama_error",
                    "message": str(exc),
                },
            )

            yield _sse_event(
                "done",
                {},
            )

        except Exception:
            current_app.logger.exception(
                "Unexpected error in /api/message"
            )

            yield _sse_event(
                "error",
                {
                    "code": "internal_error",
                    "message": (
                        "O DeepBruce encontrou "
                        "um erro interno."
                    ),
                },
            )

            yield _sse_event(
                "done",
                {},
            )

    response = Response(
        generate(),
        mimetype="text/event-stream",
    )

    response.headers[
        "Cache-Control"
    ] = "no-cache"

    response.headers[
        "X-Accel-Buffering"
    ] = "no"

    return response