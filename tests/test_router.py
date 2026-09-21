from DeepBruce_AI.services.router import (
    MessageRouter,
)


def router():
    return MessageRouter()


def test_routes_chat_message():
    decision = router().route(
        "Olá Bruce!"
    )

    assert decision.route == "chat"
    assert decision.confidence > 0


def test_routes_research_message():
    decision = router().route(
        "Quem foi Alan Turing?"
    )

    assert decision.route == "research"
    assert decision.confidence > 0


def test_routes_ambiguous_message():
    decision = router().route(
        "Quem é o pai Lula?"
    )

    assert decision.route == "ambiguous"
    assert decision.confidence < 0.70


def test_clear_relationship_routes_to_research():
    decision = router().route(
        "Quem é o pai do Lula?"
    )

    assert decision.route == "research"


def test_router_exposes_reason():
    decision = router().route(
        "Como você está?"
    )

    assert decision.reason