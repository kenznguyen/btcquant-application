# T0 Phase B Design Review — 2026-11-22

- Reviewed document: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`
- Reviewed design commit: `efbce3477c367ddc7be3e7ccfb430ba897b3e9d8`
- Reviewed design blob: `ca57a4f8628d95471bdd575d3846b1db49a4f1f5`
- T1 CSV schema reference: `kenznguyen/binance-futures-collector/docs/SCHEMA.md`, blob `895f87a8281a3f9b6d37d96b5f68568e4285bee6`
- Review type: documentation/design review; no code or runtime review.
- Verdict: **REQUEST CHANGES — PHASE B DESIGN NOT APPROVED YET**.
- Tests/workflows/artifacts: **NOT RUN / NONE**.

## 1. Overall assessment

The design direction is sound and consistent with the owner-approved Independent Multi-Source Data Foundation:
- T0 remains the sole canonical owner.
- T1 remains in its own repository.
- Raw source evidence and provenance are preserved.
- At-least-once delivery, idempotent replay, conflict quarantine and fail-closed acceptance are correctly emphasized.
- SD-05, SD-06 and SD-07 are treated as distinct domain contracts rather than being forced into the Candle model.

The draft is appropriately explicit that identities, digest encoding, provenance and checkpoint behavior are not frozen. However, several issues need correction or sharper treatment before the Phase B design baseline can be accepted.

## 2. Required findings

### R-01 — Separate SD-06 canonical event identity from stream/session epoch

Severity: **REQUIRED — correctness / deduplication**

The candidate SD-06 identity currently includes `stream_epoch`:
`(exchange, market_type, symbol, stream_epoch, first_update_id, final_update_id)`.

A repeated exchange update range observed again after reconnect/restart could then be treated as a new canonical event solely because its local capture epoch changed. This risks duplicate canonical history and ambiguous replay semantics.

Required revision:
- Define canonical exchange-event identity separately from capture/session provenance.
- Evaluate an identity candidate scoped by exchange, market, symbol and native update range, after confirming the exchange's update-ID uniqueness scope.
- Keep `stream_epoch` as continuity/checkpoint/session metadata, not automatically as part of canonical event identity.
- Specify how the same update range and same/different payload is handled across epochs.
- If the collector cannot establish a stable exchange-event identity, explicitly keep canonical acceptance blocked rather than using the epoch as an unexamined substitute.

### R-02 — Snapshot group completeness and capture identity must remain hard acceptance gates

Severity: **REQUIRED — correctness / data integrity**

The draft correctly notes that the published T1 CSV is one row per level and lacks a capture ID, level count, end marker or completeness manifest. It also correctly lists these as blockers. The design needs to make the consequence operationally unambiguous.

Required revision:
- State that EOF, file rotation, elapsed time or a row count alone does not prove snapshot completion.
- Specify the minimum acceptable source-generated capture ID and completion evidence (for example a manifest with stable capture ID, expected row count and finalized object digest, or an equivalently proven boundary).
- Define partial-write, restart, repeated capture and empty-side/empty-book behavior.
- Until this exists, all snapshot groups without completeness proof remain quarantined/not canonical-accepted.

### R-03 — Account for Binance USD-M Aggregate Trade `nq`

Severity: **REQUIRED — source fidelity**

The current Binance USDⓈ-M Aggregate Trade stream documentation includes:
- `q`: quantity with all market trades;
- `nq`: normal quantity excluding trades involving RPI orders;
- `a`, `f`, `l`, `T`, `m` and other event fields.

The T1 CSV schema currently documents `quantity` but no `nq`. The draft does not identify this source-field omission.

Required revision:
- Add a source-field completeness table for SD-05, including native fields absent from T1 CSV.
- Explicitly distinguish `q` and `nq`.
- Decide whether `nq` is required in the canonical payload, preserved only in raw evidence, or intentionally unavailable for this T1 source version.
- Do not silently imply that the CSV contains all current exchange fields.

### R-04 — Explicitly define the RPI scope of SD-06/SD-07

Severity: **REQUIRED — semantic correctness / scope**

Binance USDⓈ-M documents that ordinary depth streams exclude RPI orders and provides a separate RPI Diff Book Depth Stream. The Phase B draft does not state whether the intended book includes or excludes RPI.

Required revision:
- State that the default depth dataset is non-RPI if that is the selected source.
- Explicitly identify the resulting visibility limitation.
- Treat RPI-inclusive depth as a separate source/domain extension unless a reviewed merge contract is defined.
- Do not label a non-RPI book as a complete view of all displayed liquidity.

### R-05 — Preserve or explicitly account for depth transaction time

Severity: **REQUIRED — provenance / temporal fidelity**

The Binance USDⓈ-M depth diff payload documents both event time `E` and transaction time `T`. T1's published CSV schema documents only `timestamp_ms` as event time.

Required revision:
- Record `T` as a native field absent from the current CSV mapping.
- Decide whether transaction time is needed in the canonical event envelope or whether preserving raw source evidence is sufficient for the initial contract.
- Keep event time, transaction time, collector receive time and T0 receipt/commit time distinct.
- Do not relabel event time as transaction or receive time.

### R-06 — Specify bounded handling for out-of-order depth events and unresolved gaps

Severity: **REQUIRED — recovery correctness**

The draft says sequence-aware handling is required but does not define the design-level behavior for bounded reordering, gap detection timeout, buffer exhaustion, or restart while a gap remains unresolved.

Required revision:
- Define whether the source adapter preserves arrival order or T0 may reorder by sequence.
- If buffering/reordering is allowed, specify a bounded buffer and overflow behavior.
- Specify when a gap becomes a durable discontinuity/quarantine outcome.
- Prohibit checkpoint advancement past unresolved sequence gaps.
- Specify the recovery transition: wait for missing events, reacquire a snapshot/new stream epoch, or remain unavailable. No silent skip.

## 3. Existing blockers correctly identified — retain them

The following draft blockers are valid and must remain open until evidence resolves them:
- Exact T1 source implementation/build mapping and field semantics.
- Stream epoch capture and snapshot-to-stream linkage.
- Collision-safe snapshot capture identity and group completeness.
- Exact Binance USD-M snapshot/diff bridge and recovery rules.
- Immutable source object/row locator and file close semantics.
- Canonical digest and decimal serialization.
- Atomic persistence of provenance, identity, outcomes and checkpoints.
- Non-Candle T0 API/dataset version compatibility.

The documented T1 schema is not proof that every live collector build emits complete, immutable and correctly framed data. Read-only inspection of the pinned T1 implementation is still required before contract freeze.

## 4. Positive review observations

- SD-05 native aggregate trade ID is correctly preferred over timestamp/price/quantity composites.
- The draft correctly identifies the misleading T1 names `first_update_id`/`last_update_id` as aggregate-trade first/last trade IDs, not book update IDs.
- SD-06 correctly treats quantities as absolute level quantities and zero as level deletion.
- Snapshot levels are correctly treated as a grouped object, not individually canonical snapshots.
- Event time is not conflated with collector receive time.
- Replay and conflict semantics reject silent overwrite.
- Synthetic test cases cover important malformed, duplicate, conflict and continuity conditions, and are clearly marked NOT EXECUTED.
- Explicit exclusions preserve the owner-approved architecture and paper-first guardrails.

## 5. Review verdict and next step

**Verdict: REQUEST CHANGES.**

Required:
1. Revise the Phase B design for R-01 through R-06.
2. Update the blocker table and synthetic test matrix to cover the revised semantics.
3. Keep any source-evidence-dependent contract item unfrozen until verified against the pinned T1 implementation and official USD-M source contract.
4. Submit the revised design for another review.

This review does not authorize code, DTO, parser, validator, tests, fixtures, DDL, database, data movement, source changes, network calls, T1→T0/T2 runtime connectivity, VPS/deployment or trading.

## 6. External protocol references checked

- Binance USDⓈ-M WebSocket Market Streams — Aggregate Trade fields including `a`, `q`, `nq`, `f`, `l`, `T`, `m`: https://developers.binance.info/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/market
- Binance USDⓈ-M WebSocket Market Streams — Diff Book Depth fields `E`, `T`, `U`, `u`, `pu`; ordinary depth stream and RPI depth stream scope: https://developers.binance.info/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/public

References were checked read-only on 2026-11-22. No exchange connection or market-data acquisition was performed.
