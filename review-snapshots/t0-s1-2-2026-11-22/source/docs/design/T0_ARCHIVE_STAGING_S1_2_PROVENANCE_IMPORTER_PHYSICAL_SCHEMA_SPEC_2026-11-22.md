# T0 S1.2 — Provenance / Importer Compatibility & Physical Schema Specification

Date: 2026-11-22  
Repository: kenznguyen/btcquant-application  
Branch: main  
Status: **AMENDED DESIGN AUTHORITY — OWNER-APPROVED AMENDMENTS A/B; BOUNDED IMPLEMENTATION AUTHORIZED; S1.2 FREEZE PENDING**  
Supersedes S1.1 only where this proposal is explicitly accepted. Until then, S1.1 remains the accepted baseline.

## 1. Purpose, authority and scope

S1.2 closes findings B1–B10 from docs/reviews/T0_S1_PERSISTENCE_READINESS_COMPATIBILITY_REVIEW_2026-11-22.md. It specifies exact parser/importer/S3/SQLite mappings, duplicate and coverage semantics, append-only lifecycle, complete proposed SQLite STRICT schema v2, schema fingerprint, and gated implementation sequence.

This specification is the design baseline as amended by owner-approved Amendments A and B and the bounded owner authorization. Implementation and synthetic verification evidence are recorded separately. The design does not authorize real archive access, host preflight, acquisition, real-data staging, Canonical T0 operations or runtime deployment.

### 1.1 Contract precedence

If accepted, precedence is:
1. S1.2 — physical schema, adapter mappings, persistence lifecycle and fingerprint.
2. S1.1 — accepted failure-evidence/logical provenance semantics except explicit S1.2 resolutions.
3. S3 R3–R6 — authoritative in-memory envelope, field semantics, digest calculations, error codes/order and acceptance.
4. Provenance Validator V1 — public API, immutable DTO, V1 error catalogue and side-effect boundary; unchanged.
5. Importer-core — current in-memory behavior unchanged; S1.2 defines only its persistence adapter.
6. Parser T0_ARCHIVE_CSV_HEADER_V1 — current strict all-or-nothing behavior unchanged.

### 1.2 Retained constraints

- Former Canonical SQLite remains LOST; no recovery, replacement, migration, merge, promotion or cutover.
- Any future reconstructed dataset is labelled exactly RECONSTRUCTED — PARTIAL COVERAGE.
- Inventory remains exactly 404 explicitly inventoried objects: 202 ZIP and 202 paired CHECKSUM_SIDECAR.
- MAY-10 and REST tail excluded. T0 independent from T1/T2.
- B4 resource ceilings accepted as policy; enforcement/acquisition not authorized.
- B6 source/staging/private evidence preserved until separate deletion approval. No cleanup/deletion.
- B7 Option A: owner-controlled encrypted personal workstation, manual/on-demand only. Exact device/path and preflight pending.
- SQLite STRICT minimum 3.37.0. Exact Python patch and SQLite library versions are not selected; separate implementation approval required.
- Retain T0_STAGING_SCHEMA_V2, PRAGMA user_version=2, T0ENC1, stable identity prefixes, Candle Contract 1.2.0 and S3/V1 identifiers.

## 2. B1–B10 decisions

### B1 — Canonical market type

Persisted archive candles use exactly exchange=binance, market_type=usdm, symbol=BTCUSDT, timeframe=15m or 1h. Importer-core remains generic and accepts explicit caller identity. Its synthetic fixture token usd_m is not a persisted alias. The future adapter MUST reject usd_m for this archive profile and MUST NOT silently rewrite it. It supplies usdm only from explicit approved run configuration; never infer identity from filename/path.

### B2 — Source-row equality versus candle-value equality

Two comparisons are distinct:
- Source-row identity/payload: exact member + physical ordinal + T0ENC1 raw-row digest. Every row remains independently recorded.
- Candle identity/value: natural key (exchange, market_type, symbol, timeframe, open_time_ms) plus S3 normalized candle tuple and candle_value_id.

Only the S3 normalized tuple determines candle duplicate/conflict. Source-only fields source_close_time_ms, quote_asset_volume, number_of_trades, taker-buy fields and ignore remain in raw provenance but do not participate in candle_value_id or candle duplicate equality.

Same natural key + same normalized tuple: one candle, all source rows retained/linked; link roles UNIQUE/IDENTICAL_DUPLICATE. Same natural key + different normalized tuple: whole run QUARANTINED; no candle/link for that identity. Differences only in source-only fields do not create candle conflicts. No first/last-write-wins.

### B3 — Exact row outcome mapping

| Importer-core outcome | source_rows | candles | links | Run effect |
|---|---|---|---|---|
| ACCEPTED | ACCEPTED | one normalized candidate | one UNIQUE after S3 representative selection | continue |
| IDENTICAL_DUPLICATE | ACCEPTED | no second candle | IDENTICAL_DUPLICATE | continue |
| REJECTED | REJECTED with raw fields and stable rejection code | none | none | QUARANTINED |
| CONFLICTING | every involved row retained as REJECTED with CANDLE_IDENTITY_CONFLICT | none | none | whole run QUARANTINED |

Core accepted_count counts unique candidates, not accepted source rows. Persisted accepted source rows = accepted_count + identical_duplicate_count. Core conflicting_count maps to rejected source rows with the stable conflict reason, and the batch quarantine flag remains authoritative. For each candle natural key, S3 R6 sorts source_row_id by UTF-8 bytes; smallest receives the sole UNIQUE role, all others IDENTICAL_DUPLICATE. Input order is not the representative rule.

### B4 — Coverage interval conversion

Importer-core uses half-open [start,end); S3 R6 uses inclusive end. For interval Δ and a non-empty importer range:

~~~text
S3.start_open_time_ms = importer.start_open_time_ms
S3.end_open_time_ms   = importer.end_open_time_ms - Δ
~~~

Both endpoints must be non-negative aligned integers, end > start, and exclusive end aligned. Empty/invalid ranges fail closed. Adapter verifies expansion of the inclusive S3 range equals importer expected_open_times exactly. One-candle range has end_inclusive=start. Missing times become approved_gaps only with caller-supplied reason and evidence_ref; out-of-range times become approved_extras only with caller-supplied reason and evidence_ref. No invented approvals.

### B5 — Stable provenance mapping

