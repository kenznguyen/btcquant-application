# T0 FastAPI — Independent Review Package

- Prepared: 2026-11-19
- Repository: `kenznguyen/btcquant-application`
- Target branch: `main`
- Exact review snapshot: `4651bf1b26132ca028e6bb428ee0869963432bc0`
- Exact tested implementation/workflow SHA: `fe5f99d31aac832f85c1aab9ca007bd70386d9fe`
- Review type requested: **independent second-person code review**. The implementation author/self-reviewer must not submit this as independent sign-off.
- Package status: **REFRESHED / READY FOR REVIEW — reviewer not yet assigned; no independent approval recorded**.

## 1. Review objective

Review the T0 read-only Candle API migration from WSGI to FastAPI at the HTTP adapter boundary. Determine whether the FastAPI adapter safely preserves Candle Contract 1.1.0 and whether the source/CI evidence is sufficient to consider a separately gated WSGI/Gunicorn retirement proposal.

This package does **not** authorize WSGI/Gunicorn removal, runtime startup, endpoint probing, Nginx/VPS/systemd changes, deployment, T0/T1/T2 integration, canonical data changes, PostgreSQL activation, retention/deletion changes, or trading.

## 2. Exact source and provenance

Review snapshot:
- `main`: `440379b243d0b63e80f22b032fa8499bc2e1a6f4`
- FastAPI implementation file: `market_data/fastapi_app.py`
- Shared contract helper: `market_data/api_contract.py`
- ASGI contract tests: `market_data/test_fastapi_api.py`
- WSGI reference adapter: `market_data/api.py`
- WSGI regression tests: `market_data/test_api.py`
- Differential parity test: `market_data/test_fastapi_parity.py`
- Runtime smoke harness: `market_data/runtime_smoke.py`
- FastAPI workflow: `.github/workflows/t0-fastapi-migration.yml`
- Runtime lock: `requirements-market-data-fastapi.lock`
- Test lock: `requirements-market-data-fastapi-test.lock`
- Lock hash manifest: `requirements-market-data-fastapi.sha256`

The exact tested implementation/workflow source SHA is `fe5f99d31aac832f85c1aab9ca007bd70386d9fe`. The review snapshot `4651bf1b26132ca028e6bb428ee0869963432bc0` is the documentation state before this package refresh. The reviewer must independently compare the tested SHA with the review snapshot and confirm that all post-test changes are documentation-only.

Relevant history:
- Workflow path correction: `3bdcaf093c381b2b767be3c903f9e86d5bf75bde`
- Differential test: `78770e49c61075ff10da9ba94526b2d3aef0141d`
- Workflow integration and exact tested source SHA: `62054b53119308eca9d2256dcd5aae5561da235b`
- Current review snapshot: `4651bf1b26132ca028e6bb428ee0869963432bc0`

## 3. Exact-SHA CI evidence

The FastAPI and SQLite workflows were push-triggered on `main`, checked out the exact same source SHA `fe5f99d31aac832f85c1aab9ca007bd70386d9fe`, and concluded successfully.

