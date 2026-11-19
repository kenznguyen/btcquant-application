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
- Source implementation: **AUTHORIZED BY OWNER; EXECUTION BLOCKED**.
- New dependencies and lock: **NOT CHANGED / NOT VERIFIED**.
- Tests and workflows: **NOT RUN for FastAPI**.
- Endpoint/runtime/deployment: **NOT AUTHORIZED / NOT VERIFIED**.
- Production readiness: **NOT CERTIFIED**.


## 9. Implementation authorization and execution checkpoint — 2026-11-19

- Owner separately approved TDD/source implementation of the T0 FastAPI migration. Implementation is therefore **AUTHORIZED**, within the scope and exclusions above.
- Execution checkpoint: **BLOCKED — no source/test/dependency changes made**. The available GitHub integration in this session exposes repository read/write operations but no workflow-dispatch operation. A local checkout was attempted and failed because the execution container could not resolve `github.com` (DNS/network unavailable).
- Local Python inspection found Python 3.13.5 with FastAPI 0.128.2, not the certified CPython 3.12.16 target; this environment cannot establish the required target dependency compatibility or replace the pinned CI evidence.
- TDD RED has not been run. No code was written ahead of the failing contract tests. No dependency manifest/lock, workflow, source, canonical data or runtime was changed.
- Next execution prerequisite: run in an environment with repository checkout and GitHub Actions execution capability, first establish the CPython 3.12.16 dependency lock with exact wheel hashes, then add/run contract RED tests before implementing the FastAPI adapter. Do not bypass the dependency gate or claim PASS from the local Python 3.13 environment.
- Current statuses: architecture **APPROVED**; implementation authorization **APPROVED**; execution **BLOCKED**; FastAPI tests **NOT RUN**; runtime/deployment **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**.


## 10. Initial ASGI adapter implementation and CI checkpoint — 2026-11-19

