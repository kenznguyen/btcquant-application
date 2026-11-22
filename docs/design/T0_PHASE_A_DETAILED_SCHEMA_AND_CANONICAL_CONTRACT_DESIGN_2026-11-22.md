# T0 Phase A — Detailed Native-Schema Mapping & Canonical Contract Design — 2026-11-22

- Parent architecture: `INDEPENDENT_MULTI_SOURCE_DATA_FOUNDATION` — OWNER-APPROVED.
- Priority: Phase A — OWNER-APPROVED.
- Status: **PHASE A DESIGN COMPLETE FOR OWNER REVIEW — CONTRACT FREEZE NOT APPROVED**.
- Scope: SD-01 through SD-04, SD-09 and SD-10 only.
- Implementation/runtime/database/data movement: **NOT AUTHORIZED / NOT STARTED**.
- This document supplements the Source Domain Inventory v1 and the approved Phase Priority Addendum. It does not amend T0 Candle Contract 1.1.0 or authorize a 1.2.0 implementation.

## 1. Phase A acceptance objective

Define the minimum source-to-canonical semantics for six foundational domains:

| ID | Canonical domain | Initial source / owner | Phase A target |
|---|---|---|---|
| SD-01 | Trade OHLCV candles | Binance USD-M public market data; current T0 CCXT feeder | Preserve existing T0 BTCUSDT M15/H1 closed-candle contract |
| SD-02 | Mark-price klines | Binance USD-M REST, collected by T1 | Separate candle series, price basis = MARK |
| SD-03 | Index-price klines | Binance USD-M REST, collected by T1 | Separate candle series, price basis = INDEX |
| SD-04 | Premium-index klines | Binance USD-M REST, collected by T1 | Separate candle series, price basis = PREMIUM_INDEX |
| SD-09 | Funding-rate observations | Binance USD-M REST, collected by T1 | Point-in-time observation series |
| SD-10 | Open-interest observations | Binance USD-M REST, collected by T1 | Point-in-time observation series |

The exchange is the origin of market facts. T1 is a specialized capture/adapter, not a canonical owner. T0 validates, accepts and owns canonical records. T2 and all research/training/backtest outputs are derived consumers.

**Initial market scope:** BTCUSDT, Binance USD-M perpetual. The T1 collector can capture a wider universe, but this document does not authorize broad-universe ingestion or infer that every T1 symbol is in the T0 canonical scope.

## 2. Evidence baseline and limits

### 2.1 Exact source evidence inspected

| Source | Ref | SHA |
|---|---|---|
| T1 native CSV schema | `kenznguyen/binance-futures-collector/docs/SCHEMA.md` | `895f87a8281a3f9b6d37d96b5f68568e4285bee6` |
| T1 README / capture semantics | `kenznguyen/binance-futures-collector/README.md` | `5e03d3e00bb4b1fe6ed4ed389006e50d5683c5e3` |
| T0 current Candle value/store implementation | `market_data/store.py` | `4e1b0c54bd56455abe5be0e5c7d0807e63e0bc78` |
| T0 market-data contract overview | `market_data/README.md` | `6561214efdca5108672b83809a9c12047462d72b` |
| T0 reconstruction / availability-kind design | `docs/specs/T0_CANONICAL_RECONSTRUCTION_SPEC_2026-11-21.md` | `884d26be5b368e3aa36b94bbe747396ac006a08e` |
| T0 partial archive acceptance decision | `docs/decisions/T0_RECONSTRUCTED_PARTIAL_COVERAGE_ACCEPTANCE_2026-11-20.md` | `661efd7f8d196238fea36d62118489913e67c48d` |

T1 schema documentation describes the native CSV fields and the meaning of timestamps, but it does not fully specify every source endpoint response field type, decimal precision, REST request parameters, poll cadence, server-side retention, or capture-time semantics. Where these are absent, this design marks them **NOT SPECIFIED — VERIFY BEFORE CONTRACT FREEZE**. No type, unit or API guarantee is invented here.

