# T0 Phase B — Detailed Schema & Canonical Contract Design

- Date: 2026-11-22 (revision 9)
- Status: **PHASE B DESIGN REVISION 9 — FULL REVIEW FINDINGS R8-01..R8-04 ADDRESSED AT DOCUMENTATION LEVEL / OWNER DECISIONS AND EVIDENCE STILL REQUIRED**
- Immutable source baseline: Revision 8 design commit `9a5c65f3bc00876d98a070eee46072c5d8be368e`, blob `8f40248f2781cdf4111ef022b77843acea8279b2`. Revisions 6, 7 and 8 remain immutable; Revision 9 is a documentation-only successor.
- Scope: SD-05 aggregate trades; SD-06 order-book depth diffs; SD-07 order-book snapshots.
- Authorization: owner-approved Phase A review and Phase B documentation-only authorization, decision commit `f2f5741cad47b86c70dae23dbaa9b497258cc80a`.
- Reference only (non-binding proposal; owner review required): `docs/design/T0_SOURCE_DOMAIN_INVENTORY_AND_CANONICAL_INGESTION_CONTRACT_V1_2026-11-22.md`. For Phase B SD-06 and SD-07 identity, the detailed rules in this Revision 9 are the candidate successor rules and explicitly supersede the Inventory's conflicting identity examples for this bounded Phase B scope only. This is not an owner-approved contract or Contract Freeze.
- Phase A baseline: `docs/design/T0_PHASE_A_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`.
- T1 source schema: `kenznguyen/binance-futures-collector/docs/SCHEMA.md`, blob SHA `895f87a8281a3f9b6d37d96b5f68568e4285bee6`.
- Implementation: **NOT AUTHORIZED / NOT STARTED**.
- Synthetic matrix: **DESIGNED ONLY / NOT EXECUTED**.
- Tests/workflows/artifacts: **NOT RUN / NONE**.

## 1. Purpose, authority and invariants

This document advances only the detailed design for Phase B's three microstructure domains. It does not freeze a wire DTO, storage schema, digest encoding, checkpoint protocol or source contract.

### 1.1 Document authority and identity supersession map

The Source Domain Inventory v1 cited above is a **DESIGN PROPOSAL — OWNER REVIEW REQUIRED**, not an owner-approved governing contract. It is retained as a broad inventory/reference document and remains useful for ownership and domain context. Its SD-06/SD-07 identity examples are not authoritative for Phase B after this detailed revision. To remove ambiguity, the candidate Phase B identity rules are:

| Domain | Candidate canonical/capture identity | Fields explicitly not in that identity | Required interpretation |
|---|---|---|---|
| SD-06 depth diff | `(exchange, market_type, symbol, first_update_id, final_update_id)` subject to proof of uniqueness scope | `stream_epoch`, timestamps, source-delivery locator, collector process/connection IDs | `stream_epoch` is continuity/capture provenance only. It cannot be appended to the canonical key to conceal an unproven exchange identity namespace. |
| SD-07 snapshot capture | `(capture_producer_id, capture_sequence)` only | `exchange`, `market_type`, `symbol`, `source_kind`, `last_update_id`, snapshot event type, timestamp, request/depth parameters, producer version, payload/object digest and delivery locator | All excluded fields are immutable attributes bound to the pair. A changed attribute under the same pair is identity reuse/conflict, not a distinct capture. `(side, price)` identifies a level within a completed capture, not a capture identity. |

This Revision 9 mapping is the only candidate identity interpretation to use when reading the Phase B clauses and proposed test matrix. The older Inventory identity examples remain historical proposal text and are explicitly superseded for these two domains only. The Inventory itself is not silently edited by this document. Before Contract Freeze, the owner must either approve this bounded supersession or approve a versioned Inventory amendment with the same identity rules. No owner approval is implied here.

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

### 4.3.1 Non-identical overlapping update ranges — deterministic adjudication rule

A non-identical overlap is not a duplicate by range similarity and is not automatically accepted. Preserve each immutable source observation first. Adjudicate only against the exact pinned Binance USD-M Diff Book Depth protocol version and verified T1 parser/sequence behavior:

1. **Protocol-valid overlap candidate:** eligible for application only if the pinned protocol explicitly permits the observed overlap/bridge, the event's `pu` equals the currently applied final update ID as required by that protocol, the range covers the next required update, the active snapshot/stream epoch is valid, and no prior gap/conflict exists. If any condition is not evidenced, quarantine; do not infer validity from `U/u` overlap alone.
2. **Unproven or invalid overlap:** if `pu` does not satisfy the pinned predecessor rule, the range fails the documented bridge/continuity condition, the epoch/anchor is missing, or protocol evidence is unavailable, persist a sequence-conflict/gap outcome, mark the derived book unavailable and do not advance the book watermark.
3. **Same/overlapping range with changed payload:** if the same canonical range identity is reused with different semantic content, classify as `CONFLICT`, retain both source observations and do not apply the second payload. A partially overlapping but different range is not silently merged; it follows rule 1 only when the exchange protocol proves it is a valid next update, otherwise rule 2.
4. In all outcomes, source-delivery cursor progression is independent and may advance only after durable intake outcome/evidence; it never advances the book watermark. The synthetic matrix cases 29–31 exercise these distinctions but remain NOT EXECUTED.

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
- Lost-acknowledgement retry reuses the **same immutable source-delivery locator** (for example, immutable source-object digest plus stable row/group locator). Intake deduplicates that delivery position and returns its previously committed outcome; it must not create a new capture or apply a second book update. Canonical exchange-event deduplication remains a separate operation using the verified native exchange namespace/update range. Snapshot capture deduplication uses the producer-issued capture identity and immutable capture evidence defined in §5.2–§5.3. A stream/process epoch is continuity provenance only, not a retry key.

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

