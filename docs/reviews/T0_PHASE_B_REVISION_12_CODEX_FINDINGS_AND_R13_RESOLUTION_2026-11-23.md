# T0 Phase B Revision 12 Codex Findings and Revision 13 Resolution — 2026-11-23

## Review evidence

- Review request: PR #10 — https://github.com/kenznguyen/btcquant-application/pull/10
- Reviewed PR head / exact R12 source commit: `29c47fcf9a761af00f72c043142ac2cca7b708ab`
- Exact R12 design blob: `0c726fc05e76c41986130f8ee165d3dc67ce7044`
- Codex review: **COMPLETED WITH FINDINGS**, 4 unresolved P2 findings; review summary comment ID `7082411398`.
- PR #10 remains OPEN / NOT MERGED / DO NOT MERGE. The review was on R12, not R13.
- Workflow runs for exact R12 commit: none returned. Tests, fixtures and formal proofs: NOT RUN / NOT CREATED.

## Findings and R13 disposition

### P2-1 — Current-status handoff points to the wrong revision

**Finding:** `docs/PROJECT_SESSION_HANDOFF.md` and `docs/T0_ACTIVE_SCOPE_INDEX.md` still directed the next reviewer to R11/R12 rather than the current exact review target.

**R13 disposition:** Both current-status sections are updated to identify Revision 13 and its exact source commit/blob. Previous R12 status is retained only as a historical snapshot.

### P2-2 — SD-05 quantity test contradicts inspected source mapping

**Finding:** R12 case SD-05 #4 treated CSV `quantity` as unverified against native `q`, although the inspected T1 source proves `q → quantity`. Remaining uncertainty concerns deployed/imported build provenance and f64/12-decimal fidelity.

**R13 disposition:** SD-05 #4 now asserts the inspected-source `q → quantity` mapping. It separately tests that `nq` remains unavailable and retains the historical deployed-build and exact decimal/raw-byte fidelity limitations. This does not claim deployed binary provenance.

### P2-3 — Opaque delivery locator cannot define an ordered resume cursor

**Finding:** R12 checkpoint held only the last completed opaque locator. Out-of-order delivery could advance the cursor past an unfinished earlier observation and skip it on restart.

**R13 disposition:** The design now defines a stable producer/manifest-ordered sequence per source partition, a per-delivery durable completion record, and a cursor representing only the highest contiguous terminal sequence. Out-of-order completions are persisted but cannot move the frontier over a hole. Intentional empty positions require an explicit durable tombstone. If no stable ordered sequence/manifest ordinal exists, the design requires per-locator completion state plus safe rescan/enumeration and prohibits a last-seen-locator cursor. The cross-domain case matrix now explicitly tests sequence 102 completing before 101 and restart safety.

### P2-4 — Missing same-locator changed-content integrity test

**Finding:** R12 did not explicitly test changed bytes/digest under the same stable delivery locator.

**R13 disposition:** Cross-domain case #9 now asserts that a retry with the same locator and changed bytes/digest is an integrity conflict, not a new delivery. Existing same-locator lost-ack replay behavior remains covered.

## Exact Revision 13 review target

- Path: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_REVISION_13_2026-11-23.md`
- Source commit: `0476b76a96f5a1f9a1a5afd3b6843a15194f2f06`
- Exact design blob: `2c3e81c52ca10083e0d1c78ca3ef31858a47520d`
- Branch: `review/t0-phase-b-r13-codex-findings-20261123`
- Review state: NOT YET REVIEWED. A new review-only PR must target this exact source SHA/blob.

## Gates and restrictions

- The 101 isolated synthetic cases remain owner-approved (SD-05 14, SD-06 31, SD-07 46, cross-domain 10), but creation/execution remains sequenced after satisfactory independent review of exact R13 SHA/blob.
- No fixtures/tests were created or run as part of this R13 documentation update.
- No production DTO/parser/validator/persistence implementation, DDL/database mutation, data movement, T0/T1 runtime, T2 integration, VPS/autostart, deployment or trading is authorized.
- Contract Freeze remains NOT APPROVED.
