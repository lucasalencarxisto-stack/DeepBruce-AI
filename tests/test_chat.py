import json

from DeepBruce_AI.services import ollama
from wsgi import app


def test_chat_rejects_invalid_json():
    response = app.test_client().post(
        "/api/chat",
        data="not-json",
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "invalid_json"


def test_chat_rejects_missing_message():
    response = app.test_client().post("/api/chat", json={})

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "invalid_message"


def test_chat_rejects_empty_message():
    response = app.test_client().post("/api/chat", json={"message": "  "})

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "invalid_message"


def test_chat_streams_tokens_without_ollama(monkeypatch):
    monkeypatch.setattr(ollama, "stream_chat", lambda message, settings: ["Olá", "!"])

    response = app.test_client().post("/api/chat", json={"message": "Oi"})
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert '"content": "Ol' in body
    assert '"content": "!"' in body
    assert "event: done" in body


def test_chat_reports_ollama_unavailable(monkeypatch):
    def unavailable(message, settings):
        raise ollama.OllamaServiceError("ollama_unavailable", "Ollama indisponível.")
        yield

    monkeypatch.setattr(ollama, "stream_chat", unavailable)

    response = app.test_client().post("/api/chat", json={"message": "Oi"})
    events = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "event: error" in events
    assert '"code": "ollama_unavailable"' in events