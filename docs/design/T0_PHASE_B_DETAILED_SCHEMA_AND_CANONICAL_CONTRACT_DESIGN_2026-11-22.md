# T0 Phase B — Detailed Schema & Canonical Contract Design

- Date: 2026-11-22
- Status: **PHASE B DESIGN DRAFT — OWNER REVIEW REQUIRED**
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

### 3.1 Native-to-candidate mapping

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

### 3.2 Candidate identity and acceptance

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

### 3.3 Time and provenance

- Native `timestamp_ms` is trade time, not collector receive time.
- Current documented CSV has no explicit collector receive timestamp or WebSocket stream epoch.
- Preserve source object SHA-256, immutable object locator, row locator, source schema/parser version and T0 receipt/commit times.
- A historical file import time must not be relabeled as original collector receive time.
- A raw CSV row digest is not an exchange message digest unless exact byte framing and original message retention are proven.

### 3.4 Validation and quarantine

Quarantine/reject on missing/duplicate/invalid header, wrong datatype, unknown symbol/market, malformed timestamp, mismatch between `timestamp_ms` and `datetime_utc`, invalid ID ordering, non-finite/invalid decimal, zero/negative price or quantity, invalid maker flag, or ambiguous row provenance. Do not coerce or silently skip.

## 4. SD-06 — Order-book depth diffs

### 4.1 Native-to-candidate mapping

| Native field | Documented meaning | Candidate canonical field | Notes |
|---|---|---|---|
| `timestamp_ms` | event time | `event_time_ms` | Not receive time |
| `first_update_id` | U, first update ID | `first_update_id` | Inclusive sequence start per source contract |
| `last_update_id` | u, final update ID | `final_update_id` | Must be >= U |
| `prev_update_id` | pu, previous event's u | `previous_final_update_id` | Continuity evidence |
| `bids_json` | array of [price, qty] | `bid_changes` | Absolute quantities; zero removes level |
| `asks_json` | array of [price, qty] | `ask_changes` | Absolute quantities; zero removes level |
| Common fields | exchange/market/symbol | instrument envelope | Explicit source namespace |

### 4.2 Candidate identity and sequence integrity

Candidate message identity:
`(exchange, market_type, symbol, stream_epoch, first_update_id, final_update_id)`.

**Important:** `stream_epoch` is not present in the documented CSV schema. A collector connection/restart epoch or an equivalent immutable stream-session identifier must be added/evidenced before this identity can be frozen. Do not substitute a guessed value, file date or timestamp.

Candidate sequence rules, subject to exact Binance USD-M stream-contract verification:

- Require `first_update_id <= final_update_id`; all IDs are integers in the supported range.
- Validate each diff against a snapshot anchor and active stream epoch using the exchange-prescribed initial bridge and subsequent continuity rules.
- The documented `prev_update_id` chain must be retained and checked; do not treat timestamps as sequence.
- A sequence gap, regression, unexplained overlap, epoch mismatch or conflicting repeated range marks the reconstructed book state discontinuous. Record gap/conflict evidence and fail closed; do not claim a valid continuous book.
- Same epoch + same update range + same semantic payload is replay.
- Same epoch + same update range + changed payload is conflict.
- Overlapping ranges are not automatically duplicates. Apply only the exchange's verified sequence rules; preserve both source observations until adjudication.
- Each bid/ask change is an absolute quantity at a price level, not a delta to add. Quantity zero means delete the level.
- Never drop a message because its event timestamp matches another message.

### 4.3 Payload validation

- Parse `bids_json` and `asks_json` as arrays of two-element arrays only.
- Price must be a positive exact decimal; quantity must be a nonnegative exact decimal.
- Reject duplicate price levels within one side/message unless the source contract explicitly defines a deterministic resolution.
- Reject invalid side structure, malformed JSON, NaN/Infinity, exponent/precision overflow and noncanonical numeric coercion.
- Preserve bid and ask arrays independently; do not infer missing side as empty without source evidence.
- Cross-side price crossing may be a valid transient or indicate invalid state depending on sequence position; do not impose an unreviewed rule on an individual diff message.

