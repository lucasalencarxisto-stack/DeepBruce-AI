from DeepBruce_AI.services.intent import (
    Intent,
    IntentResult,
)
from DeepBruce_AI.services.orchestrator import (
    DeepBruceOrchestrator,
)
from DeepBruce_AI.services.router import (
    MessageRouter,
)


class FakeClassifier:
    def __init__(
        self,
        intent: Intent,
        confidence: float = 0.95,
        reason: str = "test",
    ):
        self.result = IntentResult(
            intent=intent,
            confidence=confidence,
            reason=reason,
        )

    def classify(
        self,
        message: str,
    ) -> IntentResult:
        return self.result


def make_orchestrator(
    intent: Intent,
    confidence: float = 0.95,
):
    classifier = FakeClassifier(
        intent=intent,
        confidence=confidence,
    )

    router = MessageRouter(
        classifier=classifier,
    )

    return DeepBruceOrchestrator(
        router=router,
    )


def test_empty_message_returns_error():
    orchestrator = make_orchestrator(
        Intent.CHAT
    )

    events = list(
        orchestrator.stream_message(
            "",
            settings=None,
            conversation_id="test-conversation",
        )
    )

    assert events[0]["type"] == "error"
    assert (
        events[0]["code"]
        == "empty_message"
    )


def test_chat_route_streams_ollama_tokens(
    monkeypatch,
):
    orchestrator = make_orchestrator(
        Intent.CHAT
    )

    def fake_stream_chat(
        message,
        settings,
    ):
        yield "Olá"
        yield "!"
    
    monkeypatch.setattr(
        "DeepBruce_AI.services.orchestrator."
        "ollama.stream_chat",
        fake_stream_chat,
    )

    events = list(
        orchestrator.stream_message(
            "Olá Bruce",
            settings=None,
            conversation_id="test-conversation"
        )
    )

    assert events[0]["type"] == "route"
    assert events[0]["route"] == "chat"

    assert events[1] == {
        "type": "token",
        "content": "Olá",
    }

    assert events[2] == {
        "type": "token",
        "content": "!",
    }


def test_research_route_uses_rag(
    monkeypatch,
):
    orchestrator = make_orchestrator(
        Intent.RESEARCH
    )

    def fake_stream_rag_answer(
        message,
        settings,
    ):
        yield {
            "type": "sources",
            "sources": [
                {
                    "title": "Alan Turing",
                    "url": "https://example.com",
                    "source": "wikipedia",
                }
            ],
        }

        yield {
            "type": "token",
            "content": "Alan Turing",
        }

    monkeypatch.setattr(
        "DeepBruce_AI.services.orchestrator."
        "stream_rag_answer",
        fake_stream_rag_answer,
    )

    events = list(
        orchestrator.stream_message(
            "Quem foi Alan Turing?",
            settings=None,
            conversation_id="test-conversation",
        )
    )

    assert events[0]["type"] == "route"
    assert (
        events[0]["route"]
        == "research"
    )

    assert (
        events[1]["type"]
        == "sources"
    )

    assert events[2] == {
        "type": "token",
        "content": "Alan Turing",
    }


def test_ambiguous_route_requests_clarification():
    orchestrator = make_orchestrator(
        Intent.AMBIGUOUS,
        confidence=0.55,
    )

    events = list(
        orchestrator.stream_message(
            "Quem é o pai Lula?",
            settings=None,
            conversation_id="test-conversation",
        )
    )

    assert events[0]["type"] == "route"
    assert (
        events[0]["route"]
        == "ambiguous"
    )

    clarification = events[1]

    assert (
        clarification["type"]
        == "clarification"
    )

    assert (
        clarification["original_message"]
        == "Quem é o pai Lula?"
    )

    assert (
        clarification["confidence"]
        == 0.55
    )

def test_fallback_after_clarification_limit():
    orchestrator = make_orchestrator(
        Intent.AMBIGUOUS,
        confidence=0.55,
    )

    conversation_id = "conversation-fallback"

    first = list(
        orchestrator.stream_message(
            "Quem é o pai Lula?",
            settings=None,
            conversation_id=conversation_id,
        )
    )

    second = list(
        orchestrator.stream_message(
            "Não foi isso",
            settings=None,
            conversation_id=conversation_id,
        )
    )

    third = list(
        orchestrator.stream_message(
            "Também não",
            settings=None,
            conversation_id=conversation_id,
        )
    )

    assert any(
        event["type"] == "clarification"
        and event["attempt"] == 1
        for event in first
    )

    assert any(
        event["type"] == "clarification"
        and event["attempt"] == 2
        for event in second
    )

    fallback = [
        event
        for event in third
        if event["type"] == "fallback"
    ]

    assert len(fallback) == 1

    assert (
        fallback[0]["code"]
        == "clarification_limit_reached"
    )