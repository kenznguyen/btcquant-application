# T0 S1.1 — Provenance & Staging Schema Reconciliation

Date: 2026-11-22  
Repository: `kenznguyen/btcquant-application`  
Branch: `main`  
Status: **S1.1 DESIGN RECONCILIATION — DOCUMENTATION ONLY; AWAITING OWNER ACCEPTANCE**

## 1. Authority, scope and precedence

This document is the S1.1 reconciliation of:
- `docs/design/T0_ARCHIVE_STAGING_S1_PROVENANCE_SCHEMA_FREEZE_2026-11-22.md` (original S1 proposal and design DDL);
- `docs/design/T0_PROVENANCE_VALIDATOR_S1_COVERAGE_AMENDMENT_2026-11-22.md` (S3 validator evidence contract, including R3–R6);
- `docs/design/T0_PROVENANCE_VALIDATOR_INTERFACE_V1_2026-11-22.md` (public validator boundary and stable V1 catalogue);
- the S3 GREEN validator implementation and its exact-SHA evidence.

**Precedence:** this S1.1 document is authoritative for persistence shape and failure semantics where the original S1 DDL or prose conflicts with it. The S3 amendment remains authoritative for the in-memory validator envelope, exact field semantics, stable error codes, digest calculations and acceptance checks. The V1 interface remains authoritative for public function names, DTO and V1 compatibility. This reconciliation does not silently change any S3/V1 identifier or error-code meaning.

**Approved scope:** documentation-only reconciliation and design freeze of provenance/schema semantics, including SQLite compatibility policy. No executable DDL, SQL migration, SQLite import/open/create, tests, workflow, archive access, data operation or runtime change is included.

Immutable exclusions remain in force:
- Canonical T0 is an independent asset; the former Canonical SQLite is LOST. Do not access, recover, replace, migrate, merge, restore, promote or cut over it.
- Any future reconstructed asset is labelled exactly **RECONSTRUCTED — PARTIAL COVERAGE**.
- Exact inventory scope remains 404 objects: 202 ZIP and 202 explicitly paired CHECKSUM_SIDECAR objects.
- MAY-10 excluded. REST tail closed by owner decision; no retrieval/retry/bypass.
- No T1/T2 runtime, Feeder, Scheduler, VPS, PostgreSQL/TimescaleDB activation, deployment, credentials, retention/deletion, cleanup or trading.
- This document does not approve synthetic importer implementation, SQLite implementation, archive sampling/acquisition, staging build or acceptance execution.

## 2. Frozen design decisions

1. Keep `T0_STAGING_SCHEMA_V2`, `PRAGMA user_version=2`, Candle Contract 1.2.0 natural candle primary key, T0ENC1 framing, existing object/pair/member/row/candle/link ID prefixes and S3/V1 contracts. S1.1 resolves persistence semantics without changing the validator contract version.
2. A row in a provenance table records an observation, including incomplete or failed observations. Quarantine is data, not a reason to omit evidence.
3. Evidence fields that cannot truthfully be measured or observed remain SQL NULL. Never synthesize zero, empty string, a fake digest, a fake HTTP status or a fake path to satisfy a constraint.
4. The approved inventory authenticates object identity, exact keys, kind and reciprocal pairing. It does **not** authenticate expected byte sizes or content digests.
5. Expected object size/SHA are pre-transfer request expectations captured by the acquisition caller. Measured size/SHA are post-transfer facts. The three R4 evidence layers must agree for VERIFIED status.
6. Acquisition attempts are append-only child records. A separate one-to-one relation records the successful attempt; no circular foreign key is used.
7. Pair records preserve failed/partial pair evidence. Member evidence records every observed candidate; zero or multiple candidates are representable and cause quarantine, not schema failure.
8. The coverage manifest and its exact canonical bytes/digest are persisted at run level. The validator's S3 R6 exact-set semantics remain unchanged.
9. Database CHECK/FK constraints are necessary but insufficient. The S3 validator is the application-level cross-record acceptance authority; SQLite integrity/FK checks are additional independent gates.
10. No trigger-based mutation or retention/deletion mechanism is introduced. Append-only/immutable behavior is a build-protocol requirement: one writer, no update/delete path, close writers, then read-only validation and immutable evidence.

## 3. Logical persistence model (normative, not executable DDL)

All tables are STRICT tables in the future staging database. The table and field descriptions below define the logical contract; they are not SQL and must not be pasted into a database.

### 3.1 `reconstruction_run` — exactly one run envelope per staging database

