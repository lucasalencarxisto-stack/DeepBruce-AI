from DeepBruce_AI.services.intent import (
    Intent,
    RuleBasedIntentClassifier,
)


def classifier():
    return RuleBasedIntentClassifier()


def test_routes_greeting_to_chat():
    result = classifier().classify(
        "Olá Bruce!"
    )

    assert result.intent == Intent.CHAT


def test_routes_social_question_to_chat():
    result = classifier().classify(
        "Como você está?"
    )

    assert result.intent == Intent.CHAT


def test_routes_user_introduction_to_chat():
    result = classifier().classify(
        "Meu nome é Lucas"
    )

    assert result.intent == Intent.CHAT


def test_routes_assistant_identity_to_chat():
    result = classifier().classify(
        "Quem é você?"
    )

    assert result.intent == Intent.CHAT


def test_routes_definition_to_research():
    result = classifier().classify(
        "Quem foi Alan Turing?"
    )

    assert result.intent == Intent.RESEARCH


def test_routes_explanation_to_research():
    result = classifier().classify(
        "Como funciona um buraco negro?"
    )

    assert result.intent == Intent.RESEARCH


def test_detects_ambiguous_relationship():
    result = classifier().classify(
        "Quem é o pai Lula?"
    )

    assert result.intent == Intent.AMBIGUOUS
    assert result.confidence < 0.70


def test_clear_relationship_goes_to_research():
    result = classifier().classify(
        "Quem é o pai do Lula?"
    )

    assert result.intent == Intent.RESEARCH