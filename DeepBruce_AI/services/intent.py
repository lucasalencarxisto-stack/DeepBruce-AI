import re
import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class Intent(str, Enum):
    CHAT = "chat"
    RESEARCH = "research"
    AMBIGUOUS = "ambiguous"


@dataclass(frozen=True)
class IntentResult:
    intent: Intent
    confidence: float
    reason: str = ""


class IntentClassifier(Protocol):
    """
    Contrato para qualquer classificador de intenção.

    Hoje:
        RuleBasedIntentClassifier

    Futuramente:
        modelo treinado pelo DeepBruce.
    """

    def classify(
        self,
        message: str,
    ) -> IntentResult:
        ...


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

    return re.sub(
        r"\s+",
        " ",
        text,
    )


class RuleBasedIntentClassifier:
    """
    Classificador provisório da v1.5.

    Serve para validar a arquitetura antes de
    substituirmos as regras por um modelo treinado.
    """

    def classify(
        self,
        message: str,
    ) -> IntentResult:
        text = _normalize(message)

        if not text:
            return IntentResult(
                intent=Intent.AMBIGUOUS,
                confidence=0.0,
                reason="empty_message",
            )

        # Conversa social tem prioridade sobre
        # palavras interrogativas isoladas.
        casual_patterns = (
            r"^(oi|ola|opa|salve|e ai)\b",
            r"^tudo (bem|bom)\??$",
            r"^como voce (esta|ta|vai)\??$",
            r"^quem e voce\??$",
            r"^me chamo\b",
            r"^meu nome e\b",
            r"^eu me chamo\b",
            r"^voce gosta\b",
        )

        if self._matches_any(
            text,
            casual_patterns,
        ):
            return IntentResult(
                intent=Intent.CHAT,
                confidence=0.95,
                reason="casual_conversation",
            )

        # Exemplo:
        #
        # "Quem é o pai Lula?"
        #
        # pode significar:
        # - quem é o pai DE Lula?
        # - quem é "Pai Lula"?
        #
        # Sem preposição relacional, não escolhemos
        # uma interpretação automaticamente.
        ambiguous_relationship_patterns = (
            r"^quem e o pai (?!do\b|da\b|de\b)",
            r"^quem foi o pai (?!do\b|da\b|de\b)",
            r"^quem e a mae (?!do\b|da\b|de\b)",
            r"^quem foi a mae (?!do\b|da\b|de\b)",
        )

        if self._matches_any(
            text,
            ambiguous_relationship_patterns,
        ):
            return IntentResult(
                intent=Intent.AMBIGUOUS,
                confidence=0.55,
                reason="ambiguous_relationship",
            )

        research_patterns = (
            r"^quem (e|foi|era)\b",
            r"^o que (e|foi|era)\b",
            r"^quando\b",
            r"^onde\b",
            r"^por que\b",
            r"^porque\b",
            r"^qual\b",
            r"^quais\b",
            r"^como funciona\b",
            r"^como surgiu\b",
            r"^como aconteceu\b",
            r"^como comecou\b",
            r"^explique\b",
        )

        if self._matches_any(
            text,
            research_patterns,
        ):
            return IntentResult(
                intent=Intent.RESEARCH,
                confidence=0.90,
                reason="knowledge_request",
            )

        # Nesta primeira versão é melhor uma mensagem
        # desconhecida cair no Chat Core do que mandar
        # qualquer frase para a Wikipedia.
        return IntentResult(
            intent=Intent.CHAT,
            confidence=0.60,
            reason="default_chat",
        )

    @staticmethod
    def _matches_any(
        text: str,
        patterns: tuple[str, ...],
    ) -> bool:
        return any(
            re.search(pattern, text)
            for pattern in patterns
        )