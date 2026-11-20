import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from persistent_state.contracts import (
    Checkpoint, EventRecord, IdempotencyClaim, SessionRecord, SessionStatus,
    StrategyId, canonical_json, derive_idempotency_key,
)
from persistent_state.repository import AggregateMutation, SQLiteStateRepository
from persistent_state.recovery import RecoveryValidationError, recover_repository_state


def digest(value):
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def reducer(state, event):
    aggregates = state.setdefault("aggregates", {})
    aggregates[event.aggregate_id] = {
        "aggregateVersion": event.aggregate_version,
        "state": json.loads(event.payload_json),
    }
    return state


class PersistentRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "recovery.sqlite3"
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
                self.token, expected_status=expected, new_status=target,
                at_ms=1_800_000_000_001,
            )

    def commit(self, sequence):
        payload = canonical_json({"position": str(sequence)})
        event = EventRecord(
            event_id=f"event-{sequence}", account_scope_id="paper-account",
            session_id="session-1", event_sequence=sequence,
            aggregate_version=sequence, event_type="POSITION_UPDATED",
            strategy_id=StrategyId.CORE, strategy_version="core-v1",
            created_at_ms=1_800_000_000_000 + sequence,
            recorded_at_ms=1_800_000_000_001 + sequence,
            payload_json=payload, market_snapshot_id="snapshot-1",
            candle_open_time_ms=1_800_000_000_000, aggregate_id="ledger-core",
        )
        claim = IdempotencyClaim(
            idempotency_key=derive_idempotency_key(
                account_scope_id="paper-account", ledger_id="ledger-core",
                strategy_id=StrategyId.CORE, strategy_version="core-v1",
                market_snapshot_id="snapshot-1",
                candle_open_time_ms=1_800_000_000_000,
                action_kind="RECOVERY_TEST", action_ordinal=sequence,
            ),
            payload_hash=digest(payload), account_scope_id="paper-account",
            ledger_id="ledger-core", strategy_id=StrategyId.CORE,
            strategy_version="core-v1", market_snapshot_id="snapshot-1",
            candle_open_time_ms=1_800_000_000_000,
            action_kind="RECOVERY_TEST", action_ordinal=sequence,
        )
        mutation = AggregateMutation(
            account_scope_id="paper-account", aggregate_id="ledger-core",
            aggregate_type="POSITION_LEDGER", strategy_id=StrategyId.CORE,
            expected_version=sequence - 1, state_json=payload,
        )
        self.repository.commit_transition(event, claim, mutation, fencing_token=self.token)

    def checkpoint(self, sequence):
        payload = canonical_json({
            "aggregates": {
                "ledger-core": {"aggregateVersion": sequence, "state": {"position": str(sequence)}}
            }
        })
        checkpoint = Checkpoint(
            checkpoint_id=f"checkpoint-{sequence}", account_scope_id="paper-account",
            session_id="session-1", schema_version=1,
            covered_event_sequence=sequence,
            aggregate_versions_json=canonical_json({"ledger-core": sequence}),
            payload_json=payload, payload_checksum=digest(payload),
            created_at_ms=1_800_000_100_000 + sequence,
            source_snapshot_id="snapshot-1",
            strategy_versions_json=canonical_json({"CORE": "core-v1"}),
            config_hash="sha256:" + "a" * 64,
        )
        self.repository.publish_checkpoint(checkpoint, fencing_token=self.token)

    def test_replays_full_event_history_when_no_checkpoint_exists(self):
        self.commit(1)
        self.commit(2)
        result = recover_repository_state(self.repository, "paper-account", reducer)
        self.assertEqual(result.last_event_sequence, 2)
        self.assertEqual(result.replayed_event_count, 2)
        self.assertEqual(json.loads(result.state_json)["aggregates"]["ledger-core"]["state"]["position"], "2")

    def test_replays_only_committed_tail_after_verified_checkpoint(self):
        self.commit(1)
        self.checkpoint(1)
        self.commit(2)
        result = recover_repository_state(self.repository, "paper-account", reducer)
        self.assertEqual(result.checkpoint_id, "checkpoint-1")
        self.assertEqual(result.last_event_sequence, 2)
        self.assertEqual(result.replayed_event_count, 1)
        self.assertEqual(json.loads(result.state_json)["aggregates"]["ledger-core"], {
            "aggregateVersion": 2, "state": {"position": "2"},
        })

    def test_manual_restart_after_crash_restores_checkpoint_and_committed_tail(self):
        self.commit(1)
        self.checkpoint(1)
        self.commit(2)
        reopened = SQLiteStateRepository(self.path)
        new_session = SessionRecord(
            session_id="session-after-crash", account_scope_id="paper-account",
            status=SessionStatus.START_REQUESTED, started_at_ms=1_800_000_030_000,
            initiator="MANUAL", source_snapshot_id="snapshot-1",
            config_hash="sha256:" + "a" * 64, code_version="git:" + "c" * 40,
            last_committed_event_sequence=0,
        )
        reopened.claim_writer(new_session)
        self.assertEqual(
            reopened.get_session("session-1").status, SessionStatus.INTERRUPTED,
        )
        recovered = recover_repository_state(reopened, "paper-account", reducer)
        self.assertEqual(recovered.checkpoint_id, "checkpoint-1")
        self.assertEqual(recovered.last_event_sequence, 2)
        self.assertEqual(recovered.replayed_event_count, 1)
        self.assertEqual(
            json.loads(recovered.state_json)["aggregates"]["ledger-core"]["state"]["position"],
            "2",
        )

    def test_repeated_recovery_is_deterministic_and_does_not_mutate_history(self):
        self.commit(1)
        self.commit(2)
        first = recover_repository_state(self.repository, "paper-account", reducer)
        second = recover_repository_state(self.repository, "paper-account", reducer)
        self.assertEqual(first, second)
        self.assertEqual(len(self.repository.read_events("paper-account")), 2)

    def test_recovery_rejects_event_sequence_gap_even_if_tail_is_after_checkpoint(self):
        self.commit(1)
        self.checkpoint(1)
        self.commit(2)
        with sqlite3.connect(self.path) as connection:
            connection.execute("DROP TRIGGER ps_events_no_delete")
            connection.execute("DELETE FROM ps_events WHERE event_sequence=1")
            connection.execute(
                "CREATE TRIGGER ps_events_no_delete BEFORE DELETE ON ps_events "
                "BEGIN SELECT RAISE(ABORT, 'append-only'); END"
            )
        with self.assertRaises(RecoveryValidationError):
            recover_repository_state(self.repository, "paper-account", reducer)

    def test_recovery_rejects_checkpoint_aggregate_versions_tampering(self):
        self.commit(1)
        self.checkpoint(1)
        with sqlite3.connect(self.path) as connection:
            connection.execute("DROP TRIGGER ps_checkpoints_no_update")
            connection.execute(
                "UPDATE ps_checkpoint_generations SET aggregate_versions_json=? WHERE checkpoint_id=?",
                (canonical_json({"ledger-core": 0}), "checkpoint-1"),
            )
            connection.execute(
                "CREATE TRIGGER ps_checkpoints_no_update BEFORE UPDATE ON ps_checkpoint_generations "
                "BEGIN SELECT RAISE(ABORT, 'append-only'); END"
            )
        with self.assertRaises(RecoveryValidationError):
            recover_repository_state(self.repository, "paper-account", reducer)

    def test_recovery_rejects_persisted_aggregate_that_disagrees_with_replay(self):
        self.commit(1)
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                "UPDATE ps_aggregate_state SET state_json=? WHERE aggregate_id=?",
                (canonical_json({"position": "999"}), "ledger-core"),
            )
        with self.assertRaises(RecoveryValidationError):
            recover_repository_state(self.repository, "paper-account", reducer)

    def test_recovery_rejects_aggregate_event_without_aggregate_identity(self):
        self.commit(1)
        with sqlite3.connect(self.path) as connection:
            connection.execute("DROP TRIGGER ps_events_no_update")
            connection.execute("UPDATE ps_events SET aggregate_id='' WHERE event_sequence=1")
            connection.execute(
                "CREATE TRIGGER ps_events_no_update BEFORE UPDATE ON ps_events "
                "BEGIN SELECT RAISE(ABORT, 'append-only'); END"
            )
        with self.assertRaises(RecoveryValidationError):
            recover_repository_state(self.repository, "paper-account", reducer)


if __name__ == "__main__":
    unittest.main()
