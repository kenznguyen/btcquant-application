# T0 Synthetic Binance USD-M Kline CSV Fixtures

**Status:** SYNTHETIC TEST DATA — NOT SOURCE EVIDENCE

These files were generated locally for deterministic offline parser/test development. They do not contain Binance market data and were not copied from an archive, REST response, personal host, VPS, SQLite database or Canonical T0 asset.

## Files

- `binance_um_btcusdt_m15_synthetic.csv`: two consecutive 15-minute rows.
- `binance_um_btcusdt_h1_synthetic.csv`: two consecutive 1-hour rows.

## Provisional row contract

Each file is headerless and contains exactly 12 comma-separated fields in the owner-approved provisional mapping recorded in `docs/specs/T0_CANONICAL_RECONSTRUCTION_SPEC_2026-11-21.md`:

1. open_time (Unix milliseconds)
2. open
3. high
4. low
5. close
6. volume
7. close_time (inclusive Unix milliseconds)
8. quote_asset_volume
9. number_of_trades
10. taker_buy_base_asset_volume
11. taker_buy_quote_asset_volume
12. ignore

All prices/volumes are invented deterministic values. The open timestamps are aligned to the UTC timeframe grids. The close timestamps are constructed as `open_time + interval_ms - 1`. The OHLC envelopes, non-negative volumes, integer trade counts and taker-buy volume bounds are internally consistent.

## Explicit limitations

- These fixtures test code against the **provisional** 12-field mapping only.
- They do not establish Binance archive header presence/absence, actual encoding, delimiter, ZIP member naming, numeric grammar, empty/null behavior, or source timestamp conventions.
- They do not verify that any real archive CSV uses this exact layout.
- Passing tests against these files is synthetic-fixture compatibility only, never real-source compatibility evidence.
- Do not use these rows to build a dataset, populate SQLite, calculate strategy performance, or claim market-history coverage.

No network access, archive retrieval, REST request, host access, SQLite operation or Canonical T0 access is required or permitted for tests using these fixtures.
