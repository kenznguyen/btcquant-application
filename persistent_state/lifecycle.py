"""Pure manual-session lifecycle transition rules."""
from __future__ import annotations

from persistent_state.contracts import SessionStatus


_ALLOWED_TRANSITIONS = {
    SessionStatus.START_REQUESTED: {
        SessionStatus.PREFLIGHT, SessionStatus.ABORTED, SessionStatus.FAILED_PERSISTENCE,
    },
    SessionStatus.PREFLIGHT: {
        SessionStatus.RESTORING, SessionStatus.BLOCKED_PREFLIGHT,
        SessionStatus.ABORTED, SessionStatus.FAILED_PERSISTENCE,
    },
    SessionStatus.RESTORING: {
        SessionStatus.READY, SessionStatus.BLOCKED_RESTORE,
        SessionStatus.ABORTED, SessionStatus.FAILED_PERSISTENCE,
    },
    SessionStatus.READY: {
        SessionStatus.RUNNING, SessionStatus.ABORTED, SessionStatus.FAILED_PERSISTENCE,
    },
    SessionStatus.RUNNING: {
        SessionStatus.CHECKPOINTING, SessionStatus.INTERRUPTED,
        SessionStatus.FAILED_PERSISTENCE,
    },
    SessionStatus.CHECKPOINTING: {
        SessionStatus.CLOSED, SessionStatus.INTERRUPTED,
        SessionStatus.FAILED_PERSISTENCE,
    },
}

TERMINAL_SESSION_STATUSES = frozenset({
    SessionStatus.CLOSED,
    SessionStatus.BLOCKED_PREFLIGHT,
    SessionStatus.BLOCKED_RESTORE,
    SessionStatus.INTERRUPTED,
    SessionStatus.FAILED_PERSISTENCE,
    SessionStatus.ABORTED,
})


def validate_session_transition(current: SessionStatus, target: SessionStatus) -> None:
    if not isinstance(current, SessionStatus) or not isinstance(target, SessionStatus):
        raise ValueError("session transitions require SessionStatus values")
    if target not in _ALLOWED_TRANSITIONS.get(current, set()):
        raise ValueError(f"invalid session transition: {current.value} -> {target.value}")


def is_terminal_session_status(status: SessionStatus) -> bool:
    return status in TERMINAL_SESSION_STATUSES


__all__ = [
    "TERMINAL_SESSION_STATUSES", "is_terminal_session_status",
    "validate_session_transition",
]