### 2.2 T1 common CSV envelope

Every T1 data row starts with:

| Native field | Documented meaning | Canonical handling |
|---|---|---|
| `exchange` | `binance` | Validate against registered source; canonical enum/value |
| `market` | `futures` | Resolve explicitly to Binance USD-M / USDT perpetual; do not map generic text without source registration |
| `datatype` | Data type / directory name | Validate against the registered domain-to-native-datatype mapping |
| `timestamp_ms` | UTC milliseconds; semantics vary by type | Preserve exact integer; interpret per domain below |
| `datetime_utc` | Same instant as `timestamp_ms`, ISO-8601 UTC | Redundant validation field; parse and require exact instant equality; never use as a second identity |
| `symbol` | Lowercase, e.g. `btcusdt` | Normalize only through explicit symbol mapping; canonical symbol `BTCUSDT` |

Common rules:
- Require `exchange=binance`, `market=futures`, and a registered native `datatype` for the source contract.
- Convert symbol case only after validating the source symbol against the allowlisted instrument registry. Do not infer contract type from the symbol string alone.
- Parse timestamps as nonnegative UTC Unix milliseconds using integer arithmetic. Reject float timestamps, overflow, invalid dates and disagreement between `timestamp_ms` and `datetime_utc`.
- `datetime_utc` is a human-readable duplicate, not an independent event time.
- CSV file partition path is a locator, not a canonical identity. Verify path symbol/date/datatype against every row.
- CSV files are source evidence, not the canonical store. Retain the original immutable file bytes and checksum under a separately approved evidence/staging boundary.

## 3. Domain mapping and canonical semantics

### 3.1 SD-01 — Trade OHLCV candles

**Authoritative current T0 scope:** Binance USD-M BTCUSDT, `15m` and `1h`, closed candles via CCXT `binanceusdm`. The current Candle model supports only those timeframes and BTCUSDT.

Current T0 Candle fields:

| T0 field | Type / semantics in current source | Validation / rule |
|---|---|---|
| `exchange` | fixed `binance` | Must remain Binance |
| `marketType` | fixed `USDT_PERPETUAL` | Must not collapse into generic spot/futures |
| `symbol` | fixed `BTCUSDT` | Initial allowlist only |
| `timeframe` | `15m` or `1h` | Exact supported interval |
| `openTimeMs` | nonnegative signed-64-bit UTC ms | Must align to interval |
| `closeTimeMs` | exclusive boundary = open + interval | Preserve exclusive-boundary convention |
| `open/high/low/close/volume` | bounded decimal strings | No binary-float canonicalization; positive prices, nonnegative volume; OHLC bounds |
| `isClosed` | `true` | Current contract accepts closed candles only |
| `availableAtMs` | first observation time in current live path | Must not be fabricated or backdated |
| `availabilityKind` | current live semantic `FIRST_OBSERVED` | Proposed `BAR_CLOSE_BOUNDARY` is a separate approved design for archive-derived rows only; it is not implemented |
| `quality` | `VALIDATED` | Only after all domain checks |
| `source` | current value `ccxt.binanceusdm` | Preserve adapter/source identity |

Canonical identity:
`(exchange, market_type, symbol, timeframe, price_basis=TRADE, open_time_ms)`.

Important boundary:
- Existing T0 storage primary key omits `price_basis` because it only stores trade candles. Do not alter that table or silently place MARK/INDEX/PREMIUM_INDEX rows into it.
- T1's `klines` are 1-minute WebSocket candles. Their CSV schema has OHLC, base volume, quote volume, trade count and taker buy base/quote volume, but no explicit `is_closed`, finality flag, first-seen timestamp or revision number.
- Therefore T1 1m klines are **source evidence only / NOT CANONICAL-ACCEPTANCE-READY** until the source contract can prove closed/final candle state and capture/availability semantics. They do not expand current T0 M15/H1 scope by implication.
- T0 current Candle table retains only OHLCV plus `available_at_ms`; source-object and source-row lineage must be preserved separately under a future approved provenance design. Do not discard extra native kline fields if the 1m T1 series is ever admitted.

