# Owner decision — approve bounded T0 archive materialization into isolated local staging

Date: 2026-11-20  
Status: **APPROVED — CONDITIONAL ON DESTINATION PREFLIGHT**  
Scope: Raw archive materialization and validation only. No SQLite.

## 1. Approval

The owner approves one bounded fresh retrieval and materialization of the exact 404 Binance Public Data USD-M BTCUSDT archive objects in the committed provenance inventory, into the exact staging path:

`/srv/btcquant/staging/t0-reconstructed-btcusdt-20261120-run-001`

The path is an approved target name, not a claim that the directory or filesystem has already been inspected or created. Before any network request, execution must verify that the parent resides on an owner-controlled local filesystem, is not Dropbox-synchronized, is outside operational T0/database paths, has adequate free space, and that the target is new, empty, create-only and not a symlink. Record filesystem/mount identity, ownership, permissions and free space. If any condition fails or cannot be verified, STOP and request a new owner decision; do not silently substitute another path.

## 2. Reviewed 11,277-byte discrepancy

The 202 ZIP per-object byte values in the historical provenance tables sum to 14,910,840 bytes, while the report summary states 14,922,117 ZIP bytes, a difference of 11,277 bytes. The report's 6,916-byte sidecar summary makes the corresponding aggregate discrepancy 11,277 bytes as well.

This is accepted as a **historical aggregate reconciliation/reporting discrepancy**, not as proof of missing candle data or missing bytes in a specific object. The available evidence does not identify the root cause. The 202 ZIP SHA-256-to-sidecar comparisons passed and the M15/H1 row counts reconcile, but those checks do not explain the summary arithmetic discrepancy.

Do not rewrite the historical report or fabricate a correction. For the new run:
- Verify each ZIP against its individually recorded expected byte size and SHA-256.
- Verify each paired sidecar's actual byte size and SHA-256 as a separate object; parse its asserted ZIP digest and compare it to the ZIP SHA-256.
- Measure all 404 object sizes and calculate a fresh aggregate from measured bytes.
- Do not require the new aggregate to equal the historical summary 14,929,033 bytes.
- Any per-object size/hash/checksum mismatch, missing object, extra object, or failed archive validation quarantines the entire run and requires owner review.

## 3. Exact bounded scope

- Source: `https://s3-ap-northeast-1.amazonaws.com/data.binance.vision/`
- Exact allowlist: 202 ZIP + 202 paired `.CHECKSUM` sidecars from `docs/manifests/T0_BINANCE_UM_BTCUSDT_ARCHIVE_OBJECT_PROVENANCE_INVENTORY_2026-11-20.json`.
- BTCUSDT Binance USD-M; M15 and H1.
- Monthly archives 2020-01 through 2026-10; daily archives 2019-12-31 and 2026-11-01 through 2026-11-18.
- Maximum 404 objects.
- Hard transfer ceiling: **100 MiB total transferred, including retries**. Abort before exceeding it. No wildcard discovery or additional keys.
- Bounded concurrency, per-object timeout and capped retries; create-only raw files; preserve original ZIP/sidecar bytes.
- Preserve until owner review and a separate cleanup decision. No automatic deletion, TTL or cleanup.

## 4. Required evidence

Record for each object: exact key, type, timeframe/period, retrieval timestamp, HTTP/object metadata, actual byte size, SHA-256, expected ZIP digest where relevant, validation result and destination file identity.

Re-run ZIP SHA/checksum, ZIP CRC, exactly-one-CSV, 12-column, header handling, row counts, timestamp ordering/continuity, duplicate and OHLC/numeric checks. Produce a new immutable run manifest/report and aggregate SHA-256. Keep historical evidence immutable.

Expected totals to verify independently: 202 ZIP, 202 sidecars, 241,440 M15 rows and 60,360 H1 rows. Preserve coverage bounds as RECONSTRUCTED — PARTIAL COVERAGE only.

## 5. Explicit exclusions

This approval does NOT authorize:
- REST Klines tail retrieval or any retry/bypass of the HTTP 451 restriction; tail remains NOT VERIFIED and closed.
- SQLite initialization, creation, opening, import, normalization into DB or any database writes.
- Schema/code/dependency/workflow changes or GitHub Actions runs.
- Dropbox upload/snapshot, VPS/runtime, feeder/writer/lease/scheduler, API activation, T1/T2, restore, deployment or cutover.
- Automatic deletion, cleanup or retention-policy activation.
- Promotion to OFFICIAL or VERIFIED.

SQLite creation/writes require a separate later owner approval naming its exact destination and tested source SHA.

## 6. Execution gate and status

Approval is effective for the bounded operation only after the exact destination preflight in Section 1 passes. Until then: **APPROVED — PREFLIGHT PENDING / NOT RUN**. If preflight passes, execute only the scope above. Any deviation requires stopping and obtaining a new owner decision.
