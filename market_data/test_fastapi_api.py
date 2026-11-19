"""FastAPI adapter contract tests. These intentionally target the not-yet-created ASGI app."""

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from market_data.fastapi_app import app
from market_data.store import Candle, CandleStore, INTERVAL_MS
from market_data.feeder import LeaseStore
from market_data.write_gateway import SQLiteWriteGateway


class FastApiCandleContractTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "candles.sqlite3"
        self.interval = INTERVAL_MS["15m"]
        self.start = 1_800_000_000_000 // self.interval * self.interval
        store = CandleStore(self.db)
        leases = LeaseStore(str(self.db))
        lease = leases.acquire("fastapi-test", self.start, ttl_seconds=60)
        gateway = SQLiteWriteGateway(
            store=store,
            lease_store=leases,
            owner_id="fastapi-test",
            generation_provider=lambda: lease.generation,
            clock=lambda: self.start + 1,
        )
        gateway.write_batch([
            Candle(
                "15m", self.start, "100.01", "101", "99", "100.5", "2.50",
                self.start + self.interval + 7,
            )
        ])
        self.env = {
            "MARKET_DATA_DB": str(self.db),
            "MARKET_DATA_BACKEND": "sqlite",
            "MARKET_DATA_TOKEN": "read-only-token",
        }
        self.client = TestClient(app)

    def request(self, query=None, token="read-only-token", method="GET", path="/v1/candles"):
        query = query or (
            f"symbol=BTCUSDT&timeframe=15m&startMs={self.start}"
            f"&endMs={self.start + 2 * self.interval}"
        )
        headers = {"Authorization": f"Bearer {token}"} if token is not None else {}
        with patch.dict(os.environ, self.env, clear=True):
            return self.client.request(method, path, params=query, headers=headers)

    def test_health_is_public_and_has_stable_payload(self):
        with patch.dict(os.environ, {}, clear=True):
            response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True, "service": "canonical-market-data"})
        self.assertEqual(response.headers.get("cache-control"), "no-store")

    def test_candle_response_preserves_contract_110_and_decimal_strings(self):
        evaluation = self.start + self.interval + 1_000
        with patch("market_data.fastapi_app.time.time_ns", return_value=evaluation * 1_000_000):
            response = self.request()
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["contractVersion"], "1.1.0")
        self.assertEqual(body["candles"][0]["open"], "100.01")
        self.assertEqual(body["candles"][0]["volume"], "2.5")
        self.assertEqual(body["freshness"]["evaluationAnchor"], "GENERATED_AT")
        self.assertIn("evaluable", body["freshness"])
        self.assertEqual(response.headers.get("cache-control"), "no-store")

    def test_missing_or_wrong_bearer_token_is_unauthorized(self):
        self.assertEqual(self.request(token="wrong").status_code, 401)
        self.assertEqual(self.request(token=None).status_code, 401)

    def test_missing_token_configuration_fails_closed(self):
        env = dict(self.env)
        env["MARKET_DATA_TOKEN"] = ""
        with patch.dict(os.environ, env, clear=True):
            response = self.client.get(
                "/v1/candles",
                params={"symbol": "BTCUSDT", "timeframe": "15m",
                        "startMs": self.start, "endMs": self.start + self.interval},
            )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"error": "UNCONFIGURED"})

    def test_invalid_query_uses_400_not_fastapi_default_422(self):
        base = {
            "symbol": "BTCUSDT", "timeframe": "15m",
            "startMs": self.start, "endMs": self.start + self.interval,
        }
        with patch.dict(os.environ, self.env, clear=True):
            for params in (
                {**base, "symbol": "ETHUSDT"},
                {**base, "extra": "1"},
                {**base, "startMs": "not-an-integer"},
                {**base, "endMs": self.start + 2001 * self.interval},
                {**base, "asOfMs": self.start + 10 * self.interval},
            ):
                with self.subTest(params=params):
                    response = self.client.get("/v1/candles", params=params,
                                               headers={"Authorization": "Bearer read-only-token"})
                    self.assertEqual(response.status_code, 400)
                    self.assertEqual(response.json(), {"error": "INVALID_QUERY"})

    def test_post_is_405_and_allow_header_is_get(self):
        response = self.request(method="POST")
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.headers.get("allow"), "GET")
        self.assertEqual(response.json(), {"error": "METHOD_NOT_ALLOWED"})

    def test_unknown_path_is_404_with_contract_error(self):
        response = self.request(path="/v1/orders")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": "NOT_FOUND"})

    def test_missing_sqlite_database_returns_503_without_creating_file(self):
        missing = Path(self.temp.name) / "missing.sqlite3"
        env = dict(self.env, MARKET_DATA_DB=str(missing))
        query = {
            "symbol": "BTCUSDT", "timeframe": "15m",
            "startMs": self.start, "endMs": self.start + self.interval,
        }
        with patch.dict(os.environ, env, clear=True):
            response = self.client.get(
                "/v1/candles", params=query,
                headers={"Authorization": "Bearer read-only-token"},
            )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"error": "STORE_UNAVAILABLE"})
        self.assertFalse(missing.exists())

    def test_future_as_of_is_rejected(self):
        evaluation = self.start + self.interval + 1_000
        query = {
            "symbol": "BTCUSDT", "timeframe": "15m",
            "startMs": self.start, "endMs": self.start + self.interval,
            "asOfMs": evaluation + 1,
        }
        with patch("market_data.fastapi_app.time.time_ns", return_value=evaluation * 1_000_000):
            with patch.dict(os.environ, self.env, clear=True):
                response = self.client.get(
                    "/v1/candles", params=query,
                    headers={"Authorization": "Bearer read-only-token"},
                )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "INVALID_QUERY"})

    def test_explicit_postgres_backend_fails_closed_and_never_falls_back_to_sqlite(self):
        env = dict(self.env, MARKET_DATA_BACKEND="postgres")
        query = {
            "symbol": "BTCUSDT", "timeframe": "15m",
            "startMs": self.start, "endMs": self.start + self.interval,
        }
        with patch.dict(os.environ, env, clear=True):
            response = self.client.get(
                "/v1/candles", params=query,
                headers={"Authorization": "Bearer read-only-token"},
            )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"error": "STORE_UNAVAILABLE"})
        self.assertTrue(self.db.is_file())


if __name__ == "__main__":
    unittest.main()
