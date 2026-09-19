import json
import requests
from flask import Blueprint, current_app, request, Response, stream_with_context, jsonify

# 1) Cria o Blueprint ANTES de usar decorators
bp = Blueprint("chat", __name__)

# 3) Memória simples para Flow1 (POST /chat -> GET /stream)
_last_query = {"text": "Diga oi em PT-BR."}

def _ollama_stream_chat(prompt: str):
    """Stream da API /api/chat do Ollama, yield de tokens."""
    settings = current_app.config["SETTINGS"]
    url = f"{settings.ollama_host}/api/chat"
    payload = {
        "model": settings.ollama_model,
        "messages": [
            {"role": "system", "content": "Responda sempre em PT-BR, claro e conciso."},
            {"role": "user", "content": prompt}
        ],
        "stream": True,
        "options": {
            "temperature": 0.6,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
            "num_predict": 256
        }
    }
    with requests.post(
        url,
        json=payload,
        stream=True,
        timeout=(settings.ollama_connect_timeout, settings.ollama_read_timeout),
    ) as r:
        r.raise_for_status()
        for raw in r.iter_lines(decode_unicode=False):
            if not raw:
                continue
            line = raw.strip()
            if line.startswith(b"data: "):
                line = line[6:]
            try:
                data = json.loads(line.decode("utf-8", errors="ignore"))
            except Exception:
                continue
            msg = data.get("message", {})
            chunk = msg.get("content", "")
            if chunk:
                yield chunk
            if data.get("done"):
                break

@bp.route("/chat", methods=["POST"])
def chat():
    body = request.get_json(force=True) or {}
    query = (body.get("query") or "").strip()
    if not query:
        query = "Diga oi em PT-BR."  # fallback se vier vazio
    _last_query["text"] = query
    return jsonify({"status": "ok"})

@bp.route("/stream", methods=["GET"])
def stream():
    query = _last_query["text"]

    def gen():
        for token in _ollama_stream_chat(query):
            yield f"data: {token}\n\n"
        yield "event: done\ndata: [DONE]\n\n"

    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "text/event-stream",
        "X-Accel-Buffering": "no",
        "Connection": "keep-alive",
    }
    return Response(stream_with_context(gen()), headers=headers)

@bp.route("/stream2", methods=["POST"])
def stream2():
    body = request.get_json(force=True) or {}
    query = (body.get("query") or "").strip()
    if not query:
        query = "Diga oi em PT-BR."  # fallback se vier vazio

    def gen():
        for token in _ollama_stream_chat(query):
            yield f"data: {token}\n\n"
        yield "event: done\ndata: [DONE]\n\n"

    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "text/event-stream",
        "X-Accel-Buffering": "no",
        "Connection": "keep-alive",
    }
    return Response(stream_with_context(gen()), headers=headers)
