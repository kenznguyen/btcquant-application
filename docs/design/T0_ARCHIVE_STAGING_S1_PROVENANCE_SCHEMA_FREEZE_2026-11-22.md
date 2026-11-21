# T0 Archive Staging S1 — Provenance Contracts & SQLite Schema Freeze

Date: 2026-11-22
Repository: kenznguyen/btcquant-application
Branch: main
Status: **S1 DESIGN FREEZE PROPOSAL — DOCUMENTATION ONLY**

## 1. Decision boundary

This document freezes the design-level contracts and staging schema for S1, under the owner's approval of S1 only.

It does not authorize S2 validator tests, importer implementation, archive acquisition, workflow YAML creation/dispatch, local staging files, SQLite creation, or any data operation. A separate owner approval is required for each later phase.

Immutable exclusions:
- Canonical T0 remains an independent asset and is not accessed, read, written, copied, migrated, replaced, merged, restored, promoted or cut over.
- The former Canonical SQLite remains LOST. Any future output is a new asset labelled `RECONSTRUCTED — PARTIAL COVERAGE`.
- Exact source inventory remains 404 objects: 202 ZIPs and 202 paired `.CHECKSUM` sidecars. No listing, wildcard or unlisted object.
- REST tail and MAY-10 are excluded.
- No T1/T2, Feeder, Scheduler, runtime, VPS, PostgreSQL/TimescaleDB, deployment, exchange credentials, cleanup/deletion or trading.
- Source archive and evidence retention/deletion remain separate owner decisions.

## 2. Contract set and stable identifiers

All identifiers below are lowercase hexadecimal SHA-256 strings with a fixed prefix and version. They are content-derived, not random, path-derived or dependent on database rowids. Database surrogate integer IDs are prohibited as provenance identities.

| Entity | Stable identifier | Uniqueness scope |
|---|---|---|
| Inventory | `inv1:<sha256>` | Exact inventory bytes |
| Archive object | `obj1:<sha256>` | Inventory SHA + exact object key + object kind |
| ZIP/sidecar pair | `pair1:<sha256>` | ZIP object ID + sidecar object ID |
| CSV member | `mem1:<sha256>` | Pair ID + exact member path + measured member SHA |
| Source row | `row1:<sha256>` | Member ID + physical record ordinal + raw-row digest |
| Candle identity | Natural key | exchange + market_type + symbol + timeframe + open_time_ms |
| Candle value | `cv1:<sha256>` | Candle identity + normalized value tuple |
| Provenance link | `lnk1:<sha256>` | Candle identity + source-row ID + duplicate disposition |

The prefix is part of the externally stored identifier and prevents accidental cross-domain reuse. A version change requires a new prefix/version; never reinterpret old IDs.

### 2.1 Object identity

`object_id = "obj1:" + SHA256(ENC("T0-ARCHIVE-OBJECT-V1", inventory_sha256, exact_object_key_utf8, object_kind))`

`object_kind` is exactly `ZIP` or `CHECKSUM_SIDECAR`. Object key is the exact inventory key, case-sensitive and byte-preserved after UTF-8 encoding. Pairing comes only from the pinned inventory's explicit paired-object key; no suffix derivation.

### 2.2 Pair and member identity

`pair_id = "pair1:" + SHA256(ENC("T0-ARCHIVE-PAIR-V1", zip_object_id, sidecar_object_id))`

`member_id = "mem1:" + SHA256(ENC("T0-CSV-MEMBER-V1", pair_id, exact_member_path_utf8, member_sha256_raw_32_bytes))`

A ZIP may have only the single approved CSV member for its archive. Zero or multiple candidate members quarantine the candidate; do not pick one heuristically.

### 2.3 Source-row identity and raw payload digest

For each accepted or rejected data record, preserve all 12 original field strings in source order. The first-record header, if present, is not a source data row.

`raw_row_digest = SHA256(ENC("T0-RAW-CSV-ROW-V1", field_1_utf8, ..., field_12_utf8))`

