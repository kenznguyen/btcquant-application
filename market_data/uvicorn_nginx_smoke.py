"""Isolated real-process Uvicorn + Nginx loopback integration smoke.

This test creates its own temporary SQLite fixture and never reads canonical T0 data.
Both listeners are restricted to 127.0.0.1; the CI container runs without network access.
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlencode

from market_data.store import CandleStore, INTERVAL_MS


TOKEN = "ci-only-dummy-bearer-token"
TIMEOUT_SECONDS = 10


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def request(url, method="GET", headers=None):
    req = urllib.request.Request(url, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=3) as response:
            return response.status, response.headers, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers, exc.read()


def wait_for_process(proc, log_path, label):
    deadline = time.monotonic() + TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"{label} exited early ({proc.returncode}): {log_path.read_text(errors='replace')}")
        try:
            with socket.create_connection(("127.0.0.1", proc._probe_port), timeout=0.2):
                return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError(f"{label} did not open its loopback socket: {log_path.read_text(errors='replace')}")


def main():
    if os.getuid() == 0:
        raise RuntimeError("Integration container must run as non-root")
    nginx = shutil.which("nginx")
    if not nginx:
        raise RuntimeError("nginx binary is required")
    root = Path(tempfile.mkdtemp(prefix="t0-uvicorn-nginx-", dir="/tmp"))
    uvicorn_port, nginx_port = free_port(), free_port()
    interval = INTERVAL_MS["15m"]
    now_ms = time.time_ns() // 1_000_000
    open_ms = ((now_ms - 3 * interval) // interval) * interval
    db_path = root / "fixture.sqlite3"
    CandleStore(db_path)
    import sqlite3
    with sqlite3.connect(db_path) as db:
        db.execute(
            """INSERT INTO candles (
                exchange, market_type, symbol, timeframe, open_time_ms,
                open, high, low, close, volume, available_at_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("binance", "USDT_PERPETUAL", "BTCUSDT", "15m", open_ms,
             "100.01", "101", "99", "100.5", "2.50", open_ms + interval + 7),
        )
        db.commit()

    nginx_root = root / "nginx"
    for directory in ("logs", "client_body", "proxy", "fastcgi", "uwsgi", "scgi"):
        (nginx_root / directory).mkdir(parents=True, exist_ok=True)
    access_log = nginx_root / "logs" / "access.log"
    nginx_conf = nginx_root / "nginx.conf"
    nginx_conf.write_text(f"""
worker_processes 1;
pid {nginx_root / 'nginx.pid'};
error_log {nginx_root / 'logs' / 'error.log'} notice;
events {{ worker_connections 64; }}
http {{
    access_log {access_log};
    client_body_temp_path {nginx_root / 'client_body'};
    proxy_temp_path {nginx_root / 'proxy'};
    fastcgi_temp_path {nginx_root / 'fastcgi'};
    uwsgi_temp_path {nginx_root / 'uwsgi'};
    scgi_temp_path {nginx_root / 'scgi'};
    server {{
        listen 127.0.0.1:{nginx_port};
        server_name localhost;
        client_header_timeout 5s;
        client_body_timeout 5s;
        location / {{
            proxy_pass http://127.0.0.1:{uvicorn_port};
            proxy_connect_timeout 1s;
            proxy_send_timeout 5s;
            proxy_read_timeout 7s;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header Authorization $http_authorization;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}
    }}
}}
""".strip() + "\n")

    env = dict(os.environ)
    env.update({
        "MARKET_DATA_BACKEND": "sqlite",
        "MARKET_DATA_DB": str(db_path),
        "MARKET_DATA_TOKEN": TOKEN,
        "PYTHONDONTWRITEBYTECODE": "1",
    })
    uvicorn_log = root / "uvicorn.log"
    nginx_log = root / "nginx-process.log"
    uvicorn_handle = uvicorn_log.open("w")
    nginx_handle = nginx_log.open("w")
    uvicorn_proc = nginx_proc = None
    results = []
    completed = False
    try:
        uvicorn_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "market_data.fastapi_app:app",
             "--host", "127.0.0.1", "--port", str(uvicorn_port),
             "--workers", "1", "--timeout-keep-alive", "5",
             "--timeout-graceful-shutdown", "10", "--limit-concurrency", "16",
             "--no-access-log"],
            cwd=Path.cwd(), env=env, stdout=uvicorn_handle, stderr=subprocess.STDOUT,
        )
        uvicorn_proc._probe_port = uvicorn_port
        wait_for_process(uvicorn_proc, uvicorn_log, "Uvicorn")
        nginx_proc = subprocess.Popen(
            [nginx, "-p", str(nginx_root) + "/", "-c", str(nginx_conf), "-g", "daemon off;"],
            cwd=root, env=env, stdout=nginx_handle, stderr=subprocess.STDOUT,
        )
        nginx_proc._probe_port = nginx_port
        wait_for_process(nginx_proc, nginx_log, "Nginx")
        subprocess.run(
            [nginx, "-p", str(nginx_root) + "/", "-c", str(nginx_conf), "-t"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        results.append("nginx_timeout_configuration_valid=PASS")

        base = f"http://127.0.0.1:{nginx_port}"
        code, headers, body = request(base + "/health")
        assert code == 200 and json.loads(body) == {
            "ok": True, "service": "canonical-market-data"
        }
        assert headers.get("Cache-Control") == "no-store"
        assert headers.get("Content-Type") == "application/json; charset=utf-8"
        results.append("nginx_to_uvicorn_health=PASS")

        query = urlencode({
            "symbol": "BTCUSDT", "timeframe": "15m",
            "startMs": open_ms, "endMs": open_ms + interval,
        })
        code, headers, body = request(
            base + "/v1/candles?" + query,
            headers={"Authorization": "Bearer " + TOKEN},
        )
        payload = json.loads(body)
        assert code == 200 and payload["contractVersion"] == "1.1.0"
        assert payload["candles"][0]["open"] == "100.01"
        assert payload["candles"][0]["volume"] == "2.5"
        assert payload["coverage"]["complete"] is True
        assert headers.get("Cache-Control") == "no-store"
        results.append("authorization_forwarding_and_candle_contract=PASS")

        code, _, body = request(base + "/v1/candles?" + query)
        assert code == 401 and json.loads(body) == {"error": "UNAUTHORIZED"}
        results.append("missing_bearer_rejected=PASS")

        code, headers, body = request(base + "/v1/unknown")
        assert code == 404 and json.loads(body) == {"error": "NOT_FOUND"}
        results.append("unknown_route=PASS")

        code, headers, body = request(
            base + "/v1/candles", method="POST",
            headers={"Authorization": "Bearer " + TOKEN},
        )
        assert code == 405 and headers.get("Allow") == "GET"
        assert json.loads(body) == {"error": "METHOD_NOT_ALLOWED"}
        results.append("non_get_rejected=PASS")

        uvicorn_proc.terminate()
        uvicorn_proc.wait(timeout=12)
        assert uvicorn_proc.returncode == 0
        uvicorn_proc = None
        results.append("uvicorn_sigterm_graceful_exit=PASS")
        code, _, _ = request(base + "/health")
        assert code == 502
        results.append("upstream_shutdown_returns_502=PASS")

        nginx_proc.terminate()
        nginx_proc.wait(timeout=5)
        assert nginx_proc.returncode == 0
        nginx_proc = None
        results.append("nginx_sigterm_clean_exit=PASS")

        for log_path in (access_log, nginx_root / "logs" / "error.log"):
            if log_path.exists():
                assert TOKEN not in log_path.read_text(errors="replace")
        results.append("bearer_token_absent_from_nginx_logs=PASS")

        print("\n".join(results))
        print(f"nginx_version={subprocess.check_output([nginx, '-v'], stderr=subprocess.STDOUT, text=True).strip()}")
        print("listeners=127.0.0.1_only")
        print("database=temporary_sqlite_fixture_only")
        print("canonical_t0_database=NOT_MOUNTED")
        print("external_network_during_test=DISABLED")
        completed = True
    finally:
        for proc in (nginx_proc, uvicorn_proc):
            if proc is not None and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=12 if proc is uvicorn_proc else 5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=5)
        uvicorn_handle.flush()
        nginx_handle.flush()
        if not completed:
            print("=== FAILURE DIAGNOSTICS ===", flush=True)
            print(f"diagnostic_directory={root}", flush=True)
            for label, proc, log_path in (
                ("uvicorn", uvicorn_proc, uvicorn_log),
                ("nginx", nginx_proc, nginx_log),
            ):
                returncode = None if proc is None else proc.poll()
                print(f"{label}_returncode={returncode}", flush=True)
                print(f"--- {label} stdout/stderr: {log_path} ---", flush=True)
                try:
                    print(log_path.read_text(errors="replace"), flush=True)
                except OSError as exc:
                    print(f"log_read_error={exc!r}", flush=True)
            for label, log_path in (
                ("nginx_access", access_log),
                ("nginx_error", nginx_root / "logs" / "error.log"),
            ):
                print(f"--- {label}: {log_path} ---", flush=True)
                if log_path.exists():
                    print(log_path.read_text(errors="replace"), flush=True)
            print("temporary_diagnostics_preserved=YES", flush=True)
        uvicorn_handle.close()
        nginx_handle.close()
        if completed:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
