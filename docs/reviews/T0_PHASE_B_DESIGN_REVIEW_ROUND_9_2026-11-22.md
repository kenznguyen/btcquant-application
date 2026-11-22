# T0 Phase B Revision 8 — Full Design Review Round 9

- Review date: 2026-11-22
- Reviewed design commit: `9a5c65f3bc00876d98a070eee46072c5d8be368e`
- Reviewed design blob: `8f40248f2781cdf4111ef022b77843acea8279b2`
- Revision 8 self-review commit: `1c55ef8772fb33cc51d64182217de925d1d1a45d`
- Revision 8 self-review blob: `6e1c382e4949103b200d6c0dd6f88383c88eb464`
- Immutable Revision 7 design: `f61fe365f2558569744cbc2a2ca555021a931f48` / `86825e77f69c6943096d8e9f4ecae75b413b2013`
- Immutable Revision 6 design: `9b69c18ea16731bf28efba7a92077e96a74107ce` / `7012a228561620f4447a0e363a2c5f27d734912a`
- Scope: full design review of Phase B SD-05, SD-06 and SD-07, common provenance, identity, checkpoint/recovery, acceptance semantics, proposed tests, blockers and governance/traceability.
- Review type: independent model-assisted document review. This is not a verified independent human review.

## Verdict

**REQUEST CHANGES — REVISION 8 IS NOT READY FOR CONTRACT FREEZE.**

The P2-4 correction in B-07 is present and internally consistent with the producer-pair-only identity rule in §5.2. The producer-origin and allocator/fencing prerequisites remain explicit. However, the full-document review found unresolved cross-document identity conflicts and review-baseline metadata defects. The proposed synthetic matrix also has a material gap around non-identical overlapping SD-06 update ranges.

No blocker is closed by this review. B-01..B-20 remain OPEN pending evidence or an explicit owner-approved bounded exclusion. Contract Freeze remains NOT APPROVED.

## 1. Review baseline and evidence

### 1.1 Repository handoff and design documents

- Read `docs/PROJECT_SESSION_HANDOFF.md` from main before review. It identifies Revision 8 as the candidate review baseline and says B-01..B-20 remain OPEN.
- Read `docs/T0_ACTIVE_SCOPE_INDEX.md`.
- Read the complete Revision 8 design at its exact pinned commit/blob.
- Read `docs/reviews/T0_PHASE_B_DESIGN_SELF_REVIEW_ROUND_8_2026-11-22.md` at its exact pinned commit/blob.
- Read the referenced Source Domain Inventory v1 on main. Its current header states **DESIGN PROPOSAL — OWNER REVIEW REQUIRED**, not an owner-approved canonical contract.
- Read the Phase A detailed design and the pinned T1 `docs/SCHEMA.md` content. T1 schema blob: `895f87a8281a3f9b6d37d96b5f68568e4285bee6`.
- The T1 schema documents trade `timestamp_ms` as trade time; depth-diff `timestamp_ms` as event time; snapshot `timestamp_ms` as capture time; and one CSV row per snapshot level. It does not document capture ID, capture manifest, collector receive timestamp, stream epoch, or durable per-message cursor.

### 1.2 Prior automated review evidence

- PR #8 Codex review completed on exact head `1c55ef8772fb33cc51d64182217de925d1d1a45d`, with `has_any_findings=false` and `has_unresolved_findings=false`. Receipt: https://github.com/kenznguyen/btcquant-application/pull/8#issuecomment-7080835114
- That PR review request explicitly focused on B-07/P2-1/P2-2/P2-3 consistency; it is not evidence that every Phase B clause and all 20 blockers were independently assessed.
- Graphify skipped AI code review because the change was documentation-only. Static health gate PASS; formal checks and tests were not run. The review itself says tests/proofs were not run.
- No GitHub Actions workflow run was returned for the exact Revision 8 self-review head SHA.
- No independent human reviewer identity/verdict was verified.

