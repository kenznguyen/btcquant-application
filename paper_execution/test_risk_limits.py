import sqlite3
import tempfile
import unittest
from pathlib import Path

from paper_execution.ledger import PaperLedger
from paper_execution.risk_contract import provision_account_risk_contract, read_account_risk_contract, update_account_risk_contract


class SharedRiskLimitTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/"paper.sqlite3"
        self.now=1_800_000_000_000
        self.limits={"maxDrawdownPct":20,"maxDailyLossUsdt":10,"maxExposureUsdt":1000}
        provision_account_risk_contract(
            self.path, self.limits, source="RISK_LIMIT_TEST_FIXTURE", recorded_at_ms=self.now
        )
        self.ledger=PaperLedger(self.path,max_position_base="1",require_risk_limits=True)

    def update_limits(self, limits):
        contract = read_account_risk_contract(self.path)
        update_account_risk_contract(
            self.path, limits, expected_contract_hash=contract["contractHash"],
            source="RISK_LIMIT_TEST_FIXTURE", reason="Change account risk limits for regression case",
            recorded_at_ms=self.now + 1,
        )

    def intent(self,name="risk-order",target="0.1"):
        return {"intentId":name,"symbol":"BTCUSDT","exchange":"binance","marketType":"USDT_PERPETUAL",
            "strategyVersion":"test","modelVersion":"test","datasetVersion":"sha256:"+"a"*64,
            "targetPositionBase":target,"limitPrice":"100","decisionAtMs":self.now,
            "validUntilMs":self.now+20_000,"inputSnapshotId":"sha256:"+"b"*64,"mode":"PAPER"}

    def book(self,at):
        return {"source":"hummingbot","connector":"binance_perpetual","symbol":"BTCUSDT","observedAtMs":at,
            "bids":[{"price":"99.9","quantity":"10"}],"asks":[{"price":"100","quantity":"10"}]}

    def mark(self,at,realized="0"):
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE paper_state SET realized=? WHERE id=1",(realized,))
        return self.ledger.record_equity("100",at,at,"sha256:"+"c"*64)

    def test_max_drawdown_breach_latches_kill_and_rejects_new_intent(self):
        self.mark(self.now)
        self.mark(self.now+900_000,realized="-25")
        result=self.ledger.submit(self.intent(),self.book(self.now+900_000),self.now+900_000)
        self.assertEqual(result["reason"],"MAX_DRAWDOWN_LIMIT")
        self.assertTrue(self.ledger.snapshot()["riskControl"]["killed"])
        self.assertEqual(self.ledger.snapshot()["riskControl"]["reason"],"MAX_DRAWDOWN_LIMIT")

    def test_daily_loss_breach_latches_kill(self):
        limits={**self.limits,"maxDrawdownPct":90}
        self.update_limits(limits)
        ledger=PaperLedger(self.path,max_position_base="1",require_risk_limits=True)
        ledger.record_equity("100",self.now,self.now,"sha256:"+"c"*64)
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE paper_state SET realized='-12' WHERE id=1")
        ledger.record_equity("100",self.now+900_000,self.now+900_000,"sha256:"+"d"*64)
        result=ledger.submit(self.intent("daily-loss"),self.book(self.now+900_000),self.now+900_000)
        self.assertEqual(result["reason"],"DAILY_LOSS_LIMIT")
        self.assertTrue(ledger.snapshot()["riskControl"]["killed"])

    def test_exposure_limit_rejects_without_latching_global_kill(self):
        limits={**self.limits,"maxExposureUsdt":5}
        self.update_limits(limits)
        ledger=PaperLedger(self.path,max_position_base="1",require_risk_limits=True)
        ledger.record_equity("100",self.now,self.now,"sha256:"+"c"*64)
        result=ledger.submit(self.intent("exposure"),self.book(self.now),self.now)
        self.assertEqual(result["reason"],"MAX_EXPOSURE_LIMIT")
        self.assertFalse(ledger.snapshot()["riskControl"]["killed"])

    def test_missing_limits_fail_closed(self):
        missing_path = Path(self.temp.name) / "missing.sqlite3"
        ledger = PaperLedger(missing_path, max_position_base="1", require_risk_limits=True)
        ledger.record_equity("100", self.now, self.now, "sha256:"+"c"*64)
        result = ledger.submit(self.intent("unconfigured"), self.book(self.now), self.now)
        self.assertEqual(result["reason"], "RISK_LIMITS_UNCONFIGURED")
        self.assertEqual(result["status"], "REJECTED")


if __name__=="__main__":
    unittest.main()
