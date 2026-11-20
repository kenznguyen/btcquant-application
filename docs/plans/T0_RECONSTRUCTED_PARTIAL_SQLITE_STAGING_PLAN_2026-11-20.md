# T0 Reconstructed Partial Coverage — Isolated SQLite Staging Plan

Date: 2026-11-20  
Status: **RAW ARCHIVE MATERIALIZATION APPROVED — CONDITIONAL ON EXACT DESTINATION PREFLIGHT; PREFLIGHT NOT RUN**  
SQLite creation/write/import remains **NOT AUTHORIZED** and requires a separate explicit owner decision.

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

## 4. Preflight gate — exact destination; must precede every archive request

The owner decision `docs/decisions/T0_RECONSTRUCTED_ARCHIVE_MATERIALIZATION_APPROVAL_2026-11-20.md` is the controlling authorization. It already approves raw materialization of exactly the committed 404-object allowlist, subject only to a successful preflight of this exact target:

`/srv/btcquant/staging/t0-reconstructed-btcusdt-20261120-run-001`

No second materialization approval is required for this same allowlist, source, byte cap and target. This plan does not broaden or amend that approval. Before any DNS lookup, object request, listing or transfer, verify and record all of the following against the exact target:

- Local filesystem is owner-controlled, mounted and writable by the intended owner; record canonical mount point, filesystem type/device or volume identity, mount options, owner UID/GID, mode/ACL and free bytes/inodes.
- Target and every existing parent component are inspected with `lstat`/equivalent; no component may be a symlink. Resolve and record canonical path and prove it is outside Dropbox-synchronized roots and operational T0/database paths.
- Target does not exist, or if the approval explicitly expects an already-created empty run root, it is a real directory with no entries. The materialization process must not adopt or overwrite any pre-existing file. Do not create the target during preflight unless the owner decision expressly permits that; the current approved path must be treated as create-only.
- Sufficient capacity exists for the 100 MiB transfer ceiling plus filesystem overhead and a documented safety reserve; verify free bytes and inodes.
- Parent directory permissions prevent untrusted substitution between preflight and write. The eventual writer must revalidate with directory file descriptors and no-follow semantics, use atomic exclusive creation (`O_CREAT|O_EXCL|O_NOFOLLOW` or platform equivalent), write to a unique temporary file within the same directory, fsync, then atomically publish without replacing an existing target. If the platform cannot provide equivalent guarantees, STOP.
- Record preflight timestamp, operator identity, exact path, mount/filesystem evidence, path-component inspection, free capacity, permissions, and PASS/FAIL per item. Any failed or unverifiable item means STOP. No alternate destination without a new owner decision.

The preflight itself is read-only. A passing preflight is necessary but does not authorize SQLite. No archive network activity is allowed before it passes.

The archive provenance inventory is a separate artifact from the final reconstructed dataset/build manifest. The 404-entry inventory is complete for object identity and ZIP/sidecar pairing; sidecar own historical size/hash metadata is unavailable. The final dataset/build manifest is NOT FINAL and must be generated from fresh materialization and validation evidence, not inferred from this inventory.

Before any later SQLite approval, separately confirm Candle Contract 1.1.0, SQLite `user_version=1`, exact table definitions, primary key, indexes and constraints against the exact source SHA. `available_at_ms` must be a deterministic first-observation/import timestamp, not historical candle close time. Any schema extension is a separate decision.

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

This layout is illustrative only. For the already approved raw materialization, the only permitted run root is `/srv/btcquant/staging/t0-reconstructed-btcusdt-20261120-run-001`; do not substitute `<approved-local-root>` or choose another path. Create only after exact-path preflight passes. SQLite subdirectory/database creation remains prohibited until a separate explicit SQLite approval.

## 6. Execution phases — each separately gated

### Phase A — raw archive materialization (already approved; conditional gate)

