import re
import unicodedata

from dataclasses import dataclass, field
from difflib import SequenceMatcher
from enum import Enum
from typing import List, Optional, Sequence


class EntityStatus(str, Enum):
    RESOLVED = "resolved"
    AMBIGUOUS = "ambiguous"
    NOT_FOUND = "not_found"


@dataclass(frozen=True)
class EntityCandidate:
    title: str
    url: Optional[str] = None
    score: float = 0.0


@dataclass(frozen=True)
class EntityResolutionResult:
    status: EntityStatus
    query: str
    entity_text: str
    confidence: float = 0.0
    resolved_title: Optional[str] = None
    candidates: List[EntityCandidate] = field(
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

    text = text.lower().strip()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


def _extract_entity_text(
    message: str,
) -> str:
    """
    Remove estruturas comuns de perguntas
    para tentar isolar a entidade pesquisada.

    Exemplo:
        "Quem é o Justin?"
        -> "justin"
    """

    normalized = _normalize(
        message
    ).strip(" ?!.,;:")

    patterns = [
        # Português
        r"^quem (?:e|foi|era) (?:o |a )?(.+)$",
        r"^o que (?:e|foi|era) (?:o |a )?(.+)$",

        # English
        r"^who (?:is|was) (?:the )?(.+)$",
        r"^what (?:is|was) (?:the )?(.+)$",

        # Español
        r"^quien (?:es|fue|era) (?:el |la )?(.+)$",
        r"^que (?:es|fue|era) (?:el |la )?(.+)$",
    ]

    for pattern in patterns:
        match = re.match(
            pattern,
            normalized,
        )

        if match:
            return (
                match.group(1)
                .strip(" ?!.,;:")
            )

    return normalized

def extract_entity_text(
        message: str,
 ) -> str:
    """
    Interface pública para extrair de pergunta
    o termo que representa a entidade principal.

    Exemplo:
      "Quem é o Justin?"
      -> "Justin"
    """

    return _extract_entity_text(
        message
    )

def should_resolve_entity(
    message: str,
) -> bool:
    """
    Decide se a pesquisa parece ser uma busca
    direta por uma entidade.

    Perguntas genéricas continuam indo direto
    para o RAG.
    """

    text = _normalize(
        message
    ).strip(" ?!.,;:")

    patterns = (
        # Português
        r"^quem (?:e|foi|era)\b",
        r"^o que (?:e|foi|era)\b",

        # English
        r"^who (?:is|was)\b",
        r"^what (?:is|was)\b",

        # Español
        r"^quien (?:es|fue|era)\b",
        r"^que (?:es|fue|era)\b",
    )

    return any(
        re.search(
            pattern,
            text,
        )
        for pattern in patterns
    )

def _similarity(
    query: str,
    title: str,
) -> float:
    query = _normalize(query)
    title = _normalize(title)

    if not query or not title:
        return 0.0

    if query == title:
        return 1.0

    return SequenceMatcher(
        None,
        query,
        title,
    ).ratio()


def resolve_entity(
    message: str,
    candidates: Sequence[EntityCandidate],
) -> EntityResolutionResult:
    """
    Decide se uma entidade pode ser resolvida
    automaticamente ou se precisa de
    esclarecimento.
    """

    entity_text = _extract_entity_text(
        message
    )

    if not entity_text:
        return EntityResolutionResult(
            status=EntityStatus.NOT_FOUND,
            query=message,
            entity_text="",
        )

    scored_candidates = [
        EntityCandidate(
            title=candidate.title,
            url=candidate.url,
            score=_similarity(
                entity_text,
                candidate.title,
            ),
        )
        for candidate in candidates
        if candidate.title
    ]

    scored_candidates.sort(
        key=lambda candidate: (
            candidate.score
        ),
        reverse=True,
    )

    if not scored_candidates:
        return EntityResolutionResult(
            status=EntityStatus.NOT_FOUND,
            query=message,
            entity_text=entity_text,
        )

    top = scored_candidates[0]

    second_score = (
        scored_candidates[1].score
        if len(scored_candidates) > 1
        else 0.0
    )

    margin = (
        top.score
        - second_score
    )

    entity_tokens = (
        entity_text.split()
    )

    # Uma entidade de apenas uma palavra
    # pode representar várias pessoas/temas.
    #
    # Exemplo:
    # Justin Bieber
    # Justin Timberlake
    # Justin Trudeau
    if len(entity_tokens) == 1:
        token = entity_tokens[0]

        matching = [
            candidate
            for candidate
            in scored_candidates
            if token
            in _normalize(
                candidate.title
            ).split()
        ]

        if len(matching) >= 2:
            return EntityResolutionResult(
                status=EntityStatus.AMBIGUOUS,
                query=message,
                entity_text=entity_text,
                confidence=top.score,
                candidates=matching[:5],
            )

    # Match forte com distância suficiente
    # para o segundo candidato.
    #
    # Isso permite tolerar erros como:
    # "Justem Biber" -> "Justin Bieber".
    if (
        top.score >= 0.78
        and margin >= 0.12
    ):
        return EntityResolutionResult(
            status=EntityStatus.RESOLVED,
            query=message,
            entity_text=entity_text,
            confidence=top.score,
            resolved_title=top.title,
            candidates=scored_candidates[:5],
        )

    # Vários candidatos razoavelmente
    # semelhantes significam ambiguidade.
    plausible = [
        candidate
        for candidate
        in scored_candidates
        if candidate.score >= 0.50
    ]

    if len(plausible) >= 2:
        return EntityResolutionResult(
            status=EntityStatus.AMBIGUOUS,
            query=message,
            entity_text=entity_text,
            confidence=top.score,
            candidates=plausible[:5],
        )

    # Um único candidato razoavelmente forte
    # ainda pode ser resolvido.
    if top.score >= 0.72:
        return EntityResolutionResult(
            status=EntityStatus.RESOLVED,
            query=message,
            entity_text=entity_text,
            confidence=top.score,
            resolved_title=top.title,
            candidates=scored_candidates[:5],
        )

    return EntityResolutionResult(
        status=EntityStatus.NOT_FOUND,
        query=message,
        entity_text=entity_text,
        confidence=top.score,
        candidates=scored_candidates[:5],
    )