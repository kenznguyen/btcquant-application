# T0 FastAPI Migration — Architecture Decision and Plan

- Date: 2026-11-19
- Repository: `kenznguyen/btcquant-application`
- Branch: `main` (existing branch; no branch or PR split)
- Decision status: **APPROVED — TARGET ARCHITECTURE**
- Implementation status: **NOT STARTED — NOT AUTHORIZED BY THIS DECISION**
- Runtime/deployment status: **NOT AUTHORIZED**

## 1. Decision

FastAPI is the target HTTP API framework for the Five-Layer System. T0 will migrate its existing read-only WSGI Candle API to FastAPI now, before further cross-layer HTTP integration expands the WSGI dependency surface.

This is an architecture decision and migration-plan approval only. It does not authorize source implementation, dependency installation/lock changes, test edits or execution, CI dispatch, endpoint probes, runtime connection, deployment, canonical database access/mutation, T1/T2 activation or trading. Source implementation requires a separate explicit approval.

## 2. Rationale

- The target system architecture has standardized on FastAPI; aligning T0 early avoids expanding a framework-specific WSGI boundary and reduces later migration cost.
- T0 is not certified for production operation, so the HTTP framework can be changed before a production deployment depends on the current WSGI entrypoint.
- FastAPI provides typed request/response boundaries, Pydantic validation, generated OpenAPI documentation and an ASGI service interface.
- These benefits apply to the HTTP boundary only. They do not justify restructuring T0's canonical data, writer, feeder or storage architecture.

## 3. Architecture boundary

Target request path:

`Consumers → Nginx API Gateway → FastAPI service → read-only Candle service/store interface → canonical T0 SQLite`

- Nginx remains the gateway for routing and edge controls; FastAPI does not replace Nginx.
- T0 remains an independent data asset and canonical SQLite owner.
- FastAPI is an HTTP adapter only. It must not acquire candles, write candles, manage leases, initialize databases, run migrations or expose order/trading endpoints.
- Keep SQLite access synchronous at the route boundary unless profiling and a separate design justify another execution model. Do not put blocking SQLite calls directly in an `async def` route.
- Do not retain two public HTTP implementations as a permanent dual stack. The migration should converge on one FastAPI application after compatibility is demonstrated.

## 4. Existing contract to preserve

The current authoritative API is Candle Contract **1.1.0**, not the earlier 1.0.0 contract.

Preserve:
- `GET /v1/candles` and `GET /health`.
- Bearer authentication using `MARKET_DATA_TOKEN`; constant-time token comparison; no token in query strings or logs.
- BTCUSDT and supported 15m/1h timeframes; UTC millisecond timestamps; half-open `[startMs,endMs)` windows; maximum 2,000 candles.
- Optional `asOfMs`, rejection of future anchors, and the distinction between `generatedAtMs` and `evaluationTimeMs`.
- Contract/schema versions, market identity, source, volume unit, dataset version, coverage and gap representation.
- Freshness semantics: `evaluationAnchor`, `timestampValid`, `fresh` and `evaluable`; evaluability requires complete coverage, valid timestamps and a fresh latest closed candle.
- Decimal OHLCV serialization and existing JSON field names/types.
- `Cache-Control: no-store`, existing authentication/configuration/store failure behavior, and method/path semantics (including 400 for invalid query, 401 unauthorized, 405 non-GET, 404 unknown path, 503 unavailable/unconfigured).
- Read-only behavior: missing SQLite path must fail closed and must never create a database.

FastAPI's default validation response (commonly 422) must not silently replace the current 400 invalid-query contract. Explicitly map errors to the established response envelope and status codes. Typed response validation must not coerce decimal strings, omit fields or change nullability.

## 5. Migration plan and gates

