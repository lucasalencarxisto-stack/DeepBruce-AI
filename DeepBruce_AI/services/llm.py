# oqs_step3/services/llm.py
import os, json, requests
from typing import Iterable, List, Dict
from flask import current_app

def _make_messages(user_msg: str, history: List[Dict], context_items: List[Dict]) -> List[Dict]:
    sys = (
        "Você é o assistente do projeto OQS_step3. "
        "Responda claramente e cite fontes quando houver contexto."
    )
    msgs = [{"role": "system", "content": sys}]
    msgs += history or []
    if context_items:
        ctx = "\n\n".join(it["document"][:4000] for it in context_items)
        msgs.append({"role": "system", "content": f"[contexto]\n{ctx}"})
    msgs.append({"role": "user", "content": user_msg})
    return msgs

def ollama_stream(user_msg: str, history: List[Dict], context_items: List[Dict]) -> Iterable[str]:
    host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b-instruct")
    url = f"{host}/api/chat"
    payload = {"model": model, "messages": _make_messages(user_msg, history, context_items), "stream": True}
    with requests.post(url, json=payload, stream=True, timeout=300) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                data = json.loads(line)
            except Exception:
                continue
            if data.get("done"):
                break
            delta = (data.get("message") or {}).get("content") or ""
            if delta:
                yield delta