### 1.3 External protocol cross-check

Official Binance USDⓈ-M documentation was checked for:
- Aggregate Trade Streams: `E` event time, `T` trade time, `q` quantity including RPI-involved trades, and `nq` normal quantity excluding RPI-involved trades: https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/market
- Diff Book Depth Streams: separate `E` event time and `T` transaction time, plus `U/u/pu` sequence fields: https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/public
- RPI Diff Book Depth is a separate stream from ordinary depth: same public stream documentation above.
- REST/WS API order-book limits and `lastUpdateId`: https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-api/market-data

These sources support the design's distinction between event and transaction/trade times, its `q`/`nq` concern, bounded-depth wording and non-RPI scope. They do not prove the behavior of the pinned T1 collector implementation.

## 2. Findings

### R8-01 — HIGH — Canonical identity conflicts with the referenced Source Domain Inventory

**Evidence**
- Revision 8 §1 names `docs/design/T0_SOURCE_DOMAIN_INVENTORY_AND_CANONICAL_INGESTION_CONTRACT_V1_2026-11-22.md` as the “Governing design”.
- That Inventory's status is **DESIGN PROPOSAL — OWNER REVIEW REQUIRED**.
- Inventory §3 and §5.2 describe SD-06 identity with `stream_epoch` included alongside exchange/market/symbol/update range.
- Revision 8 §4.3 explicitly says `stream_epoch` is capture/session provenance only and is not part of canonical identity.
- Inventory §3 and §5.2 describe SD-07 snapshot group identity using exchange/market/symbol/`last_update_id`/snapshot event type.
- Revision 8 §5.2 and B-07 define the only SD-07 capture identity as T1-issued `(capture_producer_id, capture_sequence)`; the other fields are immutable attributes, not identity dimensions.

**Impact**

The two documents currently present different canonical uniqueness models while one is called the governing design by the other. An implementer could derive different unique constraints, replay behavior and cross-reconnect deduplication from the two documents. The problem is not resolved by saying that Revision 8 is more detailed; the authority and supersession relationship are not recorded, and the referenced Inventory has not been owner-approved as a frozen contract.

**Required correction**
1. Explicitly identify the Inventory as a non-binding proposal/reference, or publish a versioned successor/owner-approved amendment that aligns SD-06 and SD-07 identity rules.
2. Record the exact supersession mapping: SD-06 excludes `stream_epoch` from canonical identity but retains it for continuity provenance; SD-07 uses only the producer pair as capture identity, with the native anchor and source-kind fields as immutable attributes.
3. Do not freeze either identity scheme until the owner-approved governing document and Phase B agree.

**Disposition:** OPEN — contract-freeze blocker.

### R8-02 — MEDIUM — Revision 8 source file still labels itself Revision 7

**Evidence**
- The exact Revision 8 design commit/blob has a header stating “revision 7”, a status stating “PHASE B DESIGN REVISION 7 … SELF-CHECK PENDING”, and §11 says “Next review requested (revision 7)”.
- The separate self-review file identifies the same design commit/blob as Revision 8 and says its self-check is PASS.

**Impact**

The content SHA is traceable, but the document's own release/status metadata points to a different revision and review state. This creates avoidable ambiguity when later reviewers, automation or implementation plans cite “Revision 8”.

**Required correction**
- Update the design header/status and current next-review wording to Revision 8 and the actual review state.
- Preserve historical Revision 7 correction descriptions where they explain the origin of P2-1/P2-2/P2-3; do not rewrite immutable Revision 7 artifacts.
- Add a static check that the document revision, self-review revision, commit and blob references agree.

**Disposition:** OPEN — required documentation correction.

### R8-03 — MEDIUM — SD-06 proposed test matrix does not explicitly test non-identical overlapping update ranges

**Evidence**
- Revision 8 §4.3 states that overlapping but non-identical ranges are not automatically duplicates and must be handled under verified exchange sequence rules.
- The SD-06 28-case matrix includes same-range replay/conflict, gaps, bridge/pu continuity, epoch cases and resource failures, but does not state a dedicated expected outcome for non-identical overlapping ranges.

