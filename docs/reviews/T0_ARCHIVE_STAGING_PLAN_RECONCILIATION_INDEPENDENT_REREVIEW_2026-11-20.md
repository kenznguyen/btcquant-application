# Independent re-review — reconciled T0 archive staging plan and verification rules

Date: 2026-11-20  
Repository: `kenznguyen/btcquant-application`  
Branch: `main`  
Reviewed plan blob: `b35e25d5d52a09dc73cfb1ced91b408a4979b045`  
Review type: read-only independent document, approval, and manifest consistency review

## 1. Disposition

**DOCUMENT RECONCILIATION PASS — EXECUTION REMAINS BLOCKED ONLY BY THE REQUIRED DESTINATION PREFLIGHT.**

The staging plan now reflects the existing owner approval for exactly 404 raw archive objects, conditional on a successful preflight of the one approved local target. The plan no longer says that another materialization approval is required. SQLite creation, opening, import and writes remain explicitly unauthorized and separately gated.

The plan distinguishes the archive-object provenance inventory from the final reconstructed dataset/build manifest, and replaces the stale sidecar-approval condition with fresh per-sidecar measurement requirements for the already approved run.

This is a documentation-only review. It does not establish that the destination filesystem is safe, that the archive payloads are currently retrievable, or that the new run has passed data validation.

## 2. Reviewed source artifacts

| Artifact | Blob SHA |
|---|---|
| Updated staging plan | `b35e25d5d52a09dc73cfb1ced91b408a4979b045` |
| Owner approval | `87a2be9ea1ca16f1ce3d5a27a9349c1132da698b` |
| 404-object provenance inventory | `eb251ac0924b46add906123f99b82e054d887a59` |
| Historical payload-validation evidence | `45386fa75a61039ed12e7b6b0f18e48b2f1ef725` |

## 3. Independent manifest cross-check

Recomputed against all manifest object records:

| Check | Result |
|---|---:|
| Unique object records | 404 / 404 |
| ZIP / sidecar records | 202 / 202 |
| ZIP rows with positive byte size, lowercase SHA-256 and PASS state | 202 / 202 |
| ZIP-to-sidecar key pairing | 202 / 202 |
| Sidecar-to-ZIP key pairing | 202 / 202 |
| Historical sidecar own byte size/hash retained | 0 / 202 — correctly NOT_VERIFIED |
| M15 rows | 241,440 |
| H1 rows | 60,360 |
| Total ZIP rows | 301,800 |

The inventory remains identity-complete but sidecar-own-metadata partial. The sidecar's asserted ZIP digest is not the sidecar's own digest. The historical aggregate discrepancy of 11,277 bytes remains accepted and unexplained; no historical figure was rewritten or allocated to individual objects.

## 4. Authorization consistency

**PASS.** The plan now states:
- Exactly 404 objects: 202 ZIP plus 202 paired `.CHECKSUM` sidecars.
- Official Binance Public Data S3-compatible source.
- Exact target: `/srv/btcquant/staging/t0-reconstructed-btcusdt-20261120-run-001`.
- Hard 100 MiB cumulative HTTP response-body byte ceiling, counting every retry/partial response; streaming enforcement before writing an over-limit chunk.
- Bounded concurrency/retries, create-only raw preservation and quarantine on any mismatch.
- No alternate destination, no REST tail, and no broader object discovery.
- No new approval is required for this exact previously approved scope; any deviation requires a new owner decision.

The plan defines the 100 MiB operational counter as response-body bytes, excluding HTTP headers and transport framing. It counts every object response and retry body. This is an explicit measurable implementation of the approved archive-transfer cap; it must not be reset by retry or process restart.

## 5. Verification-rule review

The following deterministic rules are now present:

1. **Destination safety:** read-only preflight; inspect every existing path component with `lstat`; reject symlinks; prove owner-controlled local mount, path isolation, ownership, permissions, capacity and inode availability; stop on any unverifiable condition.
2. **Create-only writes:** revalidate path at write time; directory-FD/no-follow semantics; exclusive creation; no overwrite; same-directory temporary file, fsync and atomic publication.
3. **Sidecar parser:** strict encoding and line grammar; exactly one digest and exact paired ZIP basename; reject malformed, multiple, ambiguous or extra tokens; record raw sidecar SHA/size separately from asserted ZIP digest.
4. **Transfer accounting:** count each response body as streamed, including failed and partial retries; abort before the next chunk would exceed 104,857,600 bytes; record per-attempt and cumulative counters.
5. **CSV contract:** pin the 12 Binance USD-M kline fields and order; deterministic exact-header detection; 12 fields per data row; record fresh per-object header mode and reconcile 76 header / 126 no-header across the full set.
6. **Numeric/OHLC checks:** exact decimal parsing; integer timestamp/trade-count parsing; finite values; positive prices; OHLC consistency; non-negative volumes; taker-buy quantities bounded by total quantities; no binary-float conversion or precision loss.
7. **Time/grid checks:** UTC open-time milliseconds; exact M15/H1 alignment; close-time relation; half-open expected grid; separate internal missing/extra/duplicate identities from archive-boundary limitations.
8. **Evidence:** per-object response metadata, retrieval time, measured bytes, raw hashes, asserted digest, validation result and destination file identity; run-level tool/config identity, allowlist, time bounds, transfer counters and quarantine reason.
9. **No silent repair:** no synthetic candles, interpolation, forward-fill, gap waiver, silent omission or automatic daily fallback.

**Qualification:** the historical payload-validation report records the 12-column structure and aggregate header counts but does not reproduce the literal header names or a per-object header-mode map. The updated plan therefore pins the expected Binance USD-M column schema, uses exact-match header detection, records the newly observed mode per object, and requires fresh run counts to reconcile to 76/126. The actual payload/header checks remain NOT RUN until the separately approved materialization occurs. Do not represent this static review as a revalidation of the old payloads.

## 6. Status matrix

| Area | Status | Basis |
|---|---|---|
| Plan authorization language | **PASS** | Matches controlling conditional owner approval |
| Exact object set / destination / transfer cap | **PASS — DOCUMENT** | Cross-checked with owner decision |
| Provenance inventory identity and pairing | **PASS** | Independently recomputed across 404 entries |
| Historical sidecar own-object metadata | **NOT VERIFIED** | Not retained; fresh values required in new run |
| Data verification rules | **PASS — DOCUMENT; PAYLOAD NOT RUN** | Deterministic fail-closed requirements now specified |
| Destination preflight | **NOT RUN / BLOCKING** | No filesystem evidence |
| Raw archive materialization | **APPROVED — CONDITIONAL; NOT RUN** | Exact preflight still pending |
| Normalization / SQLite / Dropbox / runtime | **NOT AUTHORIZED** | Separate owner approvals required |

## 7. Recovery and execution history

During the documentation update, an intermediate GitHub contents write briefly created an empty staging-plan blob in commit `2c9cf6138da440ed00b4f6349434e470a6cc13cf`. The plan was immediately restored from the prior committed source and then updated; the final reviewed plan is blob `b35e25d5d52a09dc73cfb1ced91b408a4979b045`. No other file or runtime/data asset was changed by that intermediate write. The intermediate commit remains in branch history and is disclosed here for auditability.

## 8. Explicit non-actions and next gate

No destination preflight, archive listing/request/download, staging, SQLite, Dropbox, REST tail, VPS/runtime, feeder/writer/lease, T1/T2, restore, deployment, cutover, cleanup or auto-delete was performed. No tests or GitHub Actions workflows were run; no workflow run/job/artifact was generated.

**Next permitted action:** perform the read-only preflight of the exact approved target. If every check passes, raw materialization may proceed only within the existing 404-object/100 MiB approval. If any check fails or cannot be verified, STOP; do not choose another path. SQLite remains separately unauthorized.
