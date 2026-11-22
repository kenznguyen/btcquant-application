# PROJECT SESSION HANDOFF ADDENDUM — 2026-11-22

Repository: kenznguyen/btcquant-application
Branch: main
Related S1 design commit: ee30e4bcb1e1118901e372f642f368e4f4578649

## T0 archive staging/importer S1

- Owner approved S1 only: freeze design-level provenance contracts and staging schema.
- S1 baseline: `docs/design/T0_ARCHIVE_STAGING_S1_PROVENANCE_SCHEMA_FREEZE_2026-11-22.md`.
- Original S1 design commit: `319d3db16da69c59b2efb9e9a0b4a7f5f7afe8e9`.
- Owner approved a documentation-only amendment to resolve three review findings: preserving failed/incomplete evidence, adding append-only acquisition-attempt history, and aligning nullable evidence fields with quarantine states.
- Amended S1 design commit: `ee30e4bcb1e1118901e372f642f368e4f4578649`.
- Amendment freezes `AcquisitionAttemptEvidence`, stable attempt IDs, explicit attempt outcomes (including UNKNOWN), partial-body versus complete-object digest semantics, conditional VERIFIED/QUARANTINED constraints, and pair/member failure evidence retention.
- The original DDL is a design baseline only. The amendment specifies exact changes required before any future executable DDL; no DDL was implemented or tested.
- S1 status: **DESIGN BASELINE AMENDED AND COMMITTED; DOCUMENTATION ONLY**.
- Importer, acquisition workflow, archive requests, staging SQLite, Canonical T0, MAY-10, REST tail, T1/T2, VPS/runtime, deployment and trading remain excluded/not authorized.
- Remaining open gates: exact pinned SQLite runtime/STRICT support; complete cross-table validator test design; compression/uncompressed-size/disk-reserve limits; artifact/source retention; real header-mode verification across all 202 archives.
- Main `docs/PROJECT_SESSION_HANDOFF.md` was not rewritten because it is a large append-oriented history file; this addendum remains the latest handoff record.

## Evidence and verification

- Scope: documentation-only S1 amendment.
- Design review findings addressed: (1) success-only CHECK constraints had prevented retention of failed evidence; (2) acquisition retries lacked a frozen append-only attempt contract; (3) measured object fields were NOT NULL despite incomplete/quarantined evidence states.
- Verification: content-level consistency review only; no code tests, SQL execution, SQLite creation, archive access, workflow run or artifact.
- Workflow run/job/artifact: **NONE**.
- S1 amendment source commit: `ee30e4bcb1e1118901e372f642f368e4f4578649`.
- Status: **COMMITTED — DESIGN ONLY**; implementation/test status **NOT RUN / NOT AUTHORIZED**.

## T0 archive staging/importer S2 — synthetic provenance validator RED

- Owner approved S2 limited to synthetic-only Provenance Validator RED tests; this approval does not authorize GREEN implementation.
- Added `market_data/test_archive_provenance_validator_red.py`, 12 unittest methods; final blob SHA `abbaeab16f026757923c679330f124a3d99e0774`.
- Test contract covers T0ENC1 framing, deterministic acquisition attempt IDs, inventory/object allowlist, QUARANTINED evidence, UNKNOWN/partial transfer evidence, pair/member cardinality, source-row/link cardinality, conflicting candle values and BAR_CLOSE_BOUNDARY semantics.
- Expected future module/API is documented in the test file: `market_data.archive_provenance_validator` with `encode_t0enc1`, `derive_attempt_id`, and `validate_provenance`.
- Test commit history: initial `a27d303e981da94f3c379672fb2c2c452cd08d99`; assertion correction `69a97d0c4dce7e85a00a1f49b5e0f25eb28bcc20`.
- Evidence record initially committed at `97455de1fd1d849b84aa7961d03436eee89a472b`; updated exact-source execution evidence commit: `b657c21d4f84cddce9c5ebff816267299e049f38`.
- User-provided ZIP has no `.git` metadata. Four file blobs were checked against the exact target commit and matched; whole-tree commit identity is not independently provable from this ZIP alone.
- Exact command: `python -B -m unittest -v market_data.test_archive_provenance_validator_red`.
- Local isolated execution on CPython 3.13: **12 tests run; 12 errors; exit code 1**. Every error is `ModuleNotFoundError` for the intentionally absent `market_data.archive_provenance_validator` raised in `setUp()`; no business assertion ran. The missing-module RED state is runtime-proven; the 12 invariants are **NOT VERIFIED**.
- GitHub Actions run/job/artifact: **NONE**. Full repository regression: **NOT RUN**.
- Bounded interface review found S1 does not independently freeze the validator result DTO (`valid`, `error_codes`), complete validator-level error-code catalogue, or deterministic error ordering/aggregation. Individual codes embedded in tests do not constitute a reviewed complete interface contract.
- S2 disposition: **PARTIAL — expected RED reproduced; validator assertions NOT VERIFIED; GREEN BLOCKED pending API/error-code contract freeze**.
- No production code, DDL, SQLite, importer, archive retrieval, workflow, Canonical T0/MAY-10/REST tail, VPS/runtime, T1/T2, deployment, cleanup or trading operation occurred.

