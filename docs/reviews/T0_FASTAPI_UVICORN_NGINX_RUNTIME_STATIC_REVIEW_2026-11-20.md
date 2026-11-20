# T0 FastAPI / Uvicorn / Nginx — Runtime Configuration Static Review

- Date: 2026-11-20
- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Current HEAD inspected: `86354b2e1eb71d9c8443d85183d696a12833b317`
- Exact CI-tested source SHA: `a20c51281c2fbee92e3363109bbc35f767084be4`
- Compare: current HEAD is 2 commits ahead / 0 behind the tested source; only `docs/PROJECT_SESSION_HANDOFF.md` differs. Runtime/application source, workflow and dependency locks are unchanged from the tested SHA.
- Workflow: `.github/workflows/t0-fastapi-migration.yml`, blob `82b65cad3ea90d437d73998f33384f66b543431b`.
- Review type: read-only adversarial static review by the same ChatGPT assistant that previously participated in the project. **This is not a genuine independent second-person review or security certification.**
- Scope: FastAPI adapter, storage selection/read path, shared query contract, runtime dependency lock, in-process smoke, Uvicorn/Nginx integration harness and workflow.
- No source changes, tests, workflow dispatch, service startup, endpoint probes, credentials, VPS, canonical T0 SQLite, T1/T2 or trading access occurred during this review.

## 1. Executive disposition

**STATIC REVIEW: PASS WITH OPERATIONAL QUALIFICATION BLOCKERS.**

The application-level candle route has sound fail-closed characteristics for the inspected paths: constant-time bearer comparison, bounded query parsing, GET-only behavior, read-only SQLite URI, no implicit database initialization, explicit backend selection and generic store errors. The synchronous route is appropriate for the blocking SQLite read path.

However, the repository does not contain a production Uvicorn launch definition, production Nginx configuration, service supervisor configuration or explicit operational timeout/restart policy. The only real-process configuration is a disposable CI smoke harness. The existing CI PASS must therefore remain **CI ONLY**; it is not sufficient to approve VPS or production runtime.

## 2. Findings

### F-01 — MEDIUM — `/health` is liveness-only, not readiness

**Location:** `market_data/fastapi_app.py`, `dispatch()`, `/health` branch (approximately lines 53–55).

The handler returns HTTP 200 immediately and does not check `MARKET_DATA_TOKEN`, backend selection, SQLite path existence/readability, or the selected store. Consequently, an instance can report healthy while every `GET /v1/candles` request fails closed with 503.

**Impact:** if a future Nginx upstream check, supervisor or operator treats this endpoint as readiness, it can route traffic to an unusable instance or report a false-ready state.

**Disposition:** not a defect if explicitly defined and consumed as liveness only. Document that contract and keep readiness separate. A readiness check must validate required configuration and the read-only store without creating/initializing a database or touching the canonical data during a probe. No change is authorized by this review.

### F-02 — MEDIUM / QUALIFICATION BLOCKER — No production Uvicorn/Nginx runtime configuration exists in the inspected source

**Evidence:**
- The only Uvicorn launch command is in `market_data/uvicorn_nginx_smoke.py`: loopback host, ephemeral port, one worker and access log disabled.
- The only Nginx configuration is generated dynamically inside that test harness and listens on loopback.
- The repository tree contains no production Nginx server configuration, Uvicorn deployment entrypoint, systemd/service unit, container runtime manifest for this service, or supervisor policy.

**Impact:** production binding, TLS termination, trusted proxy boundary, process ownership, privilege separation, environment/secret injection, restart policy, log rotation, graceful shutdown and resource limits cannot be assessed from source. The CI harness intentionally does not represent those deployment settings.

**Disposition:** deployment/runtime remains **NOT VERIFIED / NOT AUTHORIZED**. This is a missing operational artifact, not a finding that the CI harness should be exposed publicly. Do not create or activate a production config as part of this review.

### F-03 — MEDIUM — Proxy and graceful-shutdown timeout policy is implicit

**Location:** Nginx config generated in `market_data/uvicorn_nginx_smoke.py`; Uvicorn command in the same file.

