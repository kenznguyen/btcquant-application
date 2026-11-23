# T0 Phase B R16 findings — R21 self-review record

Date: 2026-11-23

## Owner direction

The owner directed correction of the two R16 self-review findings in a new immutable revision and explicitly removed mandatory independent review from T0. Independent review is optional feedback only and MUST NOT gate T0 progress or the already-approved isolated 101 synthetic cases. The operative review gate is a static self-review of the exact current source SHA/blob.

## Immutable revision chain

- R16 parent: commit `12f2e1db923c264660ab93b6139cb512d96a78a8`, document blob `c2be5412668b0945c5f6f51e1aeaf787383a6676`; unchanged.
- R17 first correction attempt: commit `7d722837f2156f0cd2c2b31d974b21e031e5682f`, blob `2493bd2d4f18979f815768df754cf07820e37bfc`; immutable. Its self-review identified stale revision labels, an over-escaped NUL prefix and missing explicit numeric field-tag assignment.
- R18/R19/R20 are immutable intermediate successors; they are retained as history and were not amended.
- R21 final candidate: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_REVISION_21_2026-11-23.md`.
- Exact R21 source commit: `81c5945eca0282d4dbbe5d6485274a1bb7513efb`.
- Exact R21 document blob: `72cfe9145ccb7544f453a95839b6240b324b059d`.

## R16 findings resolved

### P2-1 — source cursor / quarantine contradiction

R21 Annex A §8 step 7 now persists source evidence, terminal outcome and gap state without directly writing the source cursor or book watermark. Durable terminal outcomes, including quarantine/gap/resource outcomes, are eligible for contiguous-frontier evaluation only in step 9. Step 9 is the sole source-cursor/frontier writer and advances only after all preceding sequences have durable terminal outcomes. Changed-content retries at an already-completed locator append integrity-conflict evidence, create no second completion and do not advance the cursor. This is aligned with §4.8 and the existing 101-case matrix.

### P2-2 — ambiguous / recursive canonical digest preimage

R21 §5.2 defines an allowlisted semantic projection for SD-05, SD-06 and SD-07. It excludes the envelope except explicitly listed domain identity, excludes raw/source-object digest aliases and excludes derived `canonical_payload_sha256` and `canonical_levels_sha256` from their own preimages. SD-07 level digest has its own versioned prefix. Field tags are assigned consecutively from 1 in the published field order; nested level tags are fixed. NUL framing is represented as a single `\\0` byte escape.

## R21 exact-SHA static self-review

| Check | Result |
|---|---|
| Current revision identity / exact R21 gate references | PASS |
| §8 step 7 does not write source cursor; quarantine/gap terminal eligibility deferred to step 9 | PASS |
| §8 step 9 sole contiguous source-cursor update | PASS |
| Per-domain digest allowlists present | PASS |
| Raw/source-object and recursive digest outputs excluded | PASS |
| Stable field-tag assignment defined | PASS |
| Canonical digest NUL prefix exact | PASS |
| Independent review explicitly non-required/non-gating for T0 | PASS |
| Old R17/R18/R19/R20 exact-SHA gates absent from operative text | PASS |
| Approved synthetic matrix remains exactly 101 cases (14/31/46/10) | PASS |

**Self-review verdict: PASS** on exact R21 commit/blob above.

Scope of review: static document inspection and scripted assertions over the exact fetched R21 document. This is not a runtime test, filesystem fault-injection test, cross-language digest vector test, crash/recovery proof, formal proof or implementation test.

## Current project status

- PR #14 remains review-only, OPEN / NOT MERGED / DO NOT MERGE.
- Independent review: NOT REQUIRED for T0; optional and non-gating.
- 101 synthetic fixtures/tests: NOT CREATED / NOT RUN. The owner-approved scope is unchanged. They may proceed after this exact-SHA self-review PASS, within the existing isolation restrictions.
- GitHub Actions workflows/artifacts for R21: NONE VERIFIED.
- Contract Freeze: NOT APPROVED.
- Production implementation, DTO/parser/validator/persistence implementation, DDL/DB mutation, data movement, T0/T1 runtime, T2 integration, VPS/autostart, deployment, exchange connectivity, automatic execution and live trading remain NOT AUTHORIZED.
