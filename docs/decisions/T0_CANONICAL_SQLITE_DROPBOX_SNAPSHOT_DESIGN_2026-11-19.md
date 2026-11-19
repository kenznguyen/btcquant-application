# T0 Canonical SQLite Reconstruction and Dropbox Snapshot Design — 2026-11-19

## Status and authorization boundary

- Phase 1 only: architecture design, acceptance criteria and static review.
- Current canonical SQLite backup: **NOT IDENTIFIED**; recovery readiness remains **BLOCKED / NOT VERIFIED**.
- This document does not authorize data reconstruction, exchange downloads, database initialization, SQLite writes, backup creation, Dropbox uploads, restore, VPS provisioning, runtime activation or deployment.
- Any later phase requires a separate explicit owner approval with bounded scope.

## Decision

Use a local, controlled SQLite database as the operational primary. Use Dropbox as an off-host repository for immutable, versioned, downloadable Canonical SQLite snapshots. Dropbox is not the live SQLite primary and must not host an actively written database file inside a synchronized folder.

The term **official snapshot** means a validated, immutable backup of an accepted Canonical dataset. It does not imply that the historical pre-existing database has been recovered.

## Roles

### Operational primary

- Lives on a local filesystem suitable for SQLite locking and atomic operations.
- Is the only active read/write database for the approved T0 process.
- Is not directly synchronized by Dropbox while open or being written.
- Remains independent of the application Git repository (T0 is an independent data asset).

### Dropbox snapshot repository

- Stores completed SQLite Online Backup API snapshots, not live database/WAL/SHM files.
- Retains multiple versions; never overwrites an earlier accepted snapshot.
- Makes each accepted snapshot downloadable for recovery to an approved local machine or VPS.
- Stores a manifest and integrity metadata beside each snapshot.
- Access control, account ownership, quota and retention policy must be reviewed before operational use.

## Snapshot publication protocol

1. Read a consistent SQLite snapshot using SQLite Online Backup API from the operational primary.
2. Write the snapshot to a staging path outside any Dropbox-synchronized directory.
3. Close the snapshot and run validation against the staged file.
4. Calculate SHA-256 only after the snapshot is finalized.
5. Produce a manifest that binds the snapshot filename, byte size and SHA-256 to its dataset identity and validation results.
6. Upload the completed snapshot and manifest into a new version-specific Dropbox path. Do not replace prior versions.
7. Read back/download the uploaded object when operational backup is authorized, then verify byte size and SHA-256. A successful upload alone is not proof of a usable backup.
8. Mark the version **OFFICIAL / VERIFIED** only after all required checks pass. Otherwise mark it **QUARANTINED / NOT VERIFIED** and do not use it for restore.

Suggested layout (names are illustrative, not created):
- `Canonical/BTCUSDT/RECONSTRUCTED/<snapshot-id>/market-data.sqlite3`
- `Canonical/BTCUSDT/RECONSTRUCTED/<snapshot-id>/manifest.json`
- `Canonical/BTCUSDT/RECONSTRUCTED/<snapshot-id>/validation.txt`

If a genuinely recovered original dataset is ever identified, it must use a distinct lineage namespace and retain its original provenance. Never label reconstructed data as recovered original data.

## Required manifest fields

- `format_version`, `snapshot_id`, `dataset_id`, `lineage` (`RECOVERED_ORIGINAL` or `RECONSTRUCTED`), and explicit acceptance status.
- `source_exchange` and market type (Binance USD-M), symbol (BTCUSDT), timeframe set (M15, H1), retrieval interval and retrieval timestamp where applicable.
- Snapshot creation timestamp (UTC), source database identity, schema version and application/source SHA where relevant.
- Per-timeframe first/last candle open time, row count, expected interval, detected gaps and coverage result.
- SQLite integrity result, schema validation result, duplicate check, OHLCV validation result and validation tool/version.
- Snapshot byte size, SHA-256, and the exact snapshot filename.
- For reconstructed history: retrieval method, source endpoint family, retrieval windows, pagination/cursor continuity, rate-limit/retry observations and any unavailable intervals.
- For restore: source snapshot ID, restore timestamp, target path identity, pre/post-restore validation and operator/evidence reference.

Do not include secrets, access tokens or Dropbox credentials in the manifest.

## Acceptance gates

A snapshot may be marked **OFFICIAL / VERIFIED** only when all applicable checks pass:

1. SQLite `PRAGMA integrity_check` returns `ok`.
2. Expected tables, columns, indexes and schema version match the accepted schema contract.
3. M15 and H1 record counts and first/last timestamps are recorded and meet the separately approved coverage target.
4. Missing intervals, duplicates, invalid timestamps and OHLCV invariant violations are measured and either absent or explicitly dispositioned.
5. Dataset lineage and provenance are complete; reconstructed data is explicitly labeled `RECONSTRUCTED`.
6. Snapshot SHA-256 and byte size are recorded and match the final uploaded/downloaded bytes.
7. A restore drill to a separate destination passes checksum and SQLite/schema/data validation before any restored database is eligible for use.

A backup that has not passed a restore drill may be labeled **UPLOADED / NOT RESTORE-VERIFIED**, never fully recovery-verified.

## Restore protocol

