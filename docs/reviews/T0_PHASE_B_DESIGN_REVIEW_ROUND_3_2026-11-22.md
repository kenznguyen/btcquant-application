# T0 Phase B Revision 3 — Design Review

- Review date: 2026-11-22
- Reviewed commit: `98cde283e9b2dc2d0201e4359e3f1195016ff0ea`
- Reviewed design path: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`
- Exact design blob SHA: `2e61e13ec8dc42a37ea03130edc1491b73a903bc`
- Scope: SD-05 aggregate trades; SD-06 depth diffs; SD-07 snapshots; 66 proposed synthetic cases.
- Review method: exact-commit document inspection, cross-check against pinned T1 CSV schema blob `895f87a8281a3f9b6d37d96b5f68568e4285bee6`, prior review dispositions R-01..R-11 and official Binance USDⓈ-M documentation.
- Review type limitation: this is a separate review pass against the pinned revision, but no external human/second-model reviewer identity is established. Do not represent it as independently verified second-person approval.
- Tests/workflows/artifacts: NOT RUN / NONE (documentation review only).

## Verdict

**REQUEST CHANGES — PHASE B DESIGN REVISION 3 NOT APPROVED.**

R-07..R-11 are materially improved and the 66-case matrix is coherent in count. The prior six findings are largely addressed at the conceptual level. However, three additional consistency/contract gaps remain. Contract freeze, implementation and Phase C remain NOT APPROVED / NOT AUTHORIZED.

## Findings

### R-12 — HIGH: Snapshot source variants are not modeled as distinct capture contracts

**Location:** §5.1–§5.3, especially lines 242–255.

The pinned T1 schema describes snapshot event types `depth_snapshot_initial`, `depth_snapshot` and `depth_snapshot_bridge`, and one CSV row per level. Revision 3 correctly introduces `source_kind`, endpoint and request parameters in the proposed manifest, and explains the bounded semantics of Binance REST `/fapi/v1/depth`. However, it does not define which of the T1 snapshot event types represent:
- a direct bounded REST depth response;
- a collector-generated snapshot of its locally reconstructed book; or
- another snapshot/capture mechanism.

These source variants do not necessarily share the same completeness proof or meaning of `requested_limit`. A locally reconstructed periodic snapshot cannot be validated as though it were a direct REST response unless its source lineage, local book continuity, depth boundary and completeness are independently established.

**Required correction:** define an explicit allowlist of snapshot source kinds and a separate acceptance/completeness contract for each. For REST captures, bind the exact REST endpoint, request limit and response metadata. For collector-derived snapshots, bind the upstream snapshot anchor, stream epoch, last contiguous applied update, source-book continuity state, configured depth boundary and evidence that the local book was not already discontinuous. If a variant cannot supply its required proof, keep it non-canonically-acceptable. Add synthetic cases for source-kind mismatch and false completeness claims across variants.

### R-13 — HIGH: §6 contradicts the bounded-snapshot contract

**Location:** §6 relationship table, line 283.

The table states that the snapshot is a **“full-state anchor”**, while §5.2–§5.4 correctly states that a REST snapshot is bounded top-N, does not contain the entire exchange book, and cannot establish all deeper levels or full top-N ranking after arbitrary updates.

This wording can cause consumers to interpret a bounded response as a complete exchange state and undermines R-08.

**Required correction:** replace “full-state anchor” with wording such as “bounded snapshot anchor for the returned levels and its declared source/depth scope.” State that the snapshot anchors sequence continuity only within its proven scope; it does not establish the unseen remainder of the exchange book. Align the terminology in the synthetic matrix and derived-book contract.

### R-14 — MEDIUM: SD-06 acknowledgement matrix still treats stream epoch as part of retry identity

**Location:** §8 replay/conflict/quarantine/acknowledgement matrix, line 318.

The SD-06 “Lost acknowledgement” cell says “Retry same epoch/update range.” Earlier §4.3 explicitly says `stream_epoch` is provenance/continuity state, not canonical event identity. Requiring the same epoch as the retry identity is therefore inconsistent with R-01 and may lead to treating an identical exchange event replayed after reconnect as a different event.

The adjacent “Missing native identity” row also groups a missing `stream_epoch` with missing native identity, although the document correctly says epoch is not the canonical identity. Missing epoch should be described as missing continuity/session provenance, not missing exchange-event identity.

**Required correction:** define retry identity using the immutable source-delivery position/evidence locator plus the candidate native update range and verified exchange namespace; keep epoch as continuity metadata. Split the matrix outcomes into “native event identity missing” and “stream epoch/continuity provenance missing.” The latter blocks book-continuity acceptance but must not redefine canonical identity.

## Prior finding disposition

| Finding | Review disposition |
|---|---|
| R-01 | Conceptually addressed; uniqueness scope remains an explicit B-05 blocker |
| R-02 | Conceptually addressed; source-generated capture proof remains blocked |
| R-03 | Addressed at design level; q mapping remains NOT VERIFIED |
| R-04 | Addressed with explicit non-RPI scope |
| R-05 | Addressed at design level; source fidelity remains blocked |
| R-06 | Addressed at design level with bounded reorder/gap policy and separate cursors |
| R-07 | Addressed |
| R-08 | Addressed, but R-12/R-13 prevent approval of snapshot semantics |
| R-09 | Addressed |
| R-10 | Addressed as categories; numeric ceilings remain unfrozen |
| R-11 | Addressed; quantity-to-q consistently NOT VERIFIED |

## Positive review observations

- SD-05 now correctly distinguishes Binance aggTrade `E` event time and `T` trade time; T1 CSV `timestamp_ms` is only a candidate for `T`, not `E`.
- `q` and `nq` are distinguished; absent `nq` is not fabricated and quantity-to-`q` remains NOT VERIFIED.
- SD-06 keeps stream epoch out of candidate canonical identity and does not claim update-ID uniqueness without evidence.
- Ordinary depth is explicitly non-RPI; the design does not call it an all-liquidity book.
- Source-delivery cursor and book-sequence watermark are separately defined, including durable quarantine and restart semantics.
- Resource ceilings now include bytes, levels, numeric tokens, parser structure and snapshot group size.
- The 66 proposed tests are clearly marked NOT EXECUTED; no implementation readiness is implied.

## Evidence and limitations

1. Pinned T1 schema: `kenznguyen/binance-futures-collector/docs/SCHEMA.md`, blob `895f87a8281a3f9b6d37d96b5f68568e4285bee6`. It documents one row per snapshot level and the initial/periodic/bridge event types; it does not provide capture ID, completion manifest, source endpoint, requested limit or source-side completeness evidence.
2. Binance USDⓈ-M aggTrade stream documentation: https://developers.binance.info/docs/derivatives/usds-margined-futures/websocket-market-streams/All-Market-Mini-Tickers-Stream — defines `E`, `T`, `q`, and `nq`.
3. Binance USDⓈ-M REST depth documentation: https://developers.binance.info/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data — `/fapi/v1/depth` has supported limits through 1000, returns `lastUpdateId`, `E`, `T`, bids and asks, and excludes RPI orders.
4. Binance USDⓈ-M WebSocket API order-book documentation: https://developers.binance.me/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-api/market-data — explicitly describes the response as limited market depth.
5. The T1 implementation/parser was not inspected in this review; no source/runtime behavior is asserted.

## Status and next step

- Design review: **REQUEST CHANGES**.
- R-12..R-14: open.
- B-01..B-20: remain open unless separately evidenced or owner-accepted.
- Synthetic matrix: 66 cases, NOT EXECUTED.
- Independent second-person review: NOT VERIFIED.
- Contract freeze: NOT APPROVED.
- Implementation / database / runtime / Phase C: NOT AUTHORIZED.
- Next: revise only the Phase B design and synthetic matrix for R-12..R-14, preserve all prior blockers, then submit a new exact design SHA for review. Documentation-only.
