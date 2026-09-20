from wsgi import app

import DeepBruce_AI.routes.rag_chat as rag_chat_module


def test_rag_chat_streams_sources_tokens_and_done(
    monkeypatch,
):
    def fake_stream_rag_answer(
        question,
        settings,
        **kwargs,
    ):
        yield {
            "type": "sources",
            "sources": [
                {
                    "title": "Justin Bieber",
                    "url": "https://pt.wikipedia.org/wiki/Justin_Bieber",
                    "source": "wikipedia",
                }
            ],
        }

        yield {
            "type": "token",
            "content": "Justin Bieber",
        }

    monkeypatch.setattr(
        rag_chat_module,
        "stream_rag_answer",
        fake_stream_rag_answer,
    )

    client = app.test_client()

    response = client.post(
        "/api/rag/chat",
        json={
            "message": "Quem é o Justin Bieber?"
        },
    )

    body = response.get_data(
        as_text=True,
    )

    assert response.status_code == 200
    assert "event: sources" in body
    assert "Justin Bieber" in body
    assert "event: token" in body
    assert "event: done" in body


def test_rag_chat_rejects_empty_message():
    client = app.test_client()

    response = client.post(
        "/api/rag/chat",
        json={
            "message": ""
        },
    )

    assert response.status_code == 400