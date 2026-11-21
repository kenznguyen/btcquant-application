"""FastAPI ASGI adapter for the read-only T0 Candle Contract 1.1.0."""

import hmac
import os
import sqlite3
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from market_data.api_contract import candle_envelope, candle_query
from market_data.postgres import StoreUnavailable
from market_data.storage import create_store_from_env


app = FastAPI(
    title="Canonical Market Data API",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


def _reply(status_code, body, headers=None):
    response_headers = {
        "Cache-Control": "no-store",
        "Content-Type": "application/json; charset=utf-8",
    }
    if headers:
        response_headers.update(headers)
    return JSONResponse(status_code=status_code, content=body, headers=response_headers)


@app.middleware("http")
async def enforce_read_only_methods(request: Request, call_next):
    """Reject every non-GET method before route matching, including extension verbs."""
    if request.method != "GET":
        return _reply(
            405,
            {"error": "METHOD_NOT_ALLOWED"},
            {"Allow": "GET"},
        )
    return await call_next(request)


@app.api_route("/", methods=["GET"])
@app.api_route("/{path:path}", methods=["GET"])
def dispatch(request: Request, path: str = ""):
    """Use synchronous handlers because the canonical SQLite read is blocking."""
    route_path = "/" + path if path else "/"
    if route_path == "/health":
        return _reply(200, {"ok": True, "service": "canonical-market-data"})

    if route_path != "/v1/candles":
        return _reply(404, {"error": "NOT_FOUND"})

    token = os.environ.get("MARKET_DATA_TOKEN", "")
    if not token:
        return _reply(503, {"error": "UNCONFIGURED"})

    backend = os.environ.get("MARKET_DATA_BACKEND", "sqlite").strip().lower()
    if backend == "sqlite" and not os.environ.get("MARKET_DATA_DB"):
        return _reply(503, {"error": "UNCONFIGURED"})

    authorization = request.headers.get("authorization", "")
    if not hmac.compare_digest(
        authorization.encode("utf-8"),
        ("Bearer " + token).encode("utf-8"),
    ):
        return _reply(401, {"error": "UNAUTHORIZED"})

    try:
        raw_query = request.scope.get("query_string", b"").decode("ascii")
        query = candle_query(raw_query)
    except (UnicodeDecodeError, ValueError):
        return _reply(400, {"error": "INVALID_QUERY"})

    try:
        store = create_store_from_env()
        result = store.read_window(**query)
        generated_at_ms = time.time_ns() // 1_000_000
        if query["as_of_ms"] is not None and query["as_of_ms"] > generated_at_ms:
            return _reply(400, {"error": "INVALID_QUERY"})

        return _reply(
            200, candle_envelope(result, generated_at_ms, query["as_of_ms"])
        )
    except (OSError, sqlite3.Error, ValueError, StoreUnavailable):
        return _reply(503, {"error": "STORE_UNAVAILABLE"})
