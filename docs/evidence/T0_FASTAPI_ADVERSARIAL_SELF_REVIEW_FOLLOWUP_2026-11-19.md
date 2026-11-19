# T0 FastAPI — Adversarial Self-Review Follow-up

- Date: 2026-11-19
- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Review HEAD: `7878e2d3b5cd9522ea6ed85b1c6083f8726a2816`
- Tested implementation/workflow SHA: `fe5f99d31aac832f85c1aab9ca007bd70386d9fe`
- Review type: **same-assistant adversarial self-review**. This is not an independent second-person review.
- Scope: read-only source, test, workflow, lockfile and evidence inspection. No source edits, test execution, workflow dispatch, runtime, endpoint, credential, canonical database or deployment access.

## 1. Files inspected

- `market_data/fastapi_app.py` — blob `9f8f3352ad5510fc970ae78e9e8b9410e049bc83`
- `market_data/api_contract.py` — blob `77f4f1ab124caba07d1ba6ab16d0a1df9166b134`
- `market_data/storage.py` — blob `ae03c5a1caf68bb292ca2903e187a2a3a2474938`
- `market_data/api.py` — blob `0081357135a27bd2db586694d4461635726148d4`
- `market_data/test_fastapi_api.py` — blob `913464e62a72d04ceac52826c71e315a724efb7d`
- `market_data/test_fastapi_parity.py` — blob `2d951e924c99e5929dcc21c21ad144586658aabe`
- `market_data/runtime_smoke.py` — blob `09d5388dad0d28fb1a2b1eb970136363aa2ace55`
- `.github/workflows/t0-fastapi-migration.yml` — blob `ac2529ce2a0a6b475e8a9636ae93c2909e1653cf`
- Runtime and test dependency lockfiles.
- Project handoff, independent-review package and prior self-review evidence.

## 2. Findings

### C2 — MEDIUM — FastAPI parity workflow misses changes to the WSGI reference adapter

**Location:** `.github/workflows/t0-fastapi-migration.yml`, `on.push.paths` (lines 6–24).

The workflow runs `market_data/test_fastapi_parity.py`, which imports and invokes `market_data.api.application` as the WSGI reference implementation. However, `market_data/api.py` is absent from the workflow's push path filter. A change limited to the WSGI adapter therefore does not trigger this FastAPI parity workflow automatically.

**Impact:** the differential test can become stale exactly when its WSGI comparison target changes. The test itself compares status, complete response headers and exact body bytes for ten cases, but its CI trigger does not cover changes to one of the two implementations under comparison.

**Required remediation:** add `market_data/api.py` to `on.push.paths`. Consider also adding any future direct imports that become part of the differential test's behavioral reference. Then verify that a change to this path triggers the workflow on an exact SHA. This remediation has not been applied; no source or workflow file was changed in this review.

Severity is MEDIUM because this is a verification/control gap, not evidence that current FastAPI responses are incorrect.

## 3. Five-axis assessment

| Axis | Assessment | Boundary |
|---|---|---|
| Correctness | PASS WITH C2 | Adapter flow, query parsing, status mapping, storage read path and shared freshness helper inspected. C2 weakens regression triggering. |
| Readability | PASS | Adapter is compact; contract parsing/freshness are outside the WSGI adapter. No blocking readability issue identified. |
| Architecture | PASS WITH MIGRATION GATE | FastAPI is an HTTP-edge adapter; handlers are synchronous for blocking SQLite reads; no trading/write endpoint added. WSGI remains, so migration is partial. |
| Security | PASS FOR STATIC REVIEW; NOT CERTIFIED | Bearer token uses constant-time comparison; no query-token path; bounds and fail-closed backend selection observed. No CVE research, penetration test, proxy or runtime secret test performed. |
| Performance | PASS FOR BOUNDED REQUEST SHAPE; RUNTIME NOT VERIFIED | Query caps window at 2,000 candles; no load, concurrency or latency test. |