### 3.2 SD-02 / SD-03 / SD-04 — Mark, Index and Premium-index klines

T1 documents three distinct native datatypes:
- `mark_price_klines`
- `index_price_klines`
- `premium_index_klines`

Documented native columns after the common six:
- `open`, `high`, `low`, `close` — OHLC.
- `timestamp_ms` — candle open time.
- The README/schema describe these as 1-minute OHLC series retrieved over REST.

Canonical logical record (design proposal, not a frozen DTO):

| Field | Semantics |
|---|---|
| `exchange` | `binance` |
| `market_type` | `USDT_PERPETUAL`, after registered-source validation |
| `symbol` | Canonical instrument, initially `BTCUSDT` |
| `price_basis` | Exactly one of `MARK`, `INDEX`, `PREMIUM_INDEX` |
| `interval` | Native interval; T1 documented 1m |
| `open_time_ms` | UTC ms of bar open |
| `close_time_ms_exclusive` | Derived as open + interval only after interval is confirmed |
| `open/high/low/close` | Exact decimal values, source precision preserved |
| `is_closed` | Must be proven by source response/collection contract; not present in current CSV schema |
| `source_observed_at_ms` | Only if actual source/collector observation time is captured; absent from current documented CSV |
| `t0_ingested_at_ms` | T0 receipt/commit time, distinct from source observation time |
| `quality` | Validation state |

Identity:
`(exchange, market_type, symbol, price_basis, interval, open_time_ms)`.

Rules:
- Price basis is part of identity. Mark, index and premium-index candles must never collide or overwrite one another.
- Do not infer that premium-index values use the same unit/scale convention as mark/index prices. The native schema says OHLC but does not specify the numeric unit/scale or endpoint response representation. Confirm the Binance endpoint contract and T1 parser before freezing units.
- Do not merge these series into trade OHLCV. Do not use one generic `close` field without retaining `price_basis`.
- T1 CSV has no explicit finality flag. Until a source-level closed-bar guarantee or finality marker is evidenced, rows are retained as source observations and canonical promotion is blocked.
- If later source evidence allows revisions, define revision identity and conflict policy before accepting mutable bars. Do not use last-write-wins.

### 3.3 SD-09 — Funding-rate observations

T1 native datatype: `funding_rates`.

Documented fields:
| Native field | Documented semantics | Proposed canonical field |
|---|---|---|
| `timestamp_ms` | Sample time | `observed_at_ms` / sample timestamp |
| `funding_rate` | Current funding rate | `funding_rate` exact decimal |
| `next_funding_time` | Next settlement, UTC ms | `next_funding_at_ms` |

Identity:
`(exchange, market_type, symbol, metric=funding_rate, observed_at_ms)`.

Rules:
- `next_funding_time` is a future settlement timestamp, not the sample identity and not the sample timestamp.
- Preserve funding rate as exact decimal text; do not round or cast through binary float.
- Validate `next_funding_time` as a nonnegative UTC millisecond timestamp and require it to be semantically later than the observation time where the source contract guarantees that relationship. Invalid or contradictory values are quarantined, not repaired.
- A repeated observation timestamp with identical canonical values is a replay. Same identity with a different funding rate or next-funding time is a conflict; do not overwrite.
- The schema does not state rate bounds, sign precision, poll cadence, endpoint response precision or whether multiple records can share a timestamp. These require endpoint/parser evidence before contract freeze.
- Do not turn a sampled funding rate into a realized funding payment or a funding settlement event.

### 3.4 SD-10 — Open-interest observations

T1 native datatype: `open_interest`.

