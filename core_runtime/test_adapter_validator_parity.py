"""Composition tests for the Core producer adapter and canonical validator."""

import unittest

from core_runtime.adapter import producer_report_to_signal
from pipeline.core_signal import validate


NOW_MS = 2_000


def producer_report(action, intent_action=None, *, decision_at=1_000, valid_until=31_000,
                    target=None, symbol="BTCUSDT"):
    intent_action = intent_action or {
        "BUY": "LONG", "SELL": "SHORT", "CLOSE": "FLAT"
    }.get(action)
    if intent_action is None:
        return {"action": "WAIT", "reason": "CORE_NO_ENTRY", "intent": None}
    if target is None:
        target = {"LONG": "0.01", "SHORT": "-0.01", "FLAT": "0"}[intent_action]
    return {
        "action": action,
        "reason": "fixture-reason",
        "intent": {
            "schemaVersion": 1,
            "source": "STRATEGY_CORE",
            "exchange": "binance",
            "marketType": "USDT_PERPETUAL",
            "symbol": symbol,
            "timeframe": "15m",
            "action": intent_action,
            "strategyVersion": "rsi-adx-smart-dca-v1",
            "datasetVersion": "dataset-1",
            "inputSnapshotId": "snapshot-1",
            "decisionAtMs": decision_at,
            "validUntilMs": valid_until,
            "targetPositionBase": target,
            "limitPrice": "50000",
        },
    }


class CoreAdapterValidatorParityTest(unittest.TestCase):
    def test_buy_sell_and_close_survive_canonical_validation(self):
        expected = (("BUY", "BUY"), ("SELL", "SELL"), ("CLOSE", "CLOSE"))
        for producer_action, canonical_action in expected:
            with self.subTest(action=producer_action):
                adapted = producer_report_to_signal(producer_report(producer_action))
                result = validate(adapted, NOW_MS)
                self.assertEqual(result["action"], canonical_action)
                self.assertIsNotNone(result["intent"])
                self.assertEqual(result["source"], "STRATEGY_CORE")
                self.assertEqual(result["intent"]["symbol"], "BTCUSDT")
                self.assertEqual(result["intent"]["datasetVersion"], "dataset-1")
                self.assertEqual(result["intent"]["inputSnapshotId"], "snapshot-1")
                self.assertEqual(result["intent"]["mode"], "PAPER")

    def test_wait_remains_non_intent_through_canonical_validation(self):
        adapted = producer_report_to_signal(producer_report("WAIT"))
        result = validate(adapted, NOW_MS)
        self.assertEqual(result["action"], "WAIT")
        self.assertIsNone(result["intent"])
        self.assertEqual(result["reason"], "CORE_NO_ENTRY")

    def test_expired_producer_intent_is_denied_by_canonical_validator(self):
        adapted = producer_report_to_signal(
            producer_report("BUY", decision_at=1_000, valid_until=1_999)
        )
        result = validate(adapted, NOW_MS)
        self.assertEqual(result["action"], "WAIT")
        self.assertIsNone(result["intent"])

    def test_wrong_market_is_denied_by_canonical_validator(self):
        adapted = producer_report_to_signal(producer_report("BUY", symbol="ETHUSDT"))
        result = validate(adapted, NOW_MS)
        self.assertEqual(result["action"], "WAIT")
        self.assertIsNone(result["intent"])


if __name__ == "__main__":
    unittest.main()
