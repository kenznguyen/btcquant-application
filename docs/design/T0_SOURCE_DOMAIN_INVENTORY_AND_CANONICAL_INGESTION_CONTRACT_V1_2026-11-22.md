# T0 Source Domain Inventory & Canonical Ingestion Contract — Design v1

- Decision parent: `INDEPENDENT_MULTI_SOURCE_DATA_FOUNDATION`
- Date: 2026-11-22
- Status: **DESIGN PROPOSAL — OWNER REVIEW REQUIRED**
- Scope: source inventory, ownership, wire/landing/canonical formats, provenance, deduplication, validation and T0 acceptance boundary.
- Implementation: **NOT AUTHORIZED / NOT STARTED**
- Runtime connectivity: **NOT AUTHORIZED**

## 1. Purpose and invariants

T0 is the only canonical ownership boundary for accepted market data across supported source domains. Collectors may keep operational capture files, replay buffers and source-native evidence, but these are not alternate canonical datasets.

The design follows these invariants:

1. **Source evidence before normalization.** Preserve the source-native payload or an immutable source-object reference and checksum before canonical transformation. Never represent a normalized row as if it were the original exchange message.
2. **At-least-once delivery, idempotent acceptance.** Transport may redeliver. T0 must make repeated delivery safe through stable source identities and uniqueness constraints, not a check-then-insert race.
3. **No silent overwrite.** Same identity + same canonical content is a replay/duplicate. Same identity + different content is a conflict and is quarantined; it is not last-write-wins.
4. **Event time is not receive time.** Preserve exchange event/observation time, collector receive time and T0 ingest time as separate fields where available. Do not fabricate missing timestamps.
5. **Sequence integrity is domain-specific.** Order-book update continuity and trade identity must be validated before acceptance; a generic timestamp dedupe is insufficient.
6. **One canonical record, many derived views.** T2 features, training bundles, caches and backtest projections retain dataset lineage but do not become canonical stores.
7. **Fail closed.** Unknown schema, invalid symbol/market, malformed numeric value, missing required identity, sequence break, ambiguous timestamp semantics or unresolved conflict prevents canonical acceptance.
8. **No destructive acknowledgement.** A collector must not delete raw evidence after T0 acknowledges ingestion under this design. Retention/deletion is a separate owner decision.

## 2. Ownership model

| Role | Owns | Does not own |
|---|---|---|
| Exchange/source (Binance USD-M public market data) | Original event/observation and exchange-native IDs/timestamps | T0 normalization and canonical acceptance |
| T0 Foundation | Source registry, contracts, provenance, validation, canonical identity, dedup/conflict ledger, canonical datasets, read API and dataset versions | Exchange collection internals |
| T1 collector | Specialized microstructure collection, raw append-only CSV capture, reconnect/replay/gap evidence and source-native validation | Canonical accepted market-data state |
| T0 direct candle feeder / other approved collectors | Their collection process and source capture evidence | Independent canonical store |
| T2 Core / AI | Consumer projections, feature engineering, model datasets and signal lineage | Canonical source records |
| Paper ledger / risk / execution | Orders, positions, risk decisions and control state | Market-data canonical tables |

T1 repository ownership remains `kenznguyen/binance-futures-collector`. No collector code is copied into the application repository. Application-side code may own source contracts, DTOs, validators and adapters.

## 3. Source Domain Inventory

The following is the initial bounded inventory based on the T0 candle foundation and the T1 collector's published stream inventory. “Source owner” identifies the origin; “collector owner” identifies the software/process that obtains it.

