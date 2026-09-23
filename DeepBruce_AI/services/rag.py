import re
import unicodedata
from typing import Any, Dict, List

from DeepBruce_AI.config import Settings
from DeepBruce_AI.services import ollama
from DeepBruce_AI.services.chunk import build_chunks
from DeepBruce_AI.services.context import build_context
from DeepBruce_AI.services.retriever import Retriever
from DeepBruce_AI.services.wiki import (
    fetch_wikipedia_candidates,
    fetch_wikipedia_page,
)


class InMemoryStore:
    """
    Armazenamento temporário dos chunks usados
    durante uma consulta RAG.
    """

    def __init__(self):
        self._namespaces: Dict[
            str,
            List[Dict[str, Any]],
        ] = {}

    def replace_namespace(
        self,
        namespace: str,
        rows: List[Dict[str, Any]],
    ) -> None:
        self._namespaces[namespace] = rows

    def fetch_namespace(
        self,
        namespace: str,
    ) -> List[Dict[str, Any]]:
        return self._namespaces.get(
            namespace,
            [],
        )


def _build_source_id(
    page: Dict[str, Any],
    index: int,
) -> str:
    """
    Gera um ID previsível para os chunks de uma página.
    """

    pageid = page.get("pageid")

    if pageid:
        return f"wiki-{pageid}"

    return f"wiki-page-{index}"


def _normalize_text(
    text: str,
) -> str:
    """
    Normaliza texto para comparação entre pergunta
    e título da fonte.
    """

    text = unicodedata.normalize(
        "NFKD",
        text or "",
    )

    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )

    return text.lower().strip()


def _title_match_score(
    question: str,
    title: str,
) -> float:
    """
    Mede quanto do título da página aparece
    na pergunta do usuário.
    """

    question_tokens = set(
        re.findall(
            r"\w+",
            _normalize_text(question),
        )
    )

    title_tokens = set(
        re.findall(
            r"\w+",
            _normalize_text(title),
        )
    )

    if not question_tokens or not title_tokens:
        return 0.0

    matches = (
        question_tokens
        & title_tokens
    )

    return (
        len(matches)
        / len(title_tokens)
    )


