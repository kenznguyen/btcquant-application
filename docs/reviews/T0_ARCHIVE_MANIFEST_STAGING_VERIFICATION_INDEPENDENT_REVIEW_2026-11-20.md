# Independent review — archive provenance manifest, staging plan and data-verification rules

Date: 2026-11-20  
Repository: `kenznguyen/btcquant-application`  
Branch: `main`  
Reviewed source HEAD: `d947a97dc8908723de5cf2c800cd6df38d236f8c`  
Review type: read-only document/manifest consistency and control review

## 1. Overall disposition

**REVIEW COMPLETE — EXECUTION PLAN BLOCKED PENDING DOCUMENT RECONCILIATION AND DESTINATION PREFLIGHT.**

The 404-object archive provenance inventory is structurally consistent for object identity and ZIP-to-sidecar pairing. The existing payload-validation report records successful validation of the selected archive payloads. The staging plan contains a strong set of preservation, isolation, and data-quality controls.

However, the plan and approval record contain stale/contradictory authorization language, and several operational verification details should be made deterministic before execution. This review does not authorize or perform archive retrieval, materialization, normalization, SQLite creation, or runtime activity.

## 2. Exact reviewed artifacts and source identities

| Artifact | Path | Blob SHA |
|---|---|---|
| Provenance inventory | `docs/manifests/T0_BINANCE_UM_BTCUSDT_ARCHIVE_OBJECT_PROVENANCE_INVENTORY_2026-11-20.json` | `eb251ac0924b46add906123f99b82e054d887a59` |
| Staging plan | `docs/plans/T0_RECONSTRUCTED_PARTIAL_SQLITE_STAGING_PLAN_2026-11-20.md` | `99d4adc4ffb63ee22084fd5014dd3dd3da7e68cf` |
| Owner approval | `docs/decisions/T0_RECONSTRUCTED_ARCHIVE_MATERIALIZATION_APPROVAL_2026-11-20.md` | `87a2be9ea1ca16f1ce3d5a27a9349c1132da698b` |
| Historical payload evidence | `docs/evidence/T0_BINANCE_UM_BTCUSDT_ARCHIVE_PAYLOAD_VALIDATION_2026-11-20.md` | `45386fa75a61039ed12e7b6b0f18e48b2f1ef725` |
| Prior inventory review | `docs/reviews/T0_ARCHIVE_OBJECT_PROVENANCE_INVENTORY_STATIC_REVIEW_2026-11-20.md` | `f0c2b63d1cd0dee5d14db82cf7ca99f7a99b156e` |

The manifest's `generated_from.evidence_blob_sha` exactly matches the payload-evidence blob SHA above.

## 3. Independent manifest checks

Static checks were independently recomputed against all manifest records:

| Check | Result |
|---|---:|
| Object records / unique object keys | 404 / 404 |
| ZIP / checksum sidecar records | 202 / 202 |
| Daily / monthly ZIP records | 38 / 164 |
| ZIP rows with key, positive integer byte size, lowercase 64-hex SHA-256, integer row count and PASS state | 202 / 202 |
| ZIP records asserting successful paired checksum comparison | 202 / 202 |
| Sidecar keys equal paired ZIP key + `.CHECKSUM` | 202 / 202 |
| Sidecar-to-ZIP digest references resolve to exactly one ZIP and match its digest | 202 / 202 |
| Duplicate keys or dangling pair references | 0 |
| M15 / H1 rows represented | 241,440 / 60,360 |

Partition cross-check:
- M15: 19 daily ZIPs / 1,824 rows; 82 monthly ZIPs / 239,616 rows.
- H1: 19 daily ZIPs / 456 rows; 82 monthly ZIPs / 59,904 rows.
- Daily and monthly period selections are disjoint in the represented partition.

**Manifest disposition: PASS for identity, ZIP metadata and pair linkage; METADATA PARTIAL for sidecar objects.**

All 202 sidecar records correctly leave their own byte size and payload SHA-256 as `NOT_VERIFIED`. The `expected_zip_sha256` field is the digest asserted for the paired ZIP; it must not be interpreted as the sidecar file's own digest. The manifest is an archive-object provenance inventory, not by itself the final dataset/build manifest.

