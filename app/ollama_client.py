# ──────────────────────────────────────────────────────────────────────────────
# [PT-BR] Cliente Ollama minimalista com melhorias: normalização de URL, timeouts
#         granulares, HTTP/2, heartbeats, tratamento de erros, e *retries*
#         exponenciais opcionais (backoff), além de suporte a parâmetros extras
#         no chat (temperature/top_p/stop/system_prompt).
# [EN]    Minimalist Ollama client with improvements: URL normalization, granular
#         timeouts, HTTP/2, heartbeats, error handling, optional exponential
#         retries (backoff), plus extra params in chat (temperature/top_p/stop/
#         system_prompt).
# [ES]    Cliente Ollama minimalista con mejoras: normalización de URL, timeouts
#         granulares, HTTP/2, heartbeats, manejo de errores, *retries*
#         exponenciales opcionales (backoff), y soporte de parámetros extra en
#         chat (temperature/top_p/stop/system_prompt).
# [中文]   轻量的 Ollama 客户端：规范化 URL、细颗粒度超时、HTTP/2、心跳、错误处理，
#         可选指数退避重试（backoff），并支持聊天额外参数（temperature/top_p/stop/system_prompt）。
# ──────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import time
import logging
import math
from dataclasses import dataclass, field
from typing import Generator, List, Tuple, Optional, TypedDict, Dict, Any, Iterable

import httpx

log = logging.getLogger(__name__)

# =============================================================================
# Tipos / Types
# =============================================================================
class ModelTag(TypedDict):
    id: str


@dataclass(slots=True)
class OllamaConfig:
    """
    [PT-BR] Config padrão para chamadas ao Ollama.
    [EN]    Default config for Ollama calls.
    [ES]    Config por defecto para llamadas a Ollama.
    [中文]   Ollama 调用的默认配置。
    """
    base_url: str
    model: str = "llama3.2:3b"
    num_ctx: int = 4096
    num_predict: int = 512
    timeout_read_s: float = 60.0
    timeout_connect_s: float = 5.0
    timeout_write_s: float = 10.0
    timeout_pool_s: float = 5.0
    keep_alive: str = "30m"
    http2: bool = True
    default_headers: Dict[str, str] = field(
        default_factory=lambda: {
            "Accept": "application/json",
            "User-Agent": "oqs-ollama-client/1.0 (+github.com/lucasalencarxisto-stack)",  # [PT-BR] UA amigável / [EN] friendly UA / [ES] UA amigable / [中文] 友好的 UA
        }
    )
    # [PT-BR] Retries simples com backoff exponencial; 0 desativa.  
    # [EN]    Simple retries with exponential backoff; 0 disables.  
    # [ES]    Retries simples con backoff exponencial; 0 desactiva.
    retries: int = 0
    retry_base_delay_s: float = 0.5  # 0.5, 1, 2, 4 ...


# =============================================================================
# Helpers HTTP e utilidades
# [中文] HTTP 辅助与通用工具
# =============================================================================

def _timeout(cfg: OllamaConfig) -> httpx.Timeout:
    # [中文] 超时配置：分别设置连接/读取/写入/连接池超时
    return httpx.Timeout(
        connect=cfg.timeout_connect_s,
        read=cfg.timeout_read_s,
        write=cfg.timeout_write_s,
        pool=cfg.timeout_pool_s,
    )


def _new_client(cfg: OllamaConfig) -> httpx.Client:
    """
    [PT-BR] Cria cliente httpx com HTTP/2 e cabeçalhos padrão.
    [EN]    Create httpx client with HTTP/2 and default headers.
    [ES]    Crea cliente httpx con HTTP/2 y encabezados por defecto.
    [中文]   创建支持 HTTP/2 且带默认请求头的 httpx 客户端。
    """
    return httpx.Client(timeout=_timeout(cfg), http2=cfg.http2, headers=cfg.default_headers)


def _normalize_base_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    url = url.strip().rstrip("/")
    if not url.startswith(("http://", "https://")):
        url = "http://" + url  # [PT-BR] mude para https:// se aplicável / [EN] switch to https:// if applicable / [中文] 如适用改为 https://
    return url


def _fallback_models(default_model: str) -> List[ModelTag]:
    # [中文] 失败时的回退：返回仅含默认模型的列表
    return [{"id": default_model}]


def _should_retry(exc: Exception, status_code: Optional[int]) -> bool:
    """
    [PT-BR] Regras simples: retry em Timeout/RequestError e 5xx/429.
    [EN]    Simple rules: retry on Timeout/RequestError and 5xx/429.
    [ES]    Reglas simples: reintenta en Timeout/RequestError y 5xx/429.
    [中文]   简单规则：在超时/请求错误以及 5xx/429 时重试。
    """
    if isinstance(exc, (httpx.TimeoutException, httpx.RequestError)):
        return True
    if status_code is not None and (status_code >= 500 or status_code == 429):
        return True
    return False


