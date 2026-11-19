import sqlite3
import tempfile
import unittest
from pathlib import Path

from paper_execution.ledger import PaperLedger
from paper_execution.risk_contract import provision_account_risk_contract


class AccountRiskContractTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "account.sqlite3"
        self.now = 1_800_000_000_000
        self.limits = {
            "maxDrawdownPct": "20",
            "maxDailyLossUsdt": "10",
            "maxExposureUsdt": "1000",
        }

    def provision(self, limits=None):
        return provision_account_risk_contract(
            self.path,
            limits or self.limits,
            source="ISOLATED_TEST_FIXTURE",
            recorded_at_ms=self.now,
        )

    def test_core_and_ai_ledgers_read_the_same_persisted_account_contract(self):
        self.provision()
        core = PaperLedger(
            self.path, strategy_id="STRATEGY_CORE",
            source_sha="a" * 40, require_risk_limits=True,
        )
        ai = PaperLedger(
            self.path, strategy_id="AI_FREQAI",
            source_sha="a" * 40, leverage="2",
            require_risk_limits=True,
        )

        self.assertEqual(core.risk_limits, ai.risk_limits)
        self.assertEqual(
            {key: str(value) for key, value in core.risk_limits.items()},
            self.limits,
        )

    def test_strategy_cannot_supply_or_override_account_risk_limits(self):
        self.provision()
        conflicting = {
            "maxDrawdownPct": "30",
            "maxDailyLossUsdt": "15",
            "maxExposureUsdt": "1200",
        }

        with self.assertRaisesRegex(
            ValueError, "ACCOUNT_RISK_CONTRACT_CALLER_LIMITS_FORBIDDEN"
        ):
            PaperLedger(
                self.path, strategy_id="STRATEGY_CORE",
                source_sha="a" * 40, risk_limits=conflicting,
                require_risk_limits=True,
            )

    def test_required_account_contract_missing_fails_closed(self):
        with self.assertRaisesRegex(
            sqlite3.DatabaseError, "ACCOUNT_RISK_CONTRACT_UNAVAILABLE"
        ):
            PaperLedger(
                self.path, strategy_id="STRATEGY_CORE",
                source_sha="a" * 40, require_risk_limits=True,
            )

    def test_existing_account_contract_cannot_be_silently_replaced(self):
        self.provision()
        conflicting = {
            "maxDrawdownPct": "30",
            "maxDailyLossUsdt": "15",
            "maxExposureUsdt": "1200",
        }

        with self.assertRaisesRegex(
            (ValueError, sqlite3.DatabaseError), "ACCOUNT_RISK_CONTRACT_CONFLICT"
        ):
            self.provision(conflicting)

        reopened = PaperLedger(
            self.path, strategy_id="STRATEGY_CORE",
            source_sha="a" * 40, require_risk_limits=True,
        )
        self.assertEqual(
            {key: str(value) for key, value in reopened.risk_limits.items()},
            self.limits,
        )

    def test_contract_tampering_is_detected_before_ledger_admission(self):
        self.provision()
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """UPDATE paper_account_risk_contract
                   SET limits_json=? WHERE account_id=1""",
                ('{"maxDailyLossUsdt":"10","maxDrawdownPct":"20","maxExposureUsdt":"1"}',),
            )

        with self.assertRaisesRegex(
            sqlite3.DatabaseError, "ACCOUNT_RISK_CONTRACT_INVALID"
        ):
            PaperLedger(
                self.path, strategy_id="STRATEGY_CORE",
                source_sha="a" * 40, require_risk_limits=True,
            )


if __name__ == "__main__":
    unittest.main()
