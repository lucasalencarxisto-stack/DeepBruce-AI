import os, json, time
from typing import Generator, Tuple
from urllib import request as urlreq
from flask import Flask, jsonify, request, Response, stream_with_context, send_from_directory

# --- Flask: static = app/static ------------------------------------------------
STATIC_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static")
app = Flask(__name__, static_folder=STATIC_DIR)

# --- Config -------------------------------------------------------------------
API_TITLE   = os.getenv("APP_NAME", "portifolio-chat API")
API_VERSION = os.getenv("APP_VERSION", "0.1.0")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "").strip()           # ex: http://ollama:11434
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "llama3.2:1b").strip()
OLLAMA_TIMEOUT  = int(os.getenv("OLLAMA_TIMEOUT", "120"))
OLLAMA_NUM_CTX  = int(os.getenv("OLLAMA_NUM_CTX", "1024"))
OLLAMA_NUM_PRED = int(os.getenv("OLLAMA_NUM_PREDICT", "128"))
OQS_SYSTEM_PROMPT = os.getenv("OQS_SYSTEM_PROMPT", "").strip()

# --- CORS/CSP básico ----------------------------------------------------------
@app.after_request
def _headers(resp):
    resp.headers.setdefault("Access-Control-Allow-Origin", "*")
    resp.headers.setdefault("Access-Control-Allow-Headers", "Content-Type, Authorization")
    resp.headers.setdefault("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    resp.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; connect-src 'self'; img-src 'self' data:; "
        "style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'"
    )
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("Referrer-Policy", "no-referrer")
    return resp

# --- Home: serve app/static/index.html ----------------------------------------
@app.get("/")
def index():
    f = os.path.join(app.static_folder, "index.html")
    if os.path.exists(f):
        return send_from_directory(app.static_folder, "index.html")
    return Response(
        "<!doctype html><meta charset='utf-8'><h1>portifolio-chat</h1>"
        "<p>Suba <code>app/static/index.html</code>.</p>", mimetype="text/html"
    )

# --- Helpers ------------------------------------------------------------------
def _bool_str(v: str) -> bool:
    return str(v).strip().lower() in {"1","true","yes","y","on"}

def _extract_message() -> str:
    if request.method == "GET":
        raw = request.args.get("message")
    else:
        data = request.get_json(silent=True) or {}
        raw = data.get("message")
    return (str(raw).strip()) if raw is not None else ""

def _extract_stream_flag() -> bool:
    q = request.args.get("stream")
    if q is not None:
        return _bool_str(q)
    if request.method != "GET":
        v = (request.get_json(silent=True) or {}).get("stream")
        if isinstance(v, bool): return v
        if isinstance(v, str):  return _bool_str(v)
    return False

def _override_model_and_predict() -> Tuple[str, int]:
    model = (request.args.get("model") or OLLAMA_MODEL).strip()
    np = request.args.get("num_predict")
    try:
        num_predict = int(np) if np is not None else OLLAMA_NUM_PRED
    except Exception:
        num_predict = OLLAMA_NUM_PRED
    return model, num_predict

def _json_error(msg: str, code: int = 400):
    return jsonify({"error": {"message": msg, "type": "invalid_request_error"}}), code

def _ollama_tags() -> list:
    if not OLLAMA_BASE_URL:
        return [{"id": OLLAMA_MODEL}]
    try:
        req = urlreq.Request(f"{OLLAMA_BASE_URL}/api/tags", method="GET",
                             headers={"Content-Type": "application/json"})
        with urlreq.urlopen(req, timeout=OLLAMA_TIMEOUT) as r:
            payload = json.loads(r.read().decode("utf-8"))
        items = payload.get("models") or []
        out = []
        for m in items:
            name = (m.get("name") or m.get("model") or "").strip()
            if name: out.append({"id": name})
        return out or [{"id": OLLAMA_MODEL}]
    except Exception:
        return [{"id": OLLAMA_MODEL}]

# --- Ollama calls -------------------------------------------------------------
def _ollama_generate_stream(prompt: str, model: str, num_ctx: int, num_predict: int) -> Generator[str, None, None]:
    yield ":preamble\n"  # mantém worker vivo
    if not OLLAMA_BASE_URL:
        yield f"Você disse: {prompt}\n"; return

    body = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {"num_ctx": num_ctx, "num_predict": num_predict},
    }
    req = urlreq.Request(
        f"{OLLAMA_BASE_URL}/api/generate",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    last_hb, hb_gap = time.monotonic(), 2.0
    try:
        with urlreq.urlopen(req, timeout=OLLAMA_TIMEOUT) as r:
            for raw in r:
                now = time.monotonic()
                if now - last_hb >= hb_gap:
                    yield ":hb\n"; last_hb = now
                if not raw: continue
                try:
                    obj = json.loads(raw.decode("utf-8"))
                except Exception:
                    continue
                chunk = obj.get("response", "")
                if chunk:
                    yield chunk + "\n"
                    last_hb = time.monotonic()
                if obj.get("done"):
                    break
    except Exception as e:
        yield f"\n[degradado:{type(e).__name__}] Você disse: {prompt}\n"

def _ask_ollama_once(msg: str, model: str, num_ctx: int, num_predict: int) -> Tuple[str, str]:
    fallback = f"Você disse: {msg}"
    if not OLLAMA_BASE_URL:
        return fallback, "local-echo"
    body = {
        "model": model,
        "messages": [{"role": "user", "content": msg}],
        "stream": False,
        "options": {"num_ctx": num_ctx, "num_predict": num_predict},
    }
    try:
        req = urlreq.Request(
            f"{OLLAMA_BASE_URL}/api/chat",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlreq.urlopen(req, timeout=OLLAMA_TIMEOUT) as r:
            payload = json.loads(r.read().decode("utf-8"))
        reply = (payload.get("message") or {}).get("content") or payload.get("response")
        if not reply: return fallback, "ollama-empty"
        return reply, f"ollama:chat:{model}"
    except Exception as e:
        return f"[degradado:{type(e).__name__}] {fallback}", "degraded"

# --- Endpoints básicos --------------------------------------------------------
@app.get("/config")
def config():
    return jsonify({
        "base": OLLAMA_BASE_URL or None,
        "model": OLLAMA_MODEL,
        "num_ctx": OLLAMA_NUM_CTX,
        "num_predict": OLLAMA_NUM_PRED,
        "system_prompt": bool(OQS_SYSTEM_PROMPT),
    })

@app.get("/health")
def health():
    return jsonify({"status": "ok", "model": OLLAMA_MODEL, "provider": "ollama" if OLLAMA_BASE_URL else "local-echo"})

@app.get("/models")
def models():
    return jsonify({"models": _ollama_tags()})

@app.route("/chat", methods=["GET","POST","OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return Response(status=204)
    msg = _extract_message()
    if not msg: return _json_error("Campo 'message' é obrigatório.", 400)

    model, num_predict = _override_model_and_predict()
    stream = _extract_stream_flag()

    if stream:
        gen = _ollama_generate_stream(msg, model=model, num_ctx=OLLAMA_NUM_CTX, num_predict=num_predict)
        return Response(stream_with_context(gen), mimetype="text/plain")
    reply, provider = _ask_ollama_once(msg, model=model, num_ctx=OLLAMA_NUM_CTX, num_predict=num_predict)
    return jsonify({"provider": provider, "reply": reply})
