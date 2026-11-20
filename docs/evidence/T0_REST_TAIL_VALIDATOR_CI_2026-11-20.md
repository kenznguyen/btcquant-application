# T0 offline REST-tail validator CI evidence — 2026-11-20

## Scope

Add a dedicated isolated GitHub Actions gate for the existing offline, read-only Binance USD-M BTCUSDT REST-tail validator. No validator behavior or market data was changed.

## Source identity

- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Exact tested source SHA: `265268c0b527c4a323493c4643a67a46ee15a223`
- Validator: `market_data/rest_tail_validator.py`, blob `3437e7a9181611cfed77eab59afee27136472963`
- Tests: `market_data/test_rest_tail_validator.py`, blob `293d9a605b6ec6498d551504fda04eecf298601f`
- Workflow: `.github/workflows/t0-rest-tail-validator.yml`, blob `8303b83fb5bf6d5b309556992ae4feae60f2b446`

## CI history

1. Initial harness run [44723808398](https://github.com/kenznguyen/btcquant-application/actions/runs/44723808398) failed because `python -m py_compile` attempted to write `market_data/__pycache__` into a read-only source mount. The test module did not execute in that attempt. The failure exposed an issue in the harness, not a validator defect.
2. Corrected harness to parse source in memory with `ast.parse` and run unittest with `python -B`, preserving read-only source and avoiding bytecode writes.
3. Final run [44723882441](https://github.com/kenznguyen/btcquant-application/actions/runs/44723882441), run 2, push event, conclusion **SUCCESS**.
   - Job: `136246309375` — PASS.
   - Exact checkout SHA verified against `GITHUB_SHA`.
   - Syntax parse: PASS.
   - `python -B -m unittest -v market_data.test_rest_tail_validator`: **10/10 PASS**.
   - Test container network: disabled.
   - Canonical database, credentials, real Binance response files and runtime: not mounted or accessed.

## Artifact

- Name: `t0-rest-tail-validator-evidence`
- Artifact ID: `14622617786`
- SHA-256: `0ac0f81bacd65c8dd1b5748d1ba5da186dcc614963c050dfa8e0a403ec5ee713`
- Retention expiry: 2026-12-04

## Validation boundary

The 10 tests use deterministic synthetic fixtures and verify closed/forming candle separation, expected row counts, duplicates, missing intervals, OHLC envelope, close timestamp, finite numeric values, interval alignment, volume/trade constraints and malformed count handling.

This CI result proves only the offline validator's synthetic regression suite. It does **not** prove the real Binance REST tail payloads are valid. At tested HEAD, `m15.json` and `h1.json` are not present in the repository tree. Real payload validation remains **NOT VERIFIED**. No further REST request is authorized; the prior HTTP 451 / owner-closed decision remains controlling.

## Status

- Offline validator source and synthetic regression tests: **PASS**.
- Isolated GitHub Actions workflow and evidence artifact: **PASS**.
- Real REST response validation: **NOT VERIFIED**.
- T0 Canonical database creation/import/promotion, Feeder, VPS/runtime, T1/T2 runtime and trading: **NOT PERFORMED / NOT AUTHORIZED**.
- T0 Application Foundation: **IN PROGRESS** under the Application-first delivery order.
