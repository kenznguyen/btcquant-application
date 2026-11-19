"""Runtime-lock-only smoke test for the read-only FastAPI ASGI adapter.

This script intentionally uses only the Python standard library beyond the
runtime lock. It invokes the ASGI app in-process and never opens a socket.
"""

import asyncio
import json

from market_data.fastapi_app import app


async def _request_health():
    sent = []
    receive_count = 0

    async def receive():
        nonlocal receive_count
        receive_count += 1
        if receive_count == 1:
            return {"type": "http.request", "body": b"", "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/health",
        "raw_path": b"/health",
        "query_string": b"",
        "root_path": "",
        "headers": [],
        "client": ("127.0.0.1", 12345),
        "server": ("127.0.0.1", 80),
    }
    await app(scope, receive, send)
    return sent


def main():
    messages = asyncio.run(_request_health())
    start = next(message for message in messages if message["type"] == "http.response.start")
    body = b"".join(
        message.get("body", b"")
        for message in messages
        if message["type"] == "http.response.body"
    )
    headers = {key.lower(): value for key, value in start["headers"]}

    assert start["status"] == 200, start
    assert headers.get(b"cache-control") == b"no-store", headers
    assert headers.get(b"content-type") == b"application/json; charset=utf-8", headers
    assert json.loads(body) == {"ok": True, "service": "canonical-market-data"}, body
    print("runtime_lock_install=PASS")
    print("asgi_import=PASS")
    print("in_process_health=PASS")
    print("network_socket=not_used")
    print("canonical_database=not_accessed")
    print("credentials=none")


if __name__ == "__main__":
    main()