`source_row_id = "row1:" + SHA256(ENC("T0-SOURCE-ROW-V1", member_id, physical_record_ordinal_i64, raw_row_digest_raw_32_bytes))`

Physical record ordinal is 1-based and includes a header if present. Data-row ordinal is 1-based and excludes a header. Both are stored. The physical ordinal plus member ID makes repeated identical records in one file distinguishable. Raw row digest is separately retained to identify identical source payloads across archives.

CSV parsing must preserve the exact decoded field strings after CSV unquoting, with no trimming, case conversion, decimal reformatting or Unicode normalization. The parser's declared UTF-8 decoding policy and BOM handling remain governed by the approved parser contract. Invalid encoding or undecodable bytes quarantine the archive; do not replace invalid characters.

### 2.4 Normalized candle identity and value

Natural identity is exactly:
`exchange + market_type + symbol + timeframe + open_time_ms`.

For this archive scope, expected values are `binance`, `usdm`, `BTCUSDT`, and `15m` or `1h`. These are validated values, not inferred from arbitrary source strings.

Normalized candle value digest covers, in fixed order:
`open_time_ms, open, high, low, close, volume, available_at_ms, availability_kind`.
Decimal values are canonical fixed-point base-10 strings with no exponent, no leading plus, no redundant leading zeroes (except zero itself), and no trailing fractional zeroes. Integer values use base-10 ASCII without leading zeroes. Kind is exactly `BAR_CLOSE_BOUNDARY`.

`candle_value_id = "cv1:" + SHA256(ENC("T0-CANDLE-VALUE-V1", exchange, market_type, symbol, timeframe, open_time_ms, open, high, low, close, volume, available_at_ms, availability_kind))`

The natural candle key remains the authoritative uniqueness key in SQLite. The value digest is an audit/check value, not a substitute for the key or the row values.

### 2.5 Provenance-link identity

`link_id = "lnk1:" + SHA256(ENC("T0-CANDLE-PROVENANCE-LINK-V1", exchange, market_type, symbol, timeframe, open_time_ms, source_row_id, duplicate_disposition))`

Disposition is exactly `UNIQUE` or `IDENTICAL_DUPLICATE`. Each candle has one or more links. The source row and candle must match on the normalized identity and value digest. Conflicting values cannot link to a valid candle.

## 3. Canonical serialization and digest framing

All IDs and digests use SHA-256. Do not hash concatenated strings without framing, JSON text with unspecified key ordering, Python repr, SQL serialization, locale-formatted numbers or platform-native integer bytes.

Define `ENC(domain, fields...)` as this exact byte sequence:

1. ASCII bytes `T0ENC1` followed by one NUL byte.
2. Domain as UTF-8, preceded by unsigned 32-bit big-endian byte length.
3. Field count as unsigned 32-bit big-endian.
4. For each field in order:
   - null: one byte `0x00`, then unsigned 64-bit big-endian zero length;
   - non-null: one byte `0x01`, then unsigned 64-bit big-endian byte length, then exact field bytes.
5. Text fields are UTF-8; digest fields explicitly marked raw bytes are exactly 32 bytes; integers are canonical ASCII decimal strings before framing. No implicit null/empty equivalence.

Domain strings are the exact uppercase strings specified above. Reject invalid UTF-8, overlong encodings, invalid lengths, integer overflow and unexpected field counts. Lengths are byte lengths, not character counts.

The inventory SHA is computed over the exact pinned inventory file bytes. Object measured SHA is computed over exact downloaded bytes. Sidecar measured SHA is over the complete sidecar bytes; its parsed asserted ZIP digest is a separate 32-byte value and must equal the measured ZIP SHA. Never substitute the asserted digest for the sidecar's own measured digest.

Manifest serialization, if later emitted, is UTF-8 JSON with RFC 8785 JSON Canonicalization Scheme (JCS), no BOM, no trailing newline for digest calculation, and SHA-256 over exact canonical bytes. The manifest schema version and digest algorithm are explicit fields. Do not use JCS to derive raw CSV row digests; use ENC above.

## 4. Frozen provenance record contracts

