import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from persistent_state.contracts import SessionRecord, SessionStatus, canonical_json
from persistent_state.evidence import (
    EvidenceBinding, PreflightAttestation, RestoreAttestation,
    RiskReadinessAttestation,
)
from persistent_state.orchestrator import (
    OperatorApproval, SessionOrchestrator,
)
from persistent_state.recovery import RecoveryValidationError
from persistent_state.repository import SQLiteStateRepository


CONFIG = "sha256:" + "a" * 64
CHECKSUM = "sha256:" + "b" * 64
START = 1_800_000_000_000


def reducer(state, event):
    state.setdefault("aggregates", {})[event.aggregate_id] = {
        "aggregateVersion": event.aggregate_version,
        "state": {},
    }
    return state


class SessionOrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repository = SQLiteStateRepository(
            Path(self.temp.name) / "orchestrator.sqlite3"
        )
        self.repository.initialize()
        self.now = [START + 10]
        self.preflight_calls = 0
        self.restore_calls = 0
        self.risk_calls = 0
        self.orchestrator = SessionOrchestrator(
            self.repository,
            reducer=reducer,
            preflight_provider=self.preflight_provider,
            restore_attestation_provider=self.restore_provider,
            risk_readiness_provider=self.risk_provider,
            clock_ms=lambda: self.now[0],
            operator_approval_verifier=lambda approval: approval.operator_id == "operator-1",
        )

    def session(self, session_id="session-orchestrator"):
        return SessionRecord(
            session_id=session_id, account_scope_id="paper-account",
            status=SessionStatus.START_REQUESTED, started_at_ms=START,
            initiator="MANUAL", source_snapshot_id="snapshot-1",
            config_hash=CONFIG, code_version="git:" + "c" * 40,
            last_committed_event_sequence=0,
        )

    def binding(self, session, token, checked_at=None):
        return EvidenceBinding(
            session_id=session.session_id,
            account_scope_id=session.account_scope_id,
            fencing_generation=token.fencing_generation,
            config_hash=session.config_hash,
            source_snapshot_id=session.source_snapshot_id,
            checked_at_ms=self.now[0] if checked_at is None else checked_at,
        )

    def preflight_provider(self, session, token):
        self.preflight_calls += 1
        return PreflightAttestation(
            binding=self.binding(session, token),
            market_data_snapshot_id=session.source_snapshot_id,
            data_as_of_ms=self.now[0] - 1,
            coverage_json='{"15m":200,"1h":100}',
            provenance="test-only.synthetic",
            schema_version=1, passed=True,
        )

    def restore_provider(self, session, token, recovery):
        self.restore_calls += 1
        return RestoreAttestation(
            binding=self.binding(session, token),
            checkpoint_id=recovery.checkpoint_id or "empty-history",
            checkpoint_checksum=CHECKSUM,
            last_event_sequence=recovery.last_event_sequence,
            aggregate_versions_json=recovery.aggregate_versions_json,
            core_ledger_reconciled=True, ai_ledger_reconciled=True,
            passed=True,
        )

    def risk_provider(self, session, token):
        self.risk_calls += 1
        return RiskReadinessAttestation(
            binding=self.binding(session, token),
            risk_policy_version="test-risk-v1",
            kill_switch_latched=False,
            account_equity_quote="10000",
            ledger_reconciled=True, passed=True,
        )

    def test_start_restores_and_stops_at_ready_without_starting_execution(self):
        result = self.orchestrator.start(self.session())
        self.assertEqual(result.session.status, SessionStatus.READY)
        self.assertEqual(result.recovery.last_event_sequence, 0)
        self.assertEqual(self.preflight_calls, 1)
        self.assertEqual(self.restore_calls, 1)
        self.assertEqual(self.repository.get_session(result.session.session_id).status, SessionStatus.READY)
        self.assertEqual(
            self.repository.read_ready_evidence(result.session.session_id).risk.risk_policy_version,
            "test-risk-v1",
        )

    def test_resume_requires_operator_approval_and_a_fresh_risk_check(self):
        result = self.orchestrator.start(self.session())
        with self.assertRaises(ValueError):
            self.orchestrator.resume(result.fencing_token, None)
        self.now[0] = START + 20
        fresh_risk = self.orchestrator.prepare_resume(result.fencing_token)
        running = self.orchestrator.resume(
            result.fencing_token,
            OperatorApproval(
                operator_id="operator-1",
                confirmation_id="manual-resume-1",
                confirmed_at_ms=self.now[0],
                risk_attestation=fresh_risk,
            ),
        )
        self.assertEqual(running.status, SessionStatus.RUNNING)
        actions = self.repository.read_resume_confirmations(running.session_id)
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].operator_id, "operator-1")


    def test_resume_rejects_unverified_operator_identity(self):
        result = self.orchestrator.start(self.session("operator-auth"))
        fresh_risk = self.orchestrator.prepare_resume(result.fencing_token)
        with self.assertRaises(PermissionError):
            self.orchestrator.resume(
                result.fencing_token,
                OperatorApproval(
                    operator_id="unverified-user",
                    confirmation_id="unverified-resume",
                    confirmed_at_ms=self.now[0],
                    risk_attestation=fresh_risk,
                ),
            )
        self.assertEqual(
            self.repository.get_session("operator-auth").status,
            SessionStatus.READY,
        )

    def test_failed_preflight_blocks_before_restore(self):
        self.orchestrator.preflight_provider = lambda session, token: PreflightAttestation(
            binding=self.binding(session, token),
            market_data_snapshot_id=session.source_snapshot_id,
            data_as_of_ms=self.now[0] - 1,
            coverage_json='{"15m":200,"1h":100}',
            provenance="test-only.synthetic", schema_version=1,
            passed=False, reason_codes=("STALE_DATA",),
        )
        result = self.orchestrator.start(self.session("blocked-preflight"))
        self.assertEqual(result.session.status, SessionStatus.BLOCKED_PREFLIGHT)
        self.assertEqual(self.restore_calls, 0)

    def test_recovery_failure_blocks_restore_and_never_reaches_ready(self):
        with patch(
            "persistent_state.orchestrator.recover_repository_state",
            side_effect=RecoveryValidationError("fixture corruption"),
        ):
            result = self.orchestrator.start(self.session("blocked-restore"))
        self.assertEqual(result.session.status, SessionStatus.BLOCKED_RESTORE)
        self.assertIsNone(result.recovery)
        self.assertEqual(self.repository.get_session("blocked-restore").status, SessionStatus.BLOCKED_RESTORE)


if __name__ == "__main__":
    unittest.main()
