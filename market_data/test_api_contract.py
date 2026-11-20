"""Direct fail-closed tests for the shared T0 Candle Contract helper."""

import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from market_data.api_contract import _freshness, candle_envelope
from market_data.fastapi_app import app
from market_data.store import Candle, CandleStore, INTERVAL_MS, read_window
from market_data.feeder import LeaseStore
from market_data.write_gateway import SQLiteWriteGateway
from pipeline import api as common_api
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

    def test_future_availability_has_no_negative_observation_age(self):
        evaluation = START + M15 + 3
        result = _freshness(
            [candle(START, available_offset=M15 + 7)],
            "15m", evaluation, True, "AS_OF",
        )
        self.assertIsNone(result["observationAgeMs"])
        self.assertEqual(result["closeLagMs"], 3)
        self.assertFalse(result["timestampValid"])

    def test_future_close_and_availability_have_no_negative_lags(self):
        evaluation = START + M15 - 1
        result = _freshness(
            [candle(START)],
            "15m", evaluation, True, "AS_OF",
        )
        self.assertIsNone(result["observationAgeMs"])
        self.assertIsNone(result["closeLagMs"])
        self.assertFalse(result["timestampValid"])

    def test_fastapi_rejects_future_as_of_before_opening_store(self):
        evaluation = START + M15 + 1_000
        future = evaluation + 1
        env = {
            "MARKET_DATA_BACKEND": "sqlite",
            "MARKET_DATA_DB": "/unused/test.sqlite3",
            "MARKET_DATA_TOKEN": "isolated-contract-token",
        }
        with patch.dict(os.environ, env, clear=True):
            with patch("market_data.fastapi_app.time.time_ns",
                       return_value=evaluation * 1_000_000):
                with patch("market_data.fastapi_app.create_store_from_env",
                           side_effect=AssertionError("store must not be opened")) as factory:
                    response = TestClient(app).get(
                        "/v1/candles",
                        params={"symbol": "BTCUSDT", "timeframe": "15m",
                                "startMs": START, "endMs": START + M15,
                                "asOfMs": future},
                        headers={"Authorization": "Bearer isolated-contract-token"},
                    )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "INVALID_QUERY"})
        factory.assert_not_called()

    def test_fastapi_response_envelope_error_is_not_reported_as_store_outage(self):
        evaluation = START + M15 + 1_000
        env = {
            "MARKET_DATA_BACKEND": "sqlite",
            "MARKET_DATA_DB": "/unused/test.sqlite3",
            "MARKET_DATA_TOKEN": "isolated-contract-token",
        }
        store = type("Store", (), {
            "read_window": lambda self, **query: {
                "timeframe": "15m", "candles": [], "coverage": {"complete": False},
            }
        })()
        with patch.dict(os.environ, env, clear=True):
            with patch("market_data.fastapi_app.time.time_ns",
                       return_value=evaluation * 1_000_000):
                with patch("market_data.fastapi_app.create_store_from_env",
                           return_value=store):
                    with patch("market_data.fastapi_app.candle_envelope",
                               side_effect=ValueError("invalid internal result")):
                        response = TestClient(app).get(
                            "/v1/candles",
                            params={"symbol": "BTCUSDT", "timeframe": "15m",
                                    "startMs": START, "endMs": START + M15},
                            headers={"Authorization": "Bearer isolated-contract-token"},
                        )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"error": "INTERNAL_ERROR"})

    def test_invalid_evaluation_timestamp_is_rejected(self):
        for evaluation in (-1, True, "1800000000000", 1.5):
            with self.subTest(evaluation=evaluation):
                with self.assertRaises(ValueError):
                    _freshness([candle(START)], "15m", evaluation, True, "AS_OF")

    def test_invalid_evaluation_anchor_is_rejected(self):
        with self.assertRaises(ValueError):
            _freshness([candle(START)], "15m", START + M15 + 1_000, True, [])

    def test_unsupported_timeframe_is_rejected(self):
        with self.assertRaises(ValueError):
            _freshness([candle(START)], "1d", START + M15 + 1_000, True, "AS_OF")


    def test_h1_contiguous_current_window_is_evaluable(self):
        interval = INTERVAL_MS["1h"]
        start = 1_800_000_000_000 // interval * interval
        evaluation = start + 2 * interval + 1_000
        rows = [
            {"openTimeMs": start, "closeTimeMs": start + interval,
             "availableAtMs": start + interval + 7},
            {"openTimeMs": start + interval, "closeTimeMs": start + 2 * interval,
             "availableAtMs": start + 2 * interval + 7},
        ]
        result = _freshness(rows, "1h", evaluation, True, "AS_OF")
        self.assertTrue(result["timestampValid"])
        self.assertTrue(result["fresh"])
        self.assertTrue(result["evaluable"])

    def test_envelope_rejects_invalid_generated_timestamp(self):
        result = {
            "timeframe": "15m", "candles": [],
            "coverage": {"complete": False},
        }
        for generated in (-1, True, 1.5, "1800000000000"):
            with self.subTest(generated=generated):
                with self.assertRaises(ValueError):
                    candle_envelope(result, generated)

    def test_envelope_rejects_future_as_of_timestamp(self):
        result = {
            "timeframe": "15m", "candles": [],
            "coverage": {"complete": False},
        }
        with self.assertRaises(ValueError):
            candle_envelope(result, START + M15 + 1_000, START + M15 + 1_001)

    def test_envelope_rejects_incomplete_storage_result_shape(self):
        with self.assertRaises(ValueError):
            candle_envelope({"timeframe": "15m", "candles": []}, START)

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
            evaluation = START + M15 + 1_000
            expected = read_window(str(database), "BTCUSDT", "15m", START, end, as_of_ms=evaluation)
            env = {
                "MARKET_DATA_BACKEND": "sqlite",
                "MARKET_DATA_DB": str(database),
                "MARKET_DATA_TOKEN": "isolated-contract-token",
            }
            with patch.dict(os.environ, env, clear=True):
                application_window = market_window("BTCUSDT", "15m", START, end, as_of_ms=evaluation)
                with patch("market_data.fastapi_app.time.time_ns",
                           return_value=evaluation * 1_000_000):
                    response = TestClient(app).get(
                        "/v1/candles",
                        params={"symbol": "BTCUSDT", "timeframe": "15m",
                                "startMs": START, "endMs": end, "asOfMs": evaluation},
                        headers={"Authorization": "Bearer isolated-contract-token"},
                    )
            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertEqual(response.headers.get("cache-control"), "no-store")
            query_string = (
                f"symbol=BTCUSDT&timeframe=15m&startMs={START}&endMs={end}&asOfMs={evaluation}"
            )
            environ = {
                "PATH_INFO": "/v1/candles",
                "REQUEST_METHOD": "GET",
                "QUERY_STRING": query_string,
                "HTTP_AUTHORIZATION": "Bearer isolated-contract-token",
                "CONTENT_LENGTH": "0",
                "wsgi.input": io.BytesIO(b""),
            }
            statuses = []
            with patch.dict(os.environ, env, clear=True):
                with patch("pipeline.api.now_ms", return_value=evaluation):
                    raw_common = b"".join(
                        common_api.application(
                            environ, lambda status, headers: statuses.append((status, headers))
                        )
                    )
            self.assertEqual(statuses[0][0], "200 OK")
            common_payload = json.loads(raw_common)
            common_headers = dict(statuses[0][1])
            self.assertEqual(common_headers.get("Cache-Control"), "no-store")
            self.assertEqual(
                common_headers.get("Content-Type"),
                response.headers.get("content-type"),
            )
            for field in (
                "contractVersion", "schemaVersion", "volumeUnit", "source",
                "generatedAtMs", "freshness",
            ):
                with self.subTest(common_contract_field=field):
                    self.assertEqual(common_payload[field], payload[field])

            invalid_query = query_string + "&symbol=BTCUSDT"
            with patch.dict(os.environ, env, clear=True):
                fastapi_invalid = TestClient(app).get(
                    f"/v1/candles?{invalid_query}",
                    headers={"Authorization": "Bearer isolated-contract-token"},
                )
            invalid_environ = dict(environ, QUERY_STRING=invalid_query)
            invalid_statuses = []
            with patch.dict(os.environ, env, clear=True):
                invalid_raw = b"".join(
                    common_api.application(
                        invalid_environ,
                        lambda status, headers: invalid_statuses.append((status, headers)),
                    )
                )
            self.assertEqual(fastapi_invalid.status_code, 400)
            self.assertEqual(invalid_statuses[0][0], "400 Bad Request")
            self.assertEqual(json.loads(invalid_raw), fastapi_invalid.json())

            future_query = query_string + f"&asOfMs={evaluation + 1}"
            with patch.dict(os.environ, env, clear=True):
                fastapi_future = TestClient(app).get(
                    f"/v1/candles?{future_query}",
                    headers={"Authorization": "Bearer isolated-contract-token"},
                )
            future_environ = dict(environ, QUERY_STRING=future_query)
            future_statuses = []
            with patch.dict(os.environ, env, clear=True):
                future_raw = b"".join(
                    common_api.application(
                        future_environ,
                        lambda status, headers: future_statuses.append((status, headers)),
                    )
                )
            self.assertEqual(fastapi_future.status_code, 400)
            self.assertEqual(future_statuses[0][0], "400 Bad Request")
            self.assertEqual(json.loads(future_raw), fastapi_future.json())

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
