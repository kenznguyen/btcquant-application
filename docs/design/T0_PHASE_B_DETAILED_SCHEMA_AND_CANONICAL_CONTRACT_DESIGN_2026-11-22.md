# T0 Phase B — Detailed Schema & Canonical Contract Design

- Date: 2026-11-22 (revision 3)
- Status: **PHASE B DESIGN REVISION 3 — READY FOR NEXT REVIEW**
- Scope: SD-05 aggregate trades; SD-06 order-book depth diffs; SD-07 order-book snapshots.
- Authorization: owner-approved Phase A review and Phase B documentation-only authorization, decision commit `f2f5741cad47b86c70dae23dbaa9b497258cc80a`.
- Governing design: `docs/design/T0_SOURCE_DOMAIN_INVENTORY_AND_CANONICAL_INGESTION_CONTRACT_V1_2026-11-22.md`.
- Phase A baseline: `docs/design/T0_PHASE_A_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`.
- T1 source schema: `kenznguyen/binance-futures-collector/docs/SCHEMA.md`, blob SHA `895f87a8281a3f9b6d37d96b5f68568e4285bee6`.
- Implementation: **NOT AUTHORIZED / NOT STARTED**.
- Synthetic matrix: **DESIGNED ONLY / NOT EXECUTED**.
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

Binance USD-M aggTrade defines `E` as event time and `T` as trade time. These clocks are distinct. The pinned T1 CSV schema explicitly documents `timestamp_ms` as trade time. Therefore the CSV timestamp is only a candidate mapping to native `T`; it is not `E`. Exact T1 parser/source verification has not been performed.

| Binance native field | Meaning | Present in documented T1 CSV? | Phase B treatment |
|---|---|---:|---|
| `e` | event type | No | unavailable in CSV; preserve only if raw native message exists |
| `E` | event time | No separate field | `UNAVAILABLE_IN_T1_CSV_V1`; never map from `timestamp_ms` |
| `s` | symbol | Yes | candidate instrument envelope |
| `a` | aggregate trade ID | Yes, `trade_id` | candidate native identity; verify source mapping |
| `p` | price | Yes, `price` | candidate exact-decimal mapping; source verification pending |
| `q` | aggregate quantity including RPI-involved trades | `quantity` exists, semantics not proven | candidate mapping only; **NOT VERIFIED** pending pinned T1 parser/source inspection |
| `nq` | normal quantity excluding RPI-involved trades | No | preserve if raw native message exists; otherwise `UNAVAILABLE_IN_T1_CSV_V1`; never derive from `q` |
| `f` / `l` | first/last underlying trade IDs | `first_update_id` / `last_update_id` | candidate mapping only; not book update IDs |
| `T` | trade time | no separate native field label | candidate mapping from CSV `timestamp_ms` only; **NOT VERIFIED** against T1 parser |
| `m` | buyer-is-maker flag | `is_buyer_maker` | candidate strict boolean-domain mapping; verify source |
| `M` | ignore/auxiliary flag | No | unavailable in CSV unless raw source retained |

**Mapping status is uniform throughout this design:** every T1 CSV field-to-native-field association that is not directly established by the pinned schema is a candidate and NOT VERIFIED. In particular, `quantity` → `q` is not a frozen or documented native mapping. The existence of a CSV column named `quantity` or `size` does not establish whether it contains `q`, `nq`, or another transformed value. Do not use it as canonical `q` until pinned T1 source/parser evidence confirms it.

If raw native aggTrade messages are retained, preserve `E`, `T`, `q`, and `nq` as separate source fields without normalization that loses original bytes. If only the current CSV is available, `E` and `nq` are explicitly unavailable; `timestamp_ms` is a candidate for `T`; `quantity` is a candidate for `q`, both NOT VERIFIED. No field may be inferred from another.

### 3.2 Native-to-candidate mapping

