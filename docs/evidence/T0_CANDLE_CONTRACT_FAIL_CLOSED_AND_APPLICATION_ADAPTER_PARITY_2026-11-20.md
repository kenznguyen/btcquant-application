# T0 Candle Contract Fail-Closed and Application Adapter Parity

**Date:** 2026-11-20  
**Repository:** `kenznguyen/btcquant-application`  
**Branch:** `main`  
**Implementation/test source HEAD:** `fc2e48420c6bbd00b7c5cfbaa8b3d7b2fc996235`

## 1. Scope and authorization boundary

Completed isolated T0 API contract hardening and Application API parity checks only.

- No T0/Application runtime connection was made.
- No T1/T2 runtime, VPS, feeder, deployment, systemd/autostart, exchange credentials or trading execution was accessed.
- No canonical SQLite database was opened, created, imported, restored or modified.
- No Binance REST request or alternate route was used.
- The original local `m15.json` and `h1.json` files were not available in this repository session and were not inspected. Their previously reported SHA-256 values remain **NOT INDEPENDENTLY VERIFIED**. Do not treat the REST payload evidence as verified in this work item.

## 2. Source identity

| File | Git blob SHA |
|---|---|
| `market_data/api_contract.py` | `4297ab173fee6f7ee78ef759217c229cd58eb4e4` |
| `market_data/fastapi_app.py` | `e0b607770004a4c1b01c1368c5dce268298d89a3` |
| `pipeline/api.py` | `887901302fc767750568933232daebb947902ee1` |
| `market_data/test_api_contract.py` | `856e8b7ae8932df6e081fe012ee962a0cf509dea` |
| `pipeline/test_api.py` | `8c4b4c3d0cb16cbd53a87ff40aafb35473b73bb7` |
| `market_data/README.md` | `6561214efdca5108672b83809a9c12047462d72b` |

## 3. Implemented behavior

### Shared freshness contract

- Only supported timeframe keys in `INTERVAL_MS` are accepted.
- Evaluation timestamps must be nonnegative exact integers; booleans, floats, strings and negative values are rejected.
- Candle collections must be lists/tuples; malformed row shapes fail closed.
- Each row must have nonnegative integer `openTimeMs`, `closeTimeMs`, `availableAtMs`.
- Open times must align to timeframe boundaries.
- Close time is exclusive and must equal open time plus one interval.
- First observation cannot precede candle close or exceed the evaluation timestamp.
- Consecutive rows must be exactly one interval apart. Gaps, duplicates and out-of-order rows invalidate `timestampValid`, `fresh` and `evaluable`, even when `coverage.complete=true`.
- `evaluable=true` requires exact boolean `coverage.complete is True`, a valid contiguous sequence and a fresh latest closed candle.
- Unsupported/malformed evaluation anchors are rejected without leaking a Python `TypeError`.

### Shared HTTP envelope

Added `candle_envelope()` as the single response builder used by FastAPI T0 and the Application Common API `/v1/candles` route. Both adapters now expose the same additive Candle Contract 1.1.0 fields: `contractVersion`, `schemaVersion`, `volumeUnit`, `source`, `generatedAtMs`, and `freshness`.

Both routes use the same strict `candle_query()` parser and map duplicate/invalid query parameters and future `asOfMs` to HTTP 400 `INVALID_QUERY`. Storage failures remain HTTP 503 `STORE_UNAVAILABLE`. The Application adapter generates its timestamp after the market-data read, matching FastAPI's generated-time semantics.

The Application API fixture now returns the complete storage window contract rather than an incomplete mock object.

## 4. Regression evidence

### TDD RED evidence

