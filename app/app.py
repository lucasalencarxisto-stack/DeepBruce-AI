# ============================ Imports / ImportaÃ§Ãµes / Importaciones / å¯¼å…¥ ============================
import os, json
from pathlib import Path
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# OpenAI (carregado apenas no modo real) / only used in real mode / solo en modo real / ä»…åœ¨çœŸå®žæ¨¡å¼ä½¿ç”¨
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

# ============================ Paths & .env (ROOT) / Caminhos & .env (RAIZ) / Rutas & .env (RAÃZ) / è·¯å¾„ä¸Ž .envï¼ˆé¡¹ç›®æ ¹ï¼‰ ============================
# PT: Detecta a raiz do projeto (pasta acima de app/) para localizar templates, static e .env
# EN: Detect project root (one level above app/) to locate templates, static and .env
# ES: Detecta la raÃ­z del proyecto (una carpeta arriba de app/) para ubicar templates, static y .env
# ä¸­: è¯†åˆ«é¡¹ç›®æ ¹ç›®å½•ï¼ˆä½äºŽ app/ ä¹‹ä¸Šï¼‰ï¼Œä»¥å®šä½ templatesã€static ä¸Ž .env
ROOT_DIR = Path(__file__).resolve().parents[1]
DOTENV_PATH = ROOT_DIR / ".env"

# PT: Carrega variÃ¡veis do .env da RAIZ (override=True ajuda em dev)
# EN: Load env vars from ROOT .env (override=True helps in dev)
# ES: Carga variables desde .env en la RAÃZ (override=True Ãºtil en dev)
# ä¸­: ä»Žæ ¹ç›®å½•åŠ è½½ .envï¼ˆoverride=True ä¾¿äºŽå¼€å‘ï¼‰
load_dotenv(dotenv_path=DOTENV_PATH, override=True, verbose=True)

# ============================ Flags / Sinalizadores / SeÃ±ales / æ ‡å¿— ============================
# PT: Quando = "1", nÃ£o chama OpenAI e responde local (Ãºtil para testar UI)
# EN: When "1", skip OpenAI and reply locally (great for UI testing)
# ES: Cuando es "1", no llama a OpenAI y responde localmente (ideal para probar UI)
# ä¸­: å½“ä¸º "1" æ—¶ï¼Œä¸è°ƒç”¨ OpenAIï¼Œæœ¬åœ°å›žæ˜¾ï¼ˆä¾¿äºŽè°ƒè¯•ç•Œé¢ï¼‰
USE_FAKE_AI = (os.getenv("USE_FAKE_AI") or "0").strip() == "1"

# PT: Credenciais OpenAI (sÃ³ necessÃ¡rias se USE_FAKE_AI=0)
# EN: OpenAI credentials (needed only if USE_FAKE_AI=0)
# ES: Credenciales de OpenAI (solo necesarias si USE_FAKE_AI=0)
# ä¸­: OpenAI å‡­è¯ï¼ˆä»…åœ¨ USE_FAKE_AI=0 æ—¶éœ€è¦ï¼‰
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_ORG_ID  = os.getenv("OPENAI_ORG_ID")
OPENAI_PROJECT = os.getenv("OPENAI_PROJECT")

# ============================ Flask App (templates/static na RAIZ) / en ROOT / åœ¨é¡¹ç›®æ ¹ ============================
# PT: Aponta para templates/ e static/ da raiz do projeto
# EN: Point to project-root templates/ and static/
# ES: Apunta a templates/ y static/ en la raÃ­z
# ä¸­: æŒ‡å‘é¡¹ç›®æ ¹ç›®å½•çš„ templates/ ä¸Ž static/
app = Flask(
    __name__,
    template_folder=str(ROOT_DIR / "templates"),
    static_folder=str(ROOT_DIR / "static"),
)

# PT: Em dev, desabilita cache de templates
# EN: Disable template cache in dev
# ES: Desactiva la cachÃ© de plantillas en dev
# ä¸­: å¼€å‘çŽ¯å¢ƒç¦ç”¨æ¨¡æ¿ç¼“å­˜
app.jinja_env.cache = {}

