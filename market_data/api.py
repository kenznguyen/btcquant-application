"""Read-only canonical candle API. Collection happens separately through sync.py."""

import hmac
import json
import os
import sqlite3
import time

from market_data.postgres import StoreUnavailable
from market_data.storage import create_store_from_env
from market_data.api_contract import DATA_SOURCE, VOLUME_UNIT, _freshness, candle_query


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
