# T0 Archive Staging & Importer — Provenance-First Design Scope

Date: 2026-11-21
Status: **DESIGN PROPOSAL — DOCUMENTATION ONLY — NOT AUTHORIZED FOR IMPLEMENTATION OR EXECUTION**

## 1. Purpose

Define a bounded, auditable design for reconstructing an archive-only BTCUSDT M15/H1 dataset into a new disposable SQLite staging asset. Every imported candle must be traceable to an individually verified source archive object, its paired checksum sidecar, the CSV member and a specific source data record.

This design does not recover the former Canonical SQLite. The former Canonical asset remains **LOST**. The output, if separately approved and successfully built, is a distinct asset labeled:

**RECONSTRUCTED — PARTIAL COVERAGE**

## 2. Controlling decisions and immutable boundaries

This proposal is subordinate to:

- Preserve & Reconstruct: `docs/decisions/T0_CANONICAL_DATA_PRESERVE_AND_RECONSTRUCT_DECISION_2026-11-20.md`.
- GitHub Actions staging architecture: `docs/decisions/T0_GITHUB_ACTIONS_SQLITE_STAGING_RECOVERY_DECISION_2026-11-21.md`.
- Workflow/gate design: `docs/plans/T0_GITHUB_ACTIONS_SQLITE_STAGING_RECOVERY_WORKFLOW_DESIGN_2026-11-21.md`, including its owner-resolution addendum.
- Candle Contract 1.2.0 design: `docs/design/T0_CANDLE_CONTRACT_1_2_0_DESIGN_2026-11-21.md`.
- Parser contract: `T0_ARCHIVE_CSV_HEADER_V1`, implementation/evidence in `docs/evidence/T0_ARCHIVE_CSV_HEADER_V1_TDD_2026-11-21.md`.

Hard boundaries:

1. Canonical T0 is an independent data asset. No access, write, migration, replacement, merge, move, restore, promotion or cutover is part of this scope.
2. The old Canonical SQLite is LOST. Do not describe any reconstructed database as its recovery.
3. Initial data scope is exactly the pinned 404-object inventory: 202 ZIP archives and 202 paired `.CHECKSUM` sidecars. No bucket listing, wildcard, unlisted object, extra date or fallback source.
4. REST tail is excluded. Do not call Binance REST, access the personal host, transfer REST files or infer that REST payloads are present.
5. `MAY-10` is excluded from every source list and staging target.
6. No Feeder, Scheduler, API runtime, T1/T2, PostgreSQL/TimescaleDB, VPS, deployment, exchange credentials or trading integration.
7. No automatic cleanup or deletion of raw source, staging database or evidence. Retention/deletion requires a separate owner decision.
8. GitHub Actions is approved as architecture only. Workflow creation, dispatch, source acquisition and SQLite construction each retain separate approval gates.

## 3. Proposed pipeline and phase separation

The logical pipeline is:

`Pinned inventory`
→ `Per-object acquisition evidence`
→ `ZIP + sidecar verification`
→ `CSV member verification`
→ `Strict parsing`
→ `Row-level provenance mapping`
→ `Coverage / duplicate / conflict reconciliation`
→ `New disposable SQLite staging`
→ `Read-only database validation`
→ `Evidence bundle + owner acceptance`

No phase inherits authorization from the previous phase. A failure or unknown result stops downstream processing. Do not silently skip an archive, row, column or validation.

### Phase A — inventory pin and object pairing

- Pin inventory blob SHA exactly to `eb251ac0924b46add906123f99b82e054d887a59` unless a new inventory revision is separately reviewed and approved.
- Validate exact cardinality: 202 ZIP objects + 202 paired sidecars = 404 objects.
- Each ZIP must map to exactly one sidecar by the inventory's explicit paired key. Do not derive a sidecar key by guesswork.
- Each object record carries object key, object kind, timeframe, archive partition, period, expected size/hash when available, paired-object key, inventory blob SHA and inventory entry identity.
- Inventory omissions or historical unknowns are not filled by inference. A missing expected size/hash is a per-object provenance gap and must be resolved by an approved acquisition measurement before import.

### Phase B — immutable per-object acquisition evidence

