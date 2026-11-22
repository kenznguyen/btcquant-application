# T0 Phase B — Second-Round Design Self-Review

- Review date: 2026-11-22
- Review mode: **self-review / static design review** (not an independent second-person review)
- Exact reviewed design commit: `75e593517ec31d2e2a75ed0050e80ab5dd52edf2`
- Exact reviewed design blob: `56f2012d6625e5af328d7d5881d892a38a2121e9`
- Design path: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`
- Prior review: `docs/reviews/T0_PHASE_B_DESIGN_REVIEW_2026-11-22.md`, commit `347dbcec6f7ddedac4ac1c8e90ee57c549ae49ef`
- T1 source-schema baseline: `kenznguyen/binance-futures-collector/docs/SCHEMA.md`, blob `895f87a8281a3f9b6d37d96b5f68568e4285bee6`
- Verdict: **REQUEST CHANGES — PHASE B DESIGN NOT APPROVED**
- Contract freeze: **NOT APPROVED**
- Implementation: **NOT AUTHORIZED / NOT STARTED**
- Tests/workflows/artifacts: **NOT RUN / NONE**

## 1. Executive result

Revision 2 materially improves the design and addresses important parts of R-01..R-06. However, it is not safe to approve as a design baseline yet. Static review found five additional required findings (R-07..R-11) and identified incomplete closure of four original findings.

The most consequential issue is a timestamp mapping error in SD-05: Binance USD-M aggTrade defines `E` as event time and `T` as trade time, while the pinned T1 schema explicitly says its `timestamp_ms` is trade time. The revision's native-field table maps `E` to `timestamp_ms` and marks `T` unavailable. This reverses the documented semantics and can mislabel or lose time data.

The SD-07 snapshot design also needs to distinguish a complete capture of a bounded REST response from a complete representation of the entire order book. Binance USD-M `GET /fapi/v1/depth` returns limited market depth, with allowed limits up to 1000 levels; it is not an unlimited full-book snapshot.

## 2. Review of original findings R-01..R-06

| Original finding | Disposition | Review result |
|---|---|---|
| R-01 — canonical identity vs stream epoch | **PARTIALLY RESOLVED** | Correctly removes `stream_epoch` from candidate canonical identity and retains it as capture/continuity provenance. Cross-epoch replay/conflict behavior is clearer. However, uniqueness scope of (exchange, market, symbol, U, u) is still unproven. Keeping canonical acceptance blocked is correct; no approval until exchange/source evidence establishes the namespace and lifecycle. |
| R-02 — snapshot identity/completeness | **PARTIALLY RESOLVED** | Source-generated capture ID, framing, expected count/equivalent declaration, immutable object digest and completion manifest are good fail-closed gates. But the manifest does not yet bind the exact snapshot source/endpoint, request depth limit, returned bid/ask counts and bounded-depth semantics. Completeness must mean complete capture of the response at its declared limit, not the entire order book. See R-08. |
| R-03 — aggTrade `nq` | **PARTIALLY RESOLVED** | Correctly distinguishes `q` and `nq` and refuses to derive `nq`. However, the document simultaneously calls the CSV `quantity` a present mapping to `q`, calls it a candidate mapping pending source verification, and writes a test case as though the mapping were already documented/frozen. Normalize these statements; see R-07 and R-11. |
| R-04 — RPI depth scope | **ADDRESSED WITH SCOPE LIMITATION** | Ordinary depth is clearly labeled non-RPI and RPI inclusion is excluded. The snapshot section should also state the bounded top-N nature of the ordinary snapshot, separately from the non-RPI limitation; see R-08. |
| R-05 — depth transaction time `T` | **PARTIALLY RESOLVED** | SD-06 correctly separates `E` and `T` and marks T unavailable in current CSV. But the same native timestamp distinction is not handled for SD-05 aggTrade or the SD-07 REST snapshot response. SD-05 currently contains a reversed mapping; see R-07 and R-10. |
| R-06 — bounded reordering/gaps/checkpoints | **PARTIALLY RESOLVED** | Adds bounded event-count/age buffering, gap states, fail-closed overflow and recovery. It does not bound bytes/levels per message, and it does not clearly separate the source-delivery acknowledgement cursor from the contiguous book-sequence watermark. See R-09 and R-10. |

## 3. New required findings

### R-07 — CRITICAL: SD-05 aggTrade E/T timestamp mapping is reversed

**Evidence in reviewed design**
- Section 3.1 says native `E` (event time) is represented by T1 `timestamp_ms`, and says native `T` (trade time) has no separate field.
- Section 3.2 maps T1 `timestamp_ms` to candidate `trade_time_ms`.
- Section 3.4 and the pinned T1 schema say `timestamp_ms` is trade time.
- The pinned T1 schema blob states: “Aggregated trades ... `timestamp_ms` is the trade time.”

**Exchange evidence**
- Binance USD-M Aggregate Trade Streams defines `E` as Event time and `T` as Trade time:
  https://developers.binance.info/docs/derivatives/usds-margined-futures/websocket-market-streams/All-Market-Mini-Tickers-Stream

**Required correction**
1. Correct native mapping: `E` = event time; `T` = trade time.
2. T1 CSV `timestamp_ms` is documented as trade time and is therefore only a candidate mapping to native `T`, subject to pinned T1 implementation verification.
3. Native `E` is not represented by the currently documented T1 CSV unless source code/raw evidence proves otherwise; mark it unavailable rather than mapping it to `timestamp_ms`.
4. If raw native messages are retained, preserve both E and T distinctly.
5. Update the mapping tables, provenance/time section, blocker wording and synthetic tests to catch E/T reversal.

**Severity:** Critical — semantic time corruption in canonical records.

### R-08 — REQUIRED: SD-07 snapshot completeness is not bounded-depth completeness

**Evidence**
- SD-07 calls the grouped level set a complete snapshot and describes it as a full-state/reconstruction anchor.
- Binance USD-M `GET /fapi/v1/depth` explicitly returns limited market depth. Valid limits are 5, 10, 20, 50, 100, 500 and 1000; maximum 1000.
- The ordinary endpoint excludes RPI. A separate `/fapi/v1/rpiDepth` endpoint exists.

**Exchange evidence**
- Binance USD-M REST Market Data / Order Book:
  https://developers.binance.me/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data

**Required correction**
1. Define snapshot completeness as “all levels in the exact bounded response were captured and verified,” not “the entire exchange order book is represented.”
2. Record exact endpoint/source kind, requested limit, actual bid/ask row counts, snapshot response identity and non-RPI visibility in the capture manifest.
3. State that the reconstructed book is bounded to the snapshot's returned depth plus subsequent accepted updates; it may not know levels beyond the initial returned boundary.
4. Specify behavior when a later update introduces a level outside the initial top-N boundary and when the local book cannot prove its rank/completeness.
5. Do not describe the snapshot as a full-depth book unless a source contract actually provides full depth.

**Severity:** High — risk of overstating book completeness and downstream liquidity visibility.

### R-09 — REQUIRED: separate ingestion acknowledgement cursor from book sequence watermark

**Evidence**
- Section 8 says acknowledgement may follow a durable quarantine/gap outcome.
- Section 4.5 says a future checkpoint binds the last durably accepted sequence and source evidence position.
- Section 4.7 says the checkpoint must not advance across pending/unresolved gaps.

These can be consistent only if the design defines two distinct progress markers. A durable source row can be safely ingested/quarantined and acknowledged while the reconstructed book's contiguous sequence watermark remains before the unresolved gap.

**Required correction**
1. Define at least two separate cursors:
   - source-delivery/import cursor: source file/object/row or message delivery position, advanced only after the raw observation and its accepted/quarantine/conflict outcome are durably recorded;
   - book-sequence watermark: highest contiguous update sequence actually applied to the derived book, never advanced across gaps/conflicts/uncommitted evidence.
2. Specify restart/replay behavior for both cursors.
3. State explicitly that source acknowledgement of a durably quarantined gap does not assert book continuity or advance the book watermark.
4. Define the relationship to the atomic transaction/recovery protocol in B-12.

**Severity:** High — ambiguity can cause ingestion stalls or accidental sequence skipping.

### R-10 — REQUIRED: resource bounds do not bound memory or parser work

**Evidence**
- Section 4.7 bounds the reorder buffer by event count and residence age only.
- A single diff event may contain many bid/ask level tuples and large numeric strings; event count alone does not bound bytes, parser allocation or CPU.
- Snapshot grouping can also accumulate many rows before completion proof.

**Required correction**
1. Specify configurable hard ceilings for raw message bytes, parsed levels per diff, numeric token length/precision, total buffered bytes and snapshot group rows/bytes.
2. Fail closed before unbounded allocation/parsing; persist a bounded rejection/quarantine reference and mark the derived book unavailable if a diff cannot safely be processed.
3. Include independent synthetic cases for oversized message, too many levels, excessive decimal token length, total reorder-buffer byte exhaustion and snapshot group resource ceiling.
4. Keep numeric values unfrozen until source measurements and owner-reviewed resource budgets exist; do not invent defaults.

**Severity:** High — current count/age bounds alone do not guarantee bounded memory use.

### R-11 — REQUIRED: SD-05 q mapping is internally inconsistent

**Evidence**
- Section 3.1 table marks `quantity` as present and assigns candidate canonical `quantity_all`.
- The paragraph immediately below calls the mapping only a candidate pending source-code verification.
- Section 3.2 maps `quantity` to canonical `quantity` without the same qualification.
- Synthetic SD-05 case 1 says “documented `q` mapping,” and case 2 treats the CSV `quantity` as `q`.

**Required correction**
1. Mark every T1 CSV `quantity` → Binance `q` mapping as **candidate / NOT VERIFIED** until the pinned T1 parser/source implementation is inspected.
2. Do not call it a documented native-field mapping merely because the CSV schema labels it “size.”
3. Make all mapping tables, narrative and test cases use the same status.
4. Preserve `nq` as unavailable for this CSV version unless raw source evidence or a versioned source contract supplies it.

**Severity:** Medium — inconsistent contract language can prematurely freeze an unverified mapping.

## 4. Additional technical observations

1. The canonical event identity separation in R-01 is directionally correct, but B-05 remains a hard blocker. Do not claim cross-epoch identity is proven.
2. SD-06 correctly treats bid/ask quantities as absolute quantities and zero as level removal.
3. SD-06 non-RPI visibility is correctly disclosed. Do not infer an all-liquidity book from the ordinary stream.
4. Snapshot capture ID + immutable object digest + completion manifest is a sound direction, but the manifest must bind the source request and bounded-depth scope (R-08).
5. The design correctly keeps raw object digest separate from canonical semantic digest and does not invent serialization.
6. No source implementation, parser, fixtures, tests, DDL or runtime behavior was inspected or executed in this review.

## 5. Synthetic test matrix disposition

The 45-case matrix is useful but incomplete for the newly found risks. Add at least:
- SD-05: distinct native E and T values; assert CSV trade timestamp candidate maps only to T and E remains unavailable unless separately captured; assert q mapping remains unverified until source evidence.
- SD-06: raw message byte ceiling, level-count ceiling, numeric token ceiling, aggregate reorder-buffer byte ceiling, fail-closed state and no checkpoint advancement on resource rejection.
- SD-07: response limit and returned row counts bound to manifest; incomplete capture vs complete bounded response; explicit bounded-depth metadata; oversized group rejection; endpoint/source-kind mismatch; snapshot E/T preservation or explicit unavailability.
- Cross-domain checkpoint: durable source quarantine advances source-delivery cursor while book-sequence watermark remains unchanged before the gap; restart replays neither accepted rows nor applied book updates twice.

The current matrix remains **DESIGNED ONLY / NOT EXECUTED**. No tests were run as part of this review.

## 6. Five-axis assessment

| Axis | Result | Notes |
|---|---|---|
| Correctness | **FAIL** | R-07 timestamp reversal; R-08 bounded snapshot semantics; R-09 cursor ambiguity. |
| Readability / consistency | **PARTIAL** | R-11 mapping status contradicts itself; some “complete snapshot/full-state” wording overstates bounded source data. |
| Architecture | **PARTIAL** | T0/T1 ownership and source-vs-derived book separation are sound; cursor separation and bounded-depth modeling need explicit contracts. |
| Security / robustness | **PARTIAL** | Fail-closed principles are present, but event-count/age limits alone do not bound payload memory/parser work (R-10). |
| Performance / resource safety | **FAIL** | No byte/level/token/group resource ceilings are specified. |

## 7. Verdict and required next step

**VERDICT: REQUEST CHANGES — PHASE B DESIGN NOT APPROVED.**

Required before another review:
1. Fix R-07 through R-11.
2. Reconcile original R-01..R-06 dispositions, particularly R-02, R-03, R-05 and R-06.
3. Expand the synthetic matrix and renumber/count it accurately.
4. Keep B-01..B-16 open where evidence/owner decisions are still missing; add blockers for timestamp source mapping, bounded snapshot semantics, separate cursors and resource ceilings if not covered by existing blockers.
5. Update the design and request another review against a new exact commit/blob.

No implementation, Phase C, T1 source change, runtime ingestion, database, data movement, network/exchange calls, VPS/deployment, source deletion or trading action is authorized. Phase B remains documentation-only. Tests/workflows/artifacts: **NOT RUN / NONE**.
