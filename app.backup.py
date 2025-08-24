# -*- coding: utf-8 -*-
"""
PT-BR: Flask + SSE (básico), histórico por sessão, handler global JSON e diag. via .env.
EN-US: Flask + basic SSE, per-session history, global JSON error handler & diagnostics. Uses .env.
ES:    Flask + SSE básico, historial por sesión, manejador global JSON y diagnósticos. Usa .env.
中文:   Flask + 基础 SSE，会话历史，全局 JSON 错误处理与诊断。使用 .env。
"""

# ========== Imports / Importações / Importaciones / 导入 ==========
import os, json, time, uuid, sys
from collections import defaultdict
from pathlib import Path

from flask import Flask, request, jsonify, Response, stream_with_context, make_response, render_template
from dotenv import load_dotenv
from openai import OpenAI
#import flask_cors                           # usar via módulo evita NameError
from werkzeug.exceptions import HTTPException

# ========== Prints de diagnóstico / Diagnostics / Diagnóstico / 诊断 ==========
print(">> Running app from:", __file__)
print(">> Python:", sys.version)
print(">> flask_cors module path:", getattr(flask_cors, "__file__", "<no file>"))

# ========== Load .env (ao lado do app.py) / Cargar .env / 加载 .env ==========
DOTENV_PATH = Path(__file__).with_name(".env")
load_dotenv(dotenv_path=DOTENV_PATH, override=True, verbose=True)

# ========== App Instance / Instância / Instancia / 应用实例 ==========
app = Flask(__name__, template_folder="templates", static_folder="static")
#flask_cors.CORS(app)                        # PT: habilita CORS / EN: enable CORS / ES / 中
app.jinja_env.cache = {}                    # PT: sem cache em dev / EN: no template cache / ES / 中

# (opcional) espiar variáveis / peek env vars / ver variables / 查看环境变量
def _peek(name, mask=False):
    v = os.getenv(name)
    print(f">> ENV {name}=" + ("<NOT SET>" if v is None else (v[:8] + "***" if mask else v)))
_peek("OPENAI_API_KEY", mask=True)
_peek("OPENAI_ORG_ID")
_peek("OPENAI_PROJECT")
_peek("OPENAI_MODEL")

# ========== Env & Config / Configuração / Configuración / 配置 ==========
# PT: valores crus do ambiente (não validados) / EN: raw env values / ES / 中
RAW_OPENAI_API_KEY       = (os.getenv("OPENAI_API_KEY") or "").strip()
RAW_OPENAI_MODEL         = (os.getenv("OPENAI_MODEL") or "gpt-4o-mini").strip()
RAW_OPENAI_SUMMARY_MODEL = (os.getenv("OPENAI_SUMMARY_MODEL") or "gpt-4o-mini").strip()
RAW_TEMPERATURE          = (os.getenv("OPENAI_TEMPERATURE") or "0.7").strip()
RAW_MAX_TOKENS           = (os.getenv("OPENAI_MAX_TOKENS") or "800").strip()
# PT: suporte a chaves sk-proj- / EN: support for sk-proj- keys / ES / 中
OPENAI_ORG_ID            = (os.getenv("OPENAI_ORG_ID") or "").strip() or None
OPENAI_PROJECT           = (os.getenv("OPENAI_PROJECT") or "").strip() or None

# PT: chave obrigatória / EN: required key / ES / 中
if not RAW_OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY ausente no .env")

# PT: whitelist de modelos + fallback / EN: model whitelist + fallback / ES / 中
ALLOWED_CHAT_MODELS = {"gpt-4o", "gpt-4o-mini"}
def pick_model(env_model: str, default: str = "gpt-4o-mini") -> str:
    m = (env_model or "").strip()
    if m in ALLOWED_CHAT_MODELS:
        return m
    app.logger.warning("OPENAI_MODEL inválido (%s). Usando fallback: %s", m, default)
    return default

# PT: numéricos tolerantes / EN: tolerant numeric parsing / ES / 中
try:
    OPENAI_TEMPERATURE = float(RAW_TEMPERATURE)
except ValueError:
    app.logger.warning("OPENAI_TEMPERATURE inválido (%s). Usando 0.7.", RAW_TEMPERATURE)
    OPENAI_TEMPERATURE = 0.7
try:
    OPENAI_MAX_TOKENS = int(RAW_MAX_TOKENS)
except ValueError:
    app.logger.warning("OPENAI_MAX_TOKENS inválido (%s). Usando 800.", RAW_MAX_TOKENS)
    OPENAI_MAX_TOKENS = 800

OPENAI_MODEL         = pick_model(RAW_OPENAI_MODEL)
OPENAI_SUMMARY_MODEL = pick_model(RAW_OPENAI_SUMMARY_MODEL)

# ========== OpenAI Client / Cliente / Cliente / OpenAI 客户端 ==========
client = OpenAI(
    api_key=RAW_OPENAI_API_KEY,
    organization=OPENAI_ORG_ID,
    project=OPENAI_PROJECT,
)
app.logger.info(
    "OpenAI key prefix: %s*** | model=%s | summary_model=%s | org=%s | proj=%s | T=%.2f | max_tokens=%d",
    RAW_OPENAI_API_KEY[:8], OPENAI_MODEL, OPENAI_SUMMARY_MODEL,
    OPENAI_ORG_ID, OPENAI_PROJECT, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS
)