## Handoff correction

This section supersedes the earlier S2 statements in this addendum that said RED execution was NOT RUN. The test execution described above occurred after the exact-source ZIP was supplied. The older wording is retained only as historical state before execution.

## T0 Provenance Validator Interface V1 — documentation-only freeze

- Owner approved only the design and freeze of the Python-facing validator interface; no implementation or test modification was authorized.
- Source reviewed directly from `main`: S2 RED test blob `abbaeab16f026757923c679330f124a3d99e0774`; amended S1 design blob `af7c90af0f0bcfa8d0b2143578222619af620197`; S2 execution evidence blob `5a66bdf605d882a0ad8716d89f6b00ea533ce0d5`.
- Added `docs/design/T0_PROVENANCE_VALIDATOR_INTERFACE_V1_2026-11-22.md`.
- Interface contract commit: `e4af4c346c1d1b4090b5097901d369ab18070142`.
- Contract freezes module `market_data.archive_provenance_validator`; functions `encode_t0enc1`, `derive_attempt_id`, `validate_provenance`; immutable `ProvenanceValidationResult(valid: bool, error_codes: tuple[str, ...])`; input shape; side-effect boundary; S1 framing/attempt-ID behavior; 10 stable V1 error codes; deduplicated error aggregation and catalogue-defined deterministic ordering.
- The nine codes currently asserted in the RED test are retained exactly. One additional `PROVENANCE_INPUT_SHAPE_INVALID` code is defined for deterministic malformed top-level payload handling.
- Explicit limitation: this catalogue covers the current S2 V1 interface surface and is not a claim that all S1 invariants have dedicated codes or are tested. Additional invariants and test coverage remain NOT VERIFIED and require separate review/amendment.
- Verification: source-level design consistency review only. No executable tests, code, workflows, SQL, SQLite, archive or runtime operations.
- Workflow run/job/artifact: **NONE**.
- Status: **PASS — DOCUMENTATION CONTRACT COMMITTED; IMPLEMENTATION NOT AUTHORIZED**.
- Next: owner review of the committed contract. Any GREEN implementation, RED test edits/additions, DDL, SQLite, importer, archive retrieval or workflow requires separate explicit approval.
- All exclusions remain: Canonical T0, MAY-10, REST tail, VPS/runtime, T1/T2, deployment, cleanup/deletion and trading.

## T0 Provenance Validator Interface V1 — self-review

- Owner requested a read-only self-review of the frozen Interface V1 and a code-by-code crosswalk against the 12 S2 RED test methods before proposing GREEN scope.
- Review record: `docs/evidence/T0_PROVENANCE_VALIDATOR_INTERFACE_V1_SELF_REVIEW_2026-11-22.md`.
- Sources re-read from `main`: Interface blob `632eb6d38461ea3c65638ca073abc5fe4ae98729`; RED test blob `abbaeab16f026757923c679330f124a3d99e0774`; S1 amended design blob `af7c90af0f0bcfa8d0b2143578222619af620197`; S2 execution evidence blob `5a66bdf605d882a0ad8716d89f6b00ea533ce0d5`.
- Crosswalk: nine of ten catalogue codes have a direct RED assertion; `PROVENANCE_INPUT_SHAPE_INVALID` is additional and currently untested. Three other tests cover T0ENC1 and attempt-ID behavior.
- Review: no blocking contradiction found between the frozen interface and RED source. Coverage limitations include no executed business assertions (12 errors in `setUp()`), incomplete synthetic inventory fixtures, no tests for aggregation/order, malformed input, broader encoder/attempt-ID boundaries, normalized candle tuple digest consistency, DTO immutability/purity, or the full S1 acceptance matrix.
- Proposed next GREEN scope is bounded to one pure Python module implementing the frozen DTO and three functions, plus synthetic tests for uncovered interface contracts. Existing RED tests remain unchanged unless separately approved.
- Out of scope remains DDL, SQLite, importer, archives, workflows, Canonical T0, MAY-10, REST tail, VPS/runtime, T1/T2, deployment, cleanup/deletion and trading.
- Status: **INTERFACE REVIEW PASS WITH COVERAGE LIMITATIONS; RED ASSERTIONS NOT VERIFIED; GREEN NOT AUTHORIZED**.
- Workflow run/job/artifact: **NONE**. No executable code or runtime/data operation changed.
- Next gate: owner approval or rejection of the proposed bounded GREEN scope. No implementation begins before explicit approval.

## T0 Provenance Validator Interface V1 — GREEN implementation

