# T0 Phase B Design — Second-Round Review Request

- Date: 2026-11-22
- Review type requested: independent documentation/design review
- Revised design: docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md
- Revised design commit: 75e593517ec31d2e2a75ed0050e80ab5dd52edf2
- Revised design blob SHA: 56f2012d6625e5af328d7d5881d892a38a2121e9
- Prior review: docs/reviews/T0_PHASE_B_DESIGN_REVIEW_2026-11-22.md, commit 347dbcec6f7ddedac4ac1c8e90ee57c549ae49ef
- Prior verdict: **REQUEST CHANGES**
- Self-review report: `docs/reviews/T0_PHASE_B_DESIGN_SELF_REVIEW_ROUND_2_2026-11-22.md`, commit `2f6317b28502bc06202daf673f1f32c41f847c88`.
- Self-review verdict: **REQUEST CHANGES — PHASE B DESIGN NOT APPROVED**. Findings R-07..R-11 added; R-01..R-06 disposition recorded individually.
- Independent second-person review: **NOT PERFORMED**; this report is explicitly a self-review.
- Implementation: **NOT AUTHORIZED / NOT STARTED**
- Synthetic tests: **DESIGNED ONLY / NOT EXECUTED**
- Workflows/artifacts: **NOT RUN / NONE**

## 1. Scope of revision

The revised design covers SD-05 aggregate trades, SD-06 ordinary (non-RPI) depth diffs and SD-07 ordinary (non-RPI) snapshots. It remains documentation-only and does not freeze canonical DTOs, storage, digests, checkpoints, source schemas or transport.

## 2. Finding disposition requested for review

| Finding | Revision made | Remaining evidence dependency |
|---|---|---|
| R-01 | Canonical SD-06 identity candidate is now (exchange, market_type, symbol, first_update_id, final_update_id). stream_epoch is capture/continuity provenance only. Same range/same payload across epochs is replay; changed payload is conflict. | Exchange update-ID uniqueness scope across reconnects/restarts is not yet proven. SD-06 canonical acceptance remains blocked until verified. |
| R-02 | Snapshot acceptance requires source-generated immutable capture ID, explicit group framing, expected count/equivalent completeness declaration, finalized object digest and a bound completion manifest. EOF/rotation/elapsed time/row count alone are explicitly insufficient. Partial groups are quarantined. | Current T1 CSV has no capture ID or completeness manifest; all snapshots in that schema version remain not canonically acceptable. |
| R-03 | Added Binance native-field completeness table. Distinguishes q (all-trades quantity) from nq (excluding RPI-involved trades). Current CSV quantity is a candidate mapping to q pending pinned T1 parser/source verification; absent nq is marked unavailable, never derived. | Inspect pinned T1 source/raw retention and decide whether nq becomes a canonical field or remains raw-only/unavailable for this source version. |
| R-04 | Explicitly scopes ordinary SD-06/SD-07 depth as non-RPI; states that it is not a complete view of all displayed liquidity. RPI-inclusive depth is out of Phase B and requires a separate reviewed contract. | Verify actual snapshot source behavior and any future RPI stream/merge contract separately. |
| R-05 | Added separate E event time and T transaction time treatment; current CSV lacks T and records it unavailable. Collector receive and T0 receipt/commit clocks remain distinct. | Inspect T1 source/raw retention; do not infer T from E or import time. |
| R-06 | Defined arrival-order preservation, count+age bounded reorder buffer, GAP_PENDING, durable GAP_UNRESOLVED, overflow fail-closed behavior, checkpoint fence and recovery via complete new snapshot/new epoch/verified bridge or remain unavailable. | Numeric buffer/age/wait bounds and exact Binance bridge rules remain unfrozen pending measurement and owner review. |

## 3. Synthetic test matrix update

The design now proposes **45 synthetic cases**:
- SD-05: 10 cases covering q/nq, identity, replay/conflict, validation and time semantics.
- SD-06: 20 cases covering E/T, non-RPI scope, cross-epoch identity, sequence continuity, bounded reordering, gap recovery, checkpoint safety and idempotent retry.
- SD-07: 15 cases covering capture identity, manifest completeness, partial writes, empty-book declaration, non-RPI scope, replay/conflict and snapshot-to-stream linkage.

All are design cases only. No parser, validator, fixture, test code or workflow was created or run.

## 4. Remaining blockers

The design retains B-01..B-13 and adds:
- B-14: numeric reorder/gap resource bounds;
- B-15: nq and depth T source fidelity;
- B-16: RPI visibility/source-domain scope.

These are not claimed as resolved by prose. Source-dependent contracts remain unfrozen.

## 5. Reviewer checklist

Please assess:
1. Whether R-01's canonical identity separation and cross-epoch replay/conflict rules are correct, including the explicit block pending update-ID uniqueness evidence.
2. Whether R-02's capture manifest/completeness gate is sufficient and fail-closed for interrupted, repeated and empty snapshots.
3. Whether R-03 correctly distinguishes q/nq and avoids implying complete native-field coverage from the T1 CSV.
4. Whether R-04 accurately scopes ordinary depth as non-RPI for both diffs and snapshots.
5. Whether R-05 preserves E, T, receive time and T0 times without substitution.
6. Whether R-06's bounded reorder/gap/checkpoint/recovery state machine is safe and complete without inventing numeric limits.
7. Whether the 45-case synthetic matrix and B-01..B-16 blocker list cover the identified risks without implying implementation readiness.

## 6. Explicit exclusions

No code, DTO, parser, validator, adapter, tests, fixtures, workflow, DDL, database, data movement, network/exchange calls, credentials, T1 source/runtime changes, T1→T0/T2 connectivity, VPS/deployment, source deletion, order submission or trading action is authorized by this review request.

T0 remains the sole canonical owner; T1 implementation remains in its own repository; raw source evidence is preserved; no delete-on-ack; paper-first/no-live-trading guardrails remain unchanged.
