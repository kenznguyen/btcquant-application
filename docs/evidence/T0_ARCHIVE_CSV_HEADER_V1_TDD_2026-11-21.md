# T0_ARCHIVE_CSV_HEADER_V1 — TDD implementation and verification record

Date: 2026-11-21
Status: **FOCUSED TESTS PASS — FULL REPOSITORY REGRESSION NOT RUN**

## Frozen contract

Owner approved T0_ARCHIVE_CSV_HEADER_V1 with strict exact-match on the complete first CSV record only. Frozen ordered tuple:

`open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore`

No aliases, case folding, trimming, fuzzy matching, partial matches, or heuristic row skipping.

## Implementation

- Added `ARCHIVE_CSV_HEADER_V1`.
- Added immutable `ArchiveCsvDocument` and `parse_archive_csv_document` metadata API.
- Preserved legacy `parse_archive_csv(...)` tuple return and row model.
- Exact first-record match skips exactly one header. Every other record undergoes strict data validation.
- Later/repeated header, malformed rows, wrong field count, blank rows and malformed CSV are rejected.
- Existing timestamp, timeframe alignment, inclusive close-time, Decimal, OHLC, volume, taker-volume and ordering checks retained.
- Added 15 focused synthetic tests; original 19 parser tests unchanged.
- Added focused Actions workflow on Ubuntu 24.04 / Python 3.13.

## Source and workflow evidence

- Baseline parser blob: `7d59706778a98a18185e0b2fe744c3c43c2eb870`.
- Test module commit: `237dbfed3df5c54e8afaaf7516efb6d21f14bb53`.
- Parser implementation commit: `5375e2e276ae96c3b82e68cf312bb3591f75b5e3`.
- Regex corrections: `05484f0c97decf888eab4bc181c3090c6004d592`, `0ee4de390ed5cdd90138136883fb395e2d6ff011`.
- Workflow commit / exact tested source SHA: `54317ad0aaaa8d547889b41336c0aaed4b1d09bc`.
- Workflow run: [44925135819](https://github.com/kenznguyen/btcquant-application/actions/runs/44925135819).
- Event: push; run attempt 1; completed success at 2026-11-21T16:32:46Z.
- Job: `parser-tests`; job ID `136909445610`; completed success.
- Runner: Ubuntu 24.04.5; CPython 3.13.18.
- Checkout log confirms exact SHA `54317ad0aaaa8d547889b41336c0aaed4b1d09bc`.
- Command: `python -B -m unittest -v market_data.test_archive_csv_parser market_data.test_archive_csv_header_contract`.
- Result: **Ran 34 tests in 0.003s — OK** (19 legacy + 15 new).
- Artifacts: none published by this workflow.

## Review and status

- Contract tuple/source sample evidence: PASS (approved one-archive header inspection; run 44924695179).
- Parser implementation committed: PASS.
- Focused TDD GREEN: PASS on exact source SHA above.
- Existing 19 parser tests: PASS as part of the same 34-test run.
- New 15 strict-header tests: PASS as part of the same 34-test run.
- Self-review: PASS — API compatibility preserved; exact first-record tuple comparison; no fuzzy handling; body records remain validated; no external I/O added.
- Full repository regression: NOT RUN.
- Real archive compatibility: VERIFIED only for the approved M15 monthly 2022-08 sample header; H1/daily archive header variants NOT VERIFIED.
- Workflow artifact: none.
- Independent review is not a mandatory gate under the current project handoff policy.

## Scope protection

No source archive download, archive inventory mutation, Canonical T0 modification, SQLite creation/import, importer, Contract 1.2.0 implementation, T1/T2 connection, VPS/runtime/deployment, exchange credential, or trading behavior was touched.

## Next step

Parser header support is ready for the next separately approved staging/import design step. Do not generalize this header evidence to H1/daily archives without additional source samples. Full repository regression remains a separate, unrun check.
