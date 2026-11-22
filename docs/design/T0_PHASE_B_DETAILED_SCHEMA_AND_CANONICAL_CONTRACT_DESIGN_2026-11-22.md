# T0 Phase B — Detailed Schema & Canonical Contract Design

- Date: 2026-11-22 (revision 2)
- Status: **PHASE B DESIGN REVISION 2 — SECOND REVIEW REQUESTED**
- Scope: SD-05 aggregate trades; SD-06 order-book depth diffs; SD-07 order-book snapshots.
- Authorization: owner-approved Phase A review and Phase B documentation-only authorization, decision commit `f2f5741cad47b86c70dae23dbaa9b497258cc80a`.
- Governing design: `docs/design/T0_SOURCE_DOMAIN_INVENTORY_AND_CANONICAL_INGESTION_CONTRACT_V1_2026-11-22.md`.
- Phase A baseline: `docs/design/T0_PHASE_A_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`.
- T1 source schema: `kenznguyen/binance-futures-collector/docs/SCHEMA.md`, blob SHA `895f87a8281a3f9b6d37d96b5f68568e4285bee6`.
- Implementation: **NOT AUTHORIZED / NOT STARTED**.
- Tests/workflows/artifacts: **NOT RUN / NONE**.

## 1. Purpose and invariants

This document advances only the detailed design for Phase B's three microstructure domains. It does not freeze a wire DTO, storage schema, digest encoding, checkpoint protocol or source contract.

Invariants inherited from the owner-approved Independent Multi-Source Data Foundation:

1. T0 is the sole canonical owner of accepted market data.
2. T1 remains the specialized collector and source-capture owner in `kenznguyen/binance-futures-collector`; no full collector copy/fork is permitted in the application repository.
3. Preserve source-native evidence and provenance before canonical transformation.
4. Assume at-least-once delivery. Canonical acceptance must be idempotent under domain-native identity.
5. Same identity + same semantic content is replay. Same identity + different content is conflict; never last-write-wins.
6. Missing sequence continuity, ambiguous snapshot grouping, missing identity or incomplete provenance fails closed.
7. Event time, collector receive time and T0 receipt/commit time are distinct. Never fabricate a missing receive timestamp.
8. Acknowledgement follows durable acceptance or durable quarantine evidence. No delete-on-ack.
9. T2 features, caches, bundles and reconstructed books are derived products, not canonical source stores.

## 2. Native source evidence reviewed

T1's published CSV schema documents:

- Common prefix: `exchange, market, datatype, timestamp_ms, datetime_utc, symbol`.
- `timestamp_ms` and `datetime_utc` represent the same UTC instant; the semantic meaning varies by datatype.
- Aggregate trades are deduplicated by `trade_id`; `timestamp_ms` is trade time.
- Depth diffs carry `first_update_id` (U), `last_update_id` (u), `prev_update_id` (pu), `bids_json`, and `asks_json`; quantities are absolute, and zero removes a level.
- Depth snapshots are one row per price level; fields include `event_type`, `side`, `price`, `quantity`, and `last_update_id`; `timestamp_ms` is snapshot capture time.
- The schema calls trade `side` the aggressor side and records `is_buyer_maker`; it also retains `first_update_id`/`last_update_id` as a documented misnomer for aggTrade first/last underlying trade IDs, not book update IDs.

The CSV schema is a documentation snapshot, not proof that every live collector build, file boundary, timestamp clock or parser implementation conforms. The exact T1 source implementation and runtime behavior have not been inspected or verified as part of this documentation-only task.

## 3. SD-05 — Aggregate trades

### 3.1 Native source-field completeness and mapping

The Binance USD-M aggregate-trade event includes native fields beyond the currently documented T1 CSV. In particular, `q` and `nq` are distinct quantities: `q` is aggregate quantity including all market trades, while `nq` excludes trades involving RPI orders. They are not interchangeable.