def _sleep_backoff(attempt: int, base: float) -> None:
    delay = base * (2 ** max(0, attempt - 1))  # 0.5,1,2,4...
    time.sleep(min(delay, 8.0))  # [PT-BR] limita a 8s / [EN] cap at 8s / [ES] limitar a 8s / [中文] 最长限制为 8 秒


# =============================================================================
# API pública / Public API
# =============================================================================

# [中文] 从 /api/tags 获取模型列表；失败时返回包含默认模型的回退
def list_models(base_url: str, timeout: int, default_model: str) -> List[ModelTag]:
    """
    [PT-BR] Lista modelos do Ollama (/api/tags). Em erro, retorna [default_model].
    [EN]    List models from Ollama (/api/tags). On error, return [default_model].
    [ES]    Lista modelos de Ollama (/api/tags). En error, devuelve [default_model].
    """
    base_url = _normalize_base_url(base_url)
    if not base_url:
        return _fallback_models(default_model)

    cfg = OllamaConfig(base_url=base_url, timeout_read_s=float(timeout))
    url = f"{cfg.base_url}/api/tags"

    attempts = max(1, 1 + cfg.retries)
    last_error: Optional[str] = None

    for i in range(1, attempts + 1):
        try:
            with _new_client(cfg) as client:
                r = client.get(url)
                r.raise_for_status()
                payload = r.json()
            models = payload.get("models") or []
            out: List[ModelTag] = []
            for m in models:
                name = (m.get("name") or m.get("model") or "").strip()
                if name:
                    out.append({"id": name})
            return out or _fallback_models(default_model)

        except httpx.HTTPStatusError as e:
            code = getattr(e.response, "status_code", None)
            body_preview = ""
            try:
                body_preview = e.response.text[:500]
            except Exception:
                pass
            log.error("Ollama /api/tags HTTP %s: %s", code, body_preview)
            last_error = f"http:{code}"
            if _should_retry(e, code) and i < attempts:
                _sleep_backoff(i, cfg.retry_base_delay_s)
                continue
            return _fallback_models(default_model)
        except (httpx.TimeoutException, httpx.RequestError) as e:
            log.warning("Ollama /api/tags %s: %s", type(e).__name__, url)
            last_error = type(e).__name__.lower()
            if _should_retry(e, None) and i < attempts:
                _sleep_backoff(i, cfg.retry_base_delay_s)
                continue
            return _fallback_models(default_model)

    # fallback defensivo
    log.debug("list_models fallback due to: %s", last_error)
    return _fallback_models(default_model)