### 4.1 ArchiveObjectEvidence — exactly 404 records

Required fields:
- `object_id`, `inventory_id`, `inventory_blob_sha256`, `inventory_entry_identity`;
- `object_key`, `object_kind`, `timeframe`, `partition`, `period`, `paired_object_key`;
- nullable `expected_size_bytes`, nullable `expected_sha256` only when absent from the pinned inventory;
- `measured_size_bytes`, `measured_sha256`;
- `retrieval_source`, `requested_key`, `workflow_run_id`, `workflow_job_id`, `workflow_event`, `trigger_sha`, `checkout_sha`, `attempt_count`, `retrieved_at_utc`;
- `response_bytes_total`, `response_status`, `local_relative_path`, `exclusive_create`, `verification_status`.

Status values: `VERIFIED`, `QUARANTINED`. Eligibility requires exact allowlisted key, measured bytes/hash, satisfied available inventory expectations, safe exclusive file creation, and a successful response. A missing expected hash is not silently treated as verified by assertion; fresh measured evidence is still mandatory.

### 4.2 ArchivePairEvidence — exactly 202 records

Required fields:
- `pair_id`, `zip_object_id`, `sidecar_object_id`;
- measured ZIP and sidecar size/hash;
- parsed sidecar asserted ZIP SHA-256;
- sidecar assertion comparison result;
- ZIP CRC result;
- member count and structural result;
- `disposition`.

Disposition: `VERIFIED` or `QUARANTINED`. Both object records must be independently VERIFIED.

### 4.3 CsvMemberEvidence — expected exactly 202 records

Required fields:
- `member_id`, `pair_id`, exact member path, uncompressed size, member SHA-256;
- encoding, BOM presence, newline, delimiter;
- `header_present`, exact header contract ID when present;
- parser contract ID and parser source SHA;
- data-row count, first/last open time;
- `disposition`.

Exactly one member is accepted per archive. Unsupported header mode, encoding, delimiter, member layout or parser result quarantines the candidate. The real-source header observation remains limited to M15 monthly 2022-08; do not infer other archives' mode.

### 4.4 SourceRowProvenance — one record per data record considered

Required fields:
- `source_row_id`, `member_id`;
- physical record ordinal and data-row ordinal;
- twelve original field strings in source order;
- `raw_row_digest`;
- parser contract/source SHA and importer source SHA (importer SHA remains null until a later authorized implementation);
- normalized candle natural key, normalized value digest (nullable only for rejected rows);
- validation disposition and stable rejection code.

Disposition values: `ACCEPTED` or `REJECTED`. Every data record must have a record and disposition; no silent skip. Rejected records do not generate candles or provenance links. An archive containing any rejected/malformed row quarantines the whole candidate under the current all-or-nothing policy.

### 4.5 CandleProvenanceLink — one or more per candle

Required fields:
- `link_id`, candle natural key, `source_row_id`, `candle_value_id`;
- duplicate disposition `UNIQUE` or `IDENTICAL_DUPLICATE`.

For a unique candle there is exactly one link marked UNIQUE. If the same identity and exact normalized value is present in multiple source rows, all source rows are retained and linked; deterministic source order selects one UNIQUE representative and remaining links are IDENTICAL_DUPLICATE. Representative ordering is lexicographic `source_row_id`, not import order. If the same identity has different normalized values, quarantine the entire candidate. No first/last-write-wins.

## 5. SQLite staging schema v2 — design DDL

This is a new staging-only schema. It is not a migration script and must never be applied to any existing database. The candle table retains the Candle Contract 1.2.0 natural primary key and explicit `availability_kind`. Provenance is stored in separate immutable tables, not duplicated into the hot candle row.

The schema uses SQLite `PRAGMA user_version=2` as required by the reviewed Candle Contract 1.2.0 design. All tables use `STRICT`; importer must verify the pinned SQLite runtime supports STRICT tables before any later implementation. Foreign keys must be enabled and verified on every connection. No triggers are required; immutability is enforced by a single-writer build phase, closed writers, read-only validation and immutable evidence output.

