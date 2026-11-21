import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pipeline import api
from paper_execution.ledger import PaperLedger


class RiskPolicyEnvironmentProvisioningTests(unittest.TestCase):
    def test_environment_thresholds_never_create_or_override_persisted_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            db_path = Path(directory) / "paper.sqlite3"
            PaperLedger(db_path)
            with patch.dict(
                os.environ,
                {
                    "PAPER_DB": str(db_path),
                    "PAPER_MAX_DRAWDOWN_PCT": "1",
                    "PAPER_MAX_DAILY_LOSS_USDT": "1",
                    "PAPER_MAX_EXPOSURE_USDT": "1",
                },
                clear=True,
            ):
                ledger = api.ledger()
            self.assertIsNone(ledger.risk_limits)
            with sqlite3.connect(db_path) as connection:
                self.assertIsNone(connection.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' "
                    "AND name='paper_account_risk_contract'"
                ).fetchone())
                self.assertIsNone(connection.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' "
                    "AND name='paper_risk_policy_versions'"
                ).fetchone())


if __name__ == "__main__":
    unittest.main()
