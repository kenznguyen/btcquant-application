import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from persistent_state.contracts import (
    Checkpoint, EventRecord, IdempotencyClaim, SessionRecord, SessionStatus,
    StrategyId, canonical_json, derive_idempotency_key,
)
from persistent_state.test_support import ready_evidence_for, resume_confirmation_for
from persistent_state.repository import (
    AggregateMutation, CheckpointIntegrityError, CheckpointRequiredForCloseError,
    GracefulStopTimeoutError,
    SessionStateConflictError,
    SessionTransitionError, SQLiteStateRepository, StaleFencingTokenError,
)


def make_session(session_id, *, account="paper-account", started_at_ms=1_800_000_000_000):
    return SessionRecord(
        session_id=session_id, account_scope_id=account,
        status=SessionStatus.START_REQUESTED, started_at_ms=started_at_ms,
        initiator="MANUAL", source_snapshot_id="snapshot-1",
        config_hash="sha256:" + "a" * 64, code_version="git:" + "b" * 40,
        last_committed_event_sequence=0,
    )


def start_running(repository, session_id="session-1", *, account="paper-account", start=1_800_000_000_000):
    token = repository.claim_writer(make_session(session_id, account=account, started_at_ms=start))
    for expected, target in (
        (SessionStatus.START_REQUESTED, SessionStatus.PREFLIGHT),
        (SessionStatus.PREFLIGHT, SessionStatus.RESTORING),
        (SessionStatus.RESTORING, SessionStatus.READY),
        (SessionStatus.READY, SessionStatus.RUNNING),
    ):
        kwargs = {}
        if target is SessionStatus.RESTORING:
            kwargs["preflight_attestation"] = ready_evidence_for(
                repository.get_session(session_id), token,
            ).preflight
        if target is SessionStatus.READY:
            kwargs["readiness_evidence"] = ready_evidence_for(
                repository.get_session(session_id), token,
            )
        if target is SessionStatus.RUNNING:
            kwargs["resume_confirmation"] = resume_confirmation_for(
                repository.get_session(session_id), token, confirmed_at_ms=start + 1,
            )
        repository.advance_session(
            token, expected_status=expected, new_status=target,
            at_ms=start + 1, **kwargs,
        )
    return token


def commit_one(repository, token, *, sequence=1):
    payload = canonical_json({"position": "0.01"})
    snapshot = "snapshot-1"
    claim = IdempotencyClaim(
        idempotency_key=derive_idempotency_key(
            account_scope_id=token.account_scope_id, ledger_id="ledger-core",
            strategy_id=StrategyId.CORE, strategy_version="core-v1",
            market_snapshot_id=snapshot, candle_open_time_ms=1_800_000_000_000,
            action_kind="ENTRY", action_ordinal=sequence,
        ),
        payload_hash="sha256:" + hashlib.sha256(payload.encode()).hexdigest(),
        account_scope_id=token.account_scope_id, ledger_id="ledger-core",
        strategy_id=StrategyId.CORE, strategy_version="core-v1",
        market_snapshot_id=snapshot, candle_open_time_ms=1_800_000_000_000,
        action_kind="ENTRY", action_ordinal=sequence,
    )
    event = EventRecord(
        event_id=f"event-{sequence}", account_scope_id=token.account_scope_id,
        session_id=token.session_id, event_sequence=sequence,
        aggregate_version=sequence, event_type="POSITION_UPDATED",
        strategy_id=StrategyId.CORE, strategy_version="core-v1",
        created_at_ms=1_800_000_000_000, recorded_at_ms=1_800_000_000_001,
        payload_json=payload, market_snapshot_id=snapshot,
        candle_open_time_ms=1_800_000_000_000, aggregate_id="ledger-core",
    )
    mutation = AggregateMutation(
        account_scope_id=token.account_scope_id, aggregate_id="ledger-core",
        aggregate_type="POSITION_LEDGER", strategy_id=StrategyId.CORE,
        expected_version=sequence - 1, state_json=payload,
    )
    return repository.commit_transition(event, claim, mutation, fencing_token=token)