- **Source-delivery/import cursor:** identifies the last immutable source-delivery locator (for example, source-object SHA-256 plus stable row/group locator, or an equivalently immutable delivered-message locator) whose raw observation and terminal intake outcome (`ACCEPTED`, `DUPLICATE_REPLAY`, `CONFLICT`, `QUARANTINED`, or durable gap/resource outcome) have been durably recorded. It may advance after durable quarantine of a gap or malformed observation because source intake is complete for that position. This locator is not the exchange-native event identity, snapshot capture identity or a per-attempt T0 import ID.
- **Book-sequence watermark:** identifies the highest contiguous update sequence actually applied to the derived book from its active snapshot anchor. It advances only after the corresponding canonical diff and derived application state are durable, and never across a missing sequence, conflict, quarantine, resource rejection or unapplied buffered event.

A source cursor advancing past a durably quarantined gap means only that the source observation has been safely ingested and its outcome recorded. It does **not** mean the book is continuous, does not acknowledge missing exchange updates, and must not move the book-sequence watermark.

Restart/replay rules:
1. Resume source intake after the last durable source cursor. If acknowledgement was lost, retry the **same immutable source-delivery locator**; delivery-locator/outcome dedupe must return the prior durable result without duplicating raw evidence or canonical effects. Resolve exchange-event deduplication by verified native identity and snapshot-capture deduplication by producer-issued capture identity independently; never substitute one identity domain for another.
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
| `timestamp_ms` | snapshot capture time in current T1 CSV | `snapshot_captured_at_ms` | Not native REST event/transaction time |
| `E` (if returned by the selected REST/source variant) | response/event time | `snapshot_event_time_ms` | Preserve separately when actually captured; otherwise unavailable |
| `T` (if returned by the selected REST/source variant) | transaction time | `snapshot_transaction_time_ms` | Preserve separately when actually captured; otherwise unavailable |
| `event_type` | initial/periodic/bridge snapshot type | `snapshot_kind` | Enum allowlist |
| `side` | bid or ask | `side` | Strict enum |
| `price` | level price | `price` | Exact positive decimal |
| `quantity` | level quantity | `quantity` | Exact positive decimal for retained levels |
| `last_update_id` | book version | `last_update_id` | Snapshot sequence anchor |
| Common fields | exchange/market/symbol | instrument envelope | Explicit source namespace |

### 5.2 Grouping, source-kind allowlist and bounded-depth scope

The native CSV is one row per price level, not one row per snapshot. T0 must group all rows belonging to one capture before canonical acceptance. A single level row is never a complete capture. The CSV `event_type` values (`depth_snapshot_initial`, `depth_snapshot`, `depth_snapshot_bridge`) describe lifecycle intent only; they do **not** prove how the snapshot was obtained. Do not infer source kind from `event_type`.

The design allowlist has two supported candidate source kinds, each with a distinct completeness contract, plus an explicit reject bucket:

| Candidate `source_kind` | Meaning | Required source evidence and acceptance contract |
|---|---|---|
| `BINANCE_USDM_REST_DEPTH_RESPONSE_V1` | Direct response from the ordinary Binance USD-M REST depth endpoint | Preserve the exact raw response or an equivalently verifiable immutable source object; bind `GET /fapi/v1/depth`, symbol, requested limit, response `lastUpdateId`, response `E`/`T` when supplied, actual bid/ask counts, total rows, capture ID, digest and explicit completion. Completeness means every level in that exact bounded response is present, not the entire exchange book. |
| `T1_RECONSTRUCTED_LOCAL_BOOK_V1` | Snapshot serialized from T1's locally reconstructed book | Bind the upstream REST snapshot anchor and its source identity; stream/session epoch; last contiguous diff update applied; continuity state at capture; configured depth boundary/retention policy; source-book generation; exact capture ID, level counts, digest and completion. Acceptance requires proof that no unresolved gap, overflow, conflict or resource rejection preceded the capture and that all declared retained levels were emitted. A local snapshot is not a REST response and must not claim REST response metadata it did not receive. |
| `UNSUPPORTED_OR_UNKNOWN` | Any source variant not explicitly covered by a reviewed contract | Reject/quarantine; no canonical acceptance. |

The current T1 CSV schema does not identify which of these source kinds produced any given `event_type`. Until additive source provenance makes the distinction verifiable, every current-schema snapshot remains `NOT_CANONICAL_ACCEPTABLE`. A future source-kind value is not implicitly accepted; it requires a separately reviewed contract.

#### Producer namespace authority, uniqueness scope and lifecycle (candidate policy; not frozen)

To make the uniqueness claim operationally bounded, the candidate namespace policy is:

- **Authority:** T0 Foundation owns the producer registry, allocates/assigns each unique `capture_producer_id` within the canonical identity domain, controls registration admission, scope authorization, activation/revocation state and audit history. T1 cannot self-assign or repurpose a producer ID; it owns issuance of `capture_sequence` values only within its authorized producer namespace. T0 validates but never mints, repairs or substitutes a capture pair on an incoming record.
- **Uniqueness domain:** a `capture_producer_id` must be unique across every producer, process, host, environment, deployment, backup/restore lineage and collector version that can write into the same T0 canonical SD-07 identity domain. Separate environments may use separate namespaces only when they are technically isolated canonical identity domains and cannot later be merged without a reviewed namespace migration. A label such as `prod` or `test` is not proof of isolation.
- **Single-writer scope:** at most one active sequence allocator may issue values for a producer ID at a time. Clones, parallel processes, stale restored copies and split-brain writers must be fenced before issuance. If fencing cannot be independently verified, all captures from the ambiguous writer scope remain quarantined.
- **Lifecycle:** producer IDs are allocated once, immutable, never recycled and never reassigned to another collector/source kind. A software upgrade may retain the same producer ID only if durable sequence continuity and identity-scheme compatibility are proven. A replacement, transfer or incompatible identity-scheme change receives a new producer ID unless an explicitly reviewed transfer proves exclusive fencing and monotonic sequence continuity.
- **Revocation/retirement:** revoked or retired IDs remain permanently reserved in the registry and cannot be reactivated for a different writer or scope. Revocation blocks new captures; previously accepted evidence remains immutable and auditable.
- **Backup/restore/rollback:** restoring producer state must not permit sequence reuse. The old writer must be fenced, the restored allocator must prove a durable high-water mark and monotonic continuation, and rollback/clone evidence must be checked before the producer can become active. If any part is unproven, fail closed.
- **Proof boundary:** a registry row, self-asserted producer string, process UUID, timestamp or digest is not proof of unique issuance. The trust root, credential/workload identity lifecycle, allocation protocol, fencing primitive, durable high-water-mark storage and independent verifier remain NOT SPECIFIED / NOT FROZEN. Therefore this policy bounds the intended scope but does not close B-07 or make any current capture canonically acceptable.