Importer source_ref is opaque diagnostic context only; never a database key. For a verified member:
- member_id derives from pair_id, exact member path and raw 32-byte member SHA using frozen mem1 formula.
- importer row_ordinal is data_row_ordinal (one-based, header excluded).
- physical_record_ordinal = data_row_ordinal + 1 when approved header present; otherwise equal.
- raw_row_digest = SHA256(T0ENC1(T0-RAW-CSV-ROW-V1, exact 12 raw fields)).
- source_row_id = row1: + SHA256(T0ENC1(T0-SOURCE-ROW-V1, member_id, physical ordinal, raw digest raw 32 bytes)).
- candle_value_id recomputed from exact S3 normalized tuple.
- link_id recomputed from natural key, source_row_id and final duplicate role.

All identities content-derived. SQLite rowid/autoincrement, path-derived IDs and import order are prohibited as provenance identities.

### B6 — Parser failure

Current T0_ARCHIVE_CSV_HEADER_V1 parser is all-or-nothing: success returns complete immutable ArchiveCsvDocument; malformed CSV or semantically invalid row raises ArchiveCsvError and returns no partial rows. S1.2 does not alter this implementation or invent rejected-row DTOs.

- Successful parse: persist each returned data row exactly once; importer mapping applies.
- Parser exception: no partial source_rows fabricated. Candidate member is QUARANTINED; append stable failure_observations for member/run. Preserve source archive/member under accepted retention policy. Do not store exception prose as a stable code.
- CSV framing/encoding failure that prevents trustworthy boundaries is member-level quarantine.
- Future typed rejected-row parser output requires a separately versioned parser contract and implementation approval; it must include exact 12 decoded strings, both ordinals and stable rejection code.
- Current parser cannot provide row-level raw rejected evidence for failed documents; this limitation is explicit and such a run cannot become CANDIDATE/VALIDATED.

### B7 — Append-only run lifecycle

Remove mutable reconstruction_run.status. Derive state from append-only run_events:
- BUILDING — first event.
- CANDIDATE — writers closed and complete evidence ready for S3.
- QUARANTINED — terminal from BUILDING or CANDIDATE.
- VALIDATED — terminal after S3, SQLite integrity/FK and source-to-staging checks pass.

No event row is updated/deleted. Event sequence and transitions are checked by application validator. VALIDATED binds candidate snapshot SHA and validator payload SHA. S3 V1 run.status=CANDIDATE is projected from the immutable CANDIDATE event being certified; final state is derived from latest event. Final read-only verification replays that candidate projection and checks both digests.

### B8 — Manual execution provenance

**Proposed resolution:** acquisition, if separately approved, is initiated manually using workflow_dispatch and runs on a manually launched ephemeral self-hosted GitHub Actions runner on the owner-controlled encrypted workstation (B7 Option A). No persistent runner service, systemd, cron, autostart or schedule. Operator manually starts runner and dispatches workflow; runner stopped/removed after run.

This provides truthful workflow_run_id, workflow_job_id, workflow_event=workflow_dispatch, trigger_sha and checkout_sha, preserving V1 derive_attempt_id inputs and att1 identity. Workstation remains data destination; GitHub is orchestration/provenance control plane, not archive vault.

This proposal does not authorize host access, runner registration/installation, workflow changes/dispatch, archive requests or preflight. If owner instead requires direct local Python execution, S3/V1 cannot truthfully validate it with mandatory workflow IDs; that alternative requires separately versioned S3/V2 execution-context contract and new attempt ID prefix. Fake workflow IDs/placeholders prohibited.

### B9 — Physical schema and fingerprint

The DDL in §4 is the complete proposed schema candidate, not executable authorization. Retain schema ID/user_version 2. Exact runtime pins remain separately gated.

### B10 — Multiple failures

Append-only failure_observations stores zero or more diagnostics per evidence subject. Existing singular failure_code fields in S3 payload projections contain the deterministic primary code. All known failures are retained in failure_observations with stable ordinal order. No free-form response bodies, secrets, tokens or arbitrary exception text. No new S3/V1 code is added.

## 3. Exact component mapping

### 3.1 Parser → importer-core

Parser success output:
- ArchiveCsvDocument.rows, header_present, header_fields, data_row_count.
- Every ArchiveKlineRow.raw_fields is exactly 12 strings after CSV unquoting, without trimming or Unicode normalization.
- Decimal fields preserve exact parsed Decimal value; source-only columns remain in DTO.

Parser failure: ArchiveCsvError → member QUARANTINED + stable failure observation; no partial source rows.

Importer call uses explicit identity arguments. Persisted archive profile is binance/usdm/BTCUSDT/15m|1h; source_ref diagnostic only. calculate_coverage remains half-open and factual only.

**Conservative compatibility rule:** current importer-core compares more fields than S3 candle-value equality. A core quarantined batch remains quarantined; adapter MUST NOT downgrade it even if S3 tuple would match. For non-quarantined batches, adapter retains every row and derives persisted candle/link roles using S3 normalized tuple. Core implementation is not changed.

### 3.2 Immutable adapter DTO projection

| Logical DTO | Required data | SQLite table |
|---|---|---|
| RunEnvelope | run_id, inventory bytes/id/hash, schema ID/fingerprint, parser/importer SHAs, coverage manifest/digest, created_at | reconstruction_run |
| ObjectEvidence | inventory identity, key/kind/pair key, expected/measured evidence, request/response/path/status | archive_objects |
| AttemptEvidence | att1 ID, object/attempt number, workflow IDs/event/SHAs, times/outcome/bytes/digests/failure | acquisition_attempts |
| SuccessfulAttempt | object_id, transferred attempt_id | object_successful_attempt |
| PairEvidence | pair/object IDs, measurements, assertion, tri-state CRC/structure/member count/disposition | archive_pairs |
| MemberCandidateEvidence | candidate/member IDs, pair, central ordinal, path/size/SHA, parser metadata, row bounds/count | csv_members |
| SourceRowEvidence | row/member IDs, ordinals, raw fields/JSON/digest, parser/importer SHAs, normalized identity/value, disposition | source_rows |
| CandleEvidence | natural key, canonical OHLCV strings, available_at, kind, value ID | candles |
| CandleLinkEvidence | link ID, natural key, source row, value ID, duplicate role | candle_provenance_links |
| FailureObservation | subject kind/id, ordinal, stable failure/detail code, time, optional evidence digest | failure_observations |
| RunEvent | run ID, sequence, event/time/reason, candidate snapshot SHA, validator payload SHA | run_events |

Adapter may not infer missing data, synthesize success, create workflow IDs, derive pairing from filenames or infer identity from paths. It recomputes all stable IDs/digests before persistence and sorts records deterministically.

### 3.3 S3/V1 payload projection