Required logical fields:
- `run_id` primary key;
- `inventory_id`, `inventory_blob_sha256`, and exact `inventory_raw_bytes` (BLOB);
- exact label `RECONSTRUCTED — PARTIAL COVERAGE`;
- `parser_contract_id`, `parser_source_sha`, `importer_source_sha`;
- `schema_contract_id = T0_STAGING_SCHEMA_V2`;
- `created_at_utc`;
- `status`;
- `coverage_manifest_json` (exact canonical UTF-8 JSON text under S3 R6), `coverage_manifest_sha256`;
- run-level evidence reference fields for the acquisition/build workflow where available.

Status lifecycle:
- `BUILDING`: evidence is being assembled; never eligible for acceptance.
- `QUARANTINED`: any unapproved failure or invariant violation; terminal for this run. Its database/path is never reused.
- `CANDIDATE`: all writes are closed and the complete evidence envelope is ready for the independent read-only validator. This is the exact status supplied to S3 validation.
- `VALIDATED`: only a later, separately approved acceptance procedure may record this state after the S3 validator, SQLite integrity, FK and source-to-staging checks all pass. The validator itself returns a result only and never changes run status.

The S3 validator receives the parsed manifest mapping and run mapping. Persistence stores the exact canonical manifest text and digest; the caller must verify its digest before parsing and pass the parsed mapping unchanged in meaning. Do not use a row count as a substitute for exact coverage-set validation.

### 3.2 `archive_objects` — exactly 404 inventory object summaries

One row exists for every exact inventory object, including objects never successfully transferred. Stable `object_id` and inventory identity fields are mandatory.

Identity/catalogue fields (NOT NULL):
- `object_id`, `inventory_id`, `inventory_blob_sha256`, `inventory_entry_identity`;
- `object_key` (unique, exact, case-sensitive), `object_kind`, `timeframe`, `partition`, `period`, `paired_object_key`;
- `requested_key` when a request was actually made; if no request occurred, it is NULL and the object remains non-VERIFIED.

Expected pre-transfer fields:
- `expected_size_bytes`, `expected_sha256`. Both are nullable for incomplete/unattempted/quarantined evidence. For a VERIFIED object both are required and must be valid non-negative integer/lowercase 64-hex values. These values are request expectations, not inventory-authenticated truth.

Measured/post-transfer fields (nullable until actually measured):
- `measured_size_bytes`, `measured_sha256`;
- `response_bytes_total`, `response_status`;
- `local_relative_path`, `exclusive_create`, `retrieved_at_utc`;
- retrieval/workflow provenance: `retrieval_source`, `workflow_run_id`, `workflow_job_id`, `workflow_event`, `trigger_sha`, `checkout_sha`;
- `verification_status` and a stable `failure_code`/failure classification.

For VERIFIED status, all measured fields required by S3 R4 must be present; `requested_key = object_key`; the file must have been created exclusively; response status must satisfy the separately frozen acquisition success rule; and exactly one successful TRANSFERRED attempt must be linked. Expected size = measured size = successful attempt `response_bytes_received`; expected SHA = measured SHA = successful attempt `complete_object_sha256`; `is_complete_object=1`. No partial-body digest can satisfy this equality.

For QUARANTINED status, any field not actually observed remains NULL. A failed HTTP response may retain its status and received-byte count without a complete digest/path. An interrupted transfer may retain a partial-body digest separately. Quarantined evidence never qualifies the run for CANDIDATE/VALIDATED.

### 3.3 `acquisition_attempts` — append-only history

One row per actual attempt; zero rows are valid for an unrequested inventory object. Logical fields:
- `attempt_id` primary key, `object_id` FK, `attempt_number`;
- `workflow_run_id`, `workflow_job_id`, `trigger_sha`, `requested_key`;
- `started_at_utc`, nullable `finished_at_utc`;
- `outcome`, nullable `http_status`, nullable `response_bytes_received`;
- nullable `partial_body_sha256`;
- nullable `complete_object_sha256`, `is_complete_object`;
- nullable stable `failure_code`.

Identity is the frozen S1/V1 attempt ID:
`att1:` + SHA-256(T0ENC1(`T0-ACQUISITION-ATTEMPT-V1`, object_id, attempt_number, workflow_run_id, workflow_job_id, trigger_sha, requested_key)).

