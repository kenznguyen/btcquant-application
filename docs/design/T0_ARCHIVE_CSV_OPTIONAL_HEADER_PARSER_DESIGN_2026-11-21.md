# T0 Archive CSV Optional-Header Parser Design

**Date:** 2026-11-21  
**Repository:** `kenznguyen/btcquant-application`  
**Branch:** `main`  
**Status:** DESIGN REVIEW — PASS WITH REQUIRED INPUT GATE  
**Implementation:** NOT STARTED / NOT AUTHORIZED  
**Archive access / workflow dispatch:** NOT AUTHORIZED  
**Parser contract freeze:** BLOCKED

## 1. Purpose and scope

Design a strict parser that can accept either:
- a CSV whose first record is the one exact, approved 12-column schema header; or
- a headerless CSV whose first record is a valid 12-field data row.

The parser must never decide to skip a row merely because it looks textual, has a nonnumeric first field, or fails numeric parsing. Header recognition is a positive exact-schema match, not a heuristic.

This is a design-only increment. It does not change parser code, tests, workflow, archive allowlist, inventory, source data, SQLite, importer, Contract 1.2.0, Canonical T0, T1/T2, VPS/runtime or trading behavior.

## 2. Evidence and baseline

- Current parser: `market_data/archive_csv_parser.py`, blob `7d59706778a98a18185e0b2fe744c3c43c2eb870`.
- Current parser tests: `market_data/test_archive_csv_parser.py`, blob `50199cd168fd52314a846760cc4baf51a8cd5e9a`, 19 tests.
- Workflow: `.github/workflows/t0-real-archive-csv-sample-verification.yml`, blob `9edb0e4cf74c22f82c38f107c730e73abf04de44`.
- Third approved run: [44923634320](https://github.com/kenznguyen/btcquant-application/actions/runs/44923634320), source SHA `ab2ae82c12f858492128528d52b01c4455f43083`, job `136904830969`.
- Observed failure: M15 monthly archive `BTCUSDT-15m-2022-08.zip` contains a first row rejected by the workflow's headerless assumption: `unexpected CSV header row`.
- The preceding M15 daily 2019-12-31 sample passed far enough for the workflow to advance. The remaining four ZIPs were not verified. No diagnostic artifact was produced.
- This is evidence of at least one header-format variant in the sampled source; it is not evidence that all archive files use headers or that the archive is corrupt.

Current parser is deliberately headerless and rejects a header row. The workflow independently hardcodes the same headerless assumption and currently recognizes a header by checking only the first cell for `open_time`. That one-cell check is not a sufficiently strict schema detector.

## 3. Proposed contract

### 3.1 Positive exact-header recognition

At the first CSV record only:

1. Parse CSV using the existing strict CSV reader and comma delimiter.
2. Require exactly 12 fields.
3. Compare the entire ordered 12-field tuple against one frozen canonical header tuple.
4. If and only if the complete tuple matches, classify the document as `HEADER_PRESENT` and skip exactly that one record.
5. Otherwise classify the document as `HEADER_ABSENT` and validate the first record as ordinary data. Numeric, timestamp, decimal, timeframe, OHLC and volume validation must reject malformed rows normally.

The canonical header tuple is intentionally **not frozen in this design**. It must be transcribed from an approved real-source sample and checked against the 12-field semantic mapping before implementation. Do not invent aliases or infer the tuple from a partial label such as `open_time`.

A future explicit normalization policy may permit ASCII case-folding and surrounding ASCII whitespace only, but the default safest contract is exact field-name matching. Any normalization or alternate header spelling must be explicitly listed and tested; do not use fuzzy matching, substring matching, edit distance, positional guesses or a broad alias dictionary.

### 3.2 No heuristic row skipping

Never:
- skip a record because field 0 is not an integer;
- skip a record because numeric parsing fails;
- accept a header when only one or a subset of column names match;
- search later rows for a header;
- silently drop blank rows, malformed records or repeated headers;
- auto-detect delimiter, column count or field order;
- retry parsing after removing the first row.

A malformed/partial/reordered/unknown header is treated as data and fails normal validation (typically at `open_time`), with row number and field context. A repeated header in the body also fails normal data validation. This makes false-positive header skipping structurally difficult.

### 3.3 Data-row validation remains unchanged

After optional exact-header handling, every data record must pass all existing validations:
- exactly 12 columns;
- strict CSV syntax;
- non-empty document and at least one data row;
- integer timestamp grammar and signed-int64 bounds;
- timeframe-aligned open timestamp;
- exact inclusive close-time boundary for the selected timeframe;
- strictly increasing open timestamps;
- finite plain-decimal grammar and existing token-length limits;
- positive OHLC prices and valid OHLC envelope;
- nonnegative volume fields;
- taker-buy base/quote volumes not exceeding their respective totals.

No field coercion through float is allowed. Preserve exact Decimal values and raw fields.

### 3.4 Result metadata and compatibility

Keep the existing public convenience function behavior: `parse_archive_csv(...)` continues returning the tuple of immutable rows, so current callers do not need to consume a new result type.

For evidence and diagnostics, introduce an additive parse-document API/result in a future implementation, for example:
- `rows`
- `header_present` (`true/false`)
- `header_fields` (exact accepted tuple or null)
- `data_row_count`

The existing function may delegate to this API and return only `rows`. The exact public name/type is an implementation-time contract decision; do not silently change the existing return type.

The workflow diagnostic report should record `header_present`, exact observed header fields (only when accepted), and data-row count for each archive. This is metadata, not a change to candle semantics or provenance.

## 4. Required rejection behavior

| Input condition | Required behavior |
|---|---|
| Exact approved 12-field header, then valid rows | Accept; skip exactly first record |
| Valid headerless data rows | Accept; parse first record as data |
| First row has only `open_time` label but other labels differ | Do not skip; reject as invalid data |
| Missing, extra, duplicated or reordered header fields | Do not skip; reject |
| Header with unsupported aliases/case/whitespace | Reject unless exact normalization policy is separately approved |
| Header appears after first record | Reject as invalid data |
| Repeated header in body | Reject as invalid data |
| Header-only file | Reject: no data rows |
| Blank first/body record | Reject; never skip |
| Wrong delimiter or malformed quoting | Reject |
| Valid data row containing ordinary numeric-looking values | Parse as data; never infer header from values |
| Empty file | Reject |

## 5. Required test design (TDD)

Add tests before implementation. Keep the current 19 tests and preserve their existing expectations. New tests should cover at least:

1. Accept headerless M15 synthetic fixture unchanged.
2. Accept headerless H1 synthetic fixture unchanged.
3. Accept a synthetic CSV with the exact approved 12-field header and valid data rows.
4. Header-present and headerless versions of the same data produce identical row objects.
5. Report `header_present=true` only for an exact full ordered header match.
6. Reject first-cell-only match / partial header.
7. Reject missing, extra, duplicated and reordered header fields.
8. Reject unsupported aliases and normalization variants.
9. Reject a header in the second or later record.
10. Reject repeated header after the first record.
11. Reject header-only input.
12. Reject blank first record and blank body record.
13. Reject malformed quoting and wrong delimiter.
14. Ensure a malformed data row is not skipped as a supposed header.
15. Ensure all existing numeric, timestamp, OHLC, volume and ordering validation tests still pass.

Use synthetic fixtures only for parser unit tests. A synthetic header fixture tests the algorithm, not whether the chosen header tuple matches Binance source archives.

## 6. Workflow interaction

The current verification workflow has two headerless-only checks:
- a first-column heuristic that raises when field 0 equals `open_time`;
- a report field hardcoded to `header: absent`.

A future separately approved workflow change should:
- use the same parser header detector as the parser, not a second independent heuristic;
- pin the parser and test blobs after implementation;
- record per-object header presence and the exact accepted header;
- compare parsed data-row count (excluding the one accepted header) with the manifest's expected data-row count;
- retain the exact six ZIP + six paired sidecar allowlist and all existing byte-integrity, ZIP CRC, member-path, UTF-8, newline and source provenance checks;
- continue uploading diagnostic JSON only, never raw ZIP/sidecar/CSV data.

Do not modify or dispatch the workflow as part of this design approval.

## 7. Risks and controls

- **False-positive header detection:** controlled by exact full ordered schema match on the first record only.
- **False-negative header detection:** an unrecognized variant fails closed; add a variant only after source evidence and explicit schema approval.
- **Parser/workflow divergence:** use one shared parser detector; remove duplicated first-cell heuristics in a separately approved workflow change.
- **Row-count drift:** compare expected manifest data rows to parsed rows after excluding only the one exact header.
- **Accidental API break:** preserve `parse_archive_csv` tuple return; add diagnostic result through a separate additive function/type.
- **Unverified header names:** do not implement until the actual 12 header labels are obtained from an approved real-source sample and mapped one-to-one to existing semantic fields.
- **Archive variant overgeneralization:** one observed M15 monthly sample does not establish header behavior for other dates or H1. Verify per object; do not assume uniformity.

## 8. Approval and implementation gates

This design approval covers evaluation and documentation only.

Before implementation:
1. Obtain/inspect an approved representative real-source CSV sample (the current third run did not produce an artifact and did not complete the six-object matrix).
2. Record exact 12 header labels, order, encoding/BOM, newline, delimiter, member path and row-count semantics with source object SHA evidence.
3. Confirm whether M15/H1 and daily/monthly archives share one header tuple or require explicitly enumerated variants.
4. Freeze the accepted header tuple(s) and normalization policy in the parser contract.
5. Obtain separate approval for TDD implementation.
6. Obtain separate approval for any workflow correction and any further manual dispatch.

No fourth dispatch is approved by this design. Do not use the old run as permission to re-fetch archives. The parser, tests and workflow remain unchanged until separate implementation approval.

## 9. Status

| Item | Status |
|---|---|
| Optional-header parser design | **PASS WITH REQUIRED INPUT GATE** |
| Exact header tuple | **NOT VERIFIED / NOT FROZEN** |
| Header normalization policy | **NOT FROZEN** |
| Existing parser behavior | **UNCHANGED** |
| Parser tests | **NOT CHANGED / NOT RUN** |
| Workflow | **UNCHANGED** |
| Six-object verification | **NOT VERIFIED** |
| Parser contract freeze | **BLOCKED** |
| Implementation / importer / SQLite | **NOT AUTHORIZED** |

## 10. Work record and exclusions

- Read-only inspection of current main source, tests, workflow, handoff and prior design/evidence.
- No code or test changes.
- No archive, REST or external source request.
- No archive materialization or fixture creation.
- No workflow dispatch or rerun.
- No SQLite, importer, Contract 1.2.0 implementation, Canonical T0, T1/T2, VPS/runtime, deployment, exchange credential or trading operation.
