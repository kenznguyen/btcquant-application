# CURRENT STATUS OVERRIDE — 2026-11-23 — Phase B Revision 16 after PR #13 review

- Revision 16 is a documentation-only, immutable successor to Revision 15. R15 remains unchanged.
- Exact reviewed R15 design source: commit `5bbbd6ac253b4f8c8d9aeccb28d77170b1897919`, blob `2b1cb4a8d0a7d40f9ebfb29ccaf9d9d14930cfc0`; exact PR #13 review head `6554529d9d8bd136c85643fdc43a68256b7e1989`.
- PR #13 Codex review: **COMPLETED WITH 3 P2 FINDINGS** (review ID `PRR_kwDOVzv83s8AAAABZnV1sw`; comments `4659555256`, `4659555264`, `4659555270`). Findings: (1) current-status gate incorrectly referenced R12; (2) 101-case matrix did not explicitly assert mismatch of the two source-object SHA aliases and rejection before identity/completion/ACK; (3) filesystem publication could replace an existing immutable evidence object.
- R16 resolutions: (1) all operative fixture gates, including the current-status header, matrix, checklist, §14.3 and Annex A §10, require satisfactory review of exact R16 source SHA/blob; (2) the existing SD-07 digest-mismatch case explicitly tests `source_object.sha256 != raw_object_sha256` and fail-closed ordering without increasing the approved 101 cases; (3) filesystem publication requires atomic no-clobber create-if-absent semantics, verifies an existing target by exact digest, never overwrites, and preserves changed observations under a distinct immutable evidence key before conflict recording.
- R16 design file: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_REVISION_16_2026-11-23.md`. Its exact source commit and document blob are pinned in the companion findings/resolution report, Project Session Handoff, Active Scope Index and review-only PR metadata; the design file does not embed a self-referential hash.
- Owner-approved synthetic scope remains 101 cases: SD-05 14, SD-06 31, SD-07 46, cross-domain 10. Fixtures/tests remain **NOT CREATED / NOT RUN** until satisfactory independent review of exact R16 SHA/blob.
- Owner authorization: autonomously correct review findings in new immutable successor revisions, perform static self-review, request Codex review on each exact final PR head, and repeat this fix/review cycle until the exact current revision passes the review gate. Never modify a published revision. Once the exact design passes review, proceed only with the already-approved isolated 101 synthetic cases; no expansion of scope.
- This authorization does not approve production implementation, DDL/DB mutation, data movement, T0/T1 runtime, T2 integration, VPS/autostart, deployment, exchange connectivity, automatic execution or live trading.
- PR #13 remains historical review-only, OPEN / NOT MERGED / DO NOT MERGE. R16 will be submitted through a new review-only PR.
- Workflow runs/jobs/artifacts: none verified for R16 at document creation. Tests/formal proofs: NOT RUN. Contract Freeze: NOT APPROVED.

---

## Historical review snapshot — Revision 15 (superseded by Revision 16)

- R15 source: commit `5bbbd6ac253b4f8c8d9aeccb28d77170b1897919`, blob `2b1cb4a8d0a7d40f9ebfb29ccaf9d9d14930cfc0`.
- Review-only PR #13 exact reviewed head: `6554529d9d8bd136c85643fdc43a68256b7e1989`; Codex review completed with three P2 findings.
- P2-1: current-status fixture gate referenced R12.
- P2-2: the approved matrix did not explicitly test mismatch of `source_object.sha256` and `raw_object_sha256`.
- P2-3: filesystem atomic rename could replace an existing evidence object.
- Findings report: `docs/reviews/T0_PHASE_B_REVISION_15_CODEX_FINDINGS_2026-11-23.md`.
- PR #13 remains OPEN / NOT MERGED / DO NOT MERGE. R16 documents corrections; no tests or formal proofs were run for R15.


---

## Historical review snapshot — Revision 14 (superseded by Revision 15)

- R14 source: commit `e91706168ce8731711951546deea9399872fa368`, blob `fdfe77d2bd162f2cb9ff9b2e7a6427dd8c3eacaf`.
- Review-only PR #12 exact reviewed head: `8a5a37d9f959b93c9f0cad2cccb3d0561f7b7a01`; Codex review completed with three P2 findings.
- P2-1: matrix and Annex A §10 retained stale R12/R13 review gates.
- P2-2: `SourceDeliveryIntegrityConflictV1` mixed append-only evidence with mutable `disposition` and `resolution_ref` fields.
- P2-3: duplicate source-object digest fields had no equality invariant.
- Review threads remain unresolved on PR #12; R15 documents the corrections. No tests or formal proofs were run for R14.

---

## Historical status snapshot — Revision 13 (superseded by Revision 14)

- Revision 13 is a documentation-only successor to immutable Revision 12 and Revision 11. It incorporates the consolidated Phase B design and Annex A, addresses all four P2 findings from Codex review PR #10, and preserves prior revisions unchanged.
- Revision 11 exact reviewed source commit/blob: `0ac119c7cd31ba63d5aead6796c7b5560abf2a18` / `9d9639b4d26b42a90929f50a32b801e359b23197`.
- PR #9 Codex review: **COMPLETED WITH FINDINGS** on head `8a084c3f02de6d4f462b0f5731ed8f8569fb5fbf`; three P2 findings. Graphify skipped AI review because the PR was documentation-only; its static/advisory checks are not a substitute for the Codex review. No tests or formal proofs were run.
- R13 carries forward the R12 corrections: field-specific T1 mappings and provenance caveats; SD-07 envelope/identity equality; stable source-object/version delivery identity with digest as integrity evidence. It additionally corrects the four PR #10 findings: current-status handoff/index references R13; the SD-05 quantity case asserts inspected-source `q → quantity` mapping while separately retaining deployed-build and decimal-fidelity uncertainty; source cursor advances only over a contiguous per-partition terminal frontier with durable out-of-order completion state; and a same-locator changed-bytes/digest negative case requires durable append-only conflict evidence, preserves the original completion, and forbids a second completion.
- Owner-approved synthetic scope remains 101 cases: SD-05 14, SD-06 31, SD-07 46, cross-domain 10. Fixtures and execution remain gated on satisfactory independent review of exact Revision 14 SHA/blob.
- B-13/B-16 remain CLOSED as bounded owner-accepted exclusions. B-17 remains OPEN pending deployed/imported T1 build provenance. B-01 remains PARTIAL because semantic mapping is verified but exact decimal/raw fidelity and deployed build lineage are not.
- Revision 13 is a consolidated review candidate, NOT a Contract Freeze. PR #11 review completed on exact head `982ea9e250bfca19bdd6ecb973956143dfe27df6`; three P2 findings were recorded and are addressed by Revision 14. PR #10 on R12 completed with four unresolved P2 findings; see `docs/reviews/T0_PHASE_B_REVISION_12_CODEX_FINDINGS_AND_R13_RESOLUTION_2026-11-23.md`. No production implementation, DDL/database mutation, data movement, runtime, T2 integration, VPS/autostart or trading is authorized.


---

## Revision 11 status snapshot — superseded by Revision 12

Revision 11 was the consolidated review candidate submitted to PR #9. Its exact source SHA/blob and review findings are recorded above. This snapshot is retained for history only; Revision 14 is the current design authority.

- Owner decision: `docs/decisions/T0_PHASE_B_BOUNDED_EXCLUSIONS_AND_IDENTITY_SUPERSESSION_OWNER_DECISION_2026-11-22.md`.
- Inventory identity amendment: `docs/design/T0_SOURCE_DOMAIN_INVENTORY_PHASE_B_IDENTITY_AMENDMENT_V2_2026-11-22.md`.
## Revision 10 historical status snapshot (superseded by this Revision 12)

The prior Revision 10 status is retained only as historical context. Current authority is in the Revision 16 header and §14.3. Revision 10 remains immutable. B-13/B-16 are now closed as bounded exclusions; B-17 remains open pending build provenance. The 101-case synthetic test scope is owner-approved, but fixture creation/execution are sequenced after satisfactory independent review of Revision 14.

---

# T0 Phase B — Detailed Schema & Canonical Contract Design (Revision 16 review candidate)

- Date: 2026-11-23 (revision 16)
- Status: **POST-PR #13 FINDINGS CONSOLIDATED CANDIDATE — THREE P2 FINDINGS ADDRESSED IN DOCUMENTATION; NOT CONTRACT-FROZEN**
- Immutable history: Revisions 6–11 remain unchanged. Revision 12 is the documentation-only successor to Revision 11.
- Revision 11 exact reviewed source: commit `0ac119c7cd31ba63d5aead6796c7b5560abf2a18`, blob `9d9639b4d26b42a90929f50a32b801e359b23197`.
- Revision 10 immutable source: commit `b32d9af088099f92b09d113ecfa27056cfd9b83d`, blob `a8934cb862c330f1d1fa72aa1f3fdb2b22f9ac96`.
- Codex review PR #9: completed with three P2 findings; correction record: `docs/reviews/T0_PHASE_B_REVISION_11_CODEX_REVIEW_FINDINGS_2026-11-22.md`.
- DTO/digest/checkpoint/atomic persistence proposal incorporated as Annex A from blob `594066d98201a8cf0940b62fc36d9358033f06e0`.
- Scope: SD-05 aggregate trades; SD-06 order-book depth diffs; SD-07 order-book snapshots.
- Authorization: owner-approved Phase A review and Phase B documentation-only authorization, decision commit `f2f5741cad47b86c70dae23dbaa9b497258cc80a`.
- Reference only (non-binding proposal): `docs/design/T0_SOURCE_DOMAIN_INVENTORY_AND_CANONICAL_INGESTION_CONTRACT_V1_2026-11-22.md`. For Phase B SD-06/SD-07 identity, the owner-approved supersession and Inventory amendment recorded with Revision 10 apply to this bounded scope only. This does not freeze the broader Inventory or authorize Contract Freeze.
- Phase A baseline: `docs/design/T0_PHASE_A_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`.
- T1 source schema: `kenznguyen/binance-futures-collector/docs/SCHEMA.md`, blob SHA `895f87a8281a3f9b6d37d96b5f68568e4285bee6`.
- Implementation: **NOT AUTHORIZED / NOT STARTED**.
- Synthetic matrix: **101 CASES OWNER-APPROVED; FIXTURES NOT CREATED / EXECUTION NOT RUN; SEQUENCED AFTER SATISFACTORY INDEPENDENT REVIEW OF EXACT REVISION 16 SHA/BLOB**.
- Tests/workflows/artifacts: **NOT RUN / NONE**.

## 1. Purpose, authority and invariants

This document is an immutable documentation-only successor to Revision 15. It preserves the prior Phase B domain design and Annex A proposal while correcting the three findings from review of exact R15 source. It remains a review candidate, not a frozen contract. Annex A is included as a proposed normative design input for review; inclusion does not itself freeze wire DTOs, storage schema, digest encoding, checkpoint protocol, transaction semantics or source contract.

### 1.1 Document authority and identity supersession map

The Source Domain Inventory v1 remains a broad, non-binding inventory/reference document. The owner-approved identity supersession for this bounded Phase B scope is recorded in the Revision 10 decision and Inventory amendment. Its conflicting SD-06/SD-07 identity examples are superseded for Phase B only. The Phase B identity rules below remain subject to technical proof and independent review:

| Domain | Candidate canonical/capture identity | Fields explicitly not in that identity | Required interpretation |
|---|---|---|---|
| SD-06 depth diff | `(exchange, market_type, symbol, first_update_id, final_update_id)` subject to proof of uniqueness scope | `stream_epoch`, timestamps, source-delivery locator, collector process/connection IDs | `stream_epoch` is continuity/capture provenance only. It cannot be appended to the canonical key to conceal an unproven exchange identity namespace. |
| SD-07 snapshot capture | `(capture_producer_id, capture_sequence)` only | `exchange`, `market_type`, `symbol`, `source_kind`, `last_update_id`, snapshot event type, timestamp, request/depth parameters, producer version, payload/object digest and delivery locator | All excluded fields are immutable attributes bound to the pair. A changed attribute under the same pair is identity reuse/conflict, not a distinct capture. `(side, price)` identifies a level within a completed capture, not a capture identity. |

This owner-approved identity mapping is the governing scope decision for Phase B SD-06/SD-07 only; the supersession was recorded with Revision 10. The Inventory itself is not silently edited; its amendment is separately recorded. Technical uniqueness, producer-origin, fencing, non-reuse and rollback proofs remain open and must fail closed until independently evidenced.

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

Binance USD-M aggTrade defines `E` as event time and `T` as trade time. These clocks are distinct. The read-only source audit of T1 commit `c91a8c22d3b6236c98ab9a4d4d69b25d47f7f738` verifies that the inspected parser maps native `T` to `trade_time` and `to_csv()` writes `trade_time` to `timestamp_ms`; it does not map `E` to that column. This is source-level evidence only: deployed/imported binary provenance remains NOT VERIFIED, and CSV numeric formatting is lossy for price/quantity.

| Binance native field | Meaning | Present in inspected T1 source/CSV? | Phase B treatment |
|---|---|---|---|
| `e` | event type | Parsed in WebSocket model; not retained in CSV | unavailable in CSV; preserve only if raw native message exists |
| `E` | event time | Parsed in model; not retained as a distinct CSV field | `UNAVAILABLE_IN_T1_CSV_V1`; never map from `timestamp_ms` |
| `s` | symbol | Parsed and lowercased into CSV | source-level semantic mapping verified; normalization contract remains subject to freeze |
| `a` | aggregate trade ID | Parsed as `aggregate_trade_id`, written as `trade_id` | source-level mapping verified; deployed build provenance remains open |
| `p` | price | Parsed as `price`, written after numeric formatting | semantic field mapping verified in inspected source; exact decimal lexeme fidelity is not preserved |
| `q` | aggregate quantity including RPI-involved trades | Parsed as `quantity`, written after numeric formatting | source-level semantic mapping verified; exact decimal lexeme fidelity is not preserved; never confuse with `nq` |
| `nq` | normal quantity excluding trades involving RPI orders | No model/CSV field | `UNAVAILABLE_IN_T1_CSV_V1`; preserve only if raw native message exists; never derive from `q` |
| `f` / `l` | first/last underlying trade IDs | Parsed as `first_trade_id`/`last_trade_id`, written to legacy `first_update_id`/`last_update_id` columns | source-level mapping verified; these are trade IDs, not book update IDs |
| `T` | trade time | Parsed as `trade_time`; `to_csv()` writes it to `timestamp_ms` | source-level mapping verified: `T → trade_time → timestamp_ms`; deployed/imported build provenance remains open |
| `m` | buyer-is-maker flag | Parsed as `is_buyer_maker`; CSV also writes derived aggressor `side` | source-level mapping verified; `true → SELL`, `false → BUY` in inspected source |
| `M` | ignore/auxiliary flag | No model/CSV field | unavailable in CSV unless raw source retained |

**Mapping status is field-specific, not uniform.** The read-only audit of T1 commit `c91a8c22d3b6236c98ab9a4d4d69b25d47f7f738` and source blobs proves the inspected source-level mappings `a → aggregate_trade_id → trade_id`, `p → price`, `q → quantity`, `f/l → first/last trade IDs`, `T → trade_time → timestamp_ms`, and `m → is_buyer_maker`. The source maps `m=true` to aggressor SELL and `m=false` to BUY. This does not prove which binary produced any historical/imported CSV; build provenance remains NOT VERIFIED. Price and quantity pass through f64 parsing and fixed 12-decimal formatting, so exact original decimal lexemes/arbitrary precision are not preserved. `nq`, `M` and a distinct `E` column are unavailable in the current CSV contract.

If raw native aggTrade messages are retained, preserve `E`, `T`, `q`, and `nq` as separate source fields without normalization that loses original bytes. If only the current CSV is available, `E` and `nq` are unavailable; `timestamp_ms` is source-mapped to `T` at the inspected source SHA; `quantity` is source-mapped to `q` but has undergone f64/12-decimal formatting. Do not claim the inspected source proves deployed/imported build lineage.

### 3.2 Native-to-candidate mapping

| Source field | Documented meaning | Candidate canonical field | Verification status |
|---|---|---|---|
| `exchange` | `binance` | `exchange` | schema-documented; exact source registration pending |
| `market` | `futures` | `market_type` | candidate; exact USD-M/perpetual scope pending |
| `symbol` | lowercase symbol | `symbol` | schema-documented; normalization contract unfrozen |
| `timestamp_ms` | trade time | `trade_time_ms` / native `T` | inspected source maps `T → trade_time → timestamp_ms`; deployed/imported build provenance NOT VERIFIED |
| `trade_id` | aggregate trade ID | `aggregate_trade_id` | inspected source mapping PASS; build provenance NOT VERIFIED |
| `side` | buy/sell aggressor side | `aggressor_side` | inspected source derives from `m`: true→SELL, false→BUY; independent cross-field validation remains required |
| `price` | fill price | `price` | source-level field mapping PASS; f64/12-decimal transform means exact source decimal fidelity NOT PRESERVED |
| `quantity` | CSV quantity/size | native `q` / `quantity_all` | source-level mapping PASS; f64/12-decimal transform means exact source decimal fidelity NOT PRESERVED; `nq` is absent |
| `is_buyer_maker` | buyer maker indicator | `is_buyer_maker` | source-level mapping PASS; strict boolean conversion/cross-field validation still required |
| `first_update_id` | aggTrade `f` | `first_trade_id` | source-level mapping PASS; legacy CSV column name is misleading but not a book update ID |
| `last_update_id` | aggTrade `l` | `last_trade_id` | source-level mapping PASS; legacy CSV column name is misleading but not a book update ID |

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
- The inspected T1 source maps native `T` to `timestamp_ms` at source level; `E` is not represented as a separate CSV field. Deployed/imported build provenance remains NOT VERIFIED.
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
- Lost-acknowledgement retry reuses the **same immutable source-delivery locator** (for example, stable producer object ID/version plus stable row/group locator; content digest is checked as an immutable attribute). Intake deduplicates that delivery position and returns its previously committed outcome; it must not create a new capture or apply a second book update. Canonical exchange-event deduplication remains a separate operation using the verified native exchange namespace/update range. Snapshot capture deduplication uses the producer-issued capture identity and immutable capture evidence defined in §5.2–§5.3. A stream/process epoch is continuity provenance only, not a retry key.

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

- **Source-delivery/import cursor:** is maintained independently per stable source partition. It identifies the highest contiguous producer/manifest-ordered sequence for which every preceding delivery has a durable terminal intake outcome (`ACCEPTED`, `DUPLICATE_REPLAY`, `CONFLICT`, `QUARANTINED`, or durable gap/resource outcome). Each sequence maps to an immutable source-delivery locator; the locator itself is opaque and MUST NOT be used as an ordering key. Out-of-order terminal outcomes are retained in a durable per-sequence completion ledger and do not move the contiguous frontier past an unfinished earlier sequence. The cursor may advance after durable quarantine because intake is complete for that sequence. It is not the exchange-native event identity, snapshot capture identity or a per-attempt T0 import ID. A source without a stable ordered partition sequence or immutable manifest ordinal must use a durable per-locator completion ledger plus safe rescan/enumeration; it MUST NOT advance a last-seen-locator cursor or claim skip-free resume.
- **Book-sequence watermark:** identifies the highest contiguous update sequence actually applied to the derived book from its active snapshot anchor. It advances only after the corresponding canonical diff and derived application state are durable, and never across a missing sequence, conflict, quarantine, resource rejection or unapplied buffered event.

A source cursor advancing past a durably quarantined gap means only that the source observation has been safely ingested and its outcome recorded. It does **not** mean the book is continuous, does not acknowledge missing exchange updates, and must not move the book-sequence watermark.

Restart/replay rules:
1. Resume source intake from each partition's highest contiguous terminal sequence, consulting the durable out-of-order completion ledger and immutable source manifest. Never skip a missing lower sequence because a later locator completed. If acknowledgement was lost, retry the **same immutable source-delivery locator**; delivery-locator/outcome dedupe must return the prior durable result without duplicating raw evidence or canonical effects. Resolve exchange-event deduplication by verified native identity and snapshot-capture deduplication by producer-issued capture identity independently; never substitute one identity domain for another.
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
3. **T0 source-delivery/import locator:** identifies where the immutable capture was delivered from, independently of capture identity. Candidate locator: stable `(source_producer_id, source_object_id, source_object_version)` plus a stable capture-group byte range/ordinal (or a verifiable immutable storage-version identity). Raw object SHA-256 is an integrity attribute, not part of locator identity; a mutable path, filename, file offset without stable object identity, or per-attempt import sequence alone is insufficient. T0 must preserve the capture ID and evidence when importing; it must not relabel a T0-generated import ID as the producer's capture ID. A retry reuses the same locator.

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
2. Preserve the inspected source mapping `T → trade_time → timestamp_ms`; assert `E` remains unavailable unless independently captured. This synthetic case does not certify deployed/imported binary provenance.
3. Distinct `E`/`T` values catch any reversal or timestamp substitution.
4. Assert the inspected T1 source mapping `q → quantity`; separately assert that `nq` is unavailable and that deployed/imported historical build provenance plus exact decimal/raw-byte fidelity remain unverified.
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
10. Partial write, restart, missing rows, count mismatch or digest mismatch quarantines the entire capture. Explicitly test `source_object.sha256 != raw_object_sha256` for the same claimed immutable source object: preserve the received observation as evidence, reject/quarantine before native identity resolution, create no `SourceDeliveryCompletionV1`, do not advance source cursor/book watermark, and do not ACK; assert neither digest alias silently overrides the other.
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

1. Durable source intake outcome advances the per-partition source cursor only after evidence/outcome commit.
2. Durable GAP_UNRESOLVED quarantine may advance the contiguous source frontier while book watermark remains unchanged.
3. Source acknowledgement never implies sequence continuity or book watermark advancement.
4. Out-of-order completion: partition sequence 102 completes before 101; the frontier remains at 100, the completion ledger durably records 102, and restart cannot skip 101. Once 101 reaches a terminal durable outcome, the frontier advances contiguously through 102.
5. Crash between diff application and book watermark commit does not apply the same diff twice.
6. Restart resumes source intake from the contiguous per-partition frontier plus durable out-of-order completion state, and book application from its separate marker.
7. Buffered but unapplied events do not advance book watermark.
8. Conflict/resource rejection leaves book unavailable until reviewed recovery with a new bounded snapshot and verified bridge.
9. Lost acknowledgement retried with the same immutable source-delivery locator returns the prior durable intake outcome when bytes/digest are identical. Changed bytes/digest at that same locator are an integrity conflict, not a new delivery: preserve the conflicting bytes under a distinct immutable evidence key using atomic no-clobber publication, append a `SourceDeliveryIntegrityConflictV1` record referencing both the prior completion and new evidence, leave the original completion unchanged, create no second completion, do not allocate a new capture identity, and do not apply a second book update or advance a checkpoint. Assert an existing evidence object is never replaced, including under a concurrent publish race.
10. The same immutable capture delivered through two separately evidenced source-delivery locators deduplicates by capture identity while retaining both delivery-provenance references; changing only the delivery locator does not create a new capture.

**Approved matrix total: 101 synthetic cases** (SD-05 14, SD-06 31, SD-07 46, cross-domain 10). Owner approval is recorded. Fixtures and execution are sequenced after satisfactory independent review of the exact Revision 16 SHA/blob; currently NOT CREATED / NOT EXECUTED.

## 10. Open design blockers before contract freeze

| ID | Blocker | Why it matters | Evidence/decision required |
|---|---|---|---|
| B-01 | Exact T1 aggTrade source mapping and build behavior | Published CSV schema alone does not prove parser correctness or source payload retention | Source mapping PASS at inspected source SHA; deployed/imported build provenance and exact decimal/raw fidelity remain open |
| B-02 | AggTrade ID semantics and field bounds | Identity and first/last trade-ID meaning must be exact | Confirm exchange contract and T1 code; freeze integer ranges |
| B-03 | `side` vs `is_buyer_maker` relation | Avoid inconsistent or inverted aggressor semantics | Source mapping identified; cross-field validation tests and pinned protocol evidence remain required |
| B-04 | Depth stream epoch provenance | Current CSV lacks an immutable capture/session epoch needed for continuity and recovery, but epoch must not be part of canonical event identity | Additive source-contract design; capture epoch lifecycle and cross-restart evidence |
| B-05 | Binance depth snapshot/diff bridge and update-ID uniqueness scope | Both canonical update-range identity and sequence acceptance depend on exact USD-M semantics | Pin official USD-M protocol and T1 implementation; verify uniqueness namespace across reconnects and define initial/subsequent bridge algorithm |
| B-06 | Depth diff source message completeness and receive time | CSV does not prove complete original event bytes or collector receive timestamp | Inspect T1 source capture and decide additive provenance fields |
| B-07 | Snapshot capture identity and producer proof | Current schema has no producer-issued capture identity; timestamp + `lastUpdateId` may collide, and the current source schema does not prove producer origin or unique/fenced sequence allocation | The sole capture identity key is the T1-issued `(capture_producer_id, capture_sequence)` pair. Symbol, market, source kind, update anchor, timestamp, request/depth parameters and immutable payload/object digest are immutable attributes validated against that pair, never additional identity dimensions. Require verifiable T1 producer-origin attestation or trusted authenticated handoff, plus independently verifiable namespace uniqueness, single-writer fencing, durable sequence non-reuse and rollback protection. Missing or unverifiable evidence keeps the capture quarantined; B-07 remains OPEN until proof is independently verified |
| B-08 | Snapshot group completeness | One row per level, no count/checksum/end marker/empty-book marker | Source-generated completion manifest/group framing with expected row count (or equivalent), finalized object digest, explicit complete/empty declarations; EOF/rotation/elapsed time/row count alone prohibited |
| B-09 | Snapshot-to-stream epoch linkage | Snapshot anchor must correspond to the intended diff stream | Define source lifecycle/session relationship and recovery semantics |
| B-10 | File immutability and row locator | CSV append/rotation may expose partial groups or changing bytes | Exact close/manifest rule, immutable object SHA and stable row locator |
| B-11 | Canonical digest/decimal serialization | Cross-language deterministic replay/conflict decisions | Separate versioned byte-encoding specification and review |
| B-12 | Atomic provenance, identity, outcome and checkpoint persistence | No ack before durable evidence; no sequence skips | Logical transaction/recovery design aligned with T0 single-writer/fencing |
| B-13 | T0 API and dataset-version compatibility | Microstructure data is not a Candle and must not silently alter candle API | **CLOSED — OWNER-ACCEPTED BOUNDED EXCLUSION:** exclude non-candle read API/dataset-version compatibility from this Phase B ingestion design; track a separate follow-on read-contract. No API route, DTO compatibility, T2 consumer or runtime implication is accepted. |
| B-14 | Bounded reorder/gap policy numeric limits | Count/age bounds and gap wait determine memory safety and recovery correctness | Measure source behavior; owner-review max buffered events, max residence age, wait policy and resource budget before freeze |
| B-15 | Native `nq` and depth transaction-time `T` fidelity | Current T1 CSV omits aggTrade `nq` and depth `T`; `q` and `nq` differ, while `E` and `T` are separate clocks | Inspect pinned T1 source/raw retention; decide versioned canonical vs raw-only fields; current CSV must explicitly mark both unavailable where absent |
| B-16 | RPI visibility and source-domain scope | Ordinary depth excludes RPI and is not a complete all-liquidity book | **CLOSED — OWNER-ACCEPTED BOUNDED EXCLUSION:** Phase B covers ordinary non-RPI depth only. No RPI stream, RPI merge, or all-liquidity completeness claim is included. RPI requires a separate future source-domain/sequence/snapshot/merge design. |
| B-17 | AggTrade E/T and CSV source fidelity | E is event time; T is trade time; inspected source maps T to trade_time to timestamp_ms, but deployed/imported build provenance is not verified | **OPEN — CONDITIONAL SCOPE ACCEPTED; BUILD PROVENANCE REQUIRED:** preserve verified trade time `T` only and exclude native event time `E` from the current CSV-backed contract; `E` remains unavailable and must never be inferred from `timestamp_ms`. Source mapping passes at inspected source SHA, but the exact deployed/imported producer binary/build must be tied to that source or the import lineage constrained to a verifiable pinned build. |
| B-18 | Snapshot bounded-depth source manifest | A fully captured top-N response is not a full exchange book | Manifest binds endpoint/source kind, requested limit, actual bid/ask counts, total rows, capture ID, digest, completion and non-RPI scope; define bounded derived-view semantics |
| B-19 | Independent source cursor and book watermark | Durable quarantine acknowledgement can coexist with unresolved book sequence gap | Freeze separate cursor definitions, atomicity, restart/replay and acknowledgement semantics; align with B-12 |
| B-20 | Parser and capture resource ceilings | Count/age limits alone do not bound memory, parsing CPU or snapshot group accumulation | Measure and owner-review max raw bytes, levels, numeric token size/precision, buffer bytes and snapshot group rows/bytes; add fail-closed tests |

### 10.1 Owner-accepted bounded exclusions and remaining conditions

| Blocker | Owner decision | Bounded consequence |
|---|---|---|
| B-13 | **CLOSED — OWNER-ACCEPTED BOUNDED EXCLUSION** | Non-candle read API/dataset-version compatibility is outside this Phase B ingestion design and requires a separate read-contract. No API route, T2 compatibility or runtime connection is implied. |
| B-16 | **CLOSED — OWNER-ACCEPTED BOUNDED EXCLUSION** | Ordinary Binance USD-M non-RPI depth only. No RPI capture/merge and no all-displayed-liquidity claim. |
| B-17 | **OPEN** | T-only/E-excluded scope accepted conditionally. Source audit proves the inspected source mapping `T → trade_time → timestamp_ms`; deployed/imported binary/build provenance remains NOT VERIFIED. No event-time analysis may use `timestamp_ms` as E, and no receive-time substitution is permitted. |

B-13/B-16 closure is scope-only, not implementation or technical verification. B-17 remains open until the exact producer binary/build is tied to the inspected source or the import lineage is constrained to a verifiable pinned build. No other blocker is waived.

## 11. Phase B exit criteria and owner review

- [x] Three Phase B domains scoped: SD-05, SD-06, SD-07.
- [x] Native T1 documented columns mapped to candidate canonical fields.
- [x] Candidate identity and domain-specific sequence/grouping semantics described.
- [x] Timestamp/provenance limitations called out without fabricated receive times.
- [x] Replay/conflict/quarantine/acknowledgement behavior drafted.
- [x] 101-case synthetic matrix defined and owner-approved (14/31/46/10); SD-07 case 10 explicitly tests source-object SHA-alias mismatch and fail-before-identity/completion/ACK; fixture creation and execution remain pending satisfactory independent review of exact Revision 16 SHA/blob.
- [x] Contract-freeze blockers recorded.
- [ ] B-01 through B-20 resolved or explicitly accepted as bounded exclusions by owner.
- [ ] Canonical DTO/envelope, digest encoding, snapshot capture/group identity and diff stream epoch contract reviewed/frozen.
- [ ] Independent design review completed and findings resolved.

**Next review requested (Revision 16):** independent second-person review of the exact Revision 16 source SHA/blob, including all three PR #13 P2 resolutions, the complete consolidated Phase B/Annex A design and all inherited constraints. The 101 cases are owner-approved but not yet created or executed; test work is sequenced only after satisfactory review of this exact R16 document. Contract Freeze remains NOT APPROVED.

## 12. Revision 9 historical review status and immutable history

- Revision 8 source preserved unchanged: commit `9a5c65f3bc00876d98a070eee46072c5d8be368e`, blob `8f40248f2781cdf4111ef022b77843acea8279b2`.
- Revision 9 remains immutable; exact commit/blob and its review history are recorded in the project handoff and Revision 9 review reports. Its historical owner-pending language is superseded only by the explicit Revision 10 owner decision and the consolidated Revision 16 current-status sections.
- Revision 10 remains immutable at commit `b32d9af088099f92b09d113ecfa27056cfd9b83d` / blob `a8934cb862c330f1d1fa72aa1f3fdb2b22f9ac96`.
- Revisions 6–10 remain immutable historical artifacts. This document does not edit the Source Domain Inventory, T1 repository, Phase A baseline or any source implementation.
- Current blocker status is authoritative in §14 and Annex A §9. B-13/B-16 are closed as bounded exclusions; B-17 and all remaining technical blockers remain open/partial as stated.
- Contract Freeze: NOT APPROVED. Production implementation/runtime: NOT AUTHORIZED. The bounded 101-case synthetic test scope is separately owner-approved, with execution sequenced after satisfactory independent review of exact Revision 16 SHA/blob.

## 13. Explicit exclusions

This Phase B document authorizes no production implementation or runtime changes. The sole bounded test exception is the owner-approved isolated synthetic 101-case scope, sequenced after satisfactory independent review of exact Revision 16 SHA/blob. It authorizes no:
- production code, DTO, parser, validator, adapter, dependency, API or workflow changes; test-only fixtures/harness are limited to the approved matrix and remain isolated;
- T0 DDL/schema/database creation, open-for-write, migration, import, promotion, cutover or canonical data mutation;
- T1 source-code change, collector activation, file copy, importer execution or T1→T0 runtime connection;
- network/exchange calls, credentials, archive/data acquisition, data movement or upload;
- source cleanup, retention expiry or deletion after acknowledgement;
- T2 integration, strategy changes, runtime/VPS, process startup, systemd/autostart or deployment;
- order submission, live execution or real orders.

T0 remains the sole canonical owner. T1 implementation remains in its own repository. Raw source evidence must be preserved. Paper-first/no-live-trading guardrails remain unchanged.


---

## 14. Revision 16 status and current blocker register

This section is the authoritative current status for Revision 16. It carries forward owner decisions, the T1 source audit and Annex A proposal, and records the PR #13 review resolutions. Revisions 9–15 remain immutable historical documents.

### 14.1 Accepted Inventory supersession

For Phase B only:
- SD-06 identity: `(exchange, market_type, symbol, first_update_id, final_update_id)`, conditional on proven exchange namespace uniqueness. `stream_epoch` is continuity/capture provenance only, not identity.
- SD-07 capture identity: exactly `(capture_producer_id, capture_sequence)`. All other capture fields are immutable attributes; pair reuse with changed attributes is conflict/quarantine.
- The amendment is recorded in `docs/design/T0_SOURCE_DOMAIN_INVENTORY_PHASE_B_IDENTITY_AMENDMENT_V2_2026-11-22.md`. All other Inventory v1 proposals remain non-frozen.

### 14.2 Current blocker register — authoritative Revision 16 status

| Blocker | Revision 16 status | Meaning |
|---|---|---|
| B-01 | **PARTIAL** | Inspected T1 source maps native T to trade_time to timestamp_ms; deployed/imported binary/build provenance and exact decimal/raw fidelity remain unverified |
| B-02 | OPEN | Aggregate trade ID semantics and integer bounds require final protocol/source proof |
| B-03 | **PARTIAL** | Source-level buyer-maker/aggressor mapping is identified; independent cross-field validation evidence remains required |
| B-04..B-10 | OPEN | Epoch provenance, depth bridge/namespace, message completeness, producer proof, manifest completeness and immutable locator remain unresolved |
| B-11..B-12 | DESIGN SPECIFIED — NOT VERIFIED | Annex A specifies digest and atomic persistence candidates; test vectors, store durability and crash/recovery proof remain outstanding |
| B-13 | **CLOSED — OWNER-ACCEPTED BOUNDED EXCLUSION** | Non-candle read API and dataset-version compatibility excluded from Phase B; separate read-contract required |
| B-14..B-15 | OPEN | Numeric reorder/resource ceilings; native nq and depth T fidelity remain unresolved (T1 source omissions/drops recorded) |
| B-16 | **CLOSED — OWNER-ACCEPTED BOUNDED EXCLUSION** | Ordinary non-RPI depth only; no RPI capture/merge or all-liquidity claim |
| B-17 | **OPEN — SOURCE MAPPING PASS; BUILD PROVENANCE NOT VERIFIED** | T-only/E-excluded scope accepted conditionally; inspected source mapping passes, but deployed/imported build provenance is missing |
| B-18 | OPEN | Snapshot bounded-depth manifest and source proof remain unresolved |
| B-19 | DESIGN SPECIFIED — NOT VERIFIED | Separate source cursor/book watermark and atomic checkpoint proposal in Annex A; persistence/restart/replay proof outstanding |
| B-20 | OPEN | Parser/resource ceilings and fail-closed test evidence remain unresolved |

B-13 and B-16 are closed as scope decisions only; excluded capabilities are not implemented or technically verified. B-11/B-12/B-19 are design-specified only and must not be marked technically closed. B-17 remains open pending build provenance. No other blocker is waived.

### 14.2.1 PR #13 findings resolved in Revision 16

1. All operative 101-case gates now reference satisfactory independent review of exact Revision 16 SHA/blob, including the consolidated matrix, this §14.3 and Annex A §10. R12–R15 references in historical snapshots are historical only.
2. `SourceDeliveryIntegrityConflictV1` is an immutable append-only evidence fact. Resolution is represented only by a separate append-only `SourceDeliveryIntegrityConflictResolutionV1`; status is derived and never written back to the conflict row.
3. `source_object.sha256` and `raw_object_sha256` have identical semantics and MUST match the SHA-256 of the same exact immutable source-object bytes. Mismatch fails closed before canonical acceptance or acknowledgement.

### 14.3 Contract Freeze readiness

- Revision 9 full design review: PASS WITH CONDITIONS; it is historical and not a substitute for independent review of Revision 16.
- Revision 10 exact-SHA review: PASS WITH CONDITIONS for continued documentation; NOT READY FOR CONTRACT FREEZE.
- 101 synthetic cases: OWNER-APPROVED; fixtures/tests NOT CREATED and execution NOT RUN; sequence after satisfactory independent review of exact Revision 16 SHA/blob.
- Exact T1 source mapping: PASS at inspected source level; deployed/imported binary/build provenance NOT VERIFIED.
- Producer origin attestation, namespace allocator, single-writer fencing, durable non-reuse and restore/rollback proof: NOT VERIFIED.
- Binance depth overlap/bridge protocol evidence: NOT VERIFIED.
- Atomic provenance/identity/outcome/checkpoint persistence and restart/replay proof: DESIGN ONLY; NOT VERIFIED.
- DTO/envelope/digest/checkpoint annex: included for review; NOT FROZEN.
- GitHub Actions workflow runs/jobs/artifacts for Revision 16: NONE verified; no workflow was run as part of this documentation-only correction.
- Independent second-person review of exact Revision 16 SHA/blob: REQUESTED via a new review-only PR; verdict PENDING.

**Disposition: NOT READY FOR CONTRACT FREEZE.** Revision 16 is a consolidated review candidate only. Owner-approved test scope does not waive technical blockers or authorize production implementation, DDL, database, API, data movement, T1/T0 runtime, T2 integration, deployment or trading.


---

# Annex A — Canonical DTO, Digest, Checkpoint & Atomic Persistence Design v1

> Source: `docs/design/T0_PHASE_B_CANONICAL_DTO_DIGEST_CHECKPOINT_ATOMIC_PERSISTENCE_DESIGN_V1_2026-11-22.md`, original blob `594066d98201a8cf0940b62fc36d9358033f06e0`.
>
> This annex incorporates the complete proposal into the Revision 16 review surface. It is a **PROPOSED DESIGN INPUT — NOT CONTRACT-FROZEN**. The independent reviewer must review it together with the inherited Phase B design. No production implementation or database operation is authorized.

## Annex A source proposal — complete text

- Date: 2026-11-22
- Design baseline reviewed: Revision 10 commit `b32d9af088099f92b09d113ecfa27056cfd9b83d`, blob `a8934cb862c330f1d1fa72aa1f3fdb2b22f9ac96`.
- T1 source audit: `docs/evidence/T1_AGGTRADE_TIMESTAMP_SOURCE_MAPPING_AUDIT_2026-11-22.md`.
- Status: **PROPOSED TECHNICAL CONTRACT — NOT FROZEN; DOCUMENTATION ONLY**.
- This design does not authorize DTO code, validators, DDL, database writes, tests, fixtures, data movement, runtime or deployment.

## 1. Contract boundaries

- T0 owns canonical acceptance, identity adjudication, durable evidence, outcomes, checkpoints and derived book state.
- T1 owns acquisition, native capture provenance and SD-07 capture identity issuance.
- The application repository may own consumer contracts/DTOs/adapters only after separate authorization; it must not duplicate the T1 collector.
- At-least-once delivery is assumed. Exactly-once effects are achieved by durable idempotency and atomic state transitions, not by assuming exactly-once transport.
- Raw source evidence is immutable. No delete-on-ack, destructive normalization or silent overwrite.
- A source-delivery locator, exchange-event identity, SD-07 capture identity, stream epoch, source cursor and book watermark are different concepts and must never be substituted for one another.

## 2. Common DTO envelope (logical schema)

The following is a language-neutral logical contract, not an implementation-ready generated type. All fields are required unless explicitly nullable. For SD-07, the shared envelope capture producer/sequence fields MUST be non-null and equal SnapshotCaptureV1.identity as specified in §3.3.

```text
CanonicalSourceEnvelopeV1 {
  contract_version: "T0_CANONICAL_SOURCE_V1"
  domain: "SD05_AGG_TRADE" | "SD06_DEPTH_DIFF" | "SD07_DEPTH_SNAPSHOT"
  exchange: "binance"
  market_type: "USD_M_PERPETUAL"
  symbol: normalized lowercase exchange symbol
  source_kind: explicit allowlisted source-kind enum
  source_schema_version: immutable source schema/parser contract identifier
  source_producer: {
    repository: string
    source_commit: 40-hex SHA
    source_blob_set: map<path, 40-hex blob SHA>
    build_id: string | null
    binary_sha256: 64-hex | null
  }
  source_object: {
    sha256: 64-hex  # SHA-256 of the exact immutable source-object bytes
    media_type: string
    immutable_locator: string
    record_locator: {
      kind: "BYTE_RANGE" | "ROW_INDEX" | "GROUP_ID"
      start: uint64 | null
      end_exclusive: uint64 | null
      row_index: uint64 | null
      group_id: string | null
    }
  }
  clocks: {
    exchange_event_time_ms: int64 | null
    exchange_transaction_time_ms: int64 | null
    exchange_trade_time_ms: int64 | null
    producer_receive_time_ms: int64 | null
    t0_received_at_ms: int64
    t0_committed_at_ms: int64 | null
  }
  provenance: {
    stream_epoch: string | null
    capture_producer_id: string | null
    capture_sequence: uint64 | null
    producer_registration_ref: string | null
    producer_attestation_ref: string | null
  }
  raw_object_sha256: 64-hex  # exact alias of source_object.sha256; same source object and same bytes
  canonical_payload_sha256: 64-hex
}
```

Rules:
- Unknown clocks remain null with an explicit unavailable reason in the validation/outcome record; never copy one clock into another.
- T1 CSV imports without a verifiable build ID retain `build_id=null` and are not upgraded to verified-build provenance by inference.
- `source_object.sha256` and envelope-level `raw_object_sha256` identify the same immutable source object and MUST both equal the lowercase hexadecimal SHA-256 of the exact bytes of that object. They are intentionally duplicated compatibility fields, not independent digests. Intake validation MUST compare them and reject/quarantine any mismatch before identity resolution, canonical acceptance, completion or acknowledgement; no field may silently override the other.
- For a legacy CSV source object, both fields are the SHA-256 of the exact immutable CSV object bytes, not a claimed native WebSocket-message digest. An optional `raw_record_sha256` remains a distinct digest of an exact row byte range and MUST NOT be substituted for either object digest.
- A row locator must resolve to exactly one byte range or one stable row/group locator. File path alone is insufficient when a file can still append or rotate.
- Envelope validation requires `source_object.sha256 == raw_object_sha256` byte-for-byte after lowercase-hex normalization; both must be valid 64-character SHA-256 hex strings. A mismatch is a hard integrity failure: preserve the received evidence, quarantine, and do not create a canonical completion or acknowledge the delivery.
- This equality assertion is a cross-cutting envelope invariant exercised within the already-approved 101-case synthetic scope; it does not add a 102nd case or expand the approved scope.
- `market_type` is explicit USD-M perpetual scope; generic `futures` is not sufficient canonical namespace evidence without a pinned source-registration rule.

## 3. Domain DTOs

### 3.1 SD-05 aggregate trade

```text
AggTradeV1 {
  envelope: CanonicalSourceEnvelopeV1
  identity: {
    exchange: "binance"
    market_type: "USD_M_PERPETUAL"
    symbol: string
    aggregate_trade_id: int64_nonnegative
  }
  event: {
    trade_time_ms: int64_nonnegative | null
    event_time_ms: int64_nonnegative | null
    price: CanonicalDecimalString
    quantity_all_q: CanonicalDecimalString | null
    quantity_non_rpi_nq: CanonicalDecimalString | null
    first_trade_id: int64_nonnegative
    last_trade_id: int64_nonnegative
    is_buyer_maker: boolean
    aggressor_side: "BUY" | "SELL"
  }
}
```

Validation:
- Identity is `(exchange, market_type, symbol, aggregate_trade_id)`; never use timestamp/price as a substitute.
- Require `first_trade_id <= last_trade_id`; reject negative IDs and values outside signed 64-bit source representability.
- `is_buyer_maker=true` maps to `aggressor_side=SELL`; false maps to BUY. If both are supplied, require exact consistency.
- `q` means quantity including RPI-involved trades; `nq` means normal quantity excluding RPI-involved trades. They are distinct. Never derive `nq` from `q`.
- Current inspected T1 source maps native `T → trade_time → timestamp_ms`, and parses `p/q/a/f/l/m`; it does not parse `nq`. Current T1 CSV numeric formatting uses f64 and 12 decimal places; it is not exact native decimal-byte preservation. Preserve the raw CSV object and mark `nq` unavailable. The source audit does not prove deployed/imported binary build lineage.
- Event time E remains unavailable in current CSV. The source-level T mapping is proven; deployed build provenance remains unverified (B-01/B-17).

### 3.2 SD-06 depth diff

```text
DepthDiffV1 {
  envelope: CanonicalSourceEnvelopeV1
  identity: {
    exchange: "binance"
    market_type: "USD_M_PERPETUAL"
    symbol: string
    first_update_id: uint64
    final_update_id: uint64
  }
  sequence: {
    previous_final_update_id: uint64
    stream_epoch: string
    snapshot_anchor_update_id: uint64
  }
  event_time_ms: int64_nonnegative | null
  transaction_time_ms: int64_nonnegative | null
  bid_changes: Array<{ price: CanonicalDecimalString, quantity: CanonicalDecimalString }>
  ask_changes: Array<{ price: CanonicalDecimalString, quantity: CanonicalDecimalString }>
}
```

Validation:
- Require `first_update_id <= final_update_id`; each side is an array of exact price/absolute-quantity pairs; zero quantity deletes a level.
- `stream_epoch` is provenance/continuity state, not identity.
- Ordinary depth is non-RPI only. Do not infer RPI liquidity.
- Current T1 source parses native E and T, U/u/pu and b/a; current CSV conversion persists E as timestamp and drops T. Producer receive time is not currently proven in the CSV.
- The canonical identity remains conditional on verified exchange namespace uniqueness and protocol bridge evidence. An unproven namespace or sequence event is quarantined; do not add stream_epoch to the identity.

### 3.3 SD-07 snapshot capture and manifest

```text
SnapshotCaptureV1 {
  envelope: CanonicalSourceEnvelopeV1
  identity: {
    capture_producer_id: string
    capture_sequence: uint64
  }
  immutable_attributes: {
    exchange: "binance"
    market_type: "USD_M_PERPETUAL"
    symbol: string
    source_kind: "BINANCE_USDM_REST_DEPTH_RESPONSE_V1"
              | "T1_RECONSTRUCTED_LOCAL_BOOK_V1"
    source_schema_version: string
    snapshot_kind: "INITIAL" | "PERIODIC" | "BRIDGE"
    captured_at_ms: int64_nonnegative
    snapshot_event_time_ms: int64_nonnegative | null
    snapshot_transaction_time_ms: int64_nonnegative | null
    last_update_id: uint64
    requested_limit: uint32 | null
    actual_bid_levels: uint32
    actual_ask_levels: uint32
    total_level_rows: uint32
    complete: true
    empty_book: boolean
    declared_depth_boundary: uint32 | null
    upstream_snapshot_anchor_ref: string | null
    stream_epoch: string | null
    last_contiguous_diff_update_id: uint64 | null
    continuity_status: "CONTIGUOUS" | "NOT_APPLICABLE"
    source_object_sha256: 64-hex
    canonical_levels_sha256: 64-hex
  }
  levels: Array<{ side: "BID" | "ASK", price: CanonicalDecimalString, quantity: CanonicalDecimalString }>
}
```

Rules:
- Sole capture identity is exactly `(capture_producer_id, capture_sequence)`. All other fields are immutable attributes bound to that pair.
- For SD-07, `envelope.provenance.capture_producer_id` and `envelope.provenance.capture_sequence` are both REQUIRED, non-null, and MUST exactly equal the corresponding `identity` fields. A null, one-sided, or mismatched pair is invalid and MUST be quarantined. The envelope fields are a provenance binding to the single authoritative capture pair, not a second identity. For SD-05/SD-06, the shared envelope capture pair remains null unless a separate domain-specific contract explicitly requires it.
- T0 owns registry/authorization; T1 issues sequence within its assigned namespace. A producer registry row or producer self-assertion is not proof of origin, uniqueness or fencing.
- REST-response and T1-reconstructed snapshots have different evidence requirements and may not be conflated.
- A snapshot group is accepted only when a source-generated completion manifest proves its exact group, counts, object digest, completeness and empty-book semantics. EOF, file rotation, elapsed time or row count alone are not completion evidence.
- No partial snapshot group is canonically accepted. Group rows and manifest are committed atomically.
- Current T1 CSV lacks this manifest and producer identity; current-schema snapshots remain non-canonical-acceptable until additive evidence exists.

## 4. Decimal canonicalization

`CanonicalDecimalString` is a base-10 string, never a binary floating-point value.

- Reject NaN, Infinity, exponent notation, leading plus, whitespace, locale separators and negative zero.
- Remove redundant leading integer zeros and trailing fractional zeros; remove the decimal point if no fractional digits remain.
- Canonical zero is exactly `0`.
- Price must be strictly positive. Quantity must be nonnegative for depth changes; retained snapshot levels must be positive.
- No rounding is allowed during canonicalization. Precision/scale ceilings are separate configuration gates (B-14/B-20).
- The original source lexeme remains available only through immutable raw-object evidence; canonical decimal normalization does not replace it.

## 5. Versioned digest encoding

Do not hash ordinary JSON serialization or a language runtime's default map order.

### 5.1 Raw evidence digest

`raw_object_sha256 = SHA256(exact immutable source-object bytes)`.

For a CSV row, the source object is the exact CSV file object and the row locator identifies the exact row. A separate optional `raw_record_sha256` may hash the exact byte range for that row. Neither digest is described as a native exchange-message digest unless original native bytes were actually retained.

### 5.2 Canonical semantic digest

Version 1 is a deterministic typed-field frame:

- Prefix: ASCII bytes `BTCQ-T0-CANONICAL-V1\0`.
- Fixed field order per domain schema; each field frame is `tag:u16 big-endian | type:u8 | length:u32 big-endian | value:bytes`.
- Type codes: UTF8=1, signed-int64=2, unsigned-int64=3, boolean=4, decimal-string=5, nullable-null=6, list=7.
- Integer values use fixed-width big-endian two's-complement (signed) or unsigned representation. Boolean is one byte 0x00/0x01. Null has zero length.
- UTF-8 strings are validated; canonical instrument identifiers use the documented lowercase ASCII normalization. Do not silently normalize arbitrary source strings.
- Decimal values use §4 canonical strings encoded as UTF-8.
- Lists encode a u32 element count followed by each element as a nested length-framed typed record. Preserve the source order for depth updates and snapshot levels in v1; reordering therefore changes the digest and is conservatively a conflict.
- Include contract version and domain discriminator in the digest preimage. Exclude delivery locator, T0 receipt/commit time, retry count and transport-attempt metadata from semantic payload digest.
- `canonical_payload_sha256 = SHA256(encoded canonical semantic payload)`.

Identity and digest are separate: same identity + same semantic digest is replay; same identity + different semantic digest is conflict. Raw object digest changes do not by themselves mean canonical semantic conflict if the semantic payload is unchanged.

## 6. Source-delivery locator and idempotency

A delivery locator identifies one immutable observation in one source object; it is not a canonical event identity.

- Delivery identity MUST be based on a stable source-object identity/version that survives retries and is independent of the object's content digest. Candidate object key: `(source_producer_id, source_object_id, source_object_version)`; a CSV row locator extends it with `(byte_start, byte_end_exclusive)`, or a stable row/group ordinal only when the object version is immutable and parser/schema version is pinned.
- `raw_object_sha256` and optional `raw_record_sha256` are immutable integrity attributes compared against the stable delivery identity; they are NOT components of the delivery identity key. Re-observing the same producer/object/version with a different digest or bytes is an integrity conflict, not a new delivery.
- A storage-provider immutable object-version ID may substitute for producer-issued object ID/version only when the storage layer proves version immutability and stable retrieval. A mutable path, filename, timestamp, byte offset without object identity, or T0 per-attempt import sequence is insufficient.
- If neither producer-issued object/version identity nor a verifiable immutable storage-version identity exists, the source delivery cannot satisfy this idempotency contract and MUST be quarantined; do not silently fall back to content SHA as the identity key.
- Snapshot locator identifies the whole immutable group/manifest under the stable object/version identity, not an arbitrary price-level row.
- Unique delivery constraint: one terminal intake outcome per stable immutable locator and source schema version.
- Same stable locator retry returns the already committed outcome. Same locator with changed object digest or row bytes is a source-object integrity conflict, not a new attempt.

### 6.1 Durable evidence for a changed-content delivery-locator conflict

A stable delivery locator may already have one committed terminal completion. If the same locator is observed again with different source bytes or integrity digests, the second observation MUST be preserved as a separate append-only integrity-conflict record. It MUST NOT overwrite the original completion, be treated as a new delivery, or create a second `SourceDeliveryCompletionV1` for the same locator.

Proposed record:

```text
SourceDeliveryIntegrityConflictV1 {
  conflict_id: string
  source_producer_id: string
  source_partition_id: string
  stable_delivery_locator: immutable locator
  prior_completion_ref: immutable reference
  expected_raw_object_sha256: 64-hex
  observed_raw_object_sha256: 64-hex
  expected_raw_record_sha256: 64-hex | null
  observed_raw_record_sha256: 64-hex | null
  conflicting_source_evidence_ref: immutable durable object reference
  observed_at_ms: int64
}

