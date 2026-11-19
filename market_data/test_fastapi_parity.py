"""Differential contract tests for the retained WSGI and FastAPI adapters."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from market_data.api import application as wsgi_application
from market_data.fastapi_app import app as asgi_app
from market_data.store import Candle, CandleStore, INTERVAL_MS
from market_data.feeder import LeaseStore
from market_data.write_gateway import SQLiteWriteGateway


class CandleAdapterParityTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "candles.sqlite3"
        self.interval = INTERVAL_MS["15m"]
        self.start = 1_800_000_000_000 // self.interval * self.interval

        store = CandleStore(self.db)
        leases = LeaseStore(str(self.db))
        lease = leases.acquire("adapter-parity-test", self.start, ttl_seconds=60)
        gateway = SQLiteWriteGateway(
            store=store,
            lease_store=leases,
            owner_id="adapter-parity-test",
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
        self.client = TestClient(asgi_app)
        self.query = (
            f"symbol=BTCUSDT&timeframe=15m&startMs={self.start}"
            f"&endMs={self.start + self.interval}"
        )
        self.generated_at = self.start + self.interval + 1_000

    def _wsgi(self, method, path, query, headers):
        captured = {}
        environ = {
            "REQUEST_METHOD": method,
            "PATH_INFO": path,
            "QUERY_STRING": query,
            "HTTP_AUTHORIZATION": headers.get("Authorization", ""),
        }

        def start_response(status, response_headers):
            captured["status"] = int(status.split(" ", 1)[0])
            captured["headers"] = {key.lower(): value for key, value in response_headers}

        body = b"".join(wsgi_application(environ, start_response))
        return captured["status"], captured["headers"], body

    def _asgi(self, method, path, query, headers):
        target = path + (("?" + query) if query else "")
        response = self.client.request(method, target, headers=headers)
        return response.status_code, dict(response.headers), response.content

    def _assert_parity(self, *, method="GET", path="/v1/candles", query=None,
                       headers=None, env=None, generated_at=None):
        query = self.query if query is None else query
        headers = {"Authorization": "Bearer read-only-token"} if headers is None else headers
        effective_env = dict(self.env if env is None else env)
        clock = self.generated_at if generated_at is None else generated_at

        with patch.dict(os.environ, effective_env, clear=True):
            with patch("market_data.api.time.time_ns", return_value=clock * 1_000_000):
                wsgi = self._wsgi(method, path, query, headers)
        with patch.dict(os.environ, effective_env, clear=True):
            with patch("market_data.fastapi_app.time.time_ns", return_value=clock * 1_000_000):
                asgi = self._asgi(method, path, query, headers)

        self.assertEqual(wsgi[0], asgi[0], "HTTP status differs")
        self.assertEqual(wsgi[1], asgi[1], "HTTP headers differ")
        self.assertEqual(wsgi[2], asgi[2], "response body bytes differ")
        if wsgi[2]:
            self.assertEqual(json.loads(wsgi[2]), json.loads(asgi[2]))

    def test_same_fixture_has_identical_status_headers_and_body_for_contract_cases(self):
        cases = [
            ("health", "GET", "/health", "", {}, self.env),
            ("successful_candle_read", "GET", "/v1/candles", self.query,
             {"Authorization": "Bearer read-only-token"}, self.env),
            ("unauthorized", "GET", "/v1/candles", self.query,
             {"Authorization": "Bearer wrong"}, self.env),
            ("token_unconfigured", "GET", "/v1/candles", self.query,
             {"Authorization": "Bearer read-only-token"},
             dict(self.env, MARKET_DATA_TOKEN="")),
            ("malformed_query", "GET", "/v1/candles", "not-a-query",
             {"Authorization": "Bearer read-only-token"}, self.env),
            ("duplicate_query_parameter", "GET", "/v1/candles",
             self.query + "&symbol=BTCUSDT",
             {"Authorization": "Bearer read-only-token"}, self.env),
            ("unknown_path", "GET", "/v1/orders", "",
             {"Authorization": "Bearer read-only-token"}, self.env),
            ("non_get_method", "POST", "/v1/candles", "",
             {"Authorization": "Bearer read-only-token"}, self.env),
            ("store_unavailable", "GET", "/v1/candles", self.query,
             {"Authorization": "Bearer read-only-token"},
             dict(self.env, MARKET_DATA_DB=str(self.db) + ".missing")),
            ("historical_as_of", "GET", "/v1/candles",
             self.query + f"&asOfMs={self.start + self.interval}",
             {"Authorization": "Bearer read-only-token"}, self.env),
        ]

        for name, method, path, query, headers, env in cases:
            with self.subTest(case=name):
                self._assert_parity(
                    method=method,
                    path=path,
                    query=query,
                    headers=headers,
                    env=env,
                )


if __name__ == "__main__":
    unittest.main()
