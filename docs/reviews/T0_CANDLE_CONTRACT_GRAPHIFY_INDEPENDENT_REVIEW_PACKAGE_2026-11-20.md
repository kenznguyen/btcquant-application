# Graphify Independent Review Package — T0 Candle Contract and Application Adapter Parity

**Prepared:** 2026-11-20  
**Repository:** `kenznguyen/btcquant-application`  
**Immutable review target:** `fc2e48420c6bbd00b7c5cfbaa8b3d7b2fc996235`  
**Documentation-only repository HEAD at preparation:** `66b8fcb55998eddc4574efe842799c56f67b878e`  
**Review type:** independent, adversarial, exact-source review.

## 1. Objective

Determine whether fail-closed T0 candle validation and FastAPI ↔ Application Common API parity are correct, secure, maintainable, and safe within the bounded scope. Identify concrete defects, missing tests, incorrect assumptions, contract drift, and blockers. Passing CI is supporting evidence, not proof of correctness or a substitute for independent review.

Review the actual source at the exact target SHA. Do not infer approval from this package or the author's self-review.

## 2. Exact source scope

Inspect these exact Git blobs at commit `fc2e48420c6bbd00b7c5cfbaa8b3d7b2fc996235`:

| Path | Git blob SHA |
|---|---|
| `market_data/api_contract.py` | `4297ab173fee6f7ee78ef759217c229cd58eb4e4` |
| `market_data/fastapi_app.py` | `e0b607770004a4c1b01c1368c5dce268298d89a3` |
| `pipeline/api.py` | `887901302fc767750568933232daebb947902ee1` |
| `market_data/test_api_contract.py` | `856e8b7ae8932df6e081fe012ee962a0cf509dea` |
| `pipeline/test_api.py` | `8c4b4c3d0cb16cbd53a87ff40aafb35473b73bb7` |
| `market_data/README.md` | `6561214efdca5108672b83809a9c12047462d72b` |

The later HEAD `66b8fcb55998eddc4574efe842799c56f67b878e` is documentation-only and is not the code-review target.

### Graphify index freshness warning

At preparation, Graphify reported indexed commit `44dd517887caf256f293fc502d56afbbba124d29`, build `cf5b4948-3b68-486a-be13-bb4ea94ab585`, indexed at `2026-11-20T07:09:33Z`. This predates the target SHA. **Refresh/re-index Graphify to the exact target SHA before relying on graph-derived findings.** If exact-SHA indexing is unavailable, report Graphify coverage **NOT VERIFIED** and inspect the GitHub commit/blob sources directly. Never describe stale graph results as target-SHA evidence.

## 3. Required invariants to verify

1. Only supported timeframe keys; canonical interval math.
2. Evaluation/as-of timestamps and candle timestamp fields reject booleans, floats, strings, negatives, and malformed values without coercion.
3. Candle opens align to timeframe boundaries.
4. Close time is exclusive and equals open time + one interval.
5. First-observed/available time is not before candle close and not later than evaluation time.
6. Candles form a strictly increasing, contiguous timeframe grid. Gaps, duplicates, and out-of-order rows fail closed even when coverage claims complete.
7. Evaluable requires exact `coverage.complete is True`, valid timestamps/grid, and a fresh latest closed candle.
8. Invalid anchors/timeframes produce controlled rejection, not uncaught TypeError or permissive fallback.
9. One canonical `candle_envelope()` is used by FastAPI T0 and Application Common API `/v1/candles`.
10. Equivalent inputs produce matching envelope/freshness semantics, strict query parsing, status/error mapping, cache policy and content type.
11. Storage failures fail closed; no synthetic/venue/cache fallback or write path is introduced.
12. Response validation remains bounded (maximum 2,000 candles); assess linear-time behavior.

## 4. Five-axis review

Return findings as **Critical**, **Required**, **Optional**, **Nit**, or **FYI**. Each actionable finding must include exact file + line, concrete trigger/input, impact, and minimal remediation/test.

