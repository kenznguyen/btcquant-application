# T0 Application Foundation — current exact-source audit and independent review package

- Date: 2026-11-21
- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Current review snapshot: `d6e7516e0cdbcde58d4b78327c18c22aa3a4c2a0`
- Audit type: read-only repository, source-identity, CI-evidence and review-readiness audit. No code, tests, workflows, runtime, data or database were changed or executed in this audit.

## 1. Executive status

| Gate | Status | Evidence / limitation |
|---|---|---|
| T0 Application Foundation implementation | **PASS — CODE PRESENT** | SQLite-first store, read-only FastAPI Candle API, Candle Contract 1.1.0, Feeder/Scheduler/Recovery, lease/fencing and explicit initializer exist in the target repository. |
| FastAPI/Candle API isolated CI | **PASS** | 69/69 tests on exact source SHA `4d41294a7b82566666e50a79b87f62b668672077`; all three jobs successful. |
| Uvicorn/Nginx isolated process integration | **PASS — CI ONLY** | Real Uvicorn and Nginx processes/sockets in an isolated GitHub runner; not VPS runtime proof. |
| SQLite-only aggregate regression | **PASS — HISTORICAL EXACT-SHA** | 174/174 on exact SHA `b4e16a153ef7b0306784efa117b3121fc83dacb5`; do not relabel as a run on current HEAD. |
| REST-tail validator synthetic regression | **PASS — SYNTHETIC ONLY** | 10/10 on `265268c0b527c4a323493c4643a67a46ee15a223`. Real REST payloads remain unverified. |
| Genuine independent second-person review of current T0 source | **NOT VERIFIED / PENDING** | Existing review package targets an older source SHA; Graphify index is stale relative to current main. This report is a review package, not an independent approval. |
| Real Binance REST-tail payload validation | **NOT VERIFIED — CLOSED BY OWNER DECISION** | HTTP 451 was encountered; no retry, alternate endpoint, proxy, geo-routing or other retrieval path is permitted. |
| VPS/runtime, production deployment and production readiness | **NOT VERIFIED / NOT AUTHORIZED** | Dual-track decision keeps VPS runtime separate from CI; no service launch, systemd/autostart, public ingress or deployment authorized. |
| PostgreSQL/TimescaleDB | **PARKED / BLOCKED** | SQLite-first is the active target; no production backend switch or migration qualification. |

**Disposition:** T0 Application Foundation code and its bounded isolated CI evidence are substantially present and passing. The foundation is **not eligible for an overall independent-validation PASS** until a genuine second-person review examines the current exact-source snapshot. Real-data and runtime gates are separate and must remain unresolved; they are not to be silently folded into application CI.

## 2. Exact source identity at current main

Current T0 source/test/workflow blobs at review snapshot `d6e7516e0cdbcde58d4b78327c18c22aa3a4c2a0`:

| Path | Blob SHA |
|---|---|
| `market_data/api_contract.py` | `fb16b1d6a69fc35b3609758060d4992b91d25f37` |
| `market_data/fastapi_app.py` | `f17d6b975bb91d078e8d326fa368973b982bd9cc` |
| `market_data/storage.py` | `ae03c5a1caf68bb292ca2903e187a2a3a2474938` |
| `market_data/store.py` | `4e1b0c54bd56455abe5be0e5c7d0807e63e0bc78` |
| `market_data/feeder.py` | `299a9b5a8b1ebd581eb620d5ee860d9f9ff5dc5c` |
| `market_data/feeder_service.py` | `6d238a01f35003b943e2b22c8e05f05090ccb518` |
| `market_data/write_gateway.py` | `0a77df443ae1a817ea74946fac5dc0f3809ddd83` |
| `market_data/sync.py` | `e7ad4e6f2074225957b01f74abb0befe37675ea2` |
| `market_data/test_api_contract.py` | `d60c70ff61f8ad5d6852b1a25bdf846169469691` |
| `market_data/test_fastapi_api.py` | `62dd79df44d5f103803acdcc28973dd84016a377` |
| `market_data/uvicorn_nginx_smoke.py` | `c12ebb24c7d78a166413b0ae89a6fae78aff7cac` |
| `.github/workflows/t0-fastapi-migration.yml` | `3276dc667965d87b0dd1a442e12c5ea664432c33` |
| `.github/workflows/t0-sqlite-aggregate.yml` | `9f9d51ea64a238bccbc270f229d4043506ea9e3e` |

The repository compare from tested FastAPI SHA `4d41294a7b82566666e50a79b87f62b668672077` to current HEAD `d6e7516e0cdbcde58d4b78327c18c22aa3a4c2a0` is 107 commits ahead / 0 behind. The compare contains no T0 source, T0 test or T0 workflow path changes; subsequent changes are in risk/persistent-state, T1 orderbook and documentation paths. Therefore the T0 FastAPI source/test/workflow blobs above match the exact tested T0 snapshot. This does not make the workflow run a current-HEAD run.

The compare from SQLite aggregate SHA `b4e16a153ef7b0306784efa117b3121fc83dacb5` to current HEAD is 249 commits ahead / 0 behind. The only T0 path in that compare is `market_data/test_api_contract.py`; aggregate evidence remains historical and must be interpreted against its own allowlist and exact SHA.

## 3. Verified GitHub Actions evidence

### FastAPI / Candle Contract / migrated API

