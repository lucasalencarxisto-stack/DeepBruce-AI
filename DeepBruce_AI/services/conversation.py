from dataclasses import dataclass
from threading import Lock
from typing import Dict, Optional


MAX_CLARIFICATION_ATTEMPTS = 2


@dataclass
class ConversationState:
    """
    Estado mínimo de uma conversa do DeepBruce.

    Nesta fase armazenamos apenas informações
    necessárias para o fluxo de roteamento e
    esclarecimento.
    """

    conversation_id: str

    clarification_attempts: int = 0
    pending_clarification: bool = False

    last_message: Optional[str] = None
    last_route: Optional[str] = None


class ConversationManager:
    """
    Gerencia estados de conversa em memória.

    Nesta versão não há persistência em banco.
    Se o servidor reiniciar, os estados são perdidos.

    Isso é aceitável para a arquitetura atual da v1.5.
    """

    def __init__(
        self,
        max_clarification_attempts: int = (
            MAX_CLARIFICATION_ATTEMPTS
        ),
    ):
        if max_clarification_attempts < 1:
            raise ValueError(
                "max_clarification_attempts "
                "deve ser maior que zero."
            )

        self.max_clarification_attempts = (
            max_clarification_attempts
        )

        self._states: Dict[
            str,
            ConversationState,
        ] = {}

        self._lock = Lock()

    def get_or_create(
        self,
        conversation_id: str,
    ) -> ConversationState:
        """
        Obtém uma conversa existente ou cria
        um novo estado.
        """

        conversation_id = (
            conversation_id or ""
        ).strip()

        if not conversation_id:
            raise ValueError(
                "conversation_id é obrigatório."
            )

        with self._lock:
            state = self._states.get(
                conversation_id
            )

            if state is None:
                state = ConversationState(
                    conversation_id=conversation_id
                )

                self._states[
                    conversation_id
                ] = state

            return state

    def register_message(
        self,
        conversation_id: str,
        message: str,
        route: str,
    ) -> ConversationState:
        """
        Registra a última mensagem e rota.
        """

        state = self.get_or_create(
            conversation_id
        )

        with self._lock:
            state.last_message = (
                message or ""
            ).strip()

            state.last_route = (
                route or ""
            ).strip()

        return state

    def register_clarification(
        self,
        conversation_id: str,
    ) -> ConversationState:
        """
        Registra que o DeepBruce pediu
        esclarecimento ao usuário.
        """

        state = self.get_or_create(
            conversation_id
        )

        with self._lock:
            state.clarification_attempts += 1
            state.pending_clarification = True

        return state

    def can_request_clarification(
        self,
        conversation_id: str,
    ) -> bool:
        """
        Retorna True enquanto ainda podemos
        pedir esclarecimento.
        """

        state = self.get_or_create(
            conversation_id
        )

        return (
            state.clarification_attempts
            < self.max_clarification_attempts
        )

    def should_fallback(
        self,
        conversation_id: str,
    ) -> bool:
        """
        Retorna True quando o limite de
        esclarecimentos foi atingido.
        """

        return not self.can_request_clarification(
            conversation_id
        )

    def resolve_clarification(
        self,
        conversation_id: str,
    ) -> ConversationState:
        """
        Marca a ambiguidade como resolvida.

        Também zera o contador, permitindo
        futuros fluxos de esclarecimento na
        mesma conversa.
        """

        state = self.get_or_create(
            conversation_id
        )

        with self._lock:
            state.clarification_attempts = 0
            state.pending_clarification = False

        return state

    def reset(
        self,
        conversation_id: str,
    ) -> None:
        """
        Remove completamente o estado de uma conversa.
        """

        conversation_id = (
            conversation_id or ""
        ).strip()

        if not conversation_id:
            return

        with self._lock:
            self._states.pop(
                conversation_id,
                None,
            )