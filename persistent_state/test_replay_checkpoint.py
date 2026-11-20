import hashlib
import json
import sqlite3
from dataclasses import replace
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from persistent_state.contracts import (
    Checkpoint, EventRecord, IdempotencyClaim, SessionRecord, SessionStatus,
    StrategyId, canonical_json, derive_idempotency_key,
)
from persistent_state.repository import (
    AggregateMutation, CheckpointConflictError, CheckpointCoverageError,
    CheckpointIntegrityError, SQLiteStateRepository,
)
from persistent_state.replay import (
    ReplayValidationError, replay_events, replay_from_checkpoint,
)


def digest(value):
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def make_event(sequence, *, event_id=None, account="paper-account", aggregate_version=None):
    payload = canonical_json({"event": sequence, "position": str(sequence)})
    return EventRecord(
        event_id=event_id or f"event-{sequence}", account_scope_id=account,
        session_id="session-1", event_sequence=sequence,
        aggregate_version=aggregate_version or sequence, event_type="POSITION_UPDATED",
        strategy_id=StrategyId.CORE, strategy_version="core-v1",
        created_at_ms=1_800_000_000_000 + sequence,
        recorded_at_ms=1_800_000_000_001 + sequence, payload_json=payload,
        market_snapshot_id="snapshot-1", candle_open_time_ms=1_800_000_000_000,
        aggregate_id="ledger-core",
    )


def commit_event(repository, sequence, fencing_token):
    event = make_event(sequence, event_id=f"event-{sequence}", account=fencing_token.account_scope_id)
    event = EventRecord(
        event_id=event.event_id, account_scope_id=event.account_scope_id,
        session_id=fencing_token.session_id, event_sequence=event.event_sequence,
        aggregate_version=event.aggregate_version, event_type=event.event_type,
        strategy_id=event.strategy_id, strategy_version=event.strategy_version,
        created_at_ms=event.created_at_ms, recorded_at_ms=event.recorded_at_ms,
        payload_json=event.payload_json, market_snapshot_id=event.market_snapshot_id,
        candle_open_time_ms=event.candle_open_time_ms, aggregate_id=event.aggregate_id,
    )
    claim = IdempotencyClaim(
        idempotency_key=derive_idempotency_key(
            account_scope_id=fencing_token.account_scope_id, ledger_id="ledger-core",
            strategy_id=StrategyId.CORE, strategy_version="core-v1",
            market_snapshot_id="snapshot-1", candle_open_time_ms=1_800_000_000_000,
            action_kind="EVENT", action_ordinal=sequence,
        ),
        payload_hash=digest(event.payload_json), account_scope_id=fencing_token.account_scope_id,
        ledger_id="ledger-core", strategy_id=StrategyId.CORE, strategy_version="core-v1",
        market_snapshot_id="snapshot-1", candle_open_time_ms=1_800_000_000_000,
        action_kind="EVENT", action_ordinal=sequence,
    )
    mutation = AggregateMutation(
        account_scope_id=fencing_token.account_scope_id, aggregate_id="ledger-core",
        aggregate_type="POSITION_LEDGER", strategy_id=StrategyId.CORE,
        expected_version=sequence - 1,
        state_json=canonical_json({"position": str(sequence)}),
    )
    return repository.commit_transition(event, claim, mutation, fencing_token=fencing_token)


def make_checkpoint(sequence, *, checkpoint_id=None, payload=None, token=None):
    payload_json = canonical_json(payload or {"lastSequence": sequence, "state": {"position": str(sequence)}})
    account_scope_id = "paper-account" if token is None else token.account_scope_id
    session_id = "session-1" if token is None else token.session_id
    return Checkpoint(
        checkpoint_id=checkpoint_id or f"checkpoint-{sequence}",
        account_scope_id=account_scope_id, session_id=session_id, schema_version=1,
        covered_event_sequence=sequence,
        aggregate_versions_json=canonical_json({"ledger-core": sequence}),
        payload_json=payload_json,
        payload_checksum=digest(payload_json),
        created_at_ms=1_800_000_100_000 + sequence,
        source_snapshot_id="snapshot-1",
        strategy_versions_json=canonical_json({"CORE": "core-v1", "AI": "ai-v1"}),
        config_hash="sha256:" + "a" * 64,
    )


class CheckpointRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "checkpoint-test.sqlite3"
        self.repository = SQLiteStateRepository(self.path)
        self.repository.initialize()
        session = SessionRecord(
            session_id="session-1", account_scope_id="paper-account",
            status=SessionStatus.START_REQUESTED, started_at_ms=1_800_000_000_000,
            initiator="MANUAL", source_snapshot_id="snapshot-1",
            config_hash="sha256:" + "a" * 64, code_version="git:" + "b" * 40,
            last_committed_event_sequence=0,
        )
        self.token = self.repository.claim_writer(session)
        for expected, target in (
            (SessionStatus.START_REQUESTED, SessionStatus.PREFLIGHT),
            (SessionStatus.PREFLIGHT, SessionStatus.RESTORING),
            (SessionStatus.RESTORING, SessionStatus.READY),
            (SessionStatus.READY, SessionStatus.RUNNING),
        ):
            self.repository.advance_session(
                self.token, expected_status=expected, new_status=target, at_ms=1_800_000_000_001,
            )

    def test_publishes_verified_checkpoint_and_advances_active_pointer(self):
        commit_event(self.repository, 1, self.token)
        checkpoint = make_checkpoint(1, token=self.token)
        result = self.repository.publish_checkpoint(checkpoint, fencing_token=self.token)
        self.assertTrue(result.is_active)
        self.assertFalse(result.duplicate)
        self.assertEqual(self.repository.read_active_checkpoint("paper-account"), checkpoint)

    def test_checkpoint_cannot_cover_uncommitted_event_sequence(self):
        with self.assertRaises(CheckpointCoverageError):
            self.repository.publish_checkpoint(make_checkpoint(1, token=self.token), fencing_token=self.token)
        self.assertIsNone(self.repository.read_active_checkpoint("paper-account"))
        self.assertEqual(self.repository.list_checkpoints("paper-account"), ())

    def test_checkpoint_aggregate_versions_must_match_committed_event_prefix(self):
        commit_event(self.repository, 1, self.token)
        mismatched = replace(
            make_checkpoint(1, token=self.token),
            aggregate_versions_json=canonical_json({"ledger-core": 0}),
        )
        with self.assertRaises(CheckpointCoverageError):
            self.repository.publish_checkpoint(mismatched, fencing_token=self.token)
        self.assertEqual(self.repository.list_checkpoints("paper-account"), ())

    def test_active_checkpoint_pointer_never_moves_backwards(self):
        commit_event(self.repository, 1, self.token)
        commit_event(self.repository, 2, self.token)
        newer = make_checkpoint(2, token=self.token)
        older = make_checkpoint(1, token=self.token)
        self.assertTrue(self.repository.publish_checkpoint(newer, fencing_token=self.token).is_active)
        old_result = self.repository.publish_checkpoint(older, fencing_token=self.token)
        self.assertFalse(old_result.is_active)
        self.assertEqual(self.repository.read_active_checkpoint("paper-account"), newer)
        self.assertEqual(len(self.repository.list_checkpoints("paper-account")), 2)

    def test_same_checkpoint_id_and_same_content_is_idempotent(self):
        commit_event(self.repository, 1, self.token)
        checkpoint = make_checkpoint(1, token=self.token)
        first = self.repository.publish_checkpoint(checkpoint, fencing_token=self.token)
        retry = self.repository.publish_checkpoint(checkpoint, fencing_token=self.token)
        self.assertFalse(first.duplicate)
        self.assertTrue(retry.duplicate)
        self.assertEqual(self.repository.list_checkpoints("paper-account"), (checkpoint,))

    def test_same_checkpoint_id_with_different_content_is_conflict(self):
        commit_event(self.repository, 1, self.token)
        self.repository.publish_checkpoint(make_checkpoint(1, token=self.token), fencing_token=self.token)
        conflicting = make_checkpoint(1, payload={"lastSequence": 1, "state": {"position": "tampered"}})
        with self.assertRaises(CheckpointConflictError):
            self.repository.publish_checkpoint(conflicting, fencing_token=self.token)

    def test_different_checkpoint_ids_at_same_coverage_are_conflict(self):
        commit_event(self.repository, 1, self.token)
        self.repository.publish_checkpoint(make_checkpoint(1, checkpoint_id="checkpoint-a", token=self.token), fencing_token=self.token)
        with self.assertRaises(CheckpointConflictError):
            self.repository.publish_checkpoint(make_checkpoint(1, checkpoint_id="checkpoint-b", token=self.token), fencing_token=self.token)

    def test_checkpoint_insert_and_active_pointer_update_roll_back_together(self):
        commit_event(self.repository, 1, self.token)
        checkpoint = make_checkpoint(1, token=self.token)
        with patch.object(
            self.repository, "_set_checkpoint_head",
            side_effect=RuntimeError("injected checkpoint pointer failure"),
        ):
            with self.assertRaisesRegex(RuntimeError, "pointer failure"):
                self.repository.publish_checkpoint(checkpoint, fencing_token=self.token)
        self.assertEqual(self.repository.list_checkpoints("paper-account"), ())
        self.assertIsNone(self.repository.read_active_checkpoint("paper-account"))

    def test_corrupted_checkpoint_payload_is_rejected_on_read(self):
        commit_event(self.repository, 1, self.token)
        self.repository.publish_checkpoint(make_checkpoint(1, token=self.token), fencing_token=self.token)
        with sqlite3.connect(self.path) as connection:
            connection.execute("DROP TRIGGER ps_checkpoints_no_update")
            connection.execute(
                "UPDATE ps_checkpoint_generations SET payload_json=? WHERE checkpoint_id=?",
                ('{"corrupted":true}', "checkpoint-1"),
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
            self.repository.read_active_checkpoint("paper-account")

    def test_checkpoint_generations_are_append_only(self):
        commit_event(self.repository, 1, self.token)
        self.repository.publish_checkpoint(make_checkpoint(1, token=self.token), fencing_token=self.token)
        with sqlite3.connect(self.path) as connection:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute("DELETE FROM ps_checkpoint_generations WHERE checkpoint_id='checkpoint-1'")

    def test_keeps_all_verified_generations_without_automatic_pruning(self):
        for sequence in (1, 2, 3):
            commit_event(self.repository, sequence, self.token)
            self.repository.publish_checkpoint(make_checkpoint(sequence), fencing_token=self.token)
        self.assertEqual(len(self.repository.list_checkpoints("paper-account")), 3)


class EventReplayTests(unittest.TestCase):
    @staticmethod
    def reducer(state, event):
        state["count"] = state.get("count", 0) + 1
        state["lastEventId"] = event.event_id
        return state

    def test_replays_contiguous_events_deterministically(self):
        events = (make_event(1), make_event(2))
        initial = canonical_json({"count": 0, "lastEventId": None})
        first = replay_events(initial, events, starting_sequence=0, reducer=self.reducer)
        second = replay_events(initial, events, starting_sequence=0, reducer=self.reducer)
        self.assertEqual(first, second)
        self.assertEqual(first.event_count, 2)
        self.assertEqual(first.last_event_sequence, 2)
        self.assertEqual(first.state_json, canonical_json({"count": 2, "lastEventId": "event-2"}))

    def test_rejects_event_sequence_gap(self):
        with self.assertRaises(ReplayValidationError):
            replay_events(
                canonical_json({"count": 0}), (make_event(2),),
                starting_sequence=0, reducer=self.reducer,
            )

    def test_rejects_out_of_order_events(self):
        with self.assertRaises(ReplayValidationError):
            replay_events(
                canonical_json({"count": 0}), (make_event(2), make_event(1)),
                starting_sequence=0, reducer=self.reducer,
            )

    def test_rejects_events_from_another_account_scope(self):
        with self.assertRaises(ReplayValidationError):
            replay_events(
                canonical_json({"count": 0}), (make_event(1, account="other"),),
                starting_sequence=0, reducer=self.reducer, account_scope_id="paper-account",
            )

    def test_rejects_reducer_result_that_is_not_an_object(self):
        with self.assertRaises(ReplayValidationError):
            replay_events(
                canonical_json({"count": 0}), (make_event(1),),
                starting_sequence=0, reducer=lambda state, event: ["not", "an", "object"],
            )

    def test_replays_from_checkpoint_event_boundary(self):
        checkpoint = make_checkpoint(1)
        result = replay_from_checkpoint(checkpoint, (make_event(2),), reducer=self.reducer)
        self.assertEqual(result.last_event_sequence, 2)
        self.assertEqual(result.event_count, 1)
        self.assertEqual(result.state_json, canonical_json({
            "lastSequence": 1, "state": {"position": "1"},
            "count": 1, "lastEventId": "event-2",
        }))

    def test_empty_event_tail_preserves_checkpoint_state(self):
        checkpoint = make_checkpoint(1)
        result = replay_from_checkpoint(checkpoint, (), reducer=self.reducer)
        self.assertEqual(result.last_event_sequence, 1)
        self.assertEqual(result.event_count, 0)
        self.assertEqual(result.state_json, checkpoint.payload_json)


if __name__ == "__main__":
    unittest.main()