| ID / domain | Origin and collector owner | Native input / current capture | Canonical record family | Primary identity and dedupe |
|---|---|---|---|---|
| SD-01 Trade klines (OHLCV) | Binance USD-M; T0 direct feeder (CCXT/public API) | Exchange kline fields; T0 Candle Contract; archive CSV for reconstruction | `Candle` | `(exchange, market_type, symbol, timeframe, open_time_ms)`; identical value replay accepted, differing value conflict |
| SD-02 Mark-price klines | Binance USD-M; T1 REST poller | Native mark-price kline; T1 CSV | `MarkPriceCandle` | `(source, market, symbol, interval, open_time_ms)`; content conflict quarantined |
| SD-03 Index-price klines | Binance USD-M; T1 REST poller | Native index-price kline; T1 CSV | `IndexPriceCandle` | Same interval identity as SD-02 with distinct domain/source namespace |
| SD-04 Premium-index klines | Binance USD-M; T1 REST poller | Native premium-index kline; T1 CSV | `PremiumIndexCandle` | Same interval identity with distinct domain namespace |
| SD-05 Aggregate trades | Binance USD-M; T1 WebSocket | `aggTrade` event; T1 CSV; exchange aggregate trade ID | `AggregateTrade` | `(exchange, market, symbol, trade_id)`; duplicate ID + same payload is replay; different payload conflict |
| SD-06 Order-book depth diffs | Binance USD-M; T1 WebSocket | `depthUpdate` with `U/u/pu`, event time and bid/ask absolute quantities; T1 CSV | `OrderBookDelta` | `(exchange, market, symbol, stream_epoch, first_update_id, final_update_id)`; validate continuity and overlap rules; never dedupe solely by timestamp |
| SD-07 Order-book snapshots | Binance USD-M REST; T1 snapshot/reconstruction | REST depth snapshot with `lastUpdateId`, plus periodic serialized book snapshots | `OrderBookSnapshot` | Snapshot group: `(exchange, market, symbol, last_update_id, snapshot_event_type)`; each level is keyed within the group by `(side, price)`. Same group + same level set is replay; differing level set conflicts |
| SD-08 Liquidations / force orders | Binance USD-M; T1 WebSocket market-wide stream filtered to tracked symbols | `forceOrder` event; T1 CSV | `LiquidationEvent` | Current T1 CSV schema exposes only `timestamp_ms, symbol, side, price, quantity, value` (no native order/trade ID). A collision-safe composite key is NOT YET DEFINED; quarantine until an exact identity contract is approved |
| SD-09 Funding rates | Binance USD-M; T1 REST poller | Funding history/next funding observation; T1 CSV | `FundingRateObservation` | Current T1 CSV exposes `timestamp_ms` (sample time), `funding_rate`, `next_funding_time`; key observations by `(source, market, symbol, timestamp_ms, observation_kind)`. Do not mistake next settlement time for sample time |
| SD-10 Open interest | Binance USD-M; T1 REST poller | Point-in-time OI endpoint response; T1 CSV | `OpenInterestObservation` | Current T1 CSV exposes `timestamp_ms` sample time, `mark_price`, `open_interest`, `oi_value`; key by `(source, market, symbol, timestamp_ms)`, preserving each sample |
| SD-11 Long/short ratios | Binance USD-M; T1 REST poller | Global account, top-trader account, top-trader position; `ratio_type` column | `PositioningRatioObservation` | Current T1 CSV exposes `timestamp_ms` bucket start, `period`, `ratio_type`, `long_ratio`, `short_ratio`, `long_short_ratio`; key by `(source, market, symbol, period, ratio_type, timestamp_ms)` |
| SD-12 Taker buy/sell ratio | Binance USD-M; T1 REST poller | Native bucketed taker ratio response; T1 CSV | `TakerFlowObservation` | Current T1 CSV exposes `timestamp_ms` bucket start, `period`, `buy_volume`, `sell_volume`, `buy_sell_ratio`; key by `(source, market, symbol, period, timestamp_ms)` |
| SD-13 Source health / gap evidence | T1 collector; T0 feeder and future adapters | T1 gap registry, stats heartbeat, reconnect/orderbook continuity evidence; T0 feeder lease/cursor/gap evidence | `SourceHealthEvent`, `SourceGap`, `IngestionCheckpoint` | Stable collector instance + event ID or deterministic interval/gap identity; append-only, never merged into market-value records |

### 3.1 Inventory notes