Documented fields:
| Native field | Documented semantics | Proposed canonical field |
|---|---|---|
| `timestamp_ms` | Sample time | `observed_at_ms` |
| `mark_price` | Mark price at sample time | `mark_price` exact decimal |
| `open_interest` | Open interest, base units | `open_interest_base` exact decimal |
| `oi_value` | Quote-term value, documented as OI × mark price | `open_interest_quote_value` exact decimal |

Identity:
`(exchange, market_type, symbol, metric=open_interest, observed_at_ms)`.

Rules:
- Preserve all three numeric values independently. Do not drop `mark_price` or `oi_value` because the latter appears derivable.
- Validate the documented relation `oi_value = open_interest × mark_price` using exact decimal arithmetic and a tolerance/rounding rule only after source precision is confirmed. Until then, classify discrepancies as validation findings/quarantine; do not silently recompute or replace source values.
- `timestamp_ms` is the sample time, not the collector receive time.
- Repeated timestamp + identical canonical values is replay; same identity + changed values is conflict, not overwrite.
- The schema does not specify the quote currency field, decimal precision, endpoint response types, poll cadence or rounding mode. Confirm before contract freeze.
- A mark price repeated in this domain is a sample attribute and is not a substitute for SD-02 MARK candles.

## 4. Proposed common canonical envelope (logical contract only)

Every accepted Phase A record must be attributable to one registered source and one domain contract version. Proposed logical fields:

| Field | Required | Meaning |
|---|---:|---|
| `contract_name` | yes | `T0_CANONICAL_INGESTION` |
| `contract_version` | yes | Versioned schema identifier; exact version not frozen |
| `domain_id` | yes | SD-01 / SD-02 / SD-03 / SD-04 / SD-09 / SD-10 |
| `source_id` | yes | Registered origin/collector route, not free-form text |
| `source_schema_version` | yes | Exact source schema/parser version |
| `exchange`, `market_type`, `symbol` | yes | Explicit instrument identity |
| `native_datatype` | conditional | Required for T1-origin records |
| `native_timestamp_ms` | yes | Exact source timestamp and domain semantics |
| `source_observed_at_ms` | if evidenced | Actual source/collector observation time; never substitute native event/sample time |
| `t0_received_at_ms` | yes | T0 first receipt time, generated by T0 |
| `t0_committed_at_ms` | on acceptance | Durable canonical commit time |
| `source_object_sha256` | for file source | SHA-256 of exact immutable source file bytes |
| `source_object_locator` | for file source | Approved immutable object/file locator |
| `source_row_locator` | for file source | Stable row locator (e.g. byte offset or line number plus file digest) |
| `raw_record_sha256` | if raw record boundary is defined | Digest of exact raw row/message bytes; byte framing must be specified |
| `canonical_identity` | yes | Domain-specific stable identity |
| `canonical_content_digest` | yes | Digest of normalized semantic content; encoding algorithm not frozen |
| `quality_state` | yes | VALIDATED / QUARANTINED / CONFLICT etc. |
| `validation_profile_version` | yes | Exact validator version/ruleset |

**Do not freeze the digest preimage or serialization in this Phase A document.** The existing T0 candle dataset hash is not automatically a canonical ingestion digest for non-candle domains. A separate deterministic digest design and review are required.

For CSV provenance, a file SHA plus row locator identifies the evidence location; it does not prove a source-side exchange message ID. T0 must retain the original file evidence under a separately approved storage/retention policy. T1 currently documents append-only files but does not add a per-row receive timestamp to these CSV schemas.

## 5. Domain-specific timestamp contract