Read-only DB projection produces unchanged V1 keys: inventory, objects, pairs, members, attempts, source_rows, candles, links. S1 envelope adds exact contract_version=T0_PROVENANCE_VALIDATOR_S1_V1, inventory_raw_bytes, pinned inventory_expected_sha256, inventory_expected_id, parsed coverage_manifest and run mapping. run.status is CANDIDATE from immutable candidate event; schema_contract_id=T0_STAGING_SCHEMA_V2.

Preserve exact raw inventory bytes and exact raw_fields_json; do not reserialize before digest verification. No V1/S3 field, API or error code is added, removed or renamed. failure_observations is an additional physical audit relation, not a validator API change.

### 3.4 Mapping matrix

| Property | Parser | Importer-core | S3/V1 | S1.2 adapter/DB | Disposition |
|---|---|---|---|---|---|
| market_type | not supplied | explicit input | exact usdm | enforce binance/usdm/BTCUSDT | B1 |
| raw strings | 12 source strings | retained | R5 raw_fields/JSON/T0ENC1 | persist exact | compatible |
| duplicate | no cross-row decision | includes source-only fields | normalized tuple | core conflict remains quarantine; S3 tuple assigns link roles | conservative |
| row disposition | successful rows only | accepted/duplicate/conflict/rejected | accepted/rejected + link roles | B3 mapping | resolved |
| coverage | timeframe/rows | half-open | inclusive | end_exclusive - interval; exact expansion | B4 |
| provenance | data ordinal/raw fields | opaque ref/ordinal | stable IDs/digests | derive from verified member + physical ordinal | B5 |
| parse failure | exception/no partial rows | not called | quarantined fails | member quarantine | B6 limitation |
| run state | n/a | batch quarantine flag | requires CANDIDATE | append-only events | B7 |
| acquisition | n/a | n/a | workflow IDs mandatory | manual workflow_dispatch ephemeral runner | B8 proposed |
| physical schema | n/a | n/a | logical checks | §4 DDL | B9 |
| multiple errors | exception | batch outcome | stable code tuple | failure_observations | B10 |

## 4. Proposed SQLite schema v2 — DDL candidate

### 4.1 Preconditions

SQLite >= 3.37.0 and exactly equals a later approved pin; exact Python patch pinned separately. Every connection sets PRAGMA foreign_keys=ON before transactions and reads back 1. All tables STRICT; decimals TEXT; no REAL. No AUTOINCREMENT, rowid identities, views, virtual tables or generated columns. Exactly two append-only lifecycle triggers are required as defined in §4.2; no other triggers are permitted. No ON DELETE CASCADE. No migration. DDL applies only to a newly approved staging DB, never Canonical or any existing DB. Set foreign_keys=ON before beginning the transaction. Apply all tables, indexes and triggers, set user_version=2, and COMMIT atomically; on any failure ROLLBACK the entire initialization.

### 4.2 Complete DDL — owner-amended physical schema v2

~~~sql
-- Exact TABLE_DDL statements, in execution and fingerprint order.

CREATE TABLE reconstruction_run (
      singleton_key INTEGER PRIMARY KEY CHECK(singleton_key=1),
      run_id TEXT NOT NULL UNIQUE CHECK(length(run_id)=69 AND substr(run_id,1,5)='run1:' AND substr(run_id,6) NOT GLOB '*[^0-9a-f]*'),
      inventory_id TEXT NOT NULL CHECK(length(inventory_id)=69 AND substr(inventory_id,1,5)='inv1:' AND substr(inventory_id,6) NOT GLOB '*[^0-9a-f]*'),
      inventory_blob_sha256 TEXT NOT NULL CHECK(length(inventory_blob_sha256)=64 AND inventory_blob_sha256 NOT GLOB '*[^0-9a-f]*'),
      inventory_raw_bytes BLOB NOT NULL,
      label TEXT NOT NULL CHECK(label='RECONSTRUCTED — PARTIAL COVERAGE'),
      parser_contract_id TEXT NOT NULL CHECK(parser_contract_id='T0_ARCHIVE_CSV_HEADER_V1'),
      parser_source_sha TEXT NOT NULL CHECK(length(parser_source_sha)=40 AND parser_source_sha NOT GLOB '*[^0-9a-f]*'),
      importer_source_sha TEXT NOT NULL CHECK(length(importer_source_sha)=40 AND importer_source_sha NOT GLOB '*[^0-9a-f]*'),
      schema_contract_id TEXT NOT NULL CHECK(schema_contract_id='T0_STAGING_SCHEMA_V2'),
      schema_fingerprint_sha256 TEXT NOT NULL CHECK(length(schema_fingerprint_sha256)=64 AND schema_fingerprint_sha256 NOT GLOB '*[^0-9a-f]*'),
      created_at_utc TEXT NOT NULL,
      coverage_manifest_json TEXT NOT NULL,
      coverage_manifest_sha256 TEXT NOT NULL CHECK(length(coverage_manifest_sha256)=64 AND coverage_manifest_sha256 NOT GLOB '*[^0-9a-f]*')
    ) STRICT;

CREATE TABLE run_events (
      run_id TEXT NOT NULL REFERENCES reconstruction_run(run_id),
      event_seq INTEGER NOT NULL CHECK(event_seq>0),
      event_type TEXT NOT NULL CHECK(event_type IN ('BUILDING','CANDIDATE','QUARANTINED','VALIDATED')),
      occurred_at_utc TEXT NOT NULL,
      reason_code TEXT,
      candidate_snapshot_sha256 TEXT CHECK(candidate_snapshot_sha256 IS NULL OR (candidate_snapshot_sha256 IS NOT NULL AND length(candidate_snapshot_sha256)=64 AND candidate_snapshot_sha256 NOT GLOB '*[^0-9a-f]*')),
      validator_payload_sha256 TEXT CHECK(validator_payload_sha256 IS NULL OR (validator_payload_sha256 IS NOT NULL AND length(validator_payload_sha256)=64 AND validator_payload_sha256 NOT GLOB '*[^0-9a-f]*')),
      PRIMARY KEY(run_id,event_seq),
      CHECK(event_type NOT IN ('CANDIDATE','VALIDATED') OR candidate_snapshot_sha256 IS NOT NULL),
      CHECK(event_type<>'VALIDATED' OR validator_payload_sha256 IS NOT NULL)
    ) STRICT;