| Source field | Documented meaning | Candidate canonical field | Verification status |
|---|---|---|---|
| `exchange` | `binance` | `exchange` | schema-documented; exact source registration pending |
| `market` | `futures` | `market_type` | candidate; exact USD-M/perpetual scope pending |
| `symbol` | lowercase symbol | `symbol` | schema-documented; normalization contract unfrozen |
| `timestamp_ms` | trade time | `trade_time_ms` / candidate native `T` | schema-documented semantics; parser fidelity NOT VERIFIED |
| `trade_id` | aggregate trade ID | `aggregate_trade_id` | candidate native mapping; source verification pending |
| `side` | buy/sell aggressor side | `aggressor_side` | documented label; native mapping pending |
| `price` | fill price | `price` | candidate exact-decimal mapping |
| `quantity` | CSV quantity/size | candidate `q` / `quantity_all` | **NOT VERIFIED**; do not treat as native q |
| `is_buyer_maker` | buyer maker indicator | `is_buyer_maker` | candidate strict 0/1 mapping |
| `first_update_id` | aggTrade `f` candidate | `first_trade_id` | candidate; verify pinned source |
| `last_update_id` | aggTrade `l` candidate | `last_trade_id` | candidate; verify pinned source |

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

- Binance native `E` is event time; native `T` is trade time. They must remain separate fields.
- The pinned T1 CSV schema says `timestamp_ms` is trade time; it is a candidate mapping to `T` only. Its exact parser fidelity is NOT VERIFIED.
- The current documented CSV has no separate `E` field. Mark event time unavailable; never relabel `timestamp_ms` as `E`.
- Current CSV has no explicit collector receive timestamp or WebSocket stream epoch.
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

### 4.6 Depth visibility scope — non-RPI by default

The Phase B SD-06/SD-07 default dataset is the ordinary Binance USD-M depth feed and therefore represents **non-RPI depth only**. Binance documents RPI orders as excluded from the ordinary depth stream and provides a separate RPI Diff Book Depth stream. Consequently, this dataset is not a complete view of all displayed liquidity and must not be described as such.

RPI-inclusive depth is OUT OF SCOPE for Phase B. It requires a separately reviewed source-domain/stream identity, sequence, snapshot and merge contract; do not merge RPI observations into the ordinary book or infer missing RPI liquidity. The same non-RPI limitation applies to snapshots unless their source contract proves otherwise.

### 4.7 Bounded out-of-order, gap and recovery policy

1. The source adapter preserves original arrival order and arrival metadata. It must not sort or rewrite raw source observations by event time.
2. The sequence processor may hold a bounded reorder buffer keyed by native sequence range. Mandatory independent hard limits are: buffered event count, buffer residence age, aggregate buffered raw/parsed bytes, raw message bytes, levels per diff, numeric token length/precision, and parser nesting/structure limits. Numeric ceilings are NOT FROZEN and must be derived from measured source behavior and owner-reviewed resource budgets.
3. Snapshot grouping has separate hard ceilings for rows per capture, total capture bytes, per-row bytes, levels per side and numeric token length. A group exceeding any ceiling is rejected/quarantined as a whole; it is not partially accepted.
4. Enforce raw byte ceilings before unbounded parsing/allocation where the source boundary permits. Enforce parsed-level and numeric-token ceilings during bounded parsing. Parser limits must prevent pathological nesting, token length and allocation amplification.
5. A candidate diff can be applied only when the verified Binance bridge/continuity rule proves it is the next applicable update relative to the active snapshot anchor and last applied sequence. A later event may be buffered only while every configured count, age and byte bound remains satisfied.
6. A gap becomes `GAP_PENDING` when the next expected sequence is absent but all bounded wait conditions remain. It becomes durable `GAP_UNRESOLVED` when any bound is reached, the source session ends, a resource ceiling is exceeded, or continuity cannot be proven. Persist expected/missing range, observed ranges, epoch, timestamps and evidence references.
7. Buffer/resource overflow is fail-closed: stop applying later events, persist a bounded rejection/quarantine reference and discontinuity evidence, and mark the derived book unavailable. Never evict the oldest event silently. Do not copy an oversized payload into an unbounded error record; preserve a bounded immutable source locator/digest when safely available.
8. A book-sequence watermark may advance only through the highest contiguous, durably committed sequence actually applied to the derived book. It must never advance across `GAP_PENDING`, `GAP_UNRESOLVED`, conflict, resource rejection or uncommitted provenance.
9. Recovery order: (a) wait for missing updates only while every bound remains satisfied; (b) after unresolved gap/session loss, mark the current derived book unavailable and reacquire a new complete bounded snapshot plus a new stream epoch using the exchange-verified bridge; (c) if snapshot/bridge cannot be proven, remain unavailable/quarantined. Do not silently skip the gap or resume from a later diff.
10. Restart recovery reloads both source-delivery cursor and book-sequence watermark, plus unresolved-gap/resource-rejection state. A new local epoch does not reset canonical event identity and does not repair a sequence gap.

