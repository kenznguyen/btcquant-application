# T0 Provenance Validator S1 Coverage Amendment — S3

Date: 2026-11-22  
Status: **DESIGN CONTRACT — S3 GREEN APPROVED 2026-11-22; IMPLEMENTATION IN PROGRESS**

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


## 10. S3 GREEN clarifications — R3–R6 (owner-approved)

These rules close the executable-contract ambiguities identified in the S3 GREEN review. They are normative and take precedence over ambiguous wording in §§2–7.

### 10.1 R3 — Explicit V1/S1 dispatch

- If `contract_version` is absent **and no S1-only envelope key is present**, validate as legacy V1 only.
- The S1-only key set is: `inventory_raw_bytes`, `inventory_expected_sha256`, `inventory_expected_id`, `coverage_manifest`, and `run`.
- If the exact discriminator `T0_PROVENANCE_VALIDATOR_S1_V1` is present, run the complete V1 and S1 validation path; every S1 envelope key is mandatory and must have its specified type.
- If the discriminator is unknown, or one or more S1-only keys are present without the exact discriminator, do not downgrade to V1. Emit `RUN_ACCEPTANCE_INVARIANT_INVALID` (in addition to any independently applicable V1 diagnostics).
- A malformed/partial S1 envelope is always fail-closed. A caller cannot obtain V1-only acceptance by removing or misspelling the discriminator while retaining S1 claims.

### 10.2 R4 — Expected versus measured object values

The frozen archive inventory is an identity/pairing catalogue; it does not contain authoritative byte-size or content-digest expectations. Do not add synthetic size/SHA fields to the raw inventory or pretend that it pins them.

For each VERIFIED object:
- `expected_size_bytes` and `expected_sha256` are acquisition-request expectations captured in the object evidence before the transfer attempt. They are caller-supplied evidence, not cryptographic facts authenticated by the inventory.
- `measured_size_bytes` and `measured_sha256` are post-transfer measurements.
- The referenced successful TRANSFERRED attempt must carry `response_bytes_received`, `complete_object_sha256`, and `is_complete_object=1`.
- All three evidence layers must agree: expected size = measured size = successful attempt byte count; expected SHA = measured SHA = successful attempt complete SHA.
- Expected and measured values are required for VERIFIED objects; absent, malformed, bool/negative size, partial digest substitution, or any disagreement emits `OBJECT_MEASUREMENT_INVALID` (attempt-specific defects may additionally emit `OBJECT_ATTEMPT_HISTORY_INVALID`).
- The validator verifies internal consistency only. It does not claim that a caller's pre-transfer expectation is independently authenticated or that the inventory contains size/SHA truth.

### 10.3 R5 — Canonical raw CSV fields representation

Each source-row record MUST contain both:
- `raw_fields`: a list of exactly twelve strings, in source-column order;
- `raw_fields_json`: the exact UTF-8 text of a compact JSON array of those twelve strings, serialized with `ensure_ascii=False`, `separators=(",", ":")`, no insignificant whitespace, and no Unicode normalization.

The validator parses `raw_fields_json` as strict JSON (reject duplicate/non-standard constructs where applicable), requires an array of twelve strings, and requires its parsed value to equal `raw_fields`. The exact UTF-8 bytes of `raw_fields_json` must equal the canonical serialization of `raw_fields`. The existing `raw_row_digest` remains SHA-256 of T0ENC1(`T0-RAW-CSV-ROW-V1`, *the twelve raw_fields in order). No CSV parsing or file access is performed by the validator.

### 10.4 R6 — Coverage manifest and duplicate dispositions

The S1 `coverage_manifest` has exactly these required fields:
- `manifest_version`: exact `T0-COVERAGE-MANIFEST-V1`;
- `coverage_ranges`: a non-empty list of unique records, each exactly `{timeframe, start_open_time_ms, end_open_time_ms}`; timeframe is `15m` or `1h`, both endpoints are non-negative aligned integers, and end is inclusive;
- non-negative integer counts (bool is invalid): `expected_object_count`, `expected_pair_count`, `expected_member_count`, `expected_row_count`, `expected_candle_count`, `expected_link_count`;
- `approved_gaps` and `approved_extras`: lists of unique records, each exactly `{timeframe, open_time_ms, reason, evidence_ref}`; timeframe is `15m` or `1h`, open_time_ms is a non-negative aligned integer, and reason/evidence_ref are non-empty strings.

The validator expands every inclusive coverage range into aligned natural-key timestamps. Ranges may not overlap. Each approved gap must fall inside exactly one range and be absent from actual candles; each approved extra must fall outside all ranges and be present. The actual candle natural-key set must equal (all range timestamps minus approved gaps) union approved extras. This exact-set rule prevents unlisted gaps and extras; it does not infer missing periods from row counts alone.

Manifest counts must equal actual collection cardinalities. The fixed S1 archive acceptance counts remain 404 objects, 202 pairs, and 202 verified members. Every approved gap/extra is explicit and unique; an absent/malformed manifest, unlisted discrepancy, duplicate record, or count mismatch emits `RUN_ACCEPTANCE_INVARIANT_INVALID`. Empty gap/extra lists are valid and do not imply an unbounded allowance.

The only link `duplicate_disposition` values are `UNIQUE` and `IDENTICAL_DUPLICATE`. For each candle natural key, normalized candle tuple and value ID must be identical across all linked rows. Sort linked `source_row_id` values by UTF-8 byte sequence: the first is the sole `UNIQUE` representative; every subsequent row is `IDENTICAL_DUPLICATE`. A singleton is `UNIQUE`. Any other value, multiple/missing UNIQUE representatives, or order mismatch emits `CANDLE_PROVENANCE_LINK_INVALID`.

### 10.5 GREEN implementation boundary

The GREEN validator remains a pure in-memory function. It may parse the supplied raw inventory bytes and raw_fields_json strings, compute hashes and validate supplied records. It MUST NOT open any path, inspect archive/member bytes, perform network access, read environment variables, consult wall-clock/randomness, import SQLite, connect to a database, create files, launch processes, or mutate input objects.
