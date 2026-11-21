import unittest
from dataclasses import replace

from persistent_state.account_risk import AccountRiskProvenance, AccountRiskSnapshot
from persistent_state.contracts import RiskState, SessionStatus, StrategyId
from persistent_state.risk_admission import (
    RiskAdmissionContext, RiskProposal, SharedRiskEngine,
)
from persistent_state.risk_policy import VersionedRiskPolicy


class SharedRiskAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.engine = SharedRiskEngine()
        self.policy = VersionedRiskPolicy(
            version="shared-risk-v1", quote_asset="USDT",
            max_snapshot_age_ms=500, max_drawdown_quote="100",
            max_daily_loss_quote="30", max_gross_exposure_quote="500",
        )
        self.snapshot = AccountRiskSnapshot(
            snapshot_id="snapshot-001", schema_version=1,
            account_scope_id="paper-account", session_id="session-001",
            fencing_generation=7, generated_at_ms=10_000, as_of_ms=9_900,
            quote_asset="USDT", account_equity_quote="1000",
            gross_exposure_quote="200", reserved_margin_quote="5",
            drawdown_quote="20", daily_loss_quote="5",
            provenance=AccountRiskProvenance(
                provider_id="fixture-provider", source_id="fixture-source",
                source_snapshot_id="source-001", source_version="v1",
                source_payload_sha256="sha256:" + "a" * 64,
            ),
            verified=True, ledger_reconciled=True,
        )
        self.risk_state = RiskState(
            account_scope_id="paper-account", kill_switch_latched=False,
            kill_switch_reason=None, risk_policy_version=self.policy.version,
            reserved_margin_quote="5", aggregate_version=3,
        )
        self.context = RiskAdmissionContext(
            account_scope_id="paper-account", session_id="session-001",
            fencing_generation=7, session_status=SessionStatus.RUNNING,
            risk_state=self.risk_state, account_risk_snapshot=self.snapshot,
            risk_policy=self.policy, now_ms=10_100,
            shared_risk_engine_available=True,
        )

    def proposal(self, strategy=StrategyId.CORE, *, margin="10", exposure="10", action="ENTRY"):
        return RiskProposal(
            proposal_id=f"{strategy.value.lower()}-proposal",
            account_scope_id="paper-account", strategy_id=strategy,
            action_kind=action, direction="LONG",
            requested_margin_quote=margin,
            requested_gross_exposure_quote=exposure,
        )

    def test_core_and_ai_proposals_share_one_risk_admission_engine(self):
        for strategy in (StrategyId.CORE, StrategyId.AI):
            result = self.engine.evaluate(self.proposal(strategy), self.context)
            self.assertTrue(result.allowed, result.reason_code)
            self.assertEqual(result.risk_policy_version, "shared-risk-v1")

    def test_kill_switch_latch_blocks_both_strategy_ledgers(self):
        latched = replace(
            self.risk_state, kill_switch_latched=True,
            kill_switch_reason="operator emergency stop",
        )
        for strategy in (StrategyId.CORE, StrategyId.AI):
            result = self.engine.evaluate(
                self.proposal(strategy), replace(self.context, risk_state=latched),
            )
            self.assertFalse(result.allowed)
            self.assertEqual(result.reason_code, "KILL_SWITCH_LATCHED")

    def test_new_action_is_blocked_before_ready_and_while_not_running(self):
        for status in (
            SessionStatus.START_REQUESTED, SessionStatus.PREFLIGHT,
            SessionStatus.RESTORING, SessionStatus.READY,
            SessionStatus.CHECKPOINTING, SessionStatus.CLOSED,
        ):
            result = self.engine.evaluate(
                self.proposal(), replace(self.context, session_status=status),
            )
            self.assertFalse(result.allowed)
            self.assertEqual(result.reason_code, "SESSION_NOT_READY")

    def test_missing_shared_risk_engine_fails_closed(self):
        result = self.engine.evaluate(
            self.proposal(), replace(self.context, shared_risk_engine_available=False),
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "RISK_ENGINE_UNAVAILABLE")

    def test_missing_risk_state_fails_closed(self):
        result = self.engine.evaluate(
            self.proposal(), replace(self.context, risk_state=None),
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "RISK_STATE_UNAVAILABLE")

    def test_missing_snapshot_or_policy_fails_closed(self):
        for changes in (
            {"account_risk_snapshot": None},
            {"risk_policy": None},
        ):
            result = self.engine.evaluate(
                self.proposal(), replace(self.context, **changes),
            )
            self.assertFalse(result.allowed)

    def test_risk_state_from_another_account_scope_is_rejected(self):
        other = replace(self.risk_state, account_scope_id="other-account")
        result = self.engine.evaluate(
            self.proposal(), replace(self.context, risk_state=other),
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "RISK_SCOPE_MISMATCH")

    def test_exact_one_percent_order_margin_boundary_is_allowed(self):
        result = self.engine.evaluate(self.proposal(margin="10"), self.context)
        self.assertTrue(result.allowed, result.reason_code)

    def test_order_margin_above_one_percent_of_equity_is_blocked(self):
        result = self.engine.evaluate(self.proposal(margin="10.0001"), self.context)
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "ORDER_MARGIN_CAP_EXCEEDED")

    def test_invalid_binary_float_or_nonpositive_risk_inputs_fail_closed(self):
        for margin in (10.0, "0", "-1", "NaN", "Infinity", None):
            result = self.engine.evaluate(
                self.proposal(margin=margin), self.context,
            )
            self.assertFalse(result.allowed)
            self.assertEqual(result.reason_code, "RISK_INPUT_INVALID")

    def test_new_order_cannot_overcommit_equity_after_existing_reserved_margin(self):
        snapshot = replace(self.snapshot, reserved_margin_quote="995")
        state = replace(self.risk_state, reserved_margin_quote="995")
        result = self.engine.evaluate(
            self.proposal(margin="10"),
            replace(self.context, account_risk_snapshot=snapshot, risk_state=state),
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "INSUFFICIENT_MARGIN_CAPACITY")

    def test_reserved_margin_mismatch_is_unreconciled(self):
        state = replace(self.risk_state, reserved_margin_quote="6")
        result = self.engine.evaluate(
            self.proposal(), replace(self.context, risk_state=state),
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "RISK_STATE_UNRECONCILED")

    def test_reducing_and_exit_proposals_remain_available_after_limit_breach(self):
        breached = replace(
            self.snapshot, drawdown_quote="101", daily_loss_quote="31",
            gross_exposure_quote="600",
        )
        for action in ("REDUCE", "EXIT"):
            result = self.engine.evaluate(
                self.proposal(action=action, exposure=None),
                replace(self.context, account_risk_snapshot=breached),
            )
            self.assertTrue(result.allowed, result.reason_code)


if __name__ == "__main__":
    unittest.main()