Numeric count/age/byte/level/token/group limits, gap wait values and exact exchange bridge behavior remain explicit freeze blockers.

### 4.8 Separate source-delivery cursor and book-sequence watermark

These are distinct progress markers and must never be represented by one checkpoint value:

- **Source-delivery/import cursor:** identifies the last source object/row or delivered message whose immutable raw observation and terminal intake outcome (`ACCEPTED`, `DUPLICATE_REPLAY`, `CONFLICT`, `QUARANTINED`, or durable gap/resource outcome) have been durably recorded. It may advance after durable quarantine of a gap or malformed observation because source intake is complete for that position.
- **Book-sequence watermark:** identifies the highest contiguous update sequence actually applied to the derived book from its active snapshot anchor. It advances only after the corresponding canonical diff and derived application state are durable, and never across a missing sequence, conflict, quarantine, resource rejection or unapplied buffered event.

A source cursor advancing past a durably quarantined gap means only that the source observation has been safely ingested and its outcome recorded. It does **not** mean the book is continuous, does not acknowledge missing exchange updates, and must not move the book-sequence watermark.

Restart/replay rules:
1. Resume source intake after the last durable source cursor. If acknowledgement was lost, replay the same source position; identity/outcome dedupe must return the prior durable result without duplicating raw evidence or canonical effects.
2. Restore book state only from the last durable book-sequence watermark, its exact snapshot anchor/epoch and persisted gap state. Never infer the watermark from the source cursor.
3. If source intake has advanced while the book watermark is behind, replay or reprocess only the stored observations required by the sequence state machine; do not re-acknowledge them as new book progress.
4. If atomic persistence of source observation, provenance, intake outcome and source cursor cannot be guaranteed, do not advance the source cursor. If atomic persistence of diff application and book watermark cannot be guaranteed, do not advance the book watermark.

This separation is required by B-12. The exact physical transaction/recovery protocol remains unfrozen.

### 4.9 Book-state semantics

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

### 5.2 Grouping, bounded-depth scope and candidate identity

The native CSV is one row per price level, not one row per snapshot. T0 must group all rows belonging to one capture before canonical acceptance. A single level row is never a complete capture.

For the ordinary Binance USD-M REST order-book endpoint, the response is bounded top-N depth (documented limits include 5, 10, 20, 50, 100, 500 and 1000; maximum 1000). It is not an unlimited representation of the entire order book. A complete capture therefore means **all levels returned by that exact bounded response were captured and verified**, not that the exchange's entire book was captured.

Candidate snapshot identity proposal:
`(exchange, market_type, symbol, source_kind, requested_limit, last_update_id, snapshot_captured_at_ms, snapshot_capture_id)`.

The tuple is not frozen. `snapshot_capture_id` must be source-generated and immutable. Do not invent an ID from row order, timestamp, file path, file rotation or a locally assigned import sequence.

Within one capture, level identity is `(side, price)`. The full returned level set must be deterministic and duplicate-free. Preserve bid and ask counts separately; an absent side is not an empty side unless the source manifest explicitly declares zero returned levels.

### 5.3 Completeness, boundedness and consistency

