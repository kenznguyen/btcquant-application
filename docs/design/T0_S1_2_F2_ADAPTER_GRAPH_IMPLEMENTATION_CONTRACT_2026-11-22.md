# T0 S1.2 — F2 adapter implementation contract and execution plan

Date: 2026-11-22  
Repository: kenznguyen/btcquant-application  
Branch: main  
Status: **IMPLEMENTATION PLAN — NOT IMPLEMENTED / NOT VERIFIED**

## 1. Authority and boundaries

This document operationalizes the already approved S1.2 design, Amendment A, Amendment B, and owner authorization. It does not create a new data contract or authorize real-data work.

Allowed:
- immutable Python DTOs for the eleven logical relations in design §3.2;
- read-only projection from a caller-supplied SQLite connection containing synthetic disposable schema-v2 fixtures;
- deterministic S3/V1 payload assembly using the existing public validator contract;
- pure in-memory graph validation;
- tests using synthetic values, in-memory SQLite, or disposable temporary SQLite only.

Not allowed:
- opening or discovering an existing DB path from the adapter;
- archive/sidecar access, parsing, downloads, host/workstation/runner preflight;
- B8 workflow changes/dispatch or runner installation;
- real-data staging build/persistence, uploads, retention/deletion;
- Canonical T0 operations, MAY-10, REST tail, T1/T2, VPS, credentials, exchange or trading.

## 2. Contract sources and precedence

Implementation must follow, in order:
1. Owner authorization: docs/decisions/T0_S1_2_ADAPTER_SQLITE_STAGING_OWNER_AUTHORIZATION_2026-11-22.md.
2. Physical schema specification §3.2–3.4, §5, §6 and §7.
3. Compatibility Amendment A S12-01..S12-08.
4. Compatibility Amendment B for exactly the two append-only run-event triggers.
5. Existing market_data/archive_provenance_validator.py as the unchanged S3/V1 validation authority.

No change to importer core, S3/V1 field names, public error codes, ID prefixes, or validator behavior is in scope.

## 3. Required immutable DTO inventory

The adapter boundary must define frozen, slotted DTOs for:
- RunEnvelope ← reconstruction_run
- ObjectEvidence ← archive_objects
- AttemptEvidence ← acquisition_attempts
- SuccessfulAttempt ← object_successful_attempt
- PairEvidence ← archive_pairs
- MemberCandidateEvidence ← csv_members
- SourceRowEvidence ← source_rows
- CandleEvidence ← candles
- CandleLinkEvidence ← candle_provenance_links
- FailureObservation ← failure_observations
- RunEvent ← run_events

Existing AttemptRecord, SourceRowRecord and PairRecord may be retained only if their fields and names map losslessly to these canonical records. Avoid parallel DTOs that represent the same physical row.

All persisted integer fields crossing the adapter boundary must use exact Python int validation (bool rejected) and the signed SQLite range [0, 2^63-1]; positive ordinal/sequence fields must additionally reject zero. Required text, enum, digest, identity and nullable-field rules must be explicit and consistent.

## 4. Read-only SQLite projection contract

The projection entry point accepts an already-open sqlite3.Connection supplied by the caller; it must not accept a path, call sqlite3.connect, discover files, or change connection ownership.

Requirements:
- verify schema version, exact schema objects/fingerprint, integrity and foreign keys before reading;
- read one consistent snapshot (read transaction where appropriate);
- select columns explicitly, never SELECT *;
- deterministic ORDER BY clauses for every relation;
- convert sqlite3.Row/tuples into the immutable DTOs without inventing defaults;
- preserve reconstruction_run.inventory_raw_bytes byte-for-byte and raw_fields_json exactly;
- strict-parse raw_fields_json only for the S3 raw_fields projection, requiring twelve strings, duplicate-key rejection, canonical compact JSON equality, and digest validation;
- derive object attempt_count from all attempts; successful_attempt_id only from the physical relation;
- project candidate_member_count to the S3 member_count alias;
- project run.status=CANDIDATE only from the immutable CANDIDATE event being certified; never infer from a mutable status column;
- reject absent or duplicate singleton run envelope, absent/multiple initial BUILDING event, missing required fields, extra unsupported values, or inconsistent cardinalities;
- return an immutable projection result or raise a stable AdapterValidationError; never partially return a payload.

S3/V1 payload top-level collections remain exactly:
inventory, objects, pairs, members, attempts, source_rows, candles, links.

S1 envelope fields remain exactly:
contract_version=T0_PROVENANCE_VALIDATOR_S1_V1, inventory_raw_bytes, inventory_expected_sha256, inventory_expected_id, coverage_manifest, run.