- T1 README documents eleven on-disk data-type directories. SD-02/03/04 are separate semantic domains even if stored in related CSV directory structures; SD-06/07 share `orderbooks/`; SD-11 has three `ratio_type` variants.
- T1's published collector captures 1-minute klines, mark/index/premium 1-minute klines, aggregated trades, order-book diffs/snapshots, liquidations, funding, OI, three long/short ratio variants and taker buy/sell ratio. The authoritative field map is T1 `docs/SCHEMA.md`; this design was refined against that document on 2026-11-22.
- T0 Candle Contract 1.2.0 design applies to trade OHLCV candles. It does not automatically define contracts for the other domains.
- T1 `docs/SCHEMA.md` confirms all files begin with `exchange, market, datatype, timestamp_ms, datetime_utc, symbol`. `timestamp_ms` meaning differs by domain (event time, sample time, bar-open time or bucket-start time). Preserve that semantic discriminator; never join/dedupe by timestamp alone. The domain table below records known fields; undocumented native IDs remain explicitly unresolved.
- Scope is BTCUSDT-first for the application. Expanding to all symbols requires explicit capacity, retention, rate-limit and storage review; T1's reference all-symbol throughput/disk figures are not a deployment commitment.

## 4. Canonical envelope (common provenance contract)

Every incoming source record is wrapped in a versioned envelope. Domain payload remains typed and domain-specific.

```json
{
  "contract": "T0_CANONICAL_INGESTION_V1",
  "source": {
    "source_id": "binance_usdm_t1",
    "collector_id": "binance-futures-collector",
    "collector_version": "exact-build-or-commit",
    "transport": "WEBSOCKET|REST|ARCHIVE",
    "source_schema": "native-schema-version-or-unknown"
  },
  "domain": "AGG_TRADE",
  "market": {
    "exchange": "BINANCE",
    "market_type": "USDM_PERPETUAL",
    "symbol": "BTCUSDT"
  },
  "identity": {
    "identity_scheme": "BINANCE_AGG_TRADE_ID_V1",
    "identity_key": "source-defined-stable-key"
  },
  "time": {
    "event_time_ms": 0,
    "source_observed_at_ms": null,
    "collector_received_at_ms": 0,
    "t0_ingested_at_ms": null,
    "availability_kind": "FIRST_OBSERVED|SOURCE_TIMESTAMP|BAR_CLOSE_BOUNDARY|UNKNOWN"
  },
  "provenance": {
    "raw_object_id": "immutable-source-object-reference",
    "raw_sha256": "64-lowercase-hex",
    "raw_record_locator": "file-and-row-or-message-offset",
    "source_sequence": null
  },
  "payload": {}
}
```

Rules:
- The JSON above is illustrative shape, not an approved wire serialization or implemented DTO.
- Required fields vary by domain; null is permitted only where the domain contract explicitly allows it.
- `raw_sha256` hashes the exact raw object/record bytes under a separately frozen byte-boundary rule. It is not a hash of reserialized JSON unless the source contract explicitly defines that.
- For a CSV row, preserve object SHA-256 plus member name and row ordinal/byte range; do not claim the row hash is the original exchange message hash.
- `collector_received_at_ms` is collector wall-clock receipt time; it is not exchange event time.
- `t0_ingested_at_ms` is assigned by T0 and is never supplied or backdated by a collector.
- Keep native decimal values as canonical decimal strings; reject binary-float coercion, NaN, Infinity and exponent notation unless a domain-specific contract explicitly permits a different exact representation.
- All timestamps are integer UTC epoch milliseconds unless the source contract explicitly declares another unit. Reject seconds/milliseconds ambiguity.

## 5. Canonical domain identity and deduplication policy

### 5.1 General acceptance algorithm

For each record, T0 performs these logical steps:

1. Authenticate/authorize the source adapter and validate source registration, allowed domains and contract version.
2. Validate envelope shape, symbol/market allowlist, required provenance, timestamp units and domain payload.
3. Derive canonical identity using the domain's frozen identity scheme; the caller cannot choose an arbitrary canonical key.
4. Compute a deterministic canonical-value digest using a separately versioned encoding contract. Raw evidence digest and canonical-value digest are different concepts.
5. Atomically attempt insert under a unique canonical identity constraint.
6. If identity is new: persist raw provenance reference, normalized canonical record and acceptance outcome in one transaction.
7. If identity exists with same canonical digest: record/return `DUPLICATE_REPLAY`; do not create a second canonical value.
8. If identity exists with different canonical digest: append a conflict record, quarantine the incoming observation and preserve both provenance references. Never update the accepted record automatically.
9. Commit the source checkpoint/acknowledgement only after durable acceptance or durable quarantine evidence. A timeout/unknown commit result must be resolved by retrying the same idempotency identity, not by generating a new one.

### 5.2 Domain-specific rules

- **Candles:** stable natural key is the Candle Contract key. Archive and live sources may overlap. Same key and same normalized value is one canonical candle with multiple provenance links. Different OHLCV/availability semantics is a conflict requiring an explicit reconciliation policy. `FIRST_OBSERVED` must never be fabricated for archive candles; archive `BAR_CLOSE_BOUNDARY` semantics remain distinct.
- **Aggregate trades:** exchange aggregate trade ID is primary. A timestamp/price/quantity match is not a substitute for the exchange ID.
- **Order-book diffs:** retain every valid sequence update needed to reconstruct the book. Validate `U/u/pu` continuity against the active stream epoch and snapshot anchor. Exact repeated message/update range with same payload is replay; overlapping, skipped, regressed or conflicting update ranges create a gap/conflict event and prevent claiming continuous book state. Never drop an update merely because timestamps match.
- **Order-book snapshots:** T1 CSV stores one row per price level with `event_type`, `side`, `price`, `quantity` and `last_update_id`. Group all levels by snapshot event/time and update ID before acceptance; the group is the snapshot identity, and `(side, price)` identifies a level. Snapshot is an anchor, not a replacement for diff history. Same anchor and same level set is replay; different level set is conflict.
- **Liquidations:** T1's published CSV schema does not retain a native order/trade ID; it retains event time, symbol, side, price, quantity and value. These fields may collide for legitimate distinct events. Do not invent a composite key or claim collision safety. Either amend the source contract to preserve a native event/order identifier or approve a collision-aware identity strategy before canonical acceptance; until then quarantine this domain.
- **Bucketed REST series:** T1 CSV `timestamp_ms` is bucket start for long/short and taker ratios; include `period` and, for positioning, `ratio_type`. Funding and OI `timestamp_ms` is sample time. Funding `next_funding_time` is a separate future settlement field, not the sample identity. Preserve distinct poll observations.
- **Point-in-time metrics (OI/current funding):** append observations keyed by source observation time and collector observation time. Do not overwrite the previous observation with the latest value.
- **Ratio families:** `ratio_type` is part of identity. Global-account, top-trader-account and top-trader-position are never merged.
- **Health/gap/checkpoint events:** append-only evidence with stable event IDs; updates to operational status are represented as new events or versioned checkpoint records under a separate explicit lifecycle contract.

### 5.3 Source overlap and authority

A canonical identity may have multiple provenance links. Source priority must not be used as an implicit overwrite rule. When sources disagree:
- preserve each observation and provenance;
- classify the conflict (normalization mismatch, source revision, timestamp semantics, payload disagreement, sequence break);
- keep the existing accepted value stable;
- require a domain-specific owner-approved reconciliation policy before selecting/replacing a canonical value.

## 6. T0 ingestion and acceptance pipeline

```text
Source / Collector
   |
   | at-least-once batch + immutable raw evidence reference
   v
T0 Ingestion Boundary
   |-- source auth / registration / contract-version gate
   |-- envelope + domain schema validation
   |-- provenance and raw-object verification
   |-- identity derivation + canonical digest
   |-- domain validators (sequence, bucket, value semantics)
   v
Quarantine / Conflict Ledger  <--- invalid, ambiguous, conflicting, incomplete
   |
   | valid records only
   v
Single T0 Writer / transaction boundary
   |-- canonical domain rows
   |-- provenance links
   |-- idempotency/dedup outcome
   |-- source checkpoint / dataset version
   v
Read-only T0 API / versioned dataset bundles
   |
   v
T2 Strategy Core + independent AI consumers
```