| Domain | `timestamp_ms` meaning | Other time fields | Never infer |
|---|---|---|---|
| SD-01 trade candles | Bar open | T0 first-observed availability | Exchange event receive time |
| SD-02 MARK candles | Bar open | T0 ingest time; source observation only if captured | Finality or collector receive time |
| SD-03 INDEX candles | Bar open | Same as above | Finality or collector receive time |
| SD-04 PREMIUM_INDEX candles | Bar open | Same as above | Unit/scale or finality |
| SD-09 funding | Sample time | `next_funding_time` = future settlement | Actual poll receive time |
| SD-10 open interest | Sample time | Mark price and OI values at sample | Actual poll receive time |

For every domain, keep at least three separate concepts where available:
1. Native event/bar/sample time.
2. Collector/source observation time (currently absent from documented T1 row schema).
3. T0 receipt/commit time.

The import time of an old file is not its original capture time. If no original collector receive time exists, store it as unknown/null and record T0 receipt separately. Never backfill a fabricated capture time from the file path, timestamp or import time.

## 6. Identity, deduplication and conflict policy

### 6.1 Identity matrix

| Domain | Stable identity proposal | Current readiness |
|---|---|---|
| SD-01 | exchange + market type + symbol + TRADE + timeframe + open time | Existing T0 candle key is valid within its narrower single-price-basis table |
| SD-02 | exchange + market type + symbol + MARK + interval + open time | Proposed; require interval and closed-bar proof |
| SD-03 | exchange + market type + symbol + INDEX + interval + open time | Proposed; require interval and closed-bar proof |
| SD-04 | exchange + market type + symbol + PREMIUM_INDEX + interval + open time | Proposed; require interval, unit/scale and closed-bar proof |
| SD-09 | exchange + market type + symbol + FUNDING_RATE + sample time | Proposed; verify timestamp uniqueness/source granularity |
| SD-10 | exchange + market type + symbol + OPEN_INTEREST + sample time | Proposed; verify timestamp uniqueness/source granularity |

### 6.2 Deterministic acceptance behavior

- **New identity:** accept only after source registration, schema, instrument, timestamp, numeric, domain and provenance validation all pass.
- **Same identity + same canonical semantic content:** `DUPLICATE_REPLAY`; no second canonical row. Preserve additional provenance as a separate source observation according to a future provenance schema.
- **Same identity + different canonical semantic content:** `CONFLICT`; no overwrite, no source-priority guess, quarantine both candidate evidence references for reconciliation.
- **Missing/ambiguous identity:** `QUARANTINED` or `REJECTED` according to whether evidence is structurally valid but insufficient, versus malformed/unauthorized.
- **Out-of-order delivery:** do not reject solely because delivery order differs from event time. Validate identity and domain semantics; checkpoint advancement must not skip uncommitted earlier source records.
- **Duplicate delivery:** at-least-once transport is assumed. A unique identity claim must be atomic in the eventual storage implementation; a read-before-insert check is not sufficient.
- **Overlapping sources:** retain both source provenance records. No direct-vs-T1 priority or archive-vs-live reconciliation rule is approved here.
- **No silent correction:** do not round, recompute, replace or select a “better” value without a versioned reconciliation decision.

### 6.3 Atomicity and acknowledgement

Future ingestion must commit canonical row, provenance link, dedupe identity and source checkpoint in one atomic durability boundary, or use an explicitly reviewed recovery protocol that cannot acknowledge uncommitted data. Acknowledgement is sent only after durable commit. Lost acknowledgement causes a retry with the same source batch/record identities; it must resolve as replay, not duplicate insertion.

The exact transaction/store layout is intentionally not selected here.

## 7. Validation matrix

