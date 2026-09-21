import pytest

import DeepBruce_AI.routes.message as message_route
from DeepBruce_AI import create_app


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True

    return app.test_client()


def test_empty_message_returns_400(
    client,
):
    response = client.post(
        "/api/message",
        json={
            "message": "",
        },
    )

    assert response.status_code == 400


def test_chat_message_streams_sse(
    client,
    monkeypatch,
):
    def fake_stream_message(
        message,
        settings,
        conversation_id,
    ):
        yield {
            "type": "route",
            "route": "chat",
            "confidence": 0.95,
            "reason": "casual_conversation",
            "conversation_id": conversation_id,
        }

        yield {
            "type": "token",
            "content": "Olá",
        }

        yield {
            "type": "token",
            "content": "!",
        }

    monkeypatch.setattr(
        message_route.orchestrator,
        "stream_message",
        fake_stream_message,
    )

    response = client.post(
        "/api/message",
        json={
            "message": "Olá Bruce",
            "conversation_id": (
                "conversation-chat"
            ),
        },
    )

    body = response.get_data(
        as_text=True
    )

    assert response.status_code == 200

    assert "event: route" in body
    assert '"route": "chat"' in body

    assert (
        '"conversation_id": '
        '"conversation-chat"'
        in body
    )

    assert "event: token" in body
    assert '"content": "Olá"' in body
    assert '"content": "!"' in body

    assert "event: done" in body


def test_ambiguous_message_streams_clarification(
    client,
    monkeypatch,
):
    def fake_stream_message(
        message,
        settings,
        conversation_id,
    ):
        yield {
            "type": "route",
            "route": "ambiguous",
            "confidence": 0.55,
            "reason": (
                "ambiguous_relationship"
            ),
            "conversation_id": conversation_id,
        }

        yield {
            "type": "clarification",
            "message": (
                "Sua pergunta pode ter mais "
                "de um significado."
            ),
            "original_message": message,
            "confidence": 0.55,
            "attempt": 1,
            "keywords": [
                "pai",
                "lula",
            ],
            "options": [
                {
                    "label": (
                        "Quem foi o pai de lula?"
                    ),
                    "query": (
                        "Quem foi o pai de lula?"
                    ),
                },
                {
                    "label": "Quem é lula?",
                    "query": "Quem é lula?",
                },
            ],
        }

    monkeypatch.setattr(
        message_route.orchestrator,
        "stream_message",
        fake_stream_message,
    )

    response = client.post(
        "/api/message",
        json={
            "message": "Quem é o pai Lula?",
            "conversation_id": (
                "conversation-ambiguous"
            ),
        },
    )

    body = response.get_data(
        as_text=True
    )

    assert response.status_code == 200

    assert "event: route" in body
    assert (
        '"route": "ambiguous"'
        in body
    )

    assert (
        "event: clarification"
        in body
    )

    assert '"attempt": 1' in body
    assert '"keywords"' in body
    assert '"options"' in body

    assert "event: done" in body


def test_message_reuses_conversation_id(
    client,
    monkeypatch,
):
    received = {}

    def fake_stream_message(
        message,
        settings,
        conversation_id,
    ):
        received[
            "conversation_id"
        ] = conversation_id

        yield {
            "type": "route",
            "route": "chat",
            "confidence": 0.95,
            "reason": "test",
            "conversation_id": conversation_id,
        }

    monkeypatch.setattr(
        message_route.orchestrator,
        "stream_message",
        fake_stream_message,
    )

    response = client.post(
        "/api/message",
        json={
            "message": "Olá Bruce",
            "conversation_id": (
                "conversation-123"
            ),
        },
    )

    assert response.status_code == 200

    assert (
        received["conversation_id"]
        == "conversation-123"
    )


def test_message_generates_conversation_id(
    client,
    monkeypatch,
):
    received = {}

    def fake_stream_message(
        message,
        settings,
        conversation_id,
    ):
        received[
            "conversation_id"
        ] = conversation_id

        yield {
            "type": "route",
            "route": "chat",
            "confidence": 0.95,
            "reason": "test",
            "conversation_id": conversation_id,
        }

    monkeypatch.setattr(
        message_route.orchestrator,
        "stream_message",
        fake_stream_message,
    )

    response = client.post(
        "/api/message",
        json={
            "message": "Olá Bruce",
        },
    )

    assert response.status_code == 200

    assert received[
        "conversation_id"
    ]

    assert isinstance(
        received["conversation_id"],
        str,
    )


def test_rejects_invalid_conversation_id(
    client,
):
    response = client.post(
        "/api/message",
        json={
            "message": "Olá Bruce",
            "conversation_id": 123,
        },
    )

    assert response.status_code == 400