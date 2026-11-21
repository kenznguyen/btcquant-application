# T0 S3/S4 Provenance Validator S1 Coverage — Work Evidence

Date: 2026-11-22  
Repository: kenznguyen/btcquant-application  
Branch: main

## Scope approved

Owner approved S3 contract amendment and S4 synthetic-only RED test additions. Explicitly excluded: GREEN implementation, V1 source changes, DDL/SQLite, importer, archive retrieval, workflow creation/dispatch, Canonical T0, MAY-10, REST tail, T1/T2, VPS/runtime, deployment, cleanup and trading.

## Deliverables

1. Design amendment: docs/design/T0_PROVENANCE_VALIDATOR_S1_COVERAGE_AMENDMENT_2026-11-22.md
   - Initial commit: a9e291bcf97e63558452cd895f148eaec8229263
   - Follow-up consistency correction: 232fa7a474a7b2185dc87878cd5e40ad667abfea
   - Final blob after GitHub readback: 43719373949c0c2d553b463ab5ac66aadd64da2b
2. Synthetic RED tests: market_data/test_archive_provenance_validator_s1_red.py
   - Initial commit: 9a0f5016d29ffedb43b08fc15046343c597d17d9
   - Follow-up commit: caa4162d2f1940523c11c2d86bb61ea4667588bb
   - Final blob after GitHub readback: 4a35c34ad6dc3341db03fffe9d804443db033972
3. Existing V1 implementation and its original 12 RED / 12 GREEN tests were not modified.

## Contract coverage added

The amendment defines an S1 evidence envelope and eleven additional stable error codes for:
- exact raw inventory byte authentication and parsed-vs-supplied object set;
- measured object integrity and append-only attempt history;
- ZIP/sidecar assertion, CRC, structure and pair relationships;
- candidate CSV member metadata and verified cardinality;
- source row completeness, ordinals, raw fields and raw digest;
- recomputed normalized candle value digest and OHLCV semantics;
- complete candle/source-row/link graph;
- global run/schema/coverage acceptance.

The synthetic RED file contains targeted cases for these categories, including aggregate error ordering. It imports the existing V1 validator so that the tests are executable specifications intended to fail until a separately approved GREEN increment.

## Verification and evidence limits

- Both final files were fetched back from GitHub main; blob SHAs above are confirmed.
- Test execution: NOT RUN in this increment. No repository checkout/runtime execution facility was used; therefore no RED count, failure trace or Python syntax/runtime result is claimed.
- GitHub Actions workflow run/job/artifact: NONE.
- Full repository regression: NOT RUN.
- S4 test quality limitation: the test fixture reuses the existing V1 synthetic fixture and adds the S1 envelope. It is a targeted negative-test scaffold, not yet a complete independently valid S1 fixture with all 404 object measurements, 404 attempt histories, pair/member/source-row graph and recomputed S1 identifiers. A complete positive S1 fixture and per-invariant isolated fixtures remain NOT VERIFIED and must be completed before treating S4 coverage as complete.
- No source archive, sidecar, external network, SQLite, database, importer, Canonical T0 or runtime was accessed.

## Status

| Work item | Status |
|---|---|
| S3 contract amendment | PASS — committed and read back; design only |
| S4 RED test source | PARTIAL — committed and read back; execution NOT RUN |
| Complete valid S1 synthetic fixture | NOT VERIFIED |
| Exact per-code RED execution | NOT VERIFIED |
| V1 compatibility regression | NOT RUN in this increment |
| GREEN implementation | NOT AUTHORIZED |
| DDL/SQLite/importer/archive/runtime | NOT AUTHORIZED |

## Next step

Complete and self-review a fully valid deterministic S1 synthetic fixture, ensure each of the eleven new codes has an isolated failing test, then execute the RED suite on an exact source snapshot. Only after that should a separate GREEN scope be proposed for owner approval.


## Execution update — isolated GitHub Actions run 44940259084

