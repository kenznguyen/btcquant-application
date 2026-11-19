# T0 Binance USD-M BTCUSDT Archive Metadata Inspection — 2026-11-20

## Status, authorization and method

- Authorization: owner approved **read-only metadata-only inspection** of Binance Public Data archive index/listing.
- Scope executed: S3-compatible `ListObjectsV2` listing requests against bucket `data.binance.vision`, restricted to:
  - `data/futures/um/daily/klines/BTCUSDT/15m/`
  - `data/futures/um/daily/klines/BTCUSDT/1h/`
  - `data/futures/um/monthly/klines/BTCUSDT/15m/`
  - `data/futures/um/monthly/klines/BTCUSDT/1h/`
- Listing XML fields inspected: `Prefix`, `KeyCount`, `IsTruncated`, object key names, `LastModified`, ETag and object byte size for selected boundary objects.
- No ZIP object body, `.CHECKSUM` body, candle row, REST Klines endpoint or other market-data endpoint was fetched.
- No local files/raw staging, checksum validation, SQLite, Dropbox, VPS, writer, feeder, runtime or deployment action was performed.
- Retrieval cutoff for this metadata observation: 2026-11-20 UTC (inspection date; individual object LastModified timestamps are preserved below).

## 1. Monthly archive listing

Both timeframes returned a complete single-page listing:

| Timeframe | Prefix KeyCount | ZIP objects | .CHECKSUM objects | First month | Last month | IsTruncated |
|---|---:|---:|---:|---|---|---|
| M15 | 164 | 82 | 82 | 2020-01 | 2026-10 | false |
| H1 | 164 | 82 | 82 | 2020-01 | 2026-10 | false |

The 82 monthly ZIP filenames form a continuous month sequence from January 2020 through October 2026; the listing-level check found no missing or unexpected month names. Every listed ZIP had a matching `.CHECKSUM` object key.

Selected object metadata:

| Timeframe | Object | LastModified UTC | ZIP size |
|---|---|---|---:|
| M15 | `BTCUSDT-15m-2020-01.zip` | 2021-06-14T06:12:38Z | 139,485 bytes |
| M15 | `BTCUSDT-15m-2026-10.zip` | 2026-11-11T10:50:21Z | 142,135 bytes |
| H1 | `BTCUSDT-1h-2020-01.zip` | 2021-06-14T06:12:38Z | 37,271 bytes |
| H1 | `BTCUSDT-1h-2026-10.zip` | 2026-11-11T10:50:21Z | 37,961 bytes |

Selected `.CHECKSUM` sidecars were present. Their contents were not downloaded or verified. ETags were observed as metadata only and are not treated as SHA-256.

## 2. Daily archive listing

Each timeframe required six sequential listing pages. The exact page boundaries were checked from raw listing XML and the ZIP key names were programmatically enumerated.

| Page | M15 first → last filename date | H1 first → last filename date | ZIP objects per timeframe | Listing |
|---|---|---|---:|---|
| 1 | 2019-12-31 → 2021-05-13 | 2019-12-31 → 2021-05-13 | 500 | truncated |
| 2 | 2021-05-14 → 2022-09-25 | 2021-05-14 → 2022-09-25 | 500 | truncated |
| 3 | 2022-09-26 → 2024-02-07 | 2022-09-26 → 2024-02-07 | 500 | truncated |
| 4 | 2024-02-08 → 2025-06-21 | 2024-02-08 → 2025-06-21 | 500 | truncated |
| 5 | 2025-06-22 → 2026-11-03 | 2025-06-22 → 2026-11-03 | 500 | truncated |
| 6 | 2026-11-04 → 2026-11-18 | 2026-11-04 → 2026-11-18 | 15 | not truncated |

Per timeframe:
- Total ZIP keys: **2,515**.
- Total matching `.CHECKSUM` keys: **2,515**.
- Unique daily filename dates: **2,515**.
- First filename date: **2019-12-31**.
- Last filename date: **2026-11-18**.
- Duplicate filename dates: **0**.
- Missing calendar filename dates between the first and last listed dates: **0**.
- The daily object-name coverage is identical for M15 and H1.

Selected object metadata:

