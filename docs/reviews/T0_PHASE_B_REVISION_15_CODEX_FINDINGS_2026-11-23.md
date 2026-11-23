# Revision 15 Codex Review Findings — 2026-11-23

## Exact review target

- Repository: `kenznguyen/btcquant-application`
- Review-only PR: #13 — Revision 15
- Exact reviewed PR head: `6554529d9d8bd136c85643fdc43a68256b7e1989`
- Immutable R15 design source commit: `5bbbd6ac253b4f8c8d9aeccb28d77170b1897919`
- Exact R15 document blob: `2b1cb4a8d0a7d40f9ebfb29ccaf9d9d14930cfc0`
- Codex review ID: `PRR_kwDOVzv83s8AAAABZnV1sw`
- Review submitted: `2026-11-22T19:13:33Z`
- Review state: COMPLETED / COMMENTED
- Three unresolved P2 threads on the exact reviewed head:
  - `PRRT_kwDOVzv83s66nG14` — comment `4659555256`
  - `PRRT_kwDOVzv83s66nG19` — comment `4659555264`
  - `PRRT_kwDOVzv83s66nG2D` — comment `4659555270`

## Findings

### P2-1 — Current-status test gate still points to R12

The current-status line at the top of R15 still says fixture creation/execution follows independent review of exact Revision 12 SHA/blob. This is an operative gate, not historical context, and conflicts with the R15 gate in §9, §14.3 and Annex A. Replace it with the exact R15 SHA/blob requirement.

### P2-2 — Digest-alias mismatch is not explicit in the 101-case matrix

The design normatively requires `source_object.sha256 == raw_object_sha256`, but the existing matrix does not explicitly require a test where these two aliases disagree. The generic SD-07 digest mismatch and changed-locator retry case do not prove this specific check or its required ordering.

Resolution must specify the alias mismatch within an existing approved case, without increasing the 101-case count, and assert rejection before identity resolution, canonical completion or acknowledgement.

### P2-3 — Filesystem publication can overwrite existing evidence

The filesystem persistence recipe allows a stable object/version path and atomic rename, which can replace an existing destination. A changed-content retry could overwrite previously preserved evidence before the integrity-conflict record is appended.

Resolution must require exclusive/no-clobber publication or a distinct immutable evidence key. If the target already exists, verify its exact digest and treat matching content as already durable; mismatching content must never be overwritten and must be preserved under a distinct immutable key before conflict evidence is committed. If preservation cannot be proven, fail closed without ACK/checkpoint advancement.

## Status

- R15 design: documentation-only; source and blob identities verified.
- Codex review of exact PR head: COMPLETED WITH 3 P2 FINDINGS.
- All three review threads: OPEN / UNRESOLVED.
- PR #13: OPEN / NOT MERGED / DO NOT MERGE.
- Workflow runs/jobs/artifacts for exact PR head: none returned.
- Tests/fixtures: NOT CREATED / NOT RUN.
- Formal proofs: NOT RUN.
- Contract Freeze: NOT APPROVED.
- 101 synthetic cases remain owner-approved but execution remains gated on satisfactory independent review of the corrected successor revision's exact SHA/blob.

## Restrictions

No production DTO/parser/validator/persistence implementation, DDL/database mutation, data movement, T0/T1 runtime, T2 integration, VPS/autostart, deployment, exchange connectivity, live trading or real orders. Do not merge PR #13. Preserve R15 unchanged; any corrections belong in a new immutable successor revision.