- Run [44725263945](https://github.com/kenznguyen/btcquant-application/actions/runs/44725263945), source SHA `c21eaa88aed8d7ce304f6f65a672903b3147a85d`: the new 60-test suite exposed missing contiguous-grid validation, invalid evaluation timestamp handling and unsupported timeframe handling.
- Run [44726256618](https://github.com/kenznguyen/btcquant-application/actions/runs/44726256618) and [44728318994](https://github.com/kenznguyen/btcquant-application/actions/runs/44728318994): additional adapter-parity and invalid-anchor regressions exposed missing Application envelope/error parity and an unhashable-anchor TypeError. These failures were addressed; test-harness setup errors were separately corrected before final green.

### Final T0 FastAPI contract regression

- Run [44728558303](https://github.com/kenznguyen/btcquant-application/actions/runs/44728558303)
- Exact tested HEAD: `fc2e48420c6bbd00b7c5cfbaa8b3d7b2fc996235`
- Result: **SUCCESS — 65/65 tests PASS**.
- Includes direct fail-closed tests for M15/H1 freshness, gaps, duplicates, ordering, future observation times, incomplete/non-boolean coverage, invalid evaluation timestamps/anchors, unsupported timeframes, empty windows and invalid envelope inputs.
- Application/FastAPI parity test checks identical candle-window fields, contract envelope fields, freshness metadata, query errors, future-as-of errors, cache policy and content type.
- Additional runtime verification jobs: in-process ASGI smoke and isolated real Uvicorn + Nginx socket integration both **SUCCESS**; external network disabled; temporary SQLite fixture only.
- Artifact: `t0-fastapi-contract-evidence`, ID `14625231382`, SHA-256 `4454a5f5dea5e71d2d35210ca362945c3f2b1dfe313c70e12eefa87bf99e3e10`.
- [Artifact](https://github.com/kenznguyen/btcquant-application/actions/runs/44728558303/artifacts/14625231382)

### T0 SQLite-only aggregate regression

- Run [44728445702](https://github.com/kenznguyen/btcquant-application/actions/runs/44728445702)
- Tested source SHA: `095605015a559fb1f71811a32396af4767329cd3`; subsequent change to the contract test module did not change aggregate-suite source behavior.
- Result: **SUCCESS — 174/174 tests PASS**.
- Artifact: `t0-sqlite-aggregate-evidence`, ID `14624483667`, SHA-256 `4583c787e563863a5ef4274b0ae891f567e09136081d423282d60807e50d7f4e`.
- [Artifact](https://github.com/kenznguyen/btcquant-application/actions/runs/44728445702/artifacts/14624483667)

### Adjacent Application/Paper regressions

All successful on source HEAD `17f01a707592b7a6a392b1d409c761cff061892c`; later commits changed only T0 helper guard/test coverage and CI pin metadata, not the tested Application API or Paper implementation.

| Workflow | Run | Result | Tests | Artifact ID |
|---|---:|---|---:|---:|
| F4 Pipeline API and Decision | [44727712387](https://github.com/kenznguyen/btcquant-application/actions/runs/44727712387) | PASS | 44/44 | 14623929314 |
| F4 R1 Account Risk Contract | [44727712179](https://github.com/kenznguyen/btcquant-application/actions/runs/44727712179) | PASS | 160/160 | 14624542731 |
| F4 R3 Kill Reset Readiness | [44727712233](https://github.com/kenznguyen/btcquant-application/actions/runs/44727712233) | PASS | 145/145 | 14625190826 |

Artifact SHA-256:
- F4 Pipeline API: `30aba0a5bb70bf8a7622e5164c592df80f5dfd07bc7d93008f61fe402d1045af`
- F4 R1: `2e2a5b5061313898186254d6a3cc94a3d24be81972774b8856cf775cadad5439`
- F4 R3: `8024a5e728a470e4bc2ac56aa4b73bfb7155322b9187e43697749840ada62f49`

## 5. Review and readiness

Internal five-axis review completed for correctness, readability, architecture, security and performance:

- Correctness: **PASS** for the bounded contract behavior covered by the regression suite.
- Architecture: **PASS**; response-envelope construction is centralized instead of duplicated between adapters.
- Security: **PASS** for the reviewed boundary; authentication remains in place, strict parsing is shared, no fallback or write path was introduced.
- Performance: **PASS**; freshness validation is linear in a bounded response of at most 2,000 candles.
- Readability: **PASS**, with shared contract behavior documented in `market_data/README.md`.

**Independent second-person review: PENDING.** This work was self-reviewed; no independent reviewer approval is claimed. Therefore integration readiness remains **BLOCKED / NOT VERIFIED** until an independent review of exact source HEAD `fc2e48420c6bbd00b7c5cfbaa8b3d7b2fc996235` is recorded.

## 6. Final status and next step

- T0 API contract fail-closed tests: **PASS**.
- FastAPI ↔ Application Common API response parity: **PASS** for tested M15 fixture and error cases.
- T0 aggregate suite: **PASS**.
- Adjacent F4 API/Paper regressions: **PASS**.
- Independent review: **PENDING**.
- T0/Application runtime connection: **NOT AUTHORIZED**.
- REST M15/H1 source-file integrity: **NOT VERIFIED**; do not inspect or use those payloads until exact original files are available and their SHA-256 is independently recomputed.

Next permitted step: independent review of the exact source blobs and evidence above. No layer connection, runtime activation, database operation or additional REST retrieval is authorized by this result.
