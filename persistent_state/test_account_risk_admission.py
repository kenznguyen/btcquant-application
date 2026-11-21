import unittest
from dataclasses import FrozenInstanceError, replace

from persistent_state.account_risk import AccountRiskProvenance, AccountRiskSnapshot
from persistent_state.contracts import RiskState, SessionStatus, StrategyId
from persistent_state.risk_admission import RiskAdmissionContext, RiskProposal, SharedRiskEngine
from persistent_state.risk_policy import VersionedRiskPolicy


class AccountRiskAdmissionIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = AccountRiskSnapshot(
            snapshot_id="snapshot-001", schema_version=1,
            account_scope_id="paper-account", session_id="session-001",
            fencing_generation=7, generated_at_ms=10_000, as_of_ms=9_900,
            quote_asset="USDT", account_equity_quote="1000",
            gross_exposure_quote="200", reserved_margin_quote="50",
            drawdown_quote="20", daily_loss_quote="5",
            provenance=AccountRiskProvenance(
                provider_id="fixture-provider", source_id="fixture-source",
                source_snapshot_id="source-001", source_version="v1",
                source_payload_sha256="sha256:" + "a" * 64,
            ),
            verified=True, ledger_reconciled=True,
        )
        self.policy = VersionedRiskPolicy(
            version="risk-policy-test-v3", quote_asset="USDT",
            max_snapshot_age_ms=500,
            max_drawdown_quote="100", max_daily_loss_quote="30",
            max_gross_exposure_quote="500",
        )
        self.risk_state = RiskState(
            account_scope_id="paper-account", kill_switch_latched=False,
            kill_switch_reason=None, risk_policy_version=self.policy.version,
            reserved_margin_quote="50", aggregate_version=3,
        )
        self.context = RiskAdmissionContext(
            account_scope_id="paper-account", session_id="session-001",
            fencing_generation=7, session_status=SessionStatus.RUNNING,
            risk_state=self.risk_state, account_risk_snapshot=self.snapshot,
            risk_policy=self.policy, now_ms=10_100,
            shared_risk_engine_available=True,
        )
        self.engine = SharedRiskEngine()

    def proposal(self, *, strategy=StrategyId.CORE, margin="5", exposure="10", action="ENTRY"):
        return RiskProposal(
            proposal_id=f"{strategy.value.lower()}-proposal",
            account_scope_id="paper-account", strategy_id=strategy,
            action_kind=action, direction="LONG",
            requested_margin_quote=margin,
            requested_gross_exposure_quote=exposure,
        )

    def test_core_and_ai_share_same_verified_snapshot_and_policy(self):
        for strategy in (StrategyId.CORE, StrategyId.AI):
            result = self.engine.evaluate(self.proposal(strategy=strategy), self.context)
            self.assertTrue(result.allowed, result.reason_code)
            self.assertEqual(result.risk_policy_version, "risk-policy-test-v3")

    def test_snapshot_is_required_and_scope_session_and_fence_are_bound(self):
        for changed in (
            replace(self.context, account_risk_snapshot=None),
            replace(self.context, account_scope_id="other-account"),
            replace(self.context, session_id="other-session"),
            replace(self.context, fencing_generation=8),
        ):
            result = self.engine.evaluate(self.proposal(), changed)
            self.assertFalse(result.allowed)

    def test_unverified_or_unreconciled_snapshot_fails_closed(self):
        for snapshot in (
            replace(self.snapshot, verified=False),
            replace(self.snapshot, ledger_reconciled=False),
        ):
            result = self.engine.evaluate(
                self.proposal(), replace(self.context, account_risk_snapshot=snapshot),
            )
            self.assertFalse(result.allowed)

    def test_stale_or_future_snapshot_fails_closed(self):
        stale = replace(self.snapshot, as_of_ms=9_000)
        future = replace(self.snapshot, generated_at_ms=10_200, as_of_ms=10_100)
        for snapshot in (stale, future):
            result = self.engine.evaluate(
                self.proposal(), replace(self.context, account_risk_snapshot=snapshot),
            )
            self.assertFalse(result.allowed)

    def test_policy_version_and_quote_asset_must_match(self):
        mismatched_state = replace(self.risk_state, risk_policy_version="old-policy")
        wrong_asset = replace(self.policy, quote_asset="USD")
        for context in (
            replace(self.context, risk_state=mismatched_state),
            replace(self.context, risk_policy=wrong_asset),
        ):
            result = self.engine.evaluate(self.proposal(), context)
            self.assertFalse(result.allowed)

    def test_drawdown_policy_breach_blocks_new_exposure(self):
        snapshot = replace(self.snapshot, drawdown_quote="100.01")
        result = self.engine.evaluate(
            self.proposal(), replace(self.context, account_risk_snapshot=snapshot),
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "DRAWDOWN_LIMIT_EXCEEDED")

    def test_daily_loss_policy_breach_blocks_new_exposure(self):
        snapshot = replace(self.snapshot, daily_loss_quote="30.01")
        result = self.engine.evaluate(
            self.proposal(), replace(self.context, account_risk_snapshot=snapshot),
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "DAILY_LOSS_LIMIT_EXCEEDED")

    def test_gross_exposure_includes_requested_increment_without_netting(self):
        result = self.engine.evaluate(
            self.proposal(exposure="300.01"), self.context,
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "GROSS_EXPOSURE_LIMIT_EXCEEDED")

    def test_new_exposure_requires_exact_incremental_gross_exposure(self):
        result = self.engine.evaluate(
            self.proposal(exposure=None), self.context,
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason_code, "RISK_INPUT_INVALID")

    def test_reduce_and_exit_remain_available_when_new_exposure_limits_are_breached(self):
        snapshot = replace(
            self.snapshot, drawdown_quote="101", daily_loss_quote="31",
            gross_exposure_quote="600",
        )
        context = replace(self.context, account_risk_snapshot=snapshot)
        for action in ("REDUCE", "EXIT"):
            result = self.engine.evaluate(
                self.proposal(action=action, exposure=None), context,
            )
            self.assertTrue(result.allowed, result.reason_code)

    def test_policy_accepts_exact_decimal_limits_and_rejects_noncanonical_values(self):
        policy = VersionedRiskPolicy(
            version="decimal-policy-v1", quote_asset="USDT",
            max_snapshot_age_ms=500, max_drawdown_quote="100.25",
            max_daily_loss_quote="30.5", max_gross_exposure_quote="500.125",
        )
        self.assertEqual(policy.max_drawdown_quote, "100.25")
        for invalid in ("-1", "01", "1e2", "NaN", 1.5):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    VersionedRiskPolicy(
                        version="bad-policy", quote_asset="USDT",
                        max_snapshot_age_ms=500, max_drawdown_quote=invalid,
                        max_daily_loss_quote="30", max_gross_exposure_quote="500",
                    )

    def test_exact_risk_limit_boundaries_are_admitted(self):
        snapshot = replace(
            self.snapshot, drawdown_quote="100", daily_loss_quote="30",
            gross_exposure_quote="490",
        )
        context = replace(self.context, account_risk_snapshot=snapshot)
        result = self.engine.evaluate(self.proposal(exposure="10"), context)
        self.assertTrue(result.allowed, result.reason_code)

    def test_snapshot_at_exact_freshness_boundary_is_admitted(self):
        snapshot = replace(self.snapshot, as_of_ms=9_600)
        result = self.engine.evaluate(
            self.proposal(), replace(self.context, account_risk_snapshot=snapshot),
        )
        self.assertTrue(result.allowed, result.reason_code)

    def test_policy_requires_explicit_versioned_thresholds_and_is_immutable(self):
        with self.assertRaises((TypeError, ValueError)):
            VersionedRiskPolicy(
                version="", quote_asset="USDT", max_snapshot_age_ms=500,
                max_drawdown_quote="100", max_daily_loss_quote="30",
                max_gross_exposure_quote="500",
            )
        with self.assertRaises(FrozenInstanceError):
            self.policy.version = "mutated"


if __name__ == "__main__":
    unittest.main()
