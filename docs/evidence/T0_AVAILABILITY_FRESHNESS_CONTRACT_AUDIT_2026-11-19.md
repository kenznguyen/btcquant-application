# T0 Availability & Freshness Contract Audit — 2026-11-19

## Scope and guardrails

Repository: `kenznguyen/btcquant-application`, existing branch `main`.

Bounded task: correct the read-only Candle API's timestamp validity, freshness and evaluability contract, including point-in-time `asOfMs` semantics.

No changes to the canonical SQLite database or its contents, writer boundary, lease/fencing, sync/recovery implementation, feeder runtime, VPS, deployment, T1/T2 integration, strategy execution, paper orders or live orders. No exchange connectivity was invoked. All tests used temporary SQLite databases, fake/synthetic data and network-isolated CI.

## Contract decision

- `generatedAtMs` remains the API response-generation timestamp.
- `evaluationTimeMs` is `asOfMs` when supplied; otherwise it is `generatedAtMs`.
- `evaluationAnchor` is `AS_OF` or `GENERATED_AT`, respectively.
- A future `asOfMs` relative to `generatedAtMs` is rejected with HTTP 400 / `INVALID_QUERY`.
- `timestampValid` is true only when every returned candle has nonnegative integer timestamps, aligned open time, exclusive close equal to open plus timeframe interval, first-observed availability no earlier than close and no later than the evaluation time, and strictly increasing open times.
- `fresh` is true only when the latest returned candle is the exact latest closed candle expected at the evaluation time. Its close lag must be in `[0, timeframe interval)`.
- `evaluable` is true only when coverage is complete, all returned timestamps are valid, and the latest candle is fresh. Empty, stale, timestamp-invalid or incomplete windows fail closed.
- Contract version is now `1.1.0`; schema version remains 1 because the added freshness fields are additive.

The one-timeframe freshness bound is derived from the selected timeframe (15m or 1h); no unrelated fixed-minute threshold or runtime configuration was added.

## Consumer compatibility

Static in-repository inspection found:
- `pipeline/core_strategy.py` consumes Storage windows directly and already requires complete coverage, ordered candle timestamps, closed candles, non-future availability and bounded close lag.
- `pipeline/api.py` also reads Storage directly and explicitly checks complete coverage and availability relative to its requested evaluation timestamp.
- No in-repository consumer was found reading `market_data.api`'s `freshness.evaluable` field.

Those paths were not modified. Compatibility with external HTTP consumers is NOT VERIFIED and must be checked before any external consumer upgrade.

## TDD and exact-SHA evidence

### RED — regression tests before implementation

- Test specification commit / exact checkout SHA: `0f0d14c69358dedeb770d3239691e9b92b0ee1eb`.
- Aggregate run [44515506071](https://github.com/kenznguyen/btcquant-application/actions/runs/44515506071), job `135530354343`: 196 tests, 4 failures and 4 errors, confirming missing fields and incorrect contract behavior.
- RED artifact ID `14526155148`, SHA-256 `16feb25311f2666600a5fd4875e3386f71cc83f1159150b76aa0f6ad17ef064a`.

### Implementation and fixture correction

- API implementation commit: `c82530153c63b7c6eb17782f6e95def0817a7afb`.
- API target blob: `4f923d400b8e133a602cec7239982fdf357e9e21`.
- API README target blob at implementation commit: `dc616683ce9c21af6c59fe0e0d2eda0be7c92fdf`.
- One pre-existing historical-`asOfMs` test fixture initially used an as-of value later than the actual runner clock. The API correctly rejected it. The fixture was changed to pin `generatedAtMs` just after the historical as-of boundary; the future-as-of guard was not weakened.
- Final test fixture commit: `8f49439fafc95186a8c854fe482aad707525a658`.
- Final target test blob: `add00a2a91899d8e496df5b64c122442fc7c65c9`.
- Final aggregate workflow blob: `4a0b78b08bc687ef862669dd1107b9fbacdcd665`.
- API/Storage workflow blob: `9abfebc14463d1448658205b81af041b7a30fc65`.

### GREEN — authoritative final evidence

- Repository HEAD / exact tested SHA: `8f49439fafc95186a8c854fe482aad707525a658`, branch `main`.
- Aggregate run [44515824622](https://github.com/kenznguyen/btcquant-application/actions/runs/44515824622), job `135531439684`: **SUCCESS, 196/196**, 3.151s.
- Aggregate artifact `t0-sqlite-aggregate-evidence`, ID `14525622150`, size 6,183 bytes, SHA-256 `7437e8f5877d62f81066208cd031cebea40b4cd0138b7c791b380a824b300cba`, expires 2026-12-03T11:33:24Z.
- Dedicated API/Storage run [44515824664](https://github.com/kenznguyen/btcquant-application/actions/runs/44515824664), job `135531440595`: **SUCCESS, 21/21**, 0.047s.
- API/Storage artifact `t0-sqlite-api-storage-evidence`, ID `14525821866`, size 1,581 bytes, SHA-256 `19d5d4e718d1310299667e7f11734437b1f23841129ebdc9a4f660cb4bea9468`, expires 2026-12-03T11:33:13Z.
- Both workflows checked out the exact triggering SHA and used the pinned Python 3.12.16 image, network-disabled test containers, read-only source mounts, no credentials and no canonical database mount.

An intermediate run at implementation commit `c82530153c63b7c6eb17782f6e95def0817a7afb` had 195/196 passing because of the old fixture clock mismatch; it is not acceptance evidence. The final run above is authoritative.

## Provenance

The API implementation is intentionally no longer byte-identical to the source snapshot:
- Source `market_data/api.py` blob: `81733c9b6de811cbebb2f5d472d41f37f337990c`.
- Target `market_data/api.py` blob: `4f923d400b8e133a602cec7239982fdf357e9e21`.

The target API test suite now includes the freshness/availability regressions; it is intentionally no longer byte-identical to the source:
- Source `market_data/test_api.py` blob: `49df7e0bec12908adae67f18a4aa19063e461093`.
- Target `market_data/test_api.py` blob: `add00a2a91899d8e496df5b64c122442fc7c65c9`.

The existing SQLite writer, storage, sync, recovery and feeder implementations were not changed by this task.

## Status

| Area | Status |
|---|---|
| Availability/freshness contract definition | PASS |
| Regression tests for incomplete coverage, stale data, timestamp validity, empty window, historical replay and future as-of | PASS |
| SQLite-only aggregate suite | PASS 196/196 |
| Dedicated API/Storage suite | PASS 21/21 |
| In-repository consumer compatibility | PASS by static inspection; direct-Storage paths unchanged |
| External HTTP consumer compatibility | NOT VERIFIED |
| Canonical SQLite data, feeder/API production runtime, exchange connectivity, VPS/deployment | NOT VERIFIED / NOT AUTHORIZED |
| T1/T2 integration and trading | NOT AUTHORIZED / NOT TESTED |
| Production readiness | NOT CERTIFIED |

## Next bounded step

Record this audit in the session handoff and provenance. Before connecting any external HTTP consumer, inspect its exact contract assumptions and verify it handles `contractVersion=1.1.0`, `timestampValid`, `fresh` and stricter `evaluable` semantics. Do not deploy, activate runtime or connect T1/T2 under this work item.
