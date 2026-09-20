import pytest

from DeepBruce_AI.services.context import (
    build_context,
)


def make_results():
    return [
        {
            "id": "chunk-1",
            "document": (
                "Justin Bieber é um cantor "
                "canadense."
            ),
            "metadata": {
                "title": "Justin Bieber",
                "url": (
                    "https://pt.wikipedia.org/"
                    "wiki/Justin_Bieber"
                ),
                "source": "wikipedia",
            },
            "score": 0.91,
        },
        {
            "id": "chunk-2",
            "document": (
                "Bieber iniciou sua carreira "
                "musical ainda jovem."
            ),
            "metadata": {
                "title": "Justin Bieber",
                "url": (
                    "https://pt.wikipedia.org/"
                    "wiki/Justin_Bieber"
                ),
                "source": "wikipedia",
            },
            "score": 0.82,
        },
    ]


def test_empty_results_return_empty_context():
    context, sources = build_context([])

    assert context == ""
    assert sources == []


def test_context_contains_documents():
    context, sources = build_context(
        make_results()
    )

    assert (
        "Justin Bieber é um cantor canadense."
        in context
    )

    assert (
        "Bieber iniciou sua carreira musical"
        in context
    )


def test_context_contains_source_metadata():
    context, _ = build_context(
        make_results()
    )

    assert "Título: Justin Bieber" in context
    assert "Fonte: wikipedia" in context

    assert (
        "https://pt.wikipedia.org/wiki/Justin_Bieber"
        in context
    )


def test_sources_are_deduplicated():
    _, sources = build_context(
        make_results()
    )

    assert len(sources) == 1

    assert (
        sources[0]["title"]
        == "Justin Bieber"
    )


def test_max_chunks_is_respected():
    context, _ = build_context(
        make_results(),
        max_chunks=1,
    )

    assert "[TRECHO 1]" in context
    assert "[TRECHO 2]" not in context


def test_context_respects_character_budget():
    context, _ = build_context(
        make_results(),
        max_chars=150,
    )

    assert len(context) <= 150


def test_invalid_configuration_raises_error():
    with pytest.raises(ValueError):
        build_context(
            make_results(),
            max_chars=0,
        )

    with pytest.raises(ValueError):
        build_context(
            make_results(),
            max_chunks=0,
        )