- Select a specific immutable snapshot version and verify its manifest, byte size and SHA-256 before opening it with SQLite.
- Restore/download into a new isolated destination; never overwrite the current operational primary in place.
- Run integrity, schema, M15/H1 coverage, lineage and record-count checks.
- Preserve the prior primary unchanged until explicit acceptance and cutover approval.
- Any cutover, writer/lease ownership transition or runtime activation requires separate approval and fencing/recovery review.

## Phase plan

- **Phase 1 — DESIGN / STATIC ONLY:** document architecture, manifest contract, acceptance criteria and static tests. This is the only currently authorized phase.
- **Phase 2 — RECONSTRUCTION:** separately approve source, exact history window, download limits, storage destination and reconstructed lineage before any Binance data access or DB creation.
- **Phase 3 — VALIDATION:** independently verify reconstructed dataset, schema, integrity, coverage, gaps, provenance and reproducibility.
- **Phase 4 — SNAPSHOT / DROPBOX:** separately approve SQLite Online Backup snapshot creation, Dropbox upload, read-back verification, retention and access controls.
- **Phase 5 — RESTORE DRILL:** separately approve restore into an isolated destination; no primary cutover is implied.
- **Phase 6 — CANONICAL ACCEPTANCE:** owner acceptance of dataset lineage and evidence; operational writer/runtime remains a separate authorization.

## Explicit non-goals and prohibitions in Phase 1

No database or data payload is created, downloaded, copied, exported, modified, restored or uploaded. No Dropbox folder or API action is performed. No Binance/API/exchange access, VPS/SSH, writer, lease, feeder, systemd, runtime, deployment, PostgreSQL, T1/T2, retention/deletion or trading changes are included. No live orders; paper-first posture remains unchanged.

## Phase 1 exit criteria

- Architecture clearly distinguishes operational primary from Dropbox snapshot repository.
- Snapshot publication and restore protocols prohibit synchronizing an actively written SQLite file.
- Manifest schema and official/verified acceptance gates are explicit.
- Reconstructed versus recovered-original lineage cannot be conflated.
- Later data, Dropbox, restore and runtime phases each require separate approval.

**Phase 1 disposition:** DESIGN RECORDED; static implementation checks and independent validation **NOT YET PERFORMED**; no data/runtime action authorized.


## Static review clarifications — 2026-11-19

Static review: [T0 Canonical SQLite + Dropbox Snapshot Static Review](../reviews/T0_CANONICAL_SQLITE_DROPBOX_SNAPSHOT_STATIC_REVIEW_2026-11-19.md), commit `c08d5e225140d02235206d4dabc4e24349370f3f`.

### Dropbox object publication

- Publish with Dropbox create-only/no-overwrite semantics. If the version path already exists, fail closed; do not overwrite or silently autorename.
- Record Dropbox file ID, revision, canonical path, server-reported size and modification metadata in the manifest/evidence.
- Read back the exact uploaded revision and independently verify byte size and local SHA-256. A successful upload or Dropbox content hash alone is insufficient.

### Mandatory manifest and state transitions

The manifest is mandatory for every snapshot eligible for restore or acceptance. It must bind exact snapshot filename, byte size and SHA-256, and include format version, snapshot/dataset IDs, lineage, UTC timestamps, SQLite schema version/user_version, source/retrieval provenance, M15/H1 interval/count/min/max/gaps, semantic validation results, and Dropbox file ID/revision. Never include credentials or tokens.

Suggested status transitions:
- `STAGED` → `VALIDATED_LOCAL` → `UPLOADED_NOT_RESTORE_VERIFIED` → `RESTORE_VERIFIED` → `OFFICIAL` (only after owner acceptance).
- Any validation failure, ambiguous Dropbox object, missing/malformed manifest or digest mismatch → `QUARANTINED`.
- Upload success alone does not imply restore verification or official acceptance.

### SQLite snapshot and restore filesystem rules

- Use Python SQLite `Connection.backup` to create a consistent staging snapshot from the operational primary.
- Never copy live `.sqlite3`, `-wal` or `-shm` files independently into Dropbox.
- Close the staging snapshot before validation and hashing.
- Restore only into a new empty destination path/directory without pre-existing DB or stale WAL/SHM sidecars. Verify downloaded bytes before opening; validate read-only.
- No writer startup, primary replacement, lease transfer or cutover is implied.

### Coverage gate remains owner-defined

The exact accepted M15/H1 UTC start/end boundaries and gap policy are not yet approved. They must be explicitly set before reconstruction or official Canonical acceptance. Until then, no snapshot can be marked `OFFICIAL / VERIFIED`. The validator must also report first/last timestamps and partial-boundary treatment.

### Static review findings

- R1 Dropbox no-overwrite/object revision: required specification clarification recorded.
- R2 numeric M15/H1 coverage target: blocked pending owner decision.
- R3 mandatory external provenance manifest: required specification clarification recorded.
- R4 safe SQLite backup/restore filesystem handling: required specification clarification recorded.
- R5 manifest integrity/status transitions: required specification clarification recorded.
- R6 `PRAGMA user_version` validation: informational requirement recorded.

The current implementation has no snapshot publisher, Dropbox adapter, manifest validator or restore verifier. This design is not implementation evidence.