# ============================ OpenAI Client (lazy) / Cliente (perezoso) / å®¢æˆ·ç«¯ï¼ˆå»¶è¿Ÿåˆ›å»ºï¼‰ ============================
# PT: SÃ³ cria cliente se nÃ£o for modo fake e houver chave
# EN: Only create client if not fake mode and key exists
# ES: Solo crea cliente si no es modo fake y hay clave
# ä¸­: ä»…åœ¨éžå‡æ¨¡å¼ä¸”å­˜åœ¨å¯†é’¥æ—¶åˆ›å»ºå®¢æˆ·ç«¯
def get_openai():
    if USE_FAKE_AI:
        return None
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY ausente e USE_FAKE_AI=0")
    if OpenAI is None:
        raise RuntimeError("Biblioteca openai nÃ£o disponÃ­vel")
    return OpenAI(
        api_key=OPENAI_API_KEY,
        organization=OPENAI_ORG_ID or None,

    )

# ===== Rota principal da interface =====
@app.route("/")
def home():
    return render_template("index.html")

# ============================ Routes / Rotas / Rutas / è·¯ç”± ============================

# ---------- UI ----------
# PT: Rota principal â€” renderiza a interface (templates/index.html)
# EN: Main route â€” renders the interface
# ES: Ruta principal â€” renderiza la interfaz
# ä¸­: ä¸»é¡µè·¯ç”± â€” æ¸²æŸ“ç•Œé¢
@app.get("/")
def index():
    return render_template("index.html")

# ---------- Health ----------
# PT: Healthcheck simples p/ monitoramento / smoke test
# EN: Simple healthcheck for monitoring / smoke test
# ES: ComprobaciÃ³n simple de salud
# ä¸­: ç®€å•å¥åº·æ£€æŸ¥
@app.get("/health")
def health():
    return jsonify(ok=True, service="OQS_step2", fake=USE_FAKE_AI)

# ---------- Chat API ----------
# PT: Endpoint principal de chat (consumido pelo frontend via fetch)
# EN: Main chat endpoint (consumed by frontend via fetch)
# ES: Endpoint principal de chat (usado por el frontend con fetch)
# ä¸­: ä¸»è¦èŠå¤©æŽ¥å£ï¼ˆå‰ç«¯é€šè¿‡ fetch è°ƒç”¨ï¼‰
@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    user_msg = (data.get("message") or "").strip()

    # PT: ValidaÃ§Ã£o mÃ­nima
    # EN: Minimal validation
    # ES: ValidaciÃ³n mÃ­nima
    # ä¸­: æœ€å°æ ¡éªŒ
    if not user_msg:
        return jsonify(success=False, error="Mensagem vazia / Empty message / Mensaje vacÃ­o / ç©ºæ¶ˆæ¯"), 400

    # PT: Modo fake â€” responde local (nÃ£o consome API)
    # EN: Fake mode â€” local reply (no API usage)
    # ES: Modo fake â€” respuesta local (no usa API)
    # ä¸­: å‡æ¨¡å¼ â€” æœ¬åœ°å“åº”ï¼ˆä¸è°ƒç”¨ APIï¼‰
    if USE_FAKE_AI:
        reply = f"[FAKE] VocÃª disse: {user_msg}"
        return jsonify(success=True, reply=reply)

    # PT: Modo real â€” chama OpenAI
    # EN: Real mode â€” call OpenAI
    # ES: Modo real â€” llama a OpenAI
    # ä¸­: çœŸæ¨¡å¼ â€” è°ƒç”¨ OpenAI
    try:
        client = get_openai()
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "VocÃª Ã© um assistente Ãºtil."},
                {"role": "user",   "content": user_msg},
            ],
            temperature=0.7,
        )
        reply = resp.choices[0].message.content
        return jsonify(success=True, reply=reply)
    except Exception as e:
        # PT: Falha amigÃ¡vel
        # EN: Friendly failure
        # ES: Error amigable
        # ä¸­: å‹å¥½é”™è¯¯ä¿¡æ¯
        return jsonify(success=False, error=f"Falha OpenAI: {e}"), 500

# ============================ Main / Principal / Principal / ä¸»å‡½æ•° ============================
if __name__ == "__main__":
    # PT: Porta via env (padrÃ£o 8000) + host 0.0.0.0 p/ acesso externo
    # EN: Port from env (default 8000) + host 0.0.0.0 for external access
    # ES: Puerto por env (por defecto 8000) + host 0.0.0.0 para acceso externo
    # ä¸­: ç«¯å£æ¥è‡ªçŽ¯å¢ƒå˜é‡ï¼ˆé»˜è®¤ 8000ï¼‰ï¼Œ0.0.0.0 ä¾¿äºŽå¤–éƒ¨è®¿é—®
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