- Validate one consistent `event_type`, `last_update_id`, timestamp, exchange, market, symbol, source kind, endpoint and requested limit across every row in a group.
- Require only the versioned snapshot event types permitted by the source contract.
- Reject duplicate `(side, price)` levels, invalid sides, nonpositive price/quantity, malformed decimals and mixed group metadata.
- The current CSV row schema has no explicit group header, expected level count, checksum, end marker or empty-book marker. A file/row batch alone does not prove capture completeness.
- Minimum future acceptance evidence is: (a) source-generated immutable `snapshot_capture_id`; (b) explicit group framing/boundary; (c) expected total row count or equivalent source completeness declaration; (d) finalized immutable source-object digest; and (e) a completion manifest binding capture ID, symbol/market, source kind/endpoint, requested depth limit, actual bid count, actual ask count, total row count, snapshot kind, update ID, capture time, object digest, non-RPI visibility and completion status.
- The manifest must identify the exact endpoint/source variant and request parameters. A limit of 1000 means at most the response's bounded levels; it does not mean full-book completeness.
- Empty-side/empty-book captures require explicit source/manifest declarations with zero counts. Absence of rows is not evidence of an empty side or book.
- File EOF, file rotation, elapsed time, stable-looking file size or observed row count alone is never proof of completion.
- Partial write, process restart, collector crash, object mutation, missing end marker, row-count mismatch or digest mismatch quarantines the entire capture; no partial prefix is accepted.
- Snapshot `last_update_id` anchors only the returned bounded depth state. It is not a trade ID and must not be mixed with SD-05 identifiers.
- Same proven snapshot identity + identical complete bounded level set is replay. Same identity + differing level set is conflict; never merge levels or overwrite.
- A snapshot is a bounded reconstruction anchor, not proof of the full exchange book.
- A later diff that inserts a level outside the initial returned price boundary may be applied as an update to the known bounded state only under verified sequence rules; it does not prove that omitted deeper levels are known or that the local top-N ranking remains complete. If the derived view cannot establish its visible depth/rank semantics, mark that view bounded/incomplete or unavailable rather than asserting a complete book.
- The ordinary endpoint's non-RPI visibility is an independent limitation: even a fully captured bounded response excludes RPI liquidity. Do not conflate bounded-depth completeness with all-liquidity completeness.

### 5.4 Provenance and time

- `timestamp_ms` is documented as snapshot capture time in the T1 CSV; do not call it exchange event time or REST response event time without evidence. If the REST response exposes native `E` and `T`, preserve them separately in raw evidence and map them only under a versioned source contract. If not captured, mark each unavailable; never substitute capture time.
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

All cases below are proposed deterministic tests using isolated synthetic fixtures and clocks. They do not connect to Binance, use production/T1 captures, mutate T0 storage or imply implementation readiness. **No tests or fixtures were created or executed.**

### SD-05 — Aggregate trades (14 cases)

1. Valid native event with distinct `E` and `T`; assert they remain separate.
2. T1 CSV `timestamp_ms` maps only to candidate `T`; assert `E` remains unavailable unless independently captured.
3. Distinct `E`/`T` values catch any reversal or timestamp substitution.
4. CSV `quantity` is retained as unverified candidate; assert it is not treated as proven native `q`.
5. `q` and `nq` differ; assert neither is copied into the other.
6. Missing `nq` yields explicit unavailable status, never a fabricated value.
7. Raw native fixture preserves `E`, `T`, `q`, `nq` independently.
8. Same aggregate ID and same verified semantic payload is replay.
9. Same aggregate ID and changed semantic payload is conflict without overwrite.
10. Missing/negative/non-integer IDs or first ID greater than last ID are rejected/quarantined.
11. Strict maker flag parsing rejects truthy strings and values outside 0/1.
12. Exact decimal parsing rejects NaN, Infinity, malformed exponent/overflow and nonpositive price/quantity.
13. Timestamp/ISO UTC mismatch is rejected; trade time is not relabeled as receive time.
14. Candidate cross-field side/maker consistency is not enforced until source semantics are verified.

### SD-06 — Depth diffs (25 cases)

1. Valid diff preserves U/u/pu and distinct E/T when both are present.
2. Current T1 CSV maps timestamp only to candidate E as documented for depth; T remains explicitly unavailable.
3. Arrival order and source locator are preserved; no sorting by event time.
4. Same range/same payload across epochs is replay only after identity namespace is proven.
5. Same range/changed payload across epochs is conflict.
6. Epoch change alone does not create a new canonical event.
7. Unproven update-ID uniqueness scope causes cross-epoch quarantine, not acceptance.
8. Valid initial snapshot bridge follows the pinned exchange rule.
9. Valid subsequent pu chain is accepted under pinned rules.
10. Missing update creates GAP_PENDING while all bounds remain.
11. Gap age bound expires to durable GAP_UNRESOLVED.
12. Reorder event-count ceiling independently triggers fail-closed state.
13. Raw message byte ceiling rejects before unbounded parse/allocation.
14. Parsed level-count ceiling rejects a message exceeding max levels.
15. Numeric token length/precision ceiling rejects pathological decimal tokens.
16. Aggregate reorder-buffer byte ceiling triggers GAP_UNRESOLVED and book unavailable.
17. Resource rejection persists bounded evidence reference; oversized payload is not copied into an unbounded error record.
18. Resource rejection never advances book-sequence watermark.
19. Source cursor may advance after durable quarantine while book watermark remains before the gap.
20. Restart restores source cursor and book watermark independently.
21. Lost acknowledgement replays the same source observation without duplicate canonical/book effects.
22. Zero quantity removes exactly one level; nonzero quantity replaces absolute quantity.
23. Same timestamp with different update IDs remains distinct.
24. Malformed JSON, wrong tuple arity, duplicate prices, invalid decimal and negative quantity fail closed.
25. Buffer overflow never silently evicts an event; derived book becomes unavailable.

