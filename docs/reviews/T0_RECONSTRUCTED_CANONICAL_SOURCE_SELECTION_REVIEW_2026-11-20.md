# CURRENT STATUS OVERRIDE — 2026-11-20 — Owner approved T0 archive source partition

- Decision: `docs/decisions/T0_RECONSTRUCTED_CANONICAL_SOURCE_PARTITION_APPROVAL_2026-11-20.md`, commit `ce42ae530d5b11a46e46c4e79e573bd4b5d0f3d2`.
- Owner approved monthly USD-M archive as default bulk source for full months 2020-01–2026-10; daily archive for 2019-12-31 and 2026-11-01–2026-11-18; daily as targeted fallback/diagnostic for payload-level gaps/conflicts.
- Any retrieved daily/monthly overlap must be compared using complete normalized candle payloads. Exact duplicates may be deduplicated with both provenances retained; conflicts must be quarantined.
- REST `/fapi/v1/klines` tail remains a separate future approval gate; this decision does not authorize REST calls.
- Approval is source-partition/documentation only. ZIP/checksum body download, raw staging, market-data retrieval, SQLite, Dropbox, restore, VPS/runtime, writer/feeder and cutover remain NOT AUTHORIZED.
- Archive listing remains PASS for object-key coverage only. ZIP/checksum integrity, candle-level completeness, row counts, actual first/last candle timestamps, intra-file gaps and closed state remain NOT VERIFIED.
- Tests/workflows NOT RUN; no run/job/artifact. Documentation-only update.
- Next gate: request separate bounded approval for exact ZIP/checksum payload retrieval and validation, including staging destination and resource/retention budgets.

---

# T0 Reconstructed Canonical — Historical Source Selection Review

Date: 2026-11-20

## Status and scope

- Review type: documentation-based source comparison using Binance's published USDⓈ-M REST documentation and Binance Public Data repository documentation.
- Result: **RECOMMENDATION RECORDED — OWNER SOURCE SELECTION NOT YET APPROVED**.
- No API endpoint was called, no archive listing/object was queried, no market data was downloaded, and no raw staging/SQLite/Dropbox/runtime action was performed.
- Owner-approved coverage remains Binance USD-M BTCUSDT M15/H1 from each timeframe's independently evidenced earliest available candle through the latest fully closed candle at a recorded UTC cutoff. Lineage is `RECONSTRUCTED`.

## 1. Evidence reviewed

### Binance USDⓈ-M REST Kline endpoint

Official Binance Developer Docs identify:
- Endpoint: `GET https://fapi.binance.com/fapi/v1/klines`.
- Required `symbol` and `interval`; optional `startTime`, `endTime`, `limit`.
- Default limit 500; documented maximum 1,500.
- IP request weight varies by limit: 1 for [1,100), 2 for [100,500), 5 for [500,1000], and 10 above 1,000.
- Response is a 12-field kline tuple; open time uniquely identifies a kline. Fields include OHLC, base volume, close time, quote volume, trade count and taker-buy volumes.

Source: https://developers.binance.info/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data

Implications:
- REST supports bounded, cursor/range-based retrieval and a direct current-tail query.
- A full-history pull would require many paginated requests; request weight and retry budgets must be bounded and recorded.
- REST documentation alone does not prove the earliest BTCUSDT perpetual candle, historical completeness, or absence of gaps. Those must be evidenced during a separately approved retrieval.
- The API response has no documented per-response archive checksum; raw response bytes and local SHA-256 would be required for provenance.

### Binance Public Data historical archive

Binance's public repository documents:
- Historical public data is packaged into daily and monthly files.
- Futures data is explicitly separated into USD-M Futures (`um`) and COIN-M Futures (`cm`).
- USD-M Futures klines are sourced from `/fapi/v1/klines`; COIN-M klines use `/dapi/v1/klines`.
- Archive files have companion `.CHECKSUM` files, with SHA-256 verification instructions.
- Daily files become available the next day; monthly files are published on the first Monday of the month.
- The repository documents that archive files may be updated later for discovered issues and lists historical correction examples.

Sources:
- https://github.com/binance/binance-public-data
- https://github.com/binance/binance-public-data/blob/master/README.md
- https://github.com/binance/binance-public-data/blob/master/python/README.md

Implications:
- Archive provides a more practical bulk-history packaging format and a source-provided checksum for each ZIP.
- The `um` namespace is the relevant market-family discriminator; `cm` and `spot` must be rejected.
- Daily/monthly publication cadence means the archive alone may lag the latest closed candle at the selected retrieval cutoff.
- Since Binance can revise archive files, a checksum proves the downloaded object matches its companion checksum at retrieval; it does not prove the archive will never change or that the contents are gap-free.
- Public documentation does not establish the earliest BTCUSDT M15/H1 archive month, full archive index completeness, or the exact daily/monthly overlap behavior. Do not infer these without later read-only metadata inspection and retrieval evidence.

