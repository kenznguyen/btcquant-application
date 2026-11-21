# T2 M2.1 — FreqAI bridge and T1 consumer dependency inventory

Date: 2026-11-21

## Scope and pinned inputs

Read-only inspection of source imports, test inventory, README and workflow configuration. No file copy/edit, dependency installation, workflow dispatch, network call to T0/T1, runtime, database, model training, paper order, or execution.

- Source: `kenznguyen/btcusdt-telegram-signals2`
- Source branch: `feature/core-operational-proof-20261112`
- Source HEAD: `e6606e28a696374f31cd6db1ec0a1372d942d64d`
- Target: `kenznguyen/btcquant-application`
- Target branch: `main`
- Target HEAD at this inventory: `8cfc1ff48746cfd25bf9ef59412ff6d33dcdabce`

## FreqAI bridge — reviewed source blobs

| Path | Blob SHA | Import closure / notes |
|---|---|---|
| `freqai_bridge/http_candles.py` | `1f430c6d3a762deab9342e42072824661df3bf96` | stdlib + `requests`; bounded read-only T0 HTTP client |
| `freqai_bridge/context.py` | `e87918cb1bbef9cbbb120181b70d17ef4ca36d8a` | stdlib + local exporter/http client + `pipeline.values` |
| `freqai_bridge/exporter.py` | `3b707174316d0c6b464ac947cbbe2d2fbee73682` | stdlib + `pipeline.decision` + `pipeline.values`; no direct third-party import |
| `freqai_bridge/ChartProFreqaiResearch.py` | `a7722f1148cf105c853deedaacb88edd14e671be` | external `freqtrade.strategy` and `pandas.DataFrame`, plus local bridge |
| `freqai_bridge/test_http_candles.py` | `8b38048e72d781d9219de1fe789e7078962c4824` | stdlib, fake HTTP session; no live endpoint required |
| `freqai_bridge/test_context_http.py` | `f19fe58c761d6f09d089e760951aa06ea1ab530f` | stdlib, fake client |
| `freqai_bridge/test_context_multi_timeframe.py` | `972fb70f7a3f6bc8b3929baac011152385029a9b` | stdlib, fake client |
| `freqai_bridge/test_exporter.py` | `2d199db931ca4ab39548f88797672f7fbf0d85bc` | imports `pandas`; fake window client |
| `freqai_bridge/README.md` | `380a2c6abdfc2bc8b42281558f8a137d059c4820` | Documents Freqtrade/FreqAI 2026.9, offline/prediction-only boundaries and T0 HTTP-only access |

The source workflow `.github/workflows/t2-freqtrade-2026-9-strategy-smoke.yml` blob `89fe779e88c11c9a1598d2138286b7d4bfe7742b` uses the official `freqtradeorg/freqtrade:2026.9_freqai` image, checks dry-run/no-order configuration, loads the strategy without exchange sync, and runs selected local regressions. The workflow is pinned by image tag, not an immutable image digest; exact image digest provenance is therefore not established by this static review.

The bridge's prediction code consumes actual FreqAI output and is explicitly prediction-only; its README says entry/exit flags are zero and `confirm_trade_entry()` returns false. It does not itself implement the requested independent AI LONG/SHORT paper admission path. It is an offline research/inference producer candidate, not authorization to create AI paper orders.

## T1 orderbook consumer — reviewed source blobs

| Path | Blob SHA | Import closure / notes |
|---|---|---|
| `core_runtime/orderbook_contract.py` | `1620c9f21b1f3df3c2fb65833f2afd80374bf6a5` | stdlib-only validator, but T1→T2 interface |
| `core_runtime/orderbook_http.py` | `89e5129eea4c9e7ceaa4439a546daf112d15c3e3` | stdlib + `requests` + orderbook contract |
| `core_runtime/test_orderbook_contract.py` | `935a3f2c8467e4f56cc683a7c0afcaba8fbeee00` | stdlib-only synthetic fixtures |
| `core_runtime/test_orderbook_http.py` | `6edb8dea8ea208c229439b2655f1ed03c173e055` | `requests` + fake response/session |
| `.github/workflows/t1-t2-orderbook-contract.yml` | `fec69171d648bf0c5ddaa8c30c54ff3c06c50e4f` | Python 3.12, installs `requirements-web.txt`; workflow claims 49 tests across contract, HTTP and integration suites |

This consumer is not a T1 provider implementation. It remains a separate T1 contract boundary review; no provider activation or runtime connection follows from this inventory.

## Dependency and migration disposition

- FreqAI bridge: **MIGRATE-CANDIDATE — OFFLINE RESEARCH ONLY**, subject to an isolated target dependency lock and exact framework/image provenance. Do not add Freqtrade, LightGBM, pandas, or requests to a T0/global dependency set.
- The static workflow uses a mutable image tag rather than a digest. Before claiming reproducible framework provenance, pin and record the exact image digest in a separately approved target-specific CI design.
- `pipeline.decision` is a shared application dependency imported by the bridge exporter; its own T0/market-data and signal semantics must remain target-owned and separately reviewed. Do not copy the source `pipeline/` directory wholesale.
- T1 orderbook contract/HTTP consumer: **SEPARATE REVIEW REQUIRED**. Keep T1 implementation/ownership in `binance-futures-collector`; app repo may only own approved consumer contract, DTO, validation, adapter and deterministic fixtures.
- `rfc8785` remains a separate dependency for Core Bundle modules and must not be added to the T0/global dependency lock. Exact version/hash lock evidence was not established in this review.
- No model training, profitability evaluation, AI order admission, paper execution, or AI ledger integration is implemented or verified by this report.

## Status

- Import inventory for listed bridge/consumer files: **PASS — STATIC**
- Freqtrade reproducibility/image digest: **NOT VERIFIED**
- Isolated dependency lock and hashes: **NOT VERIFIED**
- FreqAI tests/workflows on target: **NOT RUN**
- T1 provider/consumer independent boundary review: **PENDING**
- Code migration: **NOT STARTED**
- T0/T1 runtime, databases, model training, orders and trading: **NOT ACCESSED / NOT AUTHORIZED**

## Next permitted step

Finish the per-file manifest by mapping each source test to target-owned tests and target dependencies, then submit the refreshed migration manifest for review. Do not copy code, install dependencies or run workflows until that manifest is approved.
