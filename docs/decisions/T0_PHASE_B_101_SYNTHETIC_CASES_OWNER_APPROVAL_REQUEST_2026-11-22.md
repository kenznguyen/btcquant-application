# Owner Approval Request — Execute 101 T0 Phase B Synthetic Cases

- Date: 2026-11-22
- Requested by: project workstream
- Governing design baseline: Revision 10 commit `b32d9af088099f92b09d113ecfa27056cfd9b83d`, blob `a8934cb862c330f1d1fa72aa1f3fdb2b22f9ac96`.
- Technical contract proposal: `docs/design/T0_PHASE_B_CANONICAL_DTO_DIGEST_CHECKPOINT_ATOMIC_PERSISTENCE_DESIGN_V1_2026-11-22.md`.
- Review: `docs/reviews/T0_PHASE_B_REVISION_10_EXACT_SHA_REVIEW_2026-11-22.md`.
- Current status: **APPROVAL REQUESTED — NOT APPROVED; NO TESTS OR FIXTURES CREATED/RUN**.

## Exact approval requested

Please approve or decline the following bounded work:

**Implement isolated synthetic fixtures and execute the existing 101-case Phase B matrix** for SD-05 aggregate trades, SD-06 depth diffs, SD-07 snapshots and cross-domain persistence/recovery.

Approval is limited to:
1. Create test-only DTO/validator/persistence test fixtures in a disposable temporary test environment.
2. Execute the 101 specified synthetic cases, preserving their existing expected outcomes unless a documented defect is raised for owner review.
3. Add no production market data, credentials, exchange connectivity, T1 runtime, VPS or T0 production database.
4. Do not change T1 collector source or connect T1 to T0/T2.
5. Do not create or mutate canonical production DDL/database; no import, promotion, cutover or migration.
6. Do not enable order execution, submit orders or change strategy/runtime.
7. Do not delete source evidence or implement delete-on-ack.
8. Record exact source SHA/blob, test command, test counts, failures, workflow run/job IDs, artifact IDs and logs. If a workflow is unavailable, report that explicitly rather than claiming CI PASS.

## Test scope

- SD-05: 14 cases — native field mapping, identity, replay/conflict, strict boolean/decimal/time validation and unavailable E/nq handling.
- SD-06: 31 cases — update range identity, U/u/pu sequence, snapshot bridge, overlap adjudication, gaps, replay/conflict, stream epoch provenance, RPI exclusion and bounded rejection.
- SD-07: 46 cases — producer identity pair, immutable attribute binding, duplicate/reuse conflict, source-kind separation, manifest completeness, empty capture, level validation and bounded-depth claims.
- Cross-domain: 10 cases — raw-object/canonical digest separation, stable delivery locator, source cursor vs book watermark, lost acknowledgement, atomic commit/rollback, restart/replay and no delete-on-ack.
- Total: **101 synthetic cases**.

These case counts identify the existing proposed matrix; they do not claim the tests already exist or pass.

## Preconditions before execution

1. Owner approves this exact bounded scope.
2. DTO/digest/checkpoint/atomicity proposal is reviewed and accepted as the test target, or the owner explicitly approves testing against the exact Revision 10 candidate while recording known unspecified fields as BLOCKED.
3. All fixtures are synthetic and isolated; no production or VPS database is mounted.
4. The implementation/test branch and source SHA are pinned before the first test run.
5. Failures are retained as evidence; no test is weakened or removed to obtain a pass.

## Approval record

- Decision: **PENDING**
- Approver: project owner
- Approved scope/version: pending
- Date: pending
- Restrictions or amendments: pending

Until this record is explicitly approved, do not create test fixtures, implement validators/persistence, execute the 101 cases or dispatch a workflow.