| Binance native field | Meaning | Present in documented T1 CSV? | Phase B treatment |
|---|---|---:|---|
| `e` | event type | No | raw-source-only/unavailable in CSV |
| `E` | event time | represented by `timestamp_ms` | candidate `trade_time_ms` only after exact mapping verified |
| `s` | symbol | Yes, `symbol` | canonical instrument envelope |
| `a` | aggregate trade ID | Yes, `trade_id` | native identity |
| `p` | price | Yes, `price` | exact decimal |
| `q` | quantity including RPI-involved trades | Yes, `quantity` | canonical `quantity_all` (legacy candidate name `quantity` retained only pending DTO review) |
| `nq` | normal quantity excluding RPI-involved trades | **No** | preserve if present in raw native message; otherwise `UNAVAILABLE_IN_T1_CSV_V1`; do not derive or equate to `q` |
| `f` / `l` | first/last underlying trade IDs | Yes, misleadingly named `first_update_id` / `last_update_id` | candidate first/last trade IDs |
| `T` | trade transaction time | No separate field | unavailable unless captured in raw source |
| `m` | buyer-is-maker flag | Yes, `is_buyer_maker` | strict boolean-domain mapping |
| `M` | ignore/auxiliary flag | No | raw-source-only/unavailable in CSV |

For the current T1 CSV contract, canonical `quantity` means the documented all-trades aggregate quantity `q`; `nq` is not silently substituted. Whether `nq` should become a first-class canonical field is unresolved and requires a source-contract/consumer decision. Preserve raw native messages where available. If only CSV is available, explicitly record `nq` as unavailable for that source version; do not fabricate it.

### 3.2 Native-to-candidate mapping

| Native field | Documented meaning | Candidate canonical field | Notes |
|---|---|---|---|
| `exchange` | `binance` | `exchange` | Normalize only through a versioned enum map |
| `market` | `futures` | `market_type` | Resolve exact USD-M/perpetual scope from source registration |
| `symbol` | lowercase symbol | `symbol` | Canonical symbol form must be explicit |
| `timestamp_ms` | trade time | `trade_time_ms` | UTC epoch milliseconds |
| `trade_id` | aggregate trade ID | `aggregate_trade_id` | Primary native identity |
| `side` | buy/sell aggressor side | `aggressor_side` | Preserve source meaning |
| `price` | fill price | `price` | Exact decimal; no float coercion |
| `quantity` | aggregate quantity | `quantity` | Exact decimal; no float coercion |
| `is_buyer_maker` | 1 if buyer maker, else 0 | `is_buyer_maker` | Strict boolean-domain validation |
| `first_update_id` | aggTrade `f`, first underlying trade ID | `first_trade_id` | Rename semantically; not a book update ID |
| `last_update_id` | aggTrade `l`, last underlying trade ID | `last_trade_id` | Rename semantically; not a book update ID |

### 3.3 Candidate identity and acceptance

Candidate identity:
`(exchange, market_type, symbol, aggregate_trade_id)`.

- Require the native aggregate trade ID. Timestamp/price/quantity similarity is not an acceptable substitute.
- Validate nonnegative integer ID fields and the documented relationship `first_trade_id <= last_trade_id`; verify exact exchange semantics before freezing.
- Validate positive finite price and quantity as exact decimals.
- Validate `is_buyer_maker` as exactly 0/1 in CSV and map to a boolean without truthiness coercion.
- Preserve both `aggressor_side` and `is_buyer_maker`. Do not silently derive one from the other. Add a cross-field consistency check only after the Binance source semantics and T1 mapping are verified.
- Same identity and same canonical payload: `DUPLICATE_REPLAY`.
- Same identity and changed timestamp, side, price, quantity, maker flag or first/last trade ID: `CONFLICT`; retain both evidence references and do not overwrite.
- Aggregate trade IDs are documented as monotonic per symbol. Do not assume global monotonicity across symbols or use ID alone without exchange/market/symbol namespace.

### 3.4 Time and provenance

- Native `timestamp_ms` is trade time, not collector receive time.
- Current documented CSV has no explicit collector receive timestamp or WebSocket stream epoch.
- Preserve source object SHA-256, immutable object locator, row locator, source schema/parser version and T0 receipt/commit times.
- A historical file import time must not be relabeled as original collector receive time.
- A raw CSV row digest is not an exchange message digest unless exact byte framing and original message retention are proven.

### 3.5 Validation and quarantine

Quarantine/reject on missing/duplicate/invalid header, wrong datatype, unknown symbol/market, malformed timestamp, mismatch between `timestamp_ms` and `datetime_utc`, invalid ID ordering, non-finite/invalid decimal, zero/negative price or quantity, invalid maker flag, or ambiguous row provenance. Do not coerce or silently skip.

## 4. SD-06 — Order-book depth diffs

### 4.1 Native source-field completeness and mapping

