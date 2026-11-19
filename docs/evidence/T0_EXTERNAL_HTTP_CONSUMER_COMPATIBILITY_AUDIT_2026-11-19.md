# T0 External HTTP Consumer Compatibility Audit — 2026-11-19

## 1. Scope and evidence boundary

Read-only inventory of code consumers of T0 `GET /v1/candles` and downstream consumers of the Common API candle route. Goal: identify dependencies on contract 1.0.0 and assess compatibility with the official target's 1.1.0 contract before any connection.

No source, tests, workflow, dependencies, configuration, schema, data, canonical SQLite database, runtime, service, VPS, network endpoint, exchange or credentials were accessed or changed. No HTTP request was made to a T0 endpoint. No tests or workflows were run. No T0/T1/T2 runtime was started or activated. This audit is static only.

## 2. Repository and exact source identities

### Official application target

- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- HEAD at audit start: `53e14e57f3b1ede5f3fbe34368621bf42f14fe01`
- T0 API contract implementation: `market_data/api.py`, blob `4f923d400b8e133a602cec7239982fdf357e9e21`, contract version `1.1.0`.
- T0 API regression tests: `market_data/test_api.py`, blob `add00a2a91899d8e496df5b64c122442fc7c65c9`.
- Search found no `CandleHttpClient` or `T0_CANDLE_API_BASE_URL` implementation in this official target. Its `pipeline/api.py` reads the local selected Storage interface; it is an API/server path, not an HTTP client of T0.

### Active Core First source branch

- Repository: `kenznguyen/btcusdt-telegram-signals2`
- Active branch from its Session Handoff: `feature/core-operational-proof-20261112`
- Exact inspected HEAD: `e6606e28a696374f31cd6db1ec0a1372d942d64d`.
- Its T0 `market_data/api.py` remains contract `1.0.0`, source blob `81733c9b6de811cbebb2f5d472d41f37f337990c`; its `market_data/test_api.py` still asserts `1.0.0`, blob `49df7e0bec12908adae67f18a4aa19063e461093`.
- Its active T0 HTTP client: `freqai_bridge/http_candles.py`, blob `1f430c6d3a762deab9342e42072824661df3bf96`.
- Its T2 research context: `freqai_bridge/context.py`, blob `e87918cb1bbef9cbbb120181b70d17ef4ca36d8a`.
- Core runtime factory: `core_runtime/runtime_factory.py`, blob `b2dbd2efe0076ad5e831682caea0bd5e4a4f8bd6`.
- Core bundle provider: `core_runtime/bundle_provider.py`, blob `9d67f1600d4177e6f9756e366af6ef9319b27c19`.
- Core input normalizer: `core_runtime/bundle_inputs.py`, blob `f78ebde30413a3329063a2c68c457fe862a50c5e`.
- Common API gateway: `pipeline/api.py`, blob `bb89b0bdf196f64b3ab9d9ac15b6597f333c583e`.
- Client regression tests: `freqai_bridge/test_http_candles.py`, blob `8b38048e72d781d9219de1fe789e7078962c4824`.

### Older T0 source branch

- Branch: `feature/t0-centralized-data-feeder-p1-20261101`
- Exact inspected HEAD: `c0f48b8910655fdb40d14214ad048b1d3cfa7fe9`.
- It also contains a separate T0 HTTP client implementation, blob `29c94eae7fcc38eac0a64543a4189e40cb3b60d3`, pinned to `1.0.0`.
- Treat this as a legacy/parallel branch copy, not the active Core First branch. It must not be silently assumed to be synchronized with the active branch or official target.

## 3. Confirmed direct T0 HTTP consumers

| Consumer / call path | Exact source | How it consumes T0 | 1.1.0 disposition |
|---|---|---|---|
| Shared `CandleHttpClient` | `freqai_bridge/http_candles.py` blob `1f430c6d...` | GET `/v1/candles`; strict envelope/candle/freshness validation | **BLOCKED** |
| Core Bundle provider | `core_runtime/runtime_factory.py` + `core_runtime/bundle_provider.py` | Runtime factory constructs the client; provider calls `fetch_one_page()` for 100 M15 and 100 H1 candles | **BLOCKED** |
| Core Bundle normalizer | `core_runtime/bundle_inputs.py` blob `f78ebde...` | Revalidates T0 envelope before preserving it in immutable Core Bundle v1 | **BLOCKED** |
| Common API gateway | `pipeline/api.py` blob `bb89b0...` | `market_window()` calls the same client; common API exposes `GET /v1/candles` and uses T0 for other internal candle context paths | **BLOCKED** |
| FreqAI research context | `freqai_bridge/context.py` blob `e87918cb...` | Calls `CandleHttpClient.fetch()`; supports 1–3,000-bar windows | **BLOCKED** |

