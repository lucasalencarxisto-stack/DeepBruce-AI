from DeepBruce_AI.services.retriever import Retriever


class FakeStore:
    def __init__(self, rows):
        self.rows = rows
        self.calls = 0

    def fetch_namespace(self, namespace):
        self.calls += 1
        return self.rows


def make_rows():
    return [
        {
            "id": "python-1",
            "text": (
                "Python foi criada por Guido van Rossum "
                "e lançada inicialmente em 1991."
            ),
            "meta": {
                "title": "Python",
            },
        },
        {
            "id": "java-1",
            "text": (
                "Java é uma linguagem orientada a objetos "
                "criada originalmente pela Sun Microsystems."
            ),
            "meta": {
                "title": "Java",
            },
        },
        {
            "id": "python-2",
            "text": (
                "Python é muito utilizada em ciência de dados, "
                "automação e inteligência artificial."
            ),
            "meta": {
                "title": "Python",
            },
        },
    ]


def test_empty_query_returns_no_results():
    retriever = Retriever(
        FakeStore(make_rows())
    )

    assert retriever.search(
        "default",
        "",
    ) == []


def test_retriever_finds_relevant_document():
    retriever = Retriever(
        FakeStore(make_rows())
    )

    results = retriever.search(
        "default",
        "Quem criou Python?",
        top_k=2,
    )

    assert results
    assert results[0]["id"] == "python-1"


def test_result_contains_hybrid_scores():
    retriever = Retriever(
        FakeStore(make_rows())
    )

    result = retriever.search(
        "default",
        "Python inteligência artificial",
        top_k=1,
    )[0]

    assert "score" in result
    assert "bm25_score" in result
    assert "tfidf_score" in result

    assert 0 <= result["score"] <= 1


def test_top_k_is_respected():
    retriever = Retriever(
        FakeStore(make_rows())
    )

    results = retriever.search(
        "default",
        "linguagem programação",
        top_k=2,
    )

    assert len(results) <= 2


def test_retriever_uses_cached_index():
    store = FakeStore(make_rows())

    retriever = Retriever(store)

    retriever.search(
        "default",
        "Python",
    )

    retriever.search(
        "default",
        "Java",
    )

    assert store.calls == 1


def test_invalidate_rebuilds_index():
    store = FakeStore(make_rows())

    retriever = Retriever(store)

    retriever.search(
        "default",
        "Python",
    )

    retriever.invalidate("default")

    retriever.search(
        "default",
        "Python",
    )

    assert store.calls == 2


def test_near_duplicate_chunks_are_filtered():
    rows = [
        {
            "id": "one",
            "text": (
                "Python foi criada por Guido van Rossum "
                "e lançada em 1991."
            ),
            "meta": {},
        },
        {
            "id": "two",
            "text": (
                "Python foi criada por Guido van Rossum "
                "e lançada em 1991."
            ),
            "meta": {},
        },
        {
            "id": "three",
            "text": (
                "Python possui uma grande comunidade "
                "de desenvolvedores."
            ),
            "meta": {},
        },
    ]

    retriever = Retriever(
        FakeStore(rows)
    )

    results = retriever.search(
        "default",
        "Python Guido comunidade",
        top_k=3,
    )

    ids = [
        result["id"]
        for result in results
    ]

    assert not (
        "one" in ids
        and "two" in ids
    )