# app/ollama_client.py
from __future__ import annotations
import json, time
from typing import Generator, List, Dict, Tuple
import httpx


def list_models(base_url: str | None, timeout: int, fallback_model: str) -> List[Dict[str, str]]:
    if not base_url:
        return [{"id": fallback_model}]
    try:
        with httpx.Client(timeout=timeout) as c:
            r = c.get(f"{base_url}/api/tags", headers={"Content-Type": "application/json"})
            r.raise_for_status()
            payload = r.json()
        models = []
        for m in (payload.get("models") or []):
            name = (m.get("name") or m.get("model") or "").strip()
            if name:
                models.append({"id": name})
        return models or [{"id": fallback_model}]
    except Exception:
        return [{"id": fallback_model}]


def chat_once(
    message: str,
    *,
    base_url: str | None,
    model: str,
    num_ctx: int,
    num_predict: int,
    timeout: int,
) -> Tuple[str, str]:
    """Chamada única (não stream) ao /api/chat do Ollama."""
    fallback = f"Você disse: {message}"
    if not base_url:
        return fallback, "local-echo"

    body = {
        "model": model,
        "messages": [{"role": "user", "content": message}],
        "stream": False,
        "options": {"num_ctx": num_ctx, "num_predict": num_predict},
    }
    try:
        with httpx.Client(timeout=timeout) as c:
            r = c.post(f"{base_url}/api/chat", json=body, headers={"Content-Type": "application/json"})
            r.raise_for_status()
            payload = r.json()

        reply = (payload.get("message") or {}).get("content") or payload.get("response")
        if not reply:
            return fallback, "ollama-empty"
        return reply, f"ollama:chat:{model}"
    except Exception as e:
        return f"[degradado:{type(e).__name__}] {fallback}", "degraded"


def generate_stream(
    prompt: str,
    *,
    base_url: str | None,
    model: str,
    num_ctx: int,
    num_predict: int,
    timeout: int,
    heartbeat_every: float = 2.0,
) -> Generator[str, None, None]:
    """
    Stream de texto em linhas (cada token/pedaço termina com '\n').
    Emite ':preamble' logo no início e ':hb' como 'heartbeats' enquanto carrega.
    NÃO toca no objeto Flask 'request' aqui dentro.
    """
    # Mantém o worker vivo antes de contatar o Ollama
    yield ":preamble\n"

    if not base_url:
        yield f"Você disse: {prompt}\n"
        return

    body = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {"num_ctx": num_ctx, "num_predict": num_predict},
    }

    last_hb = time.monotonic()
    try:
        with httpx.Client(timeout=timeout) as c:
            with c.stream("POST", f"{base_url}/api/generate", json=body, headers={"Content-Type": "application/json"}) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    now = time.monotonic()
                    if now - last_hb >= heartbeat_every:
                        yield ":hb\n"
                        last_hb = now

                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
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