### SD-07 — Bounded order-book snapshots (19 cases)

1. Multi-level bid/ask rows group only with source capture ID and completion manifest.
2. Manifest binds exact source kind/endpoint and request parameters.
3. Requested limit is recorded and constrained to the source-supported allowlist.
4. Actual bid count, ask count and total rows match the manifest.
5. Complete bounded response is accepted only when every returned level is captured and digest/completion evidence agrees.
6. A response at limit 1000 is not labeled a full-depth/full-book snapshot.
7. Endpoint/source-kind mismatch is rejected.
8. Ordinary non-RPI visibility is explicit and cannot be labeled all-liquidity.
9. EOF, file rotation, elapsed time, stable file size or row count alone does not prove completeness.
10. Partial write, restart, missing rows, count mismatch or digest mismatch quarantines the entire capture.
11. Explicit empty-side declaration is distinct from absent rows.
12. Missing capture ID or ambiguous repeated capture is quarantined.
13. Duplicate side/price, mixed metadata or invalid decimal is rejected.
14. Same identity/same complete bounded level set is replay.
15. Same identity/changed level set is conflict; no merge or overwrite.
16. Snapshot update ID anchors only the returned bounded state.
17. Later update outside initial price boundary does not establish unseen deeper levels or full top-N ranking.
18. Snapshot REST E/T are preserved separately if source supplies them; otherwise each is explicitly unavailable, never replaced by CSV capture time.
19. Snapshot group row/byte/level/token ceiling rejects the whole capture with bounded evidence and no partial acceptance.

### Cross-domain cursor, checkpoint and recovery (8 cases)

1. Durable source intake outcome advances source-delivery cursor only after evidence/outcome commit.
2. Durable GAP_UNRESOLVED quarantine may advance source cursor while book watermark remains unchanged.
3. Source acknowledgement never implies sequence continuity or book watermark advancement.
4. Crash between observation persistence and cursor commit does not skip the source position.
5. Crash between diff application and book watermark commit does not apply the same diff twice.
6. Restart resumes source intake and book application from their separate durable markers.
7. Buffered but unapplied events do not advance book watermark.
8. Conflict/resource rejection leaves book unavailable until reviewed recovery with a new bounded snapshot and verified bridge.

**Proposed matrix total: 66 cases** (SD-05 14, SD-06 25, SD-07 19, cross-domain 8). Designed only; NOT EXECUTED.

## 10. Open design blockers before contract freeze