For direct ordinary Binance USD-M REST depth responses, the response is bounded top-N depth (documented limits include 5, 10, 20, 50, 100, 500 and 1000; maximum 1000). It is not an unlimited representation of the entire order book. A complete capture means **all levels returned by that exact bounded response were captured and verified**, not that the exchange's entire book was captured. For collector-reconstructed snapshots, completeness is limited to the explicitly declared local retained-depth boundary and proven source-book continuity; it is not proof of unseen exchange levels.

Three identity domains must remain distinct:

1. **Exchange-native snapshot anchor/response fields:** Binance USD-M REST depth supplies the response's native `lastUpdateId` and bounded bid/ask payload; the REST response contract described here does not identify a Binance-issued unique capture ID. `lastUpdateId` is a book-version anchor, not a unique acquisition/capture identity. Do not claim Binance issued `snapshot_capture_id` unless a source field is independently evidenced.
2. **Producer-issued capture identity:** the component that actually acquires/serializes the capture issues an immutable ID. For `BINANCE_USDM_REST_DEPTH_RESPONSE_V1`, this is the T1 component in `kenznguyen/binance-futures-collector` that issues the Binance USD-M REST depth request and preserves the exact response; it is not Binance and is not a T0 ingestion component. For `T1_RECONSTRUCTED_LOCAL_BOOK_V1`, this is the T1 component in the same collector repository that serializes the reconstructed local book. Candidate form: `(capture_producer_id, capture_sequence)`, where `capture_producer_id` is a stable, uniquely provisioned producer namespace and `capture_sequence` is monotonically allocated from durable producer state, never reset/reused across process restarts. Sequence gaps are permitted. A producer clone or restored stale state must not reuse the same namespace/sequence pair; if uniqueness/fencing cannot be proven, reject/quarantine rather than inventing identity. This is a candidate contract, not a frozen ID format.
3. **T0 source-delivery/import locator:** identifies where the immutable capture was delivered from, independently of capture identity. Candidate locator: immutable source-object SHA-256 plus a stable capture-group byte range/ordinal (or another source-native immutable locator); a mutable path, file name, file offset without object digest, or per-attempt import sequence alone is insufficient. T0 must preserve the capture ID and evidence when importing; it must not relabel a T0-generated import ID as the producer's capture ID. A retry reuses the same locator.

For direct REST, the producer is the registered T1 SD-07 capture component in `kenznguyen/binance-futures-collector`. It issues the request and preserves the response; T0 does not fetch the response on T1's behalf, issue the producer capture ID, or replace that ID during ingestion. Bind the producer-issued capture ID to the exact request method/endpoint, symbol, requested limit and parameters, request/capture time, response `lastUpdateId`, raw response bytes (or an equivalently immutable object) and its digest, plus producer identity/sequence and registration evidence. Allocate the capture identity once for that acquisition and persist it with the immutable response before acknowledging delivery. Retrying delivery of that stored capture reuses the same ID and locator; making a new REST request is a new acquisition and receives a new capture ID, even if Binance returns the same `lastUpdateId`, timestamp or identical payload.

For a T1 reconstructed local book, bind the T1-issued capture ID to the upstream REST snapshot anchor/identity, stream epoch, last contiguous diff update applied, continuity state, local-book generation, retained-depth policy, emitted level counts and immutable serialized payload digest. An unresolved gap, missing epoch, generation ambiguity or inability to bind the capture ID to this evidence prevents canonical acceptance.

**Revision 7 — capture identity key and immutable attributes (P2-1 correction).** The producer-issued capture identity key is exactly `(capture_producer_id, capture_sequence)`. This pair is independently unique within the globally governed producer namespace and MUST NOT be expanded with mutable capture attributes to form a different identity. The following are immutable attributes bound to that key: `exchange`, `market_type`, `symbol`, `source_kind`, requested REST limit or reconstructed depth policy, native `last_update_id`/upstream anchor, `snapshot_captured_at_ms`, request parameters, producer implementation/version, identity-scheme version, immutable raw-response or serialized-payload digest, level counts and completion-manifest digest. The first durable evidence record for a key establishes its immutable attribute set. A later observation with the same pair and identical immutable attributes/evidence is an idempotent replay; the same pair with ANY changed/missing/contradictory immutable attribute is an identity conflict and MUST be quarantined. It MUST NOT become a new capture merely because an anchor, timestamp, limit, source kind, symbol or digest differs. A genuinely new acquisition requires a never-before-issued producer sequence under a correctly fenced namespace. The T0 source-delivery locator remains a separate identity domain and is not part of this key.

For clarity, the former composite proposal containing exchange, symbol, source kind, anchor, timestamp and producer pair is superseded as an identity key. Those non-producer fields are immutable evidence attributes checked against the producer pair, not dimensions that can make a reused pair unique. This rule is a candidate design requirement and is not frozen until the producer allocator, persistence and conflict-handling contracts are reviewed.

Do not invent an ID from row order, timestamp, file path, file rotation or a locally assigned T0 import sequence. Two separately acquired captures have different producer-issued pairs even if their `lastUpdateId`, timestamp and payload happen to match; retain them as distinct capture observations and do not collapse them into a retry replay. A T0 delivery locator may differ only when the same immutable capture is legitimately mirrored/repackaged under a separately evidenced delivery; preserve both delivery provenance records while deduplicating the capture itself.

