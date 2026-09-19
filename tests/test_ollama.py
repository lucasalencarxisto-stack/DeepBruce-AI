from unittest.mock import MagicMock

import requests

from DeepBruce_AI.config import Settings
from DeepBruce_AI.services.ollama import OllamaServiceError, stream_chat


def settings():
    return Settings(
        ollama_host="http://ollama:11434",
        ollama_model="test-model",
        ollama_connect_timeout=1,
        ollama_read_timeout=2,
        port=8000,
        oqs_namespace="test",
        cors_origins="",
    )


def test_stream_chat_decodes_ollama_chunks(monkeypatch):
    response = MagicMock()
    response.status_code = 200
    response.iter_lines.return_value = [
        b'{"message":{"content":"Oi"}}',
        b'{"message":{"content":"!"},"done":true}',
    ]
    response.__enter__.return_value = response
    response.__exit__.return_value = None
    monkeypatch.setattr(requests, "post", MagicMock(return_value=response))

    assert list(stream_chat("teste", settings())) == ["Oi", "!"]


def test_stream_chat_maps_connection_error(monkeypatch):
    monkeypatch.setattr(requests, "post", MagicMock(side_effect=requests.ConnectionError))

    try:
        list(stream_chat("teste", settings()))
    except OllamaServiceError as exc:
        assert exc.code == "ollama_unavailable"
    else:
        raise AssertionError("stream_chat deveria reportar Ollama indisponível")