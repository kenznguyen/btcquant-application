# T0 Provenance Validator V1 — GREEN Implementation Evidence

Date: 2026-11-22
Repository: kenznguyen/btcquant-application
Branch: main
Status: **PARTIAL — V1 FOCUSED GREEN PASS; FULL REPOSITORY REGRESSION NOT PASS**

## 1. Owner authorization and bounded scope

Owner approved the proposed GREEN increment:
- implement only `market_data/archive_provenance_validator.py`;
- implement the frozen `ProvenanceValidationResult`, `encode_t0enc1`, `derive_attempt_id`, and `validate_provenance`;
- add synthetic-only tests for the documented contract gaps;
- preserve the original 12 RED tests unchanged;
- do not implement DDL, SQLite staging, importer, archive acquisition, workflow, or runtime behavior.

## 2. Exact source identity

Final main HEAD after this increment:
- `70f76ef48db9373c42c8436cbb4d490ef51a90ea`

Final GitHub readback blob identities:
- Implementation: `market_data/archive_provenance_validator.py`
  - blob `c2c05dd8e62ebb8d1dce835909e1185a1a67b597`
- New synthetic tests: `market_data/test_archive_provenance_validator_green.py`
  - blob `da854052564a34c49c1e2f40da1c80315da04182`
- Original RED tests, unchanged:
  - `market_data/test_archive_provenance_validator_red.py`
  - blob `abbaeab16f026757923c679330f124a3d99e0774`

GitHub source files were fetched after commit and their blob SHAs read back. The local scratch copies used for the focused test run have matching Git blob SHAs for all three files.

Implementation commit history for this increment:
- Initial module commit: `4004c648b82cce48813ee98133afc4110e4ad0c7`.
- T0ENC1 escape correction: `bbb8e0054f63299d62da53534abf17adcd74d881`.
- Initial GREEN tests: `aa88b5a43cca9f9b1d11e92afbd0c774ce7f7d56`.
- DTO invariant hardening: `371fe1a430f53cc6a1ac51dcfe6e005639329373`.
- DTO regression tests: `861cd9a11da2c21e723368b2cc40469b6cdada02`.
- Missing provenance identity hardening: `30c413c2cb95f69774ebbbd88b258cf1c7785367`.
- Final missing-ID regression test: `d4a9b4752928ac07a7c8e869c97097308e6f8557`.
- Candle identity representation cross-check: `4b71c2b295d3e5f56e5712ace4b0d60e4e47242d`.
- Final candle identity regression test: `70f76ef48db9373c42c8436cbb4d490ef51a90ea`.

An intermediate T0ENC1 source write contained over-escaped byte/regex literals. This was detected by comparing the fetched GitHub blob with the local tested source and corrected before the final focused verification. The final blobs above match the local test copies.

## 3. Implementation summary

- Immutable, slotted `ProvenanceValidationResult`; constructor enforces boolean validity, tuple codes, uniqueness, known V1 codes, catalogue order and the valid/error-code equivalence.
- T0ENC1 implements the frozen prefix, UTF-8 domain framing, field count, NULL/non-NULL tags, 32-bit domain/count lengths and 64-bit field lengths. Strings are not normalized; booleans and unsupported types are rejected.
- Attempt IDs use the S1 domain and exact field order, SHA-256, positive signed-64-bit attempt number and the `att1:` lowercase-hex format.
- Validator enforces top-level input shape, exact 404 inventory-entry count, 202 ZIP / 202 sidecar split, reciprocal one-to-one inventory pairing, evidence key/type coverage, quarantine detection, UNKNOWN and incomplete TRANSFERRED handling, VERIFIED pair/member cardinality, ACCEPTED source-row/link cardinality, candle identity/value conflict detection and BAR_CLOSE_BOUNDARY interval semantics.
- Error aggregation is deduplicated and follows the frozen catalogue order.
- Module imports only Python standard-library modules. No network, filesystem, archive, exchange, environment, clock, random, process or database access is implemented.
- The supplied payload and nested mappings are not mutated.

## 4. TDD and test evidence

Environment: CPython 3.13, isolated extracted source ZIP workspace. All test fixtures are synthetic.

Pre-implementation RED:
- New GREEN test module failed to import the intentionally absent validator module, as expected.
- Existing RED source remained unchanged.

Focused command:
```bash
python -B -m unittest -v market_data.test_archive_provenance_validator_green market_data.test_archive_provenance_validator_red
```
Result: **24 tests — PASS** (12 new GREEN methods + 12 original RED methods).

The added tests cover:
- malformed top-level/container input;
- exact T0ENC1 byte framing and invalid types/UTF-8;
- fixed attempt-ID digest vector, per-field domain separation and numeric/string bounds;
- deduplicated aggregation, catalogue ordering and list/mapping permutation invariance;
- normalized candle tuple conflicts even when a supplied value ID is unchanged;
- missing/unhashable pair and source-row identities;
- consistency between `natural_key` and explicit candle identity fields;
- immutable result DTO and non-mutation of input payload.

Market-data package regression:
```bash
python -B -m unittest discover -s market_data -p 'test*.py'
```
Result: **357 tests — PASS**. Existing ResourceWarnings about unclosed SQLite connections were emitted by the wider test suite; no test failed.