**Revision 7 — producer-origin authenticity (P2-2 correction; candidate, not frozen).** A registered `capture_producer_id`, matching scope and response digest prove neither who submitted the object nor that T1 issued it. Canonical acceptance therefore requires verifiable evidence of producer origin, in addition to byte integrity and registration. Two candidate evidence modes may be evaluated in a separately reviewed handoff contract: (A) a producer attestation generated by the authorized T1 producer and cryptographically verifiable against an owner-approved trust binding; or (B) an explicitly trusted authenticated handoff whose authenticated workload principal is bound to the registered T1 producer and whose integrity-protected receipt binds the exact capture pair, source kind/scope, producer implementation and identity-scheme versions, immutable response/payload digest, and source-delivery locator. Either mode must provide replay-resistant, durable evidence that T0 can verify at intake. A self-asserted producer ID, unsigned manifest, digest alone, mutable file path, or unauthenticated object upload is insufficient.

The trust root, key or workload-identity provisioning, key rotation/revocation, attestation format/signature algorithm, authenticated transport/handoff mechanism, verifier implementation, clock/replay policy and durable proof retention are NOT SPECIFIED OR FROZEN here. Do not assume that any current T1 CSV/file handoff already supplies this proof. Until one evidence mode is explicitly selected, implemented in its owning boundary, independently verified and bound to an owner-approved trust registry, missing, invalid, expired, revoked, mismatched or unverifiable origin proof MUST fail closed and quarantine the capture. T0 validates proof; it does not impersonate T1 or mint a T1 attestation.

**SD-07 source-capture ownership and producer registration (candidate; not frozen).** Both allowlisted SD-07 source kinds are captured/produced by T1 under the approved collector ownership boundary: direct REST response acquisition and T1 reconstructed-local-book serialization remain within `kenznguyen/binance-futures-collector`. T1 is the source-capture producer; T0 is the canonical owner and ingestion/validation boundary. The application repository may define the registration contract and validate its evidence, but must not become a second SD-07 exchange collector or silently issue/replace T1's capture identity. A different collector may act as SD-07 producer only after a separate explicit owner-approved architecture decision and a separately reviewed source contract.

The candidate T0 source registry must validate a producer-registration record binding at least: (a) `capture_producer_id`; (b) collector identity and repository/owner identity (currently T1 / `kenznguyen/binance-futures-collector`); (c) the exact permitted source kind (`BINANCE_USDM_REST_DEPTH_RESPONSE_V1` or `T1_RECONSTRUCTED_LOCAL_BOOK_V1`); (d) exchange/market/domain and permitted symbol or symbol-scope; (e) producer implementation/version and capture-identity scheme version; and (f) registration status/scope. This registration is an authorization/provenance binding, not a substitute for the capture identity or source evidence. A producer ID registered for one source kind, market/domain or scope must not be accepted for another. Unknown, inactive, unregistered or mismatched producer registration fails closed and is quarantined; do not reinterpret it as a missing `lastUpdateId` or as an ordinary payload validation error.

The registration/allowlist is maintained at the T0 canonical acceptance boundary from owner-approved producer registration evidence. T0 may validate and record the registration reference/version, but it does not mint the producer's capture ID or sequence. The T1 producer must allocate and persist its own capture identity before acknowledging delivery. A candidate producer namespace must be uniquely provisioned to the authorized T1 producer component and fenced against concurrent clones, stale restored state and sequence rollback. The exact provisioning, durable allocator, single-writer/fencing mechanism and recovery proof are NOT FROZEN; until uniqueness and non-reuse are evidenced, the affected capture remains rejected/quarantined and B-07 stays OPEN. Merely matching the registered producer string does not prove exclusive ownership or durable sequence allocation.

**Revision 7 — producer namespace fencing proof (P2-3 correction).** Registration and an apparently increasing sequence are not proof of uniqueness. Before any SD-07 capture is eligible for canonical acceptance, the evidence package must establish all of the following for the producer namespace and sequence allocator: (1) one uniquely provisioned namespace is bound to the authorized T1 producer identity and cannot be concurrently claimed by another process/clone; (2) a verifiable single-writer lease/fencing mechanism prevents stale or concurrent writers from issuing accepted identities; (3) sequence allocation is durable and monotonic across restart, crash recovery, backup/restore and deployment replacement, with no rollback or reuse; (4) allocator state transitions are committed before capture delivery acknowledgement; and (5) the proof is bound to the producer identity/scheme version and is verifiable by T0 from trusted evidence. A gap in sequence values is permitted; reuse or uncertain allocator state is not.

The concrete namespace provisioning, fencing token/lease protocol, durable allocator, restore epoch, anti-clone controls and proof format are NOT FROZEN and have not been demonstrated. A producer registry row or a producer-supplied boolean such as `fencing_verified=true` is not sufficient evidence. Until independently verifiable proof is available, all captures from that namespace remain `QUARANTINED / NOT CANONICALLY ACCEPTABLE`, including otherwise well-formed positive examples. B-07 remains OPEN. No design text here claims the existing T1 collector currently implements these guarantees.

Within one capture, level identity is `(side, price)`. The full declared level set must be deterministic and duplicate-free. Preserve bid and ask counts separately; an absent side is not an empty side unless the source manifest explicitly declares zero returned levels.

### 5.3 Completeness, boundedness and consistency

