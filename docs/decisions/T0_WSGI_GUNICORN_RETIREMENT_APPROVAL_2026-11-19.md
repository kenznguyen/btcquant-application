# T0 WSGI/Gunicorn Retirement — Owner Approval — 2026-11-19

## Decision

The owner explicitly approves retiring the legacy WSGI/Gunicorn HTTP serving path and waives the previously pending human independent second-person review as a prerequisite for this bounded retirement.

This is an owner authorization to implement the retirement. It is not an independent technical certification and does not convert the Gemini review into a successful code review.

## Review status retained accurately

- ChatGPT supplementary adversarial static review: completed; no confirmed blocking defect identified within its inspected scope. It was performed by the implementation assistant and is not independent.
- Gemini external AI review: **BLOCKED / NOT VERIFIED** because the target repository and exact SHA were inaccessible to Gemini. No source-level findings or approval were produced.
- Human independent second-person review: **WAIVED BY OWNER** for this retirement decision; no human reviewer sign-off is claimed.

## Approved implementation scope

Repository: `kenznguyen/btcquant-application`, existing branch `main`.

Baseline main HEAD at approval: `7fdf4e3eedaf0b568c7219ee8b140684ff066718`.

Last tested implementation/workflow SHA: `a92cca39a3c23c3325191922c80e73b81384d9ce`. Current changes after that tested SHA are documentation-only according to the recorded comparison.

The bounded retirement implementation may:

1. Remove the legacy WSGI callable/server entrypoint in `market_data/api.py`.
2. Remove Gunicorn from the T0 runtime dependency manifest and its committed lock, then revalidate the lock and clean installation.
3. Migrate all remaining tests and offline acceptance fixtures that call the WSGI callable to the FastAPI ASGI application while preserving their assertions and isolation.
4. Retire the WSGI-vs-ASGI differential test after the WSGI reference is removed; preserve its completed C1 evidence as historical migration evidence.
5. Update FastAPI and SQLite aggregate workflow path filters, file checks, test commands and expected test counts so CI verifies the retired architecture on one exact SHA.
6. Update T0 README, decision, evidence, active scope index and session handoff to record the final source SHA, workflow runs, artifacts, digests and status.

## Contract and architecture invariants

- FastAPI remains the sole T0 HTTP adapter.
- Preserve Candle Contract 1.1.0, `GET /health`, `GET /v1/candles`, Bearer authentication, response schema, status/error semantics, freshness/evaluability, bounded query behavior, decimal OHLCV serialization and `Cache-Control: no-store`.
- Preserve read-only SQLite access and fail-closed storage selection.
- No new write, ingestion, lease, migration, order or trading routes.
- Do not change canonical T0 SQLite ownership, writer fencing, lease, feeder, scheduler, recovery, data schema or data contents.

## Explicit exclusions

This approval does **not** authorize or verify:

- Uvicorn process/socket startup or endpoint probing.
- Nginx configuration/routing changes.
- VPS, systemd, autostart or deployment.
- Production activation or production-readiness certification.
- T1/T2 integration or PostgreSQL/TimescaleDB activation.
- Data deletion, retention, TTL, cleanup, archive, compaction, vacuum or backup expiry.
- Strategy, risk engine, paper execution, live execution or real orders.

These remain separately gated. Paper-first and `ai_execution_enabled=false` restrictions remain unchanged.

## Verification requirements before closing retirement

- Use TDD: first establish a failing regression proving the WSGI entrypoint/dependency is absent while FastAPI contract tests and migrated acceptance tests remain the intended supported path.
- Run the focused FastAPI contract/ASGI tests and the complete SQLite aggregate regression.
- Run the dependency compatibility workflow after removing Gunicorn and prove the remaining CCXT dependency lock installs cleanly offline.
- Confirm all workflow runs check out the same exact commit SHA.
- Inspect artifacts and SHA-256 digests; record PASS/BLOCKED/NOT VERIFIED without overstating in-process smoke as socket/runtime qualification.
- Perform a bounded post-change static review and record residual limitations.

## Status

- Owner approval: **APPROVED**.
- Human independent review prerequisite: **WAIVED BY OWNER**.
- Gemini source review: **NOT VERIFIED**.
- WSGI/Gunicorn retirement implementation: **AUTHORIZED / NOT STARTED**.
- Tests and post-retirement CI: **NOT RUN**.
- Uvicorn socket, Nginx, VPS/systemd, runtime and deployment: **NOT AUTHORIZED / NOT VERIFIED**.
- Production readiness: **NOT CERTIFIED**.

Next step: implement the bounded retirement on the existing `main` branch using the verification requirements above. Do not cross any excluded runtime, data, T1/T2, PostgreSQL or trading boundary.
