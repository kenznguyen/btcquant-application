import io
import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from paper_execution.ledger import PaperLedger


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

    def test_authoritative_account_risk_not_ready_blocks_reset_preflight(self):
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

    def test_direct_reset_rechecks_account_risk_inside_write_transaction(self):
        def not_ready(connection, *, now_ms):
            self.assertTrue(connection.in_transaction)
            return {"riskReady": False}

        with patch("paper_execution.ledger._dual_ledger_migrations_ready", return_value=True), \
             patch("paper_execution.ledger._read_account_risk_snapshot_connection",
                   side_effect=not_ready):
            with self.assertRaisesRegex(ValueError, "ACCOUNT_RISK_NOT_READY"):
                self.ledger.reset_kill(True, True, self.now + 1)

        self.assertTrue(self.ledger.snapshot()["riskControl"]["killed"])

    def test_missing_kill_latch_state_blocks_reset_without_audit(self):
        with sqlite3.connect(self.path) as connection:
            connection.execute("DELETE FROM paper_risk_control")
            before = connection.execute(
                "SELECT COUNT(*) FROM paper_audit WHERE kind='KILL_SWITCH_RESET'"
            ).fetchone()[0]

        with patch("paper_execution.ledger._dual_ledger_migrations_ready", return_value=True), \
             patch("paper_execution.ledger._read_account_risk_snapshot_connection",
                   return_value={"riskReady": True}):
            with self.assertRaisesRegex(sqlite3.DatabaseError, "RISK_CONTROL_STATE_UNAVAILABLE"):
                self.ledger.reset_kill(True, True, self.now + 1)

        with sqlite3.connect(self.path) as connection:
            after = connection.execute(
                "SELECT COUNT(*) FROM paper_audit WHERE kind='KILL_SWITCH_RESET'"
            ).fetchone()[0]
            self.assertEqual(after, before)
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM paper_risk_control").fetchone()[0],
                0,
            )

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
        def ready_in_transaction(connection, *, now_ms):
            self.assertTrue(connection.in_transaction)
            return {"riskReady": True}

        with patch("paper_execution.ledger._dual_ledger_migrations_ready", return_value=True), \
             patch("paper_execution.ledger._read_account_risk_snapshot_connection",
                   side_effect=ready_in_transaction):
            with self.assertRaisesRegex(sqlite3.IntegrityError, "AUDIT_WRITE_REJECTED"):
                self.ledger.reset_kill(True, True, self.now + 1)
        self.assertTrue(self.ledger.snapshot()["riskControl"]["killed"])
