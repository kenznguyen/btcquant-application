"""Direct fail-closed tests for the shared T0 Candle Contract helper."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from market_data.api_contract import _freshness
from market_data.fastapi_app import app
from market_data.store import Candle, CandleStore, INTERVAL_MS, read_window
from market_data.feeder import LeaseStore
from market_data.write_gateway import SQLiteWriteGateway
from pipeline.api import market_window


M15 = INTERVAL_MS["15m"]
START = 1_800_000_000_000 // M15 * M15


def candle(open_ms, interval=M15, available_offset=7):
    return {
        "openTimeMs": open_ms,
        "closeTimeMs": open_ms + interval,
        "availableAtMs": open_ms + interval + available_offset,
    }


class CandleContractFailClosedTest(unittest.TestCase):
    def test_contiguous_current_window_is_evaluable(self):
        evaluation = START + 2 * M15 + 1_000
        result = _freshness(
            [candle(START), candle(START + M15)],
            "15m", evaluation, True, "AS_OF",
        )
        self.assertTrue(result["timestampValid"])
        self.assertTrue(result["fresh"])
        self.assertTrue(result["evaluable"])

    def test_gap_is_timestamp_invalid_even_when_coverage_claims_complete(self):
        evaluation = START + 3 * M15 + 1_000
        result = _freshness(
            [candle(START), candle(START + 2 * M15)],
            "15m", evaluation, True, "AS_OF",
        )
        self.assertFalse(result["timestampValid"])
        self.assertFalse(result["fresh"])
        self.assertFalse(result["evaluable"])

    def test_duplicate_and_out_of_order_opens_are_rejected(self):
        evaluation = START + 2 * M15 + 1_000
        for rows in (
            [candle(START), candle(START)],
            [candle(START + M15), candle(START)],
        ):
            with self.subTest(rows=rows):
                result = _freshness(rows, "15m", evaluation, True, "AS_OF")
                self.assertFalse(result["timestampValid"])
                self.assertFalse(result["evaluable"])

    def test_future_first_observation_is_rejected(self):
        evaluation = START + M15 + 1_000
        result = _freshness(
            [candle(START, available_offset=M15)],
            "15m", evaluation, True, "AS_OF",
        )
        self.assertFalse(result["timestampValid"])
        self.assertFalse(result["evaluable"])

    def test_incomplete_coverage_is_not_evaluable(self):
        evaluation = START + M15 + 1_000
        result = _freshness(
            [candle(START)], "15m", evaluation, False, "AS_OF",
        )
        self.assertTrue(result["timestampValid"])
        self.assertTrue(result["fresh"])
        self.assertFalse(result["evaluable"])

    def test_empty_window_is_not_evaluable(self):
        evaluation = START + M15 + 1_000
        result = _freshness([], "15m", evaluation, True, "AS_OF")
        self.assertFalse(result["timestampValid"])
        self.assertFalse(result["fresh"])
        self.assertFalse(result["evaluable"])

    def test_non_boolean_coverage_claim_is_not_evaluable(self):
        evaluation = START + M15 + 1_000
        result = _freshness(
            [candle(START)], "15m", evaluation, 1, "AS_OF",
        )
        self.assertFalse(result["evaluable"])

    def test_invalid_evaluation_timestamp_is_rejected(self):
        for evaluation in (-1, True, "1800000000000", 1.5):
            with self.subTest(evaluation=evaluation):
                with self.assertRaises(ValueError):
                    _freshness([candle(START)], "15m", evaluation, True, "AS_OF")

    def test_unsupported_timeframe_is_rejected(self):
        with self.assertRaises(ValueError):
            _freshness([candle(START)], "1d", START + M15 + 1_000, True, "AS_OF")

    def test_fastapi_and_application_market_adapter_preserve_same_candle_window(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "market.sqlite3"
            store = CandleStore(database)
            leases = LeaseStore(str(database))
            lease = leases.acquire("contract-parity-test", START, ttl_seconds=60)
            gateway = SQLiteWriteGateway(
                store=store,
                lease_store=leases,
                owner_id="contract-parity-test",
                generation_provider=lambda: lease.generation,
                clock=lambda: START + 1,
            )
            gateway.write_batch([
                Candle("15m", START, "100.01", "101", "99", "100.5", "2.50",
                       START + M15 + 7)
            ])
            end = START + M15
            expected = read_window(str(database), "BTCUSDT", "15m", START, end)
            evaluation = START + M15 + 1_000
            env = {
                "MARKET_DATA_BACKEND": "sqlite",
                "MARKET_DATA_DB": str(database),
                "MARKET_DATA_TOKEN": "isolated-contract-token",
            }
            with patch.dict(os.environ, env, clear=True):
                application_window = market_window("BTCUSDT", "15m", START, end)
                with patch("market_data.fastapi_app.time.time_ns",
                           return_value=evaluation * 1_000_000):
                    response = TestClient(app).get(
                        "/v1/candles",
                        params={"symbol": "BTCUSDT", "timeframe": "15m",
                                "startMs": START, "endMs": end},
                        headers={"Authorization": "Bearer isolated-contract-token"},
                    )
            self.assertEqual(response.status_code, 200)
            payload = response.json()
            for field in (
                "exchange", "marketType", "symbol", "timeframe", "startMs",
                "endMs", "asOfMs", "candles", "datasetVersion", "coverage",
            ):
                with self.subTest(field=field):
                    self.assertEqual(application_window[field], expected[field])
                    self.assertEqual(payload[field], expected[field])
            self.assertTrue(payload["freshness"]["timestampValid"])
            self.assertTrue(payload["freshness"]["fresh"])
            self.assertTrue(payload["freshness"]["evaluable"])


if __name__ == "__main__":
    unittest.main()
