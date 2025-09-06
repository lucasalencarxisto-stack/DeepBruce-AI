# ──────────────────────────────────────────────────────────────────────────────
# [PT-BR] Proxy simples para OpenAI/Ollama com comentários multilíngues, envs
#         padronizados, timeouts explícitos e tratamento de erros previsível.
# [EN]    Simple proxy for OpenAI/Ollama with multilingual comments, normalized
#         envs, explicit timeouts and predictable error handling.
# [ES]    Proxy simple para OpenAI/Ollama con comentarios multilingües, envs
#         normalizados, timeouts explícitos y manejo de errores predecible.
# ──────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

# ============================ Imports / 导入 ============================
import os
from pathlib import Path
from typing import Optional, Dict, Any

from flask import Flask, request, jsonify, render_template
import httpx

# [PT-BR] SDK OpenAI é opcional; o proxy funciona mesmo sem ele (apenas Ollama).
# [EN]    OpenAI SDK is optional; proxy still works without it (Ollama only).
# [ES]    El SDK de OpenAI es opcional; el proxy funciona sin él (solo Ollama).
try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # fallback


# ============================ Env / Ambientes ============================
ROOT_DIR: Path = Path(__file__).resolve().parents[1]

# [PT-BR] Provedor-alvo: "openai" ou "ollama".  
# [EN]    Target provider: "openai" or "ollama".  
# [ES]    Proveedor de destino: "openai" o "ollama".
PROVIDER = (os.getenv("PROVIDER") or "openai").strip().lower()
USE_FAKE_AI = (os.getenv("USE_FAKE_AI") or "0").strip() == "1"

# --- OpenAI ---------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
OPENAI_ORG_ID = (os.getenv("OPENAI_ORG_ID") or "").strip() or None
OPENAI_PROJECT = (os.getenv("OPENAI_PROJECT") or "").strip() or None
OPENAI_SYSTEM_PROMPT = (
    os.getenv("OPENAI_SYSTEM_PROMPT")
    or "Você é um assistente útil."
).strip()
OPENAI_REQ_TIMEOUT_S = float(os.getenv("OPENAI_REQ_TIMEOUT_S", "60"))

# --- Ollama ---------------------------------------------------------------
OLLAMA_BASE_URL = (os.getenv("OLLAMA_BASE_URL") or "http://host.docker.internal:11434").strip().rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b").strip()
OLLAMA_REQ_TIMEOUT_S = float(os.getenv("OLLAMA_REQ_TIMEOUT_S", "60"))


# ============================ App / 应用 ============================
app = Flask(
    __name__,
    template_folder=str(ROOT_DIR / "templates"),
    static_folder=str(ROOT_DIR / "static"),
)
# [PT-BR] Desabilita cache de templates para hot-reload em dev.
# [EN]    Disable template cache for hot-reload in dev.
# [ES]    Desactiva caché de plantillas para hot-reload en dev.
app.jinja_env.cache = {}


# ============================ Helpers ============================

def _normalize_base_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    url = url.strip().rstrip("/")
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    return url


def chat_with_openai(prompt: str) -> str:
    """
    [PT-BR] Faz uma chamada simples ao Chat Completions da OpenAI.
    [EN]    Performs a simple call to OpenAI Chat Completions.
    [ES]    Realiza una llamada sencilla a Chat Completions de OpenAI.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY ausente")
    if OpenAI is None:
        raise RuntimeError("Biblioteca openai indisponível")

    client = OpenAI(
        api_key=OPENAI_API_KEY,
        organization=OPENAI_ORG_ID,
        project=OPENAI_PROJECT,  # ignorado em SDKs mais antigos; benigno
    )

    # [PT-BR] NOTA: alguns SDKs novos usam Responses API; este usa Chat Completions
    # por compatibilidade. Ajuste se migrar para Responses.
    r = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": OPENAI_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        timeout=OPENAI_REQ_TIMEOUT_S,  # requer SDK>=1.51; caso contrário, usar httpx externo
    )
    return (r.choices[0].message.content or "").strip()


def chat_with_ollama(prompt: str) -> str:
    """
    [PT-BR] Chamada síncrona ao /api/generate do Ollama (sem streaming).
    [EN]    Synchronous call to Ollama's /api/generate (no streaming).
    [ES]    Llamada síncrona a /api/generate de Ollama (sin streaming).
    """
    base = _normalize_base_url(OLLAMA_BASE_URL)
    if not base:
        return "(Ollama base URL inválida)"

    url = f"{base}/api/generate"
    payload: Dict[str, Any] = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    with httpx.Client(timeout=OLLAMA_REQ_TIMEOUT_S, http2=True) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return (data.get("response", "") or "").strip() or "(sem resposta)"


# ============================ Rotas ============================
@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    """
    [PT-BR] Healthcheck básico. Se provider=ollama, tenta pingar /api/tags.
    [EN]    Basic healthcheck. If provider=ollama, tries to ping /api/tags.
    [ES]    Healthcheck básico. Si provider=ollama, intenta hacer ping a /api/tags.
    """
    info: Dict[str, Any] = {
        "ok": True,
        "fake": USE_FAKE_AI,
        "provider": PROVIDER,
        "service": "OQS_step2",
    }
    if not USE_FAKE_AI and PROVIDER == "ollama":
        try:
            r = httpx.get(f"{_normalize_base_url(OLLAMA_BASE_URL)}/api/tags", timeout=3.0)
            info["ollama_up"] = (r.status_code == 200)
        except Exception:
            info["ollama_up"] = False
    return jsonify(info)


@app.post("/chat")
def chat():
    """
    [PT-BR] Rota única de chat. Forneça JSON: {"message":"..."}.
    [EN]    Single chat route. Provide JSON: {"message":"..."}.
    [ES]    Ruta única de chat. Envíe JSON: {"message":"..."}.
    """
    data = request.get_json(silent=True) or {}
    user_msg = (data.get("message") or "").strip()
    if not user_msg:
        return jsonify(success=False, error="Mensagem vazia"), 400

    if USE_FAKE_AI:
        return jsonify(success=True, reply=f"[FAKE] Você disse: {user_msg}")

    try:
        if PROVIDER == "ollama":
            reply = chat_with_ollama(user_msg)
        else:
            reply = chat_with_openai(user_msg)
        return jsonify(success=True, reply=reply)
    except Exception as e:  # pragma: no cover
        return jsonify(success=False, error=f"Falha {PROVIDER}: {e}"), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    # [PT-BR] Em produção, use um servidor WSGI (gunicorn/uwsgi).  
    # [EN]    In production, use a WSGI server (gunicorn/uwsgi).  
    # [ES]    En producción, use un servidor WSGI (gunicorn/uwsgi).
    app.run(host="0.0.0.0", port=port, debug=True)
