import hashlib
import json
import unittest

from persistent_state.contracts import (
    Checkpoint, EventRecord, IdempotencyClaim, PositionLedger, RiskState,
    SessionRecord, SessionStatus, SmartDCAState, StrategyId, StrategyState,
    derive_idempotency_key,
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def session(**changes):
    values = dict(
        session_id="session-001", account_scope_id="personal-paper",
        status=SessionStatus.RUNNING, started_at_ms=1_800_000_000_000,
        initiator="MANUAL", source_snapshot_id="snapshot-001",
        config_hash="sha256:" + "a" * 64, code_version="git:" + "b" * 40,
        last_committed_event_sequence=0,
    )
    values.update(changes)
    return SessionRecord(**values)


def event(**changes):
    values = dict(
        event_id="event-001", account_scope_id="personal-paper", session_id="session-001",
        event_sequence=1, aggregate_version=1, event_type="POSITION_OPENED",
        strategy_id=StrategyId.CORE, strategy_version="core-v1",
        created_at_ms=1_800_000_000_000, recorded_at_ms=1_800_000_000_001,
        payload_json=canonical({"quantity": "0.01"}), market_snapshot_id="snapshot-001",
        candle_open_time_ms=1_800_000_000_000,
    )
    values.update(changes)
    return EventRecord(**values)


class SessionContractTests(unittest.TestCase):
    def test_accepts_manual_running_session(self):
        self.assertEqual(session().status, SessionStatus.RUNNING)

    def test_closed_session_requires_end_timestamp(self):
        with self.assertRaises(ValueError):
            session(status=SessionStatus.CLOSED)

    def test_end_timestamp_cannot_precede_start(self):
        with self.assertRaises(ValueError):
            session(status=SessionStatus.CLOSED, ended_at_ms=1)

    def test_boolean_is_not_a_timestamp_or_sequence(self):
        with self.assertRaises(ValueError):
            session(started_at_ms=True)
        with self.assertRaises(ValueError):
            session(last_committed_event_sequence=True)

    def test_unknown_schema_version_fails_closed(self):
        with self.assertRaises(ValueError):
            session(schema_version=2)


class EventContractTests(unittest.TestCase):
    def test_accepts_canonical_event_payload(self):
        self.assertEqual(event().event_sequence, 1)

    def test_rejects_noncanonical_json(self):
        with self.assertRaises(ValueError):
            event(payload_json='{"quantity": "0.01", "a": 1}')

    def test_rejects_recorded_time_before_created_time(self):
        with self.assertRaises(ValueError):
            event(recorded_at_ms=1)

    def test_rejects_nonpositive_event_sequence(self):
        with self.assertRaises(ValueError):
            event(event_sequence=0)


class StrategyStateContractTests(unittest.TestCase):
    def test_accepts_independent_ai_state(self):
        state = StrategyState(
            account_scope_id="personal-paper", strategy_id=StrategyId.AI,
            strategy_version="ai-v1", last_evaluated_candle_open_time_ms=100,
            cooldown_until_ms=None, eligibility_state="ELIGIBLE",
            state_json=canonical({"modelVersion": "model-v1"}),
        )
        self.assertEqual(state.strategy_id, StrategyId.AI)

    def test_rejects_cooldown_before_last_evaluated_candle(self):
        with self.assertRaises(ValueError):
            StrategyState(
                account_scope_id="personal-paper", strategy_id=StrategyId.CORE,
                strategy_version="core-v1", last_evaluated_candle_open_time_ms=100,
                cooldown_until_ms=99, eligibility_state="ELIGIBLE", state_json="{}",
            )


class PositionLedgerContractTests(unittest.TestCase):
    def test_accepts_open_short_with_exact_decimal_strings(self):
        item = PositionLedger(
            account_scope_id="personal-paper", ledger_id="ledger-ai",
            strategy_id=StrategyId.AI, position_id="position-1", symbol="BTCUSDT",
            side="SHORT", status="OPEN", quantity="0.015", average_entry_price="92000.25",
            realized_pnl_quote="-1.25", fees_quote="0.03", aggregate_version=2,
        )
        self.assertEqual(item.quantity, "0.015")

    def test_rejects_binary_float_accounting_values(self):
        with self.assertRaises(ValueError):
            PositionLedger(
                account_scope_id="personal-paper", ledger_id="ledger-core",
                strategy_id=StrategyId.CORE, position_id="position-1", symbol="BTCUSDT",
                side="LONG", status="OPEN", quantity=0.01, average_entry_price="90000",
                realized_pnl_quote="0", fees_quote="0", aggregate_version=1,
            )

    def test_closed_position_must_have_zero_quantity(self):
        with self.assertRaises(ValueError):
            PositionLedger(
                account_scope_id="personal-paper", ledger_id="ledger-core",
                strategy_id=StrategyId.CORE, position_id="position-1", symbol="BTCUSDT",
                side="LONG", status="CLOSED", quantity="0.01", average_entry_price="90000",
                realized_pnl_quote="0", fees_quote="0", aggregate_version=2,
            )

    def test_rejects_negative_quantity_and_fee(self):
        base = dict(
            account_scope_id="personal-paper", ledger_id="ledger-core",
            strategy_id=StrategyId.CORE, position_id="position-1", symbol="BTCUSDT",
            side="LONG", status="OPEN", quantity="0.01", average_entry_price="90000",
            realized_pnl_quote="0", fees_quote="0", aggregate_version=1,
        )
        with self.assertRaises(ValueError):
            PositionLedger(**{**base, "quantity": "-0.01"})
        with self.assertRaises(ValueError):
            PositionLedger(**{**base, "fees_quote": "-0.01"})


class SmartDCAContractTests(unittest.TestCase):
    def test_accepts_reconciled_core_dca_state(self):
        state = SmartDCAState(
            account_scope_id="personal-paper", strategy_id=StrategyId.CORE,
            position_id="core-position-1", dca_level=1, max_dca_levels=4,
            cumulative_added_quantity="0.01", cumulative_added_notional_quote="900",
            next_eligible_level=2, next_trigger_price="88000",
            last_dca_event_id="event-dca-1", policy_version="smart-dca-v1",
        )
        self.assertEqual(state.dca_level, 1)

    def test_ai_cannot_reuse_core_smart_dca_contract(self):
        with self.assertRaises(ValueError):
            SmartDCAState(
                account_scope_id="personal-paper", strategy_id=StrategyId.AI,
                position_id="ai-position-1", dca_level=0, max_dca_levels=4,
                cumulative_added_quantity="0", cumulative_added_notional_quote="0",
                next_eligible_level=1, next_trigger_price="88000",
                last_dca_event_id=None, policy_version="smart-dca-v1",
            )

    def test_dca_level_cannot_exceed_policy_maximum(self):
        with self.assertRaises(ValueError):
            SmartDCAState(
                account_scope_id="personal-paper", strategy_id=StrategyId.CORE,
                position_id="core-position-1", dca_level=5, max_dca_levels=4,
                cumulative_added_quantity="0.01", cumulative_added_notional_quote="900",
                next_eligible_level=None, next_trigger_price=None,
                last_dca_event_id="event-5", policy_version="smart-dca-v1",
            )


class RiskStateContractTests(unittest.TestCase):
    def test_latched_kill_switch_requires_reason(self):
        with self.assertRaises(ValueError):
            RiskState(
                account_scope_id="personal-paper", kill_switch_latched=True,
                kill_switch_reason=None, risk_policy_version="risk-v1",
                reserved_margin_quote="0", aggregate_version=1,
            )

    def test_unlatched_kill_switch_cannot_carry_stale_reason(self):
        with self.assertRaises(ValueError):
            RiskState(
                account_scope_id="personal-paper", kill_switch_latched=False,
                kill_switch_reason="operator stop", risk_policy_version="risk-v1",
                reserved_margin_quote="0", aggregate_version=1,
            )

    def test_rejects_negative_reserved_margin(self):
        with self.assertRaises(ValueError):
            RiskState(
                account_scope_id="personal-paper", kill_switch_latched=False,
                kill_switch_reason=None, risk_policy_version="risk-v1",
                reserved_margin_quote="-1", aggregate_version=1,
            )


class IdempotencyContractTests(unittest.TestCase):
    def dimensions(self, **changes):
        values = dict(
            account_scope_id="personal-paper", ledger_id="ledger-core",
            strategy_id=StrategyId.CORE, strategy_version="core-v1",
            market_snapshot_id="snapshot-001", candle_open_time_ms=1_800_000_000_000,
            action_kind="ENTRY", action_ordinal=0,
        )
        values.update(changes)
        return values

    def test_key_is_stable_for_same_logical_intent(self):
        first = derive_idempotency_key(**self.dimensions())
        second = derive_idempotency_key(**self.dimensions())
        self.assertEqual(first, second)
        self.assertRegex(first, r"^sha256:[0-9a-f]{64}$")

    def test_key_changes_when_strategy_version_changes(self):
        self.assertNotEqual(
            derive_idempotency_key(**self.dimensions()),
            derive_idempotency_key(**self.dimensions(strategy_version="core-v2")),
        )

    def test_claim_rejects_invalid_hash_and_negative_ordinal(self):
        common = self.dimensions()
        with self.assertRaises(ValueError):
            IdempotencyClaim(
                idempotency_key="sha256:" + "a" * 64, payload_hash="not-a-hash",
                **common,
            )
        with self.assertRaises(ValueError):
            IdempotencyClaim(
                idempotency_key="sha256:" + "a" * 64, payload_hash="sha256:" + "b" * 64,
                **self.dimensions(action_ordinal=-1),
            )

    def test_claim_rejects_key_that_does_not_match_logical_dimensions(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            IdempotencyClaim(
                idempotency_key="sha256:" + "a" * 64,
                payload_hash="sha256:" + "b" * 64, **self.dimensions(),
            )


class CheckpointContractTests(unittest.TestCase):
    def checkpoint(self, **changes):
        payload = canonical({"core": {"position": "0"}, "ai": {"position": "0"}})
        values = dict(
            checkpoint_id="checkpoint-001", account_scope_id="personal-paper",
            session_id="session-001", schema_version=1, covered_event_sequence=12,
            aggregate_versions_json=canonical({"CORE": 5, "AI": 7, "RISK": 2}),
            payload_json=payload,
            payload_checksum="sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest(),
            created_at_ms=1_800_000_000_000, source_snapshot_id="snapshot-001",
            strategy_versions_json=canonical({"CORE": "core-v1", "AI": "ai-v1"}),
            config_hash="sha256:" + "a" * 64,
        )
        values.update(changes)
        return Checkpoint(**values)

    def test_accepts_valid_checkpoint_checksum(self):
        self.assertEqual(self.checkpoint().covered_event_sequence, 12)

    def test_rejects_checkpoint_checksum_mismatch(self):
        with self.assertRaises(ValueError):
            self.checkpoint(payload_checksum="sha256:" + "0" * 64)

    def test_rejects_noncanonical_checkpoint_payload(self):
        with self.assertRaises(ValueError):
            self.checkpoint(payload_json='{"b":2, "a":1}')

    def test_rejects_negative_aggregate_version(self):
        with self.assertRaises(ValueError):
            self.checkpoint(aggregate_versions_json=canonical({"CORE": -1}))

    def test_rejects_unknown_checkpoint_schema_version(self):
        with self.assertRaises(ValueError):
            self.checkpoint(schema_version=2)


if __name__ == "__main__":
    unittest.main()