CREATE TABLE archive_objects (
      object_id TEXT PRIMARY KEY CHECK(length(object_id)=69 AND substr(object_id,1,5)='obj1:' AND substr(object_id,6) NOT GLOB '*[^0-9a-f]*'),
      inventory_id TEXT NOT NULL CHECK(length(inventory_id)=69 AND substr(inventory_id,1,5)='inv1:' AND substr(inventory_id,6) NOT GLOB '*[^0-9a-f]*'),
      inventory_blob_sha256 TEXT NOT NULL CHECK(length(inventory_blob_sha256)=64 AND inventory_blob_sha256 NOT GLOB '*[^0-9a-f]*'),
      inventory_entry_identity TEXT NOT NULL,
      object_key TEXT NOT NULL UNIQUE,
      object_kind TEXT NOT NULL CHECK(object_kind IN ('ZIP','CHECKSUM_SIDECAR')),
      timeframe TEXT NOT NULL CHECK(timeframe IN ('15m','1h')),
      partition TEXT NOT NULL,
      period TEXT NOT NULL,
      paired_object_key TEXT NOT NULL,
      requested_key TEXT,
      expected_size_bytes INTEGER CHECK(expected_size_bytes IS NULL OR expected_size_bytes>=0),
      expected_sha256 TEXT CHECK(expected_sha256 IS NULL OR (length(expected_sha256)=64 AND expected_sha256 NOT GLOB '*[^0-9a-f]*')),
      measured_size_bytes INTEGER CHECK(measured_size_bytes IS NULL OR measured_size_bytes>=0),
      measured_sha256 TEXT CHECK(measured_sha256 IS NULL OR (length(measured_sha256)=64 AND measured_sha256 NOT GLOB '*[^0-9a-f]*')),
      response_bytes_total INTEGER NOT NULL CHECK(response_bytes_total>=0),
      response_status INTEGER CHECK(response_status IS NULL OR response_status BETWEEN 100 AND 599),
      local_relative_path TEXT,
      exclusive_create INTEGER CHECK(exclusive_create IS NULL OR exclusive_create IN (0,1)),
      retrieval_source TEXT,
      workflow_run_id TEXT,
      workflow_job_id TEXT,
      workflow_event TEXT,
      trigger_sha TEXT CHECK(trigger_sha IS NULL OR (length(trigger_sha)=40 AND trigger_sha NOT GLOB '*[^0-9a-f]*')),
      checkout_sha TEXT CHECK(checkout_sha IS NULL OR (length(checkout_sha)=40 AND checkout_sha NOT GLOB '*[^0-9a-f]*')),
      retrieved_at_utc TEXT,
      verification_status TEXT NOT NULL CHECK(verification_status IN ('VERIFIED','QUARANTINED')),
      failure_code TEXT,
      CHECK(requested_key IS NULL OR requested_key=object_key),
      CHECK(
        (verification_status='VERIFIED'
         AND requested_key IS NOT NULL AND requested_key=object_key
         AND expected_size_bytes IS NOT NULL AND expected_sha256 IS NOT NULL
         AND measured_size_bytes IS NOT NULL AND measured_sha256 IS NOT NULL
         AND response_status IS NOT NULL AND local_relative_path IS NOT NULL
         AND exclusive_create IS NOT NULL AND exclusive_create=1
         AND workflow_run_id IS NOT NULL AND workflow_job_id IS NOT NULL
         AND workflow_event IS NOT NULL AND trigger_sha IS NOT NULL
         AND checkout_sha IS NOT NULL AND retrieved_at_utc IS NOT NULL
         AND failure_code IS NULL)
        OR (verification_status='QUARANTINED' AND failure_code IS NOT NULL)
      )
    ) STRICT;

CREATE TABLE acquisition_attempts (
      attempt_id TEXT PRIMARY KEY CHECK(length(attempt_id)=69 AND substr(attempt_id,1,5)='att1:' AND substr(attempt_id,6) NOT GLOB '*[^0-9a-f]*'),
      object_id TEXT NOT NULL REFERENCES archive_objects(object_id),
      attempt_number INTEGER NOT NULL CHECK(attempt_number>0),
      workflow_run_id TEXT NOT NULL,
      workflow_job_id TEXT NOT NULL,
      workflow_event TEXT NOT NULL CHECK(workflow_event='workflow_dispatch'),
      trigger_sha TEXT NOT NULL CHECK(length(trigger_sha)=40 AND trigger_sha NOT GLOB '*[^0-9a-f]*'),
      checkout_sha TEXT NOT NULL CHECK(length(checkout_sha)=40 AND checkout_sha NOT GLOB '*[^0-9a-f]*'),
      requested_key TEXT NOT NULL,
      expected_size_bytes INTEGER NOT NULL CHECK(expected_size_bytes>=0),
      expected_sha256 TEXT NOT NULL CHECK(length(expected_sha256)=64 AND expected_sha256 NOT GLOB '*[^0-9a-f]*'),
      started_at_utc TEXT NOT NULL,
      finished_at_utc TEXT,
      outcome TEXT NOT NULL CHECK(outcome IN ('STARTED','FAILED','TRANSFERRED','UNKNOWN')),
      failure_subtype TEXT CHECK(failure_subtype IS NULL OR failure_subtype IN ('HTTP_FAILED','TRANSFER_FAILED','VALIDATION_FAILED')),
      response_status INTEGER,
      response_bytes_received INTEGER CHECK(response_bytes_received IS NULL OR response_bytes_received>=0),
      is_complete_object INTEGER NOT NULL CHECK(is_complete_object IN (0,1)),
      partial_body_sha256 TEXT CHECK(partial_body_sha256 IS NULL OR (length(partial_body_sha256)=64 AND partial_body_sha256 NOT GLOB '*[^0-9a-f]*')),
      complete_object_sha256 TEXT CHECK(complete_object_sha256 IS NULL OR (length(complete_object_sha256)=64 AND complete_object_sha256 NOT GLOB '*[^0-9a-f]*')),
      failure_code TEXT,
      UNIQUE(object_id,attempt_number),
      UNIQUE(object_id,attempt_id),
      CHECK((outcome='STARTED' AND finished_at_utc IS NULL AND is_complete_object=0 AND failure_subtype IS NULL AND failure_code IS NULL)
         OR (outcome='FAILED' AND finished_at_utc IS NOT NULL AND is_complete_object=0 AND failure_subtype IS NOT NULL AND failure_code IS NOT NULL)
         OR (outcome='TRANSFERRED' AND finished_at_utc IS NOT NULL AND is_complete_object=1 AND failure_subtype IS NULL AND response_bytes_received IS NOT NULL AND complete_object_sha256 IS NOT NULL AND failure_code IS NULL)
         OR (outcome='UNKNOWN' AND finished_at_utc IS NOT NULL AND is_complete_object=0 AND failure_subtype IS NULL))
    ) STRICT;

CREATE TABLE object_successful_attempt (
      object_id TEXT PRIMARY KEY REFERENCES archive_objects(object_id),
      attempt_id TEXT NOT NULL UNIQUE,
      FOREIGN KEY(object_id,attempt_id) REFERENCES acquisition_attempts(object_id,attempt_id)
    ) STRICT;