The historical aggregate discrepancy remains explicit: per-object ZIP sizes total 14,910,840 bytes versus the evidence summary's 14,922,117 bytes (11,277-byte difference). Including the declared 6,916 sidecar bytes yields 14,917,756 bytes versus the declared total 14,929,033 bytes. The owner decision accepts this as an unexplained historical reporting discrepancy. No value was altered or inferred.

## 4. Staging-plan and approval consistency findings

### Finding P1 — authorization language conflicts

The staging plan header says **PREPARED — NOT AUTHORIZED FOR EXECUTION**, and Phase A says a separate approval is required for the exact object set and destination. The later Section 8 and the owner decision state that the exact 404-object materialization has already been **APPROVED — CONDITIONAL ON DESTINATION PREFLIGHT**.

These statements describe different authorization states and should not coexist without an explicit distinction. The owner decision is the controlling approval: bounded raw archive materialization is approved only after the exact target preflight passes. SQLite remains not authorized and requires separate approval.

**Required correction before execution:** update the plan header and Phase A to reflect the existing conditional approval, while retaining the preflight gate and the separate SQLite approval gate. Do not broaden the approval.

### Finding P1 — inventory versus final dataset manifest is ambiguous

Section 4 says the manifest draft is complete and machine-readable provenance is materialized, while Section 7 says the draft dataset manifest is not a final build manifest. The 404-object provenance inventory is complete for object identity, but sidecar own-object metadata is partial and the dataset/build manifest is still a separate artifact.

**Required correction:** name the 404-object archive provenance inventory and the reconstructed dataset/build manifest as separate artifacts and statuses. Do not treat the inventory as a complete database-build manifest.

### Finding P1 — stale sidecar-metadata approval condition

Section 7A says a further owner decision must explicitly accept missing historical per-sidecar size/hash fields or approve a separate metadata-only retrieval. The later owner decision already resolves the issue for the approved fresh run: retrieve each sidecar as one of the exact 404 objects, measure its actual byte size and SHA-256 independently, parse its asserted ZIP digest, and compare that assertion with the ZIP payload hash.

**Required correction:** remove the stale unresolved-approval condition and restate the approved new-run measurement rule. Historical sidecar measurements remain unavailable; the new retrieval must establish fresh per-object measurements. Do not infer historical values.

### Finding P1 — destination preflight remains unverified

The approved target is exactly:

`/srv/btcquant/staging/t0-reconstructed-btcusdt-20261120-run-001`

The decision explicitly says this is an approved path name, not evidence that the path exists or is safe. No preflight evidence is present in the reviewed artifacts.

Before any archive network request, the exact path must be proven to be on an owner-controlled local filesystem, outside Dropbox and operational T0/database paths, new/empty, non-symlink, create-only, adequately provisioned, and have recorded mount/filesystem identity, ownership and permissions. Any failed or unverifiable condition means STOP; no alternate path is allowed without a new owner decision.

## 5. Data-verification rule review

### Rules already adequately specified

The plan and owner approval require:
- Exact 404-object allowlist; no wildcard discovery or additional keys.
- Official Binance Public Data S3-compatible source; REST tail excluded.
- 100 MiB hard transfer ceiling including retries.
- Per-object expected ZIP size and SHA-256 verification.
- Independent actual size and SHA-256 for every downloaded sidecar.
- Sidecar asserted digest parsed and compared to the actual paired ZIP digest.
- Fresh measured aggregate; no requirement to match the accepted historical aggregate.
- ZIP CRC, exactly one CSV member, 12-column structure and explicit header handling.
- Filename period/date compared with first/last candle timestamps.
- Timestamp unit, interval alignment, chronological ordering and continuity.
- Numeric/OHLC validation, finite values, non-negative volume/trade-count fields.
- Exact duplicate rows may be deduplicated only under the stated canonical identity plus complete normalized-payload rule; conflicts are quarantined.
- No interpolation, forward-fill, synthetic candles, silent omission or automatic gap closure.
- Preserve raw payloads and explicitly account for source-only CSV fields.
- Any missing/extra object, size/hash/checksum mismatch, invalid archive or unresolved data defect quarantines the run.
- SQLite is a separate gated phase; if later approved, it requires exact destination/source SHA, empty-only initialization, schema/user_version checks, integrity check and independent row/grid reconciliation.
- Coverage is only **RECONSTRUCTED — PARTIAL COVERAGE**. Earliest-ever history and post-2026-11-18 tail are NOT VERIFIED. REST tail remains closed.

