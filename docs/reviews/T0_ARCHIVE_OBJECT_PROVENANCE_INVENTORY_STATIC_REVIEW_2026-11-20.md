# T0 Binance USD-M BTCUSDT archive object provenance inventory — static review

Date: 2026-11-20  
Repository: `kenznguyen/btcquant-application`  
Branch: `main`  
Reviewed baseline HEAD: `d2c1ec24ddf3dd5ddc5970d231039799960f5404`

## Scope

Read-only validation of `docs/manifests/T0_BINANCE_UM_BTCUSDT_ARCHIVE_OBJECT_PROVENANCE_INVENTORY_2026-11-20.json` against the archive payload evidence, staging plan and owner-approved materialization decision. No archive request, download, local staging, database access or runtime action was performed.

## Result

**PASS — 404/404 object identities inventoried; METADATA PARTIAL for the 202 checksum sidecars.**

| Validation | Result |
|---|---:|
| Total records | 404 |
| Unique object keys | 404 |
| ZIP records | 202 |
| Paired `.CHECKSUM` sidecar records | 202 |
| Daily ZIP | 38 |
| Monthly ZIP | 164 |
| ZIP records with key, integer byte size, 64-char SHA-256, row count and PASS validation | 202/202 |
| ZIP SHA-256 matched to paired sidecar assertion | 202/202 |
| Sidecar keys paired exactly as ZIP key + `.CHECKSUM` | 202/202 |
| Pair/link mismatches | 0 |
| M15 rows represented | 241,440 |
| H1 rows represented | 60,360 |

Static checks also confirmed all 404 keys are unique, all ZIP SHA-256 strings are lowercase 64-character hexadecimal values, each sidecar's `paired_zip_key` resolves to exactly one ZIP record, and each `expected_zip_sha256` equals that ZIP record's digest.

## Explicit metadata limitation

The 202 sidecar records do **not** contain independently retained sidecar-object byte sizes or payload SHA-256 values. Those fields remain `NOT_VERIFIED` in the inventory; the ZIP digest asserted by a sidecar is not the sidecar file's own digest. The historical evidence retained only the aggregate sidecar size (6,916 bytes), not per-sidecar measurements.

Therefore:
- Object identity and ZIP-to-sidecar pairing are complete for all 404 objects.
- ZIP payload provenance and checksum comparisons are PASS for all 202 ZIPs.
- Independent object metadata for the 202 sidecar files is **NOT VERIFIED**.
- Do not relabel the entire inventory as fully metadata-complete, and do not infer individual sidecar sizes/hashes.

## Historical aggregate discrepancy

The per-object ZIP sizes sum to 14,910,840 bytes, while the historical evidence summary states 14,922,117 ZIP bytes (difference 11,277 bytes). The summary also states 6,916 sidecar bytes and 14,929,033 total bytes. Preserve the historical figures and discrepancy as accepted by the owner; do not fabricate a per-object allocation or rewrite the historical evidence. A new materialization must measure all 404 objects individually and compute a fresh aggregate.

## Evidence and source references

- Inventory path: `docs/manifests/T0_BINANCE_UM_BTCUSDT_ARCHIVE_OBJECT_PROVENANCE_INVENTORY_2026-11-20.json`
- Inventory blob SHA at reviewed baseline: `eb251ac0924b46add906123f99b82e054d887a59`
- Payload validation evidence: `docs/evidence/T0_BINANCE_UM_BTCUSDT_ARCHIVE_PAYLOAD_VALIDATION_2026-11-20.md`
- Staging plan: `docs/plans/T0_RECONSTRUCTED_PARTIAL_SQLITE_STAGING_PLAN_2026-11-20.md`
- Owner approval: `docs/decisions/T0_RECONSTRUCTED_ARCHIVE_MATERIALIZATION_APPROVAL_2026-11-20.md`
- Approved exact staging target: `/srv/btcquant/staging/t0-reconstructed-btcusdt-20261120-run-001`

## Status and next gate

- Inventory identity: **PASS — 404/404**.
- ZIP payload provenance/checksum linkage: **PASS — 202/202**.
- Sidecar independent byte-size/SHA-256: **NOT VERIFIED — 202/202**.
- Historical aggregate reconciliation: **ACCEPTED DISCREPANCY — 11,277 bytes; unknown root cause**.
- Materialization: **APPROVED — CONDITIONAL ON DESTINATION PREFLIGHT; NOT RUN**.
- SQLite creation/open/write/import: **NOT AUTHORIZED; separate owner approval required**.

Next permitted operation is only the exact approved destination preflight. If the path/filesystem cannot be verified as owner-controlled, local, non-Dropbox, outside operational T0 paths, new/empty, create-only, non-symlink and sufficiently provisioned, stop. Do not substitute another path. No archive transfer starts before preflight passes.

## Non-actions

No network/archive request, source download, raw file staging, SQLite operation, Dropbox action, VPS/runtime, feeder/writer/lease, T1/T2, deployment, REST tail retry, code/schema/dependency/workflow change, test run or GitHub Actions run occurred for this review. No workflow run, job or artifact was generated.
