# T0 S1.2 — F2 adapter implementation contract and execution plan

Date: 2026-11-22  
Repository: kenznguyen/btcquant-application  
Branch: main  
Status: **IMPLEMENTED IN PART — SYNTHETIC CI PASS; F2 PARTIAL; INDEPENDENT REVIEW / FREEZE PENDING**

## 1. Authority and boundaries

This document operationalizes the already approved S1.2 design, Amendment A, Amendment B, and owner authorization. It does not create a new data contract or authorize real-data work.

Allowed:
- immutable Python DTOs for the eleven logical relations in design §3.2;
- read-only projection from a caller-supplied SQLite connection containing synthetic disposable schema-v2 fixtures;
- deterministic S3/V1 payload assembly using the existing public validator contract;
- pure in-memory graph validation;
- tests using synthetic values, in-memory SQLite, or explicitly opted-in disposable temporary SQLite only; file-backed tests require a new file under a `t0-staging-v2-*` directory in the system temp root and a `synthetic-staging-*` filename.

Not allowed:
- opening or discovering an existing DB path from the projection adapter; the low-level schema test helper may create a file only under the explicit disposable-path policy, using exclusive creation and rejecting existing files/symlinks;
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


### 4.1 Disposable test database policy (F6)

- The projection API accepts only an already-open caller-owned connection; it has no path parameter and never calls `sqlite3.connect`.
- `connect_staging_database` defaults to `:memory:`. File-backed use requires explicit `allow_disposable_path=True`.
- The explicit file policy accepts only a new, non-symlink file named `synthetic-staging-*` directly under a `t0-staging-v2-*` directory in the system temporary root. It uses exclusive file creation; existing files, symlinks, alternate directories and implicit file paths are rejected.
- This is a synthetic test policy, not a real-data staging builder or permission to access an existing database.

### 4.2 Atomic schema initialization (F7)

- Refuse caller-owned active transactions and non-empty/nonzero-version databases.
- Enable and verify foreign keys before starting the schema transaction.
- Use `BEGIN IMMEDIATE`; create all tables, indexes and the two approved triggers; set `user_version=2`; commit once.
- Any DDL or commit failure rolls back the entire schema and leaves `user_version=0` with no partial schema objects.

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
13. coverage manifest canonical bytes/hash, inclusive range, exact expected/gap/extra set, or six collection count mismatch; candidate snapshot digest must be present and CANDIDATE/VALIDATED events must bind the same value. The exact candidate snapshot digest preimage/serialization is not defined in the approved design, so recomputation is explicitly NOT implemented and requires a separate owner-approved design decision;
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

## 7. Current implementation and exact-SHA verification

- F1 trigger/design contradiction: **DESIGN SYNCHRONIZED**. Owner-approved Amendment B is applied to the physical schema spec; exactly two triggers are fingerprinted and verified.
- F2 DTO/projection/graph implementation: **IMPLEMENTED / SYNTHETIC TESTED**, with candidate snapshot digest recomputation explicitly unresolved.
- F3 cross-record graph checks: **SYNTHETIC TEST MATRIX PASS** for object/attempt/success relation, ZIP/sidecar reciprocity, pair/member/source-row/candle/link edges, failure observations and lifecycle cases.
- F4 run acceptance: **SYNTHETIC TEST PASS** for singleton envelope, initial BUILDING event, event order and canonical coverage manifest.
- F5 identity/digest boundary: **SYNTHETIC TEST PASS** for lower-case hexadecimal identity suffixes and digest grammar at SQL and DTO boundaries.
- F6 guarded disposable path: **SYNTHETIC TEST PASS** for default in-memory use, explicit opt-in, temporary-root/name policy, exclusive creation, existing-file and symlink rejection.
- F7 atomic schema initialization: **SYNTHETIC TEST PASS** for rollback on table/index/trigger DDL failure and commit failure after user_version assignment.
- Latest tested source SHA: `d91c92a813ffe44c4ee786861e5e710654423c26`.
- Exact-SHA CI: run [45010072833](https://github.com/kenznguyen/btcquant-application/actions/runs/45010072833), job `137170245583`, SUCCESS; requested SHA and checked-out SHA match.
- Runtime: CPython 3.13.18 / SQLite 3.45.1 for focused tests; CPython 3.12.16 for full regression.
- Results: importer-core 20/20; S1.2 adapter 43/43; SQLite staging schema 30/30; full `market_data` regression 494/494 PASS.
- No CI artifact was produced.
- Remaining design gap: candidate snapshot digest preimage/serialization is not defined by approved design. Current code checks digest shape/presence and equality between CANDIDATE and VALIDATED events; it does not recompute the snapshot digest.
- Independent review: **NOT RUN**. S1.2: **NOT FROZEN**. B8: **NOT APPROVED**. Real-data staging: **NOT AUTHORIZED**.


## 8. Next steps and gates

1. Freeze the current implementation source SHA only after the final exact-SHA regression.
2. Request an independent review of a byte-for-byte source snapshot. Do not merge the review-only PR; it exists solely to expose the exact source and design to the reviewer.
3. Resolve any Critical/Required review findings on `main`, then rerun exact-SHA CI and request follow-up review.
4. Obtain separate owner approval for the candidate snapshot digest preimage/serialization before implementing recomputation.
5. Only after independent review and owner decisions, prepare a separate approval request for B8, real archive validation, host/path preflight and real-data staging.

All tests remain synthetic. No database, archive, host, workflow, runner, or trading action is performed by this contract.