def chat_once(
    msg: str,
    *,
    base_url: str,
    model: str,
    num_ctx: int,
    num_predict: int,
    timeout: int,
    # extras
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    stop: Optional[List[str]] = None,
    system_prompt: Optional[str] = None,
) -> Tuple[str, str]:
    """
    [PT-BR] Chamada única (não-stream) para /api/chat. Retorna (reply, provider_tag).
    [EN]    Single (non-stream) call to /api/chat. Returns (reply, provider_tag).
    [ES]    Llamada única no-stream a /api/chat. Devuelve (reply, provider_tag).
    [中文]   非流式调用 /api/chat；返回 (reply, provider_tag)。
    """
    fallback = f"Você disse: {msg}"
    base_url = _normalize_base_url(base_url)
    if not base_url:
        return fallback, "local-echo"

    cfg = OllamaConfig(
        base_url=base_url,
        model=model,
        num_ctx=num_ctx,
        num_predict=num_predict,
        timeout_read_s=float(timeout),
    )
    url = f"{cfg.base_url}/api/chat"

    options: Dict[str, Any] = {"num_ctx": cfg.num_ctx, "num_predict": cfg.num_predict}
    if temperature is not None:
        options["temperature"] = temperature
    if top_p is not None:
        options["top_p"] = top_p
    if stop:
        options["stop"] = stop

    messages: List[Dict[str, Any]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": msg})

    body: Dict[str, Any] = {
        "model": cfg.model,
        "messages": messages,
        "stream": False,
        "keep_alive": cfg.keep_alive,
        "options": options,
    }

    attempts = max(1, 1 + cfg.retries)

    for i in range(1, attempts + 1):
        try:
            with _new_client(cfg) as client:
                r = client.post(url, json=body)
                r.raise_for_status()
                payload = r.json()

            reply = (payload.get("message") or {}).get("content") or payload.get("response")
            if not reply:
                return fallback, f"ollama-empty:{cfg.model}"
            return reply, f"ollama:chat:{cfg.model}"

        except httpx.HTTPStatusError as e:
            code = getattr(e.response, "status_code", None)
            if _should_retry(e, code) and i < attempts:
                _sleep_backoff(i, cfg.retry_base_delay_s)
                continue
            return f"[degradado:HTTP {code}] {fallback}", f"degraded:http:{code}"
        except httpx.TimeoutException:
            if i < attempts:
                _sleep_backoff(i, cfg.retry_base_delay_s)
                continue
            return f"[degradado:Timeout] {fallback}", "degraded:timeout"
        except httpx.RequestError:
            if i < attempts:
                _sleep_backoff(i, cfg.retry_base_delay_s)
                continue
            return f"[degradado:Request] {fallback}", "degraded:request"


def generate_stream(
    prompt: str,
    *,
    base_url: str,
    model: str,
    num_ctx: int,
    num_predict: int,
    timeout: int,
    # extras opcionais / optional extras
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    stop: Optional[List[str]] = None,
) -> Generator[str, None, None]:
    """
    [PT-BR] Streaming compatível com o frontend (:preamble, :hb, tokens com '\n').
    [EN]    Frontend-compatible streaming (:preamble, :hb, tokens ending with '\n').
    [ES]    Streaming compatible con frontend (:preamble, :hb, tokens con '\n').
    [中文]   与前端兼容的流式输出（包含 :preamble 与周期性 :hb 心跳，按行输出 tokens）。
    """
    # mantém o cliente vivo desde o início / keep connection alive early
    yield ":preamble\n"
    time.sleep(0.4)
    yield ":hb\n"

    base_url = _normalize_base_url(base_url)
    if not base_url:
        yield f"Você disse: {prompt}\n"
        return

    cfg = OllamaConfig(base_url=base_url, model=model, num_ctx=num_ctx, num_predict=num_predict, timeout_read_s=float(timeout))
    url = f"{cfg.base_url}/api/generate"

    options: Dict[str, Any] = {"num_ctx": cfg.num_ctx, "num_predict": cfg.num_predict}
    if temperature is not None:
        options["temperature"] = temperature
    if top_p is not None:
        options["top_p"] = top_p
    if stop:
        options["stop"] = stop

    body: Dict[str, Any] = {
        "model": cfg.model,
        "prompt": prompt,
        "stream": True,
        "keep_alive": cfg.keep_alive,
        "options": options,
    }

    last_hb = time.monotonic()
    hb_gap = 2.0  # envia ':hb' a cada ~2s / send ':hb' every ~2s

    try:
        # httpx.stream evita carregar tudo em memória / avoids buffering entire body
        with httpx.stream(
            "POST",
            url,
            json=body,
            timeout=_timeout(cfg),
            headers=cfg.default_headers,
        ) as r:
            r.raise_for_status()

            for line in r.iter_lines():
                now = time.monotonic()
                if now - last_hb >= hb_gap:
                    yield ":hb\n"
                    last_hb = now

                if not line:
                    continue

                try:
                    obj = json.loads(line.decode("utf-8", errors="ignore"))
                except Exception:
                    continue

                # erros do servidor / server-side errors
                # 中文: 服务器端错误
                if obj.get("error"):
                    yield f"\n[degradado:ServerError] {obj['error']}\n"
                    break

                # tokens / chunks
                # 中文: 模型增量 token（逐行输出）
                chunk = obj.get("response", "")
                if chunk:
                    yield chunk + "\n"
                    last_hb = time.monotonic()

                # término / done
                # 中文: 结束（可能包含 done_reason）
                if obj.get("done"):
                    reason = obj.get("done_reason") or ""
                    if reason and reason != "stop":
                        yield f"\n[done:{reason}]\n"
                    break

    except httpx.TimeoutException:
        yield f"\n[degradado:Timeout] Você disse: {prompt}\n"
    except httpx.HTTPStatusError as e:
        code = getattr(e.response, "status_code", "unknown")
        yield f"\n[degradado:HTTP {code}] Você disse: {prompt}\n"
    except httpx.RequestError:
        yield f"\n[degradado:Request] Você disse: {prompt}\n"


# =============================================================================
# Utilidades extra (opcionais) / Extras (optional)
# =============================================================================

def health_check(base_url: str, timeout: int = 5) -> bool:
    """
    [PT-BR] Checa se o Ollama responde (HEAD /api/tags).
    [EN]    Quick health check against Ollama (HEAD /api/tags).
    [ES]    Comprobación rápida de salud (HEAD /api/tags).
    [中文]   快速健康检查（HEAD 请求 /api/tags）。
    """
    base_url = _normalize_base_url(base_url)
    if not base_url:
        return False
    cfg = OllamaConfig(base_url=base_url, timeout_read_s=float(timeout))
    try:
        with _new_client(cfg) as client:
            r = client.head(f"{cfg.base_url}/api/tags")
            return r.status_code < 500
    except Exception:
        return False


# =============================================================================
# Público do módulo / Public symbols
# =============================================================================
__all__ = [
    "OllamaConfig",
    "ModelTag",
    "list_models",
    "chat_once",
    "generate_stream",
    "health_check",
]