- **Correctness:** timestamp boundaries, close semantics, empty/singleton windows, M15/H1 interval math, coverage truthiness, future/stale data, malformed row shapes, ordering, adapter parity, HTTP errors.
- **Readability:** naming, control flow, exception handling, behavioral rather than implementation-only tests.
- **Architecture:** shared contract ownership, import/dependency direction, no duplicated policy, no T0/Application boundary violation.
- **Security:** untrusted-input parsing, auth regression, secret/path leakage, permissive fallback, bounded request/response work.
- **Performance:** O(n) behavior, bounded 2,000-row processing, no accidental quadratic scans or unnecessary allocations.

Inspect whether tests catch realistic regressions and whether parity tests exercise both adapters, not just helper output.

## 5. CI evidence (supporting only)

- T0 FastAPI Contract Regression: [run 44728558303](https://github.com/kenznguyen/btcquant-application/actions/runs/44728558303) — **65/65 PASS**, exact tested HEAD `fc2e48420c6bbd00b7c5cfbaa8b3d7b2fc996235`.
- Artifact ID `14625231382`; SHA-256 `4454a5f5dea5e71d2d35210ca362945c3f2b1dfe313c70e12eefa87bf99e3e10`.
- T0 SQLite aggregate: [run 44728445702](https://github.com/kenznguyen/btcquant-application/actions/runs/44728445702) — **174/174 PASS**, tested SHA `095605015a559fb1f71811a32396af4767329cd3`.
- F4 Pipeline API: [run 44727712387](https://github.com/kenznguyen/btcquant-application/actions/runs/44727712387) — 44/44 PASS.
- F4 R1 Account Risk: [run 44727712179](https://github.com/kenznguyen/btcquant-application/actions/runs/44727712179) — 160/160 PASS.
- F4 R3 Kill Reset: [run 44727712233](https://github.com/kenznguyen/btcquant-application/actions/runs/44727712233) — 145/145 PASS.
- Full evidence: [T0 Candle Contract Fail-Closed and Application Adapter Parity](../evidence/T0_CANDLE_CONTRACT_FAIL_CLOSED_AND_APPLICATION_ADAPTER_PARITY_2026-11-20.md).

## 6. Limitations and non-scope

- Original `m15.json` and `h1.json` were unavailable and not inspected; any prior script-reported SHA-256 values remain **NOT INDEPENDENTLY VERIFIED**.
- No Binance REST request was made. Do not fetch or reconstruct payloads.
- No canonical SQLite was opened, created, imported, restored, or modified.
- No T0/Application runtime connection, T1/T2 runtime, VPS, feeder, deployment, systemd/autostart, exchange credentials, or trading execution was accessed or authorized.
- Approval applies only to this bounded source/test change at the exact SHA. It does not approve production readiness, real-data validity, runtime activation, layer integration, or trading.

## 7. Required reviewer output

1. Confirm exact source SHA and each reviewed blob SHA; state whether Graphify indexing is exact-SHA or stale.
2. List inspected files and tests/evidence.
3. Findings ordered by severity with precise file/line and reproducible trigger.
4. Coverage gaps and anything **NOT VERIFIED**.
5. Explicit verdict: **APPROVE**, **REQUEST CHANGES**, or **NOT VERIFIED**. APPROVE only if exact-SHA review is complete and no Critical/Required findings remain.
6. Explicitly state that approval does not authorize runtime or cross-layer integration.

## 8. Copy-ready Graphify prompt

> Independently and adversarially review `kenznguyen/btcquant-application` at exact commit `fc2e48420c6bbd00b7c5cfbaa8b3d7b2fc996235`. Review the six exact source/test blobs listed above, not the current branch by assumption and not an older Graphify index. First verify Graphify's indexed commit; if it differs, refresh/re-index or report source coverage NOT VERIFIED. Examine fail-closed timestamp/freshness validation, contiguous candle-grid enforcement, exact coverage semantics, invalid-input handling, shared envelope parity between FastAPI and Application Common API, HTTP error/header parity, bounded performance, architecture, security, and regression-test quality. Treat CI as supporting evidence only. Return findings with severity, exact file/line, trigger, impact, remediation; list unverified areas; finish with APPROVE, REQUEST CHANGES, or NOT VERIFIED. Do not modify code, create commits, connect layers, access runtime/data/VPS, make REST requests, or authorize deployment/trading.