### Gate A — contract and dependency design
- Design the FastAPI application/router boundary and lifespan behavior.
- Define typed query/response models without changing externally visible JSON.
- Decide documentation/OpenAPI exposure policy for internal service use.
- Inventory direct runtime dependencies and test-client dependencies.
- Select compatible FastAPI, Starlette, Pydantic and ASGI server versions only after compatibility review.
- Create a separate exact-version, SHA-256-hashed lock for the CPython 3.12 / Linux x86_64 target. Preserve the existing lock as historical evidence until the new lock passes the same offline compatibility gate.
- Do not add PostgreSQL dependencies.

### Gate B — source implementation (requires separate approval)
- Add the FastAPI adapter while keeping the Candle contract and storage interfaces unchanged.
- Extract only the minimal reusable HTTP-independent logic if necessary; avoid a broad refactor.
- Keep blocking SQLite operations on synchronous route handlers or a deliberate bounded worker boundary.
- Remove the WSGI entrypoint only after all contract tests pass and independent review accepts the replacement. Do not keep a permanent dual public API.

### Gate C — tests and CI (requires separate approval)
- Add ASGI tests for every existing API behavior and the complete 1.1.0 response schema.
- Add explicit tests for 400-vs-422 behavior, 401, 404, 405/Allow, 503, no-store, missing DB non-creation, decimal string preservation, future `asOfMs`, freshness/evaluability and read-only constraints.
- Preserve and run the existing SQLite-only aggregate allowlist (currently 196 tests) plus new FastAPI tests. Do not weaken, silently drop or broaden the allowlist to PostgreSQL/runtime tests.
- Run dependency hash/download and clean offline installation checks on the pinned target.
- Require exact-SHA workflow evidence, artifact inspection and independent code review.

### Gate D — runtime qualification (separate approval after source GREEN)
- Separately approve any endpoint probe, service startup, Nginx routing, VPS process, systemd or deployment work.
- Do not infer runtime readiness from unit/contract tests.

## 6. Explicit non-goals and safety constraints

- No change to canonical SQLite schema, database file, historical data, data retention or T0 ownership.
- No changes to writer fencing, leases, feeder, scheduler, recovery or CCXT ingestion.
- PostgreSQL/TimescaleDB remains PARKED.
- No T1/T2 consumer connection or cross-layer activation in this migration.
- No VPS/systemd/autostart/deployment change.
- No paper/live execution change, AI execution enablement or real orders.
- No automatic deletion, TTL, cleanup, archive, compaction, vacuum or backup expiry.

## 7. Baseline and evidence at decision time

- Current T0 API source blob: `market_data/api.py` = `4f923d400b8e133a602cec7239982fdf357e9e21` (Candle Contract 1.1.0).
- Current API test blob: `market_data/test_api.py` = `add00a2a91899d8e496df5b64c122442fc7c65c9`.
- Existing dependency manifest blob: `requirements-market-data.txt` = `107b1bad04982506a8023cd784d5d0dafae3e41a` (CCXT and Gunicorn; describes current WSGI serving).
- Existing lock blob: `requirements-market-data.lock` = `0a78b53d6d142d2ddc526a31e368adf4562bcb22` (25 packages, CPython 3.12/Linux x86_64; not a FastAPI lock).
- Existing selected SQLite aggregate evidence: run [44515824622](https://github.com/kenznguyen/btcquant-application/actions/runs/44515824622), exact tested SHA `8f49439fafc95186a8c854fe482aad707525a658`, 196/196 PASS.
- Existing API/Storage evidence: run [44515824664](https://github.com/kenznguyen/btcquant-application/actions/runs/44515824664), 21/21 PASS.
- These runs predate the FastAPI migration and are baseline evidence only; they do not test or certify FastAPI.

## 8. Current disposition

- Architecture decision: **APPROVED**.
- Migration plan: **RECORDED**.
- Source implementation: **NOT STARTED / REQUIRES SEPARATE APPROVAL**.
- New dependencies and lock: **NOT CHANGED / NOT VERIFIED**.
- Tests and workflows: **NOT RUN for FastAPI**.
- Endpoint/runtime/deployment: **NOT AUTHORIZED / NOT VERIFIED**.
- Production readiness: **NOT CERTIFIED**.