The historical payload report records 202/202 checksum comparisons, ZIP/CSV structure checks, zero detected gaps/duplicates/out-of-order timestamps and zero reported OHLC/numeric anomalies within the selected archive bounds. This review inspected that report; it did not re-download or re-parse the payloads.

### Required clarifications before execution

1. **Checksum sidecar parser contract:** define accepted encoding/line-ending/whitespace grammar, require exactly one unambiguous 64-hex digest, reject malformed or multiple digest tokens, and record the raw sidecar hash separately from the digest it asserts.
2. **Transfer-cap accounting:** specify whether the 100 MiB counter measures response-body bytes or all network bytes; count every retry's bytes, enforce the cap while streaming (not only from Content-Length), and abort before the next chunk would exceed the cap. No wildcard/listing expansion beyond the exact committed allowlist.
3. **Create-only/path safety:** specify atomic exclusive file creation and no-follow behavior, validate parent path components against symlinks, and refuse existing targets. This should prevent a preflight-to-write path substitution.
4. **CSV schema contract:** pin the exact 12 source column names/order and header/no-header rule from the validated evidence. State the complete numeric/OHLC invariants and decimal parsing rules explicitly; retain raw source columns not represented by Candle Contract.
5. **Timestamp and grid contract:** define timestamp as UTC candle open time in milliseconds, exact interval alignment and half-open expected coverage bounds; report missing/extra identities and boundary limitations separately. No implicit gap waiver.
6. **Evidence completeness:** per object retain source key, retrieval timestamp, HTTP/object response metadata, measured bytes, raw object SHA-256, expected ZIP digest where relevant, validation result and destination file identity. Keep run-level allowlist digest, tool/version/config identity, start/end times, transfer counter and quarantine reason.

These clarifications are review findings, not permission to execute or modify the source plan.

## 6. Final status matrix

| Area | Status | Basis |
|---|---|---|
| 404-object identity and uniqueness | **PASS** | Recomputed across 404 records |
| ZIP metadata and checksum pairing | **PASS** | 202/202 |
| Sidecar independent historical metadata | **NOT VERIFIED** | Not retained in historical evidence |
| Historical aggregate reconciliation | **ACCEPTED DISCREPANCY** | 11,277 bytes; root cause unknown |
| Existing archive payload validation evidence | **PASS — HISTORICAL EVIDENCE** | Prior bounded validation report; not rerun here |
| Staging-plan authorization consistency | **BLOCKED** | Stale contradictory wording |
| Destination preflight | **NOT VERIFIED / NOT RUN** | No filesystem evidence |
| Data-verification rules | **PARTIAL — CLARIFICATIONS REQUIRED** | Rules broad and sound; deterministic parser/cap/path/schema details remain |
| Raw archive materialization | **APPROVED — CONDITIONAL; NOT RUN** | Exact owner decision; preflight pending |
| SQLite build/import/validation | **NOT AUTHORIZED** | Separate explicit owner approval required |

## 7. Permitted next work and explicit non-actions

Permitted next work is documentation-only reconciliation of the staging plan to the existing owner decision, followed by the exact approved destination preflight. The preflight must be completed before any archive network request.

No archive request/download, local staging, SQLite create/open/write/import, Dropbox, VPS/runtime, feeder/writer/lease, REST-tail retrieval, T1/T2, deployment, restore, cutover, cleanup/auto-delete, code/schema/dependency/workflow change, test run or GitHub Actions run was performed for this review. No workflow run, job or artifact was generated.
