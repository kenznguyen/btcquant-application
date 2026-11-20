# T0 FastAPI liveness, timeout and lifecycle baseline

Date: 2026-11-20
Status: **OWNER APPROVED — DESIGN / ISOLATED CI ONLY**

## Decisions

1. `GET /health` remains a liveness-only endpoint. A successful response means the ASGI process can answer the health route; it does not assert that credentials, backend configuration, or the candle store are ready. Do not add a readiness endpoint until a real orchestrator/deployment contract requires one.
2. The following values are the approved design and isolated-test baseline, not a production deployment configuration:

| Layer | Setting | Baseline |
|---|---|---:|
| SQLite | connection timeout | 5 s (preserve current behavior) |
| Nginx | proxy_connect_timeout | 1 s |
| Nginx | proxy_send_timeout | 5 s |
| Nginx | proxy_read_timeout | 7 s |
| Nginx | client_header_timeout | 5 s |
| Nginx | client_body_timeout | 5 s |
| Uvicorn | keep-alive timeout | 5 s |
| Uvicorn | graceful shutdown timeout | 10 s |
| Uvicorn | concurrency limit | 16 |
| Uvicorn | worker count | 1 initially |

Nginx proxy send/read timeouts are inactivity intervals between successive I/O operations, not a guaranteed total request deadline. The end-to-end behavior must be tested rather than treating these values as a single request budget.

## Lifecycle and fail-closed requirements

- Validate required service configuration and backend selection at process startup; do not silently switch backend.
- Begin with one Uvicorn worker and bounded concurrency (16).
- Preserve read-only access to canonical T0 data; no schema creation, writes, migrations, or automatic repair.
- Storage/configuration errors fail closed; no stale cache, synthetic candle, or alternate venue fallback.
- On SIGTERM, stop accepting new work and allow in-flight work to drain for at most 10 seconds, then exit.
- Nginx and Uvicorn must exit cleanly under the isolated harness. A future supervisor may use bounded restart attempts and backoff, but no supervisor is configured or authorized now.
- Keep listeners loopback-only in the test harness, run non-root, redact credentials, and never put bearer tokens in URLs or logs.
- `/health` is not a readiness or dependency-health signal. If readiness is later required, define a separate fail-closed contract that checks configuration/backend/read capability without creating a database/schema or writing canonical T0.

## Scope approved for this increment

- Update decision/evidence/handoff documentation.
- Add regression coverage to the disposable Uvicorn/Nginx integration harness.
- Run isolated GitHub Actions only.

## Explicitly not authorized

No VPS access, canonical T0 SQLite access, production Nginx/Uvicorn config, persistent runtime, systemd/autostart, supervisor installation, public ingress/firewall change, deployment, PostgreSQL activation, T1/T2 connection, trading, or AI/Core execution.

## Acceptance criteria

- Harness launches Uvicorn with the approved keep-alive, graceful-shutdown and concurrency arguments.
- Harness applies the approved Nginx timeout directives and validates its configuration.
- Uvicorn SIGTERM exits successfully within the approved 10-second grace period; Nginx SIGTERM exits cleanly.
- Existing auth, read-only route, proxy, upstream-down, and token-redaction checks remain intact.
- CI evidence is tied to the exact source SHA and does not mount/access canonical T0 data.

## Status

Decision **APPROVED**. Implementation is limited to the isolated harness. Production runtime configuration and lifecycle remain **NOT VERIFIED**; genuine independent second-person review remains **PENDING**.