The Core First handoff states AI remains observation/research only and is not authorized for the paper execution path. The presence of the FreqAI research context does not authorize AI execution. The Core Runtime's candle path is a separate consumer of the same T0 HTTP client.

## 4. Exact contract 1.0.0 assumptions found

The active Core First client has three strict 1.0.0 assumptions:

1. It requires `payload["contractVersion"] == "1.0.0"`; 1.1.0 is rejected as `CONTRACT_UNSUPPORTED`.
2. Its exact `_FRESHNESS_FIELDS` set is only:
   `latestExpectedOpenTimeMs`, `latestReturnedOpenTimeMs`, `latestCloseTimeMs`, `latestAvailableAtMs`, `observationAgeMs`, `closeLagMs`, `evaluable`.
   Contract 1.1.0 adds `evaluationTimeMs`, `evaluationAnchor`, `timestampValid`, and `fresh`; exact-set validation rejects the new envelope as `FRESHNESS_UNAVAILABLE`.
3. It recomputes `observationAgeMs` and `closeLagMs` from `generatedAtMs`. Contract 1.1.0 uses `asOfMs` as the evaluation anchor when supplied. Core Bundle requests supply `asOfMs=decision_at_ms`; response generation can occur later. The client therefore compares different clock anchors even if its field/version checks were relaxed.

The downstream Core Bundle normalizer separately requires `contractVersion == "1.0.0"` in `normalize_candle_window()`. Updating only the HTTP client would still leave the bundle boundary rejecting 1.1.0.

## 5. Pagination incompatibility introduced by the 1.1.0 meaning of evaluable

The active client fetches up to 3,000 bars in pages of 32. Each page is validated independently. Even when `enforce_ingestion_freshness=False`, the validator still requires `freshness.evaluable is True`.

Under contract 1.1.0, `evaluable` requires complete coverage, valid timestamps and a fresh latest returned candle. An earlier page of a multi-page historical window can have complete page coverage and valid timestamps but cannot be fresh relative to the overall `asOfMs`/current evaluation time. Its correct `evaluable` value is false. The old client rejects that page before it can assemble the complete window.

This affects:
- `freqai_bridge.context.canonical_context()` for requests exceeding 32 bars.
- `pipeline.api.market_window()` when it serves a multi-page window.
- The source Core dashboard's `control_dashboard/src/api.js`, blob `38cb5a464b05acd77914c7f333d377d8ac0535ad`, requests 96 bars (three 32-bar pages) through the Common API.

A future client correction must validate each page's coverage and `timestampValid` independently, then evaluate freshness/evaluability for the assembled window using the final page and the requested evaluation anchor. It must not weaken the T0 server's `evaluable` rule or fabricate `evaluable=true` for stale historical pages.

The existing consumer `max_lag_ms` is an ingestion-lag policy (`availableAtMs - closeTimeMs`) and should remain distinct from the server's `fresh`/ `evaluable` semantics.

## 6. Downstream Common API consumers

These clients do not call the T0 endpoint directly; they call the source branch's Common API, whose `pipeline.api.market_window()` is the T0 HTTP consumer.

| Consumer | Exact source | Static behavior | Assessment |
|---|---|---|---|
| Android Five-Layer app | `android-app/.../FiveLayerApi.kt`, blob `91c9ce61a14dc54a2e2bf1b47285d5645b3f119e` | Requests 20 M15 bars with no `asOfMs`; parses candle rows and coverage; does not require a specific `contractVersion` and ignores freshness metadata | Additive 1.1.0 fields are structurally tolerated; it does not consume the new quality verdict. End-to-end remains **BLOCKED** by the gateway client. |
| Core control dashboard | `control_dashboard/src/api.js`, blob `38cb5a464b05acd77914c7f333d377d8ac0535ad` | Generic bounded JSON parser; requests a 96-bar M15 window; does not validate contract version or freshness fields | Additive fields are structurally tolerated; 96-bar request encounters the gateway pagination incompatibility. End-to-end **BLOCKED**. |

