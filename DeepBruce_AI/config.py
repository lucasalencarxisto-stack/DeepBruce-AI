import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _positive_float(name: str, default: float) -> float:
    value = os.getenv(name, str(default))
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"{name} deve ser um número positivo.") from exc
    if parsed <= 0:
        raise ValueError(f"{name} deve ser um número positivo.")
    return parsed


def _positive_int(name: str, default: int) -> int:
    value = os.getenv(name, str(default))
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"{name} deve ser um inteiro positivo.") from exc
    if parsed <= 0:
        raise ValueError(f"{name} deve ser um inteiro positivo.")
    return parsed


@dataclass(frozen=True)
class Settings:
    ollama_host: str
    ollama_model: str
    ollama_connect_timeout: float
    ollama_read_timeout: float
    port: int
    oqs_namespace: str
    cors_origins: str = ""
    max_message_length: int = 4_000

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            ollama_host=os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/"),
            ollama_model=os.getenv("OLLAMA_MODEL", "gemma3:1b"),
            ollama_connect_timeout=_positive_float("OLLAMA_CONNECT_TIMEOUT", 5),
            ollama_read_timeout=_positive_float("OLLAMA_READ_TIMEOUT", 300),
            port=_positive_int("PORT", 8000),
            oqs_namespace=os.getenv("OQS_NAMESPACE", "default"),
            cors_origins=os.getenv("CORS_ORIGINS", ""),
            max_message_length=_positive_int(
                "MAX_MESSAGE_LENGTH",
                4_000,
            ),
        )