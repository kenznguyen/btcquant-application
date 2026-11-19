# T0 Canonical Data Recovery — External Source Search — 2026-11-19

## Authorization and scope

Owner explicitly authorized read-only inspection of external backup sources, including GitHub Actions artifacts, GitHub Releases, and Dropbox if connected.

This increment used read-only GitHub repository search/file read, known-run artifact metadata lookup, and Dropbox search. No download/export/restore of candidate data, no write/mutation, no workflow dispatch, no runtime/VPS/SSH/API/exchange access, no data collection, and no source/test/workflow/dependency/schema changes occurred.

## Exact repository references

- Target: `kenznguyen/btcquant-application`, branch `main`; inventory report commit `9fe5cf641081391ad23e79975d54a151a0414f69`, index commit `458927c0b0dffde526a4b7a3ce5cc0d5608f328e`, handoff commit `483d0cee5e64a0cde35957236fdcfde1359f4fb4`.
- Source: `kenznguyen/btcusdt-telegram-signals2`, branch `feature/t0-centralized-data-feeder-p1-20261101`.
- Source progress audit blob: `17cf8fa83e6a947affe4ed7ee9acb6b00a86e169`.
- Historical GitHub artifact/data inventory blob: `92b36a488619512ef64297b53a8fadb7db8608d8`, exact source HEAD recorded in that report `93f3b0e350cf62b205f8d2a3a84fd139e9c5f59e`, recursive tree `7ed669ada40b2232c672eb026f9aa925cc43d901`.

## GitHub repository and Actions evidence

The source branch's 2026-11-12 historical inventory performed a complete, non-truncated recursive tree scan (994 entries) and reported:
- No tracked CSV, Parquet, Feather, Arrow, SQLite/SQLite3, DB, JSONL or NDJSON dataset payload.
- No canonical `T0_M15_H1_DATASET_BUNDLE_V1` payload, manifest or producer path.
- No raw BTCUSDT candles or recoverable OOS payload in the selected GitHub Actions artifact ZIPs.
- The nine selected T0 artifacts (IDs `13628691436`, `13628521899`, `13627924430`, `13627939321`, `13628178055`, `13920786893`, `13921070540`, `13921095476`, `13921095419`) contained CI/test/systemd/recovery/fencing evidence only.
- P1.8 artifacts `13546255148` and `13545287609` were explicitly synthetic and are not valid market data.
- The historical Actions listing had 1,387 total runs but returned only the newest 1,000, covering 2026-11-07 through 2026-11-12; older runs were not exhaustively enumerated.

Current read-only spot checks:
- Known run `44272495963` exposed artifact `14413755795`, `core-first-code-operational-proof-44272495963`, 19,317 bytes, digest `sha256:86370ed99fb0895e560d60469334fd5f765c40c10c2ac764912041002e2e09d6`; its identity is Core-First code operational proof, not a canonical candle backup.
- Known run IDs `42021445350` and `41996998169` did not return artifact listings from the current artifact endpoint (404); this is not proof that all historical artifacts are absent.
- Current repository search for `market-data.sqlite3`, canonical SQLite backup, SQLite artifact, recovery database, and raw candle export did not locate a tracked database or data payload.
- The connected GitHub tool set exposes known-run artifact lookup/download and repository file search, but no repository Releases listing or general Actions-run listing operation. Therefore GitHub Releases and a fresh exhaustive Actions run/artifact inventory remain **NOT VERIFIED** in this increment. Do not interpret the missing connector operation as proof that no Releases exist.

## Dropbox search

Read-only Dropbox search was executed for:
`market-data.sqlite3`, `btcquant`, `BTCUSDT`, `canonical sqlite`, `t0 backup`, `M15 H1 dataset`, `sqlite`, `database`, `backup`, `market data`, `BTC`, `quant`, `t0`, `candles`, `trades`, and `CSV`.

No matching files or folders were returned. This establishes only that the connected Dropbox search returned no matches for these terms; it does not inspect deleted Dropbox content, unindexed data, other accounts, local devices, or disconnected cloud storage.

## Recovery disposition

| Source / question | Result |
|---|---|
| Source repository tracked data payload | NOT FOUND in exact historical tree inventory |
| Selected GitHub Actions artifacts | PASS — inspected artifacts are logs/test evidence, not raw market data |
| Entire GitHub Actions history | PARTIAL — historical listing capped at newest 1,000 of 1,387 |
| GitHub Releases | NOT VERIFIED — no Releases-listing action exposed by connected GitHub tools |
| Dropbox active indexed search | NO MATCHES for listed queries |
| Deleted Dropbox / other cloud accounts / local devices | NOT CHECKED |
| Owner-held canonical SQLite backup | NOT IDENTIFIED |
| Canonical data recovery readiness | BLOCKED / NOT VERIFIED |

## Next permitted step

Do not copy, restore, reconstruct, create an empty canonical database, run the empty-only initializer against a candidate path, start a writer, provision a VPS, access Binance, or create/export a dataset.

The remaining source-discovery options are:
1. Inspect GitHub Releases manually in the authenticated repository UI or provide an exact release URL/asset reference for read-only inspection.
2. Identify any other cloud account, computer, external disk, or provider snapshot that may contain the original SQLite file.
3. If no original/backup exists, prepare a separate proposal for **RECONSTRUCTED** market data from Binance USD-M public historical data, with owner approval required before any download, ingestion, or canonical T0 creation.

Any reconstruction must be explicitly labeled reconstructed, with source, retrieval time, exchange endpoints/archive provenance, coverage, gaps, checksums and reproducible manifest. It must not be represented as the original recovered Canonical SQLite or inherit the original database's historical provenance.

No workflow run, job, or artifact was created for this documentation-only report.
