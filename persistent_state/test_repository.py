import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from persistent_state.contracts import (
    EventRecord, IdempotencyClaim, SessionRecord, SessionStatus, StrategyId,
    canonical_json, derive_idempotency_key,
)
from persistent_state.test_support import ready_evidence_for, resume_confirmation_for
from persistent_state.repository import (
    AggregateMutation, AggregateVersionConflictError, EventSequenceConflictError,
    IdempotencyConflictError, RepositorySchemaError, SQLiteStateRepository,
    TransitionContractError,
)


def digest(value):
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def start_running_session(repository, session_id, account_scope_id):
    started_at = 1_800_000_000_000
    session = SessionRecord(
        session_id=session_id, account_scope_id=account_scope_id,
        status=SessionStatus.START_REQUESTED, started_at_ms=started_at,
        initiator="MANUAL", source_snapshot_id="snapshot-1",
        config_hash="sha256:" + "a" * 64, code_version="git:" + "b" * 40,
        last_committed_event_sequence=0,
    )
    token = repository.claim_writer(session)
    for expected, target in (
        (SessionStatus.START_REQUESTED, SessionStatus.PREFLIGHT),
        (SessionStatus.PREFLIGHT, SessionStatus.RESTORING),
        (SessionStatus.RESTORING, SessionStatus.READY),
        (SessionStatus.READY, SessionStatus.RUNNING),
    ):
        kwargs = {}
        if target is SessionStatus.READY:
            kwargs["readiness_evidence"] = ready_evidence_for(
                repository.get_session(session_id), token,
            )
        if target is SessionStatus.RUNNING:
            kwargs["resume_confirmation"] = resume_confirmation_for(
                repository.get_session(session_id), token, confirmed_at_ms=started_at + 1,
            )
        repository.advance_session(
            token, expected_status=expected, new_status=target,
            at_ms=started_at + 1, **kwargs,
        )
    return token


class SQLiteStateRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "application-state-test.sqlite3"
        self.repository = SQLiteStateRepository(self.path)
        self.repository.initialize()
        self.token = start_running_session(self.repository, "session-1", "paper-account")

    def transition(self, *, account="paper-account", session_id="session-1",
                   sequence=1, expected_version=0, ordinal=0,
                   payload='{"target":"0.01"}', state='{"position":"0.01"}',
                   event_id="event-1", strategy=StrategyId.CORE):
        ledger_id = "ledger-" + strategy.value.lower()
        snapshot_id = "snapshot-1"
        strategy_version = strategy.value.lower() + "-v1"
        claim = IdempotencyClaim(
            idempotency_key=derive_idempotency_key(
                account_scope_id=account, ledger_id=ledger_id, strategy_id=strategy,
                strategy_version=strategy_version, market_snapshot_id=snapshot_id,
                candle_open_time_ms=1_800_000_000_000, action_kind="ENTRY", action_ordinal=ordinal,
            ),
            payload_hash=digest(payload), account_scope_id=account, ledger_id=ledger_id,
            strategy_id=strategy, strategy_version=strategy_version,
            market_snapshot_id=snapshot_id, candle_open_time_ms=1_800_000_000_000,
            action_kind="ENTRY", action_ordinal=ordinal,
        )
        event = EventRecord(
            event_id=event_id, account_scope_id=account, session_id=session_id,
            aggregate_id=ledger_id,
            event_sequence=sequence, aggregate_version=expected_version + 1,
            event_type="POSITION_UPDATED", strategy_id=strategy,
            strategy_version=strategy_version, created_at_ms=1_800_000_000_000,
            recorded_at_ms=1_800_000_000_001, payload_json=payload,
            market_snapshot_id=snapshot_id, candle_open_time_ms=1_800_000_000_000,
        )
        mutation = AggregateMutation(
            account_scope_id=account, aggregate_id=ledger_id,
            aggregate_type="POSITION_LEDGER", strategy_id=strategy,
            expected_version=expected_version, state_json=state,
        )
        return event, claim, mutation

    def test_constructor_does_not_create_or_open_database(self):
        missing = Path(self.temp.name) / "not-created.sqlite3"
        repo = SQLiteStateRepository(missing)
        self.assertFalse(missing.exists())
        self.assertIsNotNone(repo)

    def test_initialize_creates_schema_only_at_explicit_temporary_path(self):
        path = Path(self.temp.name) / "explicit-init.sqlite3"
        repo = SQLiteStateRepository(path)
        self.assertFalse(path.exists())
        repo.initialize()
        self.assertTrue(path.is_file())
        with sqlite3.connect(path) as connection:
            self.assertEqual(connection.execute("PRAGMA user_version").fetchone()[0], 1)

    def test_initialize_fails_closed_on_unversioned_database_with_existing_tables(self):
        path = Path(self.temp.name) / "unknown.sqlite3"
        with sqlite3.connect(path) as connection:
            connection.execute("CREATE TABLE foreign_table (value TEXT)")
        repo = SQLiteStateRepository(path)
        with self.assertRaises(RepositorySchemaError):
            repo.initialize()
        with sqlite3.connect(path) as connection:
            names = connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='foreign_table'"
            ).fetchall()
        self.assertEqual(names, [("foreign_table",)])

    def test_initialize_fails_closed_on_unknown_newer_schema(self):
        path = Path(self.temp.name) / "newer.sqlite3"
        with sqlite3.connect(path) as connection:
            connection.execute("PRAGMA user_version=99")
        with self.assertRaises(RepositorySchemaError):
            SQLiteStateRepository(path).initialize()

    def test_commit_atomically_appends_event_claim_and_aggregate(self):
        event, claim, mutation = self.transition()
        result = self.repository.commit_transition(event, claim, mutation, fencing_token=self.token)
        self.assertFalse(result.duplicate)
        self.assertEqual(result.event_id, "event-1")
        self.assertEqual(result.event_sequence, 1)
        self.assertEqual(result.aggregate_version, 1)
        aggregate = self.repository.read_aggregate("paper-account", "ledger-core")
        self.assertEqual(aggregate.state_json, '{"position":"0.01"}')
        self.assertEqual(aggregate.aggregate_version, 1)
        self.assertEqual(len(self.repository.read_events("paper-account")), 1)

    def test_same_key_and_payload_reuses_original_result_without_second_mutation(self):
        event, claim, mutation = self.transition()
        original = self.repository.commit_transition(event, claim, mutation, fencing_token=self.token)
        retry_event, retry_claim, retry_mutation = self.transition(
            sequence=2, expected_version=1, event_id="event-retry",
        )
        retried = self.repository.commit_transition(retry_event, retry_claim, retry_mutation, fencing_token=self.token)
        self.assertTrue(retried.duplicate)
        self.assertEqual(retried.event_id, original.event_id)
        self.assertEqual(self.repository.read_aggregate("paper-account", "ledger-core").aggregate_version, 1)
        self.assertEqual(self.repository.get_session("session-1").last_committed_event_sequence, 1)
        self.assertEqual(len(self.repository.read_events("paper-account")), 1)

    def test_same_key_with_different_payload_is_rejected(self):
        event, claim, mutation = self.transition()
        self.repository.commit_transition(event, claim, mutation, fencing_token=self.token)
        retry_event, retry_claim, retry_mutation = self.transition(
            sequence=2, expected_version=1, event_id="event-conflict",
            payload='{"target":"0.02"}', state='{"position":"0.02"}',
        )
        with self.assertRaises(IdempotencyConflictError):
            self.repository.commit_transition(retry_event, retry_claim, retry_mutation, fencing_token=self.token)
        self.assertEqual(len(self.repository.read_events("paper-account")), 1)

    def test_stale_aggregate_version_is_rejected_without_partial_writes(self):
        event, claim, mutation = self.transition()
        self.repository.commit_transition(event, claim, mutation, fencing_token=self.token)
        stale_event, stale_claim, stale_mutation = self.transition(
            sequence=2, expected_version=0, event_id="event-stale", ordinal=1,
        )
        with self.assertRaises(AggregateVersionConflictError):
            self.repository.commit_transition(stale_event, stale_claim, stale_mutation, fencing_token=self.token)
        self.assertEqual(len(self.repository.read_events("paper-account")), 1)
        self.assertEqual(self.repository.read_aggregate("paper-account", "ledger-core").aggregate_version, 1)

    def test_noncontiguous_event_sequence_is_rejected(self):
        event, claim, mutation = self.transition(sequence=2)
        with self.assertRaises(EventSequenceConflictError):
            self.repository.commit_transition(event, claim, mutation, fencing_token=self.token)
        self.assertEqual(self.repository.read_events("paper-account"), ())

    def test_cross_scope_or_ledger_mismatch_is_rejected_before_write(self):
        event, claim, mutation = self.transition()
        mismatched = AggregateMutation(
            account_scope_id="another-account", aggregate_id=mutation.aggregate_id,
            aggregate_type=mutation.aggregate_type, strategy_id=mutation.strategy_id,
            expected_version=0, state_json=mutation.state_json,
        )
        with self.assertRaises(TransitionContractError):
            self.repository.commit_transition(event, claim, mismatched, fencing_token=self.token)
        self.assertEqual(self.repository.read_events("paper-account"), ())

    def test_failure_after_event_and_claim_insert_rolls_back_everything(self):
        event, claim, mutation = self.transition()
        with patch.object(
            self.repository, "_apply_aggregate_mutation",
            side_effect=RuntimeError("injected failure after event and claim insert"),
        ):
            with self.assertRaisesRegex(RuntimeError, "injected failure"):
                self.repository.commit_transition(event, claim, mutation, fencing_token=self.token)
        self.assertEqual(self.repository.read_events("paper-account"), ())
        self.assertIsNone(self.repository.read_aggregate("paper-account", "ledger-core"))
        with sqlite3.connect(self.path) as connection:
            count = connection.execute("SELECT COUNT(*) FROM ps_idempotency_claims").fetchone()[0]
        self.assertEqual(count, 0)

    def test_event_and_idempotency_history_are_append_only(self):
        event, claim, mutation = self.transition()
        self.repository.commit_transition(event, claim, mutation, fencing_token=self.token)
        with sqlite3.connect(self.path) as connection:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute("DELETE FROM ps_events WHERE event_id='event-1'")
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "UPDATE ps_idempotency_claims SET payload_hash=?",
                    (digest("tamper"),),
                )

    def test_read_from_missing_database_does_not_create_it(self):
        missing = Path(self.temp.name) / "read-only-missing.sqlite3"
        repo = SQLiteStateRepository(missing)
        with self.assertRaises(FileNotFoundError):
            repo.read_events("paper-account")
        self.assertFalse(missing.exists())

    def test_account_scopes_keep_aggregate_state_separate(self):
        token_a = start_running_session(self.repository, "session-a", "paper-a")
        token_b = start_running_session(self.repository, "session-b", "paper-b")
        event_a, claim_a, mutation_a = self.transition(
            account="paper-a", session_id="session-a", event_id="event-a",
            state='{"position":"0.01"}',
        )
        event_b, claim_b, mutation_b = self.transition(
            account="paper-b", session_id="session-b", event_id="event-b",
            state='{"position":"0.02"}',
        )
        self.repository.commit_transition(event_a, claim_a, mutation_a, fencing_token=token_a)
        self.repository.commit_transition(event_b, claim_b, mutation_b, fencing_token=token_b)
        self.assertEqual(
            self.repository.read_aggregate("paper-a", "ledger-core").state_json,
            '{"position":"0.01"}',
        )
        self.assertEqual(
            self.repository.read_aggregate("paper-b", "ledger-core").state_json,
            '{"position":"0.02"}',
        )

    def test_reopen_preserves_existing_version_one_state(self):
        event, claim, mutation = self.transition()
        self.repository.commit_transition(event, claim, mutation, fencing_token=self.token)
        reopened = SQLiteStateRepository(self.path)
        reopened.initialize()
        self.assertEqual(reopened.read_aggregate("paper-account", "ledger-core").aggregate_version, 1)


if __name__ == "__main__":
    unittest.main()
