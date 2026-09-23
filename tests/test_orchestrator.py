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

    received = {}

    def fake_stream_chat(
        message,
        settings,
        *,
        lang="pt",
    ):
        received["message"] = message
        received["lang"] = lang

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

    assert (
        received["message"]
        == "Olá Bruce"
    )

    assert (
        received["lang"]
        == "pt"
    )


def test_research_route_uses_rag(
    monkeypatch,
):
    orchestrator = make_orchestrator(
        Intent.RESEARCH
    )

    def fake_search_wikipedia(
        query,
        *,
        lang="pt",
        limit=5,
    ):
        return [
            {
                "title": "Alan Turing",
                "url": "https://example.com/alan-turing",
                "rank": 1,
            },
            {
                "title": "Máquina de Turing",
                "url": "https://example.com/turing-machine",
                "rank": 2,
            },
        ]

    received = {}

    def fake_stream_rag_answer(
        message,
        settings,
        *,
        search_query=None,
        resolved_title=None,
        lang="pt",
    ):
        received["message"] = message
        received["search_query"] = search_query
        received["resolved_title"] = resolved_title
        received["lang"] = lang

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
        "search_wikipedia",
        fake_search_wikipedia,
    )

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
    assert events[0]["route"] == "research"

    assert events[1]["type"] == "sources"

    assert events[2] == {
        "type": "token",
        "content": "Alan Turing",
    }

    assert (
        received["message"]
        == "Quem foi Alan Turing?"
    )

    assert (
        received["resolved_title"]
        == "Alan Turing"
    )

    assert received["lang"] == "pt"


def test_general_research_uses_rag_without_entity_resolution(
    monkeypatch,
):
    orchestrator = make_orchestrator(
        Intent.RESEARCH
    )

    received = {}

    def fake_stream_rag_answer(
        message,
        settings,
        *,
        search_query=None,
        resolved_title=None,
        lang="pt",
    ):
        received["message"] = message
        received["search_query"] = search_query
        received["resolved_title"] = resolved_title
        received["lang"] = lang

        yield {
            "type": "token",
            "content": "Conhecimento",
        }

    monkeypatch.setattr(
        "DeepBruce_AI.services.orchestrator."
        "should_resolve_entity",
        lambda message: False,
    )

    monkeypatch.setattr(
        "DeepBruce_AI.services.orchestrator."
        "stream_rag_answer",
        fake_stream_rag_answer,
    )

    events = list(
        orchestrator.stream_message(
            "Como funciona a fotossíntese?",
            settings=None,
            conversation_id="test-general-research",
        )
    )

    assert events[0]["route"] == "research"
    assert events[1] == {
        "type": "token",
        "content": "Conhecimento",
    }
    assert received == {
        "message": "Como funciona a fotossíntese?",
        "search_query": None,
        "resolved_title": None,
        "lang": "pt",
    }


def test_ambiguous_entity_requests_specific_name(
    monkeypatch,
):
    orchestrator = make_orchestrator(
        Intent.RESEARCH
    )

    monkeypatch.setattr(
        "DeepBruce_AI.services.orchestrator.search_wikipedia",
        lambda *args, **kwargs: [
            {"title": "Justin Bieber"},
            {"title": "Justin Timberlake"},
            {"title": "Justin Trudeau"},
        ],
    )

    events = list(
        orchestrator.stream_message(
            "Quem é o Justin?",
            settings=None,
            conversation_id="test-ambiguous-justin",
        )
    )

    clarification = events[1]

    assert clarification["type"] == "clarification"
    assert clarification["message"] == (
        "Você se refere a qual Justin?"
    )
    assert [
        option["label"]
        for option in clarification["options"]
    ] == [
        "Justin Bieber",
        "Justin Timberlake",
        "Justin Trudeau",
    ]

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