The test Nginx server sets `proxy_pass` and forwarded headers but does not set explicit `proxy_connect_timeout`, `proxy_read_timeout` or `proxy_send_timeout`. The Uvicorn command does not explicitly define graceful-shutdown timeout, keep-alive timeout, concurrency/backlog limits or worker lifecycle policy. The API's SQLite connection timeout is bounded at 5 seconds; the PostgreSQL adapter also defines 5-second connect/statement/lock timeouts, but these do not define the Nginx↔Uvicorn timeout budget. PostgreSQL is not activated by this review.

**Impact:** effective proxy/server timeout behavior depends on defaults and version. There is no reviewed end-to-end timeout budget ensuring a slow store read is terminated predictably or that shutdown drains in-flight requests within an agreed bound.

**Disposition:** define explicit values and an ordered timeout budget in a separately approved runtime design before any persistent runtime. No values are prescribed here because expected request latency and shutdown requirements have not been approved.

### F-04 — MEDIUM — Process lifecycle evidence covers startup and upstream loss, not graceful lifecycle/recovery

**Location:** `market_data/uvicorn_nginx_smoke.py`, `wait_for_process()`, process start/stop and `finally` cleanup.

The harness verifies that each process opens a TCP socket, exercises HTTP through Nginx, terminates Uvicorn and observes Nginx return 502. It does not verify:
- HTTP readiness before declaring each process ready (the initial wait is a TCP connect check);
- graceful draining of an in-flight request;
- clean Nginx shutdown and worker reaping;
- restart/recovery after Uvicorn or Nginx exits;
- repeated restart, signal propagation or supervisor behavior;
- bounded shutdown under a stuck handler.

The cleanup sends terminate, waits up to five seconds and then kills the process if needed. That is useful test cleanup, not a production lifecycle policy.

**Impact:** process start/stop and upstream-failure detection are demonstrated only for the narrow CI scenario. Persistence, restart and graceful shutdown remain unverified.

**Disposition:** retain CI result as **PASS for enumerated integration assertions only**. Runtime lifecycle/recovery remains **NOT VERIFIED**.

### F-05 — LOW — Unauthenticated configuration-state distinction

**Location:** `market_data/fastapi_app.py`, token/backend configuration checks before bearer authentication.

When the token or required SQLite path is absent, the endpoint returns 503 `UNCONFIGURED` before authenticating. A configured service returns 401 for a missing/incorrect token. An unauthenticated caller can therefore distinguish unconfigured from configured state.

**Impact:** limited configuration/readiness information disclosure. The response does not expose the token, DSN, filesystem path or exception detail. This behavior was previously documented as inherited WSGI contract behavior.

**Disposition:** record as accepted residual behavior for current contract, or consider normalizing the unauthenticated response in a future separately approved contract/security change. No change made.

## 3. Positive controls observed

- `hmac.compare_digest` is used for the exact Bearer value; token is not accepted from query parameters.
- FastAPI docs, ReDoc and OpenAPI endpoints are disabled.
- Middleware rejects all non-GET methods before route dispatch; unknown paths return 404.
- `Cache-Control: no-store` is applied to adapter responses.
- Query parser limits raw query length to 2,048 characters, fields to five, rejects duplicate/unknown parameters, and caps the requested window at 2,000 candles.
- Candle route is a synchronous `def` handler, avoiding direct blocking SQLite calls inside an `async def` route.
- SQLite read path checks that the DB file exists and opens it with URI `mode=ro`; it does not create schema or initialize the DB.
- Backend selection is explicit; unknown/incomplete backend configuration raises a configuration error that maps to generic 503. No silent SQLite fallback is present for an explicit PostgreSQL selection.
- Expected storage/configuration errors map to generic error bodies rather than returning exception text.
- Runtime dependencies, including FastAPI/Uvicorn, are version-locked with SHA-256 hashes. The CI Python image is digest-pinned.
- The CI integration binds both listeners to loopback, uses a temporary fixture and dummy token, runs non-root with read-only root, dropped capabilities, no-new-privileges, bounded resources and external network disabled.
- The integration checks Authorization forwarding, missing-token rejection, method/path errors, upstream shutdown 502 and absence of the dummy token from Nginx access/error logs.

