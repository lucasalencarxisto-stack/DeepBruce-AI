# ──────────────────────────────────────────────────────────────────────────────
# [PT-BR] app/__init__.py – Inicialização do Flask, headers de segurança (CORS/CSP),
#         e endpoints de chat compatíveis com Ollama e estilo OpenAI.
# [EN]    app/__init__.py – Flask bootstrap, security headers (CORS/CSP),
#         and chat endpoints compatible with Ollama and OpenAI‑style API.
# [ES]    app/__init__.py – Inicialización de Flask, cabeceras de seguridad (CORS/CSP),
#         y endpoints de chat compatibles con Ollama y estilo OpenAI.
# [中文]   app/__init__.py – Flask 启动、CORS/CSP 安全响应头，以及与 Ollama 和 OpenAI 风格兼容的聊天端点。
# ──────────────────────────────────────────────────────────────────────────────

import os
import json
import time
from typing import Tuple, Iterable
from flask import (
    Flask,
    jsonify,
    request,
    Response,
    stream_with_context,
    send_from_directory,
)

from .ollama_client import list_models, chat_once, generate_stream

# --- Flask: static = app/static ------------------------------------------------
# [PT-BR] Define a pasta de arquivos estáticos (SPA front).  
# [EN]    Defines static folder (SPA front).  
# [ES]    Define la carpeta estática (front SPA).
# [中文]   指定静态文件目录（SPA 前端）。
STATIC_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static")
app = Flask(__name__, static_folder=STATIC_DIR)

# --- Config -------------------------------------------------------------------
# [PT-BR] Lê variáveis de ambiente com defaults seguros.  
# [EN]    Reads environment variables with safe defaults.  
# [ES]    Lee variables de entorno con valores por defecto seguros.
# [中文]   从环境变量读取配置并提供安全的默认值。
API_TITLE = os.getenv("APP_NAME", "portifolio-chat API")
API_VERSION = os.getenv("APP_VERSION", "0.1.0")

# [PT-BR] Base URL do servidor Ollama (ex.: http://ollama:11434).  
# [EN]    Ollama server base URL (e.g., http://ollama:11434).  
# [ES]    URL base del servidor Ollama (p. ej., http://ollama:11434).
# [中文]   Ollama 服务器基础地址（如：http://ollama:11434）。
OLLAMA_BASE_URL = (os.getenv("OLLAMA_BASE_URL", "").strip().rstrip("/"))

# [PT-BR] Modelo padrão e hiperparâmetros.  
# [EN]    Default model and hyperparameters.  
# [ES]    Modelo por defecto y hiperparámetros.
# [中文]   默认模型与超参数。
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b").strip()
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "1024"))
OLLAMA_NUM_PRED = int(os.getenv("OLLAMA_NUM_PREDICT", "128"))

# [PT-BR] Prompt de sistema opcional (usado pelo cliente); aqui só indicamos presença.  
# [EN]    Optional system prompt (used by client); we only indicate presence here.  
# [ES]    Prompt de sistema opcional (utilizado por el cliente); aquí solo indicamos presencia.
# [中文]   可选的系统提示（由客户端使用）；此处仅标记是否存在。
OQS_SYSTEM_PROMPT = os.getenv("OQS_SYSTEM_PROMPT", "").strip()