For every ZIP and every sidecar, independently record:

- exact object key and object kind;
- pinned inventory blob SHA and paired-object relationship;
- retrieval source/host and exact requested path/key;
- workflow run ID, job ID, event, triggering SHA and checked-out SHA;
- attempt number, UTC retrieval timestamp, HTTP status and relevant response metadata;
- response bytes actually received, measured byte size and SHA-256 of the exact received bytes;
- expected size/hash and measured-versus-expected comparison;
- local file identity/path within the unique run directory, creation mode and exclusive-create result.

For each ZIP/sidecar pair, also record:

- sidecar's own raw byte size and SHA-256 (not merely the digest written inside it);
- strictly parsed sidecar assertion and whether it equals the measured ZIP SHA-256;
- ZIP CRC result;
- exact CSV member path/name, uncompressed size and member SHA-256;
- archive/member structural validation result.

A sidecar's asserted ZIP digest is not provenance for the sidecar payload itself. The sidecar's own bytes must be hashed independently. Historical sidecar size/SHA fields that were not retained remain **NOT VERIFIED** until freshly measured.

Acquisition must use exclusive create/no-follow semantics in a new unique run directory; never overwrite, reuse or follow symlinks. The 100 MiB cumulative response-body ceiling in the approved workflow design applies across all objects and attempts; count received chunks including partial/error bodies and retries. Any byte-cap breach, unlisted object, duplicate key, missing object, checksum mismatch or unsafe path quarantines the entire run. ZIP uncompressed-size and compression-ratio ceilings remain **OPEN DESIGN INPUTS** and must be measured and explicitly approved before implementation.

### Phase C — strict CSV member and row validation

- Only parse a CSV member after its containing ZIP and paired sidecar have passed Phase B.
- Validate exactly one expected CSV member per archive; record member path, size, SHA-256, encoding, BOM, newline and delimiter.
- Apply the frozen `T0_ARCHIVE_CSV_HEADER_V1` rule: compare the complete ordered 12-field tuple only against the first CSV record. Exact match means one header record; otherwise the first record is data and must pass normal strict row validation. No aliases, normalization, fuzzy matching, partial matching or heuristic skipping.
- Headerless archives remain supported by the current parser. A malformed first data record must fail as data; it must never be skipped as a presumed header.
- The only real-source header sample currently verified is M15 monthly 2022-08. Do not infer that every H1, M15 daily or other monthly archive has the same header mode. Record `header_present` independently for every archive. Any unsupported header variant or parser mismatch quarantines the run until separately evidenced and approved.
- Validate row width, integer timestamps/trade count, exact Decimal grammar, timeframe alignment, Binance inclusive close-time relation, OHLC envelope, non-negative volumes, taker-buy bounds and strictly increasing open times.
- Preserve all 12 source field strings in immutable row-provenance evidence or an equivalent lossless source mapping. Do not silently discard the source `ignore` field or any other source-only field.
- Record physical CSV record ordinal (1-based, including a header if present) and data-row ordinal (1-based, excluding a header). These are distinct fields and must never be conflated.

### Phase D — row-level provenance and normalization

Every accepted source data row must have an immutable provenance record containing at minimum:

- inventory blob SHA and exact ZIP object key;
- measured ZIP SHA-256 and byte size;
- exact paired sidecar object key, measured sidecar SHA-256 and byte size;
- parsed sidecar assertion and successful ZIP-digest comparison;
- CSV member path/name, member SHA-256 and uncompressed size;
- header mode and frozen parser contract/version;
- physical CSV record ordinal and data-row ordinal;
- all 12 original field strings in source order, or a lossless canonical representation of them;
- deterministic row-source digest over that lossless representation;
- parser/importer source SHA and dependency-lock identity;
- normalized candle identity and normalized-value digest;
- availability semantics and validation disposition.

The trace chain is:

`inventory entry → ZIP bytes → paired sidecar bytes/assertion → CSV member bytes → source row → normalized candle`.

No normalized candle may exist without at least one complete chain. A row with incomplete provenance is rejected, not imported.

Canonical candle identity remains:
`exchange + market_type + symbol + timeframe + open_time_ms`.

