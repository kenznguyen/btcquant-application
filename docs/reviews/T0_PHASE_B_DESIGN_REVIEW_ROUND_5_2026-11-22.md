# T0 Phase B Revision 5 — Design Review

- Review date: 2026-11-22
- Exact reviewed design commit: `51a11272a7cc9204d2b42a255942614e36f40b6f`
- Exact reviewed design blob SHA: `9aeb036267e9dfce73e0b2405c7f4c9ef27cc5ab`
- Reviewed path: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`
- Scope: exact-commit design review of R-15/R-16 corrections, source/capture identity ownership, 84 proposed synthetic cases and B-01..B-20 preservation.
- Cross-checks: revision 5 self-review; revision 4 review; governing T0 source-domain inventory and ingestion contract (blob `17a502ba72136512c05cd4069edad799d9072908`); owner approval records.
- Tests/workflows/artifacts: NOT RUN / NONE. Synthetic matrix remains design-only.

## Verdict

**REQUEST CHANGES — PHASE B REVISION 5 NOT APPROVED.**

R-15 is materially improved: the design separates exchange-native anchor, producer-issued capture identity and T0 source-delivery locator. R-16 is addressed: retry reuses the immutable source-delivery locator and event/capture deduplication remain distinct. However, the direct REST capture producer is still described generically rather than assigned to the approved collector ownership boundary. This leaves capture identity issuance, producer registration and accountability ambiguous.

Contract freeze is NOT APPROVED. Implementation, database, runtime and Phase C remain NOT AUTHORIZED.

## Findings

### R-17 — HIGH: Direct REST capture producer is not bound to the approved T1 ownership boundary

**Location:** §5.2 identity domain 2; §5.3 minimum acceptance evidence; §7 provenance envelope. Related architecture: `docs/design/T0_SOURCE_DOMAIN_INVENTORY_AND_CANONICAL_INGESTION_CONTRACT_V1_2026-11-22.md` §2–§3.

Revision 5 says the producer of `BINANCE_USDM_REST_DEPTH_RESPONSE_V1` is “the direct REST capture producer (the component issuing the request and preserving its response)”. It does not identify the component/repository that is authorized to act as that producer, nor how its `capture_producer_id` is registered and bound to the source contract.

The governing source-domain inventory identifies T1 as the specialized microstructure collector and explicitly lists SD-07 as Binance USD-M REST depth snapshot via T1 snapshot/reconstruction. It assigns T0 canonical acceptance and provenance/validation, not exchange collection internals. The generic phrase “direct REST capture producer” leaves open whether T1, T0, or another collector issues the request and owns the producer namespace.

This is material because the producer issues `(capture_producer_id, capture_sequence)`, controls durable non-reuse across restarts, and binds identity to immutable response evidence. Without an explicit ownership binding, T0 cannot unambiguously validate the issuer or determine which source/collector registration is authoritative. It also creates a risk of accidentally moving exchange collection responsibility into T0 or creating an unapproved second collector.

**Required correction:** explicitly bind the direct REST capture producer to the approved source-capture owner for SD-07 (consistent with the current architecture, T1 in `kenznguyen/binance-futures-collector`), unless a separate owner-approved architecture decision authorizes a different collector. State that T0 only validates and preserves the producer identity/evidence at canonical ingestion and does not silently mint or replace it. Define the candidate registration binding between `capture_producer_id`, collector/repository identity, source kind, market/domain scope and producer version. Unknown, unregistered or mismatched producer identity must fail closed. Keep the producer allocation/fencing proof unfrozen and B-07 OPEN until evidence exists.

**Synthetic coverage required:** add cases for (1) direct REST capture issued by the registered T1 producer; (2) capture issued by an unregistered/unknown producer; (3) a producer ID registered for a different source kind/domain; (4) two active processes/clones using the same producer namespace and sequence concurrently; (5) stale producer state restored after restart attempting to reuse an ID; and (6) T0 attempting to replace/mint a capture ID instead of preserving the source producer identity. The oracle must distinguish an ownership/registration failure from a missing exchange-native `lastUpdateId`.

## Disposition of R-15 and R-16

| Finding | Disposition |
|---|---|
| R-15 | Materially addressed: exchange-native anchor, producer-issued capture identity and T0 source-delivery locator are distinct. Producer ownership/registration is still incomplete; R-17 added. |
| R-16 | Addressed in inspected sections: §4.5/§4.8 and acknowledgement matrix use immutable source-delivery locator; canonical event identity and capture identity are deduplicated separately. No remaining occurrence of the old ambiguous phrase was found. |

## Positive observations

- `lastUpdateId` is no longer misrepresented as a Binance-issued unique capture ID.
- Direct REST capture identity is conceptually producer-issued and bound to request parameters, response anchor, immutable response bytes/digest and producer evidence.
- T1 reconstructed-local-book capture identity is bound to upstream anchor, epoch, last contiguous applied update, continuity, generation, retained-depth policy and payload digest.
- Same capture identity + same evidence is replay; same identity + changed evidence is conflict; distinct acquisitions remain distinct even when payload/anchor/time match.
- Retry uses the immutable source-delivery locator; stream/process epoch is not a retry key.
- Snapshot remains bounded/source-scoped, not a full-book anchor.
- Synthetic matrix has 84 proposed cases: SD-05 14, SD-06 28, SD-07 32, cross-domain 10; NOT EXECUTED.

## Blocker and scope verification

- B-01..B-20: present in the reviewed design and remain OPEN; none removed, resolved or owner-accepted.
- B-07: remains OPEN; producer uniqueness, durable sequence, non-reuse/fencing and source evidence are not proven.
- Tests/workflows/artifacts: NOT RUN / NONE. No fixtures or test code created.
- Independent second-person reviewer identity: NOT VERIFIED; this report must not be represented as external second-person approval.
- Contract freeze: NOT APPROVED.
- Implementation/database/runtime/Phase C: NOT AUTHORIZED.
- Review is documentation-only. No design/source edits, code, DTO, parser, validator, fixtures, tests, DDL, database, data movement, T1 source/runtime, network, credentials, T1→T0/T2 runtime, VPS/deployment, Phase C or trading action occurred.

## Next step

Revise only the Phase B documentation and proposed synthetic matrix for R-17. Preserve B-01..B-20 unchanged and OPEN. Submit a new exact design commit/blob for review. Do not freeze contracts or begin implementation/Phase C before separate owner approval.