Other reviewed behavior:
- All non-GET methods are rejected before route dispatch with 405 and `Allow: GET`.
- Unknown paths return the contract 404 response; `/health` is public and candle reads require bearer auth.
- Query parsing limits total length/field count, rejects duplicate/unknown parameters and constrains market, timeframe, timestamps and window size.
- SQLite storage selection is read-only on the request path; missing SQLite path is tested not to create a database; explicit PostgreSQL selection does not silently fall back to SQLite.
- Sync route handler avoids executing blocking SQLite calls directly inside an async endpoint.
- Error mapping catches expected storage/configuration failures and returns 503; unexpected exceptions are not broadly swallowed.
- ASGI and differential tests are useful behavior tests, but the ten differential cases are not exhaustive.
- No claim is made that this review proves production readiness or full security.

## 4. Verification evidence rechecked

The repository comparison from tested SHA `fe5f99d31aac832f85c1aab9ca007bd70386d9fe` to review HEAD `7878e2d3b5cd9522ea6ed85b1c6083f8726a2816` is **6 ahead / 0 behind**. The compare lists only documentation changes:
- `docs/PROJECT_SESSION_HANDOFF.md`
- `docs/T0_ACTIVE_SCOPE_INDEX.md`
- `docs/evidence/T0_FASTAPI_RUNTIME_LOCK_SMOKE_2026-11-19.md`
- `docs/reviews/T0_FASTAPI_INDEPENDENT_REVIEW_PACKAGE_2026-11-19.md`

No executable source, test, workflow or dependency-lock drift was reported after the tested SHA.

Exact-SHA CI evidence rechecked:
- FastAPI workflow run [44536493461](https://github.com/kenznguyen/btcquant-application/actions/runs/44536493461), head SHA `fe5f99d31aac832f85c1aab9ca007bd70386d9fe`:
  - Contract/parity job `135603189986`: success; 26/26 PASS per recorded artifact evidence.
  - Runtime-only job `135603190576`: success; clean runtime-lock install, `pip check`, ASGI import and in-process health smoke.
  - Runtime artifact `14535727293`, SHA-256 `607771298cf289ab9af7f8bf7918d9738fff2d400be45e3e25bba388959042da`.
  - Contract artifact `14536536165`, SHA-256 `dbdbcc79ecd8495d91d39e14160187dbda6b9618f08d501f96cf4a6111dd02cd`.
- SQLite aggregate run [44536493268](https://github.com/kenznguyen/btcquant-application/actions/runs/44536493268), job `135603190883`: success; 196/196 PASS per recorded evidence. Artifact `14536651799`, SHA-256 `fb0b74ec9276c7fc96c95e6c67b642079644d32d8329cb1efea9eb324462522a`.

These CI results predate the six documentation-only commits and are tied to the exact tested implementation/workflow SHA above. They do not exercise a live Uvicorn socket, Nginx, VPS or deployment.

## 5. Verdict and gates

**SELF-REVIEW VERDICT: REQUEST CHANGES — C2 MEDIUM CI trigger gap.**

| Gate | Status |
|---|---|
| Static five-axis review | PASS WITH C2 |
| FastAPI contract/parity CI | PASS — 26/26 on exact tested SHA |
| SQLite aggregate CI | PASS — 196/196 on exact tested SHA |
| Runtime-lock-only install + in-process ASGI health | PASS for bounded smoke only |
| C1 ten-case differential parity | CLOSED / VERIFIED for those ten cases |
| C2 workflow trigger coverage for WSGI adapter | FINDING — MEDIUM |
| Independent second-person review | PENDING |
| WSGI/Gunicorn retirement | NOT APPROVED |
| Uvicorn socket / Nginx / VPS / deployment | NOT VERIFIED / NOT AUTHORIZED |
| Production readiness | NOT CERTIFIED |

This report supersedes the earlier self-review's C1 and D1 statuses: C1 and D1 are now closed for the bounded evidence described above. It does not supersede or satisfy the required independent second-person review.

## 6. Scope preserved

No source, test, workflow, dependency, runtime, canonical SQLite, feeder/writer/lease/recovery, T1/T2, PostgreSQL, retention/deletion or trading changes were made. No tests or workflows were run or dispatched. Next bounded action: obtain approval to fix C2 in the existing `main` branch, add the missing trigger path, then verify an exact-SHA workflow run. Independent second-person review remains a separate requirement.