- Owner approved the bounded GREEN scope: pure Python validator module plus synthetic-only coverage; preserve original 12 RED tests; no DDL, SQLite staging, importer, archive acquisition, workflow or runtime implementation.
- Implementation: `market_data/archive_provenance_validator.py`, final blob `c2c05dd8e62ebb8d1dce835909e1185a1a67b597`.
- New synthetic tests: `market_data/test_archive_provenance_validator_green.py`, final blob `da854052564a34c49c1e2f40da1c80315da04182`.
- Implementation/test commit (code and tests finalized): `70f76ef48db9373c42c8436cbb4d490ef51a90ea`.
- Original RED tests unchanged: `market_data/test_archive_provenance_validator_red.py`, blob `abbaeab16f026757923c679330f124a3d99e0774`.
- Final evidence record is `docs/evidence/T0_PROVENANCE_VALIDATOR_V1_GREEN_2026-11-22.md`.
- Candle identity representation cross-check commit: `4b71c2b295d3e5f56e5712ace4b0d60e4e47242d`; final test commit: `70f76ef48db9373c42c8436cbb4d490ef51a90ea`.
- Focused command `python -B -m unittest -v market_data.test_archive_provenance_validator_green market_data.test_archive_provenance_validator_red`: **24/24 PASS** (12 new GREEN + 12 original RED).
- Market-data suite `python -B -m unittest discover -s market_data -p 'test*.py'`: **357/357 PASS** on the supplied source ZIP snapshot.
- Full suite `python -B -m unittest discover`: **579 tests; 1 failure; 6 errors** on the supplied ZIP snapshot. All observed failures/errors are in `paper_execution/`; details are in the evidence record. They include a SyntaxError in `paper_execution/test_dual_strategy_api_red.py`, mappingproxy mutation errors, DATASET_VERSION provenance errors and RISK_CONTROL_STATE_UNAVAILABLE.
- Source identity limitation: user-provided ZIP has no Git metadata; four earlier blobs were matched and the final three relevant implementation/test blobs were matched to GitHub readback, but the whole ZIP tree was not proven identical to final main HEAD. Focused 24-test execution is tied to exact relevant blobs; exact-main full repository regression remains **NOT VERIFIED**.
- V1 implementation covers the frozen ten-code catalogue and deterministic result/encoding/attempt-ID behavior. It does not authenticate raw inventory bytes against a pinned SHA, recompute candle value digests, or implement the full S1 cross-record/acceptance matrix. These remain **NOT VERIFIED** and are explicitly documented in the evidence record.
- GitHub Actions workflow run/job/artifact: **NONE**. No workflow was created because workflow implementation was outside the approved scope.
- Same-session self-review: **PASS WITH KNOWN S1 COVERAGE LIMITATIONS**; not an independent second-person review.
- Status: **PASS — FROZEN V1 INTERFACE IMPLEMENTED; 24 FOCUSED TESTS PASS; 357 MARKET_DATA TESTS PASS ON PROVIDED ZIP; FULL SUITE PARTIAL/BLOCKED; FULL S1 NOT VERIFIED**.
- Non-actions preserved: no archive/sidecar access, no Canonical T0/MAY-10/REST tail, no staging DB/DDL/importer, no runtime/VPS, T1/T2 integration, deployment, cleanup/deletion or trading.
- Next: review the recorded V1 limitations and decide separately whether to approve additional S1 coverage/error-code/interface work. No scope expansion is implied by this GREEN increment.


## T0 Provenance Validator S1 coverage — S3/S4

- Owner approved S3 contract amendment and S4 synthetic-only RED tests. Approval excludes GREEN implementation, V1 source changes, DDL/SQLite, importer, archive retrieval, workflow creation/dispatch, Canonical T0, MAY-10, REST tail, T1/T2, VPS/runtime, deployment, cleanup and trading.
- S3 contract: `docs/design/T0_PROVENANCE_VALIDATOR_S1_COVERAGE_AMENDMENT_2026-11-22.md`.
  - Initial commit: `a9e291bcf97e63558452cd895f148eaec8229263`.
  - Candle digest tuple consistency correction: `232fa7a474a7b2185dc87878cd5e40ad667abfea`.
  - Final blob: `43719373949c0c2d553b463ab5ac66aadd64da2b`.
- S4 test source: `market_data/test_archive_provenance_validator_s1_red.py`.
  - Initial commit: `9a0f5016d29ffedb43b08fc15046343c597d17d9`.
  - Follow-up fixture-gate correction: `caa4162d2f1940523c11c2d86bb61ea4667588bb`.
  - Final blob: `4a35c34ad6dc3341db03fffe9d804443db033972`.
- Evidence: `docs/evidence/T0_PROVENANCE_VALIDATOR_S1_COVERAGE_S3_S4_2026-11-22.md`, commit `92e3c4066ddea604798ba75f7c339639e60eb48a`.
- S3 defines eleven appended stable error codes for inventory raw-byte authentication, object measurements, attempt history, pair/member evidence, source-row provenance, candle digest/OHLCV, links and global run acceptance. V1 codes and public function names remain unchanged.
- S4 adds targeted synthetic negative cases and aggregate-order coverage. Existing V1 implementation and original RED/GREEN tests were not modified.
- GitHub readback confirms final S3 blob `43719373949c0c2d553b463ab5ac66aadd64da2b` and S4 blob `4a35c34ad6dc3341db03fffe9d804443db033972`.
- Test execution: **NOT RUN**; no RED count or runtime failure trace is claimed. Actions run/job/artifact: **NONE**. Full regression: **NOT RUN**.
- S4 quality limitation: current fixture extends the V1 fixture and is not yet a complete valid S1 fixture containing all 404 measured object records, attempt histories, full pair/member/row/candle/link graph and recomputed S1 identifiers. Positive full-envelope acceptance and isolated execution of every new error code remain **NOT VERIFIED**.
- Status: S3 **PASS — DESIGN COMMITTED/READ BACK**; S4 **PARTIAL — TEST SOURCE COMMITTED/READ BACK, EXECUTION NOT RUN**; GREEN **NOT AUTHORIZED**.
- Next: complete/self-review the full valid synthetic fixture and isolated negative cases, then execute tests on an exact source snapshot. Request separate GREEN approval only after RED evidence is reproducible.