Identical duplicate identity and identical normalized payload may be deduplicated only if every contributing source row is retained as provenance. Conflicting normalized values for the same identity quarantine the complete candidate. No last-write-wins, first-write-wins, interpolation, forward-fill, synthetic candles or silent omission.

### Phase E — temporal semantics and coverage

- Archive rows use `availability_kind=BAR_CLOSE_BOUNDARY` and `available_at_ms=open_time_ms + timeframe_interval_ms`, only after validating the source inclusive close timestamp equals `open_time_ms + interval_ms - 1`.
- This is the deterministic bar-completion boundary, not historical first-observation or retrieval time.
- Live Feeder semantics remain `FIRST_OBSERVED`; no live rows are part of this archive-only build.
- Target contract/schema is the reviewed Contract 1.2.0 design and SQLite `user_version=2`. This design does not authorize schema implementation or change the current production/API contract.
- Independently calculate expected M15/H1 UTC timestamp grids and report missing, extra, duplicate and conflicting identities. Report observed first/last archive bounds separately from continuity inside those bounds.
- Historical inventory figures are acceptance references, not proof of a fresh successful reconstruction: M15 241,440 rows and H1 60,360 rows. Recompute actual totals from newly measured source objects and source rows.
- Earliest history before 2019-12-31 and post-archive tail after 2026-11-18 remain NOT VERIFIED. Do not label the dataset complete.
- REST tail counts (128 M15 / 32 H1 closed rows) are external historical evidence only and are excluded from all expected staging counts.

### Phase F — disposable SQLite staging build

Only after separately approved importer, schema, semantics and database-write scopes:

- Create one new SQLite file at one explicitly approved path under the unique ephemeral staging run directory.
- Require path absence and exclusive creation. Never open an existing DB, infer a path, reuse a failed DB or target Canonical/MAY-10.
- Use explicit Contract 1.2.0 / schema-v2 definitions, including `availability_kind` and immutable provenance tables. Do not apply a migration to any existing database.
- Keep source-object and row-provenance data separate from the hot candle table; enforce foreign keys and uniqueness/consistency constraints where applicable.
- Import in deterministic timeframe/open-time/source order. All writes go through the approved importer; no feeder, scheduler, API or other writer.
- Any error makes the run `QUARANTINED`. Do not repair by dropping rows, changing provenance, overwriting or reusing the DB path.

### Phase G — read-only validation and evidence bundle

After all write connections are closed:

- Open staging SQLite read-only for validation.
- Require `PRAGMA integrity_check = ok`; verify exact schema fingerprint, `user_version=2`, table/index/constraint definitions and foreign-key integrity.
- Recompute row counts, timeframe bounds, timestamp grids, gaps, duplicates/conflicts, OHLCV constraints and BAR_CLOSE_BOUNDARY semantics from the DB.
- Independently compare every staged candle and provenance link against normalized source rows.
- Record database byte size and SHA-256 after the DB is closed and stable.
- Package a manifest with all 404 object records, every pair verification, per-archive member/header/row results, row provenance, importer/parser/workflow/dependency SHAs, coverage/gap reports, DB schema/count/integrity evidence, run/job IDs and artifact digest/expiry.
- Upload only the evidence/data bundle explicitly approved for the run. Artifact retention is temporary review/transport, not durable Canonical storage. Retention duration and exact artifact contents require separate approval.
- Owner acceptance may label the result only `STAGED / VALIDATED — RECONSTRUCTED — PARTIAL COVERAGE`. It does not promote or designate Canonical.

## 4. Required data contracts (design-level)

### 4.1 ArchiveObjectEvidence

One record per raw object (404 records):

- `inventory_blob_sha`
- `inventory_object_key`
- `object_kind` = ZIP | CHECKSUM_SIDECAR
- `timeframe`, `partition`, `period`
- `paired_object_key`
- `expected_size_bytes`, `expected_sha256` (nullable only when inventory truly lacks it)
- `measured_size_bytes`, `measured_sha256`
- `retrieval_run_id`, `retrieval_job_id`, `retrieved_at_utc`, `attempt_count`
- `response_bytes_total`, `response_status`
- `verification_status`