**Impact**

Overlap is a distinct sequence condition from exact duplicate range, missing range or regression. Without a deterministic synthetic case, the proposed contract-test plan does not demonstrate that the implementation will distinguish valid exchange-defined overlap from ambiguous/conflicting overlap without advancing the book watermark incorrectly.

**Required correction**
- Add synthetic cases for (a) a non-identical overlap that is valid under the pinned USDⓈ-M protocol, if one exists; (b) an overlap that cannot be proven valid; and (c) same/overlapping ranges with changed payload.
- Assert source observation retention, canonical event outcome, book availability and watermark behavior separately.
- Keep these cases NOT EXECUTED until implementation and a separate test authorization exist.

**Disposition:** OPEN — test-design coverage correction; B-05 remains open.

### R8-04 — MEDIUM — Producer namespace uniqueness scope and registration lifecycle are not operationally bounded

**Evidence**
- Revision 8 §5.2 describes a “globally governed producer namespace” and requires uniqueness, fencing and non-reuse.
- The same section says the trust root, provisioning, allocator, fencing protocol, restore epoch and proof format are NOT SPECIFIED/FROZEN.
- The candidate registry lists producer identity, collector/repository, source kind, scope, implementation/version and registration status, but does not freeze the authority and lifecycle for namespace creation, environment/restore scope, revocation, transfer or retirement.

**Impact**

The pair-only identity rule is correct only if the namespace uniqueness claim has a precise scope and authority. “Global” could otherwise be interpreted differently across T0 environments, backups/restores, cloned T1 processes or future producer versions. A registry string alone cannot establish that uniqueness.

**Required correction**
- Specify the namespace authority and uniqueness scope (including all environments/writers that can feed the same canonical identity domain).
- Specify registration lifecycle and immutable producer identity across upgrade, retirement, revocation, backup/restore and replacement.
- Bind fencing and allocator proof to that scope; an asserted boolean or registry row is not evidence.

**Disposition:** OPEN — B-07 remains open; this finding makes the missing proof boundary explicit.

## 3. Full contract assessment

### SD-05 — Aggregate trades

**Strengths**
- Separates Binance event time `E` from trade time `T`.
- Does not map the T1 CSV trade timestamp to event time.
- Keeps aggregate trade ID as candidate identity; does not substitute timestamp/price/quantity similarity.
- Treats `quantity` to native `q` as unverified and refuses to derive `nq`.
- Preserves the distinction between native ID, raw source evidence and T0 delivery locator.

**Remaining blockers**
- Pinned T1 parser/source mapping is not verified.
- T1 CSV has no separate `E` or `nq`; the `quantity` to `q` mapping is not proven.
- `side` is described by T1 as aggressor side, but its exact derivation/relationship to `is_buyer_maker` must be verified.
- Numeric bounds/precision, first/last underlying trade ID semantics and parser behavior remain open.

**Assessment:** conceptually sound and fail-closed; B-01, B-02, B-03, B-15 and B-17 remain open.

### SD-06 — Depth diffs

**Strengths**
- Separates `E`, `T`, collector receive time and T0 receipt/commit time.
- Retains U/u/pu and does not treat timestamp as sequence.
- Explicitly excludes `stream_epoch` from canonical identity while retaining it as continuity provenance.
- Separates source-delivery cursor from book-sequence watermark.
- Defines bounded reorder/gap/resource handling and fail-closed book unavailability.
- Explicitly states ordinary depth is non-RPI and RPI-inclusive data needs a separate contract.

**Remaining blockers**
- T1 CSV omits native `T`, collector receive time, stream epoch and original raw message completeness.
- The uniqueness scope for update-range identity and exact bridge/continuity rules are not proven against pinned T1 source and Binance USDⓈ-M semantics.
- Overlap test coverage needs the addition in R8-03.
- Resource limits and persistence/acknowledgement atomicity are not frozen.