## T0 S4 isolated RED + V1 regression — execution result

- Owner authorized one isolated GitHub Actions workflow for S4 RED + V1 regression. No S1 GREEN, validator changes, DDL/SQLite, importer, archive acquisition, Canonical T0 access, T1/T2 runtime, VPS, deployment or trading was authorized.
- Workflow run: [44940259084](https://github.com/kenznguyen/btcquant-application/actions/runs/44940259084); job `136955679442`; run attempt `1`; workflow `.github/workflows/t0-s4-provenance-red-isolated.yml`.
- Exact source SHA requested and checked out: `6a35462fe4db37c8a09fde3c20260fe6ba84f31a`.
- Exact blobs: S4 test `74b9bf8480cfdbf7b539f1d415b31bcc0fe7ae39`; V1 RED `abbaeab16f026757923c679330f124a3d99e0774`; V1 GREEN `da854052564a34c49c1e2f40da1c80315da04182`; validator `c2c05dd8e62ebb8d1dce835909e1185a1a67b597`.
- Runtime: CPython 3.13.18 on GitHub-hosted Ubuntu 26.04.1.
- S4: `python -B -m unittest -v market_data.test_archive_provenance_validator_s1_red` — 13 tests; 1 PASS (deterministic synthetic fixture structure); 12 FAIL; exit 1. Failures show current V1 validator does not enforce most S1 mutations. Two cases currently return different V1 error codes than the intended S3 codes; aggregate S3 code assertion returns empty. Thus RED is reproduced, but isolated routing/aggregate semantics for all eleven S3 codes are **NOT VERIFIED**.
- V1: `python -B -m unittest -v market_data.test_archive_provenance_validator_red market_data.test_archive_provenance_validator_green` — **24/24 PASS**, exit 0.
- Workflow-level conclusion `success` means the wrapper completed and uploaded evidence; it intentionally captures nonzero test exit codes and must not be read as S4 PASS.
- Artifact: `t0-s4-v1-verification-44940259084`, ID `14721570797`, 3,498 bytes, expiry 2026-12-21T19:19:00Z, SHA-256 `3d27361db4f20b924329e85565f1ccb6d9797830bb4d867c25114d853433c75a`. ZIP downloaded and SHA-256 independently matched.
- Updated evidence: `docs/evidence/T0_PROVENANCE_VALIDATOR_S1_COVERAGE_S3_S4_2026-11-22.md`, commit `0d477e6d2a3b9e521254e9265d46fca1a15fa4bf`, blob `e5c80fcd315898ba9abc582288696dbee6244776`.
- Status: S4 fixture construction **PASS**; S4 RED reproduction **PASS WITH COVERAGE/DIAGNOSTIC LIMITATIONS**; per-code isolated S3 diagnostics and aggregate order **NOT VERIFIED**; V1 regression **PASS 24/24**; full repository regression **NOT RUN**; S1 GREEN **NOT AUTHORIZED**.
- Next: inspect and, if required, correct only S4 test-source isolation/expected diagnostic assertions under the existing test-only approval; rerun exact-SHA workflow. Obtain separate owner approval before any S1 GREEN implementation. All prior exclusions remain.


## S4 RED test-source correction — new exact SHA awaits workflow

- Owner requested review/correction of S4 test source only, then rerun of the existing isolated workflow. No S1 GREEN or validator changes are authorized.
- Final test-source commit on `main`: `4534904fccc74a57a3a09793dd63e24414ab2cb1`; source blob `08d02470e87e317afe8023ed6d6f14db847f5597`.
- Corrections make the 202 synthetic CSV members internally consistent (LF-terminated header+row bytes, exact size/SHA), supply synthetic importer provenance, align object expected/measured evidence, and strengthen deterministic identity/reference/coverage assertions.
- Each negative test now changes one primary invariant while recomputing dependent IDs/references where needed. Aggregate defects use disjoint records; assertions require the intended S3 code, retain expected legacy V1 diagnostics and allow only the derived global run-acceptance companion.
- Validator, original V1 tests, workflow YAML and all runtime/data components are unchanged.
- New-SHA Python execution and V1 regression: **NOT RUN / NOT VERIFIED**. Previous workflow run 44940259084 is tied to old SHA `6a35462fe4db37c8a09fde3c20260fe6ba84f31a`.
- Status: test-source correction **COMMITTED**; test verification **PENDING**; S1 GREEN **NOT AUTHORIZED**.
- Next: dispatch `.github/workflows/t0-s4-provenance-red-isolated.yml` with `source_sha=4534904fccc74a57a3a09793dd63e24414ab2cb1`. Record new run/job/artifact and inspect complete logs before making any PASS/BLOCKED decision.


## S4 corrected-source workflow result — 2026-11-22

- Workflow run [44941050940](https://github.com/kenznguyen/btcquant-application/actions/runs/44941050940), job `136958108791`, attempt `1`, workflow `.github/workflows/t0-s4-provenance-red-isolated.yml`.
- Workflow metadata HEAD was `4cdb2a6bd1526e774e94703a63a54388dd5b829e`, but the explicitly requested SHA, checkout ref, actual checkout HEAD and artifact summary all match `4534904fccc74a57a3a09793dd63e24414ab2cb1`. S4 test blob `08d02470e87e317afe8023ed6d6f14db847f5597`; V1 test/validator blobs unchanged.
- CPython 3.13.18 / Ubuntu 26.04.1. S4: 13 tests, 1 fixture-structure PASS, 12 RED assertion failures, exit 1. Ten isolated mutations return valid under the V1-only validator; inventory-set case returns only legacy V1 codes; aggregate test emits no S3 codes. The tests therefore demonstrate missing S3 enforcement, not successful S3 diagnostic behavior. V1 regression: 24/24 PASS, exit 0.
- Workflow conclusion success is harness/upload success only. Artifact `t0-s4-v1-verification-44941050940`, ID `14721587275`, 3,594 bytes, SHA-256 `4ae10f8f63a6ed03e5e1cb738bdacfcf92e4203f1d5f73f831e71c4a3ee14d05`; downloaded and inspected.
- Evidence record updated in commit `c71cccaf476d66d9ab11ca75cfd85c4ee742cce2`, blob `400b8f6b0e6f194cd2b47d6f35c0f1bf9aa8ef09`.
- Status: exact-SHA workflow execution PASS; fixture structure PASS; S4 RED assertions expose unimplemented S3 invariants; V1 regression PASS 24/24; S3 GREEN NOT AUTHORIZED; archive/Canonical T0/DDL/SQLite/importer/T1/T2 runtime/VPS/deployment/trading remain untouched.
- Next: inspect the RED assertions as executable specifications and request separate explicit approval before any S3 GREEN implementation.


## Final S4 RED review / S3 GREEN scope proposal — 2026-11-22

- Review: `docs/reviews/T0_PROVENANCE_VALIDATOR_S3_GREEN_SCOPE_REVIEW_2026-11-22.md`, commit `d1bc77871bf678a6540d0f260a367f2e08f3182f`.
- Self-review cross-walked eleven targeted S3 tests plus aggregate. Exact baseline: S4 test blob `08d02470e87e317afe8023ed6d6f14db847f5597`; V1 validator blob `c2c05dd8e62ebb8d1dce835909e1185a1a67b597`; S3 contract blob `43719373949c0c2d553b463ab5ac66aadd64da2b`; V1 interface blob `632eb6d38461ea3c65638ca073abc5fe4ae98729`; tested source SHA `4534904fccc74a57a3a09793dd63e24414ab2cb1`.
- Required findings: valid S1 fixture is never passed through validator (R1); OHLCV mutation leaves source-row/member provenance stale and is not isolated (R2); V1/S1 discriminator and unknown/partial-version behavior need freeze (R3); authoritative expected object size/SHA source unclear (R4); raw-fields compact representation underspecified (R5); coverage-manifest shape and duplicate dispositions need concrete definitions (R6).
- Proposed separate S3 GREEN package: contract clarifications R3–R6; S4 test-specification completion including positive valid-fixture proof and corrected OHLCV isolation; pure validator extension with eleven appended codes; focused + V1 + market_data tests; existing isolated exact-SHA Actions evidence. Full details and exclusions are in the review document.
- This increment changed documentation only. No validator/test/workflow/schema/DDL/SQLite/importer/archive/Canonical T0/T1/T2/VPS/runtime/deployment/trading change or access.
- Status: **SELF-REVIEW COMPLETE; S3 GREEN NOT AUTHORIZED; AWAITING OWNER DECISION**.
- Evidence update commit: `d327bc130cba39bd5469f6062a4ebdcca3cb8f0c`, blob `6ebd49334a8c09db9facd23ff83f7dba22979915`.


## S3 GREEN approved, implemented and verified — 2026-11-22

### Owner decision

- Owner explicitly approved: **S3 GREEN = complete R3–R6 contract + finish S4 synthetic tests + pure validator + synthetic tests + isolated exact-SHA GitHub Actions evidence**.
- Approval is strictly bounded. It does not authorize DDL/SQLite/staging DB, archive or sidecar access/download/decompression, importer/acquisition, Canonical T0, MAY-10/REST tail, T1/T2 runtime/data integration, VPS/systemd/autostart/deployment/Postgres, retention/deletion, credentials or trading.

### Source and contract

- Contract clarification blob: `84f881ad3e81cf42f1ec674a5b36ae5547478e33`.
- R3: exact discriminator dispatch; no silent S1-to-V1 downgrade.
- R4: distinguish pre-transfer expected size/SHA assertions from measured object values and successful transfer evidence; no claim that the raw inventory pins these measurements.
- R5: exact canonical compact JSON representation for the twelve raw source fields.
- R6: exact coverage manifest keys, inclusive non-overlapping coverage ranges, approved gap/extra semantics based on exact candle natural-key set, duplicate disposition vocabulary and representative ordering.
- Tested source SHA: `10e99c68e7acbd8a25e192075dede214f3fccad5`.
- Validator blob: `b94bac0f82ae141984552409f99a5cff70435b3b`.
- S3 test blob: `328442917535d555d09b18f0213e1ddfd75a9416`.
- Workflow blob: `b73bf266c47dd6cdb440928e2107306f4906a5b6`.
- V1 RED/GREEN blobs unchanged: `abbaeab16f026757923c679330f124a3d99e0774` / `da854052564a34c49c1e2f40da1c80315da04182`.
- All source and evidence commits remain on `main`; no divergent branch created.

### Exact-SHA verification

- Workflow run [44976345735](https://github.com/kenznguyen/btcquant-application/actions/runs/44976345735), job `137067027769`, attempt `1`, conclusion `success`.
- Requested source SHA and checked-out HEAD match exactly: `10e99c68e7acbd8a25e192075dede214f3fccad5`.
- CPython 3.13.18 / Ubuntu 26.04.1. Pinned CI test dependencies: FastAPI 0.116.1 and httpx 0.28.1.
- S3 synthetic tests: **30/30 PASS**, exit 0.
- V1 RED/GREEN compatibility: **24/24 PASS**, exit 0.
- Full market_data suite: **387/387 PASS**, exit 0. Two SQLite ResourceWarnings were emitted in unrelated tests; no test failed.
- Artifact `t0-s3-green-verification-44976345735`, ID `14735512352`, 3,678 bytes, SHA-256 `5d12d74c405e8e9bd7bd6443b3f6fe4b85681eeba1b35df5dc78a7057f11e8bf`; downloaded, contents inspected, and local checksum matched GitHub metadata.
- An earlier coverage-range attempt at SHA `d3fd1cf4656243ae8d80160d6539cc3d0c890560` failed with `NameError` (`candle_records`); fixed in final tested source SHA above. Do not use that failed run as acceptance evidence.

### Status and next gate

- R3–R6 contract: **PASS / FROZEN**.
- S4 test completion: **PASS**.
- Pure S3 validator: **PASS**.
- S3 tests: **PASS 30/30**; V1 compatibility **PASS 24/24**; full market_data **PASS 387/387**.
- Exact-SHA workflow, job, artifact and checksum: **PASS**.
- Review: same-session **SELF-REVIEW** only; independent second-person review not claimed.
- Overall bounded S3 GREEN package: **PASS**.
- No full repository regression was run. No archive, database, Canonical T0, importer, runtime, VPS, deployment, retention or trading operation occurred.
- Next allowed step requires a separate owner decision. This PASS does not authorize archive acquisition, importer, DDL/SQLite, staging DB, promotion, T1/T2 integration or runtime/deployment.

### Evidence records

- Scope review updated: `docs/reviews/T0_PROVENANCE_VALIDATOR_S3_GREEN_SCOPE_REVIEW_2026-11-22.md`, commit `dd7b2621afd557a483ca14d75345d131e554fceb`, blob `a792b501abdd8e3d7902c4b9d6aa5f4df168dfdd`.
- Evidence updated: `docs/evidence/T0_PROVENANCE_VALIDATOR_S1_COVERAGE_S3_S4_2026-11-22.md`, commit `04badccd7ea57b42954b2b58ec62d7f49ebb7dee`, blob `5af1635225662435091d36165592414b6c87ba13`.


### Final main-head verification after contract status update

- Final exact-SHA workflow run [44976543815](https://github.com/kenznguyen/btcquant-application/actions/runs/44976543815), job `137067027769`, attempt `1`, tested current `main` SHA `d1651196af3059e00b22f65461dbd897e5c599df`.
- Contract blob at this final tested SHA: `da89266c7c4d1394c731b1c2304cdb73b077d4f6`; validator `b94bac0f82ae141984552409f99a5cff70435b3b`; S3 test `328442917535d555d09b18f0213e1ddfd75a9416`; workflow `b73bf266c47dd6cdb440928e2107306f4906a5b6`.
- S3 30/30, V1 24/24 and full market_data 387/387 all PASS; exit codes 0.
- Artifact ID `14735332978`, size 3,681 bytes, SHA-256 `a359d04c458a8545e386a288ef5ad6219d6f7bb9d31a6525778444eefeb40cf8`; downloaded and verified.
- This is the final exact-SHA run for implementation + approval-status documentation. Subsequent commits only update review/evidence/handoff documentation; no tested code, test, contract or workflow blobs changed.


## T0 post-S3 blocker audit — 2026-11-22

- Read-only audit document: `docs/reviews/T0_POST_S3_BLOCKER_AUDIT_2026-11-22.md`, commit `a66234d0ee10fbcd22f67f978a3ced73570cca22`.
- `docs/T0_ACTIVE_SCOPE_INDEX.md` refreshed with a current override, commit `2ac943c66fd82da249b8c3845b2f5a208870329a`, blob `c5057e8f34f041d0f322836fd7e57c204eb6f0b1`.
- S3 remains PASS at exact tested source SHA `d1651196af3059e00b22f65461dbd897e5c599df`: S3 30/30, V1 24/24, market_data 387/387. This does not authorize any subsequent archive, importer, SQLite or runtime phase.
- Main remaining staging blockers: (B1) reconcile original S1 DDL with failed/incomplete evidence amendment and S3 R4–R6; add full append-only acquisition-attempt and successful-attempt relationship; freeze persisted coverage manifest. (B2) pin SQLite STRICT minimum/runtime verification. (B3) real header/member-format coverage beyond the one M15 monthly 2022-08 sample. (B4) decompression/ratio/disk/concurrency/retry/timeout budgets. (B5) fresh archive-derived coverage/gap manifest. (B6) source/evidence retention and artifact TTL. (B7) new owner-controlled host/path because former VPS is deleted and old path is not active. (B8) separately approved importer and SQLite build. (B9) independent T0 application review PR #3/#4 remains a separate open gate.
- REST tail remains closed by owner decision; MAY-10 excluded; former Canonical SQLite remains LOST. Any output remains `RECONSTRUCTED — PARTIAL COVERAGE`.
- Recommended next bounded task: **S1.1 documentation-only schema reconciliation**. This requires explicit approval for that design-freeze work; it does not authorize executable DDL, SQLite, importer, archive access/acquisition, workflow dispatch, host preflight, data build, cleanup or promotion.
- Audit non-actions: no archive/sidecar access, REST call, SQLite/Canonical access, importer, DDL, runtime, VPS, deployment, retention change, deletion, credential or trading operation.


## T0 S1.1 — provenance/schema reconciliation (documentation-only)

- Owner explicitly approved: `S1.1 = hòa giải và đóng băng hợp đồng provenance/schema ở mức thiết kế; chỉ cập nhật tài liệu, chưa triển khai DDL hoặc thao tác dữ liệu.`
- Reconciliation document: `docs/design/T0_ARCHIVE_STAGING_S1_1_PROVENANCE_SCHEMA_RECONCILIATION_2026-11-22.md`.
- Initial commit: `255e505149d1739a18549baab6d81ba458f124d7`; follow-up clarification commit: `2971efa75a5f8f9f75277adba2ced72514797bab`; final document blob after clarification: `30093c2bce7f62b97612a2db863dcb17853b306d`.
- Original S1 document now carries an authority notice: its historical DDL is superseded where it conflicts with S1.1. Notice commit: `5ef5641da3d881c5c07a3704289c396834331a66`; original S1 blob after notice: `55a9d1fa3db7e8c754ca30fc1c63b12b27082263`.
- S1.1 resolves B1 at design level: nullable failed/incomplete object measurements; append-only `acquisition_attempts`; separate `object_successful_attempt` relation (no circular FK); tri-state pair results; zero/multiple candidate member evidence with non-unique pair reference; exact raw-row evidence; persisted canonical coverage manifest; run lifecycle and cross-table acceptance invariants.
- S1.1 resolves B2 at policy/contract level: SQLite minimum 3.37.0 for STRICT, exact Python/SQLite runtime pins required in a later approved implementation scope, version check at process/connection, per-connection FK enable/readback, later integrity/FK checks. Exact runtime versions deliberately remain unselected pending separate implementation approval.
- S3 R3–R6, V1 API/error catalogue, T0ENC1, identity prefixes, `T0_STAGING_SCHEMA_V2` and `user_version=2` are retained. No validator source/test/workflow was changed.
- Review state: **documentation content committed; awaiting owner acceptance of the detailed S1.1 design**. Scope approval is not treated as blanket acceptance of every schema detail.
- Historical checkpoint immediately after the original-S1 authority notice: `5ef5641da3d881c5c07a3704289c396834331a66` (not the current HEAD). S1.1 final document blob: `505c23a00772667d0da3f5cc4a48f2d724b84c2a`.
- Verification: GitHub readback of S1.1 document and original S1 authority notice; content-level same-session self-review only. No executable tests, SQL parsing/execution, SQLite, workflow run/job/artifact.
- Status: **B1 RESOLVED AT DESIGN LEVEL; B2 RESOLVED AT POLICY/CONTRACT LEVEL; S1.1 DOCUMENTATION COMMITTED / OWNER ACCEPTANCE PENDING**.
- Remaining blockers: B3 archive format coverage NOT VERIFIED; B4 resource budgets OPEN; B5 actual coverage manifest NOT VERIFIED; B6 retention/artifact policy OPEN; B7 destination/preflight OPEN; B8 importer/build NOT AUTHORIZED; B9 application-foundation review remains separate and unchanged.
- Explicit non-actions: no DDL/migration, SQLite, importer, tests, workflow, archive/sidecar access, materialization, Canonical T0, MAY-10, REST tail, T1/T2 runtime, VPS, deployment, retention/deletion, credentials or trading.
- Next gate: owner reviews and accepts/rejects S1.1 design. Further implementation or data activity requires a separate explicit approval.


### S1.1 review and final readback

- Same-session review record: `docs/reviews/T0_S1_1_SCHEMA_RECONCILIATION_SELF_REVIEW_2026-11-22.md`, blob `a46dd4ce9b64bad09a6ccec078476fa10dc67a65`, commit `e1ec15f69e375433f1686513733cc4d85dd5f017`.
- Review verdict: **SELF-REVIEW PASS WITH LIMITATIONS**. This is not an independent second-person review. It confirms documentation consistency only; no SQL or runtime correctness claim.
- Final S1.1 design blob after deterministic candidate-ID clarification: `505c23a00772667d0da3f5cc4a48f2d724b84c2a`; clarification commit `c4bffd21b22ddb7d2a5b3413fe876e5c62622de4`.
- Final readback confirms S1.1 design and review documents are present on `main`. No implementation/source/test/workflow changes were made.
- Owner acceptance of the detailed design remains **PENDING**. B1/B2 resolved at design/policy level only; B3–B8 remain as recorded above; B9 separate and unchanged.
- The original S1 DDL authority notice remains in place; do not implement its superseded success-only constraints.
- No workflow run/job/artifact; no test, DDL, SQLite, archive, data or runtime operation.

- Latest verified `main` HEAD for this documentation increment: `482d631b69a4abd21db42e2a08d8dad9e790f9c8`. The authoritative main handoff T0 section was updated in commit `0c190a312747e205ca6068d54f509c5bf9756836`; active-scope index link update commit `482d631b69a4abd21db42e2a08d8dad9e790f9c8`.


## Owner acceptance — T0 S1.1 design freeze (2026-11-22)

- Owner decision: **ACCEPTED** the detailed S1.1 provenance/schema design.
- Accepted document: `docs/design/T0_ARCHIVE_STAGING_S1_1_PROVENANCE_SCHEMA_RECONCILIATION_2026-11-22.md`.
- Accepted design blob before this status-only update: `505c23a00772667d0da3f5cc4a48f2d724b84c2a`; post-acceptance status blob: `209c9d10cc0e54dc90148efa9ef6884f74aa143d`.
- Acceptance commit: `9235aeecf81c29a93be2b7aea84e83c0283a270d`.
- Status: **S1.1 DESIGN FROZEN / OWNER ACCEPTED**. B1 resolved at design level; B2 resolved at policy/contract level.
- Scope remains documentation-only. This decision does not authorize DDL, SQL migration, SQLite, importer, synthetic tests, workflow changes/dispatch, archive/sidecar inspection/acquisition, staging build, Canonical T0, MAY-10, REST tail, T1/T2 runtime, VPS/deployment, retention/deletion, credentials or trading.
- B3 archive-format coverage remains NOT VERIFIED; B4 resource limits OPEN; B5 actual source-derived coverage NOT VERIFIED; B6 retention/artifact policy OPEN; B7 destination/preflight OPEN; B8 importer/build NOT AUTHORIZED. Independent application-foundation review track unchanged.
- Same-session review remains **SELF-REVIEW PASS WITH LIMITATIONS**, not an independent review. No tests or workflow were run for this acceptance update; no workflow run/job/artifact.
- Next possible design-only work package: prepare a bounded decision package for B4/B6/B7 (resource budgets, retention/artifact policy, execution destination) for owner review. No acquisition or implementation is implied; each later phase requires separate approval.


## T0 B4 / B6 / B7 decision package — proposal only (2026-11-22)

- Owner requested a design decision package for resource limits (B4), evidence retention (B6), and execution destination (B7).
- Proposal: `docs/design/T0_B4_B6_B7_RESOURCE_RETENTION_DESTINATION_DECISION_PACKAGE_2026-11-22.md`, blob `9119b5789825951e66a061e4b9d989256934adec`.
- Same-session review: `docs/reviews/T0_B4_B6_B7_DECISION_PACKAGE_SELF_REVIEW_2026-11-22.md`, blob `6c6eb22d8643206aba517b3ea8625b70a64735c5`; verdict **SELF-REVIEW PASS WITH LIMITATIONS**, not independent review.
- B4 proposal preserves the 100 MiB cumulative received-response cap and proposes explicit per-object, decompression, ZIP structure, concurrency, retry, timeout, workspace, disk and inode ceilings. It is deliberately conservative and not validated against the real archive set.
- B6 proposal preserves source archives, staging and private provenance evidence until a separate explicit deletion approval; proposes sanitized CI artifacts with 30-day maximum retention. No artifact setting was changed and no deletion is authorized.
- B7 recommends an owner-controlled encrypted personal workstation (Option A), manual/on-demand only. No host/device or exact path has been selected or approved; no preflight was run. New VPS (B) and private object storage (C) remain alternatives.
- Status: **B4 PROPOSED / OWNER DECISION PENDING; B6 PROPOSED / OWNER DECISION PENDING; B7 OPTION A RECOMMENDED / OWNER SELECTION AND LATER PREFLIGHT PENDING**.
- No archive/sidecar access, download, decompression, source-format verification, host/SSH/mount/filesystem inspection, workflow dispatch/artifact upload, retention-setting change, DDL, SQLite, importer, staging build, cleanup/deletion, T1/T2 runtime, deployment or trading.
- B3 remains NOT VERIFIED; B5 remains NOT VERIFIED; B8 remains NOT AUTHORIZED. S1.1 stays owner-accepted and frozen. This proposal does not authorize any later phase.
- Next: owner decides B4, B6 and B7 independently. Any deferred/rejected item remains open; no limit or destination is inferred.
