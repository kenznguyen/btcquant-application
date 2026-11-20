import copy
import unittest

from persistent_state.preflight import (
    M15_MAX_LAG_MS, H1_MAX_LAG_MS, validate_market_data_preflight,
)


AS_OF = 1_800_000_000_000
INTERVALS = {"15m": 900_000, "1h": 3_600_000}


def make_snapshot(timeframe, *, count=3, as_of=AS_OF, latest_lag_periods=1):
    interval = INTERVALS[timeframe]
    latest_close = as_of - (latest_lag_periods - 1) * interval
    start = latest_close - count * interval
    candles = []
    for index in range(count):
        opening = start + index * interval
        close = opening + interval
        candles.append({
            "exchange": "binance", "marketType": "USDT_PERPETUAL",
            "symbol": "BTCUSDT", "timeframe": timeframe,
            "openTimeMs": opening, "closeTimeMs": close,
            "open": "100", "high": "102", "low": "99", "close": "101",
            "volume": "2.5", "isClosed": True,
            "availableAtMs": close,
            "availabilityKind": "FIRST_OBSERVED",
            "quality": "VALIDATED", "source": "ccxt.binanceusdm",
        })
    end = candles[-1]["closeTimeMs"]
    return {
        "exchange": "binance", "marketType": "USDT_PERPETUAL",
        "symbol": "BTCUSDT", "timeframe": timeframe,
        "source": "ccxt.binanceusdm", "asOfMs": as_of,
        "startMs": start, "endMs": end,
        "datasetVersion": "sha256:" + ("a" if timeframe == "15m" else "b") * 64,
        "candles": candles,
        "coverage": {"expected": count, "returned": count, "complete": True, "gaps": []},
    }


class MarketDataPreflightTests(unittest.TestCase):
    def setUp(self):
        self.m15 = make_snapshot("15m")
        self.h1 = make_snapshot("1h")
        self.required = {"15m": 3, "1h": 3}

    def validate(self, *, m15=None, h1=None, as_of=AS_OF, required=None):
        return validate_market_data_preflight(
            self.m15 if m15 is None else m15,
            self.h1 if h1 is None else h1,
            as_of_ms=as_of,
            required_lookback=self.required if required is None else required,
        )

    def test_accepts_aligned_complete_closed_m15_h1_snapshots(self):
        result = self.validate()
        self.assertEqual(result.status, "READY")
        self.assertEqual(result.reasons, ())
        self.assertTrue(result.snapshot_id.startswith("sha256:"))
        self.assertEqual(result.as_of_ms, AS_OF)
        self.assertEqual(result.dataset_versions_json.count("sha256:"), 2)

    def test_uses_approved_timeframe_freshness_limits(self):
        self.assertEqual(M15_MAX_LAG_MS, 20 * 60_000)
        self.assertEqual(H1_MAX_LAG_MS, 70 * 60_000)
        m15 = make_snapshot("15m", latest_lag_periods=3)
        h1 = make_snapshot("1h", latest_lag_periods=3)
        self.assertEqual(self.validate(m15=m15).status, "BLOCKED_PREFLIGHT")
        self.assertEqual(self.validate(h1=h1).status, "BLOCKED_PREFLIGHT")

    def test_blocks_mismatched_common_as_of_boundary(self):
        h1 = make_snapshot("1h", as_of=AS_OF - 1)
        result = self.validate(h1=h1)
        self.assertEqual(result.status, "BLOCKED_PREFLIGHT")
        self.assertIn("SNAPSHOT_AS_OF_MISMATCH", result.reasons)

    def test_blocks_unapproved_source_and_cross_timeframe_source_mismatch(self):
        m15 = copy.deepcopy(self.m15)
        m15["source"] = "synthetic.fallback"
        result = self.validate(m15=m15)
        self.assertIn("UNAPPROVED_DATA_SOURCE", result.reasons)
        h1 = copy.deepcopy(self.h1)
        h1["source"] = "okx"
        result = self.validate(h1=h1)
        self.assertIn("DATA_SOURCE_MISMATCH", result.reasons)

    def test_blocks_wrong_symbol_market_or_timeframe(self):
        for field, value in (("symbol", "ETHUSDT"), ("marketType", "SPOT"),
                             ("timeframe", "5m"), ("exchange", "okx")):
            snapshot = copy.deepcopy(self.m15)
            snapshot[field] = value
            with self.subTest(field=field):
                result = self.validate(m15=snapshot)
                self.assertEqual(result.status, "BLOCKED_PREFLIGHT")

    def test_blocks_incomplete_lookback_or_reported_gap(self):
        snapshot = copy.deepcopy(self.m15)
        snapshot["coverage"]["complete"] = False
        snapshot["coverage"]["gaps"] = [{"startMs": 1, "endMs": 2}]
        result = self.validate(m15=snapshot)
        self.assertIn("INCOMPLETE_LOOKBACK", result.reasons)

    def test_blocks_missing_or_short_feature_lookback(self):
        result = self.validate(required={"15m": 4, "1h": 3})
        self.assertIn("INSUFFICIENT_LOOKBACK", result.reasons)
        result = self.validate(required={"15m": 0, "1h": 3})
        self.assertEqual(result.status, "BLOCKED_PREFLIGHT")

    def test_blocks_duplicate_or_out_of_order_candles(self):
        duplicate = copy.deepcopy(self.m15)
        duplicate["candles"][1] = copy.deepcopy(duplicate["candles"][0])
        result = self.validate(m15=duplicate)
        self.assertIn("CANDLE_SEQUENCE_INVALID", result.reasons)
        unordered = copy.deepcopy(self.m15)
        unordered["candles"].reverse()
        result = self.validate(m15=unordered)
        self.assertIn("CANDLE_SEQUENCE_INVALID", result.reasons)

    def test_blocks_forming_unclosed_or_late_observed_candle(self):
        for mutation in (
            {"isClosed": False},
            {"availableAtMs": AS_OF + 1},
            {"closeTimeMs": AS_OF + 1},
        ):
            snapshot = copy.deepcopy(self.m15)
            snapshot["candles"][-1].update(mutation)
            with self.subTest(mutation=mutation):
                result = self.validate(m15=snapshot)
                self.assertEqual(result.status, "BLOCKED_PREFLIGHT")

    def test_blocks_invalid_ohlcv_and_non_decimal_values(self):
        for mutation in ({"open": 100.0}, {"high": "NaN"}, {"low": "103"},
                         {"volume": "-1"}, {"close": "Infinity"}):
            snapshot = copy.deepcopy(self.m15)
            snapshot["candles"][-1].update(mutation)
            with self.subTest(mutation=mutation):
                self.assertEqual(self.validate(m15=snapshot).status, "BLOCKED_PREFLIGHT")

    def test_blocks_dataset_version_and_coverage_count_mismatch(self):
        snapshot = copy.deepcopy(self.m15)
        snapshot["datasetVersion"] = "sha256:invalid"
        self.assertEqual(self.validate(m15=snapshot).status, "BLOCKED_PREFLIGHT")
        snapshot = copy.deepcopy(self.m15)
        snapshot["coverage"]["returned"] = 2
        self.assertIn("INCOMPLETE_LOOKBACK", self.validate(m15=snapshot).reasons)

    def test_rejects_boolean_or_invalid_preflight_clock(self):
        self.assertEqual(self.validate(as_of=True).status, "BLOCKED_PREFLIGHT")
        self.assertEqual(self.validate(as_of=-1).status, "BLOCKED_PREFLIGHT")


if __name__ == "__main__":
    unittest.main()
