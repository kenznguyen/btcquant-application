# Review Scope — T0 Phase B Design Revision 6

## Immutable source target

- Repository: `kenznguyen/btcquant-application`
- Source commit: `9b69c18ea16731bf28efba7a92077e96a74107ce`
- Source document: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`
- Exact source blob SHA-1: `7012a228561620f4447a0e363a2c5f27d734912a`
- Review snapshot: `review-snapshots/t0-phase-b-design-r6-2026-11-22/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`
- The snapshot content was fetched from the pinned source commit without edits.

## Requested design review

Review Revision 6 specifically for:
1. Whether R-17 is fully resolved: SD-07 direct REST response capture and T1 reconstructed-local-book capture remain owned by `kenznguyen/binance-futures-collector`.
2. Whether T0 producer registration binding is sufficiently precise, scoped and fail-closed for producer ID, collector/repository identity, source kind, exchange/market/domain/symbol scope, implementation version and identity-scheme version.
3. Whether T0 is prevented from minting, substituting or rewriting T1-issued capture identity.
4. Whether the seven new SD-07 synthetic cases (33–39) cover registered, unknown, mismatched, concurrent-clone, stale-state rollback and T0 identity-minting scenarios.
5. Whether the three identity domains and retry/source-delivery locator semantics from R-15/R-16 remain consistent.
6. Whether B-01 through B-20 remain explicitly open and whether the proposed 91-case matrix is internally consistent.
7. Any additional correctness, architecture, security, provenance, recovery or testability gaps.

## Required reviewer deliverable

Return one explicit verdict: **APPROVE**, **REQUEST CHANGES**, or **NOT VERIFIED**. For each finding include severity, exact document section/line, rationale, impact and a concrete remediation. State whether the review is independent of the design author and identify any evidence that could not be verified.

## Evidence and current limits

- Revision 6 self-check: PASS / READY FOR NEXT DESIGN REVIEW; it is not an independent review.
- Proposed synthetic cases: 91 total; **DESIGNED ONLY / NOT EXECUTED**.
- Tests, workflows and artifacts: **NOT RUN / NONE** for this design review target.
- B-01 through B-20 remain OPEN.
- Contract freeze: NOT APPROVED.
- Implementation, database changes, runtime/data movement, Phase C, deployment, T1/T2 runtime connection and trading: NOT AUTHORIZED.

## Review-only restrictions

**DO NOT MERGE.** This PR is a byte-for-byte review mirror and scope manifest only. Do not change production-path files, implement fixes, execute tests/workflows, access canonical data or runtime, alter T1 source/runtime, connect T1/T2, deploy, or perform trading actions. Any subsequent changes require separate owner authorization and a new exact-source review snapshot.
