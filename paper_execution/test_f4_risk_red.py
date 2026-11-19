import io
import json
import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from paper_execution.ledger import PaperLedger
from paper_execution.risk_contract import provision_account_risk_contract
from paper_execution import risk_control


class F4RiskContractRedTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "account.sqlite3"
        self.now = 1_800_000_000_000

    def test_core_and_ai_cannot_supply_conflicting_limits_for_one_account(self):
        PaperLedger(self.path, max_position_base="1")
        core_limits = {
            "maxDrawdownPct": "20",
            "maxDailyLossUsdt": "10",
            "maxExposureUsdt": "1000",
        }
        ai_limits = {
            "maxDrawdownPct": "30",
            "maxDailyLossUsdt": "15",
            "maxExposureUsdt": "1200",
        }
        bootstrap = PaperLedger(self.path, max_position_base="1")
        bootstrap.record_equity(
            "100", self.now - 60_000, self.now, "sha256:f4-risk-seed", "100"
        )
        provision_account_risk_contract(
            self.path, core_limits, source="F4_R1_REGRESSION_FIXTURE",
            recorded_at_ms=self.now,
        )
        PaperLedger(
            self.path, strategy_id="STRATEGY_CORE", source_sha="a" * 40,
            require_risk_limits=True,
        )
        with self.assertRaisesRegex(
            (ValueError, sqlite3.DatabaseError), "ACCOUNT_RISK_CONTRACT"
        ):
            PaperLedger(
                self.path, strategy_id="AI_FREQAI", source_sha="a" * 40,
                leverage="2", risk_limits=ai_limits, require_risk_limits=True,
            )


class F4KillSwitchFailClosedRedTest(unittest.TestCase):
    def test_missing_kill_switch_table_is_not_treated_as_unlatched(self):
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)

        with self.assertRaisesRegex(
            sqlite3.DatabaseError, "RISK_CONTROL_STATE_UNAVAILABLE"
        ):
            risk_control.risk_block_reason(connection)

    def test_malformed_unlatched_row_is_rejected(self):
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        connection.execute("""
            CREATE TABLE paper_risk_control (
                id INTEGER PRIMARY KEY,
                paused,
                killed,
                reason TEXT,
                updated_at_ms
            )
        """)
        connection.execute(
            "INSERT INTO paper_risk_control VALUES (1, 0, 0, NULL, 'not-a-timestamp')"
        )

        with self.assertRaisesRegex(
            sqlite3.DatabaseError, "RISK_CONTROL_STATE_INVALID"
        ):
            risk_control.risk_block_reason(connection)

    def test_missing_kill_switch_state_row_is_rejected(self):
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        connection.execute("""
            CREATE TABLE paper_risk_control (
                id INTEGER PRIMARY KEY,
                paused INTEGER NOT NULL,
                killed INTEGER NOT NULL,
                reason TEXT,
                updated_at_ms INTEGER NOT NULL
            )
        """)

        with self.assertRaisesRegex(
            sqlite3.DatabaseError, "RISK_CONTROL_STATE_UNAVAILABLE"
        ):
            risk_control.risk_block_reason(connection)

    def test_non_boolean_pause_flag_is_rejected(self):
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        connection.execute("""
            CREATE TABLE paper_risk_control (
                id INTEGER PRIMARY KEY,
                paused,
                killed,
                reason,
                updated_at_ms
            )
        """)
        connection.execute(
            "INSERT INTO paper_risk_control VALUES (1, 2, 0, NULL, 1800000000000)"
        )

        with self.assertRaisesRegex(
            sqlite3.DatabaseError, "RISK_CONTROL_STATE_INVALID"
        ):
            risk_control.risk_block_reason(connection)

    def test_non_boolean_kill_flag_is_rejected(self):
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        connection.execute("""
            CREATE TABLE paper_risk_control (
                id INTEGER PRIMARY KEY,
                paused,
                killed,
                reason,
                updated_at_ms
            )
        """)
        connection.execute(
            "INSERT INTO paper_risk_control VALUES (1, 0, 2, NULL, 1800000000000)"
        )

        with self.assertRaisesRegex(
            sqlite3.DatabaseError, "RISK_CONTROL_STATE_INVALID"
        ):
            risk_control.risk_block_reason(connection)

    def test_text_pause_flag_is_rejected(self):
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        connection.execute("""
            CREATE TABLE paper_risk_control (
                id INTEGER PRIMARY KEY,
                paused,
                killed,
                reason,
                updated_at_ms
            )
        """)
        connection.execute(
            "INSERT INTO paper_risk_control VALUES (1, 'false', 0, NULL, 1800000000000)"
        )

        with self.assertRaisesRegex(
            sqlite3.DatabaseError, "RISK_CONTROL_STATE_INVALID"
        ):
            risk_control.risk_block_reason(connection)

    def test_text_kill_flag_is_rejected(self):
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        connection.execute("""
            CREATE TABLE paper_risk_control (
                id INTEGER PRIMARY KEY,
                paused,
                killed,
                reason,
                updated_at_ms
            )
        """)
        connection.execute(
            "INSERT INTO paper_risk_control VALUES (1, 0, 'false', NULL, 1800000000000)"
        )

        with self.assertRaisesRegex(
            sqlite3.DatabaseError, "RISK_CONTROL_STATE_INVALID"
        ):
            risk_control.risk_block_reason(connection)


class F4KillResetAtomicReadinessRedTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "reset.sqlite3"
        self.now = 1_800_000_000_000
        self.ledger = PaperLedger(self.path)
        self.ledger.set_killed(True, self.now, "TEST_KILL")

    def test_direct_reset_rejects_forged_ready_true_without_account_readiness(self):
        with self.assertRaisesRegex(
            (ValueError, sqlite3.DatabaseError), "ACCOUNT_RISK_NOT_READY"
        ):
            self.ledger.reset_kill(True, True, self.now + 1)
        self.assertTrue(self.ledger.snapshot()["riskControl"]["killed"])

    def test_reset_rejects_pending_orders_even_when_caller_claims_ready(self):
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                "INSERT INTO paper_orders VALUES (?,?,?,?,?)",
                ("pending-intent", "payload-hash", "pending-order", "OPEN",
                 json.dumps({"intentId": "pending-intent", "status": "OPEN"})),
            )
        with self.assertRaisesRegex(
            (ValueError, sqlite3.DatabaseError), "PENDING_PAPER_ORDERS"
        ):
            self.ledger.reset_kill(True, True, self.now + 1)
        self.assertTrue(self.ledger.snapshot()["riskControl"]["killed"])

    def test_legacy_readiness_fallback_does_not_promote_missing_cutover_to_ready(self):
        from pipeline import api

        class LegacyLedger:
            def snapshot(self):
                return {"orders": []}

        with patch.dict(os.environ, {"MARKET_DATA_DB": str(self.path)}), \
             patch.object(api, "context", return_value={
                 "candles": {"coverage": {"complete": True}}, "book": {"observedAtMs": self.now},
             }), \
             patch("paper_execution.ledger.dual_ledger_ready", return_value=False), \
             patch.object(api, "ledger", return_value=LegacyLedger()):
            readiness = api.control_readiness(self.now)
        self.assertFalse(readiness["checks"]["accountRiskReady"])
        self.assertFalse(readiness["ready"])

    def test_missing_account_cutover_is_not_ready_even_with_dual_schema(self):
        from pipeline import api

        with patch.dict(os.environ, {"MARKET_DATA_DB": str(self.path)}), \
             patch.object(api, "context", return_value={
                 "candles": {"coverage": {"complete": True}}, "book": {"observedAtMs": self.now},
             }), \
             patch("paper_execution.ledger.dual_ledger_ready", return_value=True), \
             patch("paper_execution.ledger.read_snapshot", return_value={}), \
             patch("paper_execution.ledger.has_pending_orders", return_value=False), \
             patch("paper_execution.ledger.read_account_risk_snapshot",
                   return_value={"riskReady": False}):
            readiness = api.control_readiness(self.now)
        self.assertFalse(readiness["checks"]["accountRiskReady"])
        self.assertFalse(readiness["ready"])

    def test_api_rechecks_readiness_after_stale_preflight_before_clearing_kill(self):
        from pipeline import api

        def stale_readiness(_timestamp):
            with sqlite3.connect(self.path) as connection:
                connection.execute(
                    "INSERT INTO paper_orders VALUES (?,?,?,?,?)",
                    ("raced-intent", "raced-hash", "raced-order", "OPEN",
                     json.dumps({"intentId": "raced-intent", "status": "OPEN"})),
                )
            return {"ready": True, "checks": {
                "closedCandles": True, "orderBook": True,
                "noPendingPaperOrders": True, "accountRiskReady": True,
            }}

        raw = json.dumps({"acknowledge": True}).encode()
        environ = {
            "PATH_INFO": "/v1/paper/reset-kill", "REQUEST_METHOD": "POST",
            "HTTP_AUTHORIZATION": "Bearer control-token",
            "CONTENT_LENGTH": str(len(raw)), "wsgi.input": io.BytesIO(raw),
        }
        statuses = []
        with patch.dict(os.environ, {
                "MARKET_DATA_DB": str(self.path), "CONTROL_TOKEN": "control-token",
                "MARKET_DATA_TOKEN": "read-token",
            }), \
             patch.object(api, "now_ms", return_value=self.now + 1), \
             patch.object(api, "control_permit", return_value=True), \
             patch.object(api, "control_readiness", side_effect=stale_readiness), \
             patch.object(api, "ledger", return_value=self.ledger):
            body = b"".join(api.application(
                environ, lambda status, headers: statuses.append(status)
            ))
        response = json.loads(body)
        self.assertEqual(statuses[0].split()[0], "409")
        self.assertEqual(response.get("error"), "SYSTEM_NOT_READY")
        self.assertTrue(self.ledger.snapshot()["riskControl"]["killed"])

    def test_audit_failure_rolls_back_kill_latch_clear_atomically(self):
        with sqlite3.connect(self.path) as connection:
            connection.execute("""
                CREATE TRIGGER reject_kill_reset_audit
                BEFORE INSERT ON paper_audit
                WHEN NEW.kind='KILL_SWITCH_RESET'
                BEGIN SELECT RAISE(ABORT, 'AUDIT_WRITE_REJECTED'); END
            """)
        with self.assertRaisesRegex(sqlite3.IntegrityError, "AUDIT_WRITE_REJECTED"):
            self.ledger.reset_kill(True, True, self.now + 1)
        self.assertTrue(self.ledger.snapshot()["riskControl"]["killed"])


if __name__ == "__main__":
    unittest.main()
