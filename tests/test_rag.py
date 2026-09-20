from DeepBruce_AI.services.rag import (
    _position_score,
    _rerank_wikipedia_results,
)


def test_position_score_prefers_early_chunks():
    assert _position_score(0) == 1.0
    assert _position_score(1) == 0.5
    assert _position_score(3) == 0.25


def test_reranker_prefers_introductory_chunk():
    results = [
        {
            "id": "later",
            "document": "Trecho posterior",
            "metadata": {
                "title": "Justin Bieber",
                "search_rank": 1,
                "position": 45,
            },
            "score": 0.4894,
            "bm25_score": 0.0,
            "tfidf_score": 0.0,
        },
        {
            "id": "intro",
            "document": "Justin Bieber é um cantor canadense.",
            "metadata": {
                "title": "Justin Bieber",
                "search_rank": 1,
                "position": 0,
            },
            "score": 0.1432,
            "bm25_score": 0.0,
            "tfidf_score": 0.0,
        },
    ]

    ranked = _rerank_wikipedia_results(
        "Quem é o Justin Bieber?",
        results,
        top_k=2,
    )

    assert ranked[0]["id"] == "intro"
    assert ranked[0]["position_score"] == 1.0
    assert ranked[0]["score"] > ranked[1]["score"]