CREATE TABLE archive_pairs (
      pair_id TEXT PRIMARY KEY CHECK(length(pair_id)=70 AND substr(pair_id,1,6)='pair1:' AND substr(pair_id,7) NOT GLOB '*[^0-9a-f]*'),
      zip_object_id TEXT NOT NULL UNIQUE REFERENCES archive_objects(object_id),
      sidecar_object_id TEXT NOT NULL UNIQUE REFERENCES archive_objects(object_id),
      zip_size_bytes INTEGER CHECK(zip_size_bytes IS NULL OR zip_size_bytes>=0),
      zip_sha256 TEXT CHECK(zip_sha256 IS NULL OR (length(zip_sha256)=64 AND zip_sha256 NOT GLOB '*[^0-9a-f]*')),
      sidecar_size_bytes INTEGER CHECK(sidecar_size_bytes IS NULL OR sidecar_size_bytes>=0),
      sidecar_sha256 TEXT CHECK(sidecar_sha256 IS NULL OR (length(sidecar_sha256)=64 AND sidecar_sha256 NOT GLOB '*[^0-9a-f]*')),
      sidecar_asserted_zip_sha256 TEXT CHECK(sidecar_asserted_zip_sha256 IS NULL OR (length(sidecar_asserted_zip_sha256)=64 AND sidecar_asserted_zip_sha256 NOT GLOB '*[^0-9a-f]*')),
      assertion_matches INTEGER CHECK(assertion_matches IS NULL OR assertion_matches IN (0,1)),
      zip_crc_ok INTEGER CHECK(zip_crc_ok IS NULL OR zip_crc_ok IN (0,1)),
      candidate_member_count INTEGER CHECK(candidate_member_count IS NULL OR candidate_member_count>=0),
      structural_ok INTEGER CHECK(structural_ok IS NULL OR structural_ok IN (0,1)),
      disposition TEXT NOT NULL CHECK(disposition IN ('VERIFIED','QUARANTINED')),
      failure_code TEXT,
      CHECK((disposition='VERIFIED'
             AND zip_size_bytes IS NOT NULL AND zip_sha256 IS NOT NULL
             AND sidecar_size_bytes IS NOT NULL AND sidecar_sha256 IS NOT NULL
             AND sidecar_asserted_zip_sha256 IS NOT NULL
             AND assertion_matches IS NOT NULL AND assertion_matches=1
             AND zip_crc_ok IS NOT NULL AND zip_crc_ok=1
             AND candidate_member_count IS NOT NULL AND candidate_member_count=1
             AND structural_ok IS NOT NULL AND structural_ok=1
             AND failure_code IS NULL)
         OR (disposition='QUARANTINED' AND failure_code IS NOT NULL)),
      CHECK(zip_object_id<>sidecar_object_id)
    ) STRICT;

CREATE TABLE csv_members (
      candidate_id TEXT PRIMARY KEY CHECK(length(candidate_id)=70 AND substr(candidate_id,1,6)='cand1:' AND substr(candidate_id,7) NOT GLOB '*[^0-9a-f]*'),
      member_id TEXT UNIQUE CHECK(member_id IS NULL OR (length(member_id)=69 AND substr(member_id,1,5)='mem1:' AND substr(member_id,6) NOT GLOB '*[^0-9a-f]*')),
      pair_id TEXT NOT NULL REFERENCES archive_pairs(pair_id),
      central_directory_ordinal INTEGER NOT NULL CHECK(central_directory_ordinal>0),
      member_path TEXT,
      member_size_bytes INTEGER CHECK(member_size_bytes IS NULL OR member_size_bytes>=0),
      member_sha256 TEXT CHECK(member_sha256 IS NULL OR (length(member_sha256)=64 AND member_sha256 NOT GLOB '*[^0-9a-f]*')),
      encoding TEXT,
      bom_present INTEGER CHECK(bom_present IS NULL OR bom_present IN (0,1)),
      newline TEXT,
      delimiter TEXT,
      header_present INTEGER CHECK(header_present IS NULL OR header_present IN (0,1)),
      header_contract_id TEXT,
      parser_contract_id TEXT,
      parser_source_sha TEXT CHECK(parser_source_sha IS NULL OR (length(parser_source_sha)=40 AND parser_source_sha NOT GLOB '*[^0-9a-f]*')),
      data_row_count INTEGER CHECK(data_row_count IS NULL OR data_row_count>=0),
      first_open_time_ms INTEGER CHECK(first_open_time_ms IS NULL OR first_open_time_ms>=0),
      last_open_time_ms INTEGER CHECK(last_open_time_ms IS NULL OR last_open_time_ms>=0),
      disposition TEXT NOT NULL CHECK(disposition IN ('VERIFIED','QUARANTINED')),
      failure_code TEXT,
      UNIQUE(pair_id,central_directory_ordinal),
      CHECK((member_id IS NOT NULL AND member_path IS NOT NULL AND member_size_bytes IS NOT NULL AND member_sha256 IS NOT NULL) OR member_id IS NULL),
      CHECK((disposition='VERIFIED'
             AND member_id IS NOT NULL AND member_path IS NOT NULL
             AND member_size_bytes IS NOT NULL AND member_sha256 IS NOT NULL
             AND encoding IS NOT NULL AND encoding='UTF-8'
             AND bom_present IS NOT NULL AND bom_present=0
             AND newline IS NOT NULL AND newline='LF'
             AND delimiter IS NOT NULL AND delimiter=','
             AND header_present IS NOT NULL AND header_present=1
             AND header_contract_id IS NOT NULL AND header_contract_id='T0_ARCHIVE_CSV_HEADER_V1'
             AND parser_contract_id IS NOT NULL AND parser_contract_id='T0_ARCHIVE_CSV_HEADER_V1'
             AND parser_source_sha IS NOT NULL AND data_row_count IS NOT NULL AND data_row_count>0
             AND first_open_time_ms IS NOT NULL AND last_open_time_ms IS NOT NULL
             AND failure_code IS NULL)
         OR (disposition='QUARANTINED' AND failure_code IS NOT NULL)),
      CHECK((header_present=1 AND header_contract_id='T0_ARCHIVE_CSV_HEADER_V1')
         OR (header_present=0 AND header_contract_id IS NULL)
         OR (header_present IS NULL AND header_contract_id IS NULL)),
      CHECK(data_row_count IS NULL OR
         (data_row_count=0 AND first_open_time_ms IS NULL AND last_open_time_ms IS NULL)
         OR (data_row_count>0 AND first_open_time_ms IS NOT NULL AND last_open_time_ms IS NOT NULL))
    ) STRICT;

