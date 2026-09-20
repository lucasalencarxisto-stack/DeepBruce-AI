from typing import Any, Dict, Iterator

from DeepBruce_AI.config import Settings
from DeepBruce_AI.services import ollama
from DeepBruce_AI.services.clarifier import (
    build_clarification,
)
from DeepBruce_AI.services.conversation import (
    ConversationManager,
)
from DeepBruce_AI.services.rag import (
    stream_rag_answer,
)
from DeepBruce_AI.services.router import (
    MessageRouter,
    RouteDecision,
)


class DeepBruceOrchestrator:
    """
    Coordena os diferentes núcleos do DeepBruce.

    Fluxos disponíveis:

    chat
        -> Ollama Core

    research
        -> Wikipedia RAG Core

    ambiguous
        -> Clarification Flow

    O orchestrator não conhece Flask, HTTP ou SSE.
    Ele apenas produz eventos internos que podem ser
    convertidos pela camada de rota.
    """

    def __init__(
        self,
        router: MessageRouter | None = None,
        conversations: ConversationManager | None = None,
    ):
        self.router = (
            router
            or MessageRouter()
        )

        self.conversations = (
            conversations
            or ConversationManager()
        )

    def stream_message(
        self,
        message: str,
        settings: Settings,
        conversation_id: str,
    ) -> Iterator[Dict[str, Any]]:
        """
        Processa uma mensagem e encaminha
        para o núcleo adequado.
        """

        message = (
            message or ""
        ).strip()

        if not message:
            yield {
                "type": "error",
                "code": "empty_message",
                "message": (
                    "A mensagem não pode estar vazia."
                ),
            }
            return

        decision = self.router.route(
            message
        )

        state = (
            self.conversations
            .register_message(
                conversation_id,
                message,
                decision.route,
            )
        )

        yield {
            "type": "route",
            "route": decision.route,
            "confidence": decision.confidence,
            "reason": decision.reason,
            "conversation_id": conversation_id,
        }

        # Se havia uma ambiguidade pendente
        # e a nova mensagem conseguiu ser
        # classificada normalmente, consideramos
        # o esclarecimento resolvido.
        if (
            state.pending_clarification
            and decision.route != "ambiguous"
        ):
            self.conversations.resolve_clarification(
                conversation_id
            )

        if decision.route == "chat":
            yield from self._stream_chat(
                message,
                settings,
            )
            return

        if decision.route == "research":
            yield from self._stream_research(
                message,
                settings,
            )
            return

        if decision.route == "ambiguous":
            yield from self._handle_ambiguous(
                message,
                decision,
                conversation_id,
            )
            return

        yield {
            "type": "error",
            "code": "unknown_route",
            "message": (
                "Não foi possível determinar "
                "como processar a mensagem."
            ),
        }

    def _stream_chat(
        self,
        message: str,
        settings: Settings,
    ) -> Iterator[Dict[str, Any]]:
        """
        Núcleo de conversa simples.

        Não utiliza Wikipedia nem RAG.
        """

        for token in ollama.stream_chat(
            message,
            settings,
        ):
            yield {
                "type": "token",
                "content": token,
            }

    def _stream_research(
        self,
        message: str,
        settings: Settings,
    ) -> Iterator[Dict[str, Any]]:
        """
        Núcleo de pesquisa.

        Reutiliza o pipeline RAG existente.
        """

        yield from stream_rag_answer(
            message,
            settings,
        )

    def _handle_ambiguous(
        self,
        message: str,
        decision: RouteDecision,
        conversation_id: str,
    ) -> Iterator[Dict[str, Any]]:
        """
        Gerencia o fluxo ambíguo.

        Primeiro verifica se ainda podemos pedir
        esclarecimento. Caso o limite tenha sido
        atingido, retorna fallback seguro.
        """

        if self.conversations.should_fallback(
            conversation_id
        ):
            yield {
                "type": "fallback",
                "code": (
                    "clarification_limit_reached"
                ),
                "message": (
                    "Não consegui identificar com "
                    "segurança o que você está buscando. "
                    "Tente reformular usando nomes, datas "
                    "ou termos mais específicos. "
                    "Nesta versão, minhas pesquisas "
                    "utilizam apenas conteúdo da Wikipédia."
                ),
            }

            # Libera o estado para futuras perguntas.
            self.conversations.resolve_clarification(
                conversation_id
            )

            return

        state = (
            self.conversations
            .register_clarification(
                conversation_id
            )
        )

        yield from self._stream_clarification(
            message,
            decision,
            attempt=state.clarification_attempts,
        )

    def _stream_clarification(
        self,
        message: str,
        decision: RouteDecision,
        attempt: int,
    ) -> Iterator[Dict[str, Any]]:
        """
        Constrói uma resposta de esclarecimento
        para mensagens ambíguas.
        """

        clarification = build_clarification(
            message
        )

        yield {
            "type": "clarification",
            "message": clarification.message,
            "original_message": message,
            "confidence": decision.confidence,
            "attempt": attempt,
            "keywords": clarification.keywords,
            "options": [
                {
                    "label": option.label,
                    "query": option.query,
                }
                for option
                in clarification.options
            ],
        }