```sql
PRAGMA user_version = 2;

CREATE TABLE reconstruction_run (
    run_id TEXT PRIMARY KEY,
    inventory_id TEXT NOT NULL,
    inventory_blob_sha256 TEXT NOT NULL CHECK(length(inventory_blob_sha256) = 64),
    label TEXT NOT NULL CHECK(label = 'RECONSTRUCTED — PARTIAL COVERAGE'),
    parser_contract_id TEXT NOT NULL,
    parser_source_sha TEXT NOT NULL CHECK(length(parser_source_sha) = 40),
    importer_source_sha TEXT NOT NULL CHECK(length(importer_source_sha) = 40),
    schema_contract_id TEXT NOT NULL CHECK(schema_contract_id = 'T0_STAGING_SCHEMA_V2'),
    created_at_utc TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('BUILDING', 'QUARANTINED', 'VALIDATED'))
) STRICT;

CREATE TABLE archive_objects (
    object_id TEXT PRIMARY KEY,
    inventory_id TEXT NOT NULL,
    inventory_blob_sha256 TEXT NOT NULL CHECK(length(inventory_blob_sha256) = 64),
    inventory_entry_identity TEXT NOT NULL,
    object_key TEXT NOT NULL UNIQUE,
    object_kind TEXT NOT NULL CHECK(object_kind IN ('ZIP', 'CHECKSUM_SIDECAR')),
    timeframe TEXT NOT NULL CHECK(timeframe IN ('15m', '1h')),
    partition TEXT NOT NULL,
    period TEXT NOT NULL,
    paired_object_key TEXT NOT NULL,
    expected_size_bytes INTEGER CHECK(expected_size_bytes IS NULL OR expected_size_bytes >= 0),
    expected_sha256 TEXT CHECK(expected_sha256 IS NULL OR length(expected_sha256) = 64),
    measured_size_bytes INTEGER NOT NULL CHECK(measured_size_bytes >= 0),
    measured_sha256 TEXT NOT NULL CHECK(length(measured_sha256) = 64),
    retrieval_source TEXT NOT NULL,
    requested_key TEXT NOT NULL,
    workflow_run_id TEXT NOT NULL,
    workflow_job_id TEXT NOT NULL,
    workflow_event TEXT NOT NULL,
    trigger_sha TEXT NOT NULL CHECK(length(trigger_sha) = 40),
    checkout_sha TEXT NOT NULL CHECK(length(checkout_sha) = 40),
    attempt_count INTEGER NOT NULL CHECK(attempt_count > 0),
    retrieved_at_utc TEXT NOT NULL,
    response_bytes_total INTEGER NOT NULL CHECK(response_bytes_total >= 0),
    response_status INTEGER NOT NULL,
    local_relative_path TEXT NOT NULL,
    exclusive_create INTEGER NOT NULL CHECK(exclusive_create IN (0, 1)),
    verification_status TEXT NOT NULL CHECK(verification_status IN ('VERIFIED', 'QUARANTINED')),
    CHECK(requested_key = object_key),
    CHECK(exclusive_create = 1)
) STRICT;

CREATE TABLE archive_pairs (
    pair_id TEXT PRIMARY KEY,
    zip_object_id TEXT NOT NULL UNIQUE REFERENCES archive_objects(object_id),
    sidecar_object_id TEXT NOT NULL UNIQUE REFERENCES archive_objects(object_id),
    zip_size_bytes INTEGER NOT NULL CHECK(zip_size_bytes >= 0),
    zip_sha256 TEXT NOT NULL CHECK(length(zip_sha256) = 64),
    sidecar_size_bytes INTEGER NOT NULL CHECK(sidecar_size_bytes >= 0),
    sidecar_sha256 TEXT NOT NULL CHECK(length(sidecar_sha256) = 64),
    sidecar_asserted_zip_sha256 TEXT NOT NULL CHECK(length(sidecar_asserted_zip_sha256) = 64),
    assertion_matches INTEGER NOT NULL CHECK(assertion_matches IN (0, 1)),
    zip_crc_ok INTEGER NOT NULL CHECK(zip_crc_ok IN (0, 1)),
    member_count INTEGER NOT NULL CHECK(member_count >= 0),
    structural_ok INTEGER NOT NULL CHECK(structural_ok IN (0, 1)),
    disposition TEXT NOT NULL CHECK(disposition IN ('VERIFIED', 'QUARANTINED')),
    CHECK(assertion_matches = 1),
    CHECK(zip_crc_ok = 1),
    CHECK(structural_ok = 1),
    CHECK(member_count = 1)
) STRICT;

CREATE TABLE csv_members (
    member_id TEXT PRIMARY KEY,
    pair_id TEXT NOT NULL UNIQUE REFERENCES archive_pairs(pair_id),
    member_path TEXT NOT NULL,
    member_size_bytes INTEGER NOT NULL CHECK(member_size_bytes >= 0),
    member_sha256 TEXT NOT NULL CHECK(length(member_sha256) = 64),
    encoding TEXT NOT NULL CHECK(encoding = 'UTF-8'),
    bom_present INTEGER NOT NULL CHECK(bom_present IN (0, 1)),
    newline TEXT NOT NULL,
    delimiter TEXT NOT NULL CHECK(delimiter = ','),
    header_present INTEGER NOT NULL CHECK(header_present IN (0, 1)),
    header_contract_id TEXT,
    parser_contract_id TEXT NOT NULL CHECK(parser_contract_id = 'T0_ARCHIVE_CSV_HEADER_V1'),
    parser_source_sha TEXT NOT NULL CHECK(length(parser_source_sha) = 40),
    data_row_count INTEGER NOT NULL CHECK(data_row_count >= 0),
    first_open_time_ms INTEGER,
    last_open_time_ms INTEGER,
    disposition TEXT NOT NULL CHECK(disposition IN ('VERIFIED', 'QUARANTINED')),
    CHECK((header_present = 1 AND header_contract_id = 'T0_ARCHIVE_CSV_HEADER_V1')
       OR (header_present = 0 AND header_contract_id IS NULL)),
    CHECK((data_row_count = 0 AND first_open_time_ms IS NULL AND last_open_time_ms IS NULL)
       OR (data_row_count > 0 AND first_open_time_ms IS NOT NULL AND last_open_time_ms IS NOT NULL))
) STRICT;

CREATE TABLE candles (
    exchange TEXT NOT NULL CHECK(exchange = 'binance'),
    market_type TEXT NOT NULL CHECK(market_type = 'usdm'),
    symbol TEXT NOT NULL CHECK(symbol = 'BTCUSDT'),
    timeframe TEXT NOT NULL CHECK(timeframe IN ('15m', '1h')),
    open_time_ms INTEGER NOT NULL CHECK(open_time_ms >= 0),
    open TEXT NOT NULL,
    high TEXT NOT NULL,
    low TEXT NOT NULL,
    close TEXT NOT NULL,
    volume TEXT NOT NULL,
    available_at_ms INTEGER NOT NULL,
    availability_kind TEXT NOT NULL CHECK(availability_kind = 'BAR_CLOSE_BOUNDARY'),
    candle_value_id TEXT NOT NULL CHECK(length(candle_value_id) = 68),
    PRIMARY KEY(exchange, market_type, symbol, timeframe, open_time_ms)
) STRICT;

CREATE TABLE source_rows (
    source_row_id TEXT PRIMARY KEY,
    member_id TEXT NOT NULL REFERENCES csv_members(member_id),
    physical_record_ordinal INTEGER NOT NULL CHECK(physical_record_ordinal > 0),
    data_row_ordinal INTEGER NOT NULL CHECK(data_row_ordinal > 0),
    raw_fields_json TEXT NOT NULL,
    raw_row_digest TEXT NOT NULL CHECK(length(raw_row_digest) = 64),
    parser_contract_id TEXT NOT NULL CHECK(parser_contract_id = 'T0_ARCHIVE_CSV_HEADER_V1'),
    parser_source_sha TEXT NOT NULL CHECK(length(parser_source_sha) = 40),
    importer_source_sha TEXT NOT NULL CHECK(length(importer_source_sha) = 40),
    exchange TEXT,
    market_type TEXT,
    symbol TEXT,
    timeframe TEXT,
    open_time_ms INTEGER,
    candle_value_id TEXT,
    disposition TEXT NOT NULL CHECK(disposition IN ('ACCEPTED', 'REJECTED')),
    rejection_code TEXT,
    UNIQUE(member_id, physical_record_ordinal),
    UNIQUE(member_id, data_row_ordinal),
    CHECK((disposition = 'ACCEPTED' AND exchange IS NOT NULL AND market_type IS NOT NULL
       AND symbol IS NOT NULL AND timeframe IS NOT NULL AND open_time_ms IS NOT NULL
       AND candle_value_id IS NOT NULL AND rejection_code IS NULL)
       OR (disposition = 'REJECTED' AND candle_value_id IS NULL AND rejection_code IS NOT NULL))
) STRICT;

CREATE TABLE candle_provenance_links (
    link_id TEXT PRIMARY KEY,
    exchange TEXT NOT NULL,
    market_type TEXT NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    open_time_ms INTEGER NOT NULL,
    source_row_id TEXT NOT NULL UNIQUE REFERENCES source_rows(source_row_id),
    candle_value_id TEXT NOT NULL CHECK(length(candle_value_id) = 68),
    duplicate_disposition TEXT NOT NULL CHECK(duplicate_disposition IN ('UNIQUE', 'IDENTICAL_DUPLICATE')),
    FOREIGN KEY(exchange, market_type, symbol, timeframe, open_time_ms)
      REFERENCES candles(exchange, market_type, symbol, timeframe, open_time_ms)
) STRICT;

CREATE INDEX idx_archive_objects_pair_key ON archive_objects(paired_object_key);
CREATE INDEX idx_source_rows_candle_identity
  ON source_rows(exchange, market_type, symbol, timeframe, open_time_ms);
CREATE INDEX idx_provenance_links_candle_identity
  ON candle_provenance_links(exchange, market_type, symbol, timeframe, open_time_ms);
```

