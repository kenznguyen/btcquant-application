# Approval request — materialize validated Binance USD-M BTCUSDT archive payloads into isolated staging

Date: 2026-11-20  
Status: **PROPOSAL ONLY — NOT APPROVED — DO NOT EXECUTE**

## 1. Decision requested

Approve one bounded, read-only source retrieval/materialization operation for the exact 404 Binance Public Data USD-M archive objects already represented in:

- `docs/manifests/T0_BINANCE_UM_BTCUSDT_ARCHIVE_OBJECT_PROVENANCE_INVENTORY_2026-11-20.json`
- Source validation evidence: `docs/evidence/T0_BINANCE_UM_BTCUSDT_ARCHIVE_PAYLOAD_VALIDATION_2026-11-20.md`

The prior Firecrawl `/tmp/t0-archive-validation` directory is ephemeral and must be treated as unavailable. This proposal therefore assumes a fresh retrieval from the same official S3-compatible public archive source; it does not claim the old raw files still exist.

## 2. Exact approved-candidate scope

- Market: Binance USD-M perpetual BTCUSDT.
- Timeframes: 15m and 1h.
- Exact object set: 202 ZIP + 202 paired `.CHECKSUM` sidecars (404 objects), using only the keys in the committed inventory.
- Source: `https://s3-ap-northeast-1.amazonaws.com/data.binance.vision/`.
- Partition: monthly 2020-01 through 2026-10; daily 2019-12-31 and 2026-11-01 through 2026-11-18.
- Previously observed aggregate: 14,929,033 bytes (ZIP 14,922,117; sidecars 6,916). New execution hard cap: **100 MiB total transferred**, including retries; abort before exceeding it.
- Maximum object count: 404. No wildcard discovery or additional objects.

The inventory contains all 202 ZIP object keys and metadata. Sidecar keys are paired by appending `.CHECKSUM`; their historical individual byte sizes and payload hashes were not retained. The 202 per-object ZIP byte sizes sum to 14,910,840 bytes, 11,277 bytes below the 14,922,117 ZIP-byte aggregate stated in the historical report. The new staging operation must calculate and record actual byte size and SHA-256 for every object, then reconcile the measured aggregate and verify each sidecar's content equals its paired ZIP SHA-256. Do not backfill newly measured values into historical evidence as if previously observed.

## 3. Historical byte-total discrepancy — must be reconciled during retrieval

The historical validation report states 14,922,117 ZIP bytes and 14,929,033 aggregate bytes. However, summing the 202 individual ZIP sizes recorded in its provenance tables yields 14,910,840 bytes, a difference of 11,277 bytes. Adding the report's 6,916 sidecar aggregate gives 14,917,756 bytes, still 11,277 bytes below its declared total. This proposal preserves both values and does not assume which historical summary is correct. During any approved fresh materialization, measure each of the 404 actual payloads and reconcile the measured aggregate against the per-object inventory and historical summary. A mismatch must be reported and the run quarantined pending owner review; do not silently accept it.

## 4. Staging destination and retention

Approval must name one exact, new local destination path. It must:

- Be on an owner-controlled local filesystem, outside Dropbox-synchronized folders and outside all operational T0/database paths.
- Be empty and newly allocated for a unique run ID; no symlink, existing DB, production path or unknown path.
- Have filesystem identity, mount type, free space, permissions and ownership recorded before transfer.
- Be create-only; never overwrite or reuse a prior run directory.
- Preserve raw ZIP and sidecar bytes unchanged alongside the inventory and retrieval report.
- Be retained until owner review and a separate cleanup decision. No TTL, auto-delete, vacuum or automatic cleanup.

If no compliant destination can be confirmed, do not start.

## 5. Required execution and validation

1. Verify exact 404-key allowlist against the committed inventory; reject any extra key.
2. Retrieve only those objects from the source above, with bounded concurrency, per-object timeout, retry cap and the 100 MiB aggregate transfer ceiling.
3. Write to unique create-only files; record retrieval timestamp, HTTP/object metadata, actual bytes, SHA-256 and result for every object.
4. For each ZIP, verify its SHA-256 against the digest asserted by its paired sidecar, ZIP CRC, exactly one CSV, 12 columns, explicit header/no-header handling and expected row count.
5. For each sidecar, record its own byte size and SHA-256 and verify its parsed digest matches the ZIP SHA-256. A sidecar mismatch, missing object, unexpected size, or validation error quarantines the entire run; no silent partial success.
6. Reconcile counts: 404 objects total; 202 ZIP; 202 sidecars; 241,440 M15 rows; 60,360 H1 rows. Preserve the previously validated bounds and no-gap result only after independently reproducing those checks on the newly materialized bytes.
7. Produce a new immutable retrieval manifest/report and aggregate SHA-256. Do not overwrite the historical evidence or draft manifest.

## 6. Explicit exclusions

This approval, if granted, authorizes only raw archive materialization and validation in isolated local staging. It does **not** authorize:

- REST Klines tail retrieval, retries, alternate endpoints/domains, proxy, geo-routing or another environment to bypass HTTP 451. Tail remains closed and NOT VERIFIED.
- Normalization/import into SQLite, SQLite initialization or any database writes.
- Schema changes, source code, dependencies, workflows or GitHub Actions changes.
- Dropbox upload/snapshot, restore, VPS/runtime, feeder/writer/lease/scheduler, API activation, T1/T2, deployment or cutover.
- Automatic deletion, retention policy activation or cleanup.
- Promotion to OFFICIAL or VERIFIED; lineage remains RECONSTRUCTED — PARTIAL COVERAGE.

SQLite creation and writes require a distinct later owner approval naming the exact empty destination and tested source SHA.

## 7. Approval fields required

An approval must explicitly state:
- Approved / rejected.
- Exact local staging destination path.
- Confirmation that the 100 MiB transfer cap and exact 404-key allowlist are accepted.
- Confirmation that per-sidecar size/hash will be measured during this new retrieval (not inferred from historical evidence).
- Retention: keep until owner review and separate cleanup approval; no automatic deletion.
- Confirmation that all exclusions above remain in force.

Until these fields are approved, status remains **NOT AUTHORIZED / NOT RUN**.