The Binance USD-M Diff Book Depth event carries both `E` (event time) and `T` (transaction time), in addition to `U`, `u`, `pu`, `b` and `a`. The current documented T1 CSV maps `E` to `timestamp_ms` but has no separate `T` column. Therefore `T` is explicitly unavailable in the current CSV contract; it must not be reconstructed from `E`. If the collector retains the raw exchange message, retain `T` in immutable raw evidence and expose it as a separate candidate field only through a versioned source contract.

| Binance native field | Meaning | Current T1 CSV mapping | Treatment |
|---|---|---|---|
| `e` | event type | absent | raw-only/unavailable |
| `E` | event time | `timestamp_ms` | `event_time_ms` |
| `T` | transaction time | **absent** | preserve raw if available; otherwise explicit unavailable marker |
| `s` | symbol | `symbol` | instrument envelope |
| `U` / `u` / `pu` | first/final/previous-final update IDs | `first_update_id` / `last_update_id` / `prev_update_id` | sequence fields |
| `b` / `a` | bid/ask absolute quantity updates | `bids_json` / `asks_json` | exact level updates |

### 4.2 Native-to-candidate mapping

| Native field | Documented meaning | Candidate canonical field | Notes |
|---|---|---|---|
| `timestamp_ms` | event time | `event_time_ms` | Not receive time |
| `first_update_id` | U, first update ID | `first_update_id` | Inclusive sequence start per source contract |
| `last_update_id` | u, final update ID | `final_update_id` | Must be >= U |
| `prev_update_id` | pu, previous event's u | `previous_final_update_id` | Continuity evidence |
| `bids_json` | array of [price, qty] | `bid_changes` | Absolute quantities; zero removes level |
| `asks_json` | array of [price, qty] | `ask_changes` | Absolute quantities; zero removes level |
| Common fields | exchange/market/symbol | instrument envelope | Explicit source namespace |

### 4.3 Candidate identity and sequence integrity

Candidate **canonical exchange-event identity** (not frozen):
`(exchange, market_type, symbol, first_update_id, final_update_id)`.

This identity is conditional on evidence that Binance USD-M update-ID ranges are unique in the stated exchange/market/symbol namespace across reconnects and collector restarts. Until that scope is verified, SD-06 canonical acceptance remains BLOCKED; do not add a local epoch to the canonical key merely to make it appear unique. If exchange documentation/source evidence cannot establish this identity scope, retain observations as source evidence/quarantine and request an explicit alternative identity decision.

`stream_epoch` is **capture/session provenance and continuity state only**, not a canonical identity component. It identifies the collector's observed stream session and is required to validate continuity, snapshot linkage and recovery. It is absent from the published T1 CSV and must not be fabricated from file name, timestamp or process start time.

Candidate sequence rules, subject to exact Binance USD-M stream-contract verification:

- Require `first_update_id <= final_update_id`; all IDs are integers in the supported range.
- Validate each diff against a snapshot anchor and active stream epoch using the exchange-prescribed initial bridge and subsequent continuity rules.
- The documented `prev_update_id` chain must be retained and checked; do not treat timestamps as sequence.
- A sequence gap, regression, unexplained overlap, epoch mismatch or conflicting repeated range marks the reconstructed book state discontinuous. Record gap/conflict evidence and fail closed; do not claim a valid continuous book.
- Same canonical identity + same semantic payload is replay, including when observed in a later capture epoch.
- Same canonical identity + changed semantic payload is conflict across epochs too; preserve both immutable source observations and never overwrite.
- A changed `stream_epoch` alone does not create a new canonical event and does not make a repeated update range new data.
- If the same update range appears in two epochs but exchange identity scope is not yet proven, classify the later observation as `IDENTITY_SCOPE_UNVERIFIED`/quarantine rather than silently accepting it as either replay or a new event.
- Overlapping but non-identical ranges are not automatically duplicates. Apply only the exchange's verified sequence rules; preserve both source observations until adjudication.
- Each bid/ask change is an absolute quantity at a price level, not a delta to add. Quantity zero means delete the level.
- Never drop a message because its event timestamp matches another message.

### 4.4 Payload validation

- Parse `bids_json` and `asks_json` as arrays of two-element arrays only.
- Price must be a positive exact decimal; quantity must be a nonnegative exact decimal.
- Reject duplicate price levels within one side/message unless the source contract explicitly defines a deterministic resolution.
- Reject invalid side structure, malformed JSON, NaN/Infinity, exponent/precision overflow and noncanonical numeric coercion.
- Preserve bid and ask arrays independently; do not infer missing side as empty without source evidence.
- Cross-side price crossing may be a valid transient or indicate invalid state depending on sequence position; do not impose an unreviewed rule on an individual diff message.

