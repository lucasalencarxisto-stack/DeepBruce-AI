from dataclasses import dataclass

from DeepBruce_AI.services.intent import (
    Intent,
    IntentClassifier,
    IntentResult,
    RuleBasedIntentClassifier,
)


@dataclass(frozen=True)
class RouteDecision:
    """
    Decisão produzida pelo Message Router.

    route:
        chat
        research
        ambiguous

    confidence:
        confiança do classificador.

    reason:
        motivo técnico da classificação.
    """

    route: str
    confidence: float
    reason: str


class MessageRouter:
    """
    Decide para qual núcleo do DeepBruce
    uma mensagem deve ser encaminhada.

    O router não conhece Ollama, Wikipedia
    ou Flask.

    Ele apenas classifica e retorna
    uma decisão de roteamento.
    """

    def __init__(
        self,
        classifier: IntentClassifier | None = None,
    ):
        self.classifier = (
            classifier
            or RuleBasedIntentClassifier()
        )

    def route(
        self,
        message: str,
    ) -> RouteDecision:
        result: IntentResult = (
            self.classifier.classify(
                message
            )
        )

        if result.intent == Intent.CHAT:
            return RouteDecision(
                route="chat",
                confidence=result.confidence,
                reason=result.reason,
            )

        if result.intent == Intent.RESEARCH:
            return RouteDecision(
                route="research",
                confidence=result.confidence,
                reason=result.reason,
            )

        return RouteDecision(
            route="ambiguous",
            confidence=result.confidence,
            reason=result.reason,
        )