Constraints/invariants:
- unique (`object_id`, `attempt_number`); attempt numbers are positive, contiguous from 1 and validated in numeric order;
- attempt ID is recomputed from the exact seven identity inputs;
- STARTED has no finish timestamp; terminal outcomes have one;
- TRANSFERRED requires complete-object flag, response byte count and complete-object SHA; non-TRANSFERRED outcomes cannot claim a complete object;
- partial digest is never reused as complete digest;
- UNKNOWN is retained and always fails closed;
- no row is updated/deleted to rewrite history. A correction is a new separately identified evidence event, not an overwrite.

The existing V1/S3 outcome vocabulary is retained; do not introduce aliases or infer an outcome from missing fields.

### 3.4 `object_successful_attempt` — separate successful-attempt relation

One row per VERIFIED object, and no row for an object without a successful transfer:
- `object_id` primary key and FK to `archive_objects`;
- `attempt_id` UNIQUE and FK to `acquisition_attempts`.

This removes the circular-FK problem. Application-level validation MUST additionally prove that the referenced attempt belongs to the same object, has outcome TRANSFERRED, is complete, and matches the object's expected/measured bytes and digest. The relation is inserted only after the attempt record exists. A VERIFIED object has exactly one relation; a QUARANTINED object has none. The S3 payload's `successful_attempt_id` is projected from this relation.

### 3.5 `archive_pairs` — exactly 202 expected ZIP/sidecar relationships

One row for each inventory-defined reciprocal pair, even when either object is missing, failed or quarantined. Mandatory identity fields: `pair_id`, `zip_object_id`, `sidecar_object_id`. The pair references exact object IDs; it never derives pairing by filename suffix.

Observed result fields are nullable when not observed:
- ZIP and sidecar measured size/SHA snapshots;
- parsed sidecar asserted ZIP SHA;
- assertion comparison result;
- ZIP CRC result;
- structural result;
- observed candidate-member count;
- disposition and stable failure code.

Boolean-like results use tri-state semantics: NULL = not measured/not reached; 0 = measured and failed; 1 = measured and passed. No CHECK constraint may force a failed observation to 1. A VERIFIED pair requires both objects VERIFIED, all measurements present, sidecar assertion equal to measured ZIP SHA, CRC and structure true, and exactly one VERIFIED CSV member with no competing candidate. QUARANTINED pair records retain every known failure and may have zero or multiple candidates.

### 3.6 `csv_members` — every observed candidate member

The old `UNIQUE(pair_id)` rule is removed. `pair_id` is a non-unique FK/index because a failed ZIP can have zero or multiple candidate members.

Each observed candidate has a deterministic ID defined as `candidate_id = `cand1:` + SHA-256(T0ENC1(`T0-CSV-MEMBER-CANDIDATE-V1`, pair_id, central_directory_ordinal, exact_member_path_or_NULL))`; the exact path field is nullable and is framed as T0ENC1 NULL when unavailable, so every observed central-directory entry still has a deterministic candidate ID without inventing a path. The central-directory ordinal is the ZIP central-directory entry index (1-based), not a parser iteration order. `member_id` is nullable until exact member path, uncompressed bytes and measured member SHA are available; when available it must equal the frozen `mem1:` identity. Preserve:
- candidate ID, pair ID, central-directory ordinal and exact member path when observed;
- nullable member ID, uncompressed size and member SHA when not measurable;
- encoding, BOM, newline, delimiter, header presence/contract, parser contract/source SHA;
- row count and first/last open time when successfully parsed;
- disposition and stable failure code.

A VERIFIED pair has exactly one VERIFIED member and no disallowed competing candidate. Zero or multiple observed candidates are representable but the pair is QUARANTINED. A malformed/unreadable member is not fabricated into a valid member identity. The S3 validator's member collection must represent all observed candidates and apply its exact VERIFIED cardinality rules.

### 3.7 `source_rows` — one row per CSV data record considered

Required identity/evidence fields:
- `source_row_id`, verified `member_id` FK (and therefore the owning candidate), physical and data ordinals; source rows are created only for a candidate member whose bytes can be decoded and parsed under the approved parser contract;
- `raw_fields_json` exact compact JSON array of twelve source strings and the parsed twelve-string `raw_fields` projection;
- `raw_row_digest`, parser contract/source SHA, importer source SHA;
- nullable normalized natural-key fields and `candle_value_id`;
- disposition `ACCEPTED` or `REJECTED`, plus stable rejection code.

All twelve raw strings and their canonical compact JSON representation are retained for accepted and rejected records. Ordinals are unique/contiguous within a parsed member and obey the S3 header offset rule. Accepted rows have a complete supported natural key/value and no rejection code. Rejected rows have no candle identity/value/link and a stable rejection code. Any rejected/malformed data row quarantines the complete run under the current all-or-nothing acceptance policy. Importer SHA is mandatory for persisted parsed-row evidence; it is not populated before a later approved importer exists.

