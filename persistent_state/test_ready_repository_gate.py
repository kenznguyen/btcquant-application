import sqlite3
import tempfile
import unittest
from pathlib import Path

from persistent_state.contracts import SessionRecord, SessionStatus
from persistent_state.evidence import (
    EvidenceBinding, PreflightAttestation, RestoreAttestation,
    RiskReadinessAttestation, ReadyEvidenceBundle,
)
from persistent_state.test_support import resume_confirmation_for
from persistent_state.repository import (
    SQLiteStateRepository, SessionTransitionError, EvidenceIntegrityError,
)


class ReadyRepositoryBoundaryTests(unittest.TestCase):
    """Regression proof for the repository READY boundary and durable evidence."""

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
            self.token, expected_status=SessionStatus.START_REQUESTED,
            new_status=SessionStatus.PREFLIGHT, at_ms=1_800_000_000_001,
        )
        self.repository.advance_session(
            self.token, expected_status=SessionStatus.PREFLIGHT,
            new_status=SessionStatus.RESTORING, at_ms=1_800_000_000_002,
            preflight_attestation=self.ready_evidence().preflight,
        )

    def ready_evidence(self, *, generation=1):
        binding = EvidenceBinding(
            session_id="session-ready-gate", account_scope_id="paper-account",
            fencing_generation=generation, config_hash="sha256:" + "a" * 64,
            source_snapshot_id="snapshot-1", checked_at_ms=1_800_000_000_002,
        )
        return ReadyEvidenceBundle(
            preflight=PreflightAttestation(
                binding=binding, market_data_snapshot_id="snapshot-1",
                data_as_of_ms=1_800_000_000_000,
                coverage_json='{"15m":200,"1h":100}',
                provenance="test-fixture", schema_version=1, passed=True,
            ),
            restore=RestoreAttestation(
                binding=binding, checkpoint_id="checkpoint-test",
                checkpoint_checksum="sha256:" + "b" * 64,
                last_event_sequence=0, aggregate_versions_json="{}",
                core_ledger_reconciled=True, ai_ledger_reconciled=True,
                passed=True,
            ),
            risk=RiskReadinessAttestation(
                binding=binding, risk_policy_version="test-risk-v1",
                kill_switch_latched=False, account_equity_quote="10000",
                ledger_reconciled=True, passed=True,
            ),
        )

    def test_repository_rejects_direct_ready_transition_without_attestations(self):
        with self.assertRaises(SessionTransitionError):
            self.repository.advance_session(
                self.token, expected_status=SessionStatus.RESTORING,
                new_status=SessionStatus.READY, at_ms=1_800_000_000_003,
            )
        self.assertEqual(
            self.repository.get_session("session-ready-gate").status,
            SessionStatus.RESTORING,
        )

    def test_valid_attestations_are_committed_atomically_and_survive_reopen(self):
        ready = self.repository.advance_session(
            self.token, expected_status=SessionStatus.RESTORING,
            new_status=SessionStatus.READY, at_ms=1_800_000_000_011,
            readiness_evidence=self.ready_evidence(),
        )
        self.assertEqual(ready.status, SessionStatus.READY)
        reopened = SQLiteStateRepository(self.repository.database_path)
        self.assertEqual(
            reopened.read_ready_evidence("session-ready-gate"), self.ready_evidence()
        )

    def test_wrong_fencing_generation_does_not_persist_evidence_or_reach_ready(self):
        with self.assertRaises(SessionTransitionError):
            self.repository.advance_session(
                self.token, expected_status=SessionStatus.RESTORING,
                new_status=SessionStatus.READY, at_ms=1_800_000_000_011,
                readiness_evidence=self.ready_evidence(generation=2),
            )
        self.assertEqual(
            self.repository.get_session("session-ready-gate").status,
            SessionStatus.RESTORING,
        )
        with self.assertRaises(KeyError):
            self.repository.read_ready_evidence("session-ready-gate")


    def enter_ready(self):
        self.repository.advance_session(
            self.token, expected_status=SessionStatus.RESTORING,
            new_status=SessionStatus.READY, at_ms=1_800_000_000_011,
            readiness_evidence=self.ready_evidence(),
        )


    def test_v1_evidence_extension_requires_explicit_additive_migration(self):
        with sqlite3.connect(self.repository.database_path) as connection:
            for name in (
                "ps_session_attestations_no_update",
                "ps_session_attestations_no_delete",
                "ps_session_attestations",
                "ps_session_operator_actions_no_update",
                "ps_session_operator_actions_no_delete",
                "ps_session_operator_actions",
            ):
                connection.execute("DROP TRIGGER IF EXISTS " + name) if "no_" in name else connection.execute("DROP TABLE IF EXISTS " + name)
            self.assertEqual(connection.execute("PRAGMA user_version").fetchone()[0], 1)
        reopened = SQLiteStateRepository(self.repository.database_path)
        reopened.initialize()
        with sqlite3.connect(self.repository.database_path) as connection:
            names = {
                row[0] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'"
                )
            }
        self.assertNotIn("ps_session_attestations", names)
        reopened.migrate_v1_session_evidence()
        reopened.initialize()
        with sqlite3.connect(self.repository.database_path) as connection:
            self.assertEqual(connection.execute("PRAGMA user_version").fetchone()[0], 1)
            names = {
                row[0] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'"
                )
            }
        self.assertIn("ps_session_attestations", names)
        self.assertIn("ps_session_operator_actions", names)

    def test_repository_rejects_running_transition_without_operator_confirmation(self):
        self.enter_ready()
        with self.assertRaises(SessionTransitionError):
            self.repository.advance_session(
                self.token, expected_status=SessionStatus.READY,
                new_status=SessionStatus.RUNNING, at_ms=1_800_000_000_020,
            )
        self.assertEqual(
            self.repository.get_session("session-ready-gate").status,
            SessionStatus.READY,
        )

    def test_operator_resume_confirmation_and_fresh_risk_are_durably_audited(self):
        self.enter_ready()
        ready_session = self.repository.get_session("session-ready-gate")
        confirmation = resume_confirmation_for(
            ready_session, self.token, confirmed_at_ms=1_800_000_000_020,
        )
        running = self.repository.advance_session(
            self.token, expected_status=SessionStatus.READY,
            new_status=SessionStatus.RUNNING, at_ms=1_800_000_000_021,
            resume_confirmation=confirmation,
        )
        self.assertEqual(running.status, SessionStatus.RUNNING)
        reopened = SQLiteStateRepository(self.repository.database_path)
        self.assertEqual(
            reopened.read_resume_confirmations("session-ready-gate"),
            (confirmation,),
        )

    def test_persisted_attestation_checksum_is_verified_on_read(self):
        self.repository.advance_session(
            self.token, expected_status=SessionStatus.RESTORING,
            new_status=SessionStatus.READY, at_ms=1_800_000_000_011,
            readiness_evidence=self.ready_evidence(),
        )
        with sqlite3.connect(self.repository.database_path) as connection:
            connection.execute("DROP TRIGGER ps_session_attestations_no_update")
            connection.execute(
                "UPDATE ps_session_attestations SET payload_json=? "
                "WHERE session_id=? AND attestation_type='risk'",
                ('{"tampered":true}', "session-ready-gate"),
            )
        with self.assertRaises(EvidenceIntegrityError):
            self.repository.read_ready_evidence("session-ready-gate")


if __name__ == "__main__":
    unittest.main()
