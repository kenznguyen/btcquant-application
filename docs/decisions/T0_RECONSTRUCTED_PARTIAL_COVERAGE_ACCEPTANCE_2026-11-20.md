# T0 Reconstructed Partial Coverage Acceptance — 2026-11-20

## Owner decision

The owner explicitly accepts the currently validated Binance USD-M BTCUSDT archive payload as a **RECONSTRUCTED — PARTIAL COVERAGE** candidate for a future staged dataset.

This decision accepts the bounded, evidenced archive coverage only. It does not claim full Binance history, full coverage through the current retrieval cutoff, recovery of the deleted historical database, or OFFICIAL / VERIFIED Canonical status.

## Accepted evidence boundary

| Timeframe | First observed open (UTC) | Last validated open (UTC) | Rows | Continuity within observed span |
|---|---|---|---:|---|
| M15 | 2019-12-31 00:00 | 2026-11-18 23:45 | 241,440 | PASS |
| H1 | 2019-12-31 00:00 | 2026-11-18 23:00 | 60,360 | PASS |

Evidence: `docs/evidence/T0_BINANCE_UM_BTCUSDT_ARCHIVE_PAYLOAD_VALIDATION_2026-11-20.md`.

- 202/202 ZIP SHA-256 sidecar comparisons passed.
- 202/202 ZIP CRC and CSV structure checks passed.
- No timestamp gaps, duplicates, out-of-order rows or checked OHLC/numeric anomalies were found within the selected archive partition.
- The first observed archive candle is not asserted to be Binance's earliest-ever available candle.
- No candles after the stated last open times are included or inferred.

## Explicit unresolved boundaries

1. **Leading boundary:** data before 2019-12-31 00:00 UTC is not established as unavailable; earliest-ever history remains NOT VERIFIED.
2. **Trailing boundary:** REST tail from 2026-11-19 00:00 UTC remains **NOT VERIFIED — CLOSED BY OWNER DECISION / NO FURTHER RETRIEVAL**. Do not retry, use alternate domains/endpoints, proxies, geo-routing or another execution environment.
3. The archive PASS means continuity only inside the retrieved archive span. It is not a waiver of the full-history coverage target.
4. The candidate dataset must carry a permanent PARTIAL status and visible boundary limitations. It must not be promoted automatically to OFFICIAL / VERIFIED or described as fully complete.

## Data and schema preservation

- Lineage is exactly `RECONSTRUCTED`; the historical database was deleted and is not recovered.
- Preserve original ZIP payloads and their SHA-256/provenance as immutable source evidence in a separately approved staging location.
- The current SQLite CandleStore schema stores canonical OHLCV plus `available_at_ms`; archive-only fields not represented by the approved Candle Contract must remain recoverable from retained raw source payloads. Do not silently discard them or alter the schema under this decision.
- `available_at_ms` must represent first observation/import time, never be backdated to the historical candle close.
- No synthetic candles, interpolation, forward-fill, inferred candles or silent gap repair.

## Authorization boundary

This decision authorizes only:
- documenting the accepted partial-coverage boundary;
- preparing a draft external manifest;
- preparing an isolated staging and validation plan;
- static inspection of the existing Candle Contract and SQLite schema;
- recording this decision and evidence references in Git.

It does **not** authorize:
- archive re-download, REST calls or any other market-data retrieval;
- materializing/copying raw payloads into a new staging environment;
- SQLite initialization, creation, migration, opening for write, or candle insertion;
- database build, feeder/writer/lease activation or runtime use;
- Dropbox upload, snapshot, restore, VPS access, deployment or cutover;
- changing source code, schema, dependencies, workflows or trading behavior.

Each execution stage requires a separate explicit owner approval.

## Status

- Owner acceptance of bounded archive coverage as `RECONSTRUCTED — PARTIAL COVERAGE`: **APPROVED**.
- Manifest and staging plan preparation: **AUTHORIZED**.
- SQLite construction and writes: **NOT AUTHORIZED / NOT RUN**.
- Canonical acceptance, snapshot, restore, runtime and cutover: **NOT AUTHORIZED / NOT RUN**.
- Tests and GitHub Actions: **NOT RUN**; this is a documentation/governance increment.
