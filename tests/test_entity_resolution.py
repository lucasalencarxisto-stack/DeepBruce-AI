from DeepBruce_AI.services.entity_resolution import (
    EntityCandidate,
    EntityStatus,
    extract_entity_text,
    resolve_entity,
    should_resolve_entity,
)


JUSTIN_CANDIDATES = [
    EntityCandidate(
        title="Justin Bieber",
    ),
    EntityCandidate(
        title="Justin Timberlake",
    ),
    EntityCandidate(
        title="Justin Trudeau",
    ),
]


def test_exact_entity_is_resolved():
    result = resolve_entity(
        "Quem é Justin Bieber?",
        JUSTIN_CANDIDATES,
    )

    assert (
        result.status
        == EntityStatus.RESOLVED
    )

    assert (
        result.resolved_title
        == "Justin Bieber"
    )


def test_typo_is_resolved():
    result = resolve_entity(
        "Quem é Justem Biber?",
        JUSTIN_CANDIDATES,
    )

    assert (
        result.status
        == EntityStatus.RESOLVED
    )

    assert (
        result.resolved_title
        == "Justin Bieber"
    )


def test_single_name_is_ambiguous():
    result = resolve_entity(
        "Quem é o Justin?",
        JUSTIN_CANDIDATES,
    )

    assert (
        result.status
        == EntityStatus.AMBIGUOUS
    )

    assert len(
        result.candidates
    ) >= 2


def test_resolved_entity_has_confidence():
    result = resolve_entity(
        "Justin Bieber",
        JUSTIN_CANDIDATES,
    )

    assert (
        result.confidence
        > 0.90
    )


def test_unknown_entity_is_not_found():
    result = resolve_entity(
        "xyzabc impossível",
        JUSTIN_CANDIDATES,
    )

    assert (
        result.status
        == EntityStatus.NOT_FOUND
    )


def test_detects_person_entity_lookup():
    assert (
        should_resolve_entity(
            "Quem é o Justin?"
        )
        is True
    )


def test_detects_definition_entity_lookup():
    assert (
        should_resolve_entity(
            "O que é Python?"
        )
        is True
    )


def test_generic_research_skips_entity_resolution():
    assert (
        should_resolve_entity(
            "Como funciona um buraco negro?"
        )
        is False
    )


def test_extracts_entity_from_question():
    entity = extract_entity_text(
        "Quem é o Justin?"
    )

    assert entity == "justin"