- Initial FastAPI adapter implemented in `market_data/fastapi_app.py`; focused contract tests in `market_data/test_fastapi_api.py`.
- Runtime/test dependency inputs: FastAPI 0.165.0, Uvicorn 0.54.0, httpx2 2.16.2. Starlette 1.10.0 and Pydantic 2.14.3 resolved under the CPython 3.12.16 CI environment.
- Dependency locks were generated with SHA-256 hashes in GitHub Actions. Runtime lock hash `ed5d71e2796303e45266637dc0bffd980e9f869d9c1f25dc61abed8fffa2ee54`; test lock hash `fe4b7109fb211671e90c26a8158b29d7b7d5be6cb0d8be3f9f4c150767bfd7ea`. They are preserved in artifact `14529288115` but are not yet committed to the repository.
- FastAPI focused GREEN: run [44525016702](https://github.com/kenznguyen/btcquant-application/actions/runs/44525016702), exact SHA `f72cff4d78bbfe7beb1a3b3fe1dd6e03fe26a4f5`, **10/10 PASS**, artifact `14529288115`, SHA-256 `6ca6bf9531af536d2cd140e7609934e3b876105c8bfcc4fb6ac74e7a49b4054b`.
- SQLite aggregate on the same exact SHA: run [44525016662](https://github.com/kenznguyen/btcquant-application/actions/runs/44525016662), **196/196 PASS**, artifact `14529039136`, SHA-256 `e4fe7e0bece4353b438c6a22cd7b2c36f27c88b2152fd2d9849b84a88388d09e`.
- Detailed evidence: [T0 FastAPI Initial Adapter Regression](../evidence/T0_FASTAPI_INITIAL_ADAPTER_REGRESSION_2026-11-19.md), report commit `0122ea21d870236230c30f2c5361598fe2e0fa3c`.
- Implementation is **PARTIAL**, not a completed WSGI migration: `market_data/api.py` still contains the WSGI entrypoint and `market_data/test_api.py` still exercises it. Full 1.1.0 parity, committed dependency locks, WSGI removal and independent review remain pending.
- Runtime, endpoint probe, Nginx/VPS/systemd/deployment, T1/T2 connection and trading remain **NOT AUTHORIZED**. PostgreSQL remains PARKED. Production readiness remains **NOT CERTIFIED**.


## 11. Full ASGI contract regression — 2026-11-19

- Expanded ASGI suite to 25 tests, including duplicate query rejection, all non-GET methods, imported-history as-of handling, gap/freshness/evaluability, corrupt data, sync/reopen, and no-fallback behavior.
- FastAPI run [44525859272](https://github.com/kenznguyen/btcquant-application/actions/runs/44525859272), job `135566117694`, exact SHA `a03637372e3090595bf6e48c9426e7e076cf3bdc`: **25/25 PASS**. Artifact `14528454863`, SHA-256 `e6cafec6024a69cfa8fb2fbdfdb30eebfbd32214107455cee28934731b6d9196`.
- SQLite aggregate run [44525859257](https://github.com/kenznguyen/btcquant-application/actions/runs/44525859257), job `135566117671`, same exact SHA: **196/196 PASS**. Artifact `14531695273`, SHA-256 `5aefa96fd860f02a12a71f05f5db7a51c938676d7eff5d20cc3999405b169a6c`.
- Full evidence: [T0 FastAPI Full Contract Regression](../evidence/T0_FASTAPI_FULL_CONTRACT_REGRESSION_2026-11-19.md), report commit `43253b5b797a973fe71350bfe15dfc7bf58f2510`.
- These are source-level tests only. WSGI `application` remains in `market_data/api.py`; existing WSGI tests remain in `market_data/test_api.py`. The WSGI-to-ASGI migration is still **PARTIAL**.
- Exact hashed runtime/test locks remain in the CI artifact and are **not yet committed**. Independent code review remains **PENDING**.
- Runtime/endpoint/deployment and T1/T2 remain **NOT AUTHORIZED**; PostgreSQL remains PARKED; production readiness remains **NOT CERTIFIED**.


## 12. Committed wheel locks, offline test isolation and internal review — 2026-11-19

- Exact paired source SHA: `6558141e7de20c30447cdb9705583e05a7d80592`.
- FastAPI run [44526822603](https://github.com/kenznguyen/btcquant-application/actions/runs/44526822603), job `135569565169`: **25/25 PASS**, artifact `14533180068`, SHA-256 `43b551482bc7952dd92063067413e0464b3bc5680102e1084282bd28a44e6be5`.
- SQLite aggregate run [44526822322](https://github.com/kenznguyen/btcquant-application/actions/runs/44526822322), job `135569525255`, same SHA: **196/196 PASS**, artifact `14532985102`, SHA-256 `3a7d5b948d32c08ec53e527cbeac6c214009f01dba4a4df301bce1ee49f9d3d4`.
- Committed target-specific wheel locks: runtime SHA-256 `fb4cf8f63131cb36636b3c3230378a49bfb2d3a56b8750778ed5b3b5dac8d786`; test SHA-256 `2916098771a482a21637b94fff1f79afc0ddeb37a2a01fdae05032509a889cb6`. The CI verified both with `sha256sum -c`, downloaded wheels, then installed the test environment offline in a `--network none` container.
- Shared contract helpers were extracted to `market_data/api_contract.py`; FastAPI no longer imports the WSGI module. Non-GET middleware and legacy JSON content-type were added and tested.
- Internal five-axis code review: **PASS for current source/test/CI scope**. Independent second-reviewer sign-off remains **PENDING**; do not remove WSGI/Gunicorn until independent review accepts the migration diff.
- Detailed report: [T0 FastAPI Locked Offline CI and Review](../evidence/T0_FASTAPI_LOCKED_OFFLINE_CI_AND_REVIEW_2026-11-19.md), commit `2d130f5e0ddb3d7137febc403f53d9709f6d9d78`.
- WSGI entrypoint and `market_data/test_api.py` remain. Migration is **PARTIAL**; runtime/endpoint/deployment remains **NOT AUTHORIZED**; production readiness **NOT CERTIFIED**.


## 13. Final hardened offline CI — 2026-11-19

- Latest paired exact source SHA: `0a4432d8d101381e8b07c88a1a65bbf1ee3a787f`.
- FastAPI run [44527300856](https://github.com/kenznguyen/btcquant-application/actions/runs/44527300856), job `135571152796`: **25/25 PASS**, artifact `14532510818`, SHA-256 `563e4841b1139c16f55198407a890f6ea60400564c8c2b2cc1641576267ad49c`.
- SQLite aggregate run [44527300813](https://github.com/kenznguyen/btcquant-application/actions/runs/44527300813), job `135571149659`, same SHA: **196/196 PASS**, artifact `14533320216`, SHA-256 `6ef67fb1512cb06a62a35d74a5c34e333814cf33c865f58c4200ea5f206f7f23`.
- FastAPI workflow verifies committed runtime/test lock hashes and runs tests offline, as non-root, with a read-only root filesystem, dropped capabilities, no-new-privileges, resource bounds, and `--network none`. The only executable temporary filesystem is the bounded `/tmp` needed for SQLite temp DBs and native Python extension loading.
- Detailed update: [T0 FastAPI Locked Offline CI and Review](../evidence/T0_FASTAPI_LOCKED_OFFLINE_CI_AND_REVIEW_2026-11-19.md), follow-up commit `c2c575dad69c7e4eda2c86df13a324485bd0ee14`.
- Internal review remains PASS for the bounded adapter/CI scope; independent second-reviewer sign-off remains PENDING. WSGI entrypoint and WSGI tests remain; migration is PARTIAL. No runtime/deployment authorization is implied.