def _source_rank_score(
    search_rank,
) -> float:
    """
    Converte o ranking original da Wikipedia
    em um score entre 0 e 1.

    rank 1 -> 1.0
    rank 2 -> 0.5
    rank 3 -> 0.333...
    """

    try:
        rank = int(
            search_rank
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0.0

    if rank <= 0:
        return 0.0

    return 1.0 / rank


def _position_score(
    position,
) -> float:
    """
    Dá preferência moderada aos primeiros chunks
    de uma página.

    posição 0 -> 1.0
    posição 1 -> 0.5
    posição 2 -> 0.333...
    """

    try:
        position = int(
            position
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0.0

    if position < 0:
        return 0.0

    return (
        1.0
        / (position + 1)
    )


def _rerank_wikipedia_results(
    question: str,
    results: List[Dict[str, Any]],
    *,
    top_k: int,
) -> List[Dict[str, Any]]:
    """
    Combina quatro sinais:

    - relevância lexical do Retriever;
    - correspondência entre pergunta e título;
    - ranking original da Wikipedia;
    - posição do chunk dentro da página.
    """

    reranked: List[
        Dict[str, Any]
    ] = []

    for result in results:
        metadata = result.get(
            "metadata",
            {},
        )

        retriever_score = float(
            result.get(
                "score",
                0.0,
            )
        )

        title_score = (
            _title_match_score(
                question,
                metadata.get(
                    "title",
                    "",
                ),
            )
        )

        source_score = (
            _source_rank_score(
                metadata.get(
                    "search_rank"
                )
            )
        )

        position_score = (
            _position_score(
                metadata.get(
                    "position"
                )
            )
        )

        rag_score = (
            0.30 * retriever_score
            + 0.25 * title_score
            + 0.15 * source_score
            + 0.30 * position_score
        )

        reranked.append(
            {
                **result,
                "retriever_score": (
                    retriever_score
                ),
                "title_match_score": (
                    title_score
                ),
                "source_rank_score": (
                    source_score
                ),
                "position_score": (
                    position_score
                ),
                "score": float(
                    rag_score
                ),
            }
        )

    reranked.sort(
        key=lambda result: (
            result["score"]
        ),
        reverse=True,
    )

    return reranked[:top_k]


def retrieve_wikipedia_context(
    question: str,
    *,
    search_query: str | None = None,
    resolved_title: str | None = None,
    lang: str = "pt",
    page_limit: int = 3,
    top_k: int = 5,
    max_chars: int = 1400,
    overlap_sentences: int = 2,
) -> List[Dict[str, Any]]:
    """
    Recuperação RAG orientada por fonte.

    Quando uma entidade já foi resolvida,
    recupera diretamente sua página.

    Caso contrário, executa a descoberta
    normal de candidatos na Wikipedia.
    """

    question = (
        question or ""
    ).strip()

    if not question:
        return []

    if resolved_title:
        page = fetch_wikipedia_page(
            resolved_title,
            lang=lang,
        )

        if page.get("text"):
            page[
                "search_rank"
            ] = 1

            pages = [
                page
            ]

        else:
            pages = []

    else:
        wiki_query = (
            search_query
            or question
        ).strip()

        pages = (
            fetch_wikipedia_candidates(
                wiki_query,
                lang=lang,
                limit=page_limit,
            )
        )

    if not pages:
        return []

    store = InMemoryStore()

    retriever = Retriever(
        store
    )

    candidates: List[
        Dict[str, Any]
    ] = []

    for index, page in enumerate(
        pages,
        start=1,
    ):
        text = (
            page.get(
                "text",
                "",
            )
            or ""
        ).strip()

        if not text:
            continue

        source_id = (
            _build_source_id(
                page,
                index,
            )
        )

        chunks = build_chunks(
            text,
            source_id=source_id,
            source="wikipedia",
            title=page.get(
                "title",
                "",
            ),
            url=page.get(
                "url",
                "",
            ),
            max_chars=max_chars,
            overlap_sentences=(
                overlap_sentences
            ),
            metadata={
                "pageid": (
                    page.get(
                        "pageid"
                    )
                ),
                "search_rank": (
                    page.get(
                        "search_rank"
                    )
                ),
            },
        )

        records = [
            chunk.to_record()
            for chunk
            in chunks
        ]

        if not records:
            continue

        namespace = (
            f"wikipedia-query-{index}"
        )

        store.replace_namespace(
            namespace,
            records,
        )

        page_results = (
            retriever.search(
                namespace,
                question,
                top_k=top_k,
            )
        )

        candidates.extend(
            page_results
        )

    if not candidates:
        return []

    return (
        _rerank_wikipedia_results(
            question,
            candidates,
            top_k=top_k,
        )
    )


def stream_rag_answer(
    question: str,
    settings: Settings,
    *,
    search_query: str | None = None,
    resolved_title: str | None = None,
    lang: str = "pt",
    page_limit: int = 2,
    top_k: int = 3,
    max_context_chars: int = 5_000,
):
    """
    Executa o pipeline RAG completo:

    pergunta
        -> Wikipedia
        -> Chunker
        -> Retriever
        -> Reranker
        -> Context Builder
        -> Ollama
    """

    question = (
        question or ""
    ).strip()

    if not question:
        return

    results = (
        retrieve_wikipedia_context(
            question,
            search_query=(
                search_query
            ),
            resolved_title=(
                resolved_title
            ),
            lang=lang,
            page_limit=page_limit,
            top_k=top_k,
        )
    )

    context, sources = (
        build_context(
            results,
            max_chars=(
                max_context_chars
            ),
            max_chunks=top_k,
        )
    )

    if not context:
        context = (
            "Nenhuma informação relevante foi "
            "recuperada das fontes disponíveis."
        )

    yield {
        "type": "sources",
        "sources": sources,
    }

    for token in (
        ollama
        .stream_chat_with_context(
            question,
            context,
            settings,
            lang=lang,
        )
    ):
        yield {
            "type": "token",
            "content": token,
        }