| Validation | SD-01 | SD-02/03/04 | SD-09 | SD-10 |
|---|---:|---:|---:|---:|
| Registered exchange/market/symbol | required | required | required | required |
| Native datatype/domain match | T0 adapter identity | required | required | required |
| Timestamp integer/range | required | required | required | required |
| Timestamp semantics | aligned bar open | aligned bar open | sample time | sample time |
| `datetime_utc` consistency | if CSV source | required | required | required |
| Exact decimal parse / finite | OHLCV | OHLC | funding rate | mark/OI/value |
| Domain invariants | OHLC, nonnegative volume, closed bar | OHLC, finality proof | settlement time consistency | OI × mark relation |
| Stable identity | required | required | required | required |
| Source evidence locator/checksum | required for imported source | required | required | required |
| Source observation timestamp | live T0 availability contract | absent in current T1 CSV; do not fabricate | absent in current T1 CSV; do not fabricate | absent in current T1 CSV; do not fabricate |

Malformed CSV rows, unknown enum values, unsupported interval, timestamp mismatch, non-finite/overflow decimals, invalid OHLC, unsupported instrument, unproven candle finality, invalid next-funding timestamp, or OI arithmetic discrepancy must fail closed into quarantine/rejection with stable reason codes. Do not coerce invalid values to zero/null or silently skip rows.

## 8. Source stream checkpoint and file ingestion semantics

T1 documents one CSV file per symbol, datatype and UTC day; order-book diffs rotate hourly. Phase A file streams do not currently document a durable per-row monotonic sequence or original receive timestamp.

Proposed importer checkpoint identity:
`(source_id, source_schema_version, native_datatype, symbol, source_object_sha256, row_locator)`.

Rules:
- A file is immutable input once its SHA-256 is pinned for an import attempt. If bytes change, it is a different source object and must not resume under the old checkpoint.
- Row locator must be stable within the exact file bytes (byte offset preferred; otherwise line number plus file SHA and exact parser/header version).
- Header and column order are validated before reading data rows.
- Do not treat file name date as row event time; validate each row's timestamp against its expected UTC partition.
- Partial import must resume from a durable committed row/batch boundary. Do not advance checkpoint past a quarantined/uncommitted row unless a separately approved policy explicitly records a terminal quarantine outcome.
- A final unterminated/truncated row, changing file size, or file being actively appended is not an immutable completed source object. Wait for a separately evidenced closed-file boundary; do not guess based on a quiet period.
- Exact batch size, checkpoint store, file-close marker and partial-quarantine progression remain open contract items.

## 9. Synthetic contract-test design (not executed)

A later separately approved implementation should include deterministic tests at minimum:

1. Valid BTCUSDT SD-01 M15/H1 candle; timeframe misalignment; open/high/low/close inconsistency; zero/negative price; zero volume allowed; excessive decimal precision/exponent; open candle rejected.
2. MARK vs INDEX vs PREMIUM_INDEX at identical symbol/interval/open time produce three distinct identities.
3. Same price basis and same open time + same content replays; changed OHLC creates conflict without overwrite.
4. Candle timestamp and `datetime_utc` disagreement rejected; timezone/non-UTC string normalization does not change instant; millisecond precision retained.
5. Mark/index/premium interval unsupported or absent; finality absent; premium scale unknown — fail closed.
6. Funding sample time and next settlement are not swapped; identical sample replay; changed rate or settlement at same identity conflicts.
7. Open-interest source values preserved; exact arithmetic check; rounding edge cases quarantined pending approved precision rule; no silent recomputation.
8. Unknown exchange/market/symbol/datatype and source-schema version rejected.
9. File SHA mismatch, modified bytes under same claimed locator, header/column order mismatch, duplicate header, truncated row and path/row partition mismatch rejected.
10. Two concurrent deliveries of one identity cannot both create canonical rows; lost acknowledgement retry resolves to replay.
11. Out-of-order rows and interrupted file import do not advance checkpoint past uncommitted data.
12. Source observation time missing remains null/unknown; T0 import time is not mislabeled as collector receive time.
13. Same canonical record from two sources retains both provenance links; content conflict is quarantined, not resolved by implicit source priority.
14. Raw source evidence remains referenced after acceptance; no delete-on-ack behavior.

These are proposed test cases only. No test suite, workflow or fixture was run/created in this documentation task.