## 2. Comparison

| Criterion | USD-M REST `/fapi/v1/klines` | Binance Public Data archive |
|---|---|---|
| Market-family evidence | Direct USD-M Futures endpoint and `symbol=BTCUSDT` | Explicit `futures/um` vs `futures/cm` separation |
| Bulk history | Paginated requests; max 1,500 rows/request | Daily/monthly ZIP objects designed for historical bulk download |
| Latest closed candle | Best fit for same-day tail retrieval | Daily archive is next-day; monthly archive arrives first Monday |
| Integrity evidence | Preserve raw response + local SHA-256 | Companion SHA-256 checksum + local SHA-256 |
| Rate-limit burden | IP weight per request; bounded pagination needed | Object downloads; HTTP/object-service limits still need later review |
| Corrections | API reflects current served values; no immutable response version documented | Archive files can be updated; record retrieval time, object path and checksum |
| Completeness proof | Must independently enumerate expected timestamps | Must independently enumerate expected timestamps |
| Earliest history | Not established by docs alone | Not established by docs alone |

## 3. Recommended source topology (proposal only)

Recommend a **source-tiered, provenance-preserving workflow**, not silent source mixing:

1. **Bulk base:** Binance Public Data `futures/um/monthly/klines/BTCUSDT/{15m,1h}/...` for published historical months.
2. **Recent archive delta:** matching `futures/um/daily/klines` objects for dates not yet represented by the published monthly object. Confirm exact path availability and monthly/daily overlap behavior before approving retrieval.
3. **REST tail:** `/fapi/v1/klines` only for the interval after the newest eligible archive candle through the latest fully closed candle at the recorded cutoff, or for narrowly bounded archive gap investigation.
4. **Overlap reconciliation:** retain per-chunk source identity and checksum. For every overlapping candle identity, compare the complete normalized payload. Exact equality may be deduplicated with both source references retained; any conflicting payload must be quarantined. Never choose one source silently.
5. **No substitution:** Spot, COIN-M, mark-price, index-price, continuous-contract and premium-index klines are different datasets and are not substitutes for the BTCUSDT USD-M perpetual symbol klines requested here.

This proposal uses the archive to reduce bulk REST pagination and REST to close the archive publication lag. It does not yet establish which exact months/files exist or authorize any source access.

## 4. Required checks before source approval

A later, separately authorized metadata-only inspection should establish without downloading candle payloads:
- Exact archive index/listing mechanism and current `um/monthly/klines/BTCUSDT` and `um/daily/klines/BTCUSDT` object names for M15 and H1.
- Earliest object/date per timeframe and whether the first object is partial.
- Latest published daily/monthly object and the expected archive lag at the inspection cutoff.
- Companion checksum object presence, syntax, algorithm and filename binding.
- Whether daily and monthly objects overlap and how to identify the canonical preferred object for each date.
- REST documented parameter semantics, inclusive/exclusive boundary behavior, pagination progression, and server-side rate-limit headers/response behavior from current official docs. Any live request/probe requires explicit approval.
- A deterministic source-priority and conflict policy, plus request concurrency, retry/time and bandwidth budgets.

Do not use a zero-row response as proof of the earliest boundary until symbol validity, range bounds, endpoint behavior and source availability have been independently distinguished.

## 5. Recommendation and decision status

- **Preferred bulk source:** Binance Public Data USD-M (`um`) klines archive.
- **Preferred tail/completion source:** Binance USD-M REST `/fapi/v1/klines`.
- **Source selection:** PROPOSED, NOT OWNER-APPROVED.
- **Metadata-only archive index inspection:** NOT AUTHORIZED by this review.
- **REST metadata/API probe:** NOT AUTHORIZED.
- **Bulk download / reconstruction / raw staging:** NOT AUTHORIZED.
- **SQLite creation/write, Dropbox upload, snapshot, restore, VPS/runtime, feeder/writer or cutover:** NOT AUTHORIZED.
- **Data completeness, earliest boundaries, gap disposition and OFFICIAL acceptance:** NOT VERIFIED / PENDING evidence and explicit owner decisions.

## 6. Next approval gate

Request a narrow approval for **read-only metadata inspection only** of the Binance Public Data archive index/listing and relevant official documentation. It must not download ZIP candle payloads, checksum payloads beyond what is necessary to inspect listing metadata, call the REST klines endpoint, create local data files, or touch SQLite/Dropbox/runtime.

After that inspection, report exact available object names, boundaries, cadence and checksum metadata, then ask for separate approval of the source plan and bounded reconstruction budget.

**Final disposition: DOCUMENTATION REVIEW COMPLETE — SOURCE RECOMMENDATION PROPOSED; NO SOURCE ACCESS OR DATA RETRIEVAL EXECUTED.**