Full repository regression:
```bash
python -B -m unittest discover
```
Result: **579 tests; 1 failure; 6 errors**. All observed failing/erroring tests are under `paper_execution/`, outside the files changed in this increment:
- `test_baseline_is_consumed_by_shared_risk_snapshot_at_boundary_mark`: `ACCOUNT_RISK_MARK_PROVENANCE_INVALID:DATASET_VERSION`.
- `test_daily_loss_limit_latches_kill_after_baseline_rollover`: test mutates a `mappingproxy`.
- `test_max_exposure_limit_still_applies_after_daily_baseline`: test mutates a `mappingproxy`.
- `test_os_process_kill_after_commit_keeps_complete_state_and_retry_is_idempotent`: `ACCOUNT_RISK_MARK_PROVENANCE_INVALID:DATASET_VERSION`.
- `paper_execution.test_dual_strategy_api_red`: SyntaxError, unexpected character after line continuation character, line 98.
- `test_new_database_starts_unpaused_and_not_killed`: `RISK_CONTROL_STATE_UNAVAILABLE`.
- Failure `test_v1_baseline_audit_without_risk_snapshot_is_not_risk_ready`: expected `DAILY_BASELINE_PREVIOUS_BASELINE_UNVERIFIED`, received `ACCOUNT_RISK_MARK_PROVENANCE_INVALID:DATASET_VERSION`.

### Source snapshot limitation

The local workspace came from the user-provided ZIP `btcquant-application-69a97d0c4dce7e85a00a1f49b5e0f25eb28bcc20.zip`, which has no Git metadata. Four earlier source blobs were independently matched to its target commit, and the final implementation, new test and unchanged RED test blobs were subsequently matched against GitHub readback. The complete ZIP tree was not proven identical to final main HEAD. Therefore:
- focused 24-test execution is tied to the exact three relevant file blobs;
- the 357-test market_data run and 579-test repository run are results on the supplied ZIP snapshot, not a fully proven checkout of final main HEAD;
- full repository regression on exact final main HEAD remains **NOT VERIFIED**, in addition to the observed failures above.

## 5. V1 limitations — not a full S1 acceptance validator

This GREEN increment implements the frozen 10-code V1 surface. It does **not** prove the complete S1 acceptance matrix.

Not implemented/verified in this bounded V1:
- authenticating raw inventory bytes against a pinned inventory SHA-256; the current input contract supplies inventory metadata/entries, not raw inventory bytes or a separately frozen expected SHA-256 constant;
- all object measurements, measured size/hash versus expected metadata, object IDs and cross-table object references;
- pair object references, sidecar assertion equality, ZIP CRC and archive structure checks;
- full CSV member metadata/parser contract and every member-to-pair invariant;
- every source-row ordinal, raw row digest, rejection disposition and row-to-candle digest invariant;
- recomputing `candle_value_id` from the complete normalized value tuple;
- full OHLCV validation, timeframe alignment, gaps and the complete coverage/acceptance matrix;
- complete append-only acquisition-attempt history and every attempt cross-reference.

The candle conflict check compares the normalized value fields when present and otherwise falls back to `candle_value_id`; it does not recompute the value digest. These items require separately reviewed coverage and, where needed, a V1 amendment/new interface version before they are relied upon.

The synthetic 404-entry fixture proves only that the current V1 catalogue checks accept that fixture; it is not evidence that a real archive inventory or reconstructed dataset is validated.

## 6. Workflow, artifacts and non-actions

- GitHub Actions workflow run/job/artifact: **NONE**. No workflow was created or modified because workflow implementation was outside the approved scope.
- No archive/sidecar was requested or accessed.
- No Canonical T0, MAY-10 or REST-tail data was accessed.
- No staging SQLite, DDL, importer, data transfer or deletion was performed.
- No VPS/runtime, T1/T2 integration, deployment, exchange credential or trading behavior was changed or invoked.

## 7. Disposition

- Frozen V1 module/API implementation: **PASS**.
- Original 12 RED test bodies: **PASS**.
- New synthetic V1 tests: **PASS**.
- Market-data suite on supplied ZIP snapshot: **PASS — 357/357**.
- Full repository suite on supplied ZIP snapshot: **BLOCKED/PARTIAL — 1 failure, 6 errors**.
- Full repository regression on exact final main HEAD: **NOT VERIFIED**.
- Full S1 acceptance matrix and real inventory authentication: **NOT VERIFIED**.
- Workflow run/job/artifact: **NONE**.
- No scope expansion is authorized by this result.

## 8. Same-session self-review

- Correctness: reviewed input-shape guards, T0ENC1 framing, attempt-ID preimage and bounds, stable error aggregation, unhashable/missing identity handling, pair/member and row/link matching, and candle identity/value/boundary checks. The review found that a record could supply both `natural_key` and explicit identity fields that disagreed; this was fixed and covered by `test_candle_natural_key_must_match_explicit_identity_fields`.
- Readability/architecture: one self-contained standard-library module; no changes to existing T0 storage/API/runtime modules; public API limited to the frozen three functions plus DTO.
- Security: payload treated as untrusted mappings; no I/O, dynamic execution, SQL, network, secret handling or dependency additions.
- Performance: linear scans and bounded 404-entry inventory validation; no external calls or unbounded retrieval.
- Verdict: **SELF-REVIEW PASS WITH KNOWN S1 COVERAGE LIMITATIONS**. This is not an independent second-person review.