**Assessment:** sound logical separation, but not acceptance-ready; B-04, B-05, B-06, B-14, B-15, B-16, B-19 and B-20 remain open or need bounded-exclusion decision.

### SD-07 — Snapshots

**Strengths**
- Separates exchange-native `lastUpdateId`, producer capture identity and T0 delivery locator.
- Correctly states that `lastUpdateId` is an anchor, not a unique acquisition ID.
- Explicitly separates direct REST response and T1 reconstructed-local-book source kinds.
- Uses producer pair only as identity; changed immutable attributes become conflict/quarantine.
- Requires verifiable producer origin and independently verifiable uniqueness/fencing/non-reuse.
- Defines bounded-depth completeness and explicit non-RPI visibility; prevents claims of full-book completeness.
- Requires group completeness evidence and rejects partial groups.

**Remaining blockers**
- Current T1 CSV does not identify source kind, capture identity, completion manifest, raw response digest or group completion.
- Producer attestation/trusted handoff, trust root, registration lifecycle, allocator, single-writer fencing and rollback protection are not specified or proven.
- Snapshot group completeness, source object finalization and stable group locator are not present in the published CSV contract.
- Snapshot-to-stream epoch linkage and local-book continuity proof remain unverified.

**Assessment:** Revision 8 correctly fixes the pair-only identity wording in B-07, but the capture is intentionally not canonically acceptable until the required evidence exists; B-07, B-08, B-09, B-10 and B-18 remain open.

### Common envelope, provenance, acceptance and recovery

- The design correctly distinguishes raw-object digest from canonical semantic digest.
- It avoids freezing a wire DTO or digest preimage prematurely.
- It separates intake outcome from book progress and defines lost-ack retry using the same immutable source-delivery locator.
- It prohibits destructive acknowledgement and source evidence deletion.
- It keeps T1 as source-capture owner and T0 as canonical owner.

Still missing before freeze:
- exact envelope/DTO and schema versioning;
- digest framing and decimal canonicalization;
- physical or formally sufficient atomic recovery protocol for canonical row, provenance, identity outcome and source cursor;
- non-candle read/API and dataset-version compatibility contract;
- immutable file/object boundary and stable capture-group locator;
- exact numeric/resource ceilings.

## 4. Blocker-by-blocker disposition

No blocker is closed by this review. Recommended state after this round:

| Blocker | Review disposition | Reason / next evidence |
|---|---|---|
| B-01 | OPEN | Inspect pinned T1 aggTrade parser/source; prove field mapping and build behavior. |
| B-02 | OPEN | Verify aggregate ID and first/last trade-ID semantics and integer bounds. |
| B-03 | OPEN | Verify aggressor-side derivation and maker-flag semantics. |
| B-04 | OPEN | Add/prove immutable stream epoch provenance and lifecycle. |
| B-05 | OPEN | Pin Binance USDⓈ-M bridge/continuity rules; prove update-range uniqueness scope; add overlap tests. |
| B-06 | OPEN | Prove raw depth message completeness and collector receive-time capture or explicitly bound exclusions. |
| B-07 | OPEN | Producer pair-only rule is clarified; origin, namespace authority, uniqueness, fencing, durable allocation and rollback proof are absent. |
| B-08 | OPEN | Add source-generated snapshot group framing, completion declaration and empty-side semantics. |
| B-09 | OPEN | Prove snapshot-to-stream epoch and anchor linkage for both source kinds. |
| B-10 | OPEN | Define finalized immutable object boundary and stable row/group locator; current CSV append/rotation is insufficient. |
| B-11 | OPEN | Freeze deterministic digest preimage, encoding and decimal normalization. |
| B-12 | OPEN | Specify atomic persistence/recovery across evidence, provenance, dedupe outcome and checkpoint before ack. |
| B-13 | OPEN | Define a separate non-candle read contract/version or obtain explicit owner-approved exclusion from this freeze. |
| B-14 | OPEN | Measure source behavior and owner-approve count/age/wait/resource ceilings. |
| B-15 | OPEN | Verify raw T1 retention for aggTrade `nq` and depth `T`; otherwise record explicit bounded unavailability. |
| B-16 | CLOSURE CANDIDATE ONLY | Phase B is explicitly non-RPI. Owner may accept RPI as a bounded exclusion, with no RPI merge or all-liquidity claims. Do not close without owner confirmation. |
| B-17 | OPEN | Verify T1 parser fidelity for trade-time mapping; `E` remains unavailable unless captured separately. |
| B-18 | OPEN | Define/prove REST/local-book manifest fields, bounded depth, digest and completion. |
| B-19 | PARTIALLY SPECIFIED / OPEN | Logical cursor/watermark semantics are clear; atomic durability, restart/replay proof and B-12 alignment remain open. |
| B-20 | OPEN | Measure and approve raw bytes, parsed levels, numeric token, reorder-buffer and snapshot-group ceilings. |

