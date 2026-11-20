# T0 REST tail offline validator — preparation record — 2026-11-20

## Scope
Prepared an offline, read-only validator for the owner-supplied Binance USD-M BTCUSDT REST tail response shape:
- M15: 129 raw kline rows; cutoff 2026-11-20T08:02:15.852Z; expected 128 fully closed rows and one forming row excluded.
- H1: 33 raw kline rows; same cutoff; expected 32 fully closed rows and one forming row excluded.
- Expected first open time: 2026-11-19T00:00:00Z.

The validator accepts two local JSON files containing the original Binance response arrays. It does not make HTTP requests, import archive data, access credentials, open SQLite, or write/modify input files or databases. It prints a JSON report to stdout and exits non-zero on validation failure.

## Files and source identity
Repository: `kenznguyen/btcquant-application`, branch `main`.
- Test-first commit: `98c651bd7dda9c7dc785957db4c57217919c84fa`.
- Validator implementation commit: `014d30f75947143281176eae56557ab35672b1f`.
- `market_data/rest_tail_validator.py` blob SHA: `3437e7a9181611cfed77eab59afee27136472963`.
- `market_data/test_rest_tail_validator.py` blob SHA: `293d9a605b6ec6498d551504fda04eecf298601f`.

## Checks implemented
- Exact raw row count and Binance 12-field kline array shape.
- Integer millisecond open/close timestamps, interval alignment, exact inclusive closeTime boundary, expected start and cutoff bounds.
- Strictly increasing open times and duplicate detection.
- Closed-vs-forming classification using `closeTime < cutoff_ms`; forming rows are excluded from closed-candle count and grid checks.
- Exact expected closed row count, first/last closed candle boundaries and missing-interval detection.
- Decimal parsing with finite-number checks; positive OHLC prices; non-negative volumes; OHLC envelope invariants; non-negative integer trade count; taker-buy volumes cannot exceed corresponding totals.
- No automatic data repair, sorting, deduplication, or gap filling. Invalid input is reported as failure.

## Test evidence
- 10 deterministic `unittest` cases passed in an isolated local temporary directory using Python 3.13:
  - valid M15 and H1 closed/forming-candle separation;
  - duplicate open time;
  - missing interval;
  - invalid OHLC envelope;
  - incorrect closeTime;
  - non-finite numeric value;
  - unaligned openTime;
  - negative volume and invalid trade count;
  - wrong raw row count.
- `py_compile` passed.
- CLI smoke with generated synthetic JSON fixtures passed; expected output was 128 closed + 1 forming M15 and 32 closed + 1 forming H1.
- These are synthetic/unit tests only. No real response payload was validated and no GitHub Actions run, workflow, job, or artifact was produced. Local test runtime was Python 3.13; user's Windows Python is 3.14.10.

## Critical evidence limitation
The prior personal-host probe printed row counts and first/last timestamps but did not save the 129/33 raw response arrays. Those payloads are not present in the conversation or repository. Consequently:
- Real M15/H1 OHLCV, timestamp continuity, duplicate and gap validation remains **NOT RUN / NOT VERIFIED**.
- Do not infer a real-data PASS from the synthetic tests.
- The validator intentionally does not re-fetch Binance data. Any further REST retrieval is outside this validator and remains subject to the controlling T0 scope/approval.
- To run it, the exact original response arrays must be supplied as local JSON files. If those payloads are unavailable, obtain separate approval before any new retrieval; do not silently repeat REST calls.

## Usage
From repository root, after placing the original raw response arrays in local files:
```powershell
py -3 -m market_data.rest_tail_validator --m15 .\m15-response.json --h1 .\h1-response.json
```
The default cutoff is fixed to `2026-11-20T08:02:15.852Z`. The command reads the two input files only and writes the report to the console. It does not create output files.

## Status
- Validator implementation and synthetic regression suite: **PREPARED**.
- Real REST payload validation: **BLOCKED — RAW PAYLOAD NOT RETAINED**.
- SQLite/archive/runtime/T1/T2/trading actions: **NOT PERFORMED / NOT AUTHORIZED**.
- No workflow run or artifact exists for this increment.
