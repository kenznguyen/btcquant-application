import tempfile
import unittest
from pathlib import Path

from persistent_state.contracts import SessionRecord, SessionStatus
from persistent_state.repository import SQLiteStateRepository, SessionTransitionError


class ReadyRepositoryBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repository = SQLiteStateRepository(
            Path(self.temp.name) / "repository.sqlite3"
        )
        self.repository.initialize()
        session = SessionRecord(
            session_id="session-ready-gate",
            account_scope_id="paper-account",
            status=SessionStatus.START_REQUESTED,
            started_at_ms=1_800_000_000_000,
            initiator="MANUAL",
            source_snapshot_id="snapshot-1",
            config_hash="sha256:" + "a" * 64,
            code_version="git:" + "b" * 40,
            last_committed_event_sequence=0,
        )
        self.token = self.repository.claim_writer(session)
        self.repository.advance_session(
            self.token,
            expected_status=SessionStatus.START_REQUESTED,
            new_status=SessionStatus.PREFLIGHT,
            at_ms=1_800_000_000_001,
        )
        self.repository.advance_session(
            self.token,
            expected_status=SessionStatus.PREFLIGHT,
            new_status=SessionStatus.RESTORING,
            at_ms=1_800_000_000_002,
        )

    def test_repository_rejects_direct_ready_transition_without_attestations(self):
        with self.assertRaises(SessionTransitionError):
            self.repository.advance_session(
                self.token,
                expected_status=SessionStatus.RESTORING,
                new_status=SessionStatus.READY,
                at_ms=1_800_000_000_003,
            )
        self.assertEqual(
            self.repository.get_session("session-ready-gate").status,
            SessionStatus.RESTORING,
        )


if __name__ == "__main__":
    unittest.main()
