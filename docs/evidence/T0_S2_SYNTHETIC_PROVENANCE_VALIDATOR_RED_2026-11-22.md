# T0 S2 — Synthetic Provenance Validator RED Test Specification

Date: 2026-11-22  
Repository: kenznguyen/btcquant-application  
Status: **PARTIAL — RED TEST CONTRACT COMMITTED; EXECUTION NOT VERIFIED**

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

## Test and workflow evidence

- Test execution: **NOT RUN**. The repository source was inspected through GitHub, but the exact repository working tree was not mounted in the local execution environment for this turn.
- Expected RED reason: the production module `market_data.archive_provenance_validator` is intentionally absent. This expectation has **not been runtime-proven** in this increment.
- GitHub Actions run/job/artifact: **NONE**. No workflow was created, dispatched or rerun.
- Full repository regression: **NOT RUN**.
- Self-review: **NOT VERIFIED**.

## Disposition

**PARTIAL — test contract committed; RED execution NOT VERIFIED.**

The test-facing API and stable error-code expectations are now explicit in the test file. They require a bounded interface review before any GREEN implementation. No production validator, DDL, SQLite, importer, archive acquisition, workflow, or data operation is authorized by this work.

## Safety and exclusions

- No archive/sidecar retrieval or access.
- No SQLite file creation/open/write and no DDL execution.
- No importer or acquisition workflow.
- No Canonical T0, MAY-10 or REST tail access.
- No VPS/runtime, T1/T2, deployment, exchange credentials or trading.
- No data cleanup or deletion.
