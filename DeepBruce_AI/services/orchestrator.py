from typing import Any, Dict, Iterator

from DeepBruce_AI.config import Settings
from DeepBruce_AI.services import ollama
from DeepBruce_AI.services.clarifier import (
    build_clarification,
)
from DeepBruce_AI.services.conversation import (
    ConversationManager,
)
from DeepBruce_AI.services.entity_resolution import (
    EntityCandidate,
    EntityResolutionResult,
    EntityStatus,
    extract_entity_text,
    resolve_entity,
    should_resolve_entity,
)
from DeepBruce_AI.services.rag import (
    stream_rag_answer,
)
from DeepBruce_AI.services.router import (
    MessageRouter,
    RouteDecision,
)
from DeepBruce_AI.services.wiki import (
    search_wikipedia,
)

from DeepBruce_AI.services.language import (
    detect_language,
)

class DeepBruceOrchestrator:
    """
    Coordena os diferentes núcleos do DeepBruce.

    Fluxos disponíveis:

    chat
        -> Ollama Core

    research
        -> Entity Resolver
        -> Wikipedia RAG Core

    ambiguous
        -> Clarification Flow

    O orchestrator não conhece Flask, HTTP ou SSE.
    Ele produz eventos internos consumidos pela
    camada de rota.
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

        language = detect_language(
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

        # Se havia esclarecimento pendente e
        # agora conseguimos uma rota normal,
        # consideramos a ambiguidade resolvida.
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
                language,
            )
            return

        if decision.route == "research":
            yield from self._stream_research(
                message,
                settings,
                conversation_id,
                language,
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
        language: str,
    ) -> Iterator[Dict[str, Any]]:
        """
        Núcleo de conversa simples.

        Não utiliza Wikipedia nem RAG.
        """

        for token in ollama.stream_chat(
            message,
            settings,
            lang=language,
        ):
            yield {
                "type": "token",
                "content": token,
            }

    def _stream_research(
        self,
        message: str,
        settings: Settings,
        conversation_id: str,
        language: str,
    ) -> Iterator[Dict[str, Any]]:
        """
        Núcleo de pesquisa.

        Consultas diretas por entidades passam
        primeiro pelo Entity Resolver.

        Pesquisas gerais seguem diretamente
        para o pipeline RAG.
        """

        if not should_resolve_entity(
            message
        ):
            yield from stream_rag_answer(
                message,
                settings,
                lang=language,
            )

            return

        entity_text = extract_entity_text(
            message
        )

        search_results = search_wikipedia(
            entity_text,
            lang=language,
            limit=5,
        )

        candidates = [
            EntityCandidate(
                title=result["title"],
                url=result.get("url"),
            )
            for result in search_results
            if result.get("title")
        ]

        resolution = resolve_entity(
            message,
            candidates,
        )

        if (
            resolution.status
            == EntityStatus.RESOLVED
            and resolution.resolved_title
        ):
            yield from stream_rag_answer(
                message,
                settings,
                resolved_title=(
                    resolution.resolved_title
                ),
                lang=language,
            )
            return

        if (
            resolution.status
            == EntityStatus.AMBIGUOUS
        ):
            yield from self._handle_entity_ambiguity(
                message,
                resolution,
                conversation_id,
            )
            return

        yield {
            "type": "fallback",
            "code": "entity_not_found",
            "message": (
                "Não encontrei uma entidade "
                "suficientemente clara na Wikipédia "
                "para pesquisar com segurança. "
                "Tente informar o nome completo "
                "ou adicionar mais contexto."
            ),
        }

    def _handle_entity_ambiguity(
        self,
        message: str,
        resolution: EntityResolutionResult,
        conversation_id: str,
    ) -> Iterator[Dict[str, Any]]:
        """
        Solicita esclarecimento quando a intenção
        é clara, mas existem múltiplas entidades
        plausíveis.
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
                    "Ainda não consegui identificar "
                    "qual entidade você deseja pesquisar. "
                    "Tente informar o nome completo "
                    "ou adicionar mais contexto."
                ),
            }

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

        options = [
            {
                "label": candidate.title,
                "query": (
                    f"Quem é {candidate.title}?"
                ),
            }
            for candidate
            in resolution.candidates[:5]
        ]

        display_entity = (
            resolution.entity_text[:1].upper()
            + resolution.entity_text[1:]
        )

        if options:
            clarification_message = (
                f"Você se refere a qual "
                f"{display_entity}?"
            )
        else:
            clarification_message = (
                f"Você pode informar o nome completo "
                f"de quem você quer dizer com "
                f"'{display_entity}'?"
            )

        yield {
            "type": "clarification",
            "message": clarification_message,
            "original_message": message,
            "confidence": resolution.confidence,
            "attempt": (
                state.clarification_attempts
            ),
            "keywords": (
                [resolution.entity_text]
                if resolution.entity_text
                else []
            ),
            "options": options,
        }

    def _handle_ambiguous(
        self,
        message: str,
        decision: RouteDecision,
        conversation_id: str,
    ) -> Iterator[Dict[str, Any]]:
        """
        Gerencia ambiguidades detectadas
        pelo Intent Router.
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