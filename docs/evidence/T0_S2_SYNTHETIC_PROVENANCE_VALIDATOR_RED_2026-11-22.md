# T0 S2 — Synthetic Provenance Validator RED Test Specification

Date: 2026-11-22  
Repository: kenznguyen/btcquant-application  
Status: **PARTIAL — RED EXECUTION REPRODUCED; ASSERTION SEMANTICS NOT VERIFIED**

## Scope approval

Owner approved S2 limited to synthetic-only provenance validator RED tests. This increment adds tests only. It does not implement the validator or any production behavior.

## Scope implemented

- Added `market_data/test_archive_provenance_validator_red.py`.
- Expected future module: `market_data.archive_provenance_validator`.
- Expected API under test: `encode_t0enc1`, `derive_attempt_id`, and `validate_provenance`.
- 12 unittest methods specify:
  - T0ENC1 framing, field-boundary ambiguity and NULL versus empty distinction.
  - Deterministic acquisition attempt IDs and attempt-number domain separation.
  - Fail-closed handling of incomplete inventory/object provenance.
  - QUARANTINED object evidence with nullable measurements.
  - UNKNOWN acquisition attempt and distinction between partial and complete object digests.
  - VERIFIED pair requiring exactly one verified CSV member.
  - Accepted source-row provenance-link cardinality.
  - Conflicting candle values for the same natural identity.
  - BAR_CLOSE_BOUNDARY exclusive interval-end semantics.

All test inputs are inline synthetic dictionaries and invented identifiers. No source market data is embedded.

## Exact source evidence

- Test file path: `market_data/test_archive_provenance_validator_red.py`
- Final test blob SHA: `abbaeab16f026757923c679330f124a3d99e0774`
- Initial test-only commit: `a27d303e981da94f3c379672fb2c2c452cd08d99`
- Assertion correction commit: `69a97d0c4dce7e85a00a1f49b5e0f25eb28bcc20`
- S1 design baseline/amendment: `ee30e4bcb1e1118901e372f642f368e4f4578649`
- User-provided source ZIP: `btcquant-application-69a97d0c4dce7e85a00a1f49b5e0f25eb28bcc20.zip`; 352 entries; no `.git` metadata.
- Four independently checked Git blob hashes match the ZIP: test file `abbaeab16f026757923c679330f124a3d99e0774`, README `d92db98aed9a89635aa2ad773a6060a59dce895a`, main handoff `4bbfa5955747f29a1ea4769a7ec9a78dd2a5d792`, and amended S1 design `af7c90af0f0bcfa8d0b2143578222619af620197`.
- These matching blobs support the target-source identity for the checked files; because the ZIP has no Git metadata, they do not prove every file in the archive belongs to that commit.

## Test and workflow evidence

- Exact command: `python -B -m unittest -v market_data.test_archive_provenance_validator_red`
- Execution environment: isolated extracted ZIP checkout; CPython 3.13.
- Result: **12 tests run; 12 errors; exit code 1**.
- All 12 errors occur in `setUp()` at import of `market_data.archive_provenance_validator`, with `ModuleNotFoundError: No module named 'market_data.archive_provenance_validator'`.
- Validator module path is absent from the ZIP.
- No test body or business assertion ran. This proves the expected missing-module RED state at this source snapshot; it does not prove the 12 validator invariants.
- GitHub Actions run/job/artifact: **NONE**. No workflow was created, dispatched or rerun.
- Full repository regression: **NOT RUN**.

## Bounded interface review

Reviewed the test-facing expectations against S1 amendment `ee30e4bcb1e1118901e372f642f368e4f4578649`.

- S1 freezes T0ENC1 framing and acquisition-attempt ID inputs; the tests' named functions and attempt-ID arguments are consistent with those design definitions.
- S1 defines cross-record invariants and requires stable rejection codes for rejected source rows.
- S1 does **not** independently freeze a validator result DTO/API shape (`result.valid`, `result.error_codes`), the complete validator-level error-code catalogue, or deterministic ordering/aggregation semantics for multiple error codes. The RED test currently embeds individual expected code strings, but that alone is not a reviewed, complete interface contract.
- Therefore the test-facing result shape and stable error-code catalogue are **BLOCKED FOR GREEN IMPLEMENTATION** pending an explicit interface decision. Do not infer or invent missing codes during implementation.

## Disposition

**PARTIAL — expected missing-module RED reproduced at exact test blob; validator assertions NOT VERIFIED; GREEN implementation BLOCKED pending API/error-code contract freeze.**

## Safety and exclusions

- No archive/sidecar retrieval or access.
- No SQLite file creation/open/write and no DDL execution.
- No importer or acquisition workflow.
- No Canonical T0, MAY-10 or REST tail access.
- No VPS/runtime, T1/T2, deployment, exchange credentials or trading.
- No data cleanup or deletion.
