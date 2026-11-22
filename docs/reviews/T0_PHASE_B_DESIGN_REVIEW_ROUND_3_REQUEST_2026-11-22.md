# T0 Phase B Design — Revision 3 Independent Review Request

- Date: 2026-11-22
- Review type: independent documentation/design review
- Revised design: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`
- Exact design commit: `98cde283e9b2dc2d0201e4359e3f1195016ff0ea`
- Exact design blob SHA: `2e61e13ec8dc42a37ea03130edc1491b73a903bc`
- Prior reviewed design: `75e593517ec31d2e2a75ed0050e80ab5dd52edf2`
- Prior self-review: `docs/reviews/T0_PHASE_B_DESIGN_SELF_REVIEW_ROUND_2_2026-11-22.md`, commit `2f6317b28502bc06202daf673f1f32c41f847c88`.
- Revision 3 self-review: `docs/reviews/T0_PHASE_B_DESIGN_SELF_REVIEW_ROUND_3_2026-11-22.md` (recorded separately).
- Self-review verdict: **READY TO SUBMIT FOR INDEPENDENT DESIGN REVIEW — CONTRACT FREEZE NOT APPROVED**.
- Independent second-person review: **REQUESTED / PENDING**.
- Implementation: **NOT AUTHORIZED / NOT STARTED**.
- Synthetic tests: **66 CASES DESIGNED / NOT EXECUTED**.
- Workflows/artifacts: **NOT RUN / NONE**.

## 1. Scope of revision

Documentation-only revision of SD-05 aggregate trades, SD-06 ordinary non-RPI depth diffs and SD-07 ordinary non-RPI bounded-depth snapshots. No implementation or runtime work is included.

## 2. Finding disposition

| Finding | Revision 3 correction | Residual dependency |
|---|---|---|
| R-01 | Canonical identity excludes stream_epoch; epoch is continuity/capture provenance. | Prove exchange update-ID uniqueness scope; otherwise quarantine. |
| R-02 | Capture ID, framing, expected count, digest and source-bound completion manifest; completeness is bounded-response completeness. | Current T1 CSV lacks these fields; SD-07 acceptance remains blocked. |
| R-03 | q and nq are distinct; CSV quantity→q consistently candidate/NOT VERIFIED; nq never derived. | Pinned T1 parser/source verification and nq source policy. |
| R-04 | Ordinary depth explicitly non-RPI for diffs and snapshots; no all-liquidity claim. | RPI stream/merge remains out of Phase B. |
| R-05 | SD-05 E=event time, T=trade time; CSV timestamp candidate T only. SD-06 E/T distinct; SD-07 REST E/T separate if supplied. | Verify source/raw retention; absent fields remain unavailable. |
| R-06 | Count/age/byte/level/token/group bounds, fail-closed gaps and recovery. | Numeric bounds, exchange bridge and atomic persistence remain open. |
| R-07 | Corrected aggTrade E/T mapping; timestamp_ms never maps to E. | T1 parser fidelity not verified. |
| R-08 | Snapshot completeness defined as full capture of exact bounded response; manifest binds endpoint, limit, bid/ask counts, digest and non-RPI scope; derived book remains bounded. | Source manifest and bounded-book behavior need evidence. |
| R-09 | Separate source-delivery cursor from contiguous book-sequence watermark; restart and quarantine acknowledgement semantics specified. | Physical atomicity/recovery contract remains open. |
| R-10 | Raw bytes, levels, numeric token/precision, buffer bytes, snapshot rows/bytes and parser structure are separate resource ceilings. | Numeric values require measurement and owner approval. |
| R-11 | All quantity→q mappings normalized to candidate/NOT VERIFIED. | Same source verification as R-03. |

## 3. Synthetic matrix

- SD-05: 14 cases.
- SD-06: 25 cases.
- SD-07: 19 cases.
- Cross-domain cursor/checkpoint/recovery: 8 cases.
- Total: **66 proposed cases**.
- Status: **DESIGNED ONLY / NOT EXECUTED**. No code/fixtures/tests/workflows created or run.

## 4. Remaining blockers

B-01..B-20 remain open until evidence-backed resolution or bounded owner acceptance. In particular:
- B-05: depth update-ID uniqueness namespace and bridge.
- B-07/B-08/B-10/B-18: snapshot capture identity, group completeness, immutability and bounded response manifest.
- B-01/B-15/B-17: T1 aggTrade field mapping and E/T/q/nq fidelity.
- B-12/B-19: atomic source outcome/cursor and book application/watermark persistence.
- B-14/B-20: measured and owner-approved count/age/byte/level/token/group resource limits.
- B-11: canonical digest/decimal serialization.
- B-13: separate non-candle read API/dataset-version compatibility.
- B-16: RPI visibility remains excluded.

## 5. Reviewer checklist

Please review the exact design commit/blob and assess:
1. Correctness of E/T mapping for aggTrade, depth diffs and snapshots; no time substitution.
2. Whether every unverified T1 mapping is clearly marked candidate/NOT VERIFIED.
3. Whether source-generated snapshot identity/completeness manifest sufficiently proves a complete bounded response without claiming a full book.
4. Whether bounded-depth derived-book semantics for updates outside the initial price boundary are safe and accurately described.
5. Whether source-delivery cursor and book-sequence watermark semantics avoid acknowledgement-induced sequence skips.
6. Whether the resource ceiling dimensions and fail-closed behavior bound memory/parser work without arbitrary numeric defaults.
7. Whether R-01..R-06 are genuinely closed at the design level while residual evidence dependencies remain correctly blocked.
8. Whether the 66-case matrix and B-01..B-20 blockers cover the risks without implying implementation readiness.

## 6. Explicit exclusions

No code, DTO, parser, validator, adapter, tests, fixtures, workflow, DDL, database, data movement, network/exchange calls, credentials, T1 source/runtime changes, T1→T0/T2 connectivity, VPS/deployment, source deletion, Phase C, order submission or trading action is authorized.

T0 remains the sole canonical owner; T1 implementation remains in its own repository; raw source evidence is preserved; no delete-on-ack; paper-first/no-live-trading guardrails remain unchanged.
