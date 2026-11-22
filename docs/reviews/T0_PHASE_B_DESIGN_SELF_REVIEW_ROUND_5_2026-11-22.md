# T0 Phase B Revision 5 — Documentation Self-Review

- Review date: 2026-11-22
- Exact design commit: `51a11272a7cc9204d2b42a255942614e36f40b6f`
- Exact design blob SHA: `9aeb036267e9dfce73e0b2405c7f4c9ef27cc5ab`
- Reviewed path: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`
- Scope: documentation-only correction of R-15/R-16 and expansion of proposed synthetic cases. B-01..B-20 were required to remain byte-identical and OPEN.
- Method: exact revision 5 readback; compare blocker section byte-for-byte with exact revision 4 design blob; inspect identity definitions, retry/checkpoint wording, matrix counts and exclusions.
- Tests/workflows/artifacts: NOT RUN / NONE. Synthetic cases are design proposals only.

## Self-review result

**SELF-CHECK PASS — READY FOR NEXT DESIGN REVIEW. NOT OWNER-APPROVED; NOT INDEPENDENTLY REVIEWED.**

### R-15 — capture identity domains and producer

- Explicitly separates:
  1. Exchange-native response/book anchor (`lastUpdateId`); not treated as a unique capture ID.
  2. Producer-issued capture identity, candidate (`capture_producer_id`, `capture_sequence`).
  3. T0 source-delivery/import locator, bound to immutable source object and stable group locator.
- Direct REST capture ID is issued by the component acquiring and preserving the response, not attributed to Binance without evidence.
- T1 reconstructed-local-book capture ID is issued by the T1 serializer and bound to upstream snapshot anchor, epoch, last contiguous applied update, continuity, local-book generation, retained-depth policy and immutable payload digest.
- Same capture ID + same immutable evidence is replay; same ID + changed evidence is conflict; separate acquisitions receive distinct capture IDs even if `lastUpdateId`, timestamp and payload match.
- Producer namespace uniqueness, durable sequence allocation, restart non-reuse and fencing remain candidate/unverified. B-07 is intentionally still OPEN; this document does not claim source implementation evidence or canonical acceptance readiness.

### R-16 — retry identity

- Replaced ambiguous “same immutable message identity” wording.
- §4.5 and §4.8 now retry using the same immutable source-delivery locator.
- Native exchange-event deduplication and producer-issued snapshot capture deduplication are independent identity operations.
- Stream/process epoch remains continuity provenance, not a retry identity.
- No remaining occurrence of the ambiguous phrase was found in the revision 5 design.

### Synthetic matrix

- SD-05: 14 proposed cases.
- SD-06: 28 proposed cases.
- SD-07: 32 proposed cases, adding capture producer identity, restart reuse/collision, same-capture retry, distinct repeated acquisitions, response mismatch and T1 reconstructed-book evidence cases.
- Cross-domain: 10 proposed cases, adding source-delivery retry idempotency and capture deduplication across separately evidenced delivery locators.
- Total: **84 proposed cases**. NOT EXECUTED; no fixtures or test code created.

### Blocker preservation

- B-01..B-20 section is byte-identical to the exact revision 4 design.
- All 20 blockers remain OPEN; none removed, resolved or owner-accepted.

### Scope and gates

- Documentation-only. No code, DTO, parser, validator, tests, fixtures, DDL, database, data movement, T1 source/runtime, network, credentials, T1→T0/T2 runtime, VPS/deployment, Phase C or trading action.
- Contract freeze: NOT APPROVED.
- Implementation/database/runtime/Phase C: NOT AUTHORIZED.
- Independent second-person reviewer identity: NOT VERIFIED.
- Next step: submit exact revision 5 commit/blob for design review; keep B-01..B-20 open unless evidence-backed or explicitly bounded owner acceptance is recorded.