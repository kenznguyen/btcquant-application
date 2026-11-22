# T0 S1.2 — Compatibility Amendment A (S12-01..S12-08)

Date: 2026-11-22
Repository: kenznguyen/btcquant-application
Target: main
Status: DESIGN AMENDMENT — IMPLEMENTATION AUTHORIZED ONLY WITHIN OWNER SCOPE; S1.2 FREEZE STILL PENDING

Supersedes the conflicting clauses in `T0_ARCHIVE_STAGING_S1_2_PROVENANCE_IMPORTER_PHYSICAL_SCHEMA_SPEC_2026-11-22.md` only where this amendment states an explicit replacement. S3/V1 contracts and identifiers remain unchanged.

## 1. S12-01 — CHECK expressions must be NULL-safe

SQLite accepts a CHECK expression when it evaluates to NULL. Every VERIFIED/ACCEPTED branch must therefore require each mandatory column with `IS NOT NULL` before equality or ordering checks. The implementation shall use explicit non-null guards, not rely on `CHECK(predicate)` alone.

Required verified object fields: requested_key, expected_size_bytes, expected_sha256, measured_size_bytes, measured_sha256, response_status, local_relative_path, exclusive_create, workflow_run_id, workflow_job_id, workflow_event, trigger_sha, checkout_sha, retrieved_at_utc. Require requested_key=object_key, exclusive_create=1, valid response status, exact SHA grammar and non-negative signed-64-bit sizes.

Required verified pair fields: ZIP/sidecar measured sizes and SHA values, sidecar asserted ZIP SHA, assertion_matches, zip_crc_ok, candidate_member_count, structural_ok. Require each IS NOT NULL before requiring assertion_matches=1, zip_crc_ok=1, candidate_member_count=1, structural_ok=1.

Required verified member fields: member identity/path/size/SHA, encoding, bom_present, newline, delimiter, header_present, header_contract_id, parser_contract_id/source SHA, row count and first/last timestamps. A VERIFIED member must have encoding='UTF-8', bom_present=0, newline='LF', delimiter=',', header_present=1, header_contract_id='T0_ARCHIVE_CSV_HEADER_V1', parser_contract_id='T0_ARCHIVE_CSV_HEADER_V1', data_row_count>0, and non-null first/last timestamps. Headerless or BOM/newline variants not matching this frozen S3 profile are QUARANTINED.

Required accepted source-row fields: exchange='binance', market_type='usdm', symbol='BTCUSDT', timeframe IN ('15m','1h'), non-null aligned open_time_ms, non-null candle_value_id, non-null importer_contract_id='T0_ARCHIVE_IMPORTER_V1', parser/importer SHAs, and no rejection code. Rejected rows must have no candle value and must carry a stable rejection code.

Every OR branch must be explicitly two-valued; tests must attempt NULL in each mandatory field and prove the invalid row is rejected by SQLite.

## 2. S12-02 — Exact attempt vocabulary and complete S3/V1 projection

Physical `acquisition_attempts.outcome` is restricted to the unchanged S3/V1 vocabulary:
- `STARTED`
- `FAILED`
- `TRANSFERRED`
- `UNKNOWN`

Add `failure_subtype` with nullable stable values `HTTP_FAILED`, `TRANSFER_FAILED`, `VALIDATION_FAILED`. For physical FAILED, exactly one failure_subtype and stable failure_code are required; the S3 projection emits outcome='FAILED' and retains subtype only in the physical audit fields/failure_observations. STARTED/TRANSFERRED/UNKNOWN have NULL failure_subtype. Do not map a failure to UNKNOWN unless its actual outcome is indeterminate.

Persist `expected_size_bytes` and `expected_sha256` on each acquisition_attempt at attempt creation. For each attempt, these are immutable request expectations copied from the object evidence as it existed before that attempt. They are projected directly into S3 attempt records; no later object-row value is retroactively substituted. The successful attempt must match object expected and measured size/SHA as required by S3 R4.

Add physical `source_rows.importer_contract_id`, constrained to exact `T0_ARCHIVE_IMPORTER_V1`.