### 4.4 Time, provenance and checkpoints

- `timestamp_ms` is event time. It is not a sequence cursor or collector receive time.
- Current CSV schema does not document collector receive time, stream epoch, connection identity or durable per-message cursor beyond U/u/pu.
- A file offset is not sufficient as a semantic checkpoint for a live order-book stream.
- A future checkpoint must bind source identity, stream epoch, last durably accepted sequence, snapshot anchor/version, and immutable source evidence position.
- T0 acknowledgement may advance only after the accepted diff (or durable quarantine/gap outcome) and associated checkpoint state are committed atomically or through a reviewed recovery protocol.
- Lost acknowledgement retries the same immutable message identity; it must resolve as replay, not a second book update.

### 4.5 Book-state semantics

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
- A partially written file, interrupted group, missing final rows or unknown file-close boundary must not be accepted as a complete snapshot.
- Preserve zero-level/empty-side semantics only if the collector's source contract explicitly represents them; absence of rows cannot safely be interpreted as an empty side.
- Snapshot `last_update_id` anchors the book state. It is not a trade ID and must not be mixed with SD-05 identifiers.
- Same proven snapshot identity + identical complete level set is replay. Same identity + differing level set is conflict; never merge levels or overwrite.
- A snapshot is a reconstruction anchor, not a substitute for the diff history before/after it.

### 5.4 Provenance and time

- `timestamp_ms` is documented as when the snapshot was taken; do not call it an exchange event timestamp without evidence.
- Preserve object SHA-256, immutable source locator, row range/ordinals, source schema/parser version and T0 receipt/commit times.
- Current CSV does not expose collector receive time, REST request ID, snapshot capture ID or completeness manifest.
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

### SD-05
1. Valid BTCUSDT aggregate trade with native trade ID.
2. Duplicate ID and identical payload resolves to replay.
3. Duplicate ID with changed price/quantity/side/time/maker flag resolves to conflict without overwrite.
4. Missing/negative/non-integer IDs; first ID greater than last ID.
5. Strict `is_buyer_maker` 0/1 parsing; reject truthy strings and values outside domain.
6. Exact decimal parsing; reject NaN, Infinity, malformed exponent/overflow and nonpositive price/quantity.
7. `timestamp_ms`/ISO UTC mismatch and event-time vs receive-time separation.
8. Cross-field side/maker consistency tests only after source semantics are frozen.

### SD-06
1. Valid diff with U/u/pu and bid/ask absolute quantities.
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
1. Multi-level bid/ask rows group into one complete snapshot.
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
| B-04 | Depth stream epoch identity | Current CSV lacks a connection/session epoch; U/u/pu alone may not distinguish restarted streams | Additive source-contract design or evidence for an immutable epoch field |
| B-05 | Binance depth snapshot/diff bridge rules | Sequence acceptance must match exact USD-M protocol | Pin official stream/REST contract and source implementation; define anchor/bridge algorithm |
| B-06 | Depth diff source message completeness and receive time | CSV does not prove complete original event bytes or collector receive timestamp | Inspect T1 source capture and decide additive provenance fields |
| B-07 | Snapshot capture identity | Current schema has no unique capture ID; timestamp + lastUpdateId may collide | Source-generated ID or approved collision-safe immutable capture boundary |
| B-08 | Snapshot group completeness | One row per level, no count/checksum/end marker/empty-book marker | Add manifest/group framing and explicit close/completeness proof |
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
- [x] Synthetic test matrix proposed and explicitly marked not executed.
- [x] Contract-freeze blockers recorded.
- [ ] B-01 through B-13 resolved or explicitly accepted as bounded exclusions by owner.
- [ ] Canonical DTO/envelope, digest encoding, snapshot capture/group identity and diff stream epoch contract reviewed/frozen.
- [ ] Independent design review completed and findings resolved.

**Owner review requested:** review this Phase B design baseline, its candidate identities, sequence/snapshot integrity requirements and B-01..B-13 blockers. Approval of this draft would accept the design baseline only if explicitly stated; it would not authorize implementation unless a separate implementation decision names its exact scope.

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