- Validate one consistent `event_type`, `last_update_id`, timestamp, exchange, market, symbol, source kind and capture manifest across every row in a group. Validate REST endpoint/request limit only for the REST source kind; validate upstream anchor/epoch/contiguous-applied-update/depth policy only for the reconstructed-local-book source kind.
- Require only the versioned snapshot event types permitted by the source contract.
- Reject duplicate `(side, price)` levels, invalid sides, nonpositive price/quantity, malformed decimals and mixed group metadata.
- The current CSV row schema has no explicit group header, expected level count, checksum, end marker or empty-book marker. A file/row batch alone does not prove capture completeness.
- Minimum future acceptance evidence is: (a) independently unique producer identity key `(capture_producer_id, capture_sequence)` with every immutable capture attribute checked against that key; (b) an active T0 registry record binding producer ID to authorized T1 collector/repository, exact SD-07 source kind, exchange/market/domain and permitted symbol scope, producer implementation/version and identity-scheme version; (c) verifiable producer-origin attestation or trusted authenticated-handoff proof binding the identity key, scope/version and immutable response/payload digest; (d) independently verifiable namespace uniqueness, single-writer fencing and durable sequence non-reuse/rollback protection; (e) explicit group framing/boundary; (f) expected total row count or equivalent source completeness declaration; (g) finalized immutable source-object/raw-response digest; and (h) a completion manifest binding capture identity, producer, symbol/market, source kind/endpoint, requested depth limit or retained-depth policy, actual bid count, actual ask count, total row count, snapshot kind, native update anchor, capture time, immutable object digest, non-RPI visibility and completion status. For direct REST, the capture producer is the registered T1 request/response acquisition component in `kenznguyen/binance-futures-collector`; T0 validates the registration and preserves the issued identity/evidence but does not issue or replace the capture ID. Binance's `lastUpdateId` remains the native book anchor and is not misrepresented as a Binance capture ID. For reconstructed local books, the capture producer is T1 and the manifest additionally binds upstream anchor, epoch, last contiguous applied update, continuity state and local-book generation.
- The manifest must identify the exact source variant and its variant-specific proof. A REST manifest binds endpoint and request parameters; a reconstructed-book manifest binds the upstream anchor, epoch, contiguous applied update and retained-depth policy. Never require REST-only fields from a local snapshot or treat missing REST fields as evidence of a local snapshot.
- Empty-side/empty-book captures require explicit source/manifest declarations with zero counts. Absence of rows is not evidence of an empty side or book.
- File EOF, file rotation, elapsed time, stable-looking file size or observed row count alone is never proof of completion.
- Partial write, process restart, collector crash, object mutation, missing end marker, row-count mismatch or digest mismatch quarantines the entire capture; no partial prefix is accepted.
- Snapshot `last_update_id` anchors only the returned bounded/declared retained-depth state. It is not a trade ID and must not be mixed with SD-05 identifiers. For a reconstructed local snapshot, the manifest must additionally identify the last contiguous diff applied; the snapshot's declared anchor cannot conceal an earlier unresolved gap.
- Same proven snapshot identity + identical complete bounded level set is replay. Same identity + differing level set is conflict; never merge levels or overwrite.
- A snapshot is a bounded reconstruction anchor for its declared source and depth scope, not proof of the full exchange book.
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
| SD-06 diff vs SD-07 snapshot | Diff continuity is evaluated relative to a source-proven bounded snapshot anchor and stream epoch; snapshot anchors only its declared returned/retained depth scope, never the unseen full exchange book |
| SD-05 event time vs SD-06 event time | Both are UTC milliseconds but are not a common deduplication key |
| Raw source rows vs derived order book | Preserve raw rows/messages; reconstructed book is a versioned derived view |
| T1 files vs T0 canonical records | T1 files remain source evidence/capture output, not a competing canonical dataset |

## 7. Common provenance and acceptance envelope

Reuse the Phase A logical envelope direction without freezing serialization:

- contract name/version;
- registered source and collector identity/version;
- producer-registration reference/version and its source-kind/domain/symbol-scope binding (when a producer-issued capture identity is present);
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
| Missing native identity | Quarantine | Quarantine when native update-range identity is absent/unverifiable | Quarantine when source-generated capture identity/completeness is missing |
| Unknown/unregistered or source-kind/domain-mismatched capture producer | Not applicable | Not applicable | Quarantine; this is a producer ownership/registration failure, distinct from missing `lastUpdateId` |
| Missing stream epoch/continuity provenance | Not applicable to aggregate-trade identity | Quarantine from book-continuity acceptance; retain source observation and candidate native identity separately; epoch absence does not redefine canonical event identity | For reconstructed-local-book captures, quarantine because upstream epoch/continuity proof is required; for direct REST captures, apply only the REST source contract and do not invent an epoch requirement |
| Malformed numeric/JSON | Quarantine/reject | Quarantine/reject | Quarantine/reject |
| Out-of-order delivery | Retain by native trade ID/time; no timestamp-only rejection | Sequence-aware handling; do not advance cursor across missing update | Do not infer order solely from capture timestamp |
| Lost acknowledgement | Retry the same source observation using its immutable source-delivery locator; deduplicate canonical event by verified aggregate-trade identity | Retry the same source observation using its immutable source-delivery locator; deduplicate canonical event by verified exchange namespace + native update range. Epoch is continuity provenance only, never part of retry or canonical identity | Retry the same source observation using its immutable source-delivery locator and proven capture ID; source-kind-specific completeness evidence must remain unchanged |
| Source evidence unavailable | No canonical acceptance | No canonical acceptance | No canonical acceptance |

No source deletion follows acknowledgement. Partial acceptance must retain per-record outcomes and safe resume position. Source-delivery acknowledgement and book-sequence progress are separate as defined in §4.8; acknowledgement/checkpoint atomicity and quarantine progression remain design blockers, not implemented behavior.

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

### SD-06 — Depth diffs (31 cases)

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
26. Missing stream epoch with otherwise present candidate update range is classified as missing continuity provenance; it is not reported as missing native event identity and cannot advance book continuity.
27. Lost acknowledgement replayed from a different stream epoch but same verified native update range and same payload is canonical replay; epoch difference is retained only as provenance.
28. Retry of the same source-delivery locator after restart is idempotent even when the process/session epoch changed; source cursor and book watermark remain independently fenced.
29. A non-identical overlapping range is accepted for book application only when the pinned Binance USD-M protocol and verified T1 behavior prove it is the valid next bridge/update, including the required `pu` predecessor relationship and active snapshot/epoch; assert both observations are retained and the watermark advances only to the verified contiguous final update ID.
30. A non-identical overlapping range with a missing/mismatched `pu`, unproven bridge rule or unavailable protocol evidence is durably quarantined as a sequence gap/conflict; assert source observation retention, book unavailable, source cursor outcome recorded only after durability, and book watermark unchanged.
31. Same canonical update-range identity with changed payload is conflict; for partially overlapping but different ranges with changed payload, do not merge or silently choose one. Retain both observations and apply only if a separately proven exchange rule establishes valid continuity; otherwise quarantine and leave book watermark unchanged.