CREATE TABLE source_rows (
      source_row_id TEXT PRIMARY KEY CHECK(length(source_row_id)=69 AND substr(source_row_id,1,5)='row1:' AND substr(source_row_id,6) NOT GLOB '*[^0-9a-f]*'),
      member_id TEXT NOT NULL REFERENCES csv_members(member_id),
      physical_record_ordinal INTEGER NOT NULL CHECK(physical_record_ordinal>0),
      data_row_ordinal INTEGER NOT NULL CHECK(data_row_ordinal>0),
      raw_fields_json TEXT NOT NULL,
      raw_row_digest TEXT NOT NULL CHECK(length(raw_row_digest)=64 AND raw_row_digest NOT GLOB '*[^0-9a-f]*'),
      parser_contract_id TEXT NOT NULL CHECK(parser_contract_id='T0_ARCHIVE_CSV_HEADER_V1'),
      parser_source_sha TEXT NOT NULL CHECK(length(parser_source_sha)=40 AND parser_source_sha NOT GLOB '*[^0-9a-f]*'),
      importer_contract_id TEXT NOT NULL CHECK(importer_contract_id='T0_ARCHIVE_IMPORTER_V1'),
      importer_source_sha TEXT NOT NULL CHECK(length(importer_source_sha)=40 AND importer_source_sha NOT GLOB '*[^0-9a-f]*'),
      exchange TEXT,
      market_type TEXT,
      symbol TEXT,
      timeframe TEXT,
      open_time_ms INTEGER CHECK(open_time_ms IS NULL OR open_time_ms>=0),
      candle_value_id TEXT CHECK(candle_value_id IS NULL OR (length(candle_value_id)=68 AND substr(candle_value_id,1,4)='cv1:' AND substr(candle_value_id,5) NOT GLOB '*[^0-9a-f]*')),
      disposition TEXT NOT NULL CHECK(disposition IN ('ACCEPTED','REJECTED')),
      rejection_code TEXT,
      UNIQUE(member_id,physical_record_ordinal),
      UNIQUE(member_id,data_row_ordinal),
      CHECK((disposition='ACCEPTED'
             AND exchange IS NOT NULL AND exchange='binance'
             AND market_type IS NOT NULL AND market_type='usdm'
             AND symbol IS NOT NULL AND symbol='BTCUSDT'
             AND timeframe IS NOT NULL AND timeframe IN ('15m','1h')
             AND open_time_ms IS NOT NULL AND candle_value_id IS NOT NULL
             AND rejection_code IS NULL)
         OR (disposition='REJECTED' AND candle_value_id IS NULL AND rejection_code IS NOT NULL))
    ) STRICT;

CREATE TABLE candles (
      exchange TEXT NOT NULL CHECK(exchange='binance'),
      market_type TEXT NOT NULL CHECK(market_type='usdm'),
      symbol TEXT NOT NULL CHECK(symbol='BTCUSDT'),
      timeframe TEXT NOT NULL CHECK(timeframe IN ('15m','1h')),
      open_time_ms INTEGER NOT NULL CHECK(open_time_ms>=0),
      open TEXT NOT NULL,
      high TEXT NOT NULL,
      low TEXT NOT NULL,
      close TEXT NOT NULL,
      volume TEXT NOT NULL,
      available_at_ms INTEGER NOT NULL CHECK(available_at_ms>open_time_ms),
      availability_kind TEXT NOT NULL CHECK(availability_kind='BAR_CLOSE_BOUNDARY'),
      candle_value_id TEXT NOT NULL CHECK(length(candle_value_id)=68 AND substr(candle_value_id,1,4)='cv1:' AND substr(candle_value_id,5) NOT GLOB '*[^0-9a-f]*'),
      PRIMARY KEY(exchange,market_type,symbol,timeframe,open_time_ms)
    ) STRICT;

CREATE TABLE candle_provenance_links (
      link_id TEXT PRIMARY KEY CHECK(length(link_id)=69 AND substr(link_id,1,5)='lnk1:' AND substr(link_id,6) NOT GLOB '*[^0-9a-f]*'),
      exchange TEXT NOT NULL,
      market_type TEXT NOT NULL,
      symbol TEXT NOT NULL,
      timeframe TEXT NOT NULL,
      open_time_ms INTEGER NOT NULL,
      source_row_id TEXT NOT NULL UNIQUE REFERENCES source_rows(source_row_id),
      candle_value_id TEXT NOT NULL CHECK(length(candle_value_id)=68 AND substr(candle_value_id,1,4)='cv1:' AND substr(candle_value_id,5) NOT GLOB '*[^0-9a-f]*'),
      duplicate_disposition TEXT NOT NULL CHECK(duplicate_disposition IN ('UNIQUE','IDENTICAL_DUPLICATE')),
      FOREIGN KEY(exchange,market_type,symbol,timeframe,open_time_ms)
        REFERENCES candles(exchange,market_type,symbol,timeframe,open_time_ms)
    ) STRICT;

CREATE TABLE failure_observations (
      subject_kind TEXT NOT NULL CHECK(subject_kind IN ('RUN','OBJECT','ATTEMPT','PAIR','MEMBER','SOURCE_ROW','CANDLE','LINK')),
      subject_id TEXT NOT NULL,
      failure_ordinal INTEGER NOT NULL CHECK(failure_ordinal>0),
      failure_code TEXT NOT NULL,
      failure_detail_code TEXT,
      observed_at_utc TEXT NOT NULL,
      evidence_sha256 TEXT CHECK(evidence_sha256 IS NULL OR (length(evidence_sha256)=64 AND evidence_sha256 NOT GLOB '*[^0-9a-f]*')),
      PRIMARY KEY(subject_kind,subject_id,failure_ordinal)
    ) STRICT;

-- Exact INDEX_DDL statements, in execution and fingerprint order.

CREATE INDEX idx_archive_objects_pair_key ON archive_objects(paired_object_key,object_kind);

CREATE INDEX idx_acquisition_attempts_object_number ON acquisition_attempts(object_id,attempt_number);

CREATE INDEX idx_archive_pairs_zip_sidecar ON archive_pairs(zip_object_id,sidecar_object_id);

CREATE INDEX idx_csv_members_pair_disposition ON csv_members(pair_id,disposition);

CREATE INDEX idx_source_rows_member_ordinal ON source_rows(member_id,physical_record_ordinal);

CREATE INDEX idx_source_rows_candle_identity ON source_rows(exchange,market_type,symbol,timeframe,open_time_ms);

