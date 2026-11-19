"""Read-only canonical candle API. Collection happens separately through sync.py."""

import hmac
import json
import os
import sqlite3
import time
from urllib.parse import parse_qs

from market_data.store import INTERVAL_MS
from market_data.postgres import StoreUnavailable
from market_data.storage import create_store_from_env


MAX_API_CANDLES = 2000
VOLUME_UNIT = "BTC_BASE_ASSET"
DATA_SOURCE = "ccxt.binanceusdm"


def _freshness(candles, timeframe, evaluation_time_ms, coverage_complete, evaluation_anchor):
    interval = INTERVAL_MS[timeframe]
    latest_expected = (evaluation_time_ms // interval) * interval - interval
    latest = candles[-1] if candles else None
    base = {
        "latestExpectedOpenTimeMs": latest_expected,
        "latestReturnedOpenTimeMs": latest.get("openTimeMs") if latest else None,
        "latestCloseTimeMs": latest.get("closeTimeMs") if latest else None,
        "latestAvailableAtMs": latest.get("availableAtMs") if latest else None,
        "evaluationTimeMs": evaluation_time_ms,
        "evaluationAnchor": evaluation_anchor,
        "observationAgeMs": None,
        "closeLagMs": None,
        "timestampValid": False,
        "fresh": False,
        "evaluable": False,
    }
    if not latest:
        return base

    timestamp_valid = type(evaluation_time_ms) is int and evaluation_time_ms >= 0
    previous_open = None
    for candle in candles:
        open_time = candle.get("openTimeMs")
        close_time = candle.get("closeTimeMs")
        available_at = candle.get("availableAtMs")
        valid = all(
            type(value) is int and value >= 0
            for value in (open_time, close_time, available_at)
        )
        if valid:
            valid = (
                open_time % interval == 0
                and close_time == open_time + interval
                and available_at >= close_time
                and available_at <= evaluation_time_ms
                and (previous_open is None or open_time > previous_open)
            )
        if not valid:
            timestamp_valid = False
            break
        previous_open = open_time

    open_time = latest.get("openTimeMs")
    close_time = latest.get("closeTimeMs")
    available_at = latest.get("availableAtMs")
    if type(available_at) is int and available_at >= 0:
        base["observationAgeMs"] = evaluation_time_ms - available_at
    if type(close_time) is int and close_time >= 0:
        base["closeLagMs"] = evaluation_time_ms - close_time

    close_lag = base["closeLagMs"]
    fresh = bool(
        timestamp_valid
        and type(open_time) is int
        and open_time == latest_expected
        and type(close_lag) is int
        and 0 <= close_lag < interval
    )
    base["timestampValid"] = timestamp_valid
    base["fresh"] = fresh
    base["evaluable"] = bool(coverage_complete is True and timestamp_valid and fresh)
    return base

def candle_query(query):
    if len(query) > 2048:
        raise ValueError("Query too long")
    params = parse_qs(query, keep_blank_values=True, strict_parsing=True, max_num_fields=5)
    required = {"symbol", "timeframe", "startMs", "endMs"}
    if not required <= params.keys() or params.keys() - required - {"asOfMs"} or any(len(v) != 1 for v in params.values()):
        raise ValueError("Invalid parameters")
    values = {key: value[0] for key, value in params.items()}
    if values["symbol"] != "BTCUSDT" or values["timeframe"] not in INTERVAL_MS:
        raise ValueError("Unsupported market")

    def integer(key):
        value = values[key]
        if not value.isascii() or not value.isdigit() or len(value) > 19:
            raise ValueError("Invalid time")
        number = int(value)
        if not 0 <= number < 2**63 - 1:
            raise ValueError("Invalid time")
        return number

    start, end = integer("startMs"), integer("endMs")
    step = INTERVAL_MS[values["timeframe"]]
    if start % step or end % step or not 0 < end - start <= MAX_API_CANDLES * step:
        raise ValueError("Invalid or oversized window")
    return dict(symbol=values["symbol"], timeframe=values["timeframe"], start_ms=start,
                end_ms=end, as_of_ms=integer("asOfMs") if "asOfMs" in values else None)


def application(environ, start_response):
    def reply(status, body):
        data = json.dumps(body, allow_nan=False, separators=(",", ":")).encode()
        headers = [("Content-Type", "application/json; charset=utf-8"),
                   ("Content-Length", str(len(data))), ("Cache-Control", "no-store")]
        if status.startswith("405"):
            headers.append(("Allow", "GET"))
        start_response(status, headers)
        return [data]

    if environ.get("REQUEST_METHOD") != "GET":
        return reply("405 Method Not Allowed", {"error": "METHOD_NOT_ALLOWED"})
    path = environ.get("PATH_INFO", "")
    if path == "/health":
        return reply("200 OK", {"ok": True, "service": "canonical-market-data"})
    if path != "/v1/candles":
        return reply("404 Not Found", {"error": "NOT_FOUND"})
    token = os.environ.get("MARKET_DATA_TOKEN", "")
    if not token:
        return reply("503 Service Unavailable", {"error": "UNCONFIGURED"})
    backend = os.environ.get("MARKET_DATA_BACKEND", "sqlite").strip().lower()
    if backend == "sqlite" and not os.environ.get("MARKET_DATA_DB"):
        return reply("503 Service Unavailable", {"error": "UNCONFIGURED"})
    if not hmac.compare_digest(environ.get("HTTP_AUTHORIZATION", "").encode(), ("Bearer " + token).encode()):
        return reply("401 Unauthorized", {"error": "UNAUTHORIZED"})
    try:
        query = candle_query(environ.get("QUERY_STRING", ""))
    except ValueError:
        return reply("400 Bad Request", {"error": "INVALID_QUERY"})
    try:
        store = create_store_from_env()
        result = store.read_window(**query)
        generated_at_ms = time.time_ns() // 1_000_000
        if query["as_of_ms"] is not None and query["as_of_ms"] > generated_at_ms:
            return reply("400 Bad Request", {"error": "INVALID_QUERY"})
        evaluation_time_ms = (
            query["as_of_ms"] if query["as_of_ms"] is not None else generated_at_ms
        )
        evaluation_anchor = "AS_OF" if query["as_of_ms"] is not None else "GENERATED_AT"
        return reply("200 OK", {
            **result,
            "contractVersion": "1.1.0",
            "schemaVersion": 1,
            "volumeUnit": VOLUME_UNIT,
            "source": DATA_SOURCE,
            "generatedAtMs": generated_at_ms,
            "freshness": _freshness(
                result["candles"], query["timeframe"], evaluation_time_ms,
                result["coverage"].get("complete") is True, evaluation_anchor,
            ),
        })
    except (OSError, sqlite3.Error, ValueError, StoreUnavailable):
        return reply("503 Service Unavailable", {"error": "STORE_UNAVAILABLE"})


if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    with make_server("127.0.0.1", int(os.environ.get("PORT", "8788")), application) as server:
        server.serve_forever()