- Existing owner approval authorizes exactly 404 objects: 202 ZIP + their 202 paired `.CHECKSUM` sidecars, from the official Binance Public Data S3-compatible source, to the exact target in Section 4, with a hard 100 MiB transfer ceiling including retries. No new approval is needed for this exact scope; any changed object, source, destination, cap or retention condition requires a new owner decision.
- This phase may begin only after the exact destination preflight in Section 4 is fully PASS and recorded. No bucket listing, wildcard discovery, DNS/object request or transfer before that gate.
- Do not request REST tail or any object outside the committed 404-key allowlist. Use bounded concurrency, connect/read timeouts and bounded retries; retries must not reset the byte counter.
- Define the 100 MiB ceiling as cumulative HTTP response-body bytes received across all 404 objects and every attempt, including failed/partial retry bodies; request/response headers and transport framing are not included. Count bytes as chunks arrive, before writing each chunk; if `total + next_chunk > 104857600`, abort immediately before writing that chunk, stop all requests and quarantine the run. Do not rely on `Content-Length` as the enforcement mechanism. Record both per-attempt and cumulative counts. No unmetered retry or restart.
- Create each destination file atomically and exclusively with no-follow semantics; reject any existing target, symlink, path substitution or unexpected directory entry. Never overwrite. Preserve original bytes exactly.
- For each ZIP, verify exact expected byte size and SHA-256 from the committed inventory, ZIP CRC, exactly one CSV member, and the pinned 12-column CSV contract below. For each sidecar, independently measure actual byte size and raw payload SHA-256; parse its asserted ZIP digest and compare it to the actual paired ZIP payload SHA-256. Never treat the asserted ZIP digest as the sidecar's own hash.
- Sidecar parser contract: accept strict UTF-8/ASCII-compatible text only, no BOM or NUL, with exactly one non-empty record and at most one terminal LF or CRLF; reject bare CR, multiple records, leading/trailing whitespace, extra tokens, malformed/non-hex digest, or more than one 64-hex token. The record must be exactly `<64 lowercase-or-uppercase hex digest><one-or-more ASCII spaces or tabs><exact ZIP basename>`; basename must equal the paired allowlist key's final path component. No filename/path normalization, case folding or permissive token search. Store normalized asserted digest separately from raw sidecar byte count and raw sidecar SHA-256. If actual historical sidecar bytes/hash were not retained, keep them NOT_VERIFIED; fresh run values do not rewrite historical evidence.
- ZIP CSV contract: exact Binance USD-M kline source columns, in order: `open_time, open, high, low, close, volume, close_time, quote_asset_volume, number_of_trades, taker_buy_base_asset_volume, taker_buy_quote_asset_volume, ignore`. A header, when present, must match this exact ordered list byte-for-byte after CSV decoding; otherwise the first record is data. Header/no-header behavior must be consistent with the validated archive inventory per object (76 header / 126 no-header overall); do not infer dynamically from arbitrary first-row text. Every data row must have exactly 12 fields.
- Per-object CSV values: parse timestamps/trade count as base-10 integers; parse decimal quantities/prices using exact decimal arithmetic (never binary float). `open_time` and `close_time` are UTC milliseconds; `close_time == open_time + interval_ms - 1`. All price fields are finite and strictly positive; `high >= max(open, close, low)` and `low <= min(open, close, high)`; `volume`, `quote_asset_volume`, `taker_buy_base_asset_volume`, and `taker_buy_quote_asset_volume` are finite and non-negative; taker-buy volumes must not exceed their corresponding total volumes; `number_of_trades` is an integer >= 0; `ignore` must parse as finite decimal but is retained raw and is not used as a candle feature. Reject NaN, Infinity, exponent overflow, empty numeric fields, negative quantities, invalid decimal syntax and any precision loss. Preserve original raw ZIP/CSV payloads and all 12 source fields in audit output; fields not represented in CandleStore remain preserved, not silently discarded.
- Preserve source key, timeframe, period/date, expected and measured bytes, ZIP raw SHA-256, sidecar raw SHA-256 and asserted ZIP digest, row count, header mode, source response metadata, retrieval timestamp, tool/version/config identity, validation result, destination relative path and file identity (device/inode or equivalent), per-attempt byte counts and error/quarantine reason.
- Any missing/extra object, checksum/size mismatch, invalid sidecar/ZIP/CSV, row-count mismatch, unsafe path, cap breach or unresolved defect quarantines the entire run. No partial silent continuation and no automatic daily fallback.

### Phase B — normalization and source reconciliation