### 4.5 Time, provenance and checkpoints

- `timestamp_ms` is event time `E`. Binance USD-M depth messages also expose transaction time `T`; the current T1 CSV schema does not map `T`.
- Preserve `event_time_ms` and `transaction_time_ms` as distinct native timestamps when the source adapter captures both. For the currently documented CSV version, `transaction_time_ms` is `UNAVAILABLE_IN_SOURCE_SCHEMA`, not null-by-default and not derivable from event time.
- Collector receive time is a third clock and must be captured at the collector boundary if required; never substitute `E`, `T`, file modification time or import time.
- T0 receipt and durable commit times remain separate system timestamps.
- Current CSV schema does not document collector receive time, stream epoch, connection identity or durable per-message cursor beyond U/u/pu.
- A file offset is not sufficient as a semantic checkpoint for a live order-book stream.
- A future checkpoint must bind source identity, stream epoch, last durably accepted sequence, snapshot anchor/version, and immutable source evidence position.
- T0 acknowledgement may advance only after the accepted diff (or durable quarantine/gap outcome) and associated checkpoint state are committed atomically or through a reviewed recovery protocol.
- Lost acknowledgement retries the same immutable message identity; it must resolve as replay, not a second book update.

### 4.5 Depth visibility scope — non-RPI by default

The Phase B SD-06/SD-07 default dataset is the ordinary Binance USD-M depth feed and therefore represents **non-RPI depth only**. Binance documents RPI orders as excluded from the ordinary depth stream and provides a separate RPI Diff Book Depth stream. Consequently, this dataset is not a complete view of all displayed liquidity and must not be described as such.

RPI-inclusive depth is OUT OF SCOPE for Phase B. It requires a separately reviewed source-domain/stream identity, sequence, snapshot and merge contract; do not merge RPI observations into the ordinary book or infer missing RPI liquidity. The same non-RPI limitation applies to snapshots unless their source contract proves otherwise.

### 4.6 Bounded out-of-order, gap and recovery policy

1. The source adapter preserves original arrival order and arrival metadata. It must not sort or rewrite raw source observations by event time.
2. The sequence processor may hold a bounded reorder buffer keyed by native sequence range to tolerate limited transport reordering. Both a maximum buffered-event count and maximum residence age are mandatory configuration bounds. Their numeric values are NOT FROZEN and must be derived from measured source behavior and owner-reviewed resource limits; no arbitrary default is accepted.
3. A candidate can be applied only when the verified Binance bridge/continuity rule proves it is the next applicable update relative to the active snapshot anchor and last applied sequence. A later event may be buffered only while both configured bounds remain satisfied.
4. A gap becomes `GAP_PENDING` when the next expected sequence is absent but the bounded wait remains. It becomes durable `GAP_UNRESOLVED` when either bound is reached, the source session ends, the buffer overflows, or continuity cannot be proven. Persist the missing range/expected sequence, observed ranges, epoch, timestamps and evidence references.
5. Buffer overflow is fail-closed: stop applying later events, persist discontinuity/quarantine evidence, and mark the derived book unavailable. Never evict the oldest event silently.
6. A checkpoint may advance only through the highest contiguous, durably committed sequence. It must never advance across `GAP_PENDING`, `GAP_UNRESOLVED`, conflict, or uncommitted provenance.
7. Recovery order: (a) wait for missing updates only while both bounds remain; (b) after unresolved gap/session loss, mark the current derived book unavailable and reacquire a new complete snapshot plus a new stream epoch using the exchange-verified bridge; (c) if snapshot/bridge cannot be proven, remain unavailable/quarantined. Do not silently skip the gap or resume from a later diff.
8. Restart recovery must load the durable checkpoint and unresolved-gap state. A new local epoch does not reset canonical event identity and does not itself repair a sequence gap.

Numeric buffer bounds, gap wait values and exact exchange bridge behavior remain explicit freeze blockers.

### 4.7 Book-state semantics

Canonical diff history and a reconstructed in-memory/current book are different artifacts. T0 canonical history retains accepted source diffs and their provenance. Any derived book view must identify the exact snapshot anchor, stream epoch, last applied update ID, applied dataset version and continuity status. It must not be represented as a raw source event.

