import unittest
from dataclasses import replace

from persistent_state.contracts import RiskState, SessionStatus, StrategyId
from persistent_state.risk_admission import (
    RiskAdmissionContext, RiskProposal, SharedRiskEngine,
)


class SharedRiskAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.engine = SharedRiskEngine()
        self.risk_state = RiskState(
            account_scope_id="paper-account", kill_switch_latched=False,
            kill_switch_reason=None, risk_policy_version="shared-risk-v1",
            reserved_margin_quote="5", aggregate_version=3,
        )
        self.context = RiskAdmissionContext(
            account_scope_id="paper-account", session_status=SessionStatus.RUNNING,
            risk_state=self.risk_state, account_equity_quote="1000",
            ledger_reconciled=True, shared_risk_engine_available=True,
        )

    def proposal(self, strategy=StrategyId.CORE, *, margin="10", action="ENTRY"):
        return RiskProposal(
            proposal_id=f"{strategy.value.lower()}-proposal",
            account_scope_id="paper-account", strategy_id=strategy,
            action_kind=action, direction="LONG",
            requested_margin_quote=margin,
        )

    def test_core_and_ai_proposals_share_one_risk_admission_engine(self):
        core = self.engine.evaluate(self.proposal(StrategyId.CORE), self.context)
        ai = self.engine.evaluate(self.proposal(StrategyId.AI), self.context)
        self.assertTrue(core.allowed, core.reason_code)
        self.assertTrue(ai.allowed, ai.reason_code)
        self.assertEqual(core.risk_policy_version, "shared-risk-v1")
        self.assertEqual(ai.risk_policy_version, "shared-risk-v1")

    def test_kill_switch_latch_blocks_both_strategy_ledgers(self):
        latched = RiskState(
            account_scope_id="paper-account", kill_switch_latched=True,
            kill_switch_reason="operator emergency stop",
            risk_policy_version="shared-risk-v1", reserved_margin_quote="5",
            aggregate_version=4,
        )
        context = replace(self.context, risk_state=latched)
        for strategy in (StrategyId.CORE, StrategyId.AI):
            with self.subTest(strategy=strategy):
                result = self.engine.evaluate(self.proposal(strategy), context)
                self.assertFalse(result.allowed)
                self.assertEqual(result.reason_code, "KILL_SWITCH_LATCHED")

    def test_new_action_is_blocked_before_ready_and_while_not_running(self):
        for status in (
            SessionStatus.START_REQUESTED, SessionStatus.PREFLIGHT,
            SessionStatus.RESTORING, SessionStatus.READY,
            SessionStatus.CHECKPOINTING, SessionStatus.CLOSED,
        ):
            with self.subTest(status=status):
                result = self.engine.evaluate(
                    self.proposal(), replace(self.context, session_status=status),
                )
                self.assertFalse(result.allowed)
                self.assertEqual(result.reason_code, "SESSION_NOT_READY")

    def test_missing_shared_risk_engine_fails_closed(self):
        context = replace(self.context, shared_risk_engine_available=False)
        result = self.engine.evaluate(self.proposal(), context)
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "RISK_ENGINE_UNAVAILABLE")

    def test_missing_risk_state_fails_closed(self):
        context = replace(self.context, risk_state=None)
        result = self.engine.evaluate(self.proposal(), context)
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "RISK_STATE_UNAVAILABLE")

    def test_unreconciled_paper_ledger_fails_closed(self):
        context = replace(self.context, ledger_reconciled=False)
        result = self.engine.evaluate(self.proposal(), context)
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "RISK_STATE_UNRECONCILED")

    def test_risk_state_from_another_account_scope_is_rejected(self):
        other = RiskState(
            account_scope_id="other-account", kill_switch_latched=False,
            kill_switch_reason=None, risk_policy_version="shared-risk-v1",
            reserved_margin_quote="0", aggregate_version=1,
        )
        result = self.engine.evaluate(self.proposal(), replace(self.context, risk_state=other))
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "RISK_SCOPE_MISMATCH")

    def test_exact_one_percent_order_margin_boundary_is_allowed(self):
        result = self.engine.evaluate(self.proposal(margin="10"), self.context)
        self.assertTrue(result.allowed)

    def test_order_margin_above_one_percent_of_equity_is_blocked(self):
        result = self.engine.evaluate(self.proposal(margin="10.0001"), self.context)
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "ORDER_MARGIN_CAP_EXCEEDED")

    def test_invalid_binary_float_or_nonpositive_risk_inputs_fail_closed(self):
        for margin in (10.0, "0", "-1", "NaN", "Infinity", None):
            with self.subTest(margin=margin):
                result = self.engine.evaluate(self.proposal(margin=margin), self.context)
                self.assertFalse(result.allowed)
                self.assertEqual(result.reason_code, "RISK_INPUT_INVALID")

    def test_reserved_margin_above_equity_blocks_unreconciled_capacity(self):
        overcommitted = RiskState(
            account_scope_id="paper-account", kill_switch_latched=False,
            kill_switch_reason=None, risk_policy_version="shared-risk-v1",
            reserved_margin_quote="1001", aggregate_version=5,
        )
        result = self.engine.evaluate(
            self.proposal(), replace(self.context, risk_state=overcommitted),
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "RISK_STATE_UNRECONCILED")

    def test_reducing_and_exit_proposals_still_pass_through_shared_engine(self):
        for action in ("REDUCE", "EXIT", "DCA", "ADD"):
            with self.subTest(action=action):
                result = self.engine.evaluate(
                    self.proposal(StrategyId.AI, action=action), self.context,
                )
                self.assertTrue(result.allowed, result.reason_code)


if __name__ == "__main__":
    unittest.main()
