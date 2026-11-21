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
