# T1 Read-Only aggTrade Timestamp Mapping Audit — 2026-11-22

## Scope and guardrails

- Repository inspected: `kenznguyen/binance-futures-collector`, branch `main`.
- Latest inspected commit: `c91a8c22d3b6236c98ab9a4d4d69b25d47f7f738`.
- Last recorded source HEAD before documentation-only inventory commits: `e0142a372f3145d9eb42e23327ebcc82c3ee2ec3`.
- Read-only GitHub source inspection. No checkout, source edit, build, test execution, release, runtime, exchange, VPS, database, credential or data access.
- Relevant source blobs at inspected commit:
  - `src/models.rs`: `993419725268d1308645e3a37c15e9779a9e92cc`
  - `src/websocket/message_handler.rs`: `7d7f221fbf4b31470049baea55584645352f61b7`
  - `src/utils/csv_writer.rs`: `2c4538dcef7dfa758a854292031239c15f7c282b`
  - `src/constants.rs`: `0bf50b5fe02f4f196b38481cde6ecab9e2adb941`
  - `docs/SCHEMA.md`: `895f87a8281a3f9b6d37d96b5f68568e4285bee6`

## Direct source findings

1. `src/models.rs:74-96` defines `AggTradeWs` with serde field mappings:
   - `E → event_time`
   - `q → quantity`
   - `a → aggregate_trade_id`
   - `f → first_trade_id`
   - `l → last_trade_id`
   - `T → trade_time`
   - `m → is_buyer_maker`
   - There is no `nq` field and no `M` field.
2. `src/models.rs:366-383`, `AggTradeWs::to_csv()`, explicitly assigns `TradeCsv.timestamp_ms = self.trade_time`. It does not assign `event_time` to the CSV timestamp. It maps `a/f/l/m` to the corresponding CSV fields and derives `side = sell` when `is_buyer_maker=true`, otherwise `buy`.
3. `src/websocket/message_handler.rs:232-256` deduplicates on aggregate trade ID, calls `trade.to_csv()`, and sends the result to `CsvWriter::write_trade()`.
4. `src/utils/csv_writer.rs:379-405` uses `trade.timestamp_ms` for the path, CSV timestamp and `datetime_utc`. Therefore the source-level path is:
   `native T → trade_time → TradeCsv.timestamp_ms → CSV timestamp_ms`.
5. `src/constants.rs:28` fixes the trade CSV header and column order.
6. `src/utils/csv_writer.rs` also formats price/quantity through floating-point parsing and fixed 12-decimal formatting. `src/models.rs::format_decimal_str` parses strings as `f64` and formats to 12 decimal places. Thus the semantic source mapping `q → quantity` is proven, but byte-for-byte or arbitrary-precision decimal fidelity is not. Do not claim the CSV preserves original numeric lexemes.
7. Existing test `trade_roundtrip_matches_schema_v2` at `src/utils/csv_writer.rs:1050+` validates the CSV shape, but its fixture sets `event_time` and `trade_time` to the same constant. It does not independently catch an accidental E/T swap. No test was executed in this audit.

## Binance USD-M source-contract cross-check

The current Binance USD-M Aggregate Trade Stream reference identifies:
- `E`: event time;
- `T`: trade time;
- `q`: quantity with all market trades;
- `nq`: normal quantity excluding trades involving RPI orders;
- `m`: whether buyer is the market maker;
- `a/f/l`: aggregate trade ID and first/last underlying trade IDs.

It explicitly states RPI-involved trades are included in `q`, while `nq` excludes them. The T1 struct stores `q` but not `nq`; therefore no canonical `nq` may be inferred from the CSV quantity.

Official reference: https://developers.binance.info/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/market#aggregate-trade-streams

## Verdict

- **PASS — source-level mapping:** `timestamp_ms` is assigned from native `T`, not `E`, in the inspected source.
- **PASS — field semantics in source model:** `a/f/l/q/m` are parsed under their Binance field names; `nq` is absent.
- **PARTIAL — canonical numeric fidelity:** q/price are transformed through `f64` and fixed 12-decimal formatting; exact source decimal preservation is not established.
- **NOT VERIFIED — deployed binary/build provenance:** no evidence binds the VPS binary/release artifact to the inspected source commit and the exact source blobs. The source audit cannot certify a historical or current runtime binary.
- **B-17 remains OPEN** until the actual deployed/imported producer build identity is tied to the inspected source or the data path is explicitly constrained to this pinned source build. The source mapping finding alone is not enough to close the build-provenance portion of B-17.
- **B-01 remains PARTIALLY RESOLVED**: mapping is now evidenced, but build provenance and exact-decimal/raw-payload behavior remain unresolved.
- **B-15 confirmed OPEN**: `nq` is not parsed/stored; depth `T` is parsed by `DepthUpdateWs` but current CSV conversion retains only `E`.

## Required next evidence

1. Identify the exact producer binary/build currently associated with any T1 CSV import; record release/tag/build provenance and source commit.
2. If no reproducible build identity exists, do not retroactively assert the existing VPS binary came from this source. Keep B-17 OPEN for that binary lineage.
3. Add a future isolated test with deliberately distinct `E` and `T`, assert CSV timestamp equals T and differs from E. This requires separate implementation/test authorization.
4. Preserve raw source payloads if exact q/nq and decimal lexeme fidelity are required; otherwise version the CSV contract to state its f64/12-decimal transform and explicit `nq` unavailability.

No source file, test, build, workflow, runtime, data or database was changed.