SourceDeliveryIntegrityConflictResolutionV1 {
  resolution_id: string
  conflict_id: string
  resolution_outcome: "RESOLVED"
  resolution_reason: string
  resolution_evidence_refs: list<immutable reference>
  resolved_by_ref: immutable authority reference
  resolved_at_ms: int64
}
```

Rules:
- Before recording the conflict, durably preserve the newly observed conflicting source object/record bytes under a distinct immutable evidence key and bind its verified reference and observed digest to the conflict record. Preserve the original expected digest and prior completion reference as well.
- Filesystem and object-store evidence publication MUST use atomic no-clobber/create-if-absent semantics. Existing objects are immutable: verify exact bytes/digest and reuse only when identical; never replace or truncate an existing object. If the stable key exists with different bytes, preserve the incoming observation under a different collision-safe immutable evidence key before appending the conflict record.
- A concurrent publication race is resolved only by the no-clobber primitive: exactly one create succeeds; losing writers read/verify the winner and either deduplicate identical bytes or preserve differing bytes under a distinct evidence key. No last-writer-wins behavior is permitted.
- If no-clobber publication or distinct-key evidence preservation cannot be proven, fail closed without completion, cursor/checkpoint advancement or ACK.
- Insert `SourceDeliveryIntegrityConflictV1` append-only under a unique `conflict_id`. The conflict record is immutable after insertion: it has no `disposition`, `resolution_ref` or other mutable lifecycle field. Never update it, the prior completion or the original evidence.
- If the conflict is later adjudicated, append exactly one `SourceDeliveryIntegrityConflictResolutionV1` under a unique `resolution_id` and a unique `conflict_id`; it references the conflict and records the immutable decision, reason, evidence and authorized resolver. The resolution event is itself immutable; no UPDATE/DELETE is permitted for either record.
- Conflict status is a read-time projection, not a stored mutable field: `OPEN` when no valid resolution event exists for the conflict; `RESOLVED` when exactly one valid resolution event exists and its authority/evidence references verify. Conflicting or duplicate resolution events are an integrity violation and fail closed. Absence of a resolution event never implies resolution.
- The retry path returns `INTEGRITY_CONFLICT` after the conflict evidence is durable. It does not return the prior success as if the new observation were identical, does not create another delivery completion, and does not advance the source cursor or book watermark.
- If conflicting bytes cannot be durably preserved and referenced, fail closed: quarantine the observation, do not acknowledge it, and do not advance any checkpoint.
- This record is an evidence/audit path, not a new source identity or a mechanism to bypass the stable-locator uniqueness constraint.

## 7. Checkpoint contract

Two independently persisted checkpoints are mandatory.

```text
SourceDeliveryCursorV1 {
  source_producer_id: string
  source_partition_id: string
  highest_contiguous_terminal_sequence: uint64
  cursor_generation: uint64
  committed_at_ms: int64
}

