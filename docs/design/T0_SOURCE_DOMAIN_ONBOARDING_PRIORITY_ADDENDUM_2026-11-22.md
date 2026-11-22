# T0 Source-Domain Onboarding — Approved Priority Addendum — 2026-11-22

This addendum is authoritative for onboarding order and supplements (does not silently rewrite) the v1 inventory/ingestion design.

Owner approval record: `docs/decisions/T0_SOURCE_DOMAIN_ONBOARDING_PRIORITY_OWNER_APPROVAL_2026-11-22.md`.

## Approved order

### Phase A — foundational market series
- SD-01 Trade OHLCV candles.
- SD-02 Mark-price klines.
- SD-03 Index-price klines.
- SD-04 Premium-index klines.
- SD-09 Funding-rate observations.
- SD-10 Open-interest observations.

### Phase B — market microstructure
- SD-05 Aggregate trades.
- SD-06 Order-book depth diffs.
- SD-07 Order-book snapshots.

### Phase C — supplementary flow, positioning and operations
- SD-08 Liquidations / force orders.
- SD-11 Long/short positioning ratios (global account, top-trader account, top-trader position).
- SD-12 Taker buy/sell ratio.
- SD-13 Source health, gaps and ingestion checkpoints.

## Design execution rules

- Phase A is the next documentation-only work package. Map exact native fields, units, nullability, timestamp meaning, identity, provenance, conflict behavior, checkpoint semantics and synthetic test cases.
- Phase B and C remain sequenced after Phase A design review; do not start implementation by implication.
- The approval sets priority only. It does not freeze contracts or authorize code, tests, workflows, DB/schema, data movement, runtime, network, credentials, VPS or deployment.
- T0 is the only canonical owner; T1 remains a separate collector repository and supplies through an approved contract boundary.
- Raw source evidence is preserved. No deletion on ingestion acknowledgement.
- SD-08 remains BLOCKED for canonical acceptance until a collision-safe identity is sourced or explicitly approved. The current T1 liquidation CSV lacks native order/trade ID; timestamp/side/price/quantity alone is not accepted as proven unique.

## Status

| Work item | Status |
|---|---|
| Overall 13-domain inventory | DESIGN BASELINE RECORDED |
| Phase A priority | OWNER-APPROVED |
| Phase A detailed contract | NOT STARTED |
| Phase B priority | OWNER-APPROVED / SEQUENCED AFTER A |
| Phase C priority | OWNER-APPROVED / SEQUENCED AFTER B |
| Implementation/runtime | NOT AUTHORIZED |
| Tests/workflows/artifacts | NOT RUN |
| Database/data movement | NOT AUTHORIZED |

**Next:** complete Phase A native-schema mapping and contract refinement as documentation-only work; then submit for owner review.