failure_observations and run_events remain physical audit relations and are not added to the S3/V1 public payload.

## 5. Graph validator responsibilities

The pure graph validator must reject, with deterministic stable error codes:
1. zero/multiple run envelope or invalid initial BUILDING event;
2. illegal event sequence, duplicate sequence, non-monotonic timestamps where required, illegal transitions, or non-terminal/contradictory event history;
3. inventory bytes/hash/ID mismatch, duplicate or missing object identities, non-reciprocal ZIP/sidecar pair keys;
4. object set mismatch, duplicate keys/IDs, object identity/inventory disagreement;
5. attempt IDs not recomputed from the frozen S3 identity inputs, non-contiguous attempt numbers, requested-key mismatch, attempt expected values differing from immutable object expectations, invalid outcome/time/failure semantics;
6. successful-attempt relation not resolving to exactly one complete TRANSFERRED attempt owned by the same object; expected/measured/successful-attempt size and SHA mismatch;
7. pair references to wrong object kinds, non-reciprocal pairing, VERIFIED pair with unverified objects, assertion/CRC/structure/member-count mismatch, or not exactly one VERIFIED member;
8. member candidate/member IDs not recomputed from exact T0ENC1 inputs, unsupported header/parser profile, invalid ordinals or incomplete VERIFIED evidence;
9. missing/duplicate source rows, invalid physical/data ordinal relation, raw-field JSON/digest mismatch, parser/importer contract or SHA mismatch, unsupported disposition, or rejected row with candle/link;
10. accepted source-row identity/value mismatch, malformed canonical OHLCV, timeframe alignment/availability boundary error, or candle value ID mismatch;
11. accepted row without exactly one link, link to wrong natural key/value, candle without any link, or wrong duplicate role; exactly one UNIQUE link per candle selected by smallest source_row_id UTF-8 byte sequence;
12. failure observation whose subject is absent, whose ordinal is not contiguous per subject, or whose stable codes/order are invalid;
13. coverage manifest canonical bytes/hash, inclusive range, exact expected/gap/extra set, or six collection count mismatch;
14. unsupported row, orphan, omitted evidence, or extra projection data.

The existing S3/V1 validator remains authoritative for its unchanged public contract and error-code ordering. The graph validator supplements it; it must not silently rewrite payloads to make them pass.

## 6. TDD sequence

Before implementation:
- add focused synthetic tests for each DTO's immutability, strict field validation and lossless mapping;
- add projection tests proving read-only behavior, deterministic ordering, exact raw-byte/raw-JSON preservation, missing-value failure and no implicit connection/path creation;
- add graph tests per invariant above, including cross-object successful-attempt, object expected/measured/successful mismatch, non-reciprocal pair, source-row/candle mismatch, duplicate/missing links, wrong UNIQUE representative, illegal event transition and orphan failure observation;
- ensure tests are RED before implementation, then GREEN after the smallest implementation;
- run focused adapter tests and full market_data regression after changes.

All tests must use synthetic fixtures only. No tests may read the canonical T0 database or actual archive files.

## 7. Current baseline and gate status

- F1 design contradiction: RESOLVED by owner-approved Amendment B commit 37e54c419ea41064aa9c1d2eb68ec50b3489be52.
- F2 complete DTO/projection/graph validator: NOT IMPLEMENTED.
- F3 cross-record acceptance: BLOCKED pending graph validator.
- F4 run acceptance: BLOCKED pending projection/run-event validator.
- F5 identity/digest boundary: OPEN.
- F6 guarded disposable path boundary: OPEN; projection must not open paths.
- F7 atomic schema initialization: OPEN.
- Current reviewed implementation baseline: d7cdea3a467aa0ee2a8b177aaec23fdfea3201ce.
- No new test, CI workflow, or artifact is claimed by this planning document.
- S1.2 remains NOT FROZEN; independent review NOT RUN.

## 8. Next implementation steps

1. Add tests first for DTO coverage and projection API shape, without modifying existing public S3/V1 behavior.
2. Implement canonical DTO set and deterministic read-only row mapping.
3. Implement graph validator and stable issue reporting.
4. Integrate graph validation before returning the S3/V1 payload.
5. Add F1–F7 synthetic regression tests, including atomic initialization and guarded disposable-path policy in their respective later steps.
6. Run exact-SHA CI and full market_data regression; capture exact source SHA, run/job, artifact metadata and logs.
7. Obtain independent review before any separate request for B8, real archive validation, host/path preflight or real-data staging.

No database, archive, host, workflow, runner, or trading action is performed by this plan.