### FastAPI contract and differential regression
- Run: [44534512421](https://github.com/kenznguyen/btcquant-application/actions/runs/44534512421)
- Job: `135596271306`
- Result: **26/26 PASS**
- The log explicitly shows `test_same_fixture_has_identical_status_headers_and_body_for_contract_cases ... ok`, then `Ran 26 tests` / `OK`.
- Artifact ID: `14533664834`
- Artifact SHA-256: `555c63db97aa8466857cb4dd84728808989edc8107b25af0af31336bd3e84883`
- Artifact ZIP downloaded and inspected; `runner_metadata.txt` confirms both `workflow_commit` and `checked_out_source_sha` equal the exact tested SHA, `test_count=26`, and `test_exit_code=0`.

### SQLite aggregate regression
- Run: [44534512612](https://github.com/kenznguyen/btcquant-application/actions/runs/44534512612)
- Job: `135596271401`
- Result: **196/196 PASS**, log ends `Ran 196 tests` / `OK`.
- Artifact ID: `14534628423`
- Artifact SHA-256: `8e9c5274d48a44bb779bdd1db4119d3a83f1873c61ff889b769fc03fd6a0cfb0`
- Artifact ZIP downloaded and inspected; metadata confirms exact tested SHA and expected test count.

The SQLite aggregate is complementary coverage; the WSGI–FastAPI differential test is included in the 26-test FastAPI workflow, not counted among the 196 SQLite aggregate tests.

### D1 runtime-lock-only installation and ASGI smoke
- Run: [44536493461](https://github.com/kenznguyen/btcquant-application/actions/runs/44536493461)
- Job: `135603190576`
- Result: **success**. A fresh CPython 3.12.16 virtual environment installed only `requirements-market-data-fastapi.lock`, offline from the hash-verified runtime wheelhouse. The test lock was not installed.
- `pip check`: no broken requirements. Runtime app import and in-process GET `/health` both passed. No socket was opened.
- Artifact ID: `14535727293`
- Artifact SHA-256: `607771298cf289ab9af7f8bf7918d9738fff2d400be45e3e25bba388959042da`
- The same FastAPI workflow's contract/parity job `135603189986` passed **26/26**, artifact `14536536165`, SHA-256 `dbdbcc79ecd8495d91d39e14160187dbda6b9618f08d501f96cf4a6111dd02cd`.
- SQLite aggregate run [44536493268](https://github.com/kenznguyen/btcquant-application/actions/runs/44536493268), job `135603190883`: **196/196 PASS**, artifact `14536651799`, SHA-256 `fb0b74ec9276c7fc96c95e6c67b642079644d32d8329cb1efea9eb324462522a`.
- Detailed D1 report: `docs/evidence/T0_FASTAPI_RUNTIME_LOCK_SMOKE_2026-11-19.md`, commit `b5d03b14175fc54360630113ac41ec186929704a`.

### Dependency locks and CI isolation
- Runtime lock SHA-256: `fb4cf8f63131cb36636b3c3230378a49bfb2d3a56b8750778ed5b3b5dac8d786`
- Test lock SHA-256: `2916098771a482a21637b94fff1f79afc0ddeb37a2a01fdae05032509a889cb6`

CI verifies committed lock hashes, downloads hash-pinned wheels, and runs the test container with network disabled, read-only root filesystem, non-root UID, dropped capabilities, no-new-privileges and resource limits. The canonical database and runtime/exchange credentials are not mounted.

## 4. Required review scope

Please inspect source and evidence directly. At minimum:

1. **Contract parity**
   - `GET /health` and `GET /v1/candles`.
   - Candle Contract 1.1.0 fields, decimal serialization, coverage/gaps, dataset provenance, freshness/evaluability and historical `asOfMs`.
   - HTTP 400/401/404/405/503 behavior, response bodies, complete response headers, content type and `Cache-Control: no-store`.
   - Inspect `market_data/test_fastapi_parity.py`: one temporary SQLite fixture and deterministic clock are used for both adapters; status, all headers and exact body bytes are compared for ten cases: health, successful candle read, unauthorized, missing token configuration, malformed query, duplicate query parameter, unknown path, non-GET, unavailable store and historical `asOfMs`.
   - C1 is **CLOSED / VERIFIED for those ten enumerated cases only**. Assess whether other relevant request classes or environment differences remain untested.

2. **Authentication and security**
   - Bearer-token handling, constant-time comparison, missing configuration and secret exposure through URLs/logging/errors.
   - Query parsing limits, duplicate/unknown parameters, malformed/non-ASCII input, future anchors and oversized windows.
   - HTTP method handling, route matching, framework defaults, middleware behavior and error leakage.
   - Dependency versions, hashes and supply-chain/CVE considerations.

3. **Storage and failure behavior**
   - SQLite read-only access and missing-path no-create behavior.
   - Explicit PostgreSQL selection fails closed without SQLite fallback.
   - Blocking SQLite work is not executed directly in an async route.
   - No implicit DB initialization, writes, migrations, leases, ingestion, orders or trading routes.

4. **CI and reproducibility**
   - Trigger path completeness, exact-SHA checkout, lock/hash verification, offline test execution, artifact evidence and failure handling.
   - Whether the test lock adequately proves the independently declared runtime lock can be installed in a clean target environment.

5. **Migration and operational boundaries**
   - Whether retaining both WSGI and FastAPI creates material divergence risk.
   - Whether evidence is sufficient to recommend a separate WSGI/Gunicorn retirement change.
   - Explicitly distinguish source-level review from runtime/deployment/production qualification.

## 5. Known evidence limitations — reviewer must independently assess

- C1 differential parity is verified only for the ten enumerated cases; this is not exhaustive proof of equivalence for all requests or environments.
- D1 clean runtime-only install/smoke test is **CLOSED / PASS** for the stated clean venv, dependency consistency, ASGI import and in-process `/health` checks. It does not verify Uvicorn process/socket startup, Nginx, VPS or deployment.
- No dependency CVE/advisory research, dynamic penetration test, reverse-proxy/Nginx validation, runtime secret probe, load/concurrency/latency test or Uvicorn/VPS startup was performed.
- Independent second-person review has not yet been performed.
- Existing CI success is not proof of production readiness.

These are **NOT VERIFIED** items, not claims that defects exist. Promote any item to a finding only with evidence and severity.

## 6. Required reviewer output

Please return a review tied to exact commit `4651bf1b26132ca028e6bb428ee0869963432bc0`, containing:
- Reviewer identity and confirmation that they did not author the implementation or the internal self-review.
- Files/commits inspected and review method.
- Findings with severity (Critical/High/Medium/Low), exact file/line or evidence, impact and required remediation.
- Separate statuses for correctness, security, architecture, dependency/CI, contract parity and runtime qualification.
- Verdict: **APPROVE**, **APPROVE WITH NON-BLOCKING FINDINGS**, or **REQUEST CHANGES**.
- Explicit statement whether WSGI/Gunicorn retirement may be proposed as a separate owner-approved change. This review alone does not authorize that change.

## 7. Current decision gates

| Item | Status |
|---|---|
| FastAPI contract + differential CI | 26/26 PASS |
| SQLite aggregate CI | 196/196 PASS |
| C1 ten-case differential parity | CLOSED / VERIFIED |
| Dependency trigger proof | PASS |
| Internal self-review | PASS WITH VERIFICATION GAPS |
| D1 clean runtime-only install smoke test | CLOSED / PASS |
| Independent second-person review | PENDING |
| WSGI/Gunicorn retirement | NOT APPROVED |
| Runtime / endpoint / Nginx / VPS / deployment | NOT AUTHORIZED |
| Production readiness | NOT CERTIFIED |

## 8. Reviewer checklist

- [ ] Confirmed exact review SHA `4651bf1b26132ca028e6bb428ee0869963432bc0`.
- [ ] Verified no executable source/test/workflow/dependency drift after tested SHA `62054b53119308eca9d2256dcd5aae5561da235b`.
- [ ] Inspected FastAPI adapter and shared contract.
- [ ] Inspected WSGI adapter and assessed parity.
- [ ] Inspected ASGI tests and ten-case differential test; identified remaining coverage gaps.
- [ ] Inspected storage failure paths and read-only guarantees.
- [ ] Inspected dependency locks, hashes and CI workflow.
- [ ] Verified exact-SHA workflow logs, artifact metadata and digests, including D1 runtime-only installation evidence.
- [ ] Recorded findings and severity.
- [ ] Recorded explicit verdict and WSGI retirement recommendation.
- [ ] Confirmed no runtime/deployment authorization is implied.

## 9. Scope restrictions

Do not modify source, run or dispatch workflows, access credentials, connect to endpoints, access or mutate the canonical T0 database, start services, deploy, change VPS/systemd/Nginx, connect T1/T2, activate PostgreSQL, change data retention/deletion, or place orders as part of this review. Any additional test or remediation requiring such actions needs separate owner authorization.
