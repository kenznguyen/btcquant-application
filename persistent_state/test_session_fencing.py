import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from persistent_state.contracts import (
    Checkpoint, EventRecord, IdempotencyClaim, SessionRecord, SessionStatus,
    StrategyId, canonical_json, derive_idempotency_key,
)
from persistent_state.repository import (
    AggregateMutation, CheckpointIntegrityError, CheckpointRequiredForCloseError,
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
        repository.advance_session(token, expected_status=expected, new_status=target, at_ms=start + 1)
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
        candle_open_time_ms=1_800_000_000_000,
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
        created_at_ms=1_800_000_200_000, source_snapshot_id="snapshot-1",
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
            new_status=SessionStatus.CLOSED, at_ms=1_800_000_100_002,
        )
        self.assertEqual(closed.status, SessionStatus.CLOSED)
        self.assertEqual(closed.ended_at_ms, 1_800_000_100_002)

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