- Workflow: [T0 S4 isolated provenance RED and V1 regression](https://github.com/kenznguyen/btcquant-application/actions/runs/44940259084); run ID `44940259084`, run attempt `1`, job `136955679442`.
- Trigger: `workflow_dispatch`; branch `main`; workflow path `.github/workflows/t0-s4-provenance-red-isolated.yml`.
- Exact requested and checked-out source SHA: `6a35462fe4db37c8a09fde3c20260fe6ba84f31a` (match).
- Exact source blobs logged by the job:
  - S4 test: `74b9bf8480cfdbf7b539f1d415b31bcc0fe7ae39`.
  - V1 RED test: `abbaeab16f026757923c679330f124a3d99e0774`.
  - V1 GREEN test: `da854052564a34c49c1e2f40da1c80315da04182`.
  - V1 validator: `c2c05dd8e62ebb8d1dce835909e1185a1a67b597`.
- Runtime: CPython `3.13.18`; GitHub-hosted Ubuntu `26.04.1`.
- S4 command: `python -B -m unittest -v market_data.test_archive_provenance_validator_s1_red`; **13 tests, 1 PASS, 12 FAIL; exit code 1**. The deterministic 404-object synthetic fixture construction/structure test passed. The 12 negative/aggregate assertions failed against the current V1-only validator: several mutations were accepted (`result.valid == True`); the object-set mutation produced V1 codes `INVENTORY_OBJECT_SET_INCOMPLETE` and `OBJECT_NOT_IN_APPROVED_INVENTORY` rather than S3's `INVENTORY_OBJECT_SET_MISMATCH`; the link mutation produced `ACCEPTED_SOURCE_ROW_LINK_CARDINALITY_INVALID` rather than `CANDLE_PROVENANCE_LINK_INVALID`; aggregate selection returned no S3 codes. This reproduces the expected missing S1 coverage, but **does not yet prove isolated per-code routing or aggregate ordering for the eleven S3 codes**.
- V1 command: `python -B -m unittest -v market_data.test_archive_provenance_validator_red market_data.test_archive_provenance_validator_green`; **24/24 PASS; exit code 0**.
- Workflow conclusion is `success` because the workflow deliberately captures each test exit code and continues to write/upload evidence. It is not a claim that S4 passed.
- Artifact: `t0-s4-v1-verification-44940259084`; ID `14721570797`; 3,498 bytes; expires `2026-12-21T19:19:00Z`; GitHub-reported digest `sha256:3d27361db4f20b924329e85565f1ccb6d9797830bb4d867c25114d853433c75a`. Downloaded ZIP SHA-256 was independently recomputed and matched. Contents inspected: `provenance.txt`, both test logs, both exit-code files and `result-summary.txt`.
- S4 disposition: **RED REPRODUCED / PARTIAL TEST-SPECIFICATION EVIDENCE**. Fixture construction **PASS**; V1 regression **PASS**; per-code S3 diagnostic isolation and aggregate assertions **NOT VERIFIED / FAIL AGAINST CURRENT IMPLEMENTATION**. Do not treat workflow-level success as S4 PASS.
- Full repository regression: **NOT RUN**. No archive acquisition, archive/sidecar access, Canonical T0, SQLite/DDL, importer, T1/T2 runtime, VPS, deployment or trading was performed.
- GREEN implementation remains **NOT AUTHORIZED**. Next step: review/fix only the S4 test fixtures/assertion isolation if needed under the existing bounded test-source scope, rerun at a new exact SHA, then request separate owner approval before any S1 GREEN implementation.


## S4 test-source correction after run 44940259084 — workflow pending

- Scope: test-source-only correction, based on artifact/log review from run `44940259084`. No validator implementation, V1 tests, workflow YAML, schema, DDL, database, importer or runtime source changed.
- Final source commit on `main`: `4534904fccc74a57a3a09793dd63e24414ab2cb1`.
- Final test blob: `08d02470e87e317afe8023ed6d6f14db847f5597`.
- Fixture corrections:
  - Added a deterministic importer contract ID and synthetic 40-hex source SHA rather than leaving importer provenance absent.
  - Made object expected size/SHA agree with measured size/SHA and successful transfer evidence.
  - Constructed each synthetic CSV member from a deterministic UTF-8 header plus one row, LF-terminated; member size and SHA now describe those exact synthetic bytes.
  - Expanded fixture shape assertions for exact raw inventory parsing, coverage counts, object/attempt IDs and references, reciprocal pair relations, member digest/size, raw-row digest/identity, candle value digest, link identity and inclusive close time.
- Negative-case isolation:
  - raw inventory: invalid UTF-8 with a matching byte digest, isolating strict decoding;
  - object set: supplied inventory object list differs from the unchanged authenticated raw inventory; expected legacy V1 diagnostics are explicitly retained alongside the new S3 code;
  - object measurement: unsuccessful HTTP 302 while measured bytes and successful attempt remain aligned;
  - attempt history: sole attempt starts at ordinal 2, with attempt ID and successful-attempt pointer recomputed, isolating sequence continuity;
  - pair: CRC evidence alone is false;
  - member: parser source SHA alone is malformed;
  - source row: physical/data ordinal offset is invalid while source-row ID and link references are recomputed;
  - candle digest: forged value ID is propagated consistently to row and link, isolating tuple recomputation;
  - OHLCV: invalid high/low values with candle digest and row/link value references recomputed;
  - link: unsupported duplicate disposition with matching recomputed link ID;
  - run: schema contract ID alone is wrong.
- Aggregate test uses disjoint records for object measurement, attempt, pair, member, row, candle digest, OHLCV and link mutations. It asserts all eleven S3 codes in catalogue order, no duplicates, and the two expected legacy V1 inventory diagnostics. Individual tests allow only the documented global run-acceptance companion code.
- Source review: same-session self-review only; no independent second-person review. No Python test execution has yet been performed against this new source SHA.
- Workflow run/job/artifact for SHA `4534904fccc74a57a3a09793dd63e24414ab2cb1`: **PENDING / NOT RUN**. The previous run `44940259084` is historical evidence for SHA `6a35462fe4db37c8a09fde3c20260fe6ba84f31a` and does not verify this correction.
- Status: S4 source correction **COMMITTED**; source syntax/runtime and all corrected assertions **NOT VERIFIED**; V1 regression on new SHA **NOT RUN**; GREEN **NOT AUTHORIZED**.
- Next: manually dispatch the existing isolated workflow with `source_sha=4534904fccc74a57a3a09793dd63e24414ab2cb1`, then inspect the exact run, both test logs, exit codes and artifact before updating status.


## S4 corrected-source workflow execution — run 44941050940

- Workflow: [T0 S4 isolated provenance RED and V1 regression](https://github.com/kenznguyen/btcquant-application/actions/runs/44941050940); run ID `44941050940`; attempt `1`; job `136958108791`; workflow `.github/workflows/t0-s4-provenance-red-isolated.yml`.
- Workflow metadata HEAD SHA is `4cdb2a6bd1526e774e94703a63a54388dd5b829e` (the handoff commit that existed when dispatched). Crucially, the workflow input `source_sha`, checkout ref, `git rev-parse HEAD`, and artifact summary all confirm the exact tested source SHA `4534904fccc74a57a3a09793dd63e24414ab2cb1`; no source mismatch.
- Runtime: CPython `3.13.18`, GitHub-hosted Ubuntu `26.04.1`. Source blobs: S4 test `08d02470e87e317afe8023ed6d6f14db847f5597`; V1 RED `abbaeab16f026757923c679330f124a3d99e0774`; V1 GREEN `da854052564a34c49c1e2f40da1c80315da04182`; validator `c2c05dd8e62ebb8d1dce835909e1185a1a67b597`.
- S4 command `python -B -m unittest -v market_data.test_archive_provenance_validator_s1_red`: **13 tests; 1 PASS; 12 FAIL; exit code 1**. The complete deterministic synthetic fixture structural test passed. Ten isolated negative cases reached the validator but returned `valid=True` because the current validator still implements V1 only. The inventory-set test returned only the two legacy V1 diagnostics (`INVENTORY_OBJECT_SET_INCOMPLETE`, `OBJECT_NOT_IN_APPROVED_INVENTORY`), not the appended S3 code. The aggregate test returned no S3 code tuple. This is the expected RED against the not-yet-implemented S3 invariants; it is not S4 PASS and does not establish that the validator emits the eleven S3 diagnostics.
- V1 focused regression: `python -B -m unittest -v market_data.test_archive_provenance_validator_red market_data.test_archive_provenance_validator_green`: **24/24 PASS; exit code 0**.
- Workflow conclusion: `success` means the harness completed, captured both test exit codes and uploaded the artifact; it does not mean the S4 RED suite passed.
- Artifact: `t0-s4-v1-verification-44941050940`; ID `14721587275`; 3,594 bytes; expires `2026-12-21T19:27:53Z`; GitHub digest `sha256:4ae10f8f63a6ed03e5e1cb738bdacfcf92e4203f1d5f73f831e71c4a3ee14d05`. Artifact downloaded and all six files inspected: provenance, result summary, S4 log/exit code, V1 log/exit code.
- Scope remained isolated: no archive acquisition, Canonical T0 access, database/DDL writes, importer, T1/T2 runtime, VPS, deployment or trading.
- Disposition: exact-SHA execution **PASS**; corrected fixture structure **PASS**; S4 RED assertions **12 expected failures against V1-only implementation**; V1 regression **PASS 24/24**; S1 GREEN **NOT AUTHORIZED**. S3 behavior remains unimplemented/unverified. Next step is review the 12 RED assertions as executable specifications and, only with separate owner approval, propose a bounded S3 GREEN implementation. Do not change validator or runtime under this test-only authorization.


## Final S4 RED review and proposed S3 GREEN approval scope

- Review document: `docs/reviews/T0_PROVENANCE_VALIDATOR_S3_GREEN_SCOPE_REVIEW_2026-11-22.md`; commit `d1bc77871bf678a6540d0f260a367f2e08f3182f`.
- Review is read-only against S4 test blob `08d02470e87e317afe8023ed6d6f14db847f5597`, V1 validator blob `c2c05dd8e62ebb8d1dce835909e1185a1a67b597`, S3 contract blob `43719373949c0c2d553b463ab5ac66aadd64da2b`, V1 interface blob `632eb6d38461ea3c65638ca073abc5fe4ae98729`, and exact tested source SHA `4534904fccc74a57a3a09793dd63e24414ab2cb1`.
- Review disposition: **SELF-REVIEW COMPLETE — REQUIRED SPECIFICATION GAPS IDENTIFIED**. Eleven individual RED cases and one aggregate case were cross-walked to the eleven S3 codes. Ten individual mutations and the aggregate are useful scaffolding, but coverage is not complete against S3 §7.
- Required findings: (R1) no positive assertion calls the validator on the valid S1 fixture; (R2) OHLCV mutation leaves source raw fields/digest/member provenance stale and is not demonstrably isolated; (R3) V1/S1 dispatch for missing/unknown/partial contract_version needs a frozen fail-closed rule; (R4) expected object size/SHA source is unclear because synthetic raw inventory does not carry those values; (R5) compact raw-fields representation is not concretely specified; (R6) coverage manifest shape and duplicate disposition vocabulary need executable definitions.
- Missing boundary cases are enumerated per error family in the review document. Existing V1 tests must remain unchanged. S3 GREEN must prove a valid S1 fixture passes, all eleven S3 codes individually, aggregate order/dedup, V1 compatibility, determinism and no mutation.
- Proposed bounded approval package: clarify S3 contract R3–R6; complete S4 test specification including R1/R2 and S3 §7 boundaries; implement pure validator S3 extension; run focused/V1/market_data tests and the existing isolated exact-SHA workflow; record artifact/evidence. No DDL/SQLite, archive/sidecar, importer, Canonical T0, MAY-10/REST tail, T1/T2 runtime, VPS/deployment, cleanup/retention or trading.
- No source, validator, RED/ GREEN test, workflow, schema, database, archive, importer or runtime files were changed during this review. Only review/evidence/handoff documentation was added.
- Approval status: **S3 GREEN NOT AUTHORIZED — AWAITING OWNER DECISION**.
