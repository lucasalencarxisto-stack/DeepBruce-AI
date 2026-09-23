import time
from typing import Any, Dict, List
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup


API = "https://{lang}.wikipedia.org/w/api.php"
REST_BASE = "https://{lang}.wikipedia.org/api/rest_v1"

HEADERS = {
    "User-Agent": (
        "DeepBruce-AI/1.0 "
        "(educational RAG project)"
    )
}


def _get(
    url: str,
    *,
    params: Dict[str, Any] | None = None,
    tries: int = 3,
):
    """
    Executa uma requisição GET com retry simples para
    erros transitórios da Wikipedia.
    """
    for attempt in range(tries):
        try:
            response = requests.get(
                url,
                params=params,
                timeout=30,
                headers=HEADERS,
            )

        except requests.RequestException:
            if attempt == tries - 1:
                return None

            time.sleep(1.0 + attempt * 0.5)
            continue

        if response.status_code == 200:
            return response

        if response.status_code in (429, 502, 503, 504):
            time.sleep(1.0 + attempt * 0.5)
            continue

        return None

    return None


def _build_page_url(
    lang: str,
    title: str,
) -> str:
    """
    Gera uma URL segura para uma página da Wikipedia.
    """
    normalized_title = title.strip().replace(" ", "_")

    encoded_title = quote(
        normalized_title,
        safe="_()-",
    )

    return (
        f"https://{lang}.wikipedia.org/"
        f"wiki/{encoded_title}"
    )


def _clean_snippet(snippet: str) -> str:
    """
    Remove HTML dos snippets retornados pela busca.
    """
    if not snippet:
        return ""

    soup = BeautifulSoup(
        snippet,
        "html.parser",
    )

    return soup.get_text(
        " ",
        strip=True,
    )


def search_wikipedia(
    query: str,
    *,
    lang: str = "pt",
    limit: int = 3,
    _allow_suggestion: bool = True,
) -> List[Dict[str, Any]]:
    """
    Pesquisa páginas da Wikipedia a partir de uma
    pergunta ou termo em linguagem natural.

    Retorna resultados ordenados conforme o ranking
    fornecido pela própria Wikipedia.
    """
    query = (query or "").strip()

    if not query:
        return []

    if limit <= 0:
        return []

    response = _get(
        API.format(lang=lang),
        params={
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
            "utf8": 1,
            "format": "json",
        },
    )

    if response is None:
        return []

    try:
        payload = response.json()
    except ValueError:
        return []

    hits = (
        payload
        .get("query", {})
        .get("search", [])
    )

    if not hits and _allow_suggestion:
        suggestion = (
            payload
            .get("query", {})
            .get("searchinfo", {})
            .get("suggestion")
        )

        if suggestion and suggestion.strip().lower() != query.lower():
            return search_wikipedia(
                suggestion,
                lang=lang,
                limit=limit,
                _allow_suggestion=False,
            )

    results: List[Dict[str, Any]] = []

    for rank, hit in enumerate(
        hits,
        start=1,
    ):
        title = hit.get("title", "").strip()

        if not title:
            continue

        results.append(
            {
                "title": title,
                "pageid": hit.get("pageid"),
                "snippet": _clean_snippet(
                    hit.get("snippet", "")
                ),
                "url": _build_page_url(
                    lang,
                    title,
                ),
                "rank": rank,
            }
        )

    return results


def _plain(
    lang: str,
    title: str,
) -> Dict[str, Any]:
    """
    Tenta recuperar a versão plain-text da página.
    """
    normalized_title = (
        title.strip()
        .replace(" ", "_")
    )

    encoded_title = quote(
        normalized_title,
        safe="_()-",
    )

    response = _get(
        f"{REST_BASE.format(lang=lang)}"
        f"/page/plain/{encoded_title}"
    )

    if response is None:
        return {}

    text = response.text.strip()

    if not text:
        return {}

    return {
        "title": title.replace("_", " "),
        "text": text,
        "url": _build_page_url(
            lang,
            title,
        ),
        "source": "wikipedia",
    }


def _html(
    lang: str,
    title: str,
) -> Dict[str, Any]:
    """
    Fallback HTML caso o endpoint plain-text não
    consiga retornar conteúdo.
    """
    normalized_title = (
        title.strip()
        .replace(" ", "_")
    )

    encoded_title = quote(
        normalized_title,
        safe="_()-",
    )

    response = _get(
        f"{REST_BASE.format(lang=lang)}"
        f"/page/html/{encoded_title}"
    )

    if response is None:
        return {}

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    for element in soup.select(
        (
            "table, "
            ".reference, "
            "sup.reference, "
            "style, "
            "script"
        )
    ):
        element.decompose()

    text = soup.get_text(
        " ",
        strip=True,
    )

    if not text:
        return {}

    return {
        "title": title.replace("_", " "),
        "text": text,
        "url": _build_page_url(
            lang,
            title,
        ),
        "source": "wikipedia",
    }


def fetch_wikipedia_page(
    title: str,
    *,
    lang: str = "pt",
) -> Dict[str, Any]:
    """
    Recupera o conteúdo completo de uma página
    conhecida da Wikipedia.
    """
    title = (title or "").strip()

    if not title:
        return {}

    data = _plain(
        lang,
        title,
    )

    if data.get("text"):
        return data

    return _html(
        lang,
        title,
    )


def fetch_wikipedia_candidates(
    query: str,
    *,
    lang: str = "pt",
    limit: int = 3,
) -> List[Dict[str, Any]]:
    """
    Pipeline de descoberta da Wikipedia:

    pergunta -> busca -> páginas -> texto.

    Retorna documentos prontos para serem enviados
    ao Smart Chunker.
    """
    search_results = search_wikipedia(
        query,
        lang=lang,
        limit=limit,
    )

    pages: List[Dict[str, Any]] = []

    for result in search_results:
        page = fetch_wikipedia_page(
            result["title"],
            lang=lang,
        )

        if not page.get("text"):
            continue

        page["pageid"] = result.get(
            "pageid"
        )

        page["search_rank"] = result.get(
            "rank"
        )

        page["search_snippet"] = result.get(
            "snippet",
            "",
        )

        pages.append(page)

    return pages