- Workflow run: [44861746989](https://github.com/kenznguyen/btcquant-application/actions/runs/44861746989)
- Exact source SHA: `4d41294a7b82566666e50a79b87f62b668672077`
- Conclusion: **SUCCESS**
- Job `136716449564`: FastAPI contract tests — **69/69 PASS**.
- Job `136716449529`: runtime-lock-only install and in-process ASGI smoke — **PASS**.
- Job `136716449322`: isolated Uvicorn process/socket + Nginx reverse-proxy integration — **PASS**.
- Artifacts:
  - Contract: ID `14689618455`, SHA-256 `fe44ab13bf1dca83bcb072b88467f99d1e6f2249f6884f24f2a75b0d1f990068`.
  - Runtime lock: ID `14690086537`, SHA-256 `0c1c9fdd2424a4cf4488e9e6bf27a7a7b66f47a3735c3a91beb7a71f6e210312`.
  - Uvicorn/Nginx: ID `14690171368`, SHA-256 `736daffdceaa1b52a74d940c6e29d1b3f4593b0b3028d0e3b36b0b2b87e4088b`.
- Test isolation: canonical DB not mounted, no exchange or production runtime accessed; the Uvicorn/Nginx process test is loopback-only and isolated.

### SQLite-only aggregate regression

- Workflow run: [44740818608](https://github.com/kenznguyen/btcquant-application/actions/runs/44740818608)
- Exact tested source SHA: `b4e16a153ef7b0306784efa117b3121fc83dacb5`
- Result: **174/174 PASS**.
- Artifact ID `14629919931`; SHA-256 `87df9fe44627016066b893f9cf98d27bad5b31f80e64cb6993c7e9d8b61fc731`.
- Scope: explicit SQLite-only regression allowlist; no canonical DB mount, no production feeder, no systemd/VPS, no exchange and no PostgreSQL/TimescaleDB qualification.

### REST-tail validator regression

- Workflow run: [44723882441](https://github.com/kenznguyen/btcquant-application/actions/runs/44723882441)
- Exact tested source SHA: `265268c0b527c4a323493c4643a67a46ee15a223`
- Result: **10/10 synthetic regression tests PASS**; syntax parse PASS.
- Artifact ID `14622617786`; SHA-256 `0ac0f81bacd65c8dd1b5748d1ba5da186dcc614963c050dfa8e0a403ec5ee713`.
- Real REST response validation remains **NOT VERIFIED**. The original `m15.json` and `h1.json` files were not present in the repository session. The owner-closed HTTP 451 boundary must be preserved; do not retry or bypass.

## 4. Architecture and safety controls to independently verify

The independent reviewer must inspect exact current source blobs and verify at least:

1. SQLite remains the default application backend; PostgreSQL requires explicit selection/DSN and is not silently selected.
2. API read path is read-only, does not initialize/create a missing canonical database, and fails closed on missing/unavailable storage.
3. Explicit initializer is empty-only and never runs implicitly from API or feeder startup.
4. Candle Contract validation rejects malformed timestamps, gaps, duplicates, out-of-order candles, future availability and incomplete coverage; no coercion or synthetic fallback.
5. Query parser enforces BTCUSDT/timeframe/window/field bounds; API is GET-only, bearer-authenticated, no-store and bounded to 2,000 candles.
6. FastAPI and Application Common API use the shared envelope/parser and retain tested response/error parity.
7. Feeder writes pass through the SQLite write gateway with lease/fencing and recovery guards; lease loss or invalid recovery must fail closed.
8. Scheduler/retry/recovery lifecycle is deterministic and covered by the explicit isolated test suites.
9. Runtime dependencies are hash-locked; workflow checks exact triggering SHA; test container is network-disabled/read-only/non-root where specified.
10. No T1 orderbook adapter is treated as a candle source, no T0/T1/T2 runtime coupling is introduced, and no production runtime claim is inferred from CI.

## 5. Review history and freshness

- Existing Graphify review package `docs/reviews/T0_CANDLE_CONTRACT_GRAPHIFY_INDEPENDENT_REVIEW_PACKAGE_2026-11-20.md` targets older source SHA `fc2e48420c6bbd00b7c5cfbaa8b3d7b2fc996235`; it is not a review of the current snapshot.
- Current Graphify index at audit time reports indexed commit `1e7dcc5e70a0e6840a7c5617893d3d2b0fc952df`, build `4ea26375-bdd8-42ec-aeff-72442ce10c84`, indexed at `2026-11-21T02:34:09Z`. It is stale relative to current main and must not be represented as exact-SHA graph evidence.
- Prior FastAPI static review and self-review explicitly identify themselves as same-assistant reviews, not genuine second-person reviews.
- Owner-approved liveness semantics: `GET /health` is liveness-only, not readiness. The approved baseline is design/isolated-CI only; it does not authorize production Uvicorn/Nginx configuration or VPS deployment.

**Required reviewer output:** verify the current commit and blob SHAs; inspect the T0 source and tests; list concrete Critical/Required/Optional findings with path/line/trigger/impact/remediation; independently assess correctness, architecture, security, bounded performance and test quality; state unverified items; issue an explicit APPROVE / REQUEST CHANGES / NOT VERIFIED verdict. Do not modify source or access runtime/data/VPS.

## 6. Restrictions and next gate

- Keep T0 data ownership independent; no canonical SQLite creation, import, restore, promotion, mutation or cutover is authorized by this report.
- No Binance REST retry, alternate endpoint, proxy, geo-routing or retrieval bypass.
- No VPS/SSH/runtime launch, systemd/autostart, production Nginx/Uvicorn config, public ingress or deployment.
- No PostgreSQL/TimescaleDB activation.
- No T1 provider activation or T1 → T2 runtime connection.
- No Core/AI automatic execution, exchange credentials or real orders; `AI_EXECUTION_ENABLED=false` remains.
- Next gate: obtain genuine independent second-person review of current exact-source snapshot. Resolve any Required findings in a separately bounded change, rerun affected exact-SHA CI, then obtain focused follow-up review. Keep data validation and runtime validation as separately governed gates.
