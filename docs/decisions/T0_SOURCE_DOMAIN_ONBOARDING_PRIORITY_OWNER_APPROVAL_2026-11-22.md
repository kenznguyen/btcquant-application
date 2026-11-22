# Owner Approval — T0 Source-Domain Onboarding Priority — 2026-11-22

- Parent architecture: `INDEPENDENT_MULTI_SOURCE_DATA_FOUNDATION` (OWNER-APPROVED).
- Related design: `docs/design/T0_SOURCE_DOMAIN_INVENTORY_AND_CANONICAL_INGESTION_CONTRACT_V1_2026-11-22.md`.
- Status: **OWNER-APPROVED PRIORITY ORDER — DESIGN ONLY**.

## Approved onboarding sequence

1. **Phase A — foundational market series**
   - SD-01 Trade OHLCV candles (existing T0 direct feeder / Binance USD-M public source).
   - SD-02 Mark-price klines.
   - SD-03 Index-price klines.
   - SD-04 Premium-index klines.
   - SD-09 Funding-rate observations.
   - SD-10 Open-interest observations.

2. **Phase B — market microstructure**
   - SD-05 Aggregate trades.
   - SD-06 Order-book depth diffs.
   - SD-07 Order-book snapshots.

3. **Phase C — supplementary flow, positioning and operations**
   - SD-08 Liquidations / force orders.
   - SD-11 Long/short positioning ratios (all three ratio types remain distinct).
   - SD-12 Taker buy/sell ratio.
   - SD-13 Source health, gaps and ingestion checkpoints.

## Binding constraints

- This approval fixes the **priority order for design and contract work**. It does not freeze any wire schema, canonical DTO, digest encoding, physical database schema or ingestion transport.
- Work may proceed phase-by-phase as documentation-only native-schema mapping, contract clarification, risk analysis and test-case design.
- A phase is not implementation-authorized merely because it is prioritized or its design is complete. Each implementation/runtime step requires separate explicit owner approval.
- T0 remains the sole canonical data owner. T1 remains in `kenznguyen/binance-futures-collector`; no collector fork/copy into the application repository.
- Preserve source-native evidence and provenance. No destructive deletion after acknowledgement; retention/deletion requires a separate owner decision.
- Fail closed on unresolved identity, provenance, schema, sequence or conflict conditions.
- **SD-08 Liquidations remains BLOCKED for canonical acceptance**: current T1 CSV lacks a native order/trade event ID. Do not invent a collision-safe composite key. Keep it quarantined until source contract extension or a separately approved collision-aware identity design.
- No database creation/open/write/migration/promotion/cutover; no ingestion runtime, network, credentials, T1 provider activation, T1→T0 or T1/T2 runtime connectivity, VPS/deployment, autostart, paper order submission, live trading or real orders.

## Completion criteria for each phase's design

- Native source fields, units, timestamp semantics, nullability and source schema version mapped.
- Stable identity and collision analysis documented; unresolved identities explicitly BLOCKED.
- Provenance and raw-evidence locator/checksum boundary specified.
- Validation, dedup/replay/conflict/quarantine behavior and checkpoint/ack semantics specified.
- Canonical domain record and consumer contract described without prematurely selecting physical storage/transport.
- Synthetic test matrix and failure cases specified; no claim of test execution until actually run.
- Open questions and independent-review gates recorded.

## Next step

Proceed with **Phase A documentation-only detailed mapping and contract refinement**, then present the completed design for owner review before beginning Phase B. No implementation is included.