SourceDeliveryCompletionV1 {
  source_producer_id: string
  source_partition_id: string
  source_partition_sequence: uint64
  source_object_id: string
  source_object_version: string
  record_locator: immutable locator
  source_schema_version: string
  raw_object_sha256: 64-hex
  last_terminal_outcome: "ACCEPTED" | "DUPLICATE_REPLAY" | "CONFLICT"
                       | "QUARANTINED" | "GAP_RECORDED" | "RESOURCE_REJECTED"
  completed_at_ms: int64
}

BookSequenceWatermarkV1 {
  exchange: string
  market_type: string
  symbol: string
  snapshot_capture_identity: (capture_producer_id, capture_sequence)
  stream_epoch: string
  snapshot_anchor_update_id: uint64
  last_contiguous_applied_update_id: uint64
  continuity_state: "CONTIGUOUS" | "GAP_PENDING" | "GAP_UNRESOLVED"
                   | "CONFLICTED" | "UNAVAILABLE"
  watermark_generation: uint64
  committed_at_ms: int64
}
```

Rules:
- Each source partition has a producer/manifest-defined stable ordered sequence. Persist each terminal outcome in `SourceDeliveryCompletionV1`; enforce uniqueness on `(source_producer_id, source_partition_id, source_partition_sequence)` and on the stable delivery locator. The source cursor is the highest contiguous sequence whose every preceding sequence has a durable terminal completion. Out-of-order completions remain recorded but cannot move the frontier over a hole. Intentional no-record positions require an explicit durable producer/manifest tombstone; never infer a skipped sequence. If no stable ordered sequence/manifest ordinal exists, use per-locator completion state and safe rescan rather than a last-seen cursor.
- Source cursor/frontier is written only by transaction step 9, after the source observation and terminal outcome are durable and the contiguous-terminal check succeeds. A durable quarantine/gap/resource rejection may count as a terminal completion for its own sequence, but cannot move the frontier across any earlier unfinished sequence. Changed-content locator conflicts use the separate append-only conflict record and do not create another completion.
- Book watermark advances only after a diff is actually and contiguously applied to the derived book and the resulting book state is durable.
- A source cursor may be ahead of the book watermark. This is expected after quarantine/gap and is not evidence of book continuity.
- A watermark may never jump over a gap, conflict, quarantine, resource rejection or unapplied event.
- Restart restores both markers and unresolved-gap state independently. Never derive one from the other.

## 8. Atomic persistence and acknowledgement

Logical transaction boundary for one intake observation:

1. Verify immutable source object is durable and addressable before opening the DB transaction.
   - **Filesystem publication MUST be no-clobber.** Create a uniquely named temporary object with exclusive creation; write all bytes; flush and `fsync` the file; verify the exact byte count and SHA-256; then publish with an atomic create-if-absent/no-replace primitive (for example, a platform primitive equivalent to `renameat2(RENAME_NOREPLACE)` or an atomic hard-link publication where supported); finally `fsync` the parent directory. A regular rename that can replace an existing destination is prohibited. Never fall back to overwrite semantics when the filesystem lacks a no-replace primitive.
   - If the stable object key already exists or a concurrent publisher wins the create-if-absent race, leave that object untouched and read/verify its exact bytes and digest. If the digest and bytes match the incoming object, treat it as the same already-durable immutable object. If they differ, preserve the incoming observation under a separate unique immutable evidence key using the same no-clobber protocol, verify and sync it, then append the integrity-conflict evidence. The stable object, prior evidence and prior completion remain unchanged.
   - Evidence keys must be immutable and collision-safe. Use a content-addressed key plus a unique observation identifier where needed; if a candidate evidence key already exists, verify exact bytes/digest and allocate a different unique key on mismatch—never replace it. The evidence reference in the conflict record must resolve to the verified preserved bytes.
   - If atomic no-clobber publication, exact digest verification, durable sync or distinct-key preservation cannot be guaranteed, fail closed: do not append a completion, advance any cursor/checkpoint or ACK. A backend without the required immutability capability is unsupported for this contract.
   - For object storage, require conditional create-if-absent/immutable version semantics, successful durability acknowledgement, and read-after-write verification sufficient to prove that an existing version cannot be overwritten.
2. Begin one T0 canonical-store transaction.
3. Insert/verify source-object and record-locator evidence.
4. Claim the delivery locator under a unique constraint. On conflict, compare exact locator/object digest: if identical, return the prior terminal result; if bytes or digest differ, durably preserve the conflicting observation and append a separate `SourceDeliveryIntegrityConflictV1` record, then return `INTEGRITY_CONFLICT` without creating a second completion or changing the prior result.
5. Resolve native canonical identity:
   - absent identity → reject/quarantine;
   - same identity + same semantic digest → DUPLICATE_REPLAY;
   - same identity + different semantic digest → CONFLICT, preserve both evidence references, no overwrite;
   - new identity → candidate acceptance subject to all domain validations.
6. For accepted SD-06 diffs, apply the event to the derived book only if snapshot bridge and continuity are valid; persist canonical event, application outcome, derived book mutation and book watermark in the same transaction.
7. For a gap/conflict/quarantine/resource rejection, persist the source evidence, terminal outcome and gap state only; do not update the source cursor/frontier and do not advance the book watermark. A changed-content retry for an already-completed stable locator is recorded only in the append-only integrity-conflict evidence path; it does not create another completion.
8. For SD-07, insert manifest, capture identity, all level rows and terminal outcome in one transaction. Partial groups are not visible as accepted captures.
9. Persist the per-delivery terminal completion, then perform the sole source-cursor/frontier update in this step: recompute the highest contiguous sequence for which every preceding sequence has a durable terminal completion (including explicit tombstones for intentional no-record positions), and update it using compare-and-swap/monotonic-generation protection. Retain out-of-order completions without moving the frontier over a hole. No other step may write or advance the source cursor/frontier.
10. Commit. Only after commit may T0 acknowledge the source delivery.

### Crash/retry matrix

| Crash point | Required recovery |
|---|---|
| Before source object durable | No cursor advance; source must be reacquired/retried |
| Stable evidence key already exists with identical bytes | Verify exact bytes/digest; reuse the existing immutable object; never overwrite |
| Stable evidence key already exists with different bytes, including a concurrent publish race | Preserve incoming bytes under a distinct immutable no-clobber evidence key; append conflict evidence only after durability verification; keep existing object/completion unchanged |
| No-clobber publication or distinct evidence preservation unavailable | Fail closed; no completion, cursor/checkpoint advance or ACK |
| After object durable, before DB transaction | Orphan immutable object is safe; rescan/retry by same locator |
| Changed bytes/digest at an already-completed stable locator | Preserve conflicting bytes as an immutable evidence object; append one integrity-conflict record; retain the original completion unchanged; no second completion or cursor/book-watermark advance |
| During DB transaction | Rollback all canonical rows/outcomes/checkpoints/book changes |
| After DB commit, before acknowledgement | Retry same locator; return prior committed outcome; no duplicate book effect |
| After acknowledgement | Commit and both checkpoint states already durable |

### Store requirements

- One transaction must cover delivery claim, canonical identity/digest outcome, checkpoint state and applicable derived-book mutation.
- A store that cannot enforce unique constraints and atomic multi-record transactions cannot implement this contract.
- For SQLite, transaction mode, journal/synchronous settings, busy/lock handling, durability guarantees, backup/restore behavior and single-writer fencing must be separately verified before claiming crash durability.
- External object storage is outside the SQLite transaction; the immutable object must be durable before committing a DB reference. Orphan objects are acceptable; dangling DB references are not.
- No delete-on-ack, source-object deletion or automatic retention expiry is included.

## 9. Blocker disposition after source audit and design work

| Blocker | Current disposition | Why it remains open / closure evidence |
|---|---|---|
| B-01 | PARTIALLY RESOLVED | T1 source proves T→timestamp_ms and q/a/f/l/m mappings; build provenance and exact decimal/raw-payload fidelity remain unverified |
| B-02 | OPEN — CONTRACT PROPOSED | ID fields are parsed as signed i64; nonnegative/range/order validation must be tested and source semantics pinned |
| B-03 | RESOLVED AT SOURCE-MAPPING LEVEL | T1 maps m=true→sell, false→buy; Binance describes m as buyer-maker. Contract requires exact cross-field validation; tests still pending |
| B-04 | OPEN | No immutable stream_epoch in current T1 CSV; additive capture provenance and lifecycle proof required |
| B-05 | OPEN | Binance defines U/u/pu, but exchange namespace uniqueness across reconnect/restart and the selected exact USD-M snapshot bridge still need pinned protocol/T1 proof |
| B-06 | OPEN | T1 parses E and T but current CSV drops T; raw-message bytes and receive-time provenance are not persisted in current schema |
| B-07 | OPEN | Producer-origin attestation, allocator, single-writer fencing, durable sequence non-reuse and restore/rollback proof absent |
| B-08 | OPEN | Source-generated snapshot completion manifest absent |
| B-09 | OPEN | Snapshot-to-stream epoch linkage absent |
| B-10 | OPEN | Immutable object/manifest and stable row/group locator policy not implemented/proven |
| B-11 | DESIGN SPECIFIED — NOT VERIFIED | Typed digest preimage proposed here; requires independent review, cross-language vectors and exact-decimal tests |
| B-12 | DESIGN SPECIFIED — NOT VERIFIED | Atomic transaction/recovery protocol proposed; requires store-specific crash/restart/rollback proof |
| B-13 | CLOSED — OWNER BOUNDED EXCLUSION | Read API/dataset-version compatibility remains outside Phase B |
| B-14 | OPEN | Numeric count/age/wait limits cannot be invented; measure source behavior and owner-approve ceilings |
| B-15 | OPEN — SOURCE OMISSION CONFIRMED | aggTrade nq absent; depth T parsed but dropped by current CSV conversion |
| B-16 | CLOSED — OWNER BOUNDED EXCLUSION | Ordinary non-RPI depth only |
| B-17 | OPEN — SOURCE MAPPING PASS, BUILD PROVENANCE BLOCKED | Exact source path proven; deployed/imported producer binary not tied to that source build |
| B-18 | OPEN | Snapshot manifest fields designed; source producer does not emit/verify completion manifest |
| B-19 | DESIGN SPECIFIED — NOT VERIFIED | Independent cursor/watermark and restart semantics specified; atomic implementation proof absent |
| B-20 | OPEN | Raw bytes, parsed levels, decimal token, buffer and group ceilings require measurement and owner approval |

A design-level resolution is not an implementation/test pass. B-03 is closed only at source-mapping semantics; its DTO validation remains a mandatory test gate. B-11/B-12/B-19 are specified but remain blockers until independently reviewed and proven in the selected store.

## 10. Remaining hard gates

1. Pin and verify exact deployed/imported T1 binary/build provenance or keep the affected data lineage unverified.
2. Verify exact Binance USD-M bridge protocol and exchange identity namespace scope; do not infer across product families.
3. Define and prove T1 producer attestation, allocation, fencing, sequence persistence and restore/rollback policy.
4. Define source-generated SD-07 manifest and stable immutable source object/row locators.
5. Derive numeric limits from bounded source measurements and resource budgets; owner approval required.
6. Independently review this DTO/digest/checkpoint/atomicity design.
7. Owner approval for the isolated 101-case test scope is recorded in `docs/decisions/T0_PHASE_B_101_SYNTHETIC_CASES_OWNER_APPROVAL_2026-11-22.md`. Create fixtures and execute only after satisfactory independent review of exact Revision 16 SHA/blob; no production DTO/validator/persistence implementation is authorized.

## 11. Explicit non-authorization

No production code, DTO/parser/validator/persistence implementation, DDL, database mutation, source copy, import, data movement, collector activation, T0/T1 runtime, T2 connection, API, VPS process, systemd/autostart, deployment or trading action is authorized by this design. The separately owner-approved 101-case synthetic test scope is limited to isolated test-only fixtures/harness and execution after independent review; it remains NOT EXECUTED. Contract Freeze remains NOT APPROVED.