## 5. SD-07 — Order-book snapshots

### 5.1 Native-to-candidate mapping

| Native field | Documented meaning | Candidate canonical field | Notes |
|---|---|---|---|
| `timestamp_ms` | snapshot capture time | `snapshot_captured_at_ms` | Not exchange event time unless source proves so |
| `event_type` | initial/periodic/bridge snapshot type | `snapshot_kind` | Enum allowlist |
| `side` | bid or ask | `side` | Strict enum |
| `price` | level price | `price` | Exact positive decimal |
| `quantity` | level quantity | `quantity` | Exact positive decimal for retained levels |
| `last_update_id` | book version | `last_update_id` | Snapshot sequence anchor |
| Common fields | exchange/market/symbol | instrument envelope | Explicit source namespace |

### 5.2 Grouping and candidate identity

The native CSV is one row per price level, not one row per snapshot. T0 must group all rows belonging to one complete snapshot before canonical acceptance. A single level row is never a complete snapshot.

Candidate snapshot identity proposal:
`(exchange, market_type, symbol, snapshot_kind, last_update_id, snapshot_captured_at_ms, snapshot_capture_id)`.

**Important:** `snapshot_capture_id` is not present in the documented CSV schema. The tuple without it is only a candidate and is not proven collision-safe: repeated captures can share an update ID and potentially the same millisecond timestamp. A source-generated immutable snapshot ID or a separately evidenced unique capture boundary is required before freeze. Do not invent an ID from row order or file path.

Within one grouped snapshot, level identity is `(side, price)`. The complete level set must be deterministic and duplicate-free.

### 5.3 Completeness and consistency

- Validate one consistent `event_type`, `last_update_id`, timestamp, exchange, market and symbol across every row in a group.
- Require only `depth_snapshot_initial`, `depth_snapshot`, `depth_snapshot_bridge` until the source schema is versioned.
- Reject duplicate `(side, price)` levels, invalid sides, nonpositive price/quantity, malformed decimals, and mixed group metadata.
- The current row schema has no explicit group header, expected level count, checksum, end marker or empty-book marker. Therefore a file/row batch alone does not prove snapshot completeness.
- Minimum future acceptance evidence is: (a) source-generated immutable `snapshot_capture_id`; (b) explicit group framing/boundary; (c) expected row/level count or an equivalent source completeness declaration; (d) finalized immutable source-object digest; and (e) a manifest binding capture ID, symbol/market, snapshot kind, update ID, capture time, row count, object digest and completion status. An exchange/source checksum may strengthen validation but must not be invented where unavailable.
- An alternative to this manifest is acceptable only if a source-generated capture ID and equivalently strong, independently verifiable completeness proof are supplied and reviewed. File EOF, file rotation, elapsed time, a stable-looking file size or observed row count alone is never proof of completion.
- Partial write, process restart, collector crash, object mutation, missing end marker, row-count mismatch or digest mismatch leaves the entire capture quarantined; do not accept a partial prefix.
- Empty-side/empty-book snapshots require an explicit source representation (for example an explicit zero-level declaration in the completion manifest). Absence of rows is not evidence of an empty side or book.
- Snapshot `last_update_id` anchors the book state. It is not a trade ID and must not be mixed with SD-05 identifiers.
- Same proven snapshot identity + identical complete level set is replay. Same identity + differing level set is conflict; never merge levels or overwrite.
- A snapshot is a reconstruction anchor, not a substitute for the diff history before/after it.

### 5.4 Provenance and time

- `timestamp_ms` is documented as when the snapshot was taken; do not call it an exchange event timestamp without evidence.
- SD-07 is non-RPI by default when sourced from the ordinary depth snapshot endpoint/flow. It is not a complete view of all displayed liquidity; any RPI-inclusive snapshot requires a separately reviewed contract.
- Preserve object SHA-256, immutable source locator, row range/ordinals, source schema/parser version and T0 receipt/commit times.
- Current CSV does not expose collector receive time, REST request ID, snapshot capture ID or completeness manifest. Consequently, all snapshot groups from this schema version remain `NOT_CANONICAL_ACCEPTABLE` until the source contract provides capture identity and independently verifiable completeness proof.
- Do not infer original receive time from snapshot timestamp, file name, import time or T0 receipt.

## 6. Cross-domain relationships and non-interchangeability