### SD-07 — Bounded order-book snapshots (46 cases)

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
20. Direct REST source kind requires the exact REST endpoint, request limit, response anchor and raw/immutable response evidence; missing REST-specific evidence quarantines it.
21. Reconstructed-local-book source kind requires upstream snapshot anchor, epoch, last contiguous applied update, healthy continuity state and declared retained-depth policy; any unresolved gap/overflow/conflict rejects the capture.
22. REST-only metadata presented on a reconstructed-local-book capture, or local-book continuity metadata presented as proof of a direct REST response, is a source-kind mismatch and is rejected.
23. Unknown/future source kind is rejected by default and cannot inherit either allowlisted completeness contract.
24. A reconstructed-local-book snapshot whose source history contains a prior unresolved gap cannot be accepted merely because its emitted rows and digest are internally complete.
25. Direct REST response with no producer-issued capture identity (producer namespace or durable sequence missing) is quarantined; do not substitute `lastUpdateId`, timestamp or T0 import sequence.
26. Capture identity reused after process restart because producer sequence was reset is a collision; reject/quarantine and preserve both source evidence records.
27. Retry of the same already-captured REST response under the same capture identity and identical request/anchor/raw-response digest is replay, not a new snapshot acquisition.
28. Two separate REST acquisitions with different capture identities but identical `lastUpdateId`, capture timestamp and payload remain distinct capture observations; they are not collapsed as a retry replay.
29. Two distinct REST response payloads sharing the same `lastUpdateId`/timestamp but carrying different capture identities remain distinct observations; neither overwrites the other and their differing payloads are not hidden by anchor-based deduplication.
30. Same producer namespace/sequence reused with different request parameters, response anchor or raw-response digest is a capture-identity conflict; quarantine without overwrite.
31. Capture identity not verifiably bound to exact REST endpoint, symbol, requested limit/parameters, native response anchor and immutable response digest fails canonical acceptance.
32. T1 reconstructed-book capture identity must bind upstream snapshot anchor, stream epoch, last contiguous applied diff, continuity state, local-book generation, retained-depth policy and serialized payload digest; missing/mismatched evidence or unresolved gap rejects the capture.
33. Direct REST response capture issued by the active registered T1 SD-07 producer in `kenznguyen/binance-futures-collector`, with matching producer registration/source-kind/scope, independently verified producer-origin proof, independently verified namespace uniqueness/single-writer fencing/durable sequence non-reuse proof, and complete request/response evidence, is only eligible for candidate acceptance; T0 preserves the producer-issued capture ID unchanged.
34. T1 reconstructed-local-book capture issued by a producer registration explicitly scoped to `T1_RECONSTRUCTED_LOCAL_BOOK_V1`, with upstream anchor, epoch, continuity, generation and retained-depth evidence, independently verified producer-origin proof, and independently verified namespace uniqueness/single-writer fencing/durable sequence non-reuse proof, is only eligible for candidate acceptance; a REST-response registration cannot stand in for this registration.
35. Unknown or unregistered `capture_producer_id` is quarantined even when `lastUpdateId`, payload digest and group manifest are otherwise valid; classify this as producer registration failure, not missing native anchor.
36. A registered producer ID presented under the wrong source kind, exchange/market/domain or out-of-scope symbol is quarantined; no fallback to another registration or source-kind contract is allowed.
37. Two concurrent T1 processes/clones attempting to emit the same `(capture_producer_id, capture_sequence)` cannot both be accepted; absent verifiable single-writer fencing, preserve both evidence references and quarantine the collision rather than treating it as an ordinary identical replay.
38. A stale T1 producer state restored after restart that reuses a previously issued sequence under the same producer namespace is detected as identity reuse/collision and quarantined; restart must not reset or silently roll back the durable sequence.
39. T0 attempting to mint, substitute or rewrite the T1-issued `capture_producer_id` or `capture_sequence` during intake is rejected; the original producer identity/evidence is preserved and T0's delivery/import locator remains a separate identity domain.
40. The same `(capture_producer_id, capture_sequence)` is submitted with a changed `last_update_id`/upstream anchor; T0 treats it as an identity conflict and quarantines it, not as a distinct capture.
41. The same producer pair is submitted with a changed capture timestamp, requested REST limit or reconstructed retained-depth policy; any changed immutable attribute is a conflict and is quarantined.
42. The same producer pair is submitted with a changed source kind, symbol/market scope, request parameters, producer version or immutable response/payload digest; T0 rejects/quarantines it as identity reuse, even if the revised composite fields would otherwise appear unique.
43. A valid producer attestation whose verifier binds the exact producer pair, source kind/scope, producer and identity-scheme versions and immutable response/payload digest is eligible for further candidate validation only when its signer/trust binding is active and owner-approved; digest equality alone is insufficient.
44. Missing, invalid, expired, revoked, wrong-scope or unverifiable producer attestation, or an attestation whose signed digest differs from the delivered immutable object, is quarantined; no self-asserted producer ID can substitute.
45. An authenticated handoff is eligible only when the authenticated workload principal is bound to the registered T1 producer and the durable integrity-protected handoff receipt binds the exact producer pair, source kind/scope, versions, immutable digest and delivery locator; otherwise quarantine. This case does not select or freeze a transport mechanism.
46. Missing or unverifiable namespace uniqueness, single-writer fencing, durable sequence monotonicity/non-reuse, or stale-restore/clone rollback protection keeps the capture quarantined even when producer registration, origin proof and payload completeness otherwise pass.

### Cross-domain cursor, checkpoint and recovery (10 cases)