- Parse CSV using the pinned 12-column order and per-object header mode from the validated evidence; do not guess based on row content alone.
- `open_time` is the UTC candle-open timestamp in integer milliseconds. For timeframe interval `Δ` (900,000 ms for M15; 3,600,000 ms for H1), require `open_time >= 0`, `open_time % Δ == 0`, and `close_time == open_time + Δ - 1`. Compare filename date/month to the first and last open times in UTC.
- Compare exact decimal values and OHLCV invariants as specified in Phase A. Normalize approved Candle Contract fields without binary floating-point conversion, implicit rounding or precision loss.
- Preserve raw archive payloads and an auditable mapping of all 12 source fields. Source-only fields (`close_time`, `quote_asset_volume`, `number_of_trades`, both taker-buy volumes and `ignore`) remain in raw evidence; no schema extension is authorized.
- Deduplicate only rows with the same canonical identity `(exchange, market_type, symbol, timeframe, open_time_ms)` AND byte-for-byte equivalent canonical normalized payload under a documented decimal normalization. Conflicting payloads for one identity quarantine the run.
- Expected grid is half-open `[first_observed_open_time, last_observed_open_time + interval_ms)` independently per timeframe. For each timeframe, enumerate every expected UTC open-time identity at interval Δ; report missing, unexpected/out-of-range and duplicate identities as structured records. Do not claim anything before the first observed open or after the last observed close. Archive boundary limitations remain distinct from internal gap results. No interpolation, forward-fill, synthetic candle or implicit gap waiver.
- Record expected/observed/missing/extra/duplicate counts and exact identity lists or deterministic digest plus a separately retained complete machine-readable gap report. Any unexplained difference quarantines the run.

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
- The existing owner decision resolves the new-run treatment: all 202 sidecars are part of the exact approved 404-object set. Measure each sidecar's own byte size and raw SHA-256 during the approved retrieval, parse its asserted ZIP digest and compare that assertion with the paired ZIP's actual payload SHA-256. Historical sidecar own size/hash remains NOT_VERIFIED and must not be backfilled or inferred.

## 8. Approval gates and current status

- Controlling owner decision: `docs/decisions/T0_RECONSTRUCTED_ARCHIVE_MATERIALIZATION_APPROVAL_2026-11-20.md` (`APPROVED — CONDITIONAL ON DESTINATION PREFLIGHT`).
- Exact approved scope: exactly 404 allowlisted objects (202 ZIP + 202 paired sidecars), official Binance Public Data S3-compatible source, exact destination `/srv/btcquant/staging/t0-reconstructed-btcusdt-20261120-run-001`, 100 MiB cumulative response-body ceiling including all retry attempts, bounded retries/concurrency, create-only raw preservation. This plan only operationalizes the already approved conditions; it does not authorize any changed scope.
- The 11,277-byte historical aggregate discrepancy is accepted as an unexplained reporting/reconciliation discrepancy. Preserve historical figures. New run measures every object individually and computes a fresh aggregate; it does not need to match the historical aggregate. Any per-object mismatch quarantines the run.
- Current status: **APPROVED — PREFLIGHT PENDING / NOT RUN**. The target has not been verified or created. If preflight fails or any requirement cannot be verified, STOP; no alternate destination without a new owner decision. No archive network request before preflight PASS.
- The 404-entry archive-object provenance inventory is **IDENTITY COMPLETE / METADATA PARTIAL**; it is not the final dataset/build manifest. The final reconstructed dataset/build manifest remains **NOT FINAL / NOT GENERATED** until fresh raw retrieval and validation evidence exist.
- SQLite creation/open/write/import remains **NOT AUTHORIZED** and requires a separate explicit owner decision for exact destination and source SHA. Normalization, database build, validation, Dropbox, restore, runtime and cutover are not authorized by the raw archive materialization decision.

| Phase | Scope | Status |
|---|---|---|
| Owner acceptance of archive as partial | Decision only | APPROVED |
| Manifest draft and staging plan | Documentation/static | AUTHORIZED |
| Raw archive materialization | Exact 404-object allowlist, exact target, 100 MiB incl. retries; conditional preflight | APPROVED — PREFLIGHT PENDING / NOT RUN |
| Normalization/source reconciliation | Parse and reconcile materialized raw payloads | NOT AUTHORIZED — separate gate |
| SQLite creation and writes | New disposable DB only | NOT AUTHORIZED — separate owner approval required |
| SQLite validation | Read-only after approved build | NOT AUTHORIZED |
| Dropbox snapshot | Immutable upload/read-back | NOT AUTHORIZED |
| Restore drill | New isolated destination | NOT AUTHORIZED |
| Operational primary / runtime / cutover | Separate governance | NOT AUTHORIZED |

## 9. Explicit non-actions for this increment

- This documentation revision accessed only repository documentation; no market-data endpoint or archive was accessed.
- No raw payload was downloaded, copied or materialized.
- No SQLite file was created, opened or modified.
- No Dropbox, VPS, runtime, feeder, writer, lease, deployment or cutover action occurred.
- No source code, schema, dependencies, tests or workflows were changed or run.
