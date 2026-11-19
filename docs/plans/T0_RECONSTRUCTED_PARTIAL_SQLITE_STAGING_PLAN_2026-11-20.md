# T0 Reconstructed Partial Coverage — Isolated SQLite Staging Plan

Date: 2026-11-20  
Status: **PREPARED — NOT AUTHORIZED FOR EXECUTION**

## 1. Objective

Prepare a controlled, reproducible plan to build a disposable staging SQLite dataset from the previously validated Binance USD-M BTCUSDT M15/H1 archive evidence, with lineage `RECONSTRUCTED` and acceptance label `RECONSTRUCTED — PARTIAL COVERAGE`.

This plan does not create or open a database, fetch market data, copy raw archives, start a feeder/writer, or change the operational primary.

## 2. Immutable scope

- Market: Binance USD-M perpetual BTCUSDT.
- Timeframes: M15 (900,000 ms) and H1 (3,600,000 ms).
- M15 observed bounds: 2019-12-31 00:00 UTC through 2026-11-18 23:45 UTC; 241,440 rows.
- H1 observed bounds: 2019-12-31 00:00 UTC through 2026-11-18 23:00 UTC; 60,360 rows.
- Validated archive partition: monthly 2020-01–2026-10; daily 2019-12-31 and 2026-11-01–2026-11-18.
- 202 ZIP + 202 checksum sidecars; 202/202 checksum matches and 202/202 ZIP/CSV structural checks passed.
- Internal continuity is PASS only within the observed archive bounds. Earliest-ever history and post-archive tail are NOT VERIFIED.
- REST tail is closed by owner decision. Do not retry or route around HTTP 451.

## 3. Hard safety boundaries

1. T0 remains an independent data asset. Do not put SQLite, WAL/SHM, raw candle payloads or bulk market data in the application Git repository.
2. Staging must be a new, isolated, owner-approved local filesystem path outside Dropbox-synchronized folders and outside any operational primary path.
3. Never point the initializer at an existing file, symlink, historical path, production path or unknown path.
4. No live primary, VPS, feeder, writer, lease, scheduler, API runtime or T1/T2 consumer may be mounted or activated.
5. No schema migration, PostgreSQL adapter, source-code change, workflow change, auto-deletion, TTL, vacuum, cleanup or retention action.
6. Preserve original ZIP/CSV payloads and source checksums. Do not silently drop archive fields that are not stored by the current CandleStore schema.
7. No synthetic candles, interpolation, forward-fill, inferred candle, silent omission or automatic gap closure.
8. No Dropbox upload, snapshot, restore, cutover or OFFICIAL / VERIFIED designation in this phase.

## 4. Preflight gate — documentation/static checks only

Before any execution approval, reviewers must confirm:

- Manifest draft is complete and machine-readable per-object provenance has been materialized from the archive validation evidence.
- The original 202 ZIP and 202 sidecar payloads are available in a newly approved isolated staging location. The previous Firecrawl temporary path is ephemeral and must not be assumed to persist.
- If re-download/materialization is needed, obtain explicit bounded owner approval defining exact object list, source, destination, byte cap, retention and checksum procedure. REST tail remains excluded.
- Record staging filesystem identity, mount type, free bytes, permissions, encryption/ownership expectations and cleanup owner. Do not use Dropbox-synchronized storage.
- Independently review the source-to-CandleStore mapping, including all 12 archive CSV columns. Current SQLite schema stores only exchange, market_type, symbol, timeframe, open_time_ms, OHLCV and available_at_ms. Preserve raw source payloads so source-only columns remain auditable; any schema extension is a separate decision.
- Confirm Candle Contract 1.1.0, SQLite `user_version=1`, table definitions, primary key, indexes and constraints against exact code SHA before any write.
- Define deterministic import timestamp semantics for `available_at_ms`; it records first observation/import time, not historical candle close time.
- Confirm manifest validator can reject missing objects, digest mismatch, unexpected row counts, invalid CSV fields, out-of-range timestamps and any unaccounted gap.

No execution starts if any preflight item is unresolved.

## 5. Proposed staging layout (not created)

Use a new unique run identifier and owner-approved local path, for example:

```text
<approved-local-root>/
  t0-reconstruction/<run-id>/
    raw/
      monthly/
      daily/
    manifests/
      source-object-inventory.json
      dataset-manifest.json
    normalized/
      btcusdt-15m.ndjson
      btcusdt-1h.ndjson
    database/
      market-data.sqlite3
    reports/
      source-validation.json
      candle-validation.json
      sqlite-validation.json
    quarantine/
```

This layout is illustrative only. Do not create directories or files until the relevant retrieval/materialization and staging approvals are explicit.

## 6. Execution phases — each separately gated

### Phase A — raw archive materialization

- Requires separate approval for exact archive object set and local staging destination.
- Do not request any REST tail or any object outside the previously approved archive partition.
- Download to unique create-only paths; never overwrite.
- Verify all 202 ZIP SHA-256 values against official sidecars, ZIP CRC, one CSV per ZIP and 12-column shape.
- Preserve source object key, timeframe, period/date, byte size, ZIP SHA-256, sidecar SHA-256, archive row count and retrieval timestamp per object.
- Any mismatch or unavailable object quarantines the run; no partial silent continuation.

### Phase B — normalization and source reconciliation

- Parse CSV with explicit header/no-header handling based on validated archive evidence; do not guess based on row content alone.
- Validate all source fields, timestamp unit, interval alignment, OHLC bounds, finite decimal values, non-negative volumes/trade counts, ordering and archive filename period.
- Normalize the approved Candle Contract fields without binary floating-point conversion or price rounding.
- Preserve raw archive payloads. Explicitly document source-only columns (e.g. quote volume, trade count, taker-buy metrics and ignore field) and their treatment; do not silently discard or add schema columns.
- Deduplicate only exact canonical-identity + complete normalized payload matches. Conflicts are quarantined.
- Compute expected UTC grid independently for M15 and H1 and compare every identity. Emit structured gap records and boundary limitations. No auto-waiver.

### Phase C — disposable SQLite construction

Requires a separate explicit owner approval for database creation and writes, including the exact empty destination path and tested source SHA.

- Create only at the new approved staging path using the existing empty-only initializer; it must refuse existing paths.
- Schema baseline: Candle Contract 1.1.0, SQLite `user_version=1`, tables `candles` and `feeder_leases`; no schema migration.
- Import candles in deterministic timeframe/open-time order with bounded transactions and uniqueness enforcement.
- Keep the database isolated; no feeder/writer/lease activation. Do not use the operational API or mount it into a running service.
- On any exception, quarantine the staging run; never overwrite or reuse a failed DB path.

### Phase D — independent read-only validation

After writes are complete and connections are closed:

- Run `PRAGMA integrity_check`; require exactly `ok`.
- Verify `PRAGMA user_version=1`, exact tables/columns/indexes/constraints and primary key.
- Query counts and min/max open times independently for M15 and H1; compare with the manifest.
- Recompute the expected UTC grid, gaps, duplicates, OHLC constraints, timestamp alignment and `available_at_ms` semantics from the database.
- Compare the database rows against normalized source records and provenance inventory.
- Require exact expected row counts: M15 241,440 and H1 60,360 for the currently approved archive batch.
- Any mismatch => QUARANTINED; no acceptance promotion.

### Phase E — owner review

Provide the final machine-readable manifest, per-object inventory, validation reports, database byte size/SHA-256 and exact code SHA. Owner reviews the explicit partial-coverage boundary and gap inventory.

A successful staging build would be labeled **STAGED / VALIDATED — RECONSTRUCTED — PARTIAL COVERAGE**, not OFFICIAL / VERIFIED. Dropbox snapshot, restore drill, operational primary designation, runtime, feeder/writer and cutover each require separate approval.

## 7. Manifest completion requirements

The draft at `docs/manifests/T0_RECONSTRUCTED_BTCUSDT_M15_H1_MANIFEST_DRAFT.json` is not yet a final build manifest.

Before execution it must include:
- one machine-readable provenance entry per ZIP and checksum sidecar (404 entries);
- exact object key, object kind, timeframe, period, byte size, SHA-256, CSV row count where applicable and validation state;
- source and retrieval metadata without credentials;
- exact Candle Contract/schema mapping and explicit treatment of all source columns;
- expected/observed/missing counts and structured gap/boundary records;
- owner decision and evidence references;
- no fabricated retrieval cutoff, database metadata, snapshot revision or restore fields.