| Timeframe | Object | LastModified UTC | ZIP size |
|---|---|---|---:|
| M15 | `BTCUSDT-15m-2019-12-31.zip` | 2022-03-21T08:57:47Z | 4,678 bytes |
| M15 | `BTCUSDT-15m-2026-11-18.zip` | 2026-11-19T08:16:17Z | 5,116 bytes |
| H1 | `BTCUSDT-1h-2019-12-31.zip` | 2022-03-21T08:58:02Z | 1,387 bytes |
| H1 | `BTCUSDT-1h-2026-11-18.zip` | 2026-11-19T08:16:17Z | 1,564 bytes |

The latest listed daily archive file is dated 2026-11-18 and was last modified on 2026-11-19 at 08:16:17 UTC. The latest monthly file is October 2026 and was last modified on 2026-11-11 at 10:50:21 UTC.

## 3. Overlap and proposed source partition

The daily archive spans 2019-12-31 through 2026-11-18. The monthly archive spans 2020-01 through 2026-10. Therefore:
- Daily 2019-12-31 is the only listed daily boundary date before the first monthly month.
- Daily dates in 2020-01 through 2026-10 overlap the monthly archive's calendar coverage.
- Daily 2026-11-01 through 2026-11-18 is the current partial-month tail not yet represented by a monthly object in this listing.

Proposal, not owner-approved:
1. Use monthly objects as the default bulk source for complete calendar months 2020-01 through 2026-10.
2. Use the daily object for 2019-12-31 and daily objects for 2026-11-01 through 2026-11-18.
3. Retain daily archive as a targeted fallback/diagnostic source if monthly payload validation later finds missing or conflicting candles.
4. Compare full normalized candle payloads whenever two source objects are actually retrieved for overlapping dates. Do not assume monthly and daily payloads are identical based on filenames, object sizes, ETags or listing timestamps.
5. REST may be needed for candles after the latest daily archive object through the approved retrieval cutoff, but the REST endpoint was not accessed and remains a separate approval gate.

This partition avoids intentionally ingesting the same calendar days twice while preserving a route to investigate payload-level gaps. It does not prove candle-level completeness.

## 4. Important limitations

The inspection establishes **object-key coverage only**, not candle-level data coverage:
- A daily filename dated 2019-12-31 does not prove the first candle open timestamp inside that ZIP. The actual earliest M15/H1 candle remains unverified.
- A monthly object for every month does not prove that every expected candle exists inside each ZIP.
- The latest daily file date does not establish its last candle open time, close state, or whether a candle is fully closed at the intended retrieval cutoff.
- The existence of `.CHECKSUM` sidecars does not validate their contents or the downloaded ZIP bytes. No ZIP or checksum body was fetched.
- ETags are not treated as cryptographic SHA-256.
- The listing does not establish REST endpoint earliest history or current tail availability.
- Binance archive files may be revised. Preserve the exact listing observation time, object key, LastModified, size and checksum sidecar identity when a later retrieval is approved.

## 5. Disposition

- USD-M archive namespace and all four target prefixes: **PASS — LISTED**.
- Monthly object-name coverage: **PASS — continuous 2020-01 through 2026-10** for both timeframes.
- Daily object-name coverage: **PASS — continuous 2019-12-31 through 2026-11-18** for both timeframes.
- ZIP-to-`.CHECKSUM` key presence: **PASS — matching object keys exist for every listed ZIP**.
- Archive payload/checksum validity: **NOT VERIFIED**.
- Earliest actual candle timestamp and latest fully closed candle: **NOT VERIFIED**.
- REST source and current tail: **NOT INSPECTED**.
- Source topology: **PROPOSED — OWNER DECISION PENDING**.
- Dataset reconstruction, SQLite creation/write, Dropbox snapshot/upload, restore, VPS/runtime, writer/feeder and canonical acceptance: **NOT AUTHORIZED**.

## 6. Next gate

The metadata-only archive listing task is complete. Next, request a separate owner decision on the proposed source partition and a separate bounded approval for:
- any REST metadata/earliest-candle probe, if needed to establish whether REST exposes history earlier than the first daily archive object;
- downloading specified ZIP/checksum payloads into an isolated raw staging destination;
- validating archive checksums and candle-level contents.

No reconstruction or database creation is implied by this report.

**Final disposition: METADATA INSPECTION PASS — OBJECT LISTING COMPLETE FOR THE FOUR PREFIXES; CANDLE-LEVEL COMPLETENESS AND SOURCE APPROVAL REMAIN PENDING.**