### 6.1 Delivery and acknowledgement

- Initial delivery guarantee: **at-least-once**. Do not claim exactly-once transport.
- Batch carries `batch_id`, source identity, contract version, ordered records and a source checkpoint/cursor.
- `batch_id` is stable across retries of the same immutable batch; same ID with a different payload digest is rejected as conflict.
- T0 returns per-record outcomes: `ACCEPTED`, `DUPLICATE_REPLAY`, `QUARANTINED`, `CONFLICT`, or `REJECTED`, plus durable receipt ID and committed checkpoint where applicable.
- A source may advance its durable cursor only after T0 has committed the batch outcome and checkpoint atomically. Partial batch acceptance must return exact per-record outcomes and a safe resume cursor.
- If acknowledgement is lost, resend the same batch and IDs. T0 replays the committed receipt.
- For order-book streams, checkpoint is sequence-aware and bound to snapshot/stream epoch; a simple file offset alone is not sufficient.
- No destructive source deletion follows acknowledgement under this contract.

### 6.2 Atomicity and single-writer boundary

- The T0 write gateway remains the only canonical write path. Adapters do not open SQLite directly.
- Canonical rows, provenance links, dedupe outcome and checkpoint advance must be committed atomically or represented as a recoverable transaction protocol with an explicit acceptance state. No acknowledgement may precede durable evidence.
- The current T0 Candle writer/lease/fencing invariants remain mandatory for candle writes. Multi-domain writer concurrency and partitioning require a separate design; this document does not authorize multiple writers.
- A source failure or loss of writer lease is fail-closed: no canonical writes and no successful acknowledgement.

## 7. Initial canonical record families

| Family | Core fields (minimum design) | Additional integrity |
|---|---|---|
| Candle | Candle Contract fields incl. exchange, market type, symbol, timeframe, open time, OHLCV, available_at, availability_kind | OHLC bounds, interval alignment, close/availability semantics |
| Mark/Index/Premium candle | source, market, symbol, interval, open time, exact decimal OHLC values, source close time | interval continuity and source-specific price semantics |
| Aggregate trade | symbol, aggregate ID, price, quantity, buyer-maker flag, event time, trade time | native ID uniqueness, positive price/quantity |
| OrderBookDelta | symbol, U/u/pu, event time, bids/asks absolute quantities, stream epoch | update chain continuity and nonnegative quantities |
| OrderBookSnapshot | symbol, lastUpdateId, snapshot time, depth levels, snapshot kind | bridge validity, level ordering, nonnegative quantities |
| LiquidationEvent | symbol, side, order/trade identity, price, quantity, event time | native field consistency; stable identity required |
| FundingRateObservation | symbol, funding time, rate, mark price if supplied, observed time, forecast/settled kind | exact decimal, funding-time identity |
| OpenInterestObservation | symbol, OI quantity/value if supplied, period, observed time | no overwriting historical observations |
| PositioningRatioObservation | symbol, ratio_type, long/short values, bucket end, observed time | ratio family identity and range/consistency |
| TakerFlowObservation | symbol, buy/sell ratio, buy/sell volume if supplied, bucket end, observed time | source schema and ratio/volume constraints |
| SourceHealthEvent / SourceGap | source, collector instance, domain, symbol, start/end/sequence range, reason, observed time | append-only; gap closure is a new resolution event |

Exact physical schemas, SQL types, indexes and partitioning are **OPEN** and must be designed after per-domain native schema mapping. Do not extend current Candle schema ad hoc to fit every domain.

## 8. Error and quarantine semantics

