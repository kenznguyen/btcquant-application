# T0 Phase B Revision 13 Codex Findings and Revision 14 Resolution

Date: 2026-11-23

## Review target and result

- Repository: `kenznguyen/btcquant-application`
- Review PR: [PR #11](https://github.com/kenznguyen/btcquant-application/pull/11), OPEN / NOT MERGED / DO NOT MERGE.
- Exact reviewed PR head: `982ea9e250bfca19bdd6ecb973956143dfe27df6`.
- Exact R13 design source commit/blob: `0476b76a96f5a1f9a1a5afd3b6843a15194f2f06` / `2c3e81c52ca10083e0d1c78ca3ef31858a47520d`.
- Codex review: **COMPLETED WITH THREE P2 FINDINGS**. This is an automated Codex PR review; it is not represented as a human review or test execution.

## Findings

1. **P2 — Stale fixture gate.** R13 retained R12 review-gate wording in the exit matrix and §14.3, allowing the 101-case work to be misread as unblocked by review of the wrong revision. Review comment `4659122865`, original line 602.
2. **P2 — Missing durable conflict evidence.** When a previously committed stable delivery locator is retried with changed bytes/digest, the design did not define a separate durable append-only record to retain the conflicting observation without creating a second completion. Review comment `4659122867`, original line 966.
3. **P2 — Ambiguous cursor update.** A quarantine path could be read as persisting the source cursor at a later sequence before the contiguous-frontier check, recreating the possibility of skipping an unfinished earlier sequence. Review comment `4659122869`, original line 973.

## Revision 14 resolutions

- **P2-1:** The operative 101-case matrix gate, Phase B exit criteria, explicit exclusions and §14.3 readiness section now require satisfactory review of the exact R14 SHA/blob. R12/R13 review statements are retained only as historical snapshots.
- **P2-2:** Added proposed append-only `SourceDeliveryIntegrityConflictV1` evidence. The changed bytes are first preserved as an immutable evidence object; the conflict record references the prior completion and both expected/observed digests. The original completion is unchanged, no second `SourceDeliveryCompletionV1` is created, and the retry returns `INTEGRITY_CONFLICT`. If conflicting bytes cannot be durably retained, fail closed without acknowledgement or checkpoint movement.
- **P2-3:** Transaction step 7 persists evidence, terminal outcome and gap state only; it does not update the source cursor/frontier. Step 9 is explicitly the only step allowed to update that frontier and does so only after recomputing the highest contiguous terminal sequence with compare-and-swap/monotonic-generation protection.
- Cross-domain synthetic case 9 now requires durable append-only conflict evidence, unchanged original completion, no second completion, and no checkpoint/book side effect.

## Exact Revision 14 identity

- Path: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_REVISION_14_2026-11-23.md`
- Exact source commit: `e91706168ce8731711951546deea9399872fa368`
- Exact document blob: `fdfe77d2bd162f2cb9ff9b2e7a6427dd8c3eacaf`
- Branch: `review/t0-phase-b-r14-three-p2-20261123`
- R14 status: documentation-only review candidate; NOT Contract Freeze.

## Verification and restrictions

- Documentation transformation checks: PASS for presence of the conflict evidence type, P2-3 step-7/step-9 separation, R14 operative review gates and updated cross-domain case 9.
- Tests/fixtures: NOT CREATED / NOT RUN. The owner-approved 101-case isolated synthetic scope remains gated on satisfactory independent review of exact R14 SHA/blob.
- GitHub Actions workflows/runs/jobs/artifacts: NONE verified for this R14 documentation change.
- Formal proofs, store durability tests and crash/restart tests: NOT RUN.
- Contract Freeze: NOT APPROVED.
- No production DTO/parser/validator/persistence implementation, DDL/database mutation, data movement, T0/T1 runtime, T2 integration, VPS/autostart, deployment, source cleanup or trading is authorized.
- Next: open review-only PR #12 against `review/t0-phase-b-r10-baseline-20261122`, request review of exact R14 source commit/blob, then record final PR head SHA and review status in the handoff/index.