The Android parser checks candle identity, closed state, availability and coverage, but does not validate `timestampValid`, `fresh`, or `evaluable`. It must not be treated as an authoritative strategy-readiness validator.

## 7. Inspected paths not identified as T0 HTTP consumers

- Official target `btcquant-application/main`: no `CandleHttpClient` or `T0_CANDLE_API_BASE_URL` was found. Its current `pipeline/api.py` reads its local Storage interface; it is not an HTTP client of T0.
- T1 collector `binance-futures-collector/main`: its dashboard client calls the collector's own `/api/health`, `/api/streams`, `/api/symbols`, `/api/orderbook` and related endpoints. No T0 Candle API reference was found. T1 Orderbook HTTP is a separate contract.
- Separate Chart-Pro Android app: inspected `MarketEngine.kt` calls Binance Futures REST/WebSocket directly; no T0 URL/configuration was found in the inspected source.
- Telegram bot repository: inspected `bot.py` obtains historical candles directly from OKX; it is not a T0 HTTP consumer.
- Searches in the accessible private bot/Android repositories did not find T0 endpoint/configuration references. Their search indexes are unavailable, so absence claims for uninspected paths are not elevated to proof.

## 8. Compatibility matrix and verdict

| Layer | Contract 1.1.0 compatibility | Status |
|---|---|---|
| T0 target API implementation | Produces 1.1.0 | PASS — implementation and isolated T0 tests were previously verified at their recorded SHA |
| Active Core First T0 API copy | Still 1.0.0 | VERSION DRIFT / NOT SYNCHRONIZED |
| Active Core First HTTP client | Hard-rejects 1.1.0 and new freshness fields | **BLOCKED** |
| Core Bundle normalizer | Hard-requires 1.0.0 | **BLOCKED** |
| Core Runtime M15/H1 path | Depends on both strict layers and as-of freshness semantics | **BLOCKED** |
| Common API candle gateway | Depends on same client; multi-page behavior also conflicts with new evaluable semantics | **BLOCKED** |
| FreqAI research context | Depends on same client; paged windows affected | **BLOCKED**; AI execution remains deferred |
| Android Five-Layer parser | Permissive to additive fields, ignores new quality flags | STRUCTURAL COMPATIBILITY PASS; quality-consumption gap |
| Core control dashboard | Permissive JSON parser, 96-bar request | STRUCTURAL COMPATIBILITY PASS; gateway path BLOCKED |
| T1 collector dashboard / separate direct-Binance or OKX apps | Not T0 Candle HTTP consumers in inspected paths | OUT OF SCOPE |

**Overall verdict: BLOCKED — do not connect the active Core First branch to a T0 1.1.0 endpoint yet.** The 1.0.0 source copy, strict HTTP client, downstream bundle normalizer, as-of clock semantics and multi-page freshness handling must be reconciled first.

## 9. Recommended next bounded work item (not authorized by this audit)

Prepare a separate TDD scope for consumer migration, with no endpoint connection:

1. Freeze the intended source of truth as the official T0 1.1.0 contract. Do not downgrade T0 or silently treat 1.0.0 `evaluable` as equivalent to 1.1.0.
2. Add RED tests to the active Core First branch for 1.1.0 acceptance, exact freshness fields, `evaluationTimeMs`/`evaluationAnchor`, future `asOfMs`, `timestampValid=false`, incomplete coverage, stale final page, historical pages, 32/33/96/100/3,000-bar windows, and Core Bundle normalization.
3. Update the HTTP client to validate 1.1.0 semantics and aggregate page freshness correctly; update the Core Bundle normalizer and contract fixtures.
4. Add explicit downstream tests for the Android and dashboard response shape; make clear whether these clients display quality metadata or only candles/coverage.
5. Run only isolated, synthetic/temporary-data CI at the exact source SHA. Record run/job/artifact provenance and independent review.
6. Only after source-level GREEN and review, request a separate owner decision for any live read-only endpoint probe or runtime connection.

No source changes, CI dispatch, endpoint probe, deployment, process activation, T0/T1/T2 runtime, data mutation, strategy execution or trading is authorized by this audit.