| Outcome | Meaning | Canonical write | Retry |
|---|---|---|---|
| ACCEPTED | New valid identity committed | Yes | Same identity returns replay |
| DUPLICATE_REPLAY | Identity and canonical digest already committed identically | No new canonical row; provenance may append under contract | Safe |
| QUARANTINED | Evidence retained but semantic/quality gate failed or is incomplete | No | Only after corrected evidence/new attempt |
| CONFLICT | Same identity with different canonical content or batch digest | No overwrite | Requires reconciliation |
| REJECTED | Unauthorized source/domain, unsupported contract, malformed envelope or impossible identity | No | Fix source/contract; do not blind retry |

Quarantine must preserve reason codes, raw evidence references, validation version and timestamps. Do not put secrets or unbounded raw response bodies into diagnostic fields.

## 9. Rollout sequence — design gates only

1. **D0 Inventory confirmation:** owner confirms source list, initial symbol universe (BTCUSDT-first), domain priorities and source ownership.
2. **D1 Native schema mapping:** inspect T1 `docs/SCHEMA.md`, T1 architecture and T0 Candle Contract; map every native field, unit, nullability, event-time semantics and stable identity.
3. **D2 Contract freeze:** approve envelope, per-domain schema versions, identity schemes, canonical digest framing, error codes and checkpoint semantics.
4. **D3 Storage design:** choose physical representation/partitioning for multi-domain data without violating current SQLite and single-writer gates; estimate disk/write/read loads.
5. **D4 Synthetic contract tests:** duplicate replay, conflicting duplicate, malformed input, source overlap, order-book gap/overlap, out-of-order batches, lost acknowledgement, partial acceptance, restart/replay and provenance preservation.
6. **D5 Independent review and bounded implementation approval:** exact source SHA, test plan, evidence and exclusions.
7. **D6 Runtime/source onboarding:** separate owner approval for each connector and environment. No automatic progression from design approval.

## 10. Open decisions — do not guess

- Exact authoritative T1 native schema and per-column semantics for all eleven storage directories.
- Stable collision-safe identity for forceOrder/liquidation events if native order identity is insufficient.
- Whether mark/index/premium candles are canonical persisted domains in initial release or staged after trade candles.
- Initial source priority and conflict reconciliation for Binance direct candles versus archive/reconstruction and T1-origin observations.
- Canonical digest byte encoding for each non-candle domain; existing T0ENC1/S1 contracts do not automatically cover every new domain.
- Multi-domain SQLite physical schema, indexes, write batching, retention and capacity.
- Source registration/authentication and ingestion transport (local file importer, HTTP batch API, or other); no transport is selected here.
- Checkpoint semantics for each T1 file stream and WebSocket sequence epoch.
- Treatment of revised/in-progress kline buckets versus closed/final candles.
- Retention and deletion of raw source evidence; no deletion policy is introduced here.

## 11. Explicit exclusions and status

This is a design proposal only. It does not authorize:
- T0 schema/DDL changes, database creation, migration, promotion or cutover;
- archive retrieval/materialization, staging, real-data importer execution or source data copying;
- T1 provider activation, T1→T0 runtime connection, new API endpoint, network request or credential use;
- T0 multi-writer/partitioning changes, service startup, VPS, deployment or autostart;
- retention/deletion/cleanup or data upload;
- T2 runtime connection, strategy behavior changes, paper order submission, live trading or real orders.

| Item | Status |
|---|---|
| Independent Multi-Source Data Foundation architecture | OWNER-APPROVED |
| Source Domain Inventory v1 | DESIGN PROPOSAL — OWNER REVIEW REQUIRED |
| Canonical Ingestion Contract v1 | DESIGN PROPOSAL — OWNER REVIEW REQUIRED |
| T0 multi-domain implementation | NOT STARTED / NOT VERIFIED |
| Native T1 field mapping | PARTIAL — README-level inventory only |
| T1→T0 runtime ingestion | NOT AUTHORIZED |
| Tests/workflows/artifacts | NOT RUN / NONE |
| Database/runtime/deployment | NOT AUTHORIZED |

**Next owner decision:** confirm or amend the source inventory and BTCUSDT-first onboarding priority. After that, proceed with native schema mapping and contract freeze as documentation-only work.
