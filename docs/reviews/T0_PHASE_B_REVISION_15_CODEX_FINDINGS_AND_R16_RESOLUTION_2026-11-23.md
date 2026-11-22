# Revision 15 Codex Findings and Revision 16 Resolution — 2026-11-23

## Exact review target and provenance

- Repository: `kenznguyen/btcquant-application`
- Review-only PR: #13 — Revision 15
- Exact reviewed PR head: `6554529d9d8bd136c85643fdc43a68256b7e1989`
- R15 design source commit/blob: `5bbbd6ac253b4f8c8d9aeccb28d77170b1897919` / `2b1cb4a8d0a7d40f9ebfb29ccaf9d9d14930cfc0`
- Codex review ID: `PRR_kwDOVzv83s8AAAABZnV1sw`
- R15 review result: COMPLETED WITH THREE P2 FINDINGS.
- R16 design source commit/blob: `12f2e1db923c264660ab93b6139cb512d96a78a8` / `c2be5412668b0945c5f6f51e1aeaf787383a6676`
- R16 design path: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_REVISION_16_2026-11-23.md`
- R16 is a new immutable successor; R15 was not modified.

## Finding-by-finding resolution

### P2-1 — Stale current-status gate referenced R12

**Finding:** R15's current-status header still sequenced fixture creation/execution after review of R12, contradicting its exact-R15 gates.

**R16 resolution:** The current-status header, main synthetic-matrix gate, checklist, §14.3, Annex A §10 and the current synthetic-matrix status now require satisfactory independent review of exact R16 SHA/blob. Historical R12–R15 references remain only in historical snapshots. The current authority is explicit in the R16 header and §14.3.

### P2-2 — No explicit test for mismatch of the two source-object SHA aliases

**Finding:** The contract required `source_object.sha256 == raw_object_sha256`, but no existing matrix case explicitly tested inequality and rejection ordering.

**R16 resolution:** The existing SD-07 case 10 now explicitly tests `source_object.sha256 != raw_object_sha256` for the same claimed immutable source object. It asserts evidence preservation and rejection/quarantine before native identity resolution, no `SourceDeliveryCompletionV1`, no source cursor/book watermark advancement and no ACK. The approved matrix remains exactly 101 cases; no new case was added.

### P2-3 — Filesystem publication could overwrite immutable evidence

**Finding:** A temp-file plus ordinary atomic rename could replace an existing destination and destroy prior evidence under retries or concurrent publication.

**R16 resolution:** Filesystem publication now requires exclusive temp creation, full write, flush/fsync, exact byte-count and SHA-256 verification, then an atomic no-clobber/create-if-absent publication primitive. Regular rename with replace semantics is prohibited; no overwrite fallback is permitted. Existing targets are read and verified: identical bytes are reused; differing bytes are preserved under a separate collision-safe immutable evidence key before appending conflict evidence. Concurrent publishers use no-clobber semantics, not last-writer-wins. Object storage requires conditional create-if-absent/immutable-version semantics. If no-clobber publication, durability or preservation cannot be proven, fail closed without completion, cursor/checkpoint advancement or ACK.

## Autonomous remediation and review authorization

The owner authorized an iterative remediation/review loop: correct findings only in new immutable successor revisions; perform static self-review; request Codex review on each exact final PR head; repeat while P1/P2 findings remain. Once the exact design passes the review gate, proceed only with the already-approved isolated 101 synthetic cases. This is not authorization for production implementation or runtime changes.

## Static self-review

- Current-status header and operative fixture gates reference R16: **PASS**.
- Historical R12–R15 references are preserved as historical context only: **PASS**.
- SD-07 case 10 explicitly asserts SHA-alias mismatch and fail-before-identity/completion/ACK: **PASS**.
- Matrix count remains 101 (14/31/46/10): **PASS**.
- No-clobber publication, existing-target digest verification, distinct immutable evidence key, concurrent race handling and fail-closed behavior are specified: **PASS**.
- R15 immutability: **PASS** (R16 is a new file; R15 source remains unchanged).
- Self-review additionally removed a stale self-referential source-identity placeholder; exact R16 SHA/blob are maintained in companion metadata instead of embedded in the file itself.
- These are documentation/static consistency checks only; no runtime tests, filesystem fault-injection tests or formal proofs were run.

## Current status

- R16 documentation corrections: **PASS — static self-review only**.
- Exact R16 source SHA/blob: **VERIFIED**.
- Independent Codex review of exact R16 source: **BLOCKED — Codex review quota exhausted before a review verdict was produced**. A retry was posted; no findings/verdict were returned for R16.
- Workflow runs/jobs/artifacts: **NONE VERIFIED**.
- 101 synthetic fixtures/tests: **NOT CREATED / NOT RUN** pending satisfactory exact-R16 review.
- Formal proofs: **NOT RUN**.
- Contract Freeze: **NOT APPROVED**.

## Restrictions retained

No production DTO/parser/validator/persistence implementation, DDL/database mutation, data movement, T0/T1 runtime, T2 integration, VPS/autostart, deployment, exchange connectivity, automatic execution, live trading or real orders. The 101-case test scope remains synthetic and isolated.
