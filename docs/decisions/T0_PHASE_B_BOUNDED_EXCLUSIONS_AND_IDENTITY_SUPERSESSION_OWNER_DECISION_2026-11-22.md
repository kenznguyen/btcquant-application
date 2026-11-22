# T0 Phase B — Owner Decision: Bounded Exclusions and Identity Supersession

- Date: 2026-11-22
- Applies to Revision 9 design commit `5405928cf1ec61cf979453812d158caa8db18d4a`, blob `86c490be08961b02d03ba0a7986befe3e142b9df`.
- Decision type: owner design/scope decision only.
- Contract Freeze: **NOT APPROVED**. Implementation/runtime/data movement: **NOT AUTHORIZED**.

## Decisions

1. **B-13 — ACCEPTED BOUNDED EXCLUSION.** Phase B is limited to canonical ingestion/acceptance design. Non-candle read API, dataset-version read compatibility, API DTOs, T2 access and runtime integration are excluded and require a separately versioned read-contract decision. B-13 is CLOSED as an owner-accepted scope exclusion only.
2. **B-16 — ACCEPTED BOUNDED EXCLUSION.** Phase B depth scope is ordinary Binance USD-M non-RPI depth only. It is not a representation of all displayed liquidity. No RPI capture/merge, RPI inference or all-liquidity completeness claim is allowed. RPI requires separate source-domain/sequence/snapshot/merge design. B-16 is CLOSED as an owner-accepted scope exclusion only.
3. **B-17 — CONDITIONALLY ACCEPTED BOUNDED EXCLUSION; BLOCKER REMAINS OPEN.** The current CSV-backed contract may carry verified native aggTrade trade time T and excludes event time E. E must not be inferred from timestamp_ms; no receive-time substitution is allowed. Closure requires read-only inspection of the exact pinned T1 parser/build proving timestamp_ms is sourced from native T, with exact repository commit/blob/build evidence. If proof is absent or contradictory, quarantine and retain B-17 OPEN.
4. **Inventory identity supersession — ACCEPTED for Phase B SD-06/SD-07 only.** SD-06 canonical update identity is `(exchange, market_type, symbol, first_update_id, final_update_id)` subject to proof of exchange namespace uniqueness; `stream_epoch` is continuity/capture provenance only, not identity. SD-07 capture identity is exactly `(capture_producer_id, capture_sequence)`; all other capture fields are immutable attributes. This does not approve unrelated Inventory proposals, DTOs, schemas, digest encoding, checkpoints, storage or implementation.

## Blocker register disposition

- B-13: **CLOSED — OWNER-ACCEPTED BOUNDED EXCLUSION**.
- B-16: **CLOSED — OWNER-ACCEPTED BOUNDED EXCLUSION**.
- B-17: **OPEN — CONDITIONALLY ACCEPTED SCOPE; SOURCE-PARSER PROOF REQUIRED**.
- B-01..B-12, B-14..B-15, B-18..B-20: remain **OPEN**.
- No other blocker is waived, removed or considered complete.

## Evidence and restrictions

- Revision 9 full design review remains PASS WITH CONDITIONS, not Contract Freeze approval.
- The 101-case matrix remains DESIGN ONLY / NOT EXECUTED.
- T1 parser behavior, producer attestation/allocator/fencing, Binance overlap protocol evidence, persistence atomicity, resource ceilings, DTO/digest/checkpoint specifications and independent second-person review remain unverified or incomplete.
- No code, parser, DTO, validator, test, fixture, DDL, database, API, data transfer, collector activation, T0/T1 runtime, T2 integration, deployment, autostart or trading action is authorized.
- Preserve raw source evidence; no delete-on-ack.

## Next gate

Prepare Revision 10 and a Contract Freeze readiness dossier. Contract Freeze can be presented only after remaining blockers/evidence are resolved, Inventory amendment is recorded, and independent second-person review is completed against the exact owner-approved source SHA/blob.