| Relationship | Rule |
|---|---|
| SD-05 trade IDs vs SD-06 update IDs | Separate namespaces and identity schemes; never compare or join as one sequence |
| SD-06 diff vs SD-07 snapshot | Diff continuity is evaluated relative to a snapshot anchor and stream epoch; snapshot is a full-state anchor |
| SD-05 event time vs SD-06 event time | Both are UTC milliseconds but are not a common deduplication key |
| Raw source rows vs derived order book | Preserve raw rows/messages; reconstructed book is a versioned derived view |
| T1 files vs T0 canonical records | T1 files remain source evidence/capture output, not a competing canonical dataset |

## 7. Common provenance and acceptance envelope

Reuse the Phase A logical envelope direction without freezing serialization:

- contract name/version;
- registered source and collector identity/version;
- domain ID and native datatype;
- exchange, market type and symbol;
- domain-specific native identity;
- native event/capture timestamp and its explicit semantics;
- collector receive timestamp only when genuinely captured;
- T0 received/committed timestamps;
- source object SHA-256 and immutable object locator;
- stable row/message locator;
- raw record digest only after exact byte framing is specified;
- canonical semantic digest only after a separate deterministic encoding decision;
- validation profile version and acceptance/quarantine/conflict outcome.

Raw object digest and canonical semantic digest are different. CSV row serialization is not an exchange-native message payload. Exact digest preimages, decimal normalization, schema evolution and provenance persistence remain unfrozen.

## 8. Replay, conflict, quarantine and acknowledgement matrix

| Condition | SD-05 aggregate trade | SD-06 depth diff | SD-07 snapshot |
|---|---|---|---|
| New valid identity | Candidate accept | Candidate accept only if sequence continuity is valid | Candidate accept only if complete group is proven |
| Same identity, same semantic payload | Replay | Replay; do not apply twice | Replay; do not merge duplicate levels |
| Same identity, changed payload | Conflict; preserve both | Conflict; continuity becomes untrusted | Conflict; preserve both level-set references |
| Missing native identity | Quarantine | Quarantine; stream epoch missing in current CSV | Quarantine; capture identity/completeness missing |
| Malformed numeric/JSON | Quarantine/reject | Quarantine/reject | Quarantine/reject |
| Out-of-order delivery | Retain by native trade ID/time; no timestamp-only rejection | Sequence-aware handling; do not advance cursor across missing update | Do not infer order solely from capture timestamp |
| Lost acknowledgement | Retry same aggregate ID | Retry same epoch/update range | Retry same proven capture identity |
| Source evidence unavailable | No canonical acceptance | No canonical acceptance | No canonical acceptance |

No source deletion follows acknowledgement. Partial acceptance must retain per-record outcomes and safe resume position. Acknowledgement/checkpoint atomicity and quarantine progression are design blockers, not implemented behavior.

## 9. Synthetic test design (NOT EXECUTED)

The matrix below is a design specification only. Each case must use isolated synthetic source fixtures and deterministic clocks; it must not connect to Binance, use production/T1 captures, mutate T0 storage or imply implementation readiness. The listed matrix is not executed.

### SD-05
1. Valid BTCUSDT aggregate trade with native trade ID and documented `q` mapping.
2. Source-field completeness test asserts `q` and `nq` are distinct; current CSV fixture has `quantity`/`q` but no `nq`, and the adapter reports `nq` unavailable rather than copying `q`.
3. Raw native fixture containing `nq` preserves it byte-for-byte/in a versioned raw field; no `nq` value is fabricated when absent.
2. Duplicate ID and identical payload resolves to replay.
3. Duplicate ID with changed price/quantity/side/time/maker flag resolves to conflict without overwrite.
4. Missing/negative/non-integer IDs; first ID greater than last ID.
5. Strict `is_buyer_maker` 0/1 parsing; reject truthy strings and values outside domain.
6. Exact decimal parsing; reject NaN, Infinity, malformed exponent/overflow and nonpositive price/quantity.
7. `timestamp_ms`/ISO UTC mismatch and event-time vs receive-time separation.
8. Cross-field side/maker consistency tests only after source semantics are frozen.