# ========== Sessions / Sessões / Sesiones / 会话 ==========
sessions = defaultdict(list)

# ========== Utility Functions ==========
def get_or_create_session_id():
    """PT: cookie de sessão / EN: session cookie / ES: cookie de sesión / 中: 会话 Cookie"""
    sid = request.cookies.get("sid")
    if not sid:
        sid = str(uuid.uuid4())
    return sid

def summarize_if_needed(sid: str):
    """PT: corta histórico grande / EN: trim long history / ES: recorta historial / 中: 裁剪长历史"""
    if len(sessions[sid]) > 100:
        sessions[sid] = sessions[sid][-50:]

def sse_event(data: str) -> str:
    """PT/EN/ES/中: formata evento SSE"""
    return f"data: {data}\n\n"

# ========== Middleware (cache/SSE friendly) / 中间件 ==========
@app.after_request
def set_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# ========== Global JSON Error Handler / Manejador global / 全局错误处理 ==========
@app.errorhandler(Exception)
def handle_any_exception(e):
    code = e.code if isinstance(e, HTTPException) else 500
    app.logger.exception("Unhandled error / Erro não tratado / Error no controlado / 未处理错误")
    return jsonify(success=False, error=str(e), type=e.__class__.__name__), code

# ========== Utility Routes / Rotas utilitárias / Rutas / 工具路由 ==========
@app.route("/status", methods=["GET"])
def status():
    """PT: healthcheck / EN: healthcheck / ES: verificación / 中: 健康检查"""
    return jsonify({"status": "ok"})

@app.route("/__template_check", methods=["GET"])
def __template_check():
    """PT: verifica se templates/index.html existe / EN: checks template / ES / 中"""
    p = os.path.join(app.root_path, "templates", "index.html")
    return jsonify(path=p, exists=os.path.exists(p))

@app.route("/__diag_openai", methods=["GET"])
def __diag_openai():
    """PT: testa chave/modelo / EN: quick API diag / ES: diagnóstico / 中: 诊断"""
    try:
        r = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5, temperature=0
        )
        txt = (r.choices[0].message.content or "")[:120]
        return jsonify(ok=True, model=OPENAI_MODEL, reply=txt)
    except Exception as e:
        return jsonify(ok=False, error=str(e), type=e.__class__.__name__), 500

# ========== Pages / Páginas / Páginas / 页面 ==========
@app.route("/", methods=["GET"])
def index():
    """
    PT: tenta renderizar templates/index.html; se falhar, mostra fallback simples.
    EN: render templates/index.html; fallback to minimal page on error.
    ES: renderiza templates/index.html; fallback mínimo en error.
    中: 渲染 templates/index.html；失败时返回简易页。
    """
    sid = get_or_create_session_id()
    try:
        resp = make_response(render_template("index.html"))
    except Exception:
        html = """<!doctype html><meta charset="utf-8">
        <title>Chat</title>
        <h1>Flask Chat Online</h1>
        <p>Backend ok. Faça POST em <code>/chat</code> com {"message": "olá"}</p>"""
        resp = make_response(html)
    resp.set_cookie("sid", sid, httponly=True, samesite="Lax")
    return resp

# ========== Chat API ==========
@app.route("/chat", methods=["POST"])
def chat():
    """
    PT: recebe JSON {"message": "..."} e retorna {"success": true, "reply": "..."}.
    EN: accepts {"message": "..."} and returns {"success": true, "reply": "..."}.
    ES: recibe {"message": "..."} y devuelve {"success": true, "reply": "..."}.
    中: 接收 {"message": "..."}，返回 {"success": true, "reply": "..."}。
    """
    try:
        sid = get_or_create_session_id()
        data = request.get_json(silent=True) or {}
        user_msg = (data.get("message") or "").strip()
        if not user_msg:
            return jsonify(success=False, error="Mensagem vazia / Empty message / Mensaje vacío / 空消息"), 400

        # PT: histórico básico / EN: basic history / ES / 中
        sessions[sid].append({"role": "user", "content": user_msg})
        summarize_if_needed(sid)
        history = sessions[sid][-12:]

        # PT: chamada OpenAI / EN: OpenAI call / ES / 中
        r = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_TOKENS,
            messages=[{"role": m["role"], "content": m["content"]} for m in history],
        )
        assistant_text = r.choices[0].message.content or ""
        sessions[sid].append({"role": "assistant", "content": assistant_text})

        resp = make_response(jsonify(success=True, reply=assistant_text))
        resp.set_cookie("sid", sid, httponly=True, samesite="Lax")
        return resp
    except Exception as e:
        app.logger.exception("Erro em /chat")
        return jsonify(success=False, error=str(e), type=e.__class__.__name__), 500

# ========== Main / Principal / Principal / 主函数 ==========
if __name__ == "__main__":
    # PT: dev local / EN: local dev / ES: desarrollo local / 中: 本地开发
    app.run(debug=True, host="127.0.0.1", port=5000)