# --- CORS/CSP básico ----------------------------------------------------------
@app.after_request
def _headers(resp: Response) -> Response:
    """
    [PT-BR] Anexa cabeçalhos padrão de CORS, CSP e segurança a todas as respostas.
    [EN]    Attaches standard CORS, CSP and security headers to every response.
    [ES]    Adjunta cabeceras estándar de CORS, CSP y seguridad a todas las respuestas.
    [中文]   为所有响应附加标准的 CORS、CSP 和安全标头。
    """
    # [PT-BR] CORS permissivo (ajuste em produção).  
    # [EN]    Permissive CORS (tune for production).  
    # [ES]    CORS permisivo (ajustar en producción).
    # [中文]   宽松的 CORS（生产环境请按需收紧）。
    resp.headers.setdefault("Access-Control-Allow-Origin", "*")
    resp.headers.setdefault(
        "Access-Control-Allow-Headers", "Content-Type, Authorization"
    )
    resp.headers.setdefault("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    # [PT-BR] CSP: permite conexões com Ollama (http/https), data e blob (SSE/streams/ws).  
    # [EN]    CSP: allow connections to Ollama (http/https), data and blob (SSE/streams/ws).  
    # [ES]    CSP: permite conexiones a Ollama (http/https), data y blob (SSE/streams/ws).
    # [中文]   CSP：允许连接到 Ollama（http/https）、data 与 blob（SSE/流/WS）。
    connect_src = ["'self'", "http:", "https:", "data:", "blob:"]
    if OLLAMA_BASE_URL:
        # [PT-BR] Libera host específico do Ollama.  
        # [EN]    Allow Ollama specific host.  
        # [ES]    Permite host específico de Ollama.
        try:
            host = OLLAMA_BASE_URL.split("://", 1)[1]
            connect_src.append(f"http://{host}")
            connect_src.append(f"https://{host}")
        except Exception:
            pass

    csp = (
        "default-src 'self'; "
        "img-src 'self' data:; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'; "
        f"connect-src {' '.join(connect_src)}"
    )
    resp.headers.setdefault("Content-Security-Policy", csp)

    # [PT-BR] Cabeçalhos adicionais de segurança/stream.  
    # [EN]    Additional security/stream headers.  
    # [ES]    Cabeceras adicionales de seguridad/stream.
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("Referrer-Policy", "no-referrer")
    resp.headers.setdefault("Vary", "Accept-Encoding")
    return resp


# --- Home: serve app/static/index.html ----------------------------------------
@app.get("/")
def index() -> Response:
    """
    [PT-BR] Serve o index do front-end (SPA) ou um placeholder se não existir.
    [EN]    Serves the front-end (SPA) index or a placeholder if it doesn't exist.
    [ES]    Sirve el índice del front-end (SPA) o un placeholder si no existe.
    [中文]   返回前端（SPA）的 index 文件；若不存在则返回占位页面。
    """
    f = os.path.join(app.static_folder, "index.html")
    if os.path.exists(f):
        return send_from_directory(app.static_folder, "index.html")
    return Response(
        "<!doctype html><meta charset='utf-8'><h1>portifolio-chat</h1>"
        "<p>Suba <code>app/static/index.html</code>.</p>",
        mimetype="text/html; charset=utf-8",
    )


# --- Helpers ------------------------------------------------------------------

def _bool_str(v: str) -> bool:
    """
    [PT-BR] Converte strings comuns de boolean para True/False ("1,true,yes,y,on").
    [EN]    Converts common boolean strings to True/False ("1,true,yes,y,on").
    [ES]    Convierte strings booleanos comunes a True/False ("1,true,yes,y,on").
    [中文]   将常见的布尔字符串转换为 True/False（"1,true,yes,y,on"）。
    """
    return str(v).strip().lower() in {"1", "true", "yes", "y", "on"}


def _extract_message() -> str:
    """
    [PT-BR] Extrai o campo 'message' do GET (query) ou POST (JSON).  
    [EN]    Extracts 'message' from GET (query) or POST (JSON).  
    [ES]    Extrae 'message' del GET (query) o POST (JSON).
    [中文]   从 GET（查询参数）或 POST（JSON）中提取 'message' 字段。
    """
    if request.method == "GET":
        raw = request.args.get("message")
    else:
        data = request.get_json(silent=True) or {}
        raw = data.get("message")
    return (str(raw).strip()) if raw is not None else ""


def _extract_stream_flag() -> bool:
    """
    [PT-BR] Lê o parâmetro 'stream' (query ou JSON) e normaliza para bool.  
    [EN]    Reads 'stream' (query or JSON) and normalizes to bool.  
    [ES]    Lee 'stream' (query o JSON) y normaliza a bool.
    [中文]   读取 'stream' 参数（查询或 JSON）并归一化为布尔值。
    """
    q = request.args.get("stream")
    if q is not None:
        return _bool_str(q)
    if request.method != "GET":
        v = (request.get_json(silent=True) or {}).get("stream")
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return _bool_str(v)
    return False


def _override_model_and_predict() -> Tuple[str, int]:
    """
    [PT-BR] Permite sobrescrever o modelo e o num_predict via query (model, num_predict).  
    [EN]    Allows overriding model and num_predict via query (model, num_predict).  
    [ES]    Permite sobrescribir el modelo y num_predict vía query (model, num_predict).
    [中文]   允许通过查询参数覆盖模型与 num_predict（model, num_predict）。
    """
    model = (request.args.get("model") or OLLAMA_MODEL).strip()
    np = request.args.get("num_predict")
    try:
        num_predict = int(np) if np is not None else OLLAMA_NUM_PRED
    except Exception:
        num_predict = OLLAMA_NUM_PRED
    return model, num_predict


def _json_error(msg: str, code: int = 400):
    """
    [PT-BR] Formata um erro JSON compatível com APIs REST.  
    [EN]    Formats a JSON error compatible with REST APIs.  
    [ES]    Da formato a un error JSON compatible con APIs REST.
    [中文]   格式化一个符合 REST API 的 JSON 错误响应。
    """
    return jsonify({"error": {"message": msg, "type": "invalid_request_error"}}), code


# --- Endpoints básicos --------------------------------------------------------
@app.get("/config")
def config():
    """
    [PT-BR] Expõe configuração efetiva do backend (sem segredos).  
    [EN]    Exposes backend effective configuration (no secrets).  
    [ES]    Expone la configuración efectiva del backend (sin secretos).
    [中文]   暴露后端的有效配置（不包含机密）。
    """
    return jsonify(
        {
            "base": OLLAMA_BASE_URL or None,
            "model": OLLAMA_MODEL,
            "num_ctx": OLLAMA_NUM_CTX,
            "num_predict": OLLAMA_NUM_PRED,
            "system_prompt": bool(OQS_SYSTEM_PROMPT),
            "api": {"title": API_TITLE, "version": API_VERSION},
        }
    )


@app.get("/health")
def health():
    """
    [PT-BR] Healthcheck simples (poderia pingar Ollama diretamente).  
    [EN]    Simple healthcheck (could ping Ollama directly).  
    [ES]    Healthcheck simple (podría hacer ping a Ollama directamente).
    [中文]   简单的健康检查（也可以直接 ping Ollama）。
    """
    provider = "ollama" if OLLAMA_BASE_URL else "local-echo"
    return jsonify({"status": "ok", "model": OLLAMA_MODEL, "provider": provider})


@app.get("/models")
def models():
    """
    [PT-BR] Lista modelos disponíveis no Ollama.  
    [EN]    Lists available models in Ollama.  
    [ES]    Lista los modelos disponibles en Ollama.
    [中文]   列出 Ollama 可用的模型。
    """
    return jsonify(
        {"models": list_models(OLLAMA_BASE_URL, OLLAMA_TIMEOUT, OLLAMA_MODEL)}
    )


# --- /chat (GET/POST) ---------------------------------------------------------
@app.route("/chat", methods=["GET", "POST", "OPTIONS"])
def chat():
    """
    [PT-BR] Endpoint mínimo de chat. GET/POST aceitam 'message'; 'stream' habilita fluxo.  
    [EN]    Minimal chat endpoint. GET/POST accept 'message'; 'stream' enables streaming.  
    [ES]    Endpoint mínimo de chat. GET/POST aceptan 'message'; 'stream' habilita streaming.
    [中文]   最小聊天端点。GET/POST 接受 'message'；'stream' 开启流式输出。
    """
    if request.method == "OPTIONS":
        return Response(status=204)

    msg = _extract_message()
    if not msg:
        return _json_error("Campo 'message' é obrigatório.", 400)

    model, num_predict = _override_model_and_predict()
    stream = _extract_stream_flag()

    if stream:
        # [PT-BR] Texto simples com heartbeats. Para SSE, troque o mimetype.  
        # [EN]    Plain text with heartbeats. For SSE, switch mimetype.  
        # [ES]    Texto plano con latidos. Para SSE, cambie el mimetype.
        # [中文]   以纯文本返回，并包含心跳（:hb）。如需 SSE，请更改 mimetype。
        gen = generate_stream(
            msg,
            base_url=OLLAMA_BASE_URL,
            model=model,
            num_ctx=OLLAMA_NUM_CTX,
            num_predict=num_predict,
            timeout=OLLAMA_TIMEOUT,
        )
        return Response(
            stream_with_context(gen),
            mimetype="text/plain; charset=utf-8",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    reply, provider = chat_once(
        msg,
        base_url=OLLAMA_BASE_URL,
        model=model,
        num_ctx=OLLAMA_NUM_CTX,
        num_predict=num_predict,
        timeout=OLLAMA_TIMEOUT,
    )
    return jsonify({"provider": provider, "reply": reply})


# --- OpenAI-compatible mínimos ------------------------------------------------
@app.get("/v1/models")
def v1_models():
    """
    [PT-BR] Endpoint compatível com OpenAI para listar modelos.  
    [EN]    OpenAI‑compatible endpoint to list models.  
    [ES]    Endpoint compatible con OpenAI para listar modelos.
    [中文]   与 OpenAI 兼容的模型列表端点。
    """
    data = [
        {"id": m["id"], "object": "model"}
        for m in list_models(OLLAMA_BASE_URL, OLLAMA_TIMEOUT, OLLAMA_MODEL)
    ]
    return jsonify({"object": "list", "data": data})


def _stream_openai_style(
    prompt: str, model: str, num_ctx: int, num_predict: int
) -> Iterable[bytes]:
    """
    [PT-BR] Converte chunks do gerador em eventos SSE estilo OpenAI.  
    [EN]    Converts generator chunks into OpenAI‑style SSE events.  
    [ES]    Convierte los chunks del generador en eventos SSE al estilo OpenAI.
    [中文]   将生成器片段转换为 OpenAI 风格的 SSE 事件。
    """
    for piece in generate_stream(
        prompt,
        base_url=OLLAMA_BASE_URL,
        model=model,
        num_ctx=num_ctx,
        num_predict=num_predict,
        timeout=OLLAMA_TIMEOUT,
    ):
        # [PT-BR] Mantém heartbeats como comentários SSE (linhas com ":").  
        # [EN]    Keep heartbeats as SSE comments (lines starting with ":").  
        # [ES]    Mantiene latidos como comentarios SSE (líneas que empiezan con ":").
        # [中文]   将心跳作为 SSE 注释保留（以冒号开头的行）。
        if piece.startswith(":"):
            # [PT-BR] Garante quebra dupla, conforme SSE.  
            # [EN]    Ensure double break per SSE.  
            # [ES]    Asegura doble salto por SSE.
            # [中文]   确保按 SSE 规范进行双换行。
            yield (piece.rstrip("\n") + "\n").encode("utf-8")
            continue

        j = json.dumps(
            {
                "id": "cmpl-stream",
                "object": "chat.completion.chunk",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": piece.rstrip("\n")},
                        "finish_reason": None,
                    }
                ],
                "model": model,
            }
        )
        yield f"data: {j}\n\n".encode("utf-8")

    yield b"data: [DONE]\n\n"


