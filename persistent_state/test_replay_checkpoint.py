import hashlib
import json
import sqlite3
from dataclasses import replace
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from persistent_state.contracts import (
    Checkpoint, EventRecord, IdempotencyClaim, StrategyId, canonical_json,
    derive_idempotency_key,
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
    )


def commit_event(repository, sequence):
    event = make_event(sequence)
    claim = IdempotencyClaim(
        idempotency_key=derive_idempotency_key(
            account_scope_id="paper-account", ledger_id="ledger-core",
            strategy_id=StrategyId.CORE, strategy_version="core-v1",
            market_snapshot_id="snapshot-1", candle_open_time_ms=1_800_000_000_000,
            action_kind="EVENT", action_ordinal=sequence,
        ),
        payload_hash=digest(event.payload_json), account_scope_id="paper-account",
        ledger_id="ledger-core", strategy_id=StrategyId.CORE, strategy_version="core-v1",
        market_snapshot_id="snapshot-1", candle_open_time_ms=1_800_000_000_000,
        action_kind="EVENT", action_ordinal=sequence,
    )
    mutation = AggregateMutation(
        account_scope_id="paper-account", aggregate_id="ledger-core",
        aggregate_type="POSITION_LEDGER", strategy_id=StrategyId.CORE,
        expected_version=sequence - 1,
        state_json=canonical_json({"position": str(sequence)}),
    )
    return repository.commit_transition(event, claim, mutation)


def make_checkpoint(sequence, *, checkpoint_id=None, payload=None):
    payload_json = canonical_json(payload or {"lastSequence": sequence, "state": {"position": str(sequence)}})
    return Checkpoint(
        checkpoint_id=checkpoint_id or f"checkpoint-{sequence}",
        account_scope_id="paper-account", session_id="session-1", schema_version=1,
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

    def test_publishes_verified_checkpoint_and_advances_active_pointer(self):
        commit_event(self.repository, 1)
        checkpoint = make_checkpoint(1)
        result = self.repository.publish_checkpoint(checkpoint)
        self.assertTrue(result.is_active)
        self.assertFalse(result.duplicate)
        self.assertEqual(self.repository.read_active_checkpoint("paper-account"), checkpoint)

    def test_checkpoint_cannot_cover_uncommitted_event_sequence(self):
        with self.assertRaises(CheckpointCoverageError):
            self.repository.publish_checkpoint(make_checkpoint(1))
        self.assertIsNone(self.repository.read_active_checkpoint("paper-account"))
        self.assertEqual(self.repository.list_checkpoints("paper-account"), ())

    def test_checkpoint_aggregate_versions_must_match_committed_event_prefix(self):
        commit_event(self.repository, 1)
        mismatched = replace(
            make_checkpoint(1),
            aggregate_versions_json=canonical_json({"ledger-core": 0}),
        )
        with self.assertRaises(CheckpointCoverageError):
            self.repository.publish_checkpoint(mismatched)
        self.assertEqual(self.repository.list_checkpoints("paper-account"), ())

    def test_active_checkpoint_pointer_never_moves_backwards(self):
        commit_event(self.repository, 1)
        commit_event(self.repository, 2)
        newer = make_checkpoint(2)
        older = make_checkpoint(1)
        self.assertTrue(self.repository.publish_checkpoint(newer).is_active)
        old_result = self.repository.publish_checkpoint(older)
        self.assertFalse(old_result.is_active)
        self.assertEqual(self.repository.read_active_checkpoint("paper-account"), newer)
        self.assertEqual(len(self.repository.list_checkpoints("paper-account")), 2)

    def test_same_checkpoint_id_and_same_content_is_idempotent(self):
        commit_event(self.repository, 1)
        checkpoint = make_checkpoint(1)
        first = self.repository.publish_checkpoint(checkpoint)
        retry = self.repository.publish_checkpoint(checkpoint)
        self.assertFalse(first.duplicate)
        self.assertTrue(retry.duplicate)
        self.assertEqual(self.repository.list_checkpoints("paper-account"), (checkpoint,))

    def test_same_checkpoint_id_with_different_content_is_conflict(self):
        commit_event(self.repository, 1)
        self.repository.publish_checkpoint(make_checkpoint(1))
        conflicting = make_checkpoint(1, payload={"lastSequence": 1, "state": {"position": "tampered"}})
        with self.assertRaises(CheckpointConflictError):
            self.repository.publish_checkpoint(conflicting)

    def test_different_checkpoint_ids_at_same_coverage_are_conflict(self):
        commit_event(self.repository, 1)
        self.repository.publish_checkpoint(make_checkpoint(1, checkpoint_id="checkpoint-a"))
        with self.assertRaises(CheckpointConflictError):
            self.repository.publish_checkpoint(make_checkpoint(1, checkpoint_id="checkpoint-b"))

    def test_checkpoint_insert_and_active_pointer_update_roll_back_together(self):
        commit_event(self.repository, 1)
        checkpoint = make_checkpoint(1)
        with patch.object(
            self.repository, "_set_checkpoint_head",
            side_effect=RuntimeError("injected checkpoint pointer failure"),
        ):
            with self.assertRaisesRegex(RuntimeError, "pointer failure"):
                self.repository.publish_checkpoint(checkpoint)
        self.assertEqual(self.repository.list_checkpoints("paper-account"), ())
        self.assertIsNone(self.repository.read_active_checkpoint("paper-account"))

    def test_corrupted_checkpoint_payload_is_rejected_on_read(self):
        commit_event(self.repository, 1)
        self.repository.publish_checkpoint(make_checkpoint(1))
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
        commit_event(self.repository, 1)
        self.repository.publish_checkpoint(make_checkpoint(1))
        with sqlite3.connect(self.path) as connection:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute("DELETE FROM ps_checkpoint_generations WHERE checkpoint_id='checkpoint-1'")

    def test_keeps_all_verified_generations_without_automatic_pruning(self):
        for sequence in (1, 2, 3):
            commit_event(self.repository, sequence)
            self.repository.publish_checkpoint(make_checkpoint(sequence))
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
