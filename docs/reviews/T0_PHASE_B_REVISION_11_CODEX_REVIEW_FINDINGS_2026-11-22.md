# T0 Phase B Revision 11 — Codex Review Findings and Revision 12 Corrections

- Review date: 2026-11-22
- Repository: `kenznguyen/btcquant-application`
- Review PR: [#9](https://github.com/kenznguyen/btcquant-application/pull/9)
- Reviewed PR head: `8a084c3f02de6d4f462b0f5731ed8f8569fb5fbf`
- Exact Revision 11 target commit/blob: `0ac119c7cd31ba63d5aead6796c7b5560abf2a18` / `9d9639b4d26b42a90929f50a32b801e359b23197`
- Codex review submission: `PRR_kwDOVzv83s8AAAABZmpveA`; summary comment ID `7081855192`.
- Review state: **COMPLETED WITH FINDINGS**. Three P2 findings; not a clean approval.
- Graphify: AI code review skipped because the PR changed documentation only. Its static/advisory check reported PASS but explicitly did not run tests or formal proofs. This is not an independent design verdict.
- Workflow evidence for reviewed head: no PR-triggered workflow runs returned by the repository workflow-run lookup. Tests, proofs and fixtures: **NOT RUN / NOT CREATED**.

## Findings and disposition

### R11-CODEX-01 — P2: Reconcile stale aggTrade mapping status

- Inline review comment: `PRRC_kwDOVzv83s66lkRR`, file line 97.
- Finding: a blanket statement marked all T1 CSV/native field mappings unverified, contradicting the read-only T1 source audit and the later Annex A mapping. It obscured which fields could be semantically mapped.
- Evidence: T1 source commit `c91a8c22d3b6236c98ab9a4d4d69b25d47f7f738`; source blobs `src/models.rs` `993419725268d1308645e3a37c15e9779a9e92cc`, `src/websocket/message_handler.rs` `7d7f221fbf4b31470049baea55584645352f61b7`, `src/utils/csv_writer.rs` `2c4538dcef7dfa758a854292031239c15f7c282b`.
- Correction in Revision 12: field-by-field source mapping matrix distinguishes verified semantic mappings (`a/p/q/f/l/T/m`) from absent `nq/M/E`, lossy f64/12-decimal price/quantity formatting, and unverified deployed/imported build provenance. `B-01` remains PARTIAL and `B-17` remains OPEN.

### R11-CODEX-02 — P2: Require snapshot identity to match envelope provenance

- Inline review comment: `PRRC_kwDOVzv83s66lkRV`, file line 812.
- Finding: `SnapshotCaptureV1.identity` required a producer/sequence pair while the shared envelope independently allowed those fields to be null or conflicting.
- Correction in Revision 12: `SnapshotCaptureV1` explicitly carries `CanonicalSourceEnvelopeV1`; for SD-07, both envelope provenance fields are required, non-null and exactly equal to the identity pair. Null, one-sided or mismatched pairs must be quarantined. The envelope pair is a provenance binding, not a second identity.

### R11-CODEX-03 — P2: Key delivery integrity checks by stable object identity

- Inline review comment: `PRRC_kwDOVzv83s66lkRY`, file line 893.
- Finding: using `raw_object_sha256` inside the delivery locator means changed bytes create a different locator and bypass the same-locator digest-conflict check.
- Correction in Revision 12: delivery identity uses stable `(source_producer_id, source_object_id, source_object_version)` plus a row/group locator. Raw object/record SHA-256 is an immutable integrity attribute checked against that stable identity, not part of the key. A verifiable immutable storage-version identity may substitute. If no stable object/version identity exists, quarantine; do not fall back to content SHA as identity.

## Revision 12 correction target

- File: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_REVISION_12_2026-11-22.md`
- Revision 12 is a documentation-only successor. Revision 11 remains immutable.
- The exact Revision 12 commit/blob is recorded in the current project handoff and the review-only follow-up PR.
- Disposition: all three findings are addressed in the candidate text, but **NOT YET RE-REVIEWED**. Do not mark the findings closed until a reviewer confirms the exact Revision 12 SHA/blob.
- PR #9 remains a completed historical review record and must not be merged. A follow-up review request should target Revision 12.

## Authorization and next gate

- Owner-approved 101-case matrix remains 14/31/46/10.
- Fixture creation and execution remain sequenced after independent review of exact Revision 12 SHA/blob.
- No production implementation, DDL/database mutation, T0/T1 runtime, T2 integration, deployment or trading is authorized.
- Contract Freeze remains **NOT APPROVED**.