### SD-06
1. Valid diff with U/u/pu, `E` event time, `T` transaction time and bid/ask absolute quantities.
2. Current T1 CSV fixture maps `E` only; `T` is explicitly unavailable, never copied from `E` or import time.
3. Ordinary-depth fixture is labeled non-RPI; an RPI observation is not silently merged and the derived-book metadata declares the RPI visibility limitation.
4. Same canonical update range/payload observed in different local epochs resolves to replay when exchange identity scope is verified.
5. Same canonical update range with changed payload across epochs resolves to conflict; epoch change alone never creates a new canonical identity.
6. If update-ID uniqueness scope is unverified, cross-epoch repeated range is quarantined as identity-scope-unverified, not accepted.
7. Arrival order is preserved in raw evidence; a bounded reorder buffer accepts only in-bound reordering and applies only contiguous sequence events.
8. Reorder buffer count limit and age limit are independently enforced; count overflow and age expiry persist `GAP_UNRESOLVED`, stop application and mark book unavailable.
9. A missing sequence remains `GAP_PENDING` only within both bounds; recovery waits within bounds, then requires a new complete snapshot/new epoch and verified bridge or remains unavailable.
10. Checkpoint stays before the gap while pending/unresolved and cannot advance over buffered-but-unapplied or uncommitted events.
2. Zero quantity removes exactly one price level.
3. Valid sequence bridge from a snapshot and valid subsequent pu chain.
4. Missing update, regressed ID, invalid overlap, wrong pu, stream epoch change.
5. Same range/same payload replay; same range/different payload conflict.
6. Same timestamp but different update IDs remains distinct.
7. Malformed JSON, wrong tuple arity, duplicate prices, invalid decimal, negative quantity.
8. Missing stream epoch fails closed; file offset alone cannot establish sequence continuity.
9. Lost acknowledgement retry does not apply a diff twice.
10. Checkpoint cannot advance beyond an uncommitted update or unresolved gap.

### SD-07
1. Multi-level bid/ask rows group into one complete snapshot only when capture ID, completion manifest, expected count and finalized object digest agree.
2. EOF, file rotation, elapsed time, stable file size or row count without a source completion manifest does not prove completeness and remains quarantined.
3. Partial write, restart, missing rows, count mismatch or digest mismatch quarantines the entire capture; no partial prefix is accepted.
4. Explicit empty-side/empty-book manifest is accepted as such; absence of rows without an explicit declaration is not interpreted as empty.
5. Ordinary snapshot source is marked non-RPI; the book is not labeled as complete all-liquidity visibility.
6. Repeated capture with a new capture ID but identical update ID/time is a distinct capture observation only if source-generated identity/completeness evidence proves it; otherwise quarantine.
2. Mixed timestamp/update ID/event type/symbol within group rejected.
3. Duplicate side/price level rejected.
4. Same identity and same full level set replay; changed set conflict.
5. Missing capture ID or ambiguous repeated capture quarantined.
6. Truncated/partial group and missing close marker cannot be accepted.
7. Empty side/book is not inferred from absent rows.
8. Snapshot anchor correctly links to a diff stream epoch only when source evidence establishes the relation.
9. Different event types at same symbol/update ID remain distinguishable.
10. Lost acknowledgement retry resolves to replay for the same complete capture identity.

These cases are proposed only. No tests, fixtures, parser, validator or workflow were created or run.

## 10. Open design blockers before contract freeze