### 3.8 `candles` — normalized candidate candle values

Keep the existing Candle Contract 1.2.0 natural primary key:
`exchange, market_type, symbol, timeframe, open_time_ms`.

Keep TEXT decimal values and exact fields:
`open, high, low, close, volume, available_at_ms, availability_kind, candle_value_id`.

The exact S3 digest tuple/order is:
`exchange, market_type, symbol, timeframe, open_time_ms, open, high, low, close, volume, available_at_ms, availability_kind`.

No float coercion, exponent notation, NaN/Infinity or lossy decimal normalization. S3 OHLCV, alignment, interval and BAR_CLOSE_BOUNDARY checks remain authoritative. A natural key may map to only one normalized value.

### 3.9 `candle_provenance_links` — source-to-candle graph

Each link contains `link_id`, candle natural key, `source_row_id`, `candle_value_id`, and duplicate disposition. `source_row_id` is unique across links. Every accepted source row has exactly one link; rejected rows have none. Every candle has at least one link. The link's natural key and value ID must equal both its source row and candle. Duplicate representative selection is exactly S3 R6: sort source_row_id by UTF-8 bytes; first is sole UNIQUE, all later rows are IDENTICAL_DUPLICATE. Conflicting values quarantine the run.

## 4. Normative cross-table and lifecycle invariants

The future schema/validator implementation MUST prove all of the following; FK/CHECK constraints alone do not suffice:

1. Exactly one run envelope; exact inventory raw bytes hash to the pinned lowercase SHA and parsed inventory ID.
2. Exactly 404 inventory entries and object summaries: 202 ZIP + 202 sidecars, exact key set, unique keys, reciprocal explicit pairing.
3. Exactly 202 pair summaries, each referencing its exact ZIP and sidecar objects.
4. Every actual attempt references one known object; attempt numbers are contiguous; attempt IDs and outcomes are valid; UNKNOWN/partial transfers fail closed.
5. Every VERIFIED object has exactly one successful-attempt relation; every QUARANTINED object has none; relation and attempt belong to the same object.
6. Every VERIFIED object's expected, measured and successful-attempt byte counts/digests agree exactly under S3 R4.
7. Every VERIFIED pair has both objects VERIFIED, assertion/CRC/structure success and exactly one VERIFIED member. Failed pair evidence is retained, not coerced.
8. All observed member candidates are retained. Pair ID is non-unique in member evidence. Zero/multiple candidates cannot be VERIFIED.
9. Every parsed CSV data row is represented exactly once; no silent skip; raw_fields_json, raw_fields and raw-row digest agree under S3 R5.
10. Accepted/rejected row constraints and header-adjusted ordinals are exact. Rejected rows cannot support candles or links.
11. Every candle digest is recomputed from the full S3 tuple; all OHLCV/timeframe/availability constraints pass.
12. Every accepted row has exactly one matching link; every candle has one or more links; deterministic duplicate disposition follows S3 R6.
13. The persisted coverage manifest has exact canonical bytes/digest and its parsed value satisfies S3 R6 exact timestamp-set semantics and collection cardinality counts.
14. Candidate acceptance requires all 404 objects, 202 pairs, 202 verified members, complete attempt history, no quarantined/rejected evidence, no unapproved gaps/extras/conflicts and all SQLite integrity/FK/source-to-staging checks.
15. Any failure sets the run to QUARANTINED; do not partially accept rows/candles or reuse the same run database/path.

## 5. SQLite STRICT and connection compatibility contract

- Minimum SQLite library version: **3.37.0**, the first SQLite release supporting STRICT tables. Any runtime below this minimum is an unconditional preflight failure.
- Future implementation must pin an exact Python patch version and exact SQLite library version in its runtime/dependency evidence. A floating system SQLite or unpinned runner image is not acceptable. The exact chosen versions are deliberately **not selected by S1.1**; they must be proposed and approved as part of a later SQLite implementation scope, then pinned in that scope's lock/image and exact-SHA CI.
- At process start and on every DB connection, record the Python version and `sqlite3.sqlite_version`; assert the runtime SQLite version equals the approved pin and is >= 3.37.0. Also verify STRICT support with a disposable in-memory capability probe in a later approved test scope; no persistent DB is needed for that probe.
- Foreign keys are connection-local. Every writer and read-only validator connection must set `PRAGMA foreign_keys=ON` before transaction work and read it back as exactly 1. If unavailable/off, abort closed. Run `PRAGMA foreign_key_check` during later read-only acceptance.
- Later acceptance must also run `PRAGMA integrity_check` and require exactly `ok`. These are future implementation requirements, not commands authorized now.
- `PRAGMA user_version=2` remains the schema version. No migration from Canonical or any existing database is defined.

