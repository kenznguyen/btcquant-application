import unittest

from persistent_state.contracts import SessionStatus
from persistent_state.lifecycle import (
    TERMINAL_SESSION_STATUSES, is_terminal_session_status,
    validate_session_transition,
)


ALLOWED = {
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


class CompleteSessionLifecycleMatrixTests(unittest.TestCase):
    def test_every_documented_transition_is_allowed(self):
        for current, targets in ALLOWED.items():
            for target in targets:
                with self.subTest(current=current, target=target):
                    validate_session_transition(current, target)

    def test_every_undocumented_transition_is_rejected(self):
        for current in SessionStatus:
            for target in SessionStatus:
                if target in ALLOWED.get(current, set()):
                    continue
                with self.subTest(current=current, target=target):
                    with self.assertRaises(ValueError):
                        validate_session_transition(current, target)

    def test_all_failure_and_terminal_states_are_terminal(self):
        expected = {
            SessionStatus.CLOSED, SessionStatus.BLOCKED_PREFLIGHT,
            SessionStatus.BLOCKED_RESTORE, SessionStatus.INTERRUPTED,
            SessionStatus.FAILED_PERSISTENCE, SessionStatus.ABORTED,
        }
        self.assertEqual(TERMINAL_SESSION_STATUSES, frozenset(expected))
        for status in SessionStatus:
            self.assertEqual(is_terminal_session_status(status), status in expected)

    def test_idle_is_not_a_persisted_or_executable_transition_state(self):
        with self.assertRaises(ValueError):
            validate_session_transition(SessionStatus.IDLE, SessionStatus.START_REQUESTED)


if __name__ == "__main__":
    unittest.main()