def checkpoint_for(token, sequence=1):
    payload = canonical_json({"ledger": {"position": "0.01"}})
    return Checkpoint(
        checkpoint_id=f"checkpoint-{token.session_id}-{sequence}",
        account_scope_id=token.account_scope_id, session_id=token.session_id,
        schema_version=1, covered_event_sequence=sequence,
        aggregate_versions_json=canonical_json({"ledger-core": sequence}),
        payload_json=payload,
        payload_checksum="sha256:" + hashlib.sha256(payload.encode()).hexdigest(),
        created_at_ms=1_800_000_100_001, source_snapshot_id="snapshot-1",
        strategy_versions_json=canonical_json({"CORE": "core-v1", "AI": "ai-v1"}),
        config_hash="sha256:" + "a" * 64,
    )


class SessionFencingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "session-fencing.sqlite3"
        self.repository = SQLiteStateRepository(self.path)
        self.repository.initialize()

    def test_manual_start_claims_first_fencing_generation(self):
        token = self.repository.claim_writer(make_session("session-1"))
        self.assertEqual(token.fencing_generation, 1)
        self.assertEqual(self.repository.get_writer_fence("paper-account"), token)
        self.assertEqual(self.repository.get_session("session-1").status, SessionStatus.START_REQUESTED)

    def test_new_manual_start_interrupts_previous_session_and_fences_old_token(self):
        old_token = start_running(self.repository, "old-session")
        new_token = self.repository.claim_writer(
            make_session("new-session", started_at_ms=1_800_000_010_000)
        )
        self.assertEqual(new_token.fencing_generation, old_token.fencing_generation + 1)
        old_session = self.repository.get_session("old-session")
        self.assertEqual(old_session.status, SessionStatus.INTERRUPTED)
        self.assertEqual(old_session.ended_at_ms, 1_800_000_010_000)
        self.assertEqual(self.repository.get_writer_fence("paper-account"), new_token)

    def test_stale_fencing_token_cannot_commit_after_new_owner_claim(self):
        old_token = start_running(self.repository, "old-session")
        self.repository.claim_writer(make_session("new-session", started_at_ms=1_800_000_010_000))
        with self.assertRaises(StaleFencingTokenError):
            commit_one(self.repository, old_token)

    def test_new_owner_cannot_commit_before_running(self):
        token = self.repository.claim_writer(make_session("new-session"))
        with self.assertRaises(SessionStateConflictError):
            commit_one(self.repository, token)


    def test_repository_rejects_restore_transition_without_durable_preflight_evidence(self):
        token = self.repository.claim_writer(make_session("missing-preflight"))
        self.repository.advance_session(
            token, expected_status=SessionStatus.START_REQUESTED,
            new_status=SessionStatus.PREFLIGHT, at_ms=1_800_000_000_001,
        )
        with self.assertRaises(SessionTransitionError):
            self.repository.advance_session(
                token, expected_status=SessionStatus.PREFLIGHT,
                new_status=SessionStatus.RESTORING, at_ms=1_800_000_000_002,
            )
        self.assertEqual(
            self.repository.get_session("missing-preflight").status,
            SessionStatus.PREFLIGHT,
        )

    def test_valid_state_machine_requires_preflight_restore_ready_running_order(self):
        token = self.repository.claim_writer(make_session("session-1"))
        with self.assertRaises(SessionTransitionError):
            self.repository.advance_session(
                token, expected_status=SessionStatus.START_REQUESTED,
                new_status=SessionStatus.RUNNING, at_ms=1_800_000_000_001,
            )
        self.assertEqual(self.repository.get_session("session-1").status, SessionStatus.START_REQUESTED)

    def test_crash_restart_preserves_event_tail_and_marks_old_session_interrupted(self):
        old_token = start_running(self.repository, "old-session")
        commit_one(self.repository, old_token)
        new_token = self.repository.claim_writer(
            make_session("recovery-session", started_at_ms=1_800_000_020_000)
        )
        old_session = self.repository.get_session("old-session")
        self.assertEqual(old_session.status, SessionStatus.INTERRUPTED)
        self.assertEqual(old_session.last_committed_event_sequence, 1)
        self.assertEqual(len(self.repository.read_events("paper-account")), 1)
        self.assertEqual(new_token.fencing_generation, 2)
        for expected, target in (
            (SessionStatus.START_REQUESTED, SessionStatus.PREFLIGHT),
            (SessionStatus.PREFLIGHT, SessionStatus.RESTORING),
            (SessionStatus.RESTORING, SessionStatus.READY),
            (SessionStatus.READY, SessionStatus.RUNNING),
        ):
            kwargs = {}
            if target is SessionStatus.RESTORING:
                kwargs["preflight_attestation"] = ready_evidence_for(
                    self.repository.get_session("recovery-session"), new_token,
                ).preflight
            if target is SessionStatus.READY:
                kwargs["readiness_evidence"] = ready_evidence_for(
                    self.repository.get_session("recovery-session"), new_token,
                )
            if target is SessionStatus.RUNNING:
                kwargs["resume_confirmation"] = resume_confirmation_for(
                    self.repository.get_session("recovery-session"), new_token,
                    confirmed_at_ms=1_800_000_020_001,
                )
            self.repository.advance_session(
                new_token, expected_status=expected, new_status=target,
                at_ms=1_800_000_020_001, **kwargs,
            )
        commit_one(self.repository, new_token, sequence=2)
        self.assertEqual(
            [event.event_sequence for event in self.repository.read_events("paper-account")],
            [1, 2],
        )
        self.assertEqual(
            self.repository.get_session("recovery-session").last_committed_event_sequence, 2,
        )

    def test_checkpoint_from_stale_session_is_rejected(self):
        old_token = start_running(self.repository, "old-session")
        commit_one(self.repository, old_token)
        self.repository.claim_writer(
            make_session("new-session", started_at_ms=1_800_000_030_000)
        )
        with self.assertRaises(StaleFencingTokenError):
            self.repository.publish_checkpoint(checkpoint_for(old_token), fencing_token=old_token)

    def test_clean_close_requires_verified_checkpoint_at_latest_event_boundary(self):
        token = start_running(self.repository)
        commit_one(self.repository, token)
        self.repository.advance_session(
            token, expected_status=SessionStatus.RUNNING,
            new_status=SessionStatus.CHECKPOINTING, at_ms=1_800_000_100_000,
        )
        with self.assertRaises(CheckpointRequiredForCloseError):
            self.repository.advance_session(
                token, expected_status=SessionStatus.CHECKPOINTING,
                new_status=SessionStatus.CLOSED, at_ms=1_800_000_100_001,
            )
        self.repository.publish_checkpoint(checkpoint_for(token), fencing_token=token)
        closed = self.repository.advance_session(
            token, expected_status=SessionStatus.CHECKPOINTING,
            new_status=SessionStatus.CLOSED, at_ms=1_800_000_130_000,
        )
        self.assertEqual(closed.status, SessionStatus.CLOSED)
        self.assertEqual(closed.ended_at_ms, 1_800_000_130_000)

    def test_stop_exceeding_30_second_grace_becomes_interrupted(self):
        token = start_running(self.repository)
        stop_requested_at = 1_800_000_100_000
        self.repository.advance_session(
            token, expected_status=SessionStatus.RUNNING,
            new_status=SessionStatus.CHECKPOINTING, at_ms=stop_requested_at,
        )
        result = self.repository.advance_session(
            token, expected_status=SessionStatus.CHECKPOINTING,
            new_status=SessionStatus.CLOSED, at_ms=stop_requested_at + 30_001,
        )
        self.assertEqual(result.status, SessionStatus.INTERRUPTED)
        self.assertEqual(result.ended_at_ms, stop_requested_at + 30_001)
        self.assertEqual(result.stop_requested_at_ms, stop_requested_at)

    def test_late_checkpoint_is_rejected_after_stop_grace_expires(self):
        token = start_running(self.repository)
        commit_one(self.repository, token)
        stop_requested_at = 1_800_000_100_000
        self.repository.advance_session(
            token, expected_status=SessionStatus.RUNNING,
            new_status=SessionStatus.CHECKPOINTING, at_ms=stop_requested_at,
        )
        late_checkpoint = checkpoint_for(token)
        late_checkpoint = Checkpoint(
            checkpoint_id=late_checkpoint.checkpoint_id,
            account_scope_id=late_checkpoint.account_scope_id,
            session_id=late_checkpoint.session_id,
            schema_version=late_checkpoint.schema_version,
            covered_event_sequence=late_checkpoint.covered_event_sequence,
            aggregate_versions_json=late_checkpoint.aggregate_versions_json,
            payload_json=late_checkpoint.payload_json,
            payload_checksum=late_checkpoint.payload_checksum,
            created_at_ms=stop_requested_at + 30_001,
            source_snapshot_id=late_checkpoint.source_snapshot_id,
            strategy_versions_json=late_checkpoint.strategy_versions_json,
            config_hash=late_checkpoint.config_hash,
        )
        with self.assertRaises(GracefulStopTimeoutError):
            self.repository.publish_checkpoint(late_checkpoint, fencing_token=token)
        result = self.repository.advance_session(
            token, expected_status=SessionStatus.CHECKPOINTING,
            new_status=SessionStatus.CLOSED, at_ms=stop_requested_at + 30_001,
        )
        self.assertEqual(result.status, SessionStatus.INTERRUPTED)

    def test_close_revalidates_checkpoint_aggregate_versions_before_marking_closed(self):
        token = start_running(self.repository)
        commit_one(self.repository, token)
        self.repository.advance_session(
            token, expected_status=SessionStatus.RUNNING,
            new_status=SessionStatus.CHECKPOINTING, at_ms=1_800_000_100_000,
        )
        self.repository.publish_checkpoint(checkpoint_for(token), fencing_token=token)
        with sqlite3.connect(self.path) as connection:
            connection.execute("DROP TRIGGER ps_checkpoints_no_update")
            connection.execute(
                "UPDATE ps_checkpoint_generations SET aggregate_versions_json=? WHERE checkpoint_id=?",
                (canonical_json({"ledger-core": 0}), "checkpoint-session-1-1"),
            )
            connection.execute(
                """
                CREATE TRIGGER ps_checkpoints_no_update
                BEFORE UPDATE ON ps_checkpoint_generations
                BEGIN
                    SELECT RAISE(ABORT, 'ps_checkpoint_generations is append-only');
                END
                """
            )
        with self.assertRaises(CheckpointIntegrityError):
            self.repository.advance_session(
                token, expected_status=SessionStatus.CHECKPOINTING,
                new_status=SessionStatus.CLOSED, at_ms=1_800_000_100_001,
            )
        self.assertEqual(self.repository.get_session("session-1").status, SessionStatus.CHECKPOINTING)

    def test_stop_blocks_new_paper_transitions_after_checkpointing_begins(self):
        token = start_running(self.repository)
        commit_one(self.repository, token)
        self.repository.advance_session(
            token, expected_status=SessionStatus.RUNNING,
            new_status=SessionStatus.CHECKPOINTING, at_ms=1_800_000_100_000,
        )
        with self.assertRaises(SessionStateConflictError):
            commit_one(self.repository, token, sequence=2)
        self.assertEqual(len(self.repository.read_events("paper-account")), 1)

    def test_blocked_preflight_and_restore_are_terminal(self):
        preflight_token = self.repository.claim_writer(make_session("blocked-preflight"))
        self.repository.advance_session(
            preflight_token, expected_status=SessionStatus.START_REQUESTED,
            new_status=SessionStatus.PREFLIGHT, at_ms=1_800_000_000_001,
        )
        self.repository.advance_session(
            preflight_token, expected_status=SessionStatus.PREFLIGHT,
            new_status=SessionStatus.BLOCKED_PREFLIGHT, at_ms=1_800_000_000_002,
        )
        with self.assertRaises(SessionTransitionError):
            self.repository.advance_session(
                preflight_token, expected_status=SessionStatus.BLOCKED_PREFLIGHT,
                new_status=SessionStatus.READY, at_ms=1_800_000_000_003,
            )
        self.assertEqual(
            self.repository.get_session("blocked-preflight").status,
            SessionStatus.BLOCKED_PREFLIGHT,
        )

        restore_token = self.repository.claim_writer(
            make_session("blocked-restore", started_at_ms=1_800_000_010_000)
        )
        self.repository.advance_session(
            restore_token, expected_status=SessionStatus.START_REQUESTED,
            new_status=SessionStatus.PREFLIGHT, at_ms=1_800_000_010_001,
        )
        self.repository.advance_session(
            restore_token, expected_status=SessionStatus.PREFLIGHT,
            new_status=SessionStatus.RESTORING, at_ms=1_800_000_010_002,
            preflight_attestation=ready_evidence_for(
                self.repository.get_session("blocked-restore"), restore_token,
            ).preflight,
        )
        self.repository.advance_session(
            restore_token, expected_status=SessionStatus.RESTORING,
            new_status=SessionStatus.BLOCKED_RESTORE, at_ms=1_800_000_010_003,
        )
        with self.assertRaises(SessionTransitionError):
            self.repository.advance_session(
                restore_token, expected_status=SessionStatus.BLOCKED_RESTORE,
                new_status=SessionStatus.READY, at_ms=1_800_000_010_004,
            )
        self.assertEqual(
            self.repository.get_session("blocked-restore").status,
            SessionStatus.BLOCKED_RESTORE,
        )

    def test_failed_persistence_and_aborted_sessions_cannot_resume(self):
        failed_token = self.repository.claim_writer(make_session("failed-session"))
        self.repository.advance_session(
            failed_token, expected_status=SessionStatus.START_REQUESTED,
            new_status=SessionStatus.FAILED_PERSISTENCE, at_ms=1_800_000_000_001,
        )
        with self.assertRaises(SessionTransitionError):
            self.repository.advance_session(
                failed_token, expected_status=SessionStatus.FAILED_PERSISTENCE,
                new_status=SessionStatus.PREFLIGHT, at_ms=1_800_000_000_002,
            )
        aborted_token = self.repository.claim_writer(
            make_session("aborted-session", started_at_ms=1_800_000_010_000)
        )
        self.repository.advance_session(
            aborted_token, expected_status=SessionStatus.START_REQUESTED,
            new_status=SessionStatus.ABORTED, at_ms=1_800_000_010_001,
        )
        with self.assertRaises(SessionTransitionError):
            self.repository.advance_session(
                aborted_token, expected_status=SessionStatus.ABORTED,
                new_status=SessionStatus.PREFLIGHT, at_ms=1_800_000_010_002,
            )

    def test_close_revalidates_checkpoint_checksum_before_marking_closed(self):
        token = start_running(self.repository)
        commit_one(self.repository, token)
        self.repository.advance_session(
            token, expected_status=SessionStatus.RUNNING,
            new_status=SessionStatus.CHECKPOINTING, at_ms=1_800_000_100_000,
        )
        self.repository.publish_checkpoint(checkpoint_for(token), fencing_token=token)
        with sqlite3.connect(self.path) as connection:
            connection.execute("DROP TRIGGER ps_checkpoints_no_update")
            connection.execute(
                "UPDATE ps_checkpoint_generations SET payload_json=? WHERE checkpoint_id=?",
                ('{"tampered":true}', "checkpoint-session-1-1"),
            )
            connection.execute(
                """
                CREATE TRIGGER ps_checkpoints_no_update
                BEFORE UPDATE ON ps_checkpoint_generations
                BEGIN
                    SELECT RAISE(ABORT, 'ps_checkpoint_generations is append-only');
                END
                """
            )
        with self.assertRaises(CheckpointIntegrityError):
            self.repository.advance_session(
                token, expected_status=SessionStatus.CHECKPOINTING,
                new_status=SessionStatus.CLOSED, at_ms=1_800_000_100_001,
            )
        self.assertEqual(self.repository.get_session("session-1").status, SessionStatus.CHECKPOINTING)

    def test_closed_session_is_not_relabelled_interrupted_on_next_start(self):
        token = start_running(self.repository)
        commit_one(self.repository, token)
        self.repository.advance_session(
            token, expected_status=SessionStatus.RUNNING,
            new_status=SessionStatus.CHECKPOINTING, at_ms=1_800_000_100_000,
        )
        self.repository.publish_checkpoint(checkpoint_for(token), fencing_token=token)
        self.repository.advance_session(
            token, expected_status=SessionStatus.CHECKPOINTING,
            new_status=SessionStatus.CLOSED, at_ms=1_800_000_100_001,
        )
        self.repository.claim_writer(
            make_session("next-session", started_at_ms=1_800_000_200_000)
        )
        self.assertEqual(self.repository.get_session("session-1").status, SessionStatus.CLOSED)

    def test_fencing_generations_are_independent_per_account_scope(self):
        first = self.repository.claim_writer(make_session("account-a", account="account-a"))
        other = self.repository.claim_writer(make_session("account-b", account="account-b"))
        self.assertEqual(first.fencing_generation, 1)
        self.assertEqual(other.fencing_generation, 1)
        self.assertEqual(self.repository.get_writer_fence("account-a"), first)
        self.assertEqual(self.repository.get_writer_fence("account-b"), other)

    def test_session_and_fencing_state_survive_repository_reopen(self):
        token = start_running(self.repository)
        reopened = SQLiteStateRepository(self.path)
        self.assertEqual(reopened.get_writer_fence("paper-account"), token)
        self.assertEqual(reopened.get_session("session-1").status, SessionStatus.RUNNING)


if __name__ == "__main__":
    unittest.main()