## 10. Unresolved items required before contract freeze

| ID | Open item | Why it blocks freeze | Required evidence/decision |
|---|---|---|---|
| A-01 | T1 REST endpoint response schema and parser version for mark/index/premium klines | CSV schema does not state full precision, unit/scale, interval source or finality marker | Inspect exact T1 implementation at pinned commit and Binance endpoint contract; owner accepts mapping |
| A-02 | T1 poll cadence and source observation/receive timestamp capture for all Phase A REST domains | CSV only exposes sample/bar timestamp, not actual collector receive time | Confirm code behavior; decide whether T1 contract must add a separate receive timestamp |
| A-03 | Funding rate numeric precision, bounds, poll interval and timestamp uniqueness | Not specified by CSV schema | Endpoint/parser evidence and owner-approved validation rules |
| A-04 | OI numeric precision, quote currency semantics, rounding rule and poll interval | CSV documents base units and quote value relation but not rounding/precision | Endpoint/parser evidence; deterministic arithmetic tolerance decision |
| A-05 | Mark/index/premium candle finality and revision policy | No finality flag in T1 CSV | Source guarantee or additive source contract field; explicit revision/conflict rule |
| A-06 | Source precedence and overlap reconciliation | T0 direct trade candles and T1 observations may overlap; no approved precedence | Owner decision; preserve dual provenance before any canonical merge |
| A-07 | Canonical digest byte encoding and schema-version evolution | Must be deterministic across languages and retries | Separate digest framing specification and review |
| A-08 | Immutable source-object boundary and stable row locator | Current CSV may be appended/flushed periodically; no row receive timestamp | File-close/manifest evidence and importer checkpoint contract |
| A-09 | Logical provenance persistence boundary | Current T0 candle table does not store source lineage | Additive provenance design; no DDL until separately approved |
| A-10 | Contract version compatibility across current Candle API and non-candle domains | Current Candle Contract 1.1.0 is candle-only; proposed 1.2.0 availability-kind work is separate | Versioning/consumer compatibility review; no silent 1.1.0 modification |

## 11. Phase A exit criteria and review request

Phase A is ready for owner review as a detailed design baseline, but **not ready for contract freeze or implementation**.

Proposed exit criteria:
- [x] Six domains and approved priority order recorded.
- [x] Native T1 CSV fields documented where source schema supports them.
- [x] Current T0 candle constraints and source/canonical ownership boundaries mapped.
- [x] Timestamp meaning, proposed identity and replay/conflict semantics specified per domain.
- [x] Provenance requirements and missing receive-time limitations recorded.
- [x] Validation and synthetic test matrix drafted.
- [x] Explicit blockers and evidence needed for contract freeze listed.
- [ ] A-01 through A-10 resolved or explicitly accepted as bounded exclusions by owner.
- [ ] Exact canonical DTO/envelope and digest encoding reviewed/frozen.
- [ ] Independent design review completed and findings resolved.

**Owner review requested:** approve/revise the Phase A design baseline and its exit criteria. This review is the gate before starting Phase B design work. If approved, Phase B may begin as documentation-only work; it does not authorize implementation.

## 12. Explicit exclusions

This document authorizes no:
- code, DTO, parser, validator, test, workflow, dependency or API changes;
- T0 DDL/schema/database creation, opening for write, migration, merge, promotion or cutover;
- T1 source-code changes, collector activation, file copying, importer execution or T1→T0 runtime connection;
- network requests, Binance calls, credentials, archive retrieval/materialization or data upload;
- source cleanup, retention expiry or deletion after acknowledgement;
- VPS, process startup, systemd/autostart or deployment;
- T2 connection, strategy behavior changes, order submission, live execution or real orders.

T0 remains the sole canonical owner; T1 remains owned in its own repository. Raw source evidence must not be destructively deleted after acknowledgement. Paper-first/no-live-trading guardrails remain unchanged.