DDL notes and required application-level checks:
- The DDL is a contract proposal. It must be implemented and tested later; it is not executable authorization.
- `candle_value_id` length 68 is the prefix `cv1:` plus 64 hex characters; equivalent length applies to row/link/object IDs with their own prefix lengths. Later validator must verify lowercase hexadecimal syntax, not only length.
- All SHA fields must be lowercase hex; SQL length checks are only a first guard.
- `raw_fields_json` is compact UTF-8 JSON array of exactly 12 strings, serialized with RFC 8785-compatible string escaping; no whitespace. The raw row digest is still calculated using ENC, not JSON.
- `physical_record_ordinal` and `data_row_ordinal` are unique within a member and must obey the header offset relation: physical = data ordinal + 1 when header present, otherwise equal. Enforce in validator.
- Source-row table includes rejected row records for audit. Current all-or-nothing policy means any rejected row quarantines the run and no valid staging candidate is accepted.
- A unique constraint on `source_row_id` in provenance links ensures one source row cannot support multiple candle identities.
- Cross-table equality of source row identity/value and candle identity/value, object-kind pairing, exact 202/404 cardinalities, deterministic UNIQUE representative, interval-derived available_at_ms and no rejected rows in a VALIDATED run are validator invariants; SQLite CHECK/FK constraints alone cannot express all of them.
- For a future validated DB, `reconstruction_run.status` becomes VALIDATED only after all write connections close and independent read-only validation succeeds. Failed run remains QUARANTINED and its DB path is never reused.
- Schema uses STRICT tables and TEXT decimal storage to preserve exact decimal semantics. The supported SQLite runtime must be pinned and tested before implementation.
- Foreign-key enforcement is connection-local: importer and validator must each execute and verify `PRAGMA foreign_keys=ON`.
- No trigger or application runtime mutation path is included. After build completion, artifact is immutable by workflow discipline and hash evidence.

