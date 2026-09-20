import re
import unicodedata
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class ClarificationOption:
    label: str
    query: str


@dataclass(frozen=True)
class ClarificationResult:
    message: str
    keywords: List[str] = field(
        default_factory=list
    )
    options: List[ClarificationOption] = field(
        default_factory=list
    )


def _normalize(text: str) -> str:
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


def _extract_keywords(
    message: str,
) -> List[str]:
    """
    Extração simples de palavras relevantes.

    Nesta fase não usamos NLP pesado.
    O objetivo é fornecer pistas para
    o fluxo de esclarecimento.
    """

    stopwords = {
        "o",
        "a",
        "os",
        "as",
        "um",
        "uma",
        "de",
        "do",
        "da",
        "dos",
        "das",
        "e",
        "é",
        "foi",
        "quem",
        "que",
        "qual",
    }

    words = re.findall(
        r"\b[\wÀ-ÿ]+\b",
        message,
    )

    return [
        word
        for word in words
        if (
            len(word) > 1
            and word.lower()
            not in stopwords
        )
    ]


def build_clarification(
    message: str,
) -> ClarificationResult:
    """
    Produz uma pergunta de esclarecimento
    sem chamar Ollama ou Wikipedia.
    """

    original = (
        message or ""
    ).strip()

    normalized = _normalize(
        original
    )

    keywords = _extract_keywords(
        original
    )

    relationship_match = re.match(
        r"^quem (?:e|foi) o "
        r"(pai|mae) "
        r"(.+?)\??$",
        normalized,
    )

    if relationship_match:
        relationship = (
            relationship_match.group(1)
        )

        entity = (
            relationship_match.group(2)
            .strip()
        )

        relationship_label = {
            "pai": "pai",
            "mae": "mãe",
        }[relationship]

        return ClarificationResult(
            message=(
                "Sua pergunta pode ter "
                "mais de um significado. "
                "Qual destas opções representa "
                "melhor o que você quer saber?"
            ),
            keywords=keywords,
            options=[
                ClarificationOption(
                    label=(
                        f"Quem foi o "
                        f"{relationship_label} "
                        f"de {entity}?"
                    ),
                    query=(
                        f"Quem foi o "
                        f"{relationship_label} "
                        f"de {entity}?"
                    ),
                ),
                ClarificationOption(
                    label=(
                        f"Quem é {entity}?"
                    ),
                    query=(
                        f"Quem é {entity}?"
                    ),
                ),
            ],
        )

    return ClarificationResult(
        message=(
            "Não consegui identificar com "
            "segurança o que você quis dizer. "
            "Pode reformular a pergunta usando "
            "termos mais específicos?"
        ),
        keywords=keywords,
        options=[],
    )