### Potential bounded exclusions for owner decision

1. **B-16 (RPI):** close only if the owner explicitly accepts Phase B as ordinary non-RPI depth only. RPI must remain a separate future source-domain design.
2. **B-13 (read API):** consider moving the non-candle read API to a separate follow-on contract, if Contract Freeze is explicitly limited to canonical ingestion and no T2 consumer/runtime is authorized. This must not silently imply API compatibility.
3. **B-17 (event time E):** a bounded exclusion of native aggTrade `E` may be considered if the owner accepts that Phase B preserves trade time `T` only and T1 parser fidelity is verified. It cannot be closed by merely assuming the CSV timestamp is correct.

These are recommendations only. No owner acceptance or blocker state change is implied.

## 5. Contract Freeze readiness gate

Contract Freeze should not be presented for approval until all of the following are true:

1. R8-01 and R8-02 are corrected in a new immutable documentation revision.
2. R8-03 test-design coverage is added.
3. R8-04 producer namespace authority/scope/lifecycle is specified or explicitly bounded.
4. The owner resolves the Inventory-vs-Phase-B identity authority conflict.
5. Every B-01..B-20 is either evidence-backed CLOSED or explicitly accepted as a bounded exclusion with owner, scope and consequence recorded.
6. The exact DTO/envelope, identity schemes, provenance fields, digest rules, snapshot manifest and cursor/checkpoint semantics are frozen together as one versioned contract.
7. Independent second-person review is completed on the resulting exact commit/blob. Model self-review or a docs-only static gate is not a substitute.

**Current recommendation: do not submit Contract Freeze for approval yet.** First prepare a new documentation-only revision that corrects the review findings and proposes bounded-exclusion decisions without changing the blocker register's owner-approved state. Then request a new full design review.

## 6. Verification and exclusions

- Review performed against exact Revision 8 commit/blob stated above.
- Manual document consistency and source-schema review: COMPLETED.
- Static checks: manual review only; no automated static-check command was run in this round.
- Tests/fixtures: NOT RUN / NOT CREATED.
- GitHub Actions workflows/artifacts: NONE verified for the exact Revision 8 head.
- Runtime, database, DDL, API, T1 collector, network, credentials, deployment, T2, trading: NOT TOUCHED.
- PR #7 and PR #8 remain review-only / DO NOT MERGE; this report does not authorize merge.
- No implementation or Contract Freeze approval is granted by this review.

## 7. Next step

Prepare Revision 9 as documentation-only: reconcile the governing Inventory identity definitions, correct Revision 8 metadata, add SD-06 overlap cases, define producer namespace authority/scope/lifecycle, and present proposed bounded-exclusion wording for B-13, B-16 and B-17. Preserve Revision 8 and earlier revisions unchanged. Keep B-01..B-20 OPEN until the owner explicitly accepts closures/exclusions.
