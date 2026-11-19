# T0 Binance USD-M BTCUSDT REST tail validation — 2026-11-20

## Owner approval and bounded scope

Owner explicitly approved a read-only public Binance USD-M REST tail validation:
- Endpoint: `GET https://fapi.binance.com/fapi/v1/klines`
- Symbol: BTCUSDT
- Timeframes: M15 and H1
- Requested start: 2026-11-19 00:00:00 UTC
- Keep only candles closed by the exact recorded UTC retrieval cutoff.
- Maximum 500 rows per timeframe; isolated staging cap 5 MiB.
- Validate timestamps, interval alignment, ordering, duplicates, gaps and OHLC/numeric semantics.
- No API key.

Explicit exclusions: SQLite creation or writes, Dropbox, VPS/runtime, feeder/writer, deployment, restore and cutover.

## Execution result

**BLOCKED — public REST endpoint returned HTTP 451.**

- The approved endpoint was called from an isolated Firecrawl execution environment using a standard-library HTTPS GET.
- The first network request (M15) returned HTTP 451 before any kline payload was received.
- Because the M15 request was blocked, H1 was not requested; no timeframe payload was retrieved.
- An earlier local execution attempt failed before networking because the optional `requests` package was unavailable; it made no HTTP request. The subsequent standard-library attempt reached the endpoint and received 451.
- No API key, alternate endpoint/domain, proxy or workaround was used.
- No response body containing market data was received. No raw payload was staged and the 5 MiB cap was not approached.
- Since no valid retrieval cutoff/payload pair could be established, candle-level validation, closed-candle filtering, row counts, last candle timestamps, gaps, duplicates and OHLC checks are **NOT VERIFIED**.

## Impact on archive coverage

The previously validated archive payload ends at:
- M15: 2026-11-18 23:45 UTC
- H1: 2026-11-18 23:00 UTC

This REST attempt does not extend archive coverage. The post-archive tail from 2026-11-19 00:00 UTC remains **NOT VERIFIED**.

## Governance and evidence

- Owner approval: received in conversation on 2026-11-20 for the bounded REST tail validation above.
- Repository: `kenznguyen/btcquant-application`, branch `main`.
- This is a data-access/validation attempt, not a source-code test. No GitHub Actions workflow, test run, job or artifact was created.
- No repository source, workflow, dependency, schema or canonical data was changed by the validation attempt.
- No SQLite, Dropbox, VPS/runtime, feeder/writer, deployment, restore or cutover action occurred.

## Status

| Area | Status |
|---|---|
| Approval and scope control | PASS |
| Public REST reachability from this execution environment | BLOCKED — HTTP 451 |
| M15 tail payload | NOT RETRIEVED |
| H1 tail payload | NOT ATTEMPTED |
| Candle-level tail validation | NOT VERIFIED |
| Archive coverage through 2026-11-18 | PASS, per separate archive evidence |
| Full coverage through retrieval cutoff | NOT VERIFIED |
| SQLite / Dropbox / VPS / runtime / cutover | NOT RUN |

## Next step and limits

Do not bypass the HTTP 451 with alternate domains, proxies or geo-routing. If the owner wants to continue, first decide whether to leave the REST tail unresolved or authorize a separately scoped attempt from an owner-approved, legally available execution environment. Any such attempt must retain the same endpoint, read-only behavior, budgets and validation rules. SQLite creation, Dropbox, VPS/runtime, feeder/writer and cutover remain separately gated.
