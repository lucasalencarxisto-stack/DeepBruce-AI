import json
import os

import requests


class OllamaServiceError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def stream_chat(message: str):
    host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    model = os.getenv("OLLAMA_MODEL", "gemma3:1b")

    url = f"{host.rstrip('/')}/api/chat"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Você é DeepBruce, um assistente de inteligência artificial. "
                    "Responda em português brasileiro quando o usuário falar em português. "
                    "Seja claro, útil e objetivo."
                ),
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        "stream": True,
        "options": {
            "temperature": 0.6,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
            "num_predict": 512,
        },
    }

    try:
        with requests.post(
            url,
            json=payload,
            stream=True,
            timeout=(5, 300),
        ) as response:

            if response.status_code == 404:
                raise OllamaServiceError(
                    "ollama_model_not_found",
                    f"O modelo '{model}' não foi encontrado no Ollama.",
                )

            response.raise_for_status()

            for raw_line in response.iter_lines():
                if not raw_line:
                    continue

                try:
                    data = json.loads(raw_line.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue

                content = data.get("message", {}).get("content", "")

                if content:
                    yield content

                if data.get("done"):
                    break

    except requests.ConnectionError as exc:
        raise OllamaServiceError(
            "ollama_unavailable",
            "Não foi possível conectar ao Ollama.",
        ) from exc

    except requests.Timeout as exc:
        raise OllamaServiceError(
            "ollama_timeout",
            "O Ollama demorou demais para responder.",
        ) from exc

    except requests.HTTPError as exc:
        raise OllamaServiceError(
            "ollama_http_error",
            "O Ollama retornou um erro HTTP.",
        ) from exc