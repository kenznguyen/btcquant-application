# T0 Phase B Revision 9 — Full Design Review

- Review date: 2026-11-22
- Reviewed design path: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_REVISION_9_2026-11-22.md`
- Exact reviewed design commit: `5405928cf1ec61cf979453812d158caa8db18d4a`
- Exact reviewed design blob: `86c490be08961b02d03ba0a7986befe3e142b9df`
- Immutable Revision 8 source: commit `9a5c65f3bc00876d98a070eee46072c5d8be368e`, blob `8f40248f2781cdf4111ef022b77843acea8279b2`
- Revision 9 self-review: `docs/reviews/T0_PHASE_B_DESIGN_SELF_REVIEW_REVISION_9_2026-11-22.md`, commit `d29d0d636a90cb22be5e23fcf15ebf408e1907db`, blob `f5f4acb4e198e5ec8ce95550eb0014993aa4128b`
- Scope: full review of SD-05, SD-06, SD-07, common provenance/identity/acceptance/checkpoint rules, synthetic matrix, B-01..B-20, R8-01..R8-04 remediation and proposed bounded exclusions.
- Review type: full documentation design review and source-document cross-check. Not a verified independent human review.

## Verdict

**PASS WITH CONDITIONS — REVISION 9 IS READY FOR OWNER REVIEW, NOT READY FOR CONTRACT FREEZE.**

No new material document-level findings were identified in this full review. The four Revision 8 findings are addressed in the Revision 9 document. Their underlying evidence and owner-decision dependencies remain explicit and open. This verdict is not an owner approval, contract freeze, implementation authorization or proof that T1 producer mechanisms exist.

## 1. R8 finding closure assessment

| Finding | Revision 9 disposition | Result |
|---|---|---|
| R8-01 HIGH — Source Domain Inventory identity conflict | Inventory is explicitly classified as a non-binding design proposal/reference. Revision 9 provides a bounded supersession map: SD-06 identity excludes stream_epoch; SD-07 capture identity is only `(capture_producer_id, capture_sequence)`. Owner must approve supersession or an aligned Inventory amendment before freeze. | **ADDRESSED AT DOCUMENT LEVEL**; owner approval pending |
| R8-02 MEDIUM — stale Revision 7 metadata | Header, status, immutable source baseline and next-review request consistently identify Revision 9. Historical Revision 7 references remain only where explaining prior P2 corrections. | **ADDRESSED** |
| R8-03 MEDIUM — missing SD-06 overlap cases | New §4.3.1 defines protocol-gated overlap adjudication. SD-06 cases 29–31 cover a protocol-valid candidate, unproven/invalid overlap and changed-payload conflict. | **ADDRESSED IN TEST DESIGN**; NOT EXECUTED |
| R8-04 MEDIUM — producer namespace authority/scope/lifecycle | §5.2 assigns namespace registry/producer-ID allocation to T0, sequence issuance to T1, and defines identity-domain scope, single-writer fencing, upgrades, replacement, retirement, revocation and backup/restore/rollback requirements. | **ADDRESSED AS CANDIDATE POLICY**; proof mechanisms remain unfrozen |

## 2. Full contract review

### SD-05 — Aggregate trades

- E and T remain distinct; current CSV timestamp is only a candidate for T, never E.
- q mapping remains unverified; nq is not derived from q.
- Aggregate trade ID remains the candidate native identity; no timestamp/price/quantity substitute.
- Aggressor side and buyer-maker flag remain separate until source semantics and parser mapping are verified.
- No field mapping has been incorrectly promoted to verified by Revision 9.
- Outstanding: B-01, B-02, B-03, B-15 and B-17. B-17 has a bounded-exclusion proposal, but requires exact pinned T1 parser evidence and owner acceptance.

**Assessment:** coherent and fail-closed; evidence-dependent, not acceptance-ready.

### SD-06 — Depth diffs

- Candidate identity remains `(exchange, market_type, symbol, first_update_id, final_update_id)`, conditional on exchange namespace uniqueness proof.
- stream_epoch remains continuity/capture provenance only and is not added to canonical identity.
- U/u/pu, E/T, receive time, T0 receipt/commit time and source-delivery cursor remain separate concepts.
- Non-identical overlap is neither auto-deduplicated nor auto-accepted. Application requires the pinned exchange protocol and verified T1 behavior to prove the predecessor/bridge conditions; otherwise durable quarantine and no book-watermark advancement.
- Cases 29–31 are consistent with this conditional policy and do not assert that a valid overlap pattern has already been observed.
- Ordinary depth remains non-RPI; no all-liquidity claim.
- Outstanding: B-04, B-05, B-06, B-14, B-15, B-19 and B-20. B-16 has a proposed bounded exclusion.

**Assessment:** internally coherent at design level; protocol, T1 provenance, resource limits and persistence proof remain blockers.

### SD-07 — Snapshots

- Capture identity is exactly `(capture_producer_id, capture_sequence)`; native anchor, source kind, symbol/market, timestamps, request parameters, versions and digest are immutable attributes.
- T0 registry owns producer-ID allocation and registration/scope/revocation; T1 issues sequence values inside its authorized namespace.
- Namespace uniqueness covers every writer/environment/restore lineage that can feed the same canonical SD-07 identity domain.
- At most one active allocator per producer ID; clone/stale restore/rollback must be fenced.
- Retired/revoked producer IDs are never recycled or reassigned.
- Origin attestation/trusted handoff, trust root, allocator, fencing primitive and independent verifier remain unspecified/unproven; captures remain quarantined until evidence exists.
- Direct REST and reconstructed-local-book remain separate T1 source kinds with different completeness evidence.
- Outstanding: B-07, B-08, B-09, B-10 and B-18.

**Assessment:** identity and governance policy are clearer; implementation/proof intentionally remains blocked.

### Common envelope, provenance, replay and recovery

- Raw object digest and canonical semantic digest remain distinct.
- Source-delivery locator, exchange event identity, snapshot capture identity, source cursor and book watermark remain separate.
- Lost-ack retry reuses the same immutable source-delivery locator; no delete-on-ack.
- Cursor/watermark definitions are logically distinct, but atomic persistence/recovery remains unfrozen.
- Exact DTO/schema version, digest preimage, decimal canonicalization, atomicity and resource ceilings remain unfrozen.
- Outstanding: B-11, B-12, B-13, B-19 and B-20.

**Assessment:** no new internal contradiction found; freeze blockers remain substantive.

## 3. B-01..B-20 register integrity

The Revision 9 blocker table contains all 20 unique blocker IDs. B-13, B-16 and B-17 each appear again in the separate proposal table; this is deliberate duplication for owner decision clarity, not a missing/renumbered blocker.

- B-01..B-20 remain **OPEN** in the blocker register.
- B-19 remains partially specified but OPEN because atomic persistence/restart/replay proof is absent.
- No blocker is closed by this review.

### Conditional bounded-exclusion proposals

| Blocker | Proposal | Conditions before closure | Consequence |
|---|---|---|---|
| B-13 | Exclude non-candle read API/dataset-version compatibility from this Phase B ingestion freeze; track as a separate read-contract design. | Explicit owner approval of ingestion-only Phase B boundary and separate tracking; no implied API/T2/runtime compatibility. | No microstructure read API, T2 access, DTO compatibility or runtime connection is authorized by the freeze. |
| B-16 | Accept ordinary non-RPI depth only; exclude RPI-inclusive depth. | Explicit owner acceptance that the dataset is not all displayed liquidity and RPI needs separate design/review. | No RPI capture/merge or all-liquidity claims. |
| B-17 | Accept verified native trade time T only; exclude event time E for the current CSV-backed contract. | Exact pinned T1 parser/source proof that timestamp_ms maps to T, followed by explicit owner acceptance that E is unavailable/out of scope. | No event-time/latency analysis may use timestamp_ms as E; no receive-time substitution. |

All three remain OPEN pending these conditions. The review does not accept any exclusion on the owner's behalf.

## 4. Static consistency verification

- Exact Revision 9 design fetched at commit `5405928cf1ec61cf979453812d158caa8db18d4a`; blob verified as `86c490be08961b02d03ba0a7986befe3e142b9df`.
- Revision 8 source commit/blob references match the preserved baseline.
- Source Domain Inventory current status remains DESIGN PROPOSAL — OWNER REVIEW REQUIRED; Revision 9 accurately does not claim it is owner-approved.
- Revision 9 header/status no longer carries stale Revision 7 metadata.
- Matrix arithmetic independently counted: SD-05 14, SD-06 31, SD-07 46, cross-domain 10; total 101.
- Blocker IDs independently counted: 20 unique IDs, B-01 through B-20 present. Extra rows for B-13/B-16/B-17 belong to the conditional proposal table.
- Self-review references the final design commit/blob.
- T1 docs/SCHEMA.md fetched from main; blob matches the pinned schema SHA `895f87a8281a3f9b6d37d96b5f68568e4285bee6`.
- GitHub Actions workflow runs for the exact design SHA: none returned.

## 5. Evidence and limitations

- Manual full-document review and deterministic structure/count checks: COMPLETED.
- Revision 9 self-check: PASS; not independent review.
- Tests/fixtures: NOT RUN / NOT CREATED.
- Synthetic 101-case matrix: DESIGN ONLY / NOT EXECUTED.
- Workflow/artifacts: NONE verified for the exact design SHA.
- Independent human reviewer identity/verdict: NOT VERIFIED.
- T1 parser/source runtime behavior, producer attestation, allocator/fencing, persistence atomicity, resource measurements and actual source captures: NOT VERIFIED.
- No code, DTO, parser, validator, test, fixture, database, DDL, API, T1 runtime, T0 runtime, deployment, T2 or trading action was performed.

## 6. Recommendation

Revision 9 may proceed to **owner review of the candidate design and the three bounded-exclusion proposals**. Do not present Contract Freeze for approval yet. Before freeze, record the owner's decision on the Inventory supersession and B-13/B-16/B-17, obtain the required T1/protocol/provenance/persistence evidence, resolve the remaining B-01..B-20 blockers or explicitly accept bounded exclusions, and obtain independent second-person review on the exact approved source SHA/blob.

PR #7 and PR #8 remain historical review-only / DO NOT MERGE. This report does not authorize merging them or implementing any part of Phase B.
