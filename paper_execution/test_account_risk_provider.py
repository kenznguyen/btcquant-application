import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from paper_execution.versioned_risk_policy_store import (
    initialize_risk_policy_schema,
    publish_versioned_risk_policy,
)
from persistent_state.account_risk import PaperAccountBinding, AccountRiskSnapshot
from persistent_state.risk_policy import VersionedRiskPolicy


NOW = 1_800_000_000_000
POLICY = {
    "schemaVersion": 1,
    "policyVersion": "paper-risk-provider-v1",
    "quoteAsset": "USDT",
    "maxSnapshotAgeMs": 30_000,
    "drawdownLimit": {"mode": "ABSOLUTE_QUOTE", "value": "100"},
    "maxDailyLossQuote": "50",
    "maxGrossExposureQuote": "2000",
}


class SQLitePaperAccountRiskProviderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.paper_db = Path(self.temp.name) / "paper.sqlite3"
        with sqlite3.connect(self.paper_db) as db:
            db.execute("CREATE TABLE provider_fixture (id INTEGER PRIMARY KEY)")
            initialize_risk_policy_schema(
                db, source_sha="a" * 40, applied_at_ms=NOW - 500
            )
            raw = json.dumps(POLICY, sort_keys=True, separators=(",", ":"))
            publish_versioned_risk_policy(
                db, raw, expected_active_hash=None,
                source_git_commit_sha="b" * 40,
                source_policy_path="config/risk_policies/paper-risk-provider-v1.json",
                source_policy_sha256=hashlib.sha256(raw.encode()).hexdigest(),
                operator_id="operator:test", reason="provider fixture",
                published_at_ms=NOW - 400,
            )
        self.binding = PaperAccountBinding(
            account_id=1, account_mode="PAPER", account_scope_id="paper-account",
            session_id="session-1", fencing_generation=7,
        )
        self.raw = {
            "mode": "PAPER", "liveTradingSupported": False, "available": True,
            "riskReady": True, "accountEquityQuote": "1000",
            "grossExposureQuote": "250", "reservedMarginQuote": "20",
            "maxDrawdownUsdt": "30", "dailyLossUsdt": "10",
            "markObservedAtMs": NOW - 1_000,
            "datasetVersion": "sha256:" + "c" * 64,
            "markProvenance": {
                "sourceId": "T0_CANONICAL_MARKET_DATA",
                "sourceSnapshotId": "sha256:" + "c" * 64,
                "sourceVersion": "sha256:" + "c" * 64,
                "sourcePayloadSha256": "sha256:" + "d" * 64,
            },
        }
        self.state_repository = object()
        from paper_execution.account_risk_provider import SQLitePaperAccountRiskSnapshotProvider
        self.provider = SQLitePaperAccountRiskSnapshotProvider(
            self.paper_db, self.state_repository, clock=lambda: NOW
        )

    def run_provider(self, *, raw=None, bindings=None):
        from paper_execution.account_risk_provider import SQLitePaperAccountRiskSnapshotProvider
        provider = SQLitePaperAccountRiskSnapshotProvider(
            self.paper_db, self.state_repository, clock=lambda: NOW
        )
        values = [self.binding, self.binding] if bindings is None else bindings
        with patch(
            "paper_execution.account_scope_binding.resolve_paper_account_binding",
            side_effect=values,
        ) as resolve, patch(
            "paper_execution.ledger._read_account_risk_snapshot_connection",
            side_effect=lambda db, now_ms: self.assert_read_only_snapshot(db, raw or self.raw),
        ):
            result = provider.read_bundle(
                account_scope_id="paper-account", session_id="session-1",
                fencing_generation=7,
            )
        self.assertEqual(resolve.call_count, 2)
        return result

    def assert_read_only_snapshot(self, db, value):
        self.assertEqual(db.execute("PRAGMA query_only").fetchone()[0], 1)
        self.assertTrue(db.in_transaction)
        return value

    def test_provider_returns_typed_snapshot_and_versioned_policy_from_one_read_transaction(self):
        bundle = self.run_provider()
        self.assertIsInstance(bundle.snapshot, AccountRiskSnapshot)
        self.assertIsInstance(bundle.policy, VersionedRiskPolicy)
        self.assertEqual(bundle.snapshot.account_scope_id, "paper-account")
        self.assertEqual(bundle.snapshot.session_id, "session-1")
        self.assertEqual(bundle.snapshot.fencing_generation, 7)
        self.assertTrue(bundle.snapshot.verified)
        self.assertTrue(bundle.snapshot.ledger_reconciled)
        self.assertEqual(bundle.snapshot.account_equity_quote, "1000")
        self.assertEqual(bundle.snapshot.gross_exposure_quote, "250")
        self.assertEqual(bundle.snapshot.reserved_margin_quote, "20")
        self.assertEqual(bundle.snapshot.drawdown_quote, "30")
        self.assertEqual(bundle.snapshot.daily_loss_quote, "10")
        self.assertEqual(bundle.policy.version, "paper-risk-provider-v1")
        self.assertEqual(bundle.policy.max_snapshot_age_ms, 30_000)
        self.assertEqual(bundle.policy.max_drawdown_quote, "100")
        self.assertEqual(bundle.binding, self.binding)

    def test_provider_protocol_read_snapshot_returns_only_verified_snapshot(self):
        with patch(
            "paper_execution.account_scope_binding.resolve_paper_account_binding",
            side_effect=[self.binding, self.binding],
        ), patch(
            "paper_execution.ledger._read_account_risk_snapshot_connection",
            side_effect=lambda db, now_ms: self.assert_read_only_snapshot(db, self.raw),
        ):
            snapshot = self.provider.read_snapshot(
                account_scope_id="paper-account", session_id="session-1",
                fencing_generation=7,
            )
        self.assertIsInstance(snapshot, AccountRiskSnapshot)
        self.assertTrue(snapshot.verified)

    def test_provider_fails_closed_when_ledger_is_not_risk_ready(self):
        with self.assertRaisesRegex(sqlite3.DatabaseError, "ACCOUNT_RISK_NOT_READY"):
            self.run_provider(raw={**self.raw, "riskReady": False})

    def test_provider_fails_closed_when_source_provenance_is_mismatched(self):
        bad = {**self.raw, "markProvenance": {
            **self.raw["markProvenance"], "sourceSnapshotId": "sha256:" + "e" * 64,
        }}
        with self.assertRaisesRegex(sqlite3.DatabaseError, "ACCOUNT_RISK_PROVENANCE_INVALID"):
            self.run_provider(raw=bad)

    def test_provider_fails_closed_when_mark_is_from_the_future(self):
        future = {**self.raw, "markObservedAtMs": NOW + 1}
        with self.assertRaisesRegex(sqlite3.DatabaseError, "ACCOUNT_RISK_MARK_TIME_INVALID"):
            self.run_provider(raw=future)

    def test_provider_fails_closed_when_session_fence_changes_during_read(self):
        newer = PaperAccountBinding(
            account_id=1, account_mode="PAPER", account_scope_id="paper-account",
            session_id="session-2", fencing_generation=8,
        )
        with self.assertRaisesRegex(ValueError, "PAPER_SESSION_FENCE_CHANGED_DURING_SNAPSHOT"):
            self.run_provider(bindings=[self.binding, newer])

    def test_provider_fails_closed_when_active_policy_is_missing(self):
        with sqlite3.connect(self.paper_db) as db:
            db.execute("DROP TRIGGER paper_risk_policy_active_no_delete")
            db.execute("DELETE FROM paper_risk_policy_active WHERE account_id=1")
        with patch(
            "paper_execution.account_scope_binding.resolve_paper_account_binding",
            side_effect=[self.binding, self.binding],
        ), patch(
            "paper_execution.ledger._read_account_risk_snapshot_connection",
            side_effect=lambda db, now_ms: self.assert_read_only_snapshot(db, self.raw),
        ):
            with self.assertRaisesRegex(sqlite3.DatabaseError, "RISK_POLICY_ACTIVE_UNAVAILABLE"):
                self.provider.read_bundle(
                    account_scope_id="paper-account", session_id="session-1",
                    fencing_generation=7,
                )


if __name__ == "__main__":
    unittest.main()