1. Durable source intake outcome advances source-delivery cursor only after evidence/outcome commit.
2. Durable GAP_UNRESOLVED quarantine may advance source cursor while book watermark remains unchanged.
3. Source acknowledgement never implies sequence continuity or book watermark advancement.
4. Crash between observation persistence and cursor commit does not skip the source position.
5. Crash between diff application and book watermark commit does not apply the same diff twice.
6. Restart resumes source intake and book application from their separate durable markers.
7. Buffered but unapplied events do not advance book watermark.
8. Conflict/resource rejection leaves book unavailable until reviewed recovery with a new bounded snapshot and verified bridge.
9. Lost acknowledgement retried with the same immutable source-delivery locator returns the prior durable intake outcome; it does not allocate a new capture identity or apply a second book update.
10. The same immutable capture delivered through two separately evidenced source-delivery locators deduplicates by capture identity while retaining both delivery-provenance references; changing only the delivery locator does not create a new capture.

**Proposed matrix total: 101 cases** (SD-05 14, SD-06 31, SD-07 46, cross-domain 10). Designed only; NOT EXECUTED.

## 10. Open design blockers before contract freeze

| ID | Blocker | Why it matters | Evidence/decision required |
|---|---|---|---|
| B-01 | Exact T1 aggTrade source mapping and build behavior | Published CSV schema alone does not prove parser correctness or source payload retention | Read-only inspection of pinned T1 source and exact Binance USD-M aggTrade contract |
| B-02 | AggTrade ID semantics and field bounds | Identity and first/last trade-ID meaning must be exact | Confirm exchange contract and T1 code; freeze integer ranges |
| B-03 | `side` vs `is_buyer_maker` relation | Avoid inconsistent or inverted aggressor semantics | Verify exchange semantics and T1 mapping; owner accepts validation |
| B-04 | Depth stream epoch provenance | Current CSV lacks an immutable capture/session epoch needed for continuity and recovery, but epoch must not be part of canonical event identity | Additive source-contract design; capture epoch lifecycle and cross-restart evidence |
| B-05 | Binance depth snapshot/diff bridge and update-ID uniqueness scope | Both canonical update-range identity and sequence acceptance depend on exact USD-M semantics | Pin official USD-M protocol and T1 implementation; verify uniqueness namespace across reconnects and define initial/subsequent bridge algorithm |
| B-06 | Depth diff source message completeness and receive time | CSV does not prove complete original event bytes or collector receive timestamp | Inspect T1 source capture and decide additive provenance fields |
| B-07 | Snapshot capture identity and producer proof | Current schema has no producer-issued capture identity; timestamp + `lastUpdateId` may collide, and the current source schema does not prove producer origin or unique/fenced sequence allocation | The sole capture identity key is the T1-issued `(capture_producer_id, capture_sequence)` pair. Symbol, market, source kind, update anchor, timestamp, request/depth parameters and immutable payload/object digest are immutable attributes validated against that pair, never additional identity dimensions. Require verifiable T1 producer-origin attestation or trusted authenticated handoff, plus independently verifiable namespace uniqueness, single-writer fencing, durable sequence non-reuse and rollback protection. Missing or unverifiable evidence keeps the capture quarantined; B-07 remains OPEN until proof is independently verified |
| B-08 | Snapshot group completeness | One row per level, no count/checksum/end marker/empty-book marker | Source-generated completion manifest/group framing with expected row count (or equivalent), finalized object digest, explicit complete/empty declarations; EOF/rotation/elapsed time/row count alone prohibited |
| B-09 | Snapshot-to-stream epoch linkage | Snapshot anchor must correspond to the intended diff stream | Define source lifecycle/session relationship and recovery semantics |
| B-10 | File immutability and row locator | CSV append/rotation may expose partial groups or changing bytes | Exact close/manifest rule, immutable object SHA and stable row locator |
| B-11 | Canonical digest/decimal serialization | Cross-language deterministic replay/conflict decisions | Separate versioned byte-encoding specification and review |
| B-12 | Atomic provenance, identity, outcome and checkpoint persistence | No ack before durable evidence; no sequence skips | Logical transaction/recovery design aligned with T0 single-writer/fencing |
| B-13 | T0 API and dataset-version compatibility | Microstructure data is not a Candle and must not silently alter candle API | **PROPOSED BOUNDED EXCLUSION — OWNER DECISION PENDING:** exclude non-candle read API/dataset-version compatibility from this Phase B ingestion-contract freeze; no API route, DTO, T2 consumer compatibility or runtime implication is accepted. Track it as a separate follow-on contract. Until owner accepts this scope exclusion, B-13 remains OPEN. |
| B-14 | Bounded reorder/gap policy numeric limits | Count/age bounds and gap wait determine memory safety and recovery correctness | Measure source behavior; owner-review max buffered events, max residence age, wait policy and resource budget before freeze |
| B-15 | Native `nq` and depth transaction-time `T` fidelity | Current T1 CSV omits aggTrade `nq` and depth `T`; `q` and `nq` differ, while `E` and `T` are separate clocks | Inspect pinned T1 source/raw retention; decide versioned canonical vs raw-only fields; current CSV must explicitly mark both unavailable where absent |
| B-16 | RPI visibility and source-domain scope | Ordinary depth excludes RPI and is not a complete all-liquidity book | **PROPOSED BOUNDED EXCLUSION — OWNER DECISION PENDING:** Phase B covers ordinary non-RPI depth only. No RPI stream, RPI merge, or all-liquidity completeness claim is included. RPI requires a separate future source-domain/sequence/snapshot/merge design. Until owner accepts this exclusion, B-16 remains OPEN. |
| B-17 | AggTrade E/T and CSV source fidelity | E is event time; T is trade time; current CSV timestamp_ms is documented as trade time but exact parser mapping is not verified | **PROPOSED BOUNDED EXCLUSION — OWNER DECISION PENDING:** Phase B may preserve verified trade time `T` only and explicitly exclude native event time `E` from the current CSV-backed canonical contract; `E` remains unavailable and must never be inferred from `timestamp_ms`. This exclusion is conditional on read-only verification of the pinned T1 parser proving `timestamp_ms` is sourced from native `T`, with exact build/source evidence. If parser proof is absent or contradicts the mapping, quarantine and keep B-17 OPEN. Even with parser proof, the owner must explicitly accept the loss/unavailability of `E` before B-17 can close. |
| B-18 | Snapshot bounded-depth source manifest | A fully captured top-N response is not a full exchange book | Manifest binds endpoint/source kind, requested limit, actual bid/ask counts, total rows, capture ID, digest, completion and non-RPI scope; define bounded derived-view semantics |
| B-19 | Independent source cursor and book watermark | Durable quarantine acknowledgement can coexist with unresolved book sequence gap | Freeze separate cursor definitions, atomicity, restart/replay and acknowledgement semantics; align with B-12 |
| B-20 | Parser and capture resource ceilings | Count/age limits alone do not bound memory, parsing CPU or snapshot group accumulation | Measure and owner-review max raw bytes, levels, numeric token size/precision, buffer bytes and snapshot group rows/bytes; add fail-closed tests |