| ID | Blocker | Why it matters | Evidence/decision required |
|---|---|---|---|
| B-01 | Exact T1 aggTrade source mapping and build behavior | Published CSV schema alone does not prove parser correctness or source payload retention | Read-only inspection of pinned T1 source and exact Binance USD-M aggTrade contract |
| B-02 | AggTrade ID semantics and field bounds | Identity and first/last trade-ID meaning must be exact | Confirm exchange contract and T1 code; freeze integer ranges |
| B-03 | `side` vs `is_buyer_maker` relation | Avoid inconsistent or inverted aggressor semantics | Verify exchange semantics and T1 mapping; owner accepts validation |
| B-04 | Depth stream epoch provenance | Current CSV lacks an immutable capture/session epoch needed for continuity and recovery, but epoch must not be part of canonical event identity | Additive source-contract design; capture epoch lifecycle and cross-restart evidence |
| B-05 | Binance depth snapshot/diff bridge and update-ID uniqueness scope | Both canonical update-range identity and sequence acceptance depend on exact USD-M semantics | Pin official USD-M protocol and T1 implementation; verify uniqueness namespace across reconnects and define initial/subsequent bridge algorithm |
| B-06 | Depth diff source message completeness and receive time | CSV does not prove complete original event bytes or collector receive timestamp | Inspect T1 source capture and decide additive provenance fields |
| B-07 | Snapshot capture identity | Current schema has no unique capture ID; timestamp + lastUpdateId may collide | Source-generated immutable capture ID bound to symbol/market/kind/update ID and immutable object evidence |
| B-08 | Snapshot group completeness | One row per level, no count/checksum/end marker/empty-book marker | Source-generated completion manifest/group framing with expected row count (or equivalent), finalized object digest, explicit complete/empty declarations; EOF/rotation/elapsed time/row count alone prohibited |
| B-09 | Snapshot-to-stream epoch linkage | Snapshot anchor must correspond to the intended diff stream | Define source lifecycle/session relationship and recovery semantics |
| B-10 | File immutability and row locator | CSV append/rotation may expose partial groups or changing bytes | Exact close/manifest rule, immutable object SHA and stable row locator |
| B-11 | Canonical digest/decimal serialization | Cross-language deterministic replay/conflict decisions | Separate versioned byte-encoding specification and review |
| B-12 | Atomic provenance, identity, outcome and checkpoint persistence | No ack before durable evidence; no sequence skips | Logical transaction/recovery design aligned with T0 single-writer/fencing |
| B-13 | T0 API and dataset-version compatibility | Microstructure data is not a Candle and must not silently alter candle API | Separate non-candle read contract/version and consumer compatibility review |
| B-14 | Bounded reorder/gap policy numeric limits | Count/age bounds and gap wait determine memory safety and recovery correctness | Measure source behavior; owner-review max buffered events, max residence age, wait policy and resource budget before freeze |
| B-15 | Native `nq` and depth transaction-time `T` fidelity | Current T1 CSV omits aggTrade `nq` and depth `T`; `q` and `nq` differ, while `E` and `T` are separate clocks | Inspect pinned T1 source/raw retention; decide versioned canonical vs raw-only fields; current CSV must explicitly mark both unavailable where absent |
| B-16 | RPI visibility and source-domain scope | Ordinary depth excludes RPI and is not a complete all-liquidity book | Keep Phase B non-RPI; separately approve any RPI stream and merge contract before inclusion |
| B-17 | AggTrade E/T and CSV source fidelity | E is event time; T is trade time; current CSV timestamp_ms is documented as trade time but exact parser mapping is not verified | Inspect pinned T1 parser/source read-only; preserve E/T distinctly; never map timestamp_ms to E |
| B-18 | Snapshot bounded-depth source manifest | A fully captured top-N response is not a full exchange book | Manifest binds endpoint/source kind, requested limit, actual bid/ask counts, total rows, capture ID, digest, completion and non-RPI scope; define bounded derived-view semantics |
| B-19 | Independent source cursor and book watermark | Durable quarantine acknowledgement can coexist with unresolved book sequence gap | Freeze separate cursor definitions, atomicity, restart/replay and acknowledgement semantics; align with B-12 |
| B-20 | Parser and capture resource ceilings | Count/age limits alone do not bound memory, parsing CPU or snapshot group accumulation | Measure and owner-review max raw bytes, levels, numeric token size/precision, buffer bytes and snapshot group rows/bytes; add fail-closed tests |

## 11. Phase B exit criteria and owner review

- [x] Three Phase B domains scoped: SD-05, SD-06, SD-07.
- [x] Native T1 documented columns mapped to candidate canonical fields.
- [x] Candidate identity and domain-specific sequence/grouping semantics described.
- [x] Timestamp/provenance limitations called out without fabricated receive times.
- [x] Replay/conflict/quarantine/acknowledgement behavior drafted.
- [x] Synthetic test matrix expanded to 66 proposed cases, including E/T separation, unverified q mapping, bounded top-N snapshots, independent cursors and byte/level/token/group resource ceilings; explicitly marked NOT EXECUTED.
- [x] Contract-freeze blockers recorded.
- [ ] B-01 through B-20 resolved or explicitly accepted as bounded exclusions by owner.
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