The projection is deterministic and has no lossy inference:

| S3/V1 field | Physical source | Projection |
|---|---|---|
| inventory raw bytes / expected SHA / ID | reconstruction_run | exact stored BLOB and pinned values; no reserialization |
| object inventory identity/key/kind/pairing | archive_objects | direct fields |
| object attempt_count | acquisition_attempts | count all attempts for object, including STARTED/FAILED/UNKNOWN; must be contiguous and non-empty |
| object successful_attempt_id | object_successful_attempt | direct attempt ID after composite FK proves same-object ownership |
| attempt identity/outcome/times/bytes/digest | acquisition_attempts | direct fields; outcome vocabulary already S3-compatible |
| attempt expected size/SHA | acquisition_attempts | direct immutable fields |
| pair member_count | archive_pairs.candidate_member_count | direct alias; NULL is projection failure |
| source raw_fields | source_rows.raw_fields_json | strict parse to list[str] of exactly 12; parsed list must equal canonical compact JSON representation and digest; invalid JSON fails projection |
| source importer_contract_id | source_rows.importer_contract_id | direct exact constant |
| all other S3 collections | corresponding physical table | direct mapping per immutable DTO field names; missing required values fail projection; no defaults |

The adapter must validate all projection cardinalities and required fields before calling S3/V1. It must not fabricate workflow identifiers, attempt outcomes, headers, row ordinals, measurements, parser metadata or source references.

## 3. S12-03 — Headerless member quarantine

The unchanged S3 validator requires header_present=1 and physical_record_ordinal=data_row_ordinal+1. Therefore headerless CSV may be parsed as diagnostic evidence by the parser, but it is always persisted as QUARANTINED and is never eligible for a CANDIDATE or VALIDATED run. No synthetic header or ordinal offset may be inserted. A future headerless acceptance requires a separately versioned S3 contract and owner approval.

## 4. S12-04 — Truthful conflict reason without weakening fail-closed behavior

Importer-core `CONFLICTING` continues to quarantine the entire batch; the adapter may not release candidates or downgrade quarantine.

For each conflicting natural-key group, compare the S3 normalized candle tuple independently using the exact source OHLCV fields plus the frozen availability boundary/kind. If normalized candle tuples differ, record the S3-compatible identity/value conflict reason. If normalized candle tuples are equal but importer-core payloads differ only in source-only columns, record stable physical code `IMPORTER_SOURCE_ONLY_PAYLOAD_CONFLICT`. This physical diagnostic is not an S3 error-code addition and does not claim candle-value conflict. Retain every source row and its exact raw evidence. This conservative core behavior may reduce accepted historical coverage; it must not be bypassed in this increment.

## 5. S12-05 — One-run-per-database

Add `singleton_key INTEGER PRIMARY KEY CHECK(singleton_key=1)` to reconstruction_run and require `singleton_key=1` on its sole row. This prevents a second run envelope. Zero rows remains possible at the schema level; before any evidence insert and at final acceptance, the builder/validator must require exactly one reconstruction_run row and exactly one initial BUILDING event. All evidence tables are scoped to this single run database; no run mixing is permitted.

## 6. S12-06 — B8 remains outside this implementation increment

No acquisition runner, self-hosted runner, workflow dispatch, token, host, filesystem or network acquisition is authorized. The adapter accepts workflow provenance as supplied immutable evidence and validates its shape; it never creates it.

For any future B8 decision, `workflow_job_id` must be the numeric Actions job ID returned by the GitHub Actions jobs API, serialized as a non-empty base-10 string; it is not the workflow YAML job key/context name. The acquisition workflow must later document the minimum read permission/API retrieval path, repository-only runner group, approved ref/SHA, single-job policy, isolated disposable VM, filesystem/network egress boundary, and cleanup/revocation behavior for normal exit, failure, cancellation and host crash. No self-hosted runner on a normal personal workstation is approved by this amendment. B8 remains NOT READY / NOT APPROVED; no fake IDs are permitted in real evidence. Synthetic fixtures may use clearly synthetic identifiers only inside tests.