### 10.1 Conditional bounded-exclusion proposals — owner approval required

The following are scope proposals only. They do not change the blocker register or create an implied acceptance:

| Blocker | Proposed freeze treatment | Conditions required before closure | Explicit consequence accepted |
|---|---|---|---|
| B-13 | Exclude non-candle read API/dataset-version compatibility from this Phase B ingestion freeze; defer to a separately versioned read-contract design | Owner explicitly approves the Phase B boundary as canonical ingestion/acceptance design only; follow-on API work is separately tracked; no API/consumer/runtime compatibility is implied | Phase B freeze would not authorize a T0 microstructure read API, T2 access, DTO compatibility or runtime connection |
| B-16 | Accept ordinary Binance USD-M non-RPI depth only; exclude RPI-inclusive depth | Owner explicitly accepts that Phase B data is not all displayed liquidity and RPI needs separate review | No RPI capture/merge, no all-liquidity book claims, and no inferred RPI values |
| B-17 | Accept native aggTrade trade time `T` only for the current CSV-backed path; exclude event time `E` | First obtain exact pinned T1 parser/source evidence that CSV `timestamp_ms` maps to native `T`; then owner explicitly accepts `E` as unavailable/out of scope. Without both, remain OPEN | No event-time analysis or latency/event ordering may use `timestamp_ms` as `E`; no receive-time substitution; future E support requires an additive source-contract revision |

For all three, closure requires an explicit owner decision recorded with the exact Revision 9 commit/blob and scope. Until then, the status remains OPEN. No implementation, API, runtime, T1 source modification or data operation is authorized by these proposals.

## 11. Phase B exit criteria and owner review

- [x] Three Phase B domains scoped: SD-05, SD-06, SD-07.
- [x] Native T1 documented columns mapped to candidate canonical fields.
- [x] Candidate identity and domain-specific sequence/grouping semantics described.
- [x] Timestamp/provenance limitations called out without fabricated receive times.
- [x] Replay/conflict/quarantine/acknowledgement behavior drafted.
- [x] Synthetic test matrix expanded to 101 proposed cases, including E/T separation, unverified q mapping, source-kind-specific REST/local-book completeness, T1 producer ownership/registration, immutable producer-pair attributes, producer-origin attestation/trusted handoff, namespace uniqueness/single-writer fencing/durable non-reuse, fail-closed behavior and three SD-06 overlap adjudication cases; explicitly marked NOT EXECUTED.
- [x] Contract-freeze blockers recorded.
- [ ] B-01 through B-20 resolved or explicitly accepted as bounded exclusions by owner.
- [ ] Canonical DTO/envelope, digest encoding, snapshot capture/group identity and diff stream epoch contract reviewed/frozen.
- [ ] Independent design review completed and findings resolved.

**Next review requested (Revision 9):** conduct a full design review of SD-05, SD-06, SD-07, the common envelope/provenance/identity/digest/checkpoint rules, all 20 blockers and the proposed bounded exclusions. Specifically verify: (1) the Inventory is explicitly non-binding and the Phase B SD-06/SD-07 identity supersession map is internally consistent; (2) Revision 9 metadata and immutable Revision 8 source references are exact; (3) SD-06 overlap cases 29–31 have deterministic expected outcomes without inventing protocol behavior; (4) producer namespace authority, uniqueness scope, single-writer fencing, registration lifecycle, revocation and restore/rollback policy are bounded while proof mechanisms remain explicitly unfrozen; and (5) B-13/B-16/B-17 remain OPEN pending the stated owner decisions/evidence. The 101-case matrix is DESIGN ONLY / NOT EXECUTED. B-01..B-20 remain OPEN; no contract freeze or implementation is authorized.

## 12. Revision 9 review status and immutable history

- Revision 8 source preserved unchanged: commit `9a5c65f3bc00876d98a070eee46072c5d8be368e`, blob `8f40248f2781cdf4111ef022b77843acea8279b2`.
- Revision 9 is a documentation-only candidate. Its exact source commit/blob is recorded in the matching self-review and full-review reports; self-review is not owner approval or independent second-person review.
- Revisions 6, 7 and 8 remain immutable historical artifacts. This document does not edit the Source Domain Inventory, T1 repository, Phase A baseline or any source implementation.
- B-01..B-20 remain OPEN until evidence-backed closure or explicit owner acceptance of a bounded exclusion. The three proposals B-13/B-16/B-17 are not accepted by default.
- Contract Freeze: NOT APPROVED. Implementation: NOT AUTHORIZED.

## 13. Explicit exclusions

This Phase B document authorizes no:
- code, DTO, parser, validator, adapter, fixture, test, dependency, API or workflow changes;
- T0 DDL/schema/database creation, open-for-write, migration, import, promotion, cutover or canonical data mutation;
- T1 source-code change, collector activation, file copy, importer execution or T1→T0 runtime connection;
- network/exchange calls, credentials, archive/data acquisition, data movement or upload;
- source cleanup, retention expiry or deletion after acknowledgement;
- T2 integration, strategy changes, runtime/VPS, process startup, systemd/autostart or deployment;
- order submission, live execution or real orders.

T0 remains the sole canonical owner. T1 implementation remains in its own repository. Raw source evidence must be preserved. Paper-first/no-live-trading guardrails remain unchanged.