## 6. Failure and immutability semantics

- Missing evidence is NULL or absent in the in-memory payload; it is never filled with a guessed success value.
- QUARANTINED is a valid recorded evidence disposition but invalid for run acceptance.
- Failed attempts, response statuses, partial byte counts/digests, parser failures, pair/member failures and rejected rows are retained.
- A transfer retry creates a new attempt row; it never overwrites an earlier attempt.
- A failed run is terminal and its database/path is not reused. A later attempt/build is a new run with a new run ID and distinct destination approved for that later phase.
- No retention schedule, deletion rule, artifact TTL or cleanup behavior is defined here. All source/evidence preservation and cleanup remain separate owner decisions.
- No mutable runtime service or background job is implied.

## 7. S3/V1 compatibility crosswalk

| Existing contract | S1.1 treatment |
|---|---|
| V1 public functions, DTO and ten error codes | Unchanged |
| S3 eleven appended error codes and fixed order | Unchanged |
| R3 exact V1/S1 dispatch; no silent downgrade | Unchanged |
| R4 expected vs measured vs complete-attempt agreement | Persisted as separate pre-transfer, post-transfer and attempt evidence |
| R5 raw_fields + canonical raw_fields_json + T0ENC1 raw digest | All persisted; no lossy reserialization |
| R6 manifest ranges/gaps/extras/counts/duplicate ordering | Exact manifest stored at run level; S3 exact-set validator unchanged |
| T0ENC1 and stable identity prefixes | Unchanged |
| `T0_STAGING_SCHEMA_V2` / `user_version=2` | Retained; no version bump in S1.1 |
| Existing success-only DDL constraints | Superseded by conditional status-dependent semantics in this reconciliation |

## 8. Blocker disposition

| Blocker | S1.1 result |
|---|---|
| B1 schema conflicts, failed evidence, attempt history, successful-attempt relation, manifest persistence | **RESOLVED AT DESIGN LEVEL** |
| B2 minimum STRICT version and per-connection FK/runtime verification contract | **RESOLVED AT POLICY/CONTRACT LEVEL**; exact runtime pin deferred to later approval |
| B3 real archive format coverage | **NOT VERIFIED**; requires separate exact-scope source inspection/acquisition approval |
| B4 decompression, compression ratio, disk/inode, concurrency, timeout/retry budget | **OPEN / BLOCKING ACQUISITION** |
| B5 actual coverage manifest and archive-derived completeness | **NOT VERIFIED**; requires approved acquisition and offline parse |
| B6 source/evidence retention and artifact TTL | **OPEN / OWNER DECISION REQUIRED** |
| B7 owner-controlled execution destination and preflight | **OPEN / OWNER DECISION REQUIRED** |
| B8 importer implementation/build validation | **NOT IMPLEMENTED / NOT AUTHORIZED** |
| B9 T0 application-foundation independent review | **SEPARATE TRACK**; S1.1 does not change its status |

## 9. Explicit non-authorization

S1.1 does NOT authorize:
- executable SQL/DDL, schema migrations, SQLite in-memory or persistent database operations;
- importer implementation, synthetic importer tests or data build;
- archive/sidecar listing, requests, downloads, decompression, parsing, materialization or sample inspection;
- workflow YAML changes/creation/dispatch, artifacts or CI run;
- Canonical T0, MAY-10, REST tail, T1/T2, Feeder/Scheduler, VPS/runtime, PostgreSQL, deployment or trading;
- retention/deletion/cleanup, credential access or destination preflight.

Each later phase requires a separate explicit owner approval with exact scope and limits.

## 10. Review and status

- S1.1 scope: documentation-only schema/provenance reconciliation.
- S1.1 design disposition: **DRAFT COMMITTED FOR OWNER ACCEPTANCE**; scope approval does not imply acceptance of every design detail.
- Executable DDL/SQLite/importer/archive/data operations: **NOT RUN / NOT AUTHORIZED**.
- Runtime exact-version choice: **DEFERRED** to a separately approved implementation package; minimum 3.37.0 and verification method are frozen.
- Workflow run/job/artifact: **NONE**.
- Source SHA, blob SHA, commit SHA and verification status must be added to the project handoff after the documentation commit is read back.