## 6. Cross-record invariants and acceptance matrix

### 6.1 Required invariants

1. Inventory is the exact approved blob SHA and contains exactly 404 unique object entries, 202 ZIP + 202 sidecars, with one-to-one explicit pairing.
2. Every object has measured size/SHA and exact key; measured size/hash satisfy all inventory expectations that exist.
3. Every pair contains one ZIP and its explicitly paired sidecar; sidecar assertion equals measured ZIP SHA; CRC and member structure pass.
4. Every verified ZIP has exactly one verified CSV member.
5. Every CSV data record has exactly one SourceRowProvenance record; no missing ordinal, duplicate ordinal or silent skip.
6. Every accepted source row maps to exactly one candle identity/value. Rejected rows have stable rejection code and no candle/link.
7. Every candle has at least one provenance link; every link points to an accepted source row with matching identity and value digest.
8. All source rows for one candle identity have identical normalized values; otherwise the entire candidate is quarantined.
9. Every candle is archive-derived and has `availability_kind=BAR_CLOSE_BOUNDARY` and `available_at_ms=open_time_ms+interval_ms`; source close_time is validated as inclusive `open+interval-1`.
10. Every valid candle's OHLCV constraints and timeframe alignment pass the frozen parser and Candle validator.
11. A VALIDATED run has exactly 202 verified pairs, 202 verified members, 404 verified object records, no rejected rows, no gaps/extras/conflicts outside the separately approved coverage manifest, and passing DB integrity/FK/source-to-DB checks.
12. The complete candidate remains quarantined on any unapproved missing object, unsupported format, provenance gap, parser failure, duplicate conflict, schema mismatch or evidence failure.

