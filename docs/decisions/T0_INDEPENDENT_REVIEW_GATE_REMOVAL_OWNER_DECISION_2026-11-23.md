# Owner decision — remove mandatory independent review gate from T0

- Date: 2026-11-23
- Authority: explicit owner direction in the project conversation.
- Status: **APPROVED**

## Decision

Mandatory independent/second-person review is removed as a prerequisite or blocking gate for all T0 work, including design revisions, the Phase B contract workstream and the already-approved isolated synthetic test scope.

T0 may use an owner-directed self-review of the exact immutable source SHA/blob as its review gate. Independent review, Codex review or Graphify review may still be requested as optional advisory feedback, but its absence, quota exhaustion, queue status or incomplete result MUST NOT block T0 progress.

## Required controls retained

This decision changes only the reviewer requirement. It does not waive or replace:

1. Exact source SHA/blob identification for each reviewed revision.
2. Immutable revision history; corrections require a new revision, never amend a published revision.
3. Static self-review and explicit PASS/BLOCKED/NOT VERIFIED status with recorded evidence.
4. Required tests, synthetic cases, runtime/fault-injection tests, cross-language vectors, formal proofs or store-specific durability evidence applicable to the work.
5. Explicit owner approval where a scope or architecture decision requires it.
6. Existing fail-closed behavior, data ownership, security, paper-first and no-live-trading restrictions.

## Current application to T0 Phase B

- Current design candidate: Revision 21.
- Exact source commit: `81c5945eca0282d4dbbe5d6485274a1bb7513efb`.
- Exact document blob: `72cfe9145ccb7544f453a95839b6240b324b059d`.
- Exact-SHA static self-review: PASS; report `docs/reviews/T0_PHASE_B_R16_FINDINGS_R21_SELF_REVIEW_2026-11-23.md`.
- Owner-approved isolated synthetic scope remains exactly 101 cases: SD-05 14, SD-06 31, SD-07 46, cross-domain 10. It is no longer blocked by an independent-review requirement; execution still must remain within the approved isolated synthetic-only scope.
- Contract Freeze remains NOT APPROVED. No production implementation, DDL/database mutation, data movement, T0/T1 runtime, T2 integration, VPS/autostart, deployment, exchange connectivity, automatic execution or live trading is authorized by this decision.

## Interpretation

"Independent review not required" does not mean "technical verification not required." A self-review PASS can satisfy the review gate, but it cannot be represented as proof of runtime correctness, durability, exchange-protocol compliance or production readiness.
