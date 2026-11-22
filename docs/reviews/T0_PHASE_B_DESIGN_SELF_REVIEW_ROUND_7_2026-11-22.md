# T0 Phase B Revision 7 — Documentation Self-Check

- Date: 2026-11-22
- Exact design path: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`
- Source baseline (preserved unchanged): Revision 6 commit `9b69c18ea16731bf28efba7a92077e96a74107ce`, blob `7012a228561620f4447a0e363a2c5f27d734912a`
- Scope: documentation-only correction of three P2 findings from PR #6 automated review. No code, database, runtime or deployment work.

## Verdict

**SELF-CHECK PASS — READY FOR NEXT DESIGN REVIEW. NOT OWNER-APPROVED. NOT AN INDEPENDENT SECOND-PERSON REVIEW.**

## P2-1 — Identity key vs immutable attributes

- Capture identity key is exactly `(capture_producer_id, capture_sequence)`, independently unique and non-reusable.
- Anchor, timestamp, source kind, symbol/scope, request/depth policy, producer/scheme versions and immutable payload evidence are immutable attributes, not identity-key dimensions.
- Same pair + same immutable evidence is replay; same pair + any changed or contradictory attribute is conflict/quarantine.
- Synthetic cases 40–42 cover anchor, timestamp/limit/depth policy, source kind/scope/version/digest reuse.

## P2-2 — Verifiable T1 producer origin

- Registration and digest alone are explicitly insufficient to prove T1 origin.
- Candidate evidence modes are (A) verifiable T1 producer attestation against an owner-approved trust binding, or (B) trusted authenticated handoff with an authenticated workload principal and durable receipt binding producer pair, source kind/scope, versions, immutable digest and delivery locator.
- Self-asserted ID, unsigned manifest, digest alone or unauthenticated upload fail closed.
- Trust root, key/workload identity lifecycle, signature/receipt format, transport, verifier and replay policy remain NOT SPECIFIED / NOT FROZEN. No existing handoff is claimed to provide proof.
- Synthetic cases 43–45 cover valid binding and missing/invalid/revoked/mismatched proof.

## P2-3 — Namespace uniqueness and fencing proof

- Acceptance requires independently verifiable unique namespace provisioning, single-writer fencing, durable monotonic sequence allocation, restart/restore/clone rollback protection and commit-before-ack evidence.
- Registry row or producer-supplied boolean is not proof.
- Without verifiable proof, every capture from the namespace remains QUARANTINED / NOT CANONICALLY ACCEPTABLE.
- Synthetic case 46 enforces fail-closed behavior; positive cases 33–34 now explicitly require origin and fencing proofs.

## Static verification

- Revision 7 header and Revision 6 immutable-baseline reference present.
- Composite capture identity proposal superseded by producer pair key and immutable attribute comparison.
- Origin-authenticity requirements and unresolved trust lifecycle limitations present.
- Namespace uniqueness, single-writer fencing, durable non-reuse and rollback protections are mandatory acceptance preconditions.
- Proposed matrix reconciles: SD-05 14 + SD-06 28 + SD-07 46 + cross-domain 10 = **98 cases**.
- B-01..B-20 are retained unchanged and OPEN.
- Revision 6 source blob is referenced exactly; no overwrite of Revision 6.
- Static/document comparison only. No tests, fixtures, workflows or artifacts executed.

## Status and exclusions

- B-01..B-20: **OPEN / unchanged**; B-07 remains OPEN.
- Contract freeze: **NOT APPROVED**.
- Tests/workflows/artifacts: **NOT RUN / NONE**.
- Independent second-person review: **NOT VERIFIED**.
- No code, DTO, parser, validator, fixture, test, DDL, database, data movement, network, credentials, collector activation, runtime integration, VPS/deployment or trading action occurred.
- Revision 7 is a candidate design revision, not an owner-approved contract and not implementation authorization.

## Next step

Submit the exact Revision 7 design commit/blob for design review. Preserve Revision 6 unchanged and keep B-01..B-20 OPEN until evidence-backed resolution or bounded owner acceptance.
