from typing import Any, Dict, List, Tuple


def build_context(
    results: List[Dict[str, Any]],
    *,
    max_chars: int = 10_000,
    max_chunks: int = 5,
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Constrói o contexto que será enviado ao LLM.

    Recebe resultados rankeados pelo Retriever e retorna:

    - texto formatado para o prompt;
    - lista de fontes únicas utilizadas.
    """

    if max_chars <= 0:
        raise ValueError(
            "max_chars deve ser maior que zero."
        )

    if max_chunks <= 0:
        raise ValueError(
            "max_chunks deve ser maior que zero."
        )

    if not results:
        return "", []

    context_parts: List[str] = []
    sources: List[Dict[str, Any]] = []

    seen_sources = set()
    current_size = 0

    for index, result in enumerate(
        results[:max_chunks],
        start=1,
    ):
        document = (
            result.get("document", "")
            or ""
        ).strip()

        if not document:
            continue

        metadata = result.get(
            "metadata",
            {},
        )

        title = (
            metadata.get("title")
            or "Fonte sem título"
        )

        url = (
            metadata.get("url")
            or ""
        )

        source = (
            metadata.get("source")
            or "desconhecida"
        )

        header = (
            f"[TRECHO {index}]\n"
            f"Título: {title}\n"
            f"Fonte: {source}\n"
        )

        if url:
            header += f"URL: {url}\n"

        header += "Conteúdo:\n"

        separator = "\n\n"

        remaining = (
            max_chars
            - current_size
            - len(header)
            - len(separator)
        )

        if remaining <= 0:
            break

        if len(document) > remaining:
            document = document[:remaining].rstrip()

        block = (
            f"{header}"
            f"{document}"
        )

        context_parts.append(block)

        current_size += (
            len(block)
            + len(separator)
        )

        source_key = (
            title,
            url,
        )

        if source_key not in seen_sources:
            seen_sources.add(
                source_key
            )

            sources.append(
                {
                    "title": title,
                    "url": url,
                    "source": source,
                }
            )

        if current_size >= max_chars:
            break

    context = "\n\n".join(
        context_parts
    )

    return context, sources