### 6.2 Acceptance matrix

| Case | Required disposition | Candle may be stored? | Run acceptable? |
|---|---|---:|---:|
| Exact verified ZIP + sidecar + member + valid row | ACCEPTED | Yes | Only if all global gates pass |
| Inventory expected hash absent, but measured hash and sidecar/CRC checks pass | ACCEPTED WITH MEASURED PROVENANCE | Yes | Conditional on full evidence |
| Missing measured ZIP or sidecar hash/size | QUARANTINED | No | No |
| Sidecar raw hash absent although asserted ZIP hash exists | QUARANTINED | No | No |
| Sidecar assertion differs from measured ZIP hash | QUARANTINED | No | No |
| ZIP CRC/member count/member digest fails | QUARANTINED | No | No |
| Unsupported header/encoding/delimiter/member shape | QUARANTINED | No | No |
| Missing, malformed or silently skipped source row | QUARANTINED | No | No |
| Row rejected by strict parser | QUARANTINED | No | No |
| Same identity + same normalized value from multiple rows | Keep every provenance row; deduplicate candle | Yes | Yes, if all other gates pass |
| Same identity + conflicting normalized value | QUARANTINED | No | No |
| Link references missing row/candle or mismatched digest | QUARANTINED | No | No |
| BAR_CLOSE_BOUNDARY off by 1 ms or wrong interval | QUARANTINED | No | No |
| Any Canonical/MAY-10 access or unlisted object | Stop and quarantine | No | No |

## 7. Deterministic processing order

For stable evidence and repeatability:
1. Inventory objects sorted by exact UTF-8 object-key bytes, then object kind.
2. Pairs sorted by ZIP object key bytes.
3. Members sorted by exact member path bytes (although exactly one is permitted).
4. Source rows processed by physical record ordinal.
5. Candle identities sorted by timeframe then open_time_ms; for cross-timeframe ordering, use timeframe order `15m` then `1h`.
6. Identical duplicate links sorted by source_row_id bytes; smallest source_row_id is UNIQUE representative, all others IDENTICAL_DUPLICATE.
7. Manifest arrays use the same deterministic order. Timestamps in evidence are UTC RFC 3339 with `Z`, fixed millisecond precision.

