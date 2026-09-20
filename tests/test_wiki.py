from DeepBruce_AI.services import wiki


class FakeResponse:
    def __init__(
        self,
        *,
        json_data=None,
        text="",
        status_code=200,
    ):
        self._json_data = json_data
        self.text = text
        self.status_code = status_code

    def json(self):
        return self._json_data


def test_search_empty_query_returns_empty():
    assert wiki.search_wikipedia("") == []


def test_search_invalid_limit_returns_empty():
    assert wiki.search_wikipedia(
        "Python",
        limit=0,
    ) == []


def test_search_wikipedia_returns_results(
    monkeypatch,
):
    payload = {
        "query": {
            "search": [
                {
                    "title": "Justin Bieber",
                    "pageid": 123,
                    "snippet": (
                        "<span>cantor canadense</span>"
                    ),
                },
                {
                    "title": (
                        "Discografia de Justin Bieber"
                    ),
                    "pageid": 456,
                    "snippet": "discografia",
                },
            ]
        }
    }

    def fake_get(
        url,
        *,
        params=None,
        tries=3,
    ):
        return FakeResponse(
            json_data=payload
        )

    monkeypatch.setattr(
        wiki,
        "_get",
        fake_get,
    )

    results = wiki.search_wikipedia(
        "Quem é o Justin Bieber?",
        limit=2,
    )

    assert len(results) == 2

    assert (
        results[0]["title"]
        == "Justin Bieber"
    )

    assert results[0]["pageid"] == 123
    assert results[0]["rank"] == 1

    assert (
        results[0]["snippet"]
        == "cantor canadense"
    )


def test_fetch_wikipedia_page_prefers_plain(
    monkeypatch,
):
    expected = {
        "title": "Python",
        "text": "Python é uma linguagem.",
        "url": "https://example.com",
        "source": "wikipedia",
    }

    monkeypatch.setattr(
        wiki,
        "_plain",
        lambda lang, title: expected,
    )

    result = wiki.fetch_wikipedia_page(
        "Python"
    )

    assert result == expected


def test_fetch_wikipedia_page_uses_html_fallback(
    monkeypatch,
):
    monkeypatch.setattr(
        wiki,
        "_plain",
        lambda lang, title: {},
    )

    monkeypatch.setattr(
        wiki,
        "_html",
        lambda lang, title: {
            "title": title,
            "text": "Fallback HTML",
            "url": "https://example.com",
            "source": "wikipedia",
        },
    )

    result = wiki.fetch_wikipedia_page(
        "Python"
    )

    assert result["text"] == "Fallback HTML"


def test_fetch_candidates_combines_search_and_page(
    monkeypatch,
):
    monkeypatch.setattr(
        wiki,
        "search_wikipedia",
        lambda query, lang="pt", limit=3: [
            {
                "title": "Justin Bieber",
                "pageid": 123,
                "snippet": "cantor canadense",
                "rank": 1,
                "url": "https://example.com",
            }
        ],
    )

    monkeypatch.setattr(
        wiki,
        "fetch_wikipedia_page",
        lambda title, lang="pt": {
            "title": title,
            "text": (
                "Justin Bieber é um "
                "cantor canadense."
            ),
            "url": "https://example.com",
            "source": "wikipedia",
        },
    )

    pages = wiki.fetch_wikipedia_candidates(
        "Quem é o Justin Bieber?"
    )

    assert len(pages) == 1

    page = pages[0]

    assert page["title"] == "Justin Bieber"
    assert page["pageid"] == 123
    assert page["search_rank"] == 1

    assert (
        page["search_snippet"]
        == "cantor canadense"
    )