# T0 Canonical SQLite + Dropbox Snapshot Design — Static Review — 2026-11-19

## Review scope

Read-only static review of the design document, market_data/initialize_sqlite.py, market_data/store.py, market_data/storage.py, market_data/feeder.py and the T0 read-only inventory evidence.

Review was performed against main HEAD 5955423a8edc1661e9cd4f9b7b80a317c6bc77cf. Source file blob identities: initialize_sqlite.py 58bd2deba66cc667bad8d6446c5ff54e7f5dd240; store.py 4e1b0c54bd56455abe5be0e5c7d0807e63e0bc78; storage.py ae03c5a1caf68bb292ca2903e187a2a3a2474938; feeder.py 299a9b5a8b1ebd581eb620d5ee860d9f9ff5dc5c.

## Verdict

**DESIGN REVIEW: PASS WITH REQUIRED SPECIFICATION CLARIFICATIONS.**

The architectural separation is sound: local SQLite remains the operational primary; Dropbox receives closed, versioned snapshots; restore targets a separate location; reconstructed data is not conflated with recovered original data.

The repository does not contain a snapshot publisher, Dropbox adapter, manifest validator, or restore verifier. Static inspection therefore cannot prove backup/restore works. No tests were run and no operational backup was created.

## Findings

### R1 — REQUIRED: define Dropbox object identity and no-overwrite publication

A unique path alone is not a sufficient immutable-version guarantee. A future publisher must use Dropbox no-overwrite/create-only write mode (or equivalent conditional creation), and record returned Dropbox file ID and revision (id, rev), path, server-reported size and modification metadata. It must fail closed if the target already exists; never silently update or autorename into an ambiguous location.

After upload, download/read back that exact revision and verify byte size and locally calculated SHA-256 against the staged snapshot. Dropbox's own content hash is not interchangeable with a locally calculated SHA-256.

### R2 — REQUIRED: establish explicit dataset coverage acceptance before OFFICIAL status

The current design requires M15/H1 coverage but does not define a numeric coverage target or exact accepted history interval. This is intentionally not guessed. Before reconstruction or canonical acceptance, the owner must approve required start/end UTC boundaries for M15 and H1; complete-coverage or acceptable-gap policy; treatment of first/last partial history boundaries; and whether the dataset includes all source-available candles or a bounded interval.

Until those values are approved and validated, a snapshot cannot be marked OFFICIAL / VERIFIED.

### R3 — REQUIRED: make external provenance manifest a mandatory companion

The inspected SQLite schema stores candle identity, OHLCV and available_at_ms; it does not persist dedicated dataset lineage, source retrieval manifest, scheduler cursor or recovery checkpoint. The manifest must therefore be mandatory for every accepted snapshot and bound to the database by exact filename, byte size and SHA-256. A missing, malformed or digest-mismatched manifest makes the snapshot ineligible for restore/acceptance.

Do not imply manifest metadata is present in SQLite rows. Keep source-level facts, retrieval history and dataset acceptance in the external manifest/evidence.

### R4 — REQUIRED: clarify safe SQLite snapshot and restore filesystem handling

The publisher should use Python SQLite's online backup interface (Connection.backup) to copy a consistent database image from the live primary to a staging database. Do not copy the live .sqlite3, -wal or -shm files independently. Validate only after the staged backup connection is closed.

Restore must use a new, empty destination directory/path with no pre-existing database or stale -wal/-shm sidecars. Verify downloaded bytes before opening the file; open read-only for validation; do not start a writer or perform primary cutover. Any later writable activation requires separate approval and a fresh fencing/lease review.

### R5 — REQUIRED: define manifest integrity and status transitions

The manifest must include format/schema version, dataset lineage, snapshot ID, UTC timestamps, SQLite schema/user_version, per-timeframe interval/count/min/max/gaps, validation results, snapshot byte size and SHA-256, and Dropbox object ID/revision. It must not contain credentials or tokens.

Suggested explicit transitions: STAGED → VALIDATED_LOCAL → UPLOADED_NOT_RESTORE_VERIFIED → RESTORE_VERIFIED → OFFICIAL (only after owner acceptance). Any validation failure, ambiguous Dropbox object, missing manifest, or digest mismatch → QUARANTINED. Upload success alone never implies restore verification or official acceptance.

### R6 — INFORMATIONAL: schema version is currently SQLite user_version

The current empty-only initializer sets PRAGMA user_version = 1. The snapshot validator should inspect that value as well as exact expected tables, columns, constraints and indexes. Do not infer schema version from filename or manifest alone.

## Existing implementation observations

- market_data/store.py uses WAL mode and defines the candles table; the empty-only initializer adds feeder_leases and sets user_version=1.
- The candle primary key prevents duplicate identity tuples at the SQLite constraint level, but a validator must still report counts and timestamp continuity per timeframe.
- Candle construction validates supported market/timeframes, timestamp alignment, closed-candle availability, decimal bounds and OHLC range consistency. A backup validator should independently scan persisted rows through equivalent contract validation; integrity_check alone does not establish semantic correctness.
- Scheduler completion watermarks are in-memory in the inspected implementation; do not represent them as recoverable from the SQLite snapshot.
- No Dropbox/snapshot/restore implementation was found in the reviewed files.

## Phase 1 status

| Item | Status |
|---|---|
| Primary vs Dropbox role separation | PASS |
| Online Backup API / no live-file sync rule | PASS — design requirement only |
| Dropbox no-overwrite and object revision verification | REQUIRED SPECIFICATION UPDATE |
| M15/H1 numeric coverage acceptance | BLOCKED pending owner-defined target |
| Mandatory provenance manifest | REQUIRED SPECIFICATION UPDATE |
| SQLite snapshot/restore sidecar isolation | REQUIRED SPECIFICATION UPDATE |
| Implementation/tests/restore drill | NOT IMPLEMENTED / NOT RUN |
| Independent second-person review | NOT PERFORMED |

## Scope and restrictions

This review made no source, test, workflow, dependency, schema, data, Dropbox, VPS or runtime changes. No SQLite database was opened. No data was downloaded, copied, exported, snapshotted, uploaded or restored. No tests or workflows were run; no run, job or artifact exists.

Phase 1 remains design/static review only. Any reconstruction, Binance access, database creation, Dropbox operation, restore drill, VPS/runtime activation, writer/lease/feeder operation or primary cutover requires separate explicit approval.

## Next step

Update the design document with R1–R5. Keep numeric coverage acceptance unresolved until the owner approves exact boundaries and gap policy. Then request owner review of the clarified design before any implementation proposal.