Acquisition retrieval order is evidence, not identity. Retries do not change object ID or measured-content identity; each attempt is recorded in acquisition evidence. This S1 schema's object record is the final successful acquisition summary; detailed per-attempt history must be a separate append-only acquisition-attempt record in the later manifest, or added by a separately approved schema amendment before implementation. Do not silently overwrite attempt history.

## 8. Schema review findings and unresolved design risks

The following require resolution before any implementation, but do not block recording this S1 proposal as a frozen design baseline:
- The existing Candle Contract 1.2.0 proposal specifies the candle columns and user_version=2, while this staging design adds provenance tables in the same new staging DB. This is additive and preserves the candle natural key; confirm table-name collisions against the exact implementation baseline before any DDL implementation.
- SQLite cannot enforce every cross-table and timeframe invariant; later validator tests must prove them.
- `STRICT` requires a compatible SQLite version. Pin and test the exact runtime before implementation.
- The current schema captures successful acquisition summary, not each retry attempt. An append-only attempt manifest is mandatory for audit; schema addition may be needed if acquisition workflow requires queryable retry history.
- Exact object expected sizes/hashes may be absent for some sidecars in historical inventory. The schema permits null expectations but never null measured evidence.
- The 100 MiB cumulative response-body cap remains in force. ZIP uncompressed-size, compression-ratio and disk-reserve limits remain OPEN and block acquisition implementation.
- Retention, artifact content/expiry and source retention remain unresolved and require separate owner decisions.
- The current archive header parser has real-source evidence only for M15 monthly 2022-08. All other archive modes must be verified individually; one unsupported archive quarantines the complete candidate under current scope.

## 9. Frozen S1 contract identifiers

Subject to owner review, use these exact identifiers:
- Inventory format: `T0_ARCHIVE_INVENTORY_V1`
- Object evidence: `T0_ARCHIVE_OBJECT_EVIDENCE_V1`
- Pair evidence: `T0_ARCHIVE_PAIR_EVIDENCE_V1`
- CSV member evidence: `T0_CSV_MEMBER_EVIDENCE_V1`
- Source row provenance: `T0_SOURCE_ROW_PROVENANCE_V1`
- Candle provenance link: `T0_CANDLE_PROVENANCE_LINK_V1`
- Digest framing: `T0ENC1`
- Staging schema: `T0_STAGING_SCHEMA_V2`
- Header parser: `T0_ARCHIVE_CSV_HEADER_V1`
- Candle semantics: `T0_CANDLE_CONTRACT_1_2_0`

Any semantic or structural change to these contracts requires a version bump or explicit owner-approved amendment before implementation.

## 10. S1 status and next gates

| Work item | Status |
|---|---|
| S1 scope approval | APPROVED |
| Stable IDs and identity domains | FROZEN — DESIGN |
| Canonical serialization and SHA-256 framing | FROZEN — DESIGN |
| Object/pair/member/row/candle provenance contracts | FROZEN — DESIGN |
| SQLite staging schema v2 DDL | FROZEN — DESIGN |
| Acceptance matrix and cross-record invariants | FROZEN — DESIGN |
| DDL implementation / schema tests | NOT AUTHORIZED |
| S2 provenance validator RED tests | NOT AUTHORIZED |
| Importer / acquisition workflow | NOT AUTHORIZED |
| SQLite creation / archive materialization | NOT AUTHORIZED |
| Canonical T0 / MAY-10 / REST tail | EXCLUDED |
| Runtime / T1 / T2 / trading | NOT AUTHORIZED |

Next: owner reviews this S1 freeze proposal. After review, request separate approval for S2 synthetic-only provenance validator RED tests. S2 must not access archives, create SQLite, or implement the importer.

## 11. Work record

- Documentation-only S1 design freeze proposal.
- No source archive or sidecar request/download; no network/object-store/exchange request.
- No workflow YAML creation, dispatch or rerun.
- No local staging files or SQLite creation.
- No Canonical T0/MAY-10 access.
- No code, tests, dependencies, runtime, VPS, T1/T2, deployment or trading changes.
- Workflow run/job/artifact: none.