## 4. Timeout and lifecycle matrix

| Boundary | Source evidence | Assessment |
|---|---|---|
| SQLite connection | 5-second connect timeout in `market_data/store.py` | Bounded |
| PostgreSQL connect/statement/lock | 5 seconds in `market_data/postgres.py` | Bounded in code; backend not activated |
| Query size/window | 2,048-byte query; max 2,000 API candles | Bounded |
| Client request timeout in CI harness | 3 seconds in `request()` | Test-only |
| Process startup wait in CI harness | 10 seconds, TCP socket probe | Test-only; not HTTP readiness |
| Nginx proxy connect/read/send | Not explicitly configured | NOT VERIFIED |
| Uvicorn graceful shutdown / keep-alive / concurrency | Not explicitly configured in launch command | NOT VERIFIED |
| Supervisor restart / process persistence | No service definition | NOT VERIFIED |

## 5. Exact-source and CI qualification

- CI run [44689777567](https://github.com/kenznguyen/btcquant-application/actions/runs/44689777567), run number 40, event `workflow_dispatch`, exact source SHA `a20c51281c2fbee92e3363109bbc35f767084be4`: overall SUCCESS.
- FastAPI contract job `136132549651`: 50 tests PASS.
- Runtime-lock install + in-process ASGI smoke job `136132549745`: PASS.
- Uvicorn process/socket + Nginx loopback integration job `136132549996`: PASS.
- Artifacts:
  - Contract evidence ID `14607339737`, SHA-256 `e6a81ef582329ac2480022018b48daad568731c924d921e77fddee600ddfe3f7`.
  - Runtime-lock smoke ID `14608650299`, SHA-256 `8d3c569084472adb4c23adf346d99d8b7bbcf881577e56d5226398f4fba558d4`.
  - Uvicorn/Nginx integration ID `14608046967`, SHA-256 `343fd8bd1b94744f825d217316bc6f50033c6719985ce5e76cd49a13fbf80db9`.
- Current main HEAD `86354b2e1eb71d9c8443d85183d696a12833b317` compares 2 ahead / 0 behind the tested SHA; the only changed path is this handoff documentation. The runtime source, workflow and lock files are unchanged.
- The CI integration proves only its enumerated ephemeral loopback scenario. It does not prove production Nginx settings, public TLS, VPS service behavior, restart policy, load/concurrency, or production readiness.

## 6. Overall decision

| Dimension | Result |
|---|---|
| FastAPI application security boundary | PASS for inspected static controls; not security-certified |
| Fail-closed storage behavior | PASS for candle route and inspected storage selection |
| Health/readiness semantics | FINDING F-01 |
| Uvicorn/Nginx production configuration | BLOCKED / NOT PRESENT |
| Explicit proxy/server timeout policy | NOT VERIFIED |
| Process lifecycle/recovery | PARTIAL CI PASS; operational lifecycle NOT VERIFIED |
| CI exact-SHA evidence | PASS |
| VPS/production readiness | NOT VERIFIED / NOT AUTHORIZED |
| Genuine independent second-person review | PENDING |

**Review verdict:** do not approve persistent runtime/deployment on the basis of this source and CI evidence alone. The application adapter is suitable for continued isolated CI validation, subject to the readiness semantic being explicitly documented. A production runtime review requires an owner-approved, separately scoped deployment configuration and runtime validation. T0 canonical data, VPS, T1/T2, PostgreSQL activation, trading and deployment remain outside this review.

## 7. Scope and next gate

Read-only review only. No source, test, workflow, dependency, runtime, database, VPS, secret, T1/T2 or trading change was made. No test was executed or dispatched during this review.

Next gate: preserve the CI-only PASS; decide whether `/health` is formally liveness-only and define a separate readiness contract if required. Separately, request approval for a production runtime configuration review before any deployment or persistent process. This report does not satisfy the genuine independent second-person review requirement.
