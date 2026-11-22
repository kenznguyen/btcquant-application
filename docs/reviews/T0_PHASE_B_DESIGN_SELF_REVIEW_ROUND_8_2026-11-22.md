# T0 Phase B Revision 8 — Documentation Self-Check

- Date: 2026-11-22
- Exact Revision 8 design commit: `9a5c65f3bc00876d98a070eee46072c5d8be368e`
- Exact Revision 8 design blob: `8f40248f2781cdf4111ef022b77843acea8279b2`
- Immutable Revision 7 design baseline: commit `f61fe365f2558569744cbc2a2ca555021a931f48`, blob `86825e77f69c6943096d8e9f4ecae75b413b2013`.
- Immutable Revision 6 source baseline: commit `9b69c18ea16731bf28efba7a92077e96a74107ce`, blob `7012a228561620f4447a0e363a2c5f27d734912a`.
- Scope: one documentation-only consistency correction to B-07 based on manual review of PR #7. No code, database, runtime or deployment work.

## Verdict

**SELF-CHECK PASS — READY FOR NEXT DESIGN REVIEW. NOT OWNER-APPROVED. NOT AN INDEPENDENT SECOND-PERSON REVIEW.**

## Finding P2-4 — B-07 composite identity ambiguity

Revision 7's main §5.2 correctly defines `(capture_producer_id, capture_sequence)` as the sole capture identity key, but blocker B-07 retained wording that could be read as binding symbol/market/source kind/update ID into a composite identity.

Revision 8 rewrites B-07 to explicitly state:
- The sole key is the T1-issued pair `(capture_producer_id, capture_sequence)`.
- Symbol, market, source kind, update anchor, timestamp, request/depth parameters and immutable payload/object digest are immutable attributes validated against the pair, never additional identity dimensions.
- Verifiable producer-origin attestation or trusted authenticated handoff is required.
- Independently verifiable namespace uniqueness, single-writer fencing, durable sequence non-reuse and rollback protection are required.
- Missing or unverifiable evidence keeps the capture quarantined; B-07 remains OPEN.

## Static verification

- Updated B-07 no longer contains the ambiguous “capture ID bound to symbol/market/kind/update ID” wording.
- B-01..B-20 remain OPEN; only B-07's explanatory wording/evidence requirement was clarified.
- Prior P2-1, P2-2 and P2-3 sections remain present.
- Proposed matrix remains 98 cases (SD-05 14, SD-06 28, SD-07 46, cross-domain 10), NOT EXECUTED.
- Revision 7 design blob and Revision 6 source blob are pinned above and remain unchanged.
- Static document inspection only. No tests, fixtures, workflows or artifacts executed.

## Status and exclusions

- B-01..B-20: OPEN; B-07 OPEN pending independent proof.
- Contract freeze: NOT APPROVED.
- PR #7 Codex review of head `f623bc8dd878bf4f897f727f07afbed968f581c4`: PENDING at time of this self-check; the manual P2-4 finding has been recorded in PR #7 discussion.
- Independent second-person review: NOT VERIFIED.
- Tests/workflows/artifacts: NOT RUN / NONE.
- No code, DTO, parser, validator, fixture, test, DDL, database, data movement, network, credentials, collector activation, runtime integration, VPS/deployment, Phase C or trading action occurred.
- Revision 8 is a candidate documentation revision, not an owner-approved contract and not implementation authorization.

## Next step

Submit the exact Revision 8 design commit/blob for a separate design review after the PR #7 automated review result is recorded. Keep Revision 7 and Revision 6 immutable.
