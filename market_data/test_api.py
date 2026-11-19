import json
import os
import sqlite3
from contextlib import closing
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from market_data.fastapi_app import app
from market_data.store import Candle, CandleStore, INTERVAL_MS
from market_data.feeder import LeaseStore
from market_data.write_gateway import SQLiteWriteGateway
from market_data.sync import sync_window


class CandleApiTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "candles.sqlite3"
        self.interval = INTERVAL_MS["15m"]
        self.start = 1_800_000_000_000 // self.interval * self.interval
        store = CandleStore(self.db)
        leases = LeaseStore(str(self.db))
        lease = leases.acquire("api-test", self.start, ttl_seconds=60)
        gateway = SQLiteWriteGateway(
            store=store, lease_store=leases, owner_id="api-test",
            generation_provider=lambda: lease.generation, clock=lambda: self.start + 1,
        )
        gateway.write_batch([
            Candle("15m", self.start, "100.01", "101", "99", "100.5", "2.50",
                   self.start + self.interval + 7)
        ])
        self.config = {"MARKET_DATA_DB": str(self.db), "MARKET_DATA_TOKEN": "read-only-token"}
        self.client = TestClient(app)

    def request(self, query=None, token="read-only-token", method="GET", path="/v1/candles"):
        query = query if query is not None else f"symbol=BTCUSDT&timeframe=15m&startMs={self.start}&endMs={self.start + 2*self.interval}"
        headers = {"Authorization": "Bearer " + token}
        with patch.dict(os.environ, self.config, clear=True):
            response = self.client.request(method, f"{path}?{query}", headers=headers)
        self.assertEqual(response.headers.get("cache-control"), "no-store")
        self.assertEqual(response.headers.get("content-type"), "application/json; charset=utf-8")
        return response.status_code, response.json()

    def test_reads_persisted_decimal_candles_and_reports_gap(self):
        code, body = self.request()
        self.assertEqual(code, 200)
        self.assertEqual(body["exchange"], "binance")
        self.assertEqual(body["marketType"], "USDT_PERPETUAL")
        self.assertEqual(body["candles"][0]["open"], "100.01")
        self.assertTrue(body["candles"][0]["isClosed"])
        self.assertEqual(body["coverage"]["expected"], 2)
        self.assertEqual(body["coverage"]["returned"], 1)
        self.assertFalse(body["coverage"]["complete"])
        self.assertEqual(body["coverage"]["gaps"], [{"startMs": self.start + self.interval, "endMs": self.start + 2*self.interval}])

    def test_as_of_does_not_backdate_imported_history(self):
        query = f"symbol=BTCUSDT&timeframe=15m&startMs={self.start}&endMs={self.start+self.interval}&asOfMs={self.start+self.interval}"
        generated_at = self.start + self.interval + 100
        with patch("market_data.fastapi_app.time.time_ns", return_value=generated_at * 1_000_000):
            code, body = self.request(query)
        self.assertEqual(code, 200)
        self.assertEqual(body["candles"], [])
        self.assertFalse(body["coverage"]["complete"])

    def test_missing_auth_or_store_fails_without_creating_database(self):
        self.assertEqual(self.request(token="wrong")[0], 401)
        self.config["MARKET_DATA_TOKEN"] = ""
        self.assertEqual(self.request()[0], 503)
        self.config["MARKET_DATA_TOKEN"] = "read-only-token"
        missing = Path(self.temp.name) / "absent.sqlite3"
        self.config["MARKET_DATA_DB"] = str(missing)
        code, body = self.request()
        self.assertEqual(code, 503)
        self.assertFalse(missing.exists())
        self.assertNotIn(str(missing), json.dumps(body))


    def test_explicit_postgres_without_dsn_fails_closed_instead_of_using_sqlite(self):
        self.config["MARKET_DATA_BACKEND"] = "postgres"
        code, body = self.request()
        self.assertEqual(code, 503)
        self.assertEqual(body, {"error": "STORE_UNAVAILABLE"})
        self.assertTrue(self.db.is_file())

    def test_invalid_duplicate_unbounded_and_unknown_parameters(self):
        base = f"symbol=BTCUSDT&timeframe=15m&startMs={self.start}&endMs={self.start+self.interval}"
        for query in (base + "&symbol=ETHUSDT", base + "&token=secret", base.replace("BTCUSDT", "ETHUSDT"),
                      base.replace("15m", "1d"), base.replace(str(self.start), "nan"),
                      base + "&asOfMs=-1", base.replace(str(self.start+self.interval), str(self.start+2001*self.interval)),
                      "x=" + "a"*2100):
            with self.subTest(query=query[:100]):
                self.assertEqual(self.request(query)[0], 400)

    def test_read_only_methods_and_process_health(self):
        self.assertEqual(self.request(method="POST")[0], 405)
        self.assertEqual(self.request(path="/v1/orders")[0], 404)
        code, body = self.request(path="/health", token="")
        self.assertEqual(code, 200)
        self.assertEqual(body, {"ok": True, "service": "canonical-market-data"})

    def test_corrupt_stored_prices_are_not_served_as_validated(self):
        with closing(sqlite3.connect(self.db)) as connection:
            with connection:
                connection.execute("UPDATE candles SET high='0'")
        code, body = self.request()
        self.assertEqual(code, 503)
        self.assertEqual(body, {"error": "STORE_UNAVAILABLE"})

    def test_sync_to_reopened_api_preserves_gaps_and_observation_time(self):
        start, step = self.start, self.interval

        class Exchange:
            id = "binanceusdm"

            def load_markets(self):
                market = dict(symbol="BTC/USDT:USDT", id="BTCUSDT", base="BTC", quote="USDT",
                              settle="USDT", active=True, swap=True, linear=True, spot=False)
                return {market["symbol"]: market}

            def fetch_time(self):
                return start + step

            def fetch_ohlcv(self, *args, **kwargs):
                return [[start, 100, 101, 99, 100.5, 2.5],
                        [start + step, 100, 102, 99, 101, 3]]

        path = Path(self.temp.name) / "pipeline.sqlite3"
        store = CandleStore(path)
        leases = LeaseStore(str(path))
        lease = leases.acquire("api-pipeline-test", start, ttl_seconds=60)
        gateway = SQLiteWriteGateway(
            store=store, lease_store=leases, owner_id="api-pipeline-test",
            generation_provider=lambda: lease.generation, clock=lambda: start + 1,
        )
        inserted = sync_window(Exchange(), gateway, "15m", start, start+2*step,
                               now_ms=lambda: start+3*step)
        self.assertEqual(inserted, 1)
        self.config["MARKET_DATA_DB"] = str(path)
        code, result = self.request()
        self.assertEqual(code, 200)
        self.assertEqual(result["coverage"]["returned"], 1)
        self.assertFalse(result["coverage"]["complete"])
        self.assertEqual(result["candles"][0]["availableAtMs"], start+3*step)
        self.assertEqual(result["candles"][0]["availabilityKind"], "FIRST_OBSERVED")


    def test_missing_sqlite_path_preserves_unconfigured_response(self):
        self.config.pop("MARKET_DATA_DB")
        code, body = self.request()
        self.assertEqual(code, 503)
        self.assertEqual(body, {"error": "UNCONFIGURED"})


    def test_contract_v1_response_has_explicit_version_and_market_identity(self):
        generated_at = self.start + 2*self.interval + 1_000
        with patch("market_data.fastapi_app.time.time_ns", return_value=generated_at * 1_000_000):
            code, body = self.request()

        self.assertEqual(code, 200)
        self.assertEqual(body["contractVersion"], "1.1.0")
        self.assertEqual(body["schemaVersion"], 1)
        self.assertEqual(body["exchange"], "binance")
        self.assertEqual(body["marketType"], "USDT_PERPETUAL")
        self.assertEqual(body["symbol"], "BTCUSDT")
        self.assertEqual(body["timeframe"], "15m")
        self.assertEqual(body["volumeUnit"], "BTC_BASE_ASSET")
        self.assertEqual(body["source"], "ccxt.binanceusdm")
        self.assertEqual(body["startMs"], self.start)
        self.assertEqual(body["endMs"], self.start + 2*self.interval)
        self.assertIsNone(body["asOfMs"])
        self.assertRegex(body["datasetVersion"], r"^sha256:[0-9a-f]{64}$")

    def test_contract_v1_freshness_requires_complete_coverage(self):
        evaluation_time = self.start + self.interval + 1_000
        with patch("market_data.fastapi_app.time.time_ns", return_value=evaluation_time * 1_000_000):
            code, body = self.request()

        self.assertEqual(code, 200)
        self.assertFalse(body["coverage"]["complete"])
        self.assertEqual(body["freshness"], {
            "latestExpectedOpenTimeMs": self.start,
            "latestReturnedOpenTimeMs": self.start,
            "latestCloseTimeMs": self.start + self.interval,
            "latestAvailableAtMs": self.start + self.interval + 7,
            "evaluationTimeMs": evaluation_time,
            "evaluationAnchor": "GENERATED_AT",
            "observationAgeMs": evaluation_time - (self.start + self.interval + 7),
            "closeLagMs": evaluation_time - (self.start + self.interval),
            "timestampValid": True,
            "fresh": True,
            "evaluable": False,
        })


    def test_contract_v1_complete_current_window_is_evaluable(self):
        evaluation_time = self.start + self.interval + 1_000
        query = (
            f"symbol=BTCUSDT&timeframe=15m&startMs={self.start}"
            f"&endMs={self.start+self.interval}"
        )
        with patch("market_data.fastapi_app.time.time_ns", return_value=evaluation_time * 1_000_000):
            code, body = self.request(query)

        self.assertEqual(code, 200)
        self.assertTrue(body["coverage"]["complete"])
        self.assertTrue(body["freshness"]["timestampValid"])
        self.assertTrue(body["freshness"]["fresh"])
        self.assertTrue(body["freshness"]["evaluable"])


    def test_contract_v1_stale_latest_candle_is_not_fresh_or_evaluable(self):
        evaluation_time = self.start + 2*self.interval + 1_000
        with patch("market_data.fastapi_app.time.time_ns", return_value=evaluation_time * 1_000_000):
            code, body = self.request()

        self.assertEqual(code, 200)
        self.assertFalse(body["freshness"]["fresh"])
        self.assertFalse(body["freshness"]["evaluable"])


    def test_contract_v1_historical_as_of_anchors_freshness_to_replay_time(self):
        evaluation_time = self.start + self.interval + 1_000
        generated_at = self.start + 10*self.interval
        query = (
            f"symbol=BTCUSDT&timeframe=15m&startMs={self.start}"
            f"&endMs={self.start+self.interval}&asOfMs={evaluation_time}"
        )
        with patch("market_data.fastapi_app.time.time_ns", return_value=generated_at * 1_000_000):
            code, body = self.request(query)

        self.assertEqual(code, 200)
        self.assertEqual(body["generatedAtMs"], generated_at)
        self.assertEqual(body["asOfMs"], evaluation_time)
        self.assertEqual(body["freshness"]["evaluationTimeMs"], evaluation_time)
        self.assertEqual(body["freshness"]["evaluationAnchor"], "AS_OF")
        self.assertTrue(body["freshness"]["fresh"])
        self.assertTrue(body["freshness"]["evaluable"])


    def test_contract_v1_future_as_of_is_rejected(self):
        generated_at = self.start + 2*self.interval
        query = (
            f"symbol=BTCUSDT&timeframe=15m&startMs={self.start}"
            f"&endMs={self.start+self.interval}&asOfMs={generated_at+1}"
        )
        with patch("market_data.fastapi_app.time.time_ns", return_value=generated_at * 1_000_000):
            code, body = self.request(query)

        self.assertEqual(code, 400)
        self.assertEqual(body, {"error": "INVALID_QUERY"})


    def test_contract_v1_future_availability_timestamp_is_invalid(self):
        evaluation_time = self.start + self.interval + 1_000
        with closing(sqlite3.connect(self.db)) as connection:
            with connection:
                connection.execute(
                    "UPDATE candles SET available_at_ms=?",
                    (evaluation_time + 1,),
                )
        query = (
            f"symbol=BTCUSDT&timeframe=15m&startMs={self.start}"
            f"&endMs={self.start+self.interval}"
        )
        with patch("market_data.fastapi_app.time.time_ns", return_value=evaluation_time * 1_000_000):
            code, body = self.request(query)

        self.assertEqual(code, 200)
        self.assertFalse(body["freshness"]["timestampValid"])
        self.assertFalse(body["freshness"]["fresh"])
        self.assertFalse(body["freshness"]["evaluable"])


    def test_contract_v1_empty_as_of_window_has_null_freshness_and_is_not_evaluable(self):
        generated_at = self.start + 2*self.interval + 1_000
        query = (
            f"symbol=BTCUSDT&timeframe=15m&startMs={self.start}"
            f"&endMs={self.start+self.interval}&asOfMs={self.start+self.interval}"
        )
        with patch("market_data.fastapi_app.time.time_ns", return_value=generated_at * 1_000_000):
            code, body = self.request(query)

        self.assertEqual(code, 200)
        self.assertEqual(body["candles"], [])
        self.assertEqual(body["freshness"], {
            "latestExpectedOpenTimeMs": self.start,
            "latestReturnedOpenTimeMs": None,
            "latestCloseTimeMs": None,
            "latestAvailableAtMs": None,
            "evaluationTimeMs": self.start + self.interval,
            "evaluationAnchor": "AS_OF",
            "observationAgeMs": None,
            "closeLagMs": None,
            "timestampValid": False,
            "fresh": False,
            "evaluable": False,
        })

    def test_contract_v1_candle_has_explicit_exclusive_close_and_quality_provenance(self):
        generated_at = self.start + 2*self.interval + 1_000
        with patch("market_data.fastapi_app.time.time_ns", return_value=generated_at * 1_000_000):
            code, body = self.request()

        self.assertEqual(code, 200)
        candle = body["candles"][0]
        self.assertEqual(candle["openTimeMs"], self.start)
        self.assertEqual(candle["closeTimeMs"], self.start + self.interval)
        self.assertEqual(candle["availabilityKind"], "FIRST_OBSERVED")
        self.assertEqual(candle["quality"], "VALIDATED")
        self.assertEqual(candle["source"], "ccxt.binanceusdm")
        self.assertEqual(candle["volume"], "2.5")


if __name__ == "__main__":
    unittest.main()
