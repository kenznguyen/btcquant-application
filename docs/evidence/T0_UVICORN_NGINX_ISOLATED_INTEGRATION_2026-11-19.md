# T0 Uvicorn process/socket and Nginx isolated integration — 2026-11-19

## Scope and owner authorization

The owner requested an isolated GitHub Actions integration check for a real Uvicorn process/socket and an Nginx reverse proxy, while retaining test-only operation and prohibiting real trading.

Authorized scope:
- Add a disposable CI integration harness that starts Uvicorn as a subprocess on `127.0.0.1`.
- Start a real Nginx subprocess on `127.0.0.1` and proxy to Uvicorn.
- Exercise the HTTP path through Nginx, including Authorization forwarding and failure behavior.
- Use only a temporary synthetic SQLite fixture and a dummy CI token.
- Run the integration container non-root, read-only except bounded `/tmp`, with external network disabled.

Explicit exclusions:
- No VPS/Scaleway SSH or remote execution.
- No systemd, autostart, service installation, persistent process, public listener, DNS, TLS or production Nginx configuration.
- No canonical T0 SQLite mount/read/write; no feeder, writer, lease, scheduler or recovery access.
- No T1/T2, exchange, strategy, risk engine, order endpoint, credentials or real orders.
- No production-readiness certification.

## Implementation

Repository: `kenznguyen/btcquant-application`, branch `main`.

- Integration harness: `market_data/uvicorn_nginx_smoke.py`.
- Workflow: `.github/workflows/t0-fastapi-migration.yml`, new job `uvicorn-nginx-socket-integration`.
- Exact tested source/workflow commit: `65661cd4a2492f9552fe05186581c66d14fbe293`.
- Harness blob SHA: `38e5fcdf10990af265f68f3597cdfef386f5a0aa`.
- Workflow blob SHA: `82b65cad3ea90d437d73998f33384f66b543431b`.
- Previous source commit for harness: `3821a082fb6a48470366cceacba239968e1cac83`.
- Runtime dependency lock unchanged; SHA-256 verified by workflow against `requirements-market-data-fastapi.sha256`. Uvicorn remains pinned in `requirements-market-data-fastapi.lock`.

The job builds an ephemeral image from the pinned CPython 3.12.16 slim image, installs Nginx and the committed hash-pinned FastAPI runtime lock, then runs the integration container with `--network none`, read-only root, UID 65534, dropped capabilities, no-new-privileges, bounded PID/CPU/memory and a bounded temporary filesystem. Both listeners bind only to loopback.

## Integration assertions — PASS

The real-process integration step completed successfully and asserted:
1. Uvicorn subprocess starts and opens its loopback TCP socket.
2. Nginx subprocess starts and opens its loopback TCP socket.
3. Nginx `GET /health` reaches Uvicorn and returns the stable health payload and `Cache-Control: no-store`.
4. Nginx forwards the synthetic Bearer Authorization header; `GET /v1/candles` returns Candle Contract 1.1.0 with exact decimal strings and complete fixture coverage.
5. Missing Bearer token returns 401 / `UNAUTHORIZED`.
6. Unknown route returns 404 / `NOT_FOUND`.
7. POST returns 405 / `METHOD_NOT_ALLOWED` with `Allow: GET`.
8. Stopping Uvicorn causes Nginx to return 502 for the upstream failure.
9. The dummy Bearer token is absent from Nginx access/error logs.

The fixture is created and removed inside the integration process. No canonical database is mounted. The integration test has no external network access.

## Exact-SHA CI evidence

### FastAPI workflow

- Workflow run: [44550458804](https://github.com/kenznguyen/btcquant-application/actions/runs/44550458804)
- Exact head SHA: `65661cd4a2492f9552fe05186581c66d14fbe293`
- Overall conclusion: **SUCCESS**
- Uvicorn/Nginx job: `135652465869` — **SUCCESS**
- Existing FastAPI contract job: `135652465887` — **SUCCESS**
- Runtime-lock-only smoke job: `135652465650` — **SUCCESS**
- Integration artifact: `14543536038`, `t0-uvicorn-nginx-socket-integration`
- Integration artifact SHA-256: `af07b99fa0a53ff315bad148c508533ea0e808d6365fc2c81faafa11ebe8c872`
- FastAPI contract artifact: `14541653518`, SHA-256 `cdcc7a4c039c1b3fe4115c3d770c42754312b660efd384bc34319e59a447cdaa`
- Runtime smoke artifact: `14543502169`, SHA-256 `e6779dd50b10d003e0e850c35cab245e003f9e5babafd3f8ee5be45ca7a1b6e7`

### SQLite-only aggregate workflow

- Workflow run: [44550458851](https://github.com/kenznguyen/btcquant-application/actions/runs/44550458851)
- Exact head SHA: `65661cd4a2492f9552fe05186581c66d14fbe293`
- Aggregate SQLite-only job: `135652463602` — **SUCCESS**
- Artifact: `14543096166`, `t0-sqlite-aggregate-evidence`
- Artifact SHA-256: `852ce0109b95bd7f9d021d9fc2ccda4db076409f45cf189d989d2dd7c4bdd78f`

## Status

- Uvicorn process start/stop and real loopback socket: **PASS** (CI only).
- Nginx process start/stop and real loopback reverse proxy: **PASS** (CI only).
- HTTP contract/auth/header/error/upstream-failure checks through Nginx: **PASS** for the enumerated cases.
- FastAPI existing contract suite: **PASS** on the same SHA.
- SQLite-only aggregate regression: **PASS** on the same SHA.
- VPS/Scaleway process/socket and Nginx integration: **NOT VERIFIED**.
- Persistent runtime, systemd/autostart, public ingress, TLS, load/performance, operational security and production readiness: **NOT VERIFIED / NOT AUTHORIZED**.
- Live trading and real orders: **NOT AUTHORIZED**; paper-first and `ai_execution_enabled=false` remain unchanged.

## Next step and limits

The isolated CI integration gate is complete. A separate owner decision is required before any VPS probe, deployment, persistent service, Nginx modification, public endpoint, TLS or runtime activation. Do not infer VPS readiness from this CI result.
