# T0 FastAPI — Independent Review Package

- Prepared: 2026-11-19
- Repository: `kenznguyen/btcquant-application`
- Target branch: `main`
- Exact review snapshot: `d69e2e44707ea9b177548c79d36bf72ac8a18f0b`
- Review type requested: **independent second-person code review**. The implementation author/self-reviewer must not submit this as independent sign-off.
- Package status: **READY FOR REVIEW — reviewer not yet assigned; no independent approval recorded**.

## 1. Review objective

Review the T0 read-only Candle API migration from WSGI to FastAPI at the HTTP adapter boundary. Determine whether the FastAPI adapter safely preserves Candle Contract 1.1.0 and whether the source/CI evidence is sufficient to consider a separately gated WSGI/Gunicorn retirement proposal.

This package does **not** authorize WSGI/Gunicorn removal, runtime startup, endpoint probing, Nginx/VPS/systemd changes, deployment, T0/T1/T2 integration, canonical data changes, PostgreSQL activation, retention/deletion changes, or trading.

## 2. Exact source and provenance

Review snapshot:
- `main`: `d69e2e44707ea9b177548c79d36bf72ac8a18f0b`
- FastAPI implementation file blob: `market_data/fastapi_app.py` — `9f8f3352ad5510fc970ae78e9e8b9410e049bc83`
- Shared contract helper blob: `market_data/api_contract.py` — `77f4f1ab124caba07d1ba6ab16d0a1df9166b134`
- ASGI test file: `market_data/test_fastapi_api.py`
- WSGI reference adapter: `market_data/api.py`
- FastAPI workflow: `.github/workflows/t0-fastapi-migration.yml`
- Runtime lock: `requirements-market-data-fastapi.lock`
- Test lock: `requirements-market-data-fastapi-test.lock`
- Lock hash manifest: `requirements-market-data-fastapi.sha256`

The exact tested implementation/workflow source SHA is `b53e3e4f800d498317ac7ab4d0d01b44ef63a55c`. GitHub comparison from that SHA to the review snapshot reports 8 commits ahead, 0 behind. The four changed paths are documentation files plus a one-line test-module docstring correction; no executable application logic, workflow, or dependency lock changed. Therefore the paired CI evidence below covers the same executable FastAPI implementation and workflow present in the review snapshot. The reviewer should still inspect the full target snapshot, not rely only on this summary.

Relevant history:
- Workflow path correction: `3bdcaf093c381b2b767be3c903f9e86d5bf75bde`
- Dependency-only trigger proof / paired test source SHA: `b53e3e4f800d498317ac7ab4d0d01b44ef63a55c`
- R2 docstring correction and latest main snapshot: `d69e2e44707ea9b177548c79d36bf72ac8a18f0b`

## 3. Paired CI evidence

Both workflows checked out the exact same SHA `b53e3e4f800d498317ac7ab4d0d01b44ef63a55c`.

### FastAPI contract regression
- Run: [44529575151](https://github.com/kenznguyen/btcquant-application/actions/runs/44529575151)
- Job: `135579262823`
- Result: **25/25 PASS**
- Artifact ID: `14532693874`
- Artifact SHA-256: `7bcf6fdd46e8c5e1c81f76bf078377437b81cdbb178a546ce0b18166a8ade5f5`

### SQLite aggregate regression
- Run: [44529575307](https://github.com/kenznguyen/btcquant-application/actions/runs/44529575307)
- Job: `135579168097`
- Result: **196/196 PASS**
- Artifact ID: `14531469720`
- Artifact SHA-256: `93f30f492c9006a995c1f6248101080a3c2238be9d0530ab04421ce41f0580e8`

### Dependency locks
- Runtime lock SHA-256: `fb4cf8f63131cb36636b3c3230378a49bfb2d3a56b8750778ed5b3b5dac8d786`
- Test lock SHA-256: `2916098771a482a21637b94fff1f79afc0ddeb37a2a01fdae05032509a889cb6`

The workflow verifies committed lock hashes, downloads hash-pinned wheels, and runs the test container with network disabled, read-only root filesystem, non-root UID, dropped capabilities, no-new-privileges and resource limits. The canonical database and runtime/exchange credentials are not mounted.

## 4. Required review scope

Please inspect source and evidence directly. At minimum:

1. **Contract parity**
   - `GET /health` and `GET /v1/candles`.
   - Candle Contract 1.1.0 fields, decimal serialization, coverage/gaps, dataset provenance, freshness/evaluability and historical `asOfMs`.
   - HTTP 400/401/404/405/503 behavior, response bodies, content type and `Cache-Control: no-store`.
   - Compare WSGI and FastAPI behavior; identify any untested differences. In particular, consider adding/running a same-fixture differential test if needed before accepting parity.

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

- No automated differential suite has been recorded that invokes WSGI and FastAPI against identical fixtures and compares complete HTTP responses.
- No dependency CVE research, dynamic penetration test, reverse-proxy/Nginx validation, runtime secret probe, load test, production latency benchmark or Uvicorn/VPS startup was performed.
- The runtime lock is hash-verified and its wheels are downloaded by CI; the test lock is installed for the ASGI suite. A clean, independent runtime-only installation/smoke test is not recorded.
- Existing CI success is not proof of production readiness.

These are **NOT VERIFIED** items, not claims that defects exist. Please promote any item to a finding only with evidence and severity.

## 6. Required reviewer output

Please return a review tied to exact commit `d69e2e44707ea9b177548c79d36bf72ac8a18f0b`, containing:

- Reviewer identity and confirmation that they did not author the implementation or the internal self-review.
- Files/commits inspected and review method.
- Findings with severity (Critical/High/Medium/Low), exact file/line or evidence, impact, and required remediation.
- Separate statuses for correctness, security, architecture, dependency/CI, contract parity and runtime qualification.
- Verdict: **APPROVE**, **APPROVE WITH NON-BLOCKING FINDINGS**, or **REQUEST CHANGES**.
- Explicit statement whether WSGI/Gunicorn retirement may be proposed as a separate owner-approved change. This review alone does not authorize that change.

## 7. Current decision gates

| Item | Status |
|---|---|
| FastAPI 25/25 CI | PASS |
| SQLite aggregate 196/196 CI | PASS |
| Workflow dependency trigger proof | PASS |
| Internal self-review | PASS |
| Independent second-person review | PENDING |
| WSGI/Gunicorn retirement | NOT APPROVED |
| Runtime / endpoint / Nginx / VPS / deployment | NOT AUTHORIZED |
| Production readiness | NOT CERTIFIED |

## 8. Reviewer checklist

- [ ] Confirmed exact review SHA.
- [ ] Inspected FastAPI adapter and shared contract.
- [ ] Inspected WSGI adapter and assessed parity.
- [ ] Inspected ASGI tests and identified coverage gaps.
- [ ] Inspected storage failure paths and read-only guarantees.
- [ ] Inspected dependency locks, hashes and CI workflow.
- [ ] Reviewed paired CI evidence and artifact digests.
- [ ] Recorded findings and severity.
- [ ] Recorded explicit verdict and WSGI retirement recommendation.
- [ ] Confirmed no runtime/deployment authorization is implied.

## 9. Scope restrictions

Do not modify source, run or dispatch workflows, access credentials, connect to endpoints, access or mutate the canonical T0 database, start services, deploy, change VPS/systemd/Nginx, connect T1/T2, activate PostgreSQL, change data retention/deletion, or place orders as part of this review. Any additional test or remediation requiring such actions needs separate owner authorization.