## 7. S12-07 — Composite constraints and application-only invariants

Add `UNIQUE(object_id, attempt_id)` to acquisition_attempts. Define `object_successful_attempt(object_id, attempt_id)` with composite foreign key `(object_id, attempt_id) REFERENCES acquisition_attempts(object_id, attempt_id)`, plus a foreign key from object_id to archive_objects. This makes cross-object successful-attempt links impossible at the database layer.

The immutable adapter/acceptance validator remains authoritative for these cross-record invariants that are not fully expressible in local CHECK/FK constraints:

1. Exactly one run envelope and valid append-only event sequence/transitions — S1 run acceptance validator.
2. Exact inventory raw bytes, pinned digest/ID, 404 object set, unique keys and reciprocal ZIP/sidecar pairing — S3 S1 inventory validation.
3. Exactly one archive_objects record per inventory item and no extras — S3 object-set validation.
4. Attempt numbers contiguous from 1, attempt IDs recomputed, requested key equals object key, expected values immutable per attempt, exactly one complete TRANSFERRED success for VERIFIED objects — S3 attempt-history validation plus adapter graph validator.
5. Object expected=measured=successful-attempt size/SHA — S3 R4.
6. Pair references correct ZIP and sidecar kinds and reciprocal object pairing; VERIFIED pair has both verified objects, sidecar assertion, CRC/structure and exactly one verified member — S3 pair validation plus adapter graph validator.
7. Member candidate/member IDs recomputed from exact T0ENC1 inputs; VERIFIED member uses supported header profile — S3 member validation.
8. Every parser-success source record represented once with exact raw fields, parser/importer SHAs and ordinal relation; rejected rows have no candle/link — S3 source-row validation.
9. Every accepted row identity/value supported; candle value IDs recomputed from exact canonical tuple; OHLCV, alignment and availability boundary valid — S3 candle validation.
10. Every accepted row has exactly one link, every candle has at least one link, link/source/candle natural keys and value IDs agree — S3 link validation.
11. Exactly one UNIQUE link per candle, selected by smallest source_row_id UTF-8 byte sequence; remaining links IDENTICAL_DUPLICATE — S3 R6.
12. Coverage canonical bytes/hash, inclusive ranges, exact expected/gap/extra sets and six collection counts — S3 R6.
13. Failure observation subjects exist and stable ordinal/code ordering is valid — adapter graph validator.
14. SQLite integrity_check is exactly 'ok', foreign_key_check returns zero rows, foreign_keys=1 on every connection, and no unexpected tables/indexes/triggers/views exist — read-only schema acceptance validator.
15. No unsupported row, orphan, omitted evidence, stale SHA, extra schema object or unapproved coverage exception — adapter graph validator and S3.

A successful PRAGMA foreign_key_check is necessary but never sufficient for graph acceptance.

## 8. S12-08 — Signed 64-bit storage boundary

Before binding any Python integer to SQLite INTEGER, the adapter requires exact type int (bool rejected) and `0 <= value <= 9223372036854775807`, unless the field's contract allows a documented signed range (none currently do). Overflow or wrong type fails closed with stable adapter diagnostic `SQLITE_INTEGER_OUT_OF_RANGE`; no truncation, float conversion or silent quarantine inference. Apply to timestamps, sizes, byte counts, ordinals, counts, sequence numbers and user_version. Tests cover -1, bool, 2^63-1 and 2^63.

## 9. Status and boundaries

- S12-01..S12-05, S12-07 and S12-08: design resolution proposed here; require executable synthetic tests and review before closure.
- S12-06/B8: explicitly NOT APPROVED; no acquisition execution.
- S1.2: NOT FROZEN until revised DDL, adapter contract and review pass.
- Owner authorization permits adapter, synthetic tests and disposable synthetic SQLite staging only. No real archive or sidecar data is in scope.
- Existing S3/V1 APIs, error codes, IDs and semantics remain unchanged.
- No Canonical database, existing database, archive, host, workstation, runner, network, credentials, T1/T2, VPS or trading access.
