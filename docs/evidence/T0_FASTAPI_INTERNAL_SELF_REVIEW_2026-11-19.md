# T0 FastAPI — Internal Self-Review Record

- Date: 2026-11-19
- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Reviewed source SHA: `0a4432d8d101381e8b07c88a1a65bbf1ee3a787f`
- Review type: internal self-review by the implementation/reviewing assistant; **not an independent second-reviewer sign-off**.
- Scope: FastAPI ASGI adapter, shared Candle Contract helpers, ASGI tests, dependency locks/hash manifest, FastAPI CI workflow and paired SQLite aggregate workflow. No runtime or canonical database access.

## Context and verification evidence

The migration target is an HTTP-adapter-only replacement for the T0 read-only WSGI API, preserving Candle Contract 1.1.0. Nginx remains the gateway; the canonical SQLite store, writer/lease/feeder/recovery and ingestion are outside this change.

Paired CI on the exact reviewed source SHA:
- FastAPI: run [44527300856](https://github.com/kenznguyen/btcquant-application/actions/runs/44527300856), job `135571152796`, 25/25 PASS; artifact `14532510818`, SHA-256 `563e4841b1139c16f55198407a890f6ea60400564c8c2b2cc1641576267ad49c`.
- SQLite aggregate: run [44527300813](https://github.com/kenznguyen/btcquant-application/actions/runs/44527300813), job `135571149659`, 196/196 PASS; artifact `14533320216`, SHA-256 `6ef67fb1512cb06a62a35d74a5c34e333814cf33c865f58c4200ea5f206f7f23`.
- Runtime lock SHA-256: `fb4cf8f63131cb36636b3c3230378a49bfb2d3a56b8750778ed5b3b5dac8d786`.
- Test lock SHA-256: `2916098771a482a21637b94fff1f79afc0ddeb37a2a01fdae05032509a889cb6`.

## Five-axis review

### 1. Correctness — PASS for the reviewed contract surface

- The adapter exposes only GET dispatch; the middleware rejects all non-GET methods before route matching and returns 405 with `Allow: GET`.
- `/health` remains public; candle reads require a configured Bearer token and use `hmac.compare_digest`.
- Query parsing remains bounded (2,048 raw characters, at most five fields, 2,000-candle maximum), rejects duplicate/unknown/malformed parameters, and retains 400 rather than FastAPI's default 422.
- Future `asOfMs` is rejected; historical evaluation uses the supplied anchor; freshness/evaluability are delegated to the shared 1.1.0 helper.
- Missing SQLite configuration/path and explicit unavailable storage fail closed; the missing-path test verifies no database is created. No SQLite fallback is attempted for an explicit PostgreSQL backend.
- The 25 ASGI tests cover contract fields, decimals, gaps, freshness, auth, status codes, read-only methods and error paths. The paired 196-test SQLite aggregate provides additional regression evidence.
- No runtime contract defect was identified in the inspected scope. This is not proof of untested runtime behavior.

### 2. Readability — PASS; minor nits

- Module ownership is understandable: `api_contract.py` owns shared parsing/freshness; `fastapi_app.py` owns the ASGI boundary.
- Minor cleanup only: add explicit type annotations to the shared helpers and reflow the long validation condition in `candle_query`. These are non-blocking and should be separate from WSGI retirement.
- The test module's top-level docstring still says it targets a “not-yet-created ASGI app”; this is stale wording and a low-priority nit.

### 3. Architecture — PASS WITH MIGRATION PARTIAL

- FastAPI does not import the WSGI module; shared contract logic is extracted.
- Route handlers are synchronous, so blocking SQLite reads are not executed directly inside an `async def` route handler.
- Storage selection remains behind the existing read-only storage facade; no write, lease, initialization, migration, ingestion, order or trading endpoint was introduced.
- WSGI and FastAPI currently duplicate some HTTP orchestration (auth, store selection, response/error mapping). This is an acknowledged transitional state while WSGI remains. Do not expand this dual implementation; remove WSGI only after the required independent review and owner gate.

### 4. Security — PASS for the inspected boundary and CI controls

- Bearer credentials are read from environment configuration, compared in constant time, and are not accepted through query parameters.
- Responses are marked `Cache-Control: no-store`; API documentation/OpenAPI routes are disabled.
- Query size/field count/candle count are bounded; non-GET methods are rejected.
- CI uses exact-SHA checkout, read-only source mounts, non-root execution, dropped capabilities, no-new-privileges, resource bounds and a network-disabled test container. Dependency hashes are checked before wheel download/install.
- The dedicated executable `/tmp` tmpfs is writable only inside the bounded, non-root, network-isolated test container and is required by native extension loading. This is an accepted test-harness trade-off, not a production runtime control.
- This review did not perform dependency CVE research, dynamic penetration testing, reverse-proxy validation or runtime secret-handling probes.

### 5. Performance — PASS for the bounded read path

- The request window is bounded to at most 2,000 candles.
- The synchronous endpoint keeps blocking SQLite work off the ASGI event loop via FastAPI's synchronous-handler execution model.
- No unbounded loop, background task, network call or write path was added to the request handler.
- No load test or production latency benchmark was run; performance conclusions are limited to static path review and unit-level tests.

## Findings and required disposition

### R1 — Required: FastAPI CI trigger omits runtime/test dependencies

The `.github/workflows/t0-fastapi-migration.yml` push-path filter covers the adapter, shared helper, ASGI test and lock files, but omits files imported or exercised by that suite: at minimum `market_data/storage.py`, `market_data/store.py`, and `market_data/postgres.py`; the test fixture also directly depends on `market_data/feeder.py`, `market_data/write_gateway.py`, and `market_data/sync.py`.

The SQLite aggregate workflow does trigger for some of those files, but its explicit unittest command does not execute `market_data.test_fastapi_api`. Therefore a change to one of these dependencies can run the aggregate suite while silently skipping the FastAPI contract suite. Add the dependency paths to the FastAPI workflow trigger, then make a harmless test-only change or workflow dispatch to prove the expected trigger and both suites on one exact SHA. No production source change is required for this finding.

- Severity: **Required CI coverage correction** before treating the FastAPI workflow as durable regression protection.
- Status: **OPEN / NOT FIXED**. This review did not modify workflow or source.

### R2 — Nit: stale test module docstring

`market_data/test_fastapi_api.py` says tests intentionally target the “not-yet-created ASGI app”, although `market_data/fastapi_app.py` now exists. Correct the wording in a separate small cleanup.

### Other dispositions

- No Critical source-code finding identified in the bounded adapter review.
- **Process gate remains OPEN:** this self-review cannot satisfy the project's independent second-reviewer requirement. WSGI/Gunicorn removal is therefore **NOT APPROVED** by this record.
- **Runtime/deployment remains NOT AUTHORIZED**. No endpoint probe, Uvicorn startup, Nginx routing, VPS/systemd operation or production readiness claim is made.

## Verdict

**INTERNAL SELF-REVIEW: PASS WITH REQUIRED CI ACTION ITEM.**

The inspected API implementation has no identified blocking contract defect, but the FastAPI CI trigger has a regression-coverage gap (R1). The 25/25 and 196/196 results remain valid for their exact historical SHA; they do not prove the missing trigger behavior. This is not an independent review, runtime verification, completed migration or production-readiness certification.

Next gates:
1. Correct and verify the FastAPI CI dependency-path triggers.
2. Obtain an actual independent reviewer sign-off against the source diff.
3. Only after both gates and owner approval, propose the bounded WSGI/Gunicorn retirement.