A record is eligible only if the object was fetched from the approved exact key, measured, and all available inventory expectations were satisfied. For a ZIP pair, its sidecar must independently pass the checks below.

### 4.2 ArchivePairEvidence

One record per ZIP + sidecar pair (202 records):

- ZIP object key, measured ZIP SHA/size;
- sidecar key, measured sidecar SHA/size;
- sidecar parsed asserted ZIP digest;
- asserted digest equals measured ZIP digest;
- ZIP CRC and member structural result;
- disposition: VERIFIED or QUARANTINED.

### 4.3 CsvMemberEvidence

One record per verified ZIP (expected 202):

- ZIP pair identity;
- exact member path/name, member size and SHA-256;
- encoding/BOM/newline/delimiter;
- exact 12-column width and header mode;
- parser contract/version and parser result;
- total data-row count and first/last open time;
- disposition: VERIFIED or QUARANTINED.

### 4.4 SourceRowProvenance

One record per accepted source data row before deduplication:

- ZIP pair identity and CSV member identity;
- physical record ordinal and data-row ordinal;
- lossless original 12-field values;
- deterministic source-row digest;
- normalized candle identity and normalized-value digest;
- importer/parser source SHA;
- disposition and rejection reason, if rejected.

### 4.5 CandleProvenanceLink

One or more records per normalized candle identity:

- normalized candle identity;
- source-row provenance identity;
- duplicate disposition: UNIQUE | IDENTICAL_DUPLICATE;
- no conflicting source may be linked to a valid candle.

Exact SQL, canonical serialization, digest framing and table DDL are intentionally not frozen here. They require a separate schema/API contract and TDD approval.

## 5. Fail-closed acceptance rules

The complete staging candidate is **NOT ACCEPTABLE** if any of the following is true:

- inventory blob or object allowlist differs from approved source;
- fewer/more than 404 raw objects or 202 complete ZIP/sidecar pairs;
- any object has no independently measured size/SHA-256;
- sidecar bytes/hash are not recorded independently of the asserted ZIP hash;
- any sidecar assertion, ZIP hash, CRC or member check fails;
- archive/member/header format is unsupported or unverified;
- any data row is skipped, silently normalized, malformed or unaccounted;
- any source row lacks its full provenance chain;
- any duplicate identity conflicts in normalized values;
- any row/candle has invalid BAR_CLOSE_BOUNDARY semantics;
- any gap/extra/duplicate differs from the approved coverage policy;
- schema, foreign keys, SQLite integrity or source-to-DB comparison is not PASS;
- evidence bundle is incomplete or its approved upload/retention requirements fail.

A failed object quarantines the entire 404-object candidate by default. Partial acceptance is not allowed by silently dropping that object. A smaller object set requires a separately approved revised inventory/scope and must carry an explicit narrower coverage label.

## 6. Importer responsibilities and non-responsibilities

Importer is a deterministic offline transformation component:

**Responsibilities**
- consume only a completed, immutable, hash-verified local source manifest and files;
- re-verify file size and SHA-256 before parsing;
- verify ZIP/sidecar/member relationship using recorded evidence;
- call the strict archive CSV parser;
- emit normalized candle candidates plus source-row provenance;
- reconcile identity, duplicates, conflicts and coverage;
- write only to the explicitly supplied new staging DB path when the DB-build gate is enabled;
- produce deterministic reports and fail-closed dispositions.

**Must not**
- make HTTP/network/object-store/exchange requests;
- discover/list objects or invent source paths;
- fetch or transfer REST-tail payloads;
- open, attach, migrate, copy, replace or write Canonical/MAY-10 databases;
- start or control Feeder/Scheduler/API/T1/T2;
- infer FIRST_OBSERVED from archive timestamps;
- fabricate candles or repair source rows;
- delete raw inputs, database files or evidence;
- promote the output or modify any production configuration.

This separation makes acquisition evidence independently reviewable and keeps the importer pure/offline apart from its explicitly gated SQLite output.

## 7. Proposed implementation sequence (each step needs separate approval)