Database/snapshot/restore fields remain null or NOT_RUN until those phases are separately approved and actually executed.

## 7A. Provenance inventory result — 2026-11-20

- Machine-readable inventory: `docs/manifests/T0_BINANCE_UM_BTCUSDT_ARCHIVE_OBJECT_PROVENANCE_INVENTORY_2026-11-20.json` (404 records: 202 ZIP + 202 paired `.CHECKSUM` sidecars).
- ZIP records: all 202 have object key, byte size, SHA-256, timeframe, period, CSV row count and PASS validation; 202/202 SHA-256 values matched the paired sidecar.
- Sidecar records: all 202 object keys are deterministically paired as ZIP key + `.CHECKSUM`; each record carries the expected ZIP digest as the digest asserted by that sidecar. The sidecar object's own byte size and payload SHA-256 were not retained individually in the source report and remain `NOT_VERIFIED` (not inferred from the ZIP digest).
- Inventory status: **IDENTITY COMPLETE / METADATA PARTIAL**. It is not a claim that every sidecar has a complete independent object metadata record.
- Static cross-check: ZIP counts 38 daily + 164 monthly = 202; total inventory 404. ZIP row totals reconcile exactly to M15 241,440 and H1 60,360. Archive bounds and timeframe counts match the manifest. Selected daily/monthly periods are disjoint; overlap comparison remains NOT APPLICABLE.
- **Byte aggregate reconciliation BLOCKED:** the 202 per-object ZIP byte sizes sum to 14,910,840 bytes, but the evidence summary declares 14,922,117 ZIP bytes (difference 11,277). Adding the declared 6,916 sidecar bytes yields 14,917,756, versus the declared 14,929,033 total (same difference). Preserve both values; do not guess which summary value is wrong. Any newly approved materialization must record actual bytes per object and reconcile the aggregate before acceptance.
- Before raw materialization, approval must explicitly accept the missing historical per-sidecar size/hash fields as unavailable, or separately authorize a bounded metadata-only retrieval of the 202 sidecar objects. No such retrieval is included in the proposal below.

## 8. Approval gates and current status

- Owner approved bounded archive materialization, conditional on exact destination preflight: `/srv/btcquant/staging/t0-reconstructed-btcusdt-20261120-run-001`. Decision: `docs/decisions/T0_RECONSTRUCTED_ARCHIVE_MATERIALIZATION_APPROVAL_2026-11-20.md`.
- The 11,277-byte historical aggregate discrepancy is accepted as an unexplained reporting/reconciliation discrepancy. New run verifies each object individually and computes a fresh aggregate; it does not need to match the historical aggregate. Any per-object mismatch quarantines the run.
- Current status: APPROVED — PREFLIGHT PENDING / NOT RUN. If destination preflight fails, stop and request a new owner decision. SQLite creation/writes remain a separate approval gate.

| Phase | Scope | Status |
|---|---|---|
| Owner acceptance of archive as partial | Decision only | APPROVED |
| Manifest draft and staging plan | Documentation/static | AUTHORIZED |
| Raw archive materialization | 202 ZIP + 202 sidecars; identity inventory complete, sidecar own size/hash NOT VERIFIED | NOT AUTHORIZED |
| Normalization/source reconciliation | Read staged payloads | NOT AUTHORIZED |
| SQLite creation and writes | New disposable DB only | NOT AUTHORIZED |
| SQLite validation | Read-only after approved build | NOT AUTHORIZED |
| Dropbox snapshot | Immutable upload/read-back | NOT AUTHORIZED |
| Restore drill | New isolated destination | NOT AUTHORIZED |
| Operational primary / runtime / cutover | Separate governance | NOT AUTHORIZED |

## 9. Explicit non-actions for this increment

- No market-data endpoint or archive was accessed.
- No raw payload was downloaded, copied or materialized.
- No SQLite file was created, opened or modified.
- No Dropbox, VPS, runtime, feeder, writer, lease, deployment or cutover action occurred.
- No source code, schema, dependencies, tests or workflows were changed or run.