CREATE INDEX idx_candle_links_candle_identity ON candle_provenance_links(exchange,market_type,symbol,timeframe,open_time_ms);

CREATE INDEX idx_failure_observations_subject_code ON failure_observations(subject_kind,subject_id,failure_code);

-- Exact TRIGGER_DDL statements, in execution and fingerprint order.

CREATE TRIGGER trg_run_events_no_update BEFORE UPDATE ON run_events BEGIN SELECT RAISE(ABORT,'run_events are append-only'); END;

CREATE TRIGGER trg_run_events_no_delete BEFORE DELETE ON run_events BEGIN SELECT RAISE(ABORT,'run_events are append-only'); END;
~~~

### 4.3 DDL versus cross-table validator

SQLite CHECK/FK/UNIQUE constraints enforce local shape only. A later S3 projection/read-only DB validator MUST additionally enforce:
1. Exact inventory raw-byte SHA, inventory ID, 404-object set, unique keys and reciprocal pairing.
2. Exactly 404 object summaries and 202 pair summaries.
3. Contiguous attempt numbers, V1 attempt IDs, requested-key equality, same-object successful attempt relation and exactly one complete TRANSFERRED attempt for each VERIFIED object.
4. R4 expected size/SHA = measured size/SHA = successful attempt bytes/SHA; partial digests never substitute.
5. Every VERIFIED pair has verified objects, matching sidecar assertion, CRC/structure true and exactly one VERIFIED member.
6. Candidate/member IDs recomputed from exact T0ENC1 inputs.
7. Every parser-success data row exactly once, exact header-adjusted ordinals, 12-string raw_fields_json, and R5 digest.
8. ACCEPTED rows have supported natural identity/value; REJECTED rows have no candle/link and stable rejection code.
9. Every candle value ID recomputed from exact S3 tuple; canonical decimals, OHLCV, alignment and available_at_ms=open_time_ms+interval.
10. Every accepted row exactly one link; every candle at least one link; source/link/candle natural key and value agree.
11. Sole UNIQUE link is smallest source_row_id by UTF-8 bytes; others IDENTICAL_DUPLICATE.
12. Coverage canonical bytes/hash, inclusive exact-set ranges, approved gap/extra sets and all six collection counts match R6.
13. Run event sequence/transitions and snapshot/validator digests valid; no quarantined/rejected evidence in VALIDATED run.
14. PRAGMA integrity_check exactly ok; foreign_key_check zero rows; foreign_keys=1 verified per connection.
15. No unsupported/unlisted object, row omission, conflict, missing evidence, stale SHA or unapproved coverage exception.

## 5. Deterministic schema fingerprint

Schema fingerprint identifies schema, not database contents.

Canonical manifest fields:
- schema_contract_id = T0_STAGING_SCHEMA_V2
- user_version = integer 2
- sqlite_minimum_version = "3.37.0"
- tables = exact CREATE TABLE statements in §4.2 order
- indexes = exact CREATE INDEX statements in §4.2 order
- triggers = exact CREATE TRIGGER statements in §4.2 order
- pragmas = ["PRAGMA user_version=2;"]

Canonicalize as RFC 8785 JCS UTF-8, no BOM/no trailing newline. Array order is significant. DDL text uses LF, UTF-8, no trailing spaces; do not normalize SQL tokens, whitespace inside literals or identifier case.

Formula:

~~~text
schema_fingerprint_sha256 =
  lowercase_hex(SHA256(T0ENC1(
    "T0-SQLITE-SCHEMA-FINGERPRINT-V1",
    "T0_STAGING_SCHEMA_V2",
    2,
    canonical_schema_manifest_utf8_bytes
  )))
~~~

Store the 64-hex result in reconstruction_run.schema_fingerprint_sha256; do not embed the value in the manifest (avoids self-reference).

Later read-only verification reconstructs the expected manifest from version-controlled approved DDL, recomputes fingerprint, reads user_version/sqlite_schema/table metadata, compares exact table/index/trigger sets and SQL, rejects any view, extra/missing object, altered constraint or trigger, and compares the run row. Never trust only the stored fingerprint string.

## 6. S3/V1 compatibility

Unchanged public API:
- encode_t0enc1(domain, *fields)
- derive_attempt_id(object_id, attempt_number, workflow_run_id, workflow_job_id, trigger_sha, requested_key)
- validate_provenance(payload)
- immutable ProvenanceValidationResult(valid, error_codes)
- all ten V1 codes and eleven S3 appended codes, meanings, deduplication and fixed order.
- R3 exact V1/S1 dispatch; R4 three-layer equality; R5 raw fields/JSON/T0ENC1; R6 inclusive exact-set coverage and deterministic duplicate role.
- S3 remains pure in-memory; no SQLite/filesystem/archive/network/runtime access.

### 6.1 Error catalogue (fixed order)

V1:
1. PROVENANCE_INPUT_SHAPE_INVALID
2. INVENTORY_OBJECT_SET_INCOMPLETE
3. OBJECT_NOT_IN_APPROVED_INVENTORY
4. QUARANTINED_EVIDENCE_PRESENT
5. ATTEMPT_OUTCOME_UNKNOWN
6. TRANSFERRED_ATTEMPT_INCOMPLETE
7. VERIFIED_PAIR_MEMBER_CARDINALITY_INVALID
8. ACCEPTED_SOURCE_ROW_LINK_CARDINALITY_INVALID
9. CANDLE_IDENTITY_VALUE_CONFLICT
10. CANDLE_AVAILABILITY_BOUNDARY_INVALID

S3 appended:
11. INVENTORY_RAW_BYTES_INVALID
12. INVENTORY_OBJECT_SET_MISMATCH
13. OBJECT_MEASUREMENT_INVALID
14. OBJECT_ATTEMPT_HISTORY_INVALID
15. ARCHIVE_PAIR_EVIDENCE_INVALID
16. CSV_MEMBER_EVIDENCE_INVALID
17. SOURCE_ROW_PROVENANCE_INVALID
18. CANDLE_VALUE_DIGEST_INVALID
19. CANDLE_OHLCV_CONSTRAINT_INVALID
20. CANDLE_PROVENANCE_LINK_INVALID
21. RUN_ACCEPTANCE_INVARIANT_INVALID

S1.2 adds no code and repurposes none. Full failure_observations are physical audit records; S3 result remains the frozen stable code tuple.

### 6.2 Known compatibility limitations

