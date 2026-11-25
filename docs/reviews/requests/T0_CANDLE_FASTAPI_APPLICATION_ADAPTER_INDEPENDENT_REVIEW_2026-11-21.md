# Independent Review Request — T0 Candle Contract, FastAPI and Application Adapter

**Review classification:** independent second-person, adversarial source review  
**Review target repository:** `kenznguyen/btcquant-application`  
**Immutable source snapshot:** `b79c7e5d0bc7cf5e6beee0d4e05505a1b1aa6556` (branch `main` at request creation)  
**Review target paths:** source/test/workflow blobs listed below.  
**PR purpose:** review request and scope only. No implementation change is proposed.

## Reviewer instructions

Review the immutable source snapshot above, not merely this PR's documentation-only diff. Verify each listed blob SHA against the target commit before review. Do not rely on prior assistant self-reviews as independent evidence. Return a signed-off GitHub review with one verdict: **APPROVE**, **REQUEST CHANGES**, or **NOT VERIFIED**.

For every finding include severity (Critical/Required/Optional), exact path and line, concrete trigger/reproduction, impact, and a bounded remediation. Explicitly distinguish observed defects from missing evidence. If a required path is not in scope or unavailable, mark it NOT VERIFIED rather than assuming correctness.

## Scope A — Candle Contract and query semantics

- `market_data/api_contract.py` — `fb16b1d6a69fc35b3609758060d4992b91d25f37`
- `market_data/test_api_contract.py` — `d60c70ff61f8ad5d6852b1a25bdf846169469691`
- `market_data/README.md` — `6561214efdca5108672b83809a9c12047462d72b`

Verify:
1. Contract 1.1.0 schema/envelope is deterministic and backward-compatible where promised.
2. Query parsing rejects invalid symbol, timeframe, bounds, field sets, duplicates, malformed timestamps and future `asOfMs`.
3. Candle ordering, uniqueness, interval alignment, coverage, gaps, provenance, closed-candle freshness and staleness are validated fail-closed.
4. No coercion, synthetic candle generation, venue fallback, cache fallback or silent data substitution.
5. Error codes/status mapping are stable, safe and consistent; no sensitive internals leak.
6. Boundary conditions: empty windows, exact start/end, maximum window, one-candle window, future clock, stale latest candle, partial/gapped windows and duplicate records.

## Scope B — FastAPI read-only HTTP adapter

- `market_data/fastapi_app.py` — `f17d6b975bb91d078e8d326fa368973b982bd9cc`
- `market_data/test_fastapi_api.py` — `62dd79df44d5f103803acdcc28973dd84016a377`
- `.github/workflows/t0-fastapi-migration.yml` — `3276dc667965d87b0dd1a442e12c5ea664432c33`
- `requirements-market-data-fastapi.in` — `e1b0d4036330e6e1c4c682511cc6bf5e95acb869`
- `requirements-market-data-fastapi.lock` — `c0194db6b085efaebf35c1bbf3450d4d8f1aa8f3`
- `requirements-market-data-fastapi-test.in` — `02adf127e61fbe6a94aa2d5c8ef99a8463664993`
- `requirements-market-data-fastapi-test.lock` — `c480820c3378a93fb8bb274ced326745f8bd4c3d`
- `requirements-market-data-fastapi.sha256` — `21918356eae2cff797cb60b8a0e32154d2f47b2a`

Verify:
1. API is GET-only and read-only; missing DB/config fails closed and does not create or initialize storage.
2. Bearer token comparison, missing/invalid token behavior, timing-safe comparison, no token in URL/log/error and no-store behavior.
3. Input/body/header/query limits and maximum candle count are enforced before expensive storage work.
4. Storage exceptions are mapped safely; no accidental traceback, path, DSN or credential disclosure.
5. FastAPI response is semantically identical to the shared contract builder and Application Common API adapter.
6. ASGI lifecycle, import side effects, app construction, concurrency and dependency compatibility.
7. CI pins exact source SHA, uses committed hash-locked dependencies and tests the intended files; no hidden network/runtime dependency.

## Scope C — Application Common API adapter parity

- `pipeline/api.py` — `47e0be41e8507c3c5464756d8ced4ad80a347aa5`
- `market_data/api_contract.py` — shared builder above.
- `market_data/storage.py` — `ae03c5a1caf68bb292ca2903e187a2a3a2474938`
- `market_data/test_api.py` — inspect at the same immutable source commit (verify its blob SHA from the Git tree; do not assume an older hash).

Verify that both adapters share the same envelope, query parsing, timestamp anchors, freshness semantics, failure behavior and storage read-only boundary. Identify any drift caused by duplicated parsing, separate storage selection, or distinct error handling. Explicitly assess whether the adapter's wider application responsibilities create hidden coupling to paper/trading state.

## Existing evidence — context only, not independent approval

- FastAPI workflow run [44861746989](https://github.com/kenznguyen/btcquant-application/actions/runs/44861746989), tested T0 source SHA `4d41294a7b82566666e50a79b87f62b668672077`: contract 69/69 PASS, runtime-lock smoke PASS, isolated Uvicorn/Nginx loopback integration PASS.
- The T0 source/test/workflow paths were compared unchanged from that tested SHA to the current review snapshot. This preserves the exact tested blobs but is not a new CI run on this snapshot.
- Older review materials target older source SHAs and do not satisfy this request.

## Required reviewer deliverable

1. Confirm exact target commit and each blob SHA reviewed.
2. Review correctness, API/security boundaries, contract parity, reliability, bounded performance, maintainability and test adequacy.
3. Inspect adversarial cases and add no code; report missing tests as findings.
4. Provide a finding table and explicit final verdict.
5. State whether the review was performed independently by a reviewer other than the implementation author.

## Non-scope / safety boundary

- No code changes, merge, refactor, runtime launch, deployment, VPS/SSH access or production readiness claim.
- Do not access, create, migrate, restore, copy, mutate or promote Canonical SQLite or any T0 production data.
- Do not contact Binance or retry HTTP 451; real REST payload retrieval is owner-closed.
- No T1/T2 runtime connection, PostgreSQL/TimescaleDB activation, exchange credentials, AI execution or real orders.
- This review is source-only. CI evidence is historical context and must not be represented as runtime validation.

## PR acceptance criteria

- A genuine independent reviewer submits an explicit review on this PR.
- Any Critical/Required finding is recorded with reproduction and remediation; no finding is silently waived.
- If source changes are required, use a separate bounded implementation PR and re-run exact-SHA CI; then request follow-up review.
- This PR must remain unmerged unless its documentation is intentionally accepted; it is not an implementation or deployment authorization.
