import os
import httpx
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("PROVIDER", "ollama").strip().lower()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434").rstrip("/")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

prompt = "Diga olá em português, inglês e espanhol."

def chat_with_openai() -> str:
    if not OPENAI_API_KEY:
        return "❌ OPENAI_API_KEY não configurada. Adicione no .env."
    try:
        from openai import OpenAI
    except ImportError:
        return "❌ Pacote 'openai' não instalado. Rode: pip install openai"
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "Você é um assistente útil."},
            {"role": "user", "content": prompt},
        ],
    )
    return resp.choices[0].message.content

def chat_with_ollama() -> str:
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    try:
        with httpx.Client(timeout=60) as client:
            r = client.post(url, json=payload)
            r.raise_for_status()
            return (r.json().get("response") or "").strip() or "(sem resposta)"
    except Exception as e:
        return f"❌ Erro ao falar com Ollama: {e}"

if __name__ == "__main__":
    print(f"🔹 Provider: {PROVIDER}")
    print(chat_with_openai() if PROVIDER == "openai" else chat_with_ollama())
