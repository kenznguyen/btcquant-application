# Exact-SHA Review — T0 Phase B Revision 10

- Review date: 2026-11-22
- Target repository: `kenznguyen/btcquant-application`
- Exact target commit: `b32d9af088099f92b09d113ecfa27056cfd9b83d`
- Exact target blob: `a8934cb862c330f1d1fa72aa1f3fdb2b22f9ac96`
- Target: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_REVISION_10_2026-11-22.md`
- Review type: exact-SHA document/design review by the current assistant; **not an independent second-person review**.
- Review scope: owner-decision overlay, identity supersession, blocker register, SD-05/06/07, evidence claims, DTO/digest/checkpoint/atomicity readiness, approval boundaries.
- No source changes, tests, fixtures, DDL, data operations or runtime actions were performed.

## Verdict

**PASS WITH CONDITIONS FOR CONTINUED DOCUMENTATION; NOT READY FOR CONTRACT FREEZE.**

Revision 10 records the owner decisions, but it is an overlay on the full Revision 9 text rather than a fully consolidated successor. It should not be treated as the final frozen specification. The separate DTO/digest/checkpoint/atomicity design v1 is a proposal and requires its own review before freeze.

## Findings

### R10-01 — Stale Revision 9 status language remains inside the Revision 10 document

- Severity: **HIGH — documentation consistency**
- Evidence: the Revision 10 top override and §14 record B-13/B-16 CLOSED, B-17 OPEN and the accepted identity amendment. However, inherited sections still describe Revision 9 as current, say the Inventory supersession is not owner-approved, and say B-01..B-20 remain open with B-13/B-16/B-17 owner decisions pending.
- Impact: readers navigating directly to §1, §3, §10 or §12 can encounter contradictory authority/status statements. A top-level override reduces but does not remove this ambiguity.
- Required action: publish a consolidated successor that rewrites the affected inherited sections and clearly marks Revision 9 as immutable historical evidence. Keep R10 unchanged.

### R10-02 — Revision 10 is not a complete DTO/digest/checkpoint/atomic persistence contract

- Severity: **HIGH — freeze readiness**
- Evidence: R10 §1 says wire DTO, storage schema, digest encoding and checkpoint protocol are not frozen; §14.3 repeats that these are not frozen.
- Impact: owner scope decisions alone cannot support a Contract Freeze.
- Required action: define a versioned logical DTO, identity/digest preimage, source-delivery locator, independent source cursor/book watermark, atomic transaction boundary, crash/retry behavior, and store-specific durability proof. A separate documentation-only proposal v1 has now been created; it is not frozen.

### R10-03 — T1 parser/build evidence was not part of the R10 evidence baseline

- Severity: **HIGH — source provenance**
- Evidence: R10 §14.3 lists exact T1 parser implementation/build mapping as NOT VERIFIED. A subsequent read-only source audit found direct source mapping `T → trade_time → timestamp_ms`, but did not establish the build identity of the binary associated with imported/runtime data.
- Impact: source mapping can be proven without proving a historical deployed binary was built from that source.
- Required action: preserve B-17 OPEN until the actual producer binary/build is tied to the inspected source commit, or constrain the relevant import lineage to a verifiable pinned build.

### R10-04 — Proposed synthetic matrix is not execution evidence

- Severity: **MEDIUM — verification**
- Evidence: the 101-case matrix is design-only and not executed.
- Impact: identity conflict, replay, snapshot completeness, crash atomicity and watermark invariants remain unproven.
- Required action: obtain separate explicit owner approval for isolated synthetic test/fixture implementation and execution. Do not use production data or activate runtime.

### R10-05 — No independent second-person review exists for the exact R10 SHA

- Severity: **HIGH — governance**
- Evidence: prior R9 review is not a second-person review of R10; this review is authored by the same assistant context.
- Impact: the independent review gate remains unsatisfied.
- Required action: request a named independent reviewer to review the exact target SHA/blob and the subsequent consolidated DTO/digest/checkpoint proposal.

## Positive evidence

1. Owner decisions for B-13 and B-16 are explicit and bounded. B-17 remains conditional/open.
2. SD-06 identity excludes `stream_epoch`; SD-07 identity is exactly `(capture_producer_id, capture_sequence)`.
3. The document preserves fail-closed handling, immutable evidence, conflict retention, no delete-on-ack and no implementation authorization.
4. The separate source audit establishes the source-level T mapping without overclaiming deployed binary provenance.
5. The new contract proposal separates raw-object digest, semantic payload digest, delivery locator, native event identity and checkpoint state.

## Review status by dimension

| Dimension | Result | Notes |
|---|---|---|
| Owner authority/scope | PASS WITH CONDITIONS | B-13/B-16 accepted; B-17 open; no Contract Freeze |
| Identity consistency | PASS WITH CONDITIONS | Owner amendment recorded, but R10 inherited text needs consolidation |
| Source mapping | PARTIAL PASS | T mapping proven in source; runtime/build lineage unknown |
| DTO/digest/checkpoint | NOT FROZEN | Proposal v1 exists separately |
| Atomicity/recovery | DESIGN ONLY | No DB/SQLite crash or restore proof |
| Test evidence | NOT VERIFIED | 101 synthetic cases not executed |
| Independent review | NOT VERIFIED | Required second-person review absent |
| Implementation/runtime safety | PASS | No implementation/runtime actions performed |

## Recommended disposition

- Keep Revision 10 immutable.
- Use the new DTO/digest/checkpoint/atomicity proposal as input to a consolidated Revision 11.
- Keep B-01 PARTIALLY RESOLVED; B-02 OPEN; B-03 resolved only at source-mapping level; B-04..B-12 open or design-only as recorded in the proposal; B-14/B-15 and B-18/B-20 open; B-17 open pending build provenance; B-13/B-16 closed as owner-accepted exclusions.
- Obtain separate owner approval for the 101 synthetic test cases.
- Obtain independent second-person review on the exact consolidated source SHA/blob before any Contract Freeze request.

No Contract Freeze, implementation, tests, fixtures, database, DDL, T1/T0 runtime, T2 integration, deployment or trading activity is authorized.
