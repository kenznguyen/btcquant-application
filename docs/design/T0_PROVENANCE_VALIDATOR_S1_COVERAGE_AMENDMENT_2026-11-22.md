# T0 Provenance Validator S1 Coverage Amendment — S3

Date: 2026-11-22  
Status: **DESIGN CONTRACT — SYNTHETIC RED AUTHORIZED; GREEN NOT AUTHORIZED**

## 1. Purpose and compatibility

This amendment extends `T0_PROVENANCE_VALIDATOR_INTERFACE_V1` so that the pure validator can prove the frozen S1 cross-record invariants. It does not change the three public function names or their side-effect boundary:

- `encode_t0enc1(domain, *fields)`
- `derive_attempt_id(...)`
- `validate_provenance(payload)`

V1 error codes remain stable and retain their relative ordering. New codes are appended after the existing V1 catalogue in the order listed in §5. Existing V1 payload fixtures remain valid inputs to the V1 checks, but a payload claiming S1-complete validation must provide the S1 evidence envelope defined here. No silent inference or default success is permitted.

The result remains immutable:
`ProvenanceValidationResult(valid: bool, error_codes: tuple[str, ...])`.

## 2. Extended S1 evidence envelope

The top-level mapping retains all V1 keys and adds:

- `contract_version`: exact string `T0_PROVENANCE_VALIDATOR_S1_V1`.
- `inventory_raw_bytes`: exact immutable `bytes` of the approved inventory document.
- `inventory_expected_sha256`: lowercase 64-hex SHA-256 pinned by the owner-approved inventory manifest.
- `inventory_expected_id`: exact inventory identifier pinned by the caller's approved configuration.
- `coverage_manifest`: mapping with explicit approved coverage boundaries and no implicit gap allowance.
- `run`: mapping with `run_id`, `status`, and `schema_contract_id`.

For S1-complete validation, all eight V1 collections remain required: `objects`, `pairs`, `members`, `attempts`, `source_rows`, `candles`, `links`, plus `inventory.objects`.

The validator receives evidence values already measured or parsed by an upstream caller. It does not open paths, fetch bytes, decompress ZIPs, parse CSV, access SQLite, or consult environment/network/time.

## 3. Inventory byte authentication

The validator must:

1. Require `inventory_raw_bytes` to be bytes and `inventory_expected_sha256` to be lowercase 64-hex.
2. Compute SHA-256 over the exact raw bytes and compare it to the pinned digest.
3. Parse those bytes as strict UTF-8 JSON; reject invalid UTF-8, duplicate JSON object keys, non-standard constants, malformed JSON, and non-object top-level values.
4. Require the parsed inventory identifier to equal `inventory_expected_id`.
5. Derive the canonical object entries from the parsed bytes, not from the separately supplied `inventory.objects` list.
6. Require the parsed and supplied object sets to match exactly, with unique keys, exactly 404 entries, 202 ZIP and 202 CHECKSUM_SIDECAR entries, and reciprocal one-to-one pairing.

The raw inventory byte sequence is authoritative. Re-serialization must not be used to authenticate it.

## 4. Object, attempt, pair and member invariants

### 4.1 Object evidence

Every inventory object has exactly one evidence record keyed by exact `object_key`. Require matching `requested_key`, object kind and paired key. VERIFIED evidence requires:

- non-negative integer `measured_size_bytes` (bool is invalid);
- lowercase 64-hex `measured_sha256`;
- response status in the successful HTTP range defined by the acquisition contract;
- non-empty `local_relative_path`;
- `exclusive_create is 1`;
- no failure code;
- exactly one referenced successful attempt with outcome TRANSFERRED;
- successful attempt complete byte count and digest equal the object measurements.

QUARANTINED evidence remains valid evidence but makes the run unacceptable. Missing, duplicate, extra or mismatched object evidence is a validation failure. A partial-body digest must never satisfy the complete-object digest requirement.

### 4.2 Attempt history