| ID | Blocker | Why it matters | Evidence/decision required |
|---|---|---|---|
| B-01 | Exact T1 aggTrade source mapping and build behavior | Published CSV schema alone does not prove parser correctness or source payload retention | Read-only inspection of pinned T1 source and exact Binance USD-M aggTrade contract |
| B-02 | AggTrade ID semantics and field bounds | Identity and first/last trade-ID meaning must be exact | Confirm exchange contract and T1 code; freeze integer ranges |
| B-03 | `side` vs `is_buyer_maker` relation | Avoid inconsistent or inverted aggressor semantics | Verify exchange semantics and T1 mapping; owner accepts validation |
| B-04 | Depth stream epoch provenance | Current CSV lacks an immutable capture/session epoch needed for continuity and recovery, but epoch must not be part of canonical event identity | Additive source-contract design; capture epoch lifecycle and cross-restart evidence |
| B-05 | Binance depth snapshot/diff bridge and update-ID uniqueness scope | Both canonical update-range identity and sequence acceptance depend on exact USD-M semantics | Pin official USD-M protocol and T1 implementation; verify uniqueness namespace across reconnects and define initial/subsequent bridge algorithm |
| B-14 | Bounded reorder/gap policy numeric limits | Count/age bounds and gap wait determine memory safety and recovery correctness | Measure source behavior; owner-review max buffered events, max residence age, wait policy and resource budget before freeze |
| B-06 | Depth diff source message completeness and receive time | CSV does not prove complete original event bytes or collector receive timestamp | Inspect T1 source capture and decide additive provenance fields |
| B-15 | Native `nq` and depth transaction-time `T` fidelity | Current T1 CSV omits aggTrade `nq` and depth `T`; `q` and `nq` differ, while `E` and `T` are separate clocks | Inspect pinned T1 source/raw retention; decide versioned canonical vs raw-only fields; current CSV must explicitly mark both unavailable where absent |
| B-16 | RPI visibility and source-domain scope | Ordinary depth excludes RPI and is not a complete all-liquidity book | Keep Phase B non-RPI; separately approve any RPI stream and merge contract before inclusion |
| B-07 | Snapshot capture identity | Current schema has no unique capture ID; timestamp + lastUpdateId may collide | Source-generated immutable capture ID bound to symbol/market/kind/update ID and immutable object evidence |
| B-08 | Snapshot group completeness | One row per level, no count/checksum/end marker/empty-book marker | Source-generated completion manifest/group framing with expected row count (or equivalent), finalized object digest, explicit complete/empty declarations; EOF/rotation/elapsed time/row count alone prohibited |
| B-09 | Snapshot-to-stream epoch linkage | Snapshot anchor must correspond to the intended diff stream | Define source lifecycle/session relationship and recovery semantics |
| B-10 | File immutability and row locator | CSV append/rotation may expose partial groups or changing bytes | Exact close/manifest rule, immutable object SHA and stable row locator |
| B-11 | Canonical digest/decimal serialization | Cross-language deterministic replay/conflict decisions | Separate versioned byte-encoding specification and review |
| B-12 | Atomic provenance, identity, outcome and checkpoint persistence | No ack before durable evidence; no sequence skips | Logical transaction/recovery design aligned with T0 single-writer/fencing |
| B-13 | T0 API and dataset-version compatibility | Microstructure data is not a Candle and must not silently alter candle API | Separate non-candle read contract/version and consumer compatibility review |

## 11. Phase B exit criteria and owner review

- [x] Three Phase B domains scoped: SD-05, SD-06, SD-07.
- [x] Native T1 documented columns mapped to candidate canonical fields.
- [x] Candidate identity and domain-specific sequence/grouping semantics described.
- [x] Timestamp/provenance limitations called out without fabricated receive times.
- [x] Replay/conflict/quarantine/acknowledgement behavior drafted.
- [x] Synthetic test matrix expanded for cross-epoch identity, capture completeness, q/nq distinction, RPI scope, E/T time fidelity, bounded reordering, gap recovery and checkpoint fail-closed behavior; explicitly marked NOT EXECUTED.
- [x] Contract-freeze blockers recorded.
- [ ] B-01 through B-16 resolved or explicitly accepted as bounded exclusions by owner.
- [ ] Canonical DTO/envelope, digest encoding, snapshot capture/group identity and diff stream epoch contract reviewed/frozen.
- [ ] Independent design review completed and findings resolved.

**Second-round review requested:** review this revised Phase B design against findings R-01..R-06, the expanded synthetic matrix, and blockers B-01..B-16. The six findings have been addressed at the design level, but source-dependent identity scope, source capture fields, numeric buffer bounds and exact protocol bridge remain unfrozen blockers. Approval of this draft would accept the design baseline only if explicitly stated; it would not authorize implementation unless a separate implementation decision names its exact scope.

## 12. Explicit exclusions

This Phase B document authorizes no:
- code, DTO, parser, validator, adapter, fixture, test, dependency, API or workflow changes;
- T0 DDL/schema/database creation, open-for-write, migration, import, promotion, cutover or canonical data mutation;
- T1 source-code change, collector activation, file copy, importer execution or T1→T0 runtime connection;
- network/exchange calls, credentials, archive/data acquisition, data movement or upload;
- source cleanup, retention expiry or deletion after acknowledgement;
- T2 integration, strategy changes, runtime/VPS, process startup, systemd/autostart or deployment;
- order submission, live execution or real orders.

T0 remains the sole canonical owner. T1 implementation remains in its own repository. Raw source evidence must be preserved. Paper-first/no-live-trading guardrails remain unchanged.