@app.route("/v1/chat/completions", methods=["POST", "OPTIONS"])
def v1_chat_completions():
    """
    [PT-BR] Endpoint /v1/chat/completions compatível (mínimo) com OpenAI.  
    [EN]    Minimal OpenAI‑compatible /v1/chat/completions endpoint.  
    [ES]    Endpoint /v1/chat/completions compatible (mínimo) con OpenAI.
    [中文]   与 OpenAI 兼容（最小实现）的 /v1/chat/completions 端点。
    """
    if request.method == "OPTIONS":
        return Response(status=204)

    data = request.get_json(silent=True) or {}
    messages = data.get("messages") or []
    req_model = (data.get("model") or OLLAMA_MODEL).strip()
    stream = bool(data.get("stream", False))

    # [PT-BR] Captura o último conteúdo textual válido.  
    # [EN]    Capture the last valid textual content.  
    # [ES]    Captura el último contenido textual válido.
    # [中文]   提取最后一个有效的文本内容。
    last = ""
    for m in messages:
        role = (m.get("role") or "").strip()
        if role in ("user", "system", "assistant"):
            c = m.get("content")
            if isinstance(c, str) and c.strip():
                last = c.strip()
    if not last:
        return _json_error("Campo 'messages' inválido ou vazio.", 400)

    model = req_model or OLLAMA_MODEL
    num_predict = OLLAMA_NUM_PRED

    if stream:
        return Response(
            stream_with_context(
                _stream_openai_style(
                    last, model=model, num_ctx=OLLAMA_NUM_CTX, num_predict=num_predict
                )
            ),
            mimetype="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    reply, _provider = chat_once(
        last,
        base_url=OLLAMA_BASE_URL,
        model=model,
        num_ctx=OLLAMA_NUM_CTX,
        num_predict=num_predict,
        timeout=OLLAMA_TIMEOUT,
    )
    resp = {
        "id": "cmpl-nonstream",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {"index": 0, "message": {"role": "assistant", "content": reply}, "finish_reason": "stop"}
        ],
        "usage": {
            # [PT-BR] Preencher se desejar (token counts).  
            # [EN]    Fill if desired (token counts).  
            # [ES]    Completar si se desea (conteo de tokens).
            # [中文]   如需可填写（token 统计）。
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
        },
    }
    return jsonify(resp)
