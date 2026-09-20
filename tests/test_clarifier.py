from DeepBruce_AI.services.clarifier import (
    build_clarification,
)


def test_extracts_ambiguous_relationship_options():
    result = build_clarification(
        "Quem é o pai Lula?"
    )

    assert "pai" in [
        keyword.lower()
        for keyword in result.keywords
    ]

    assert "lula" in [
        keyword.lower()
        for keyword in result.keywords
    ]

    assert len(result.options) == 2


def test_first_option_asks_relationship():
    result = build_clarification(
        "Quem é o pai Lula?"
    )

    assert (
        result.options[0].query
        == "Quem foi o pai de lula?"
    )


def test_second_option_asks_about_entity():
    result = build_clarification(
        "Quem é o pai Lula?"
    )

    assert (
        result.options[1].query
        == "Quem é lula?"
    )


def test_generic_ambiguity_has_no_options():
    result = build_clarification(
        "Me explica aquele negócio lá"
    )

    assert result.options == []
    assert result.message