# T0 Provenance Validator S3 GREEN — Final RED Review and Approval Scope

Date: 2026-11-22  
Repository: `kenznguyen/btcquant-application`  
Branch: `main`  
Review type: **SELF-REVIEW — specification and test-source review only**  
Disposition: **S3 GREEN NOT AUTHORIZED — approval requested**

## 1. Review baseline and exact sources

Read-only review performed against:

| Source | Exact blob / commit |
|---|---|
| S4 S1 RED tests `market_data/test_archive_provenance_validator_s1_red.py` | `08d02470e87e317afe8023ed6d6f14db847f5597` |
| V1 validator `market_data/archive_provenance_validator.py` | `c2c05dd8e62ebb8d1dce835909e1185a1a67b597` |
| V1 RED tests | `abbaeab16f026757923c679330f124a3d99e0774` |
| V1 GREEN tests | `da854052564a34c49c1e2f40da1c80315da04182` |
| S3 contract amendment | `43719373949c0c2d553b463ab5ac66aadd64da2b` |
| V1 interface contract | `632eb6d38461ea3c65638ca073abc5fe4ae98729` |
| Tested source SHA | `4534904fccc74a57a3a09793dd63e24414ab2cb1` |
| Existing workflow run | [44941050940](https://github.com/kenznguyen/btcquant-application/actions/runs/44941050940) |

Workflow 44941050940 checked out the requested source SHA exactly. S4 command result: 13 tests, 1 fixture-structure PASS, 12 assertion failures, exit 1. V1 regression: 24/24 PASS, exit 0. The workflow's SUCCESS status means its evidence-capture wrapper completed; it is not an S4 PASS.

The current validator is V1-only: its stable catalogue contains the ten V1 codes and it does not implement the eleven S3 codes. No S3 implementation exists in the reviewed source.

## 2. Review of the twelve RED assertions

There are eleven individual code-targeted tests and one aggregate test. The separate deterministic fixture test is not one of the twelve RED assertions.

| RED assertion | Intended invariant / code | Review verdict |
|---|---|---|
| `test_inventory_raw_bytes_invalid_isolated` | Exact raw bytes, pinned SHA, strict UTF-8/JSON — `INVENTORY_RAW_BYTES_INVALID` | **PARTIAL**. Invalid UTF-8 with matching byte digest isolates strict decoding. Missing pin mismatch, malformed JSON, duplicate keys, non-standard constants, non-object JSON, and inventory-ID mismatch cases. |
| `test_inventory_object_set_mismatch_isolated` | Parsed raw inventory vs supplied set, exact 404/202/202 and reciprocal pairing — `INVENTORY_OBJECT_SET_MISMATCH` | **GOOD TARGET / LEGACY COMPANION EXPECTED**. Removing one supplied entry while raw bytes remain fixed exercises mismatch. The two V1 diagnostics are expected compatibility diagnostics. Missing duplicate-key/object, extra/duplicate/mispaired and wrong-kind cases. |
| `test_object_measurement_invalid_isolated` | Object measurement/response/path/create/expectation — `OBJECT_MEASUREMENT_INVALID` | **PARTIAL**. HTTP 302 is a focused invalid-response example. No isolated size/SHA mismatch, bool/negative size, malformed digest, path/create-mode, missing measurement, or expected-vs-measured source-of-truth case. |
| `test_object_attempt_history_invalid_isolated` | Attempt IDs, sequence 1..N, outcomes/timestamps and successful pointer — `OBJECT_ATTEMPT_HISTORY_INVALID` | **GOOD TARGET**. Sole attempt starts at 2; its ID and successful pointer are recomputed, so the sequence gap is the primary defect. Missing duplicate IDs, multiple attempts, terminal timestamp rules, partial/failed/UNKNOWN, wrong ID and pointer mismatch. |
| `test_archive_pair_evidence_invalid_isolated` | ZIP/sidecar relation, assertion, CRC, structure and member cardinality — `ARCHIVE_PAIR_EVIDENCE_INVALID` | **GOOD TARGET**. CRC false is isolated. Sidecar mismatch, pair references/kinds, structural flag, zero/multiple candidate members and quarantine semantics remain uncovered. |
| `test_csv_member_evidence_invalid_isolated` | Member metadata/parser evidence — `CSV_MEMBER_EVIDENCE_INVALID` | **GOOD TARGET**. Invalid parser SHA is focused. Path/digest/size, UTF-8/BOM/newline/delimiter/header, row count/time range, competing candidates and exact pair references remain uncovered. |
| `test_source_row_provenance_invalid_isolated` | Row completeness, ordinals, raw fields/digest and parser/importer provenance — `SOURCE_ROW_PROVENANCE_INVALID` | **GOOD TARGET**. Header-present physical/data ordinal offset is invalidated while source-row ID and link references are recomputed. Duplicate/skipped ordinals, 12-field grammar, canonical raw representation/digest, missing rows and rejected-row/link behavior remain uncovered. |
| `test_candle_value_digest_invalid_isolated` | Recompute exact normalized tuple and `candle_value_id` — `CANDLE_VALUE_DIGEST_INVALID` | **GOOD TARGET**. Forged value ID is propagated to row and link, isolating tuple recomputation. Missing/malformed ID, wrong tuple member/order, and digest-format cases remain uncovered. |
| `test_candle_ohlcv_constraint_invalid_isolated` | Decimal grammar, OHLCV, identity/alignment/close boundary — `CANDLE_OHLCV_CONSTRAINT_INVALID` | **REQUIRED TEST CORRECTION**. The test changes candle high/low but leaves the source row's raw CSV fields, raw digest, source-row ID, member digest/identity and provenance chain unchanged. Because S3 requires accepted source rows to map to normalized candle values, a correct validator may also emit `SOURCE_ROW_PROVENANCE_INVALID`. The mutation is therefore not demonstrably isolated. Update the synthetic source chain consistently or choose a mutation that violates only the OHLCV constraint. The aggregate case repeats this coupling on another row. |
| `test_candle_provenance_link_invalid_isolated` | Link graph, disposition and deterministic duplicate policy — `CANDLE_PROVENANCE_LINK_INVALID` | **GOOD TARGET**. Unsupported disposition with recomputed link ID is focused. Orphan/missing/extra/duplicate links, candle-without-link, natural-key mismatch and UNIQUE/IDENTICAL_DUPLICATE representative ordering remain uncovered. |
| `test_run_acceptance_invariant_invalid_isolated` | Global cardinality, coverage, schema and candidate run-state — `RUN_ACCEPTANCE_INVARIANT_INVALID` | **PARTIAL**. Wrong schema ID is isolated. Coverage counts, approved gaps/extras, invalid run state, rejected/quarantined evidence and incomplete cross-table cardinalities remain uncovered. |
| `test_aggregate_new_codes_are_ordered_and_deduplicated` | All eleven S3 codes, fixed order, deduplication and V1 compatibility | **GOOD AGGREGATE SKELETON / NOT FULLY PROVEN**. It uses disjoint records and asserts all eleven codes plus two V1 diagnostics in order. The OHLCV/source-row coupling above remains. It does not prove permutation invariance or duplicate triggers for each S3 code. |

### Cross-cutting required findings

**R1 — Positive S1 acceptance is not asserted.**  
`test_complete_s1_fixture_is_deterministic_and_structurally_valid` checks fixture construction independently, but never calls `validate_provenance(self.payload)`. A validator that rejects every S1 payload could still satisfy all twelve negative assertions. GREEN acceptance must include a positive test proving the complete valid fixture returns `valid is True` and `error_codes == ()`, and does not mutate the payload.

**R2 — OHLCV negative mutation is not isolated.**  
The specific test and aggregate fixture need consistent raw-row/member provenance updates, or a revised single-defect fixture. A dedicated OHLCV error must not be “proven” by simultaneously corrupting the source-row-to-candle mapping.

**R3 — S1/V1 mode dispatch needs a frozen rule.**  
The S3 amendment says legacy V1 payloads remain valid inputs to V1 checks and an S1-complete claim requires the S1 envelope. It does not fully state behavior for an unknown `contract_version`, a missing discriminator with S1-only fields, or a partially supplied S1 envelope. Before GREEN, freeze: legacy payload with no S1 discriminator follows V1; exact `T0_PROVENANCE_VALIDATOR_S1_V1` invokes all S1 checks and requires every envelope field; unknown/partial claims fail closed with a documented stable code. Do not silently downgrade an S1 claim to V1.

**R4 — Expected object size/SHA trust source is underspecified.**  
S3 says measured values must match inventory expectations, but the current synthetic raw inventory entries contain object key/kind/pair/timeframe/partition/period and do not contain expected size/SHA. The fixture puts expected size/SHA on the object evidence itself, equal to measured values. That is self-consistency, not proof against an independently pinned inventory expectation. Freeze where expected size/SHA originate and how absence is represented before implementing `OBJECT_MEASUREMENT_INVALID`.

**R5 — Raw-field canonical representation needs a concrete contract.**  
S3 requires a compact JSON representation of the twelve raw fields, but the fixture currently supplies only `raw_fields` as a list and a T0ENC1 digest. Specify the exact canonical representation/field and whether the validator recomputes it, or remove/clarify that requirement. Do not invent a serializer during GREEN.

**R6 — Coverage manifest and duplicate semantics need executable shapes.**  
The amendment names approved gaps/extras and deterministic duplicate dispositions, but the current fixture uses empty gap/extra lists and unique candles only. Freeze the accepted manifest record shape, allowed gap/extra semantics, and exact disposition vocabulary/representative ordering before coding those checks.

These are contract/test-completeness findings, not reasons to modify the current V1 behavior. The present RED run proves that the S3 behavior is absent; it does not prove every S3 invariant has a complete, isolated executable specification.

## 3. Proposed bounded S3 GREEN approval scope

### Goal

Extend the existing pure `market_data.archive_provenance_validator.validate_provenance(payload)` to validate the S1 evidence envelope and all S3 cross-record invariants, preserving V1 compatibility and the existing public API.

### Work package (approval requested)

1. **Contract clarification before implementation**
   - Resolve R3–R6 above in a small S3 contract follow-up.
   - Freeze V1-vs-S1 dispatch, expected size/SHA provenance, raw-field canonical representation, coverage-manifest shape and duplicate disposition vocabulary.
   - Preserve the three public functions and immutable `ProvenanceValidationResult(valid, error_codes)`.
2. **Test-specification completion**
   - Correct the OHLCV fixture so the source-row/member chain remains internally consistent.
   - Add a positive complete-S1 validation assertion.
   - Add focused synthetic boundary tests from S3 §7: raw inventory parse/pin cases; object measurement and attempt-history cases; pair/member cardinality and integrity; row ordinal/raw digest/rejection; candle canonical decimal/digest/OHLCV/time alignment; link graph/duplicate ordering; global coverage/run acceptance.
   - Keep all fixtures deterministic and in-memory. Do not edit the original V1 RED/GREEN tests.
3. **Pure validator GREEN**
   - Append the eleven S3 codes in the exact frozen order after all V1 codes; retain all V1 meanings/order.
   - Implement strict raw-byte SHA/UTF-8/JSON checks (including duplicate-key and non-standard-constant rejection), parsed-vs-supplied inventory equality and exact pairing.
   - Validate object measurements and complete append-only attempt histories, including recomputed attempt IDs and successful-attempt linkage.
   - Validate pair, sidecar, CRC/structure and candidate-member evidence.
   - Validate member metadata, every source-row ordinal/raw-field/digest/parser/importer invariant, canonical candle tuple digest, Decimal/OHLCV/time constraints, provenance links, duplicate representative rules and global run acceptance.
   - Aggregate all applicable codes once, in exact catalogue order; fail closed; never mutate input.
   - Keep the implementation pure and deterministic: standard library only; no file, archive, network, environment, clock, random, SQLite, database or process access.
4. **Compatibility and verification**
   - Preserve all existing V1 RED/GREEN source blobs unchanged and prove 24/24 V1 tests pass.
   - Prove the valid S1 fixture passes with no codes; each of the eleven S3 codes has an isolated negative assertion; aggregate order/dedup and permutation behavior pass.
   - Run the full `market_data` test suite and record any unrelated baseline failures separately.
   - Reuse the existing isolated GitHub Actions workflow, updating only what is required to execute the S3 tests and V1 regression. Run against the exact final source SHA; inspect job logs, both exit codes and artifact/checksum.
   - Perform and label same-session **SELF-REVIEW**. No claim of independent second-person review.
5. **GitHub evidence**
   - Record scope, exact source/test/workflow blob SHAs, test commands/results, run/job/artifact IDs and digest, PASS/BLOCKED/NOT VERIFIED, remaining limitations and next gate.
   - Commit to the existing `main` branch; do not create a divergent implementation branch.

### Explicit exclusions

This approval request does **not** include:
- DDL, schema migration, SQLite/staging database creation or writes;
- archive/sidecar access, download, decompression or materialization;
- importer, acquisition workflow, new acquisition automation or real archive validation;
- Canonical T0, MAY-10, REST tail, T1/T2 runtime or data integration;
- VPS, systemd/autostart, deployment, PostgreSQL activation;
- cleanup/deletion/retention changes, exchange credentials, order placement or trading.

### Acceptance criteria

- [x] Contract clarifications R3–R6 committed before relying on them in code.
- [x] Positive complete S1 fixture: `valid=True`, `error_codes=()`, input unchanged.
- [x] Each of eleven S3 codes individually exercised with no unintended local diagnostic; documented global run-acceptance companion code is permitted where contractually required.
- [x] Aggregate returns all eleven S3 codes exactly once in catalogue order, with V1 diagnostics in their original order.
- [x] Input/list permutation and mapping insertion-order determinism proven, except where row ordinal ordering is semantically meaningful.
- [x] Existing V1 regression remains 24/24 PASS and V1 public API/result DTO unchanged.
- [x] Full market_data regression result recorded.
- [x] Exact-SHA GitHub Actions run/job/artifact inspected and evidence committed.
- [x] No excluded resource or runtime operation occurred.

## 4. Approval decision — APPROVED 2026-11-22

Owner explicitly approved this bounded work package on 2026-11-22:

**S3 GREEN = contract clarifications R3–R6 + S4 test-specification completion (including R1/R2) + pure validator implementation + synthetic tests + isolated exact-SHA CI/evidence only.**

Approval did not authorize any excluded database, archive, importer, runtime, deployment or trading work.

## 5. Final implementation and verification status — 2026-11-22

- R3–R6 contract clarifications: **COMMITTED / FROZEN**. R6 includes explicit coverage ranges and exact gap/extra set semantics.
- S4 test-spec completion: **PASS** — positive complete S1 fixture, isolated OHLCV chain, per-code negative assertions, strict raw inventory/JSON cases, object/attempt/pair/member/row/candle/link/run boundaries, coverage range/gap tests, aggregate ordering/dedup and permutation checks.
- Pure S1 validator implementation: **PASS** — V1 API and catalogue retained; eleven S3 codes appended; fail-closed dispatch; deterministic in-memory validation; no I/O or input mutation.
- Exact-SHA GitHub Actions: **PASS** — run `44976345735`, job `137067027769`, exact source SHA `10e99c68e7acbd8a25e192075dede214f3fccad5`.
- S3 synthetic suite: **30/30 PASS**, exit 0.
- V1 RED/GREEN compatibility: **24/24 PASS**, exit 0; original V1 test blobs unchanged.
- Full `market_data` regression: **387/387 PASS**, exit 0. Two SQLite `ResourceWarning` messages were emitted; they did not fail tests.
- Artifact: `t0-s3-green-verification-44976345735`, ID `14735512352`, 3,678 bytes, SHA-256 `5d12d74c405e8e9bd7bd6443b3f6fe4b85681eeba1b35df5dc78a7057f11e8bf`; downloaded, ZIP integrity/content inspected, checksum matched GitHub metadata.
- Source blobs at tested SHA: validator `b94bac0f82ae141984552409f99a5cff70435b3b`; S3 tests `328442917535d555d09b18f0213e1ddfd75a9416`; S3 contract `84f881ad3e81cf42f1ec674a5b36ae5547478e33`; workflow `b73bf266c47dd6cdb440928e2107306f4906a5b6`; V1 RED `abbaeab16f026757923c679330f124a3d99e0774`; V1 GREEN `da854052564a34c49c1e2f40da1c80315da04182`.
- Runtime: CPython 3.13.18, Ubuntu 26.04.1. Workflow installed pinned test dependencies FastAPI 0.116.1 and httpx 0.28.1.
- Same-session **SELF-REVIEW COMPLETE**. No independent second-person review is claimed.
- DDL/SQLite/archive/importer/Canonical T0/MAY-10/REST tail/T1/T2/VPS/runtime/deployment/retention/trading: **NOT AUTHORIZED / NOT TOUCHED**.

- Final `main` HEAD confirmation after recording the owner approval/PASS status in the contract document: workflow run `44976543815`, job `137067027769`, exact source SHA `d1651196af3059e00b22f65461dbd897e5c599df`; contract blob `da89266c7c4d1394c731b1c2304cdb73b077d4f6`. Results remained S3 30/30, V1 24/24, market_data 387/387, all exit 0. Artifact `t0-s3-green-verification-44976543815`, ID `14735332978`, SHA-256 `a359d04c458a8545e386a288ef5ad6219d6f7bb9d31a6525778444eefeb40cf8`.
- Disposition: bounded S3 GREEN implementation and verification **PASS**. This is not archive acquisition/validation, staging DB acceptance, or promotion authorization.