For each object, attempt numbers are unique, positive, contiguous from 1, and strictly ordered by attempt number. Each attempt ID is recomputed using the frozen `derive_attempt_id` contract and all seven identity inputs. STARTED may have no finish timestamp; terminal outcomes require one. TRANSFERRED requires complete-object flag, exact response byte count and complete SHA. Other outcomes cannot claim a complete object. UNKNOWN is retained and fails closed. An object successful-attempt reference must identify the unique successful TRANSFERRED attempt; failed earlier attempts remain present.

### 4.3 ZIP/sidecar pair evidence

Each pair references exactly one ZIP object and its explicitly paired sidecar object. Require both objects VERIFIED; measured ZIP size/SHA and sidecar measurements must be present; parsed sidecar assertion must equal measured ZIP SHA; CRC and structure checks must be true; exactly one verified candidate member must exist. Preserve failed pair evidence and stable failure code, but never accept a QUARANTINED pair.

### 4.4 CSV member evidence

Retain every observed candidate member. A pair may have zero, one or multiple candidate records in quarantined evidence. A VERIFIED pair has exactly one VERIFIED member and no competing candidate that violates the frozen member policy. For a verified member, require exact pair reference, member path, non-negative size, lowercase SHA-256, UTF-8 encoding, BOM flag, newline contract, comma delimiter, exact header mode/contract, parser contract ID and 40-hex parser source SHA, row count, and first/last open-time semantics. The validator checks evidence values; it does not parse member bytes.

## 5. Source-row, candle and provenance-link invariants

### 5.1 Source rows

Every CSV data record is represented exactly once. For each member, physical and data ordinals are positive, unique, contiguous from 1, and obey:
- header present: physical ordinal = data ordinal + 1;
- header absent: physical ordinal = data ordinal.

Require raw fields to be exactly 12 strings, compact JSON representation to match the frozen raw-fields contract, and raw row digest to equal SHA-256(T0ENC1 framing of the exact 12 source fields). Parser/importer contract IDs and source SHAs must be valid. Any REJECTED row makes the run unacceptable; it retains a stable rejection code and has no candle identity/value or provenance link.

### 5.2 Candle identity and normalized value digest

Each ACCEPTED source row maps to exactly one candle natural key and one normalized value. Recompute `candle_value_id` from the exact S1 tuple and order:
`exchange, market_type, symbol, timeframe, open_time_ms, open, high, low, close, volume, available_at_ms, availability_kind`
using the frozen `T0-CANDLE-VALUE-V1` T0ENC1 domain and `cv1:` + lowercase SHA-256. The tuple includes availability boundary and kind; it is not permissible to omit either field. Decimal strings must be canonical plain decimal strings; no float coercion, exponent notation, NaN or Infinity.

Require supported identity values (Binance USD-M BTCUSDT, 15m/1h), non-negative aligned open time, finite positive OHLC, valid OHLC envelope, non-negative volume, and BAR_CLOSE_BOUNDARY availability exactly `open_time_ms + interval_ms`. Source close time is inclusive `open_time_ms + interval_ms - 1`.

All rows sharing one candle natural key must have identical normalized values and value ID. Identical duplicates retain all source-row links; the deterministic UNIQUE representative is the smallest source_row_id by UTF-8 bytes and all others are IDENTICAL_DUPLICATE.

### 5.3 Links and global acceptance

Every accepted source row has exactly one link; every link references an existing accepted row and existing candle with exactly matching natural key and value ID. Every candle has at least one link. No orphan, extra, duplicate or conflicting link is allowed.

A run may be VALIDATED only if:
- inventory and object evidence cardinalities are exactly 404 (202 ZIP + 202 sidecars);
- pair cardinality is exactly 202;
- every pair has exactly one VERIFIED member;
- all attempt histories are complete and internally consistent;
- no object, pair, member or source row is quarantined/rejected;
- all row/member/candle/link cardinalities and invariants pass;
- coverage manifest explicitly accounts for every permitted gap/exception; no implicit gaps or extras;
- schema contract ID is `T0_STAGING_SCHEMA_V2`;
- the caller supplies a run status of CANDIDATE; validator output does not mutate or promote the run.

The validator is read-only and returns a result only. A separate future builder may use a valid result as one prerequisite; this amendment does not authorize that builder.

## 6. Stable error-code catalogue extension

Retain all ten V1 codes unchanged and append:

1. `INVENTORY_RAW_BYTES_INVALID` — raw bytes, pinned digest, strict JSON or inventory identity invalid.
2. `INVENTORY_OBJECT_SET_MISMATCH` — parsed raw inventory and supplied object set differ, duplicate or pairing/cardinality mismatch.
3. `OBJECT_MEASUREMENT_INVALID` — missing/invalid measured size, digest, response, path, create mode or mismatch against inventory expectation.
4. `OBJECT_ATTEMPT_HISTORY_INVALID` — missing/duplicate/non-contiguous attempts, invalid attempt ID/outcome/timestamps or successful-attempt reference mismatch.
5. `ARCHIVE_PAIR_EVIDENCE_INVALID` — ZIP/sidecar relation, sidecar assertion, CRC, structure, pair cardinality or disposition invalid.
6. `CSV_MEMBER_EVIDENCE_INVALID` — member identity/path/digest/encoding/header/parser metadata or verified-member cardinality invalid.
7. `SOURCE_ROW_PROVENANCE_INVALID` — missing/extra row, ordinal, raw field, raw digest, parser/importer provenance or rejected-row invariant invalid.
8. `CANDLE_VALUE_DIGEST_INVALID` — canonical normalized value encoding or recomputed candle_value_id mismatch.
9. `CANDLE_OHLCV_CONSTRAINT_INVALID` — candle identity, decimal grammar, OHLCV envelope, alignment or close-time semantics invalid.
10. `CANDLE_PROVENANCE_LINK_INVALID` — missing/extra/orphan/mismatched links, candle without provenance, or duplicate disposition invalid.
11. `RUN_ACCEPTANCE_INVARIANT_INVALID` — global cardinality, coverage manifest, schema contract or requested VALIDATED status gate invalid.

Error aggregation is set-based, deduplicated and returned in the fixed catalogue order: all V1 codes first in their frozen order, followed by the eleven codes above in this exact order.

## 7. Synthetic RED scope

S4 tests must use deterministic in-memory synthetic evidence only. The valid fixture must contain 404 synthetic inventory objects, 202 reciprocal pairs, verified object measurements and attempts, verified member metadata, synthetic rows/candles/links, and exact pinned raw inventory bytes generated by the test fixture.

Negative cases must independently exercise each new error code and include boundary/combination tests for:
- altered inventory byte, wrong pin, invalid UTF-8/JSON, duplicate keys and raw-vs-parsed object mismatch;
- missing/duplicate/extra object, incorrect size/SHA, partial digest confusion, failed/UNKNOWN/reordered/missing attempts and successful reference mismatch;
- sidecar assertion mismatch, bad CRC, unsupported structure, zero/multiple candidate members and invalid header/parser evidence;
- missing/duplicate/skipped ordinals, header offset, malformed raw fields, raw digest mismatch, rejected row with link;
- candle digest mismatch, non-canonical decimal, float/bool values, OHLCV invalidity, timeframe alignment and inclusive/exclusive close boundary;
- orphan/mismatched/duplicate links, candle without source, duplicate representative ordering;
- incomplete global counts, gap/extra coverage and invalid run/schema state.

Each test asserts the exact stable error code and fail-closed result. A valid synthetic fixture asserts valid=True and no error codes. Tests must not create files, SQLite, network calls, archive bytes from external sources, workflows, or runtime state.

## 8. Explicit non-authorization

This is a contract amendment and synthetic RED-test authorization only. It does NOT authorize:
- validator GREEN implementation or changes to V1 implementation;
- DDL, migrations, SQLite creation or staging database;
- archive/sidecar requests, downloads, decompression or materialization;
- importer, acquisition workflow, workflow dispatch or new workflow YAML;
- Canonical T0, MAY-10, REST tail, T1/T2, VPS/runtime, deployment or trading;
- cleanup, deletion or retention-policy changes.

## 9. Status

- S3 extended contract: **DESIGN ONLY** until committed and read back.
- S4 synthetic RED tests: **AUTHORIZED** by owner, but test execution status must be recorded separately.
- GREEN implementation: **NOT AUTHORIZED**.
- SQLite/DDL and archive acquisition: **NOT AUTHORIZED**.
