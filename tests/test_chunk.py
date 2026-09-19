import pytest

from DeepBruce_AI.services.chunk import (
    Chunk,
    build_chunks,
    split_sentences,
)


def test_split_sentences_returns_empty_for_empty_text():
    assert split_sentences("") == []
    assert split_sentences("   ") == []


def test_split_sentences_normalizes_whitespace():
    result = split_sentences(
        "Python   é legal.   RAG também é."
    )

    assert result == [
        "Python é legal.",
        "RAG também é.",
    ]


def test_build_chunks_keeps_small_text_in_one_chunk():
    chunks = build_chunks(
        "Python é uma linguagem. Ela é muito utilizada.",
        source_id="wiki-python",
        source="wikipedia",
        title="Python",
        url="https://pt.wikipedia.org/wiki/Python",
        max_chars=500,
    )

    assert len(chunks) == 1
    assert chunks[0].id == "wiki-python-0000"
    assert chunks[0].position == 0
    assert chunks[0].title == "Python"


def test_build_chunks_preserves_metadata():
    chunks = build_chunks(
        "DeepBruce usa recuperação de contexto.",
        source_id="deepbruce",
        metadata={"language": "pt-BR"},
    )

    record = chunks[0].to_record()

    assert record["id"] == "deepbruce-0000"
    assert record["meta"]["language"] == "pt-BR"
    assert record["meta"]["position"] == 0


def test_build_chunks_creates_overlap():
    text = (
        "Alpha one. "
        "Beta two. "
        "Gamma three. "
        "Delta four."
    )

    chunks = build_chunks(
        text,
        source_id="test",
        max_chars=23,
        overlap_sentences=1,
    )

    assert len(chunks) >= 2

    first_words = set(chunks[0].text.split())
    second_words = set(chunks[1].text.split())

    assert first_words & second_words


def test_chunks_respect_max_chars():
    text = (
        "Primeira frase relativamente longa. "
        "Segunda frase relativamente longa. "
        "Terceira frase relativamente longa."
    )

    chunks = build_chunks(
        text,
        source_id="limit-test",
        max_chars=40,
        overlap_sentences=1,
    )

    assert chunks

    for chunk in chunks:
        assert len(chunk.text) <= 40


def test_build_chunks_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        build_chunks(
            "texto",
            source_id="test",
            max_chars=0,
        )

    with pytest.raises(ValueError):
        build_chunks(
            "texto",
            source_id="test",
            overlap_sentences=-1,
        )


def test_build_chunks_requires_source_id():
    with pytest.raises(ValueError):
        build_chunks(
            "texto",
            source_id="",
        )