1. **S1 — Contract/schema freeze:** define exact Contract 1.2.0 staging schema, provenance serialization/digest rules, object/pair/member/row identifiers, indexes, constraints and manifest formats.
2. **S2 — Provenance validator RED:** synthetic-only tests proving missing/incorrect object, sidecar, member and row provenance fails closed. No real archive access.
3. **S3 — Offline importer RED/GREEN:** synthetic fixture-only parser-to-normalized-candidate transformation; no DB and no network.
4. **S4 — Reconciliation RED/GREEN:** synthetic-only grid/gap/duplicate/conflict and deterministic manifest tests.
5. **S5 — SQLite schema/build RED/GREEN:** only after separate approval for new disposable DB creation; synthetic inputs first, exact schema v2, no Canonical path.
6. **S6 — Acquisition workflow design/implementation:** separate approval for exact 404-key retrieval, GitHub runner preflight, response-byte/decompression limits and retention. Importer itself remains offline.
7. **S7 — Full archive staging run:** separate explicit approval naming source inventory, workflow SHA, run ID, staging destination, importer SHA, limits and coverage acceptance. One run, one new DB.
8. **S8 — Read-only validation and owner acceptance:** separate approval for validation/artifact; owner reviews exact SHA/run/job/artifact before any later storage decision.

No step is implicitly approved by this design document.

## 8. Open design inputs before implementation

- Exact SQL DDL and provenance serialization/digest framing.
- Stable identifiers for archive object, CSV member, source row and normalized candle link.
- Whether all 202 archive ZIPs contain exactly one CSV member and whether any have format variants beyond the one observed M15 monthly header sample.
- Per-object/aggregate uncompressed-byte and compression-ratio ceilings; safe extraction method and disk-space reserve.
- Exact retry/backoff/timeouts under the 100 MiB cumulative response-body ceiling.
- Full staging schema fingerprint, indexes, foreign keys and transaction sizing.
- Exact expected row-count/gap acceptance manifest after remeasurement of all source objects.
- Evidence artifact content and retention duration.
- Whether archive originals remain available outside the ephemeral runner after the run; no automatic deletion is allowed, and source-retention behavior needs explicit approval.
- Canonical serialization rules for row hashes and source manifest digests.

No implementation may guess these values. Unresolved inputs block the relevant phase.

## 9. Current status

| Work item | Status |
|---|---|
| Preserve & Reconstruct architecture | APPROVED — DESIGN |
| GitHub Actions staging architecture | APPROVED — ARCHITECTURE ONLY |
| 404-object archive-only scope | APPROVED — DESIGN |
| REST tail / MAY-10 exclusion | FIXED — EXCLUDED |
| Contract 1.2.0 BAR_CLOSE_BOUNDARY semantics | APPROVED — DESIGN |
| Header V1 parser | PASS — 34 focused tests at exact SHA |
| Header variants across all 202 ZIPs | NOT VERIFIED |
| Per-object fresh acquisition provenance | DESIGN DEFINED; NOT COLLECTED |
| Row-level provenance chain | DESIGN DEFINED; NOT IMPLEMENTED |
| Provenance/schema contracts and DDL | NOT FROZEN |
| Importer | NOT IMPLEMENTED |
| SQLite staging | NOT CREATED |
| Workflow creation/preflight/acquisition | NOT AUTHORIZED / NOT RUN |
| Canonical T0 access/mutation/promotion | NOT AUTHORIZED |
| Full repository regression | NOT RUN |

## 10. Non-actions and next gate

This is documentation-only design work. It does not authorize or perform:

- any archive/sidecar request, download, bucket listing or materialization;
- REST request or personal-host access/transfer;
- workflow YAML creation, dispatch or rerun;
- local/raw staging file creation;
- SQLite creation, read, write, migration or validation;
- Canonical T0 or MAY-10 access;
- Contract 1.2.0 implementation, importer implementation or source/test/workflow changes;
- T1/T2 runtime connection, VPS/runtime, deployment, PostgreSQL, exchange credentials or trading;
- deletion/cleanup or promotion.

**Next gate:** owner review and approval of S1 only — freeze the provenance object/row contracts and exact staging schema design. S1 approval would still not authorize importer implementation, archive retrieval, workflow creation, SQLite creation or any data operation.
