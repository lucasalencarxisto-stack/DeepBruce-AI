import pytest

from DeepBruce_AI.services.conversation import (
    ConversationManager,
)


def manager():
    return ConversationManager(
        max_clarification_attempts=2
    )


def test_creates_conversation_state():
    conversations = manager()

    state = conversations.get_or_create(
        "conversation-1"
    )

    assert (
        state.conversation_id
        == "conversation-1"
    )

    assert (
        state.clarification_attempts
        == 0
    )

    assert (
        state.pending_clarification
        is False
    )


def test_returns_existing_state():
    conversations = manager()

    first = conversations.get_or_create(
        "conversation-1"
    )

    second = conversations.get_or_create(
        "conversation-1"
    )

    assert first is second


def test_registers_message_and_route():
    conversations = manager()

    state = conversations.register_message(
        "conversation-1",
        "Quem é o pai Lula?",
        "ambiguous",
    )

    assert (
        state.last_message
        == "Quem é o pai Lula?"
    )

    assert (
        state.last_route
        == "ambiguous"
    )


def test_registers_clarification_attempt():
    conversations = manager()

    state = (
        conversations
        .register_clarification(
            "conversation-1"
        )
    )

    assert (
        state.clarification_attempts
        == 1
    )

    assert (
        state.pending_clarification
        is True
    )


def test_allows_clarification_before_limit():
    conversations = manager()

    conversations.register_clarification(
        "conversation-1"
    )

    assert (
        conversations
        .can_request_clarification(
            "conversation-1"
        )
        is True
    )


def test_blocks_clarification_after_limit():
    conversations = manager()

    conversations.register_clarification(
        "conversation-1"
    )

    conversations.register_clarification(
        "conversation-1"
    )

    assert (
        conversations
        .can_request_clarification(
            "conversation-1"
        )
        is False
    )

    assert (
        conversations.should_fallback(
            "conversation-1"
        )
        is True
    )


def test_resolve_clarification_resets_attempts():
    conversations = manager()

    conversations.register_clarification(
        "conversation-1"
    )

    state = (
        conversations
        .resolve_clarification(
            "conversation-1"
        )
    )

    assert (
        state.clarification_attempts
        == 0
    )

    assert (
        state.pending_clarification
        is False
    )


def test_reset_removes_conversation():
    conversations = manager()

    original = conversations.get_or_create(
        "conversation-1"
    )

    conversations.reset(
        "conversation-1"
    )

    recreated = conversations.get_or_create(
        "conversation-1"
    )

    assert recreated is not original


def test_rejects_empty_conversation_id():
    conversations = manager()

    with pytest.raises(ValueError):
        conversations.get_or_create("")