- Current importer-core synthetic fixture uses usd_m; adapter rejects it for persistence and requires explicit usdm.
- Current importer-core duplicate comparison includes source-only fields. A core-quarantined batch remains quarantined; S1.2 does not bypass or change it.
- Current parser is all-or-nothing; parser errors are member quarantine, not fabricated partial rows.
- S3 V1 requires workflow IDs; proposed manually dispatched ephemeral runner provides real IDs but remains unapproved.
- S3 does not read SQLite; future read-only projection adapter maps DB records into unchanged payload.
- S3 run.status=CANDIDATE is projected from immutable candidate event; current state derives from latest event.

## 7. Run snapshot and validation protocol

Later approved builder must:
1. Create new staging DB and insert immutable run envelope + BUILDING event.
2. Insert all evidence in deterministic order. No UPDATE/DELETE. Any failure appends QUARANTINED and abandons the DB/path.
3. Close writers; compute candidate evidence snapshot digest over logical evidence rows excluding run_events and digest field itself. Exact row serialization/domain must be frozen in the later adapter contract; it does not replace S3 validation.
4. Append CANDIDATE event with snapshot digest; close writer; read-only project S3 payload. Require valid=True and empty error_codes.
5. Run integrity/FK/schema/runtime/source-to-staging checks read-only.
6. On pass, append VALIDATED event binding candidate snapshot SHA and validator payload SHA. Close all connections.
7. Final read-only verification checks event sequence, bound digests, schema fingerprint, integrity/FK and replays the candidate S3 projection.
8. Record final DB SHA, schema fingerprint, run ID, source SHAs, validator result, runtime versions and evidence in a separate approved evidence record. Never upload raw DB/source to GitHub.

No part of this protocol is authorized by S1.2.

## 8. B1–B10 closure register

| Finding | S1.2 disposition | Status |
|---|---|---|
| B1 market_type | canonical usdm; reject usd_m; explicit profile | DESIGN RESOLVED |
| B2 duplicate equality | raw-row identity separated from normalized candle tuple | DESIGN RESOLVED; core remains stricter |
| B3 row/link disposition | exact mapping in §2 B3 | DESIGN RESOLVED |
| B4 coverage bounds | half-open to inclusive formula + exact expansion | DESIGN RESOLVED |
| B5 provenance IDs | derive from verified member + ordinals + T0ENC1 | DESIGN RESOLVED |
| B6 parser failure | member quarantine; no fabricated partial rows | RESOLVED WITH LIMITATION |
| B7 run lifecycle | append-only events and derived state | DESIGN RESOLVED |
| B8 execution provenance | manual workflow_dispatch on ephemeral workstation runner | PROPOSED; OWNER ACCEPTANCE REQUIRED |
| B9 physical DDL | complete DDL candidate + fingerprint | SPECIFIED; OWNER ACCEPTANCE REQUIRED |
| B10 multiple failures | append-only failure_observations | DESIGN RESOLVED |

## 9. Required separate approvals

S1.2 acceptance freezes documentation only. It does NOT authorize implementation.

| Gate | Scope | Status |
|---|---|---|
| S1.2 owner acceptance | B1–B10, DDL, runner provenance and fingerprint | PENDING |
| DDL design review | syntax/constraints/FK/index/fingerprint review | NOT RUN |
| Adapter DTO contract | immutable DTO + DB↔S3 projection | NOT AUTHORIZED |
| Synthetic adapter TDD | synthetic-only tests, no SQLite/archive unless separately scoped | NOT AUTHORIZED |
| SQLite runtime pin | exact Python patch, SQLite library and runner image | NOT SELECTED |
| SQLite schema implementation | disposable new staging DB only, exact-SHA CI | NOT AUTHORIZED |
| Workstation/runner preflight | exact device/path/encryption/disk/inodes/manual ephemeral runner | BLOCKED / NOT AUTHORIZED |
| Archive B3/B5 validation | separate source-access approval | NOT AUTHORIZED |
| Importer/build | separate approval after prerequisites | NOT AUTHORIZED |
| Canonical promotion | separate acceptance and owner decision | NOT AUTHORIZED |

### 9.1 Explicit exclusions

No parser/importer-core/S3/V1/workflow implementation changes; no adapter/tests; no SQLite open/create/DDL/PRAGMA/migration; no archive listing/download/extraction/parse/sample; no workstation/SSH/filesystem/path/runner registration/preflight/provisioning; no artifact upload/retention change/deletion; no Canonical T0/MAY-10/REST tail; no T1/T2/VPS/runtime/deployment/credentials/exchange/trading.

## 10. Self-review and limitations

Same-session documentation self-review against:
- S1.1 blob 209c9d10cc0e54dc90148efa9ef6884f74aa143d
- S3 contract blob da89266c7c4d1394c731b1c2304cdb73b077d4f6
- V1 interface blob 632eb6d38461ea3c65638ca073abc5fe4ae98729
- importer-core blob a7d7245fe7379f3d3b67c0a111e906a4364f6d10
- parser blob 10fe2313103c45d5455f17ff71f3fd0af2e6f038
- S3 validator blob b94bac0f82ae141984552409f99a5cff70435b3b

Checklist:
- [x] No S3/V1 API or error-code change.
- [x] T0ENC1 and stable identity prefixes retained.
- [x] Candle natural key and usdm retained.
- [x] Failed evidence and quarantine semantics retained.
- [x] Attempts/run events append-only; no mutable status.
- [x] Coverage conversion explicit.
- [x] Parser limitation disclosed; no partial rows fabricated.
- [x] DDL candidate, constraints, indexes and fingerprint specified.
- [x] STRICT/FK/runtime/no-migration gates retained.
- [x] No implementation/data operation performed.

Limitations:
1. Same-session self-review only; not independent.
2. DDL has not been parsed/executed against SQLite. SQL syntax, FK compatibility and STRICT behavior NOT VERIFIED.
3. Ephemeral manual runner is a proposal requiring owner acceptance and later host/workflow approval.
4. Current importer-core stricter duplicate comparison may quarantine rows S3 candle semantics would consider identical; fail closed, no core change.
5. Parser cannot emit partial row diagnostics; member-level quarantine is current behavior.
6. Exact runtime pins, real archive formats, source coverage, workstation path/preflight and actual resource availability unresolved.

**Disposition: S1.2 DESIGN PROPOSAL COMPLETE; SELF-REVIEW PASS WITH LIMITATIONS; OWNER ACCEPTANCE PENDING; PERSISTENCE BLOCKED.**

## 11. Work record

Documentation-only. No source/test/workflow change, DDL execution, SQLite connection/PRAGMA/migration, archive/sidecar/host/workstation/runner/filesystem/Canonical T0/runtime access, workflow run/job/artifact. Next: owner review, especially B8 execution model and DDL candidate. Adapter, tests, DDL and SQLite each require separate explicit approval.
