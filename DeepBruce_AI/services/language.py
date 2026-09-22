import re
import unicodedata


SUPPORTED_LANGUAGES = {
    "pt",
    "en",
    "es",
}


def _normalize(
    text: str,
) -> str:
    text = unicodedata.normalize(
        "NFKD",
        text or "",
    )

    text = "".join(
        char
        for char in text
        if not unicodedata.combining(char)
    )

    return text.lower().strip()


def detect_language(
    text: str,
) -> str:
    """
    Detector leve para os idiomas oficialmente
    suportados pelo DeepBruce v1.5:

    pt -> Português
    en -> English
    es -> Español
    """

    raw = (
        text or ""
    ).lower()

    if not raw.strip():
        return "pt"

    # Sinais praticamente exclusivos.
    if (
        "¿" in raw
        or "¡" in raw
        or "ñ" in raw
    ):
        return "es"

    if any(
        char in raw
        for char in (
            "ã",
            "õ",
            "ç",
        )
    ):
        return "pt"

    normalized = _normalize(
        raw
    )

    tokens = set(
        re.findall(
            r"\b[a-z]+\b",
            normalized,
        )
    )

    markers = {
        "pt": {
            "oi",
            "ola",
            "quem",
            "quando",
            "onde",
            "voce",
            "meu",
            "minha",
            "nao",
            "faco",
            "fazer",
            "entende",
            "programacao",
            "isso",
            "um",
        },
        "en": {
            "hello",
            "hi",
            "hey",
            "who",
            "what",
            "when",
            "where",
            "why",
            "how",
            "you",
            "your",
            "does",
            "do",
            "can",
            "the",
            "programming",
            "explain",
            "write",
        },
        "es": {
            "hola",
            "quien",
            "cuando",
            "donde",
            "usted",
            "puedes",
            "puede",
            "hago",
            "hacer",
            "programacion",
            "esto",
            "una",
            "un",
            "es",
        },
    }

    scores = {
        lang: len(
            tokens & words
        )
        for lang, words
        in markers.items()
    }

    best = max(
        scores,
        key=scores.get,
    )

    if scores[best] == 0:
        return "pt"

    return best