# T0 Source Domain Inventory — Phase B Identity Amendment v2

- Date: 2026-11-22
- Base inventory: `docs/design/T0_SOURCE_DOMAIN_INVENTORY_AND_CANONICAL_INGESTION_CONTRACT_V1_2026-11-22.md` (blob `17a502ba72136512c05cd4069edad799d9072908`).
- Owner decision: `docs/decisions/T0_PHASE_B_BOUNDED_EXCLUSIONS_AND_IDENTITY_SUPERSESSION_OWNER_DECISION_2026-11-22.md`.
- Status: **OWNER-APPROVED AMENDMENT FOR PHASE B SD-06/SD-07 IDENTITY ONLY; REMAINDER OF INVENTORY REMAINS DESIGN PROPOSAL**.

## Superseding identity rules

| Domain | Approved Phase B identity | Not part of identity | Rules |
|---|---|---|---|
| SD-06 depth diff | `(exchange, market_type, symbol, first_update_id, final_update_id)` subject to proof of exchange namespace uniqueness | `stream_epoch`, timestamps, delivery locator, collector process/connection IDs | `stream_epoch` is continuity/capture provenance only. It must not be appended to canonical identity to conceal an unproven exchange namespace. |
| SD-07 snapshot capture | Exactly `(capture_producer_id, capture_sequence)` | Exchange/market/symbol/source kind/anchor/event type/time/request/depth parameters/version/digest/delivery locator | All excluded fields are immutable attributes bound to the pair. Reuse of the pair with changed attributes is conflict/quarantine. `(side, price)` identifies a level within a capture, not a capture. |

## Scope boundary

- This amendment supersedes only the conflicting SD-06 and SD-07 identity examples in Inventory v1 for Phase B.
- All other Inventory v1 content remains proposal-level and is not frozen by this amendment.
- The amendment does not approve canonical DTOs, physical schemas, digest encoding, checkpoint semantics, storage, APIs, T1/T0 runtime, T2 connectivity or implementation.
- T0 remains the sole canonical owner; T1 remains source-capture owner for SD-07; raw source evidence and provenance must be preserved.
- Contract Freeze remains **NOT APPROVED**.