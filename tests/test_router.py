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


def test_routes_project_identity_questions():
    messages = (
        "Quem te criou?",
        "Quem criou você?",
        "Quem é o seu criador?",
        "Que é o seu desenvolvedor?",
        "Quem desenvolveu o DeepBruce?",
        "Qual é o nome do seu desenvolvedor?",
        "Who created you?",
        "Who is your developer?",
        "¿Quién te creó?",
        "¿Quién es tu creador?",
    )

    for message in messages:
        decision = router().route(
            message
        )

        assert decision.route == "chat"
        assert decision.confidence == 1.0
        assert decision.reason == "project_identity"


def test_external_creator_question_is_not_project_identity():
    decision = router().route(
        "Quem criou o Python?"
    )

    assert decision.reason != "project_identity"
