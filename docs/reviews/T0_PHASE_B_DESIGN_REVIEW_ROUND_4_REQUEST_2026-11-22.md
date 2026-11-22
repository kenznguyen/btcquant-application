# T0 Phase B Design — Revision 4 Review Request

- Date: 2026-11-22
- Review type requested: design review of exact revision 4 documentation baseline
- Design: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`
- Exact design commit: `f4ab46715657675d15c907faeff8aa545c7cb161`
- Exact design blob SHA: `90bdb1495770f977cb3ef1d307b28189a2478c2c`
- Prior review: `docs/reviews/T0_PHASE_B_DESIGN_REVIEW_ROUND_3_2026-11-22.md`, commit `01b8e3aa32bb71cb48ef2f2d501eab7aa2869ea1`.
- Revision 4 self-review: `docs/reviews/T0_PHASE_B_DESIGN_SELF_REVIEW_ROUND_4_2026-11-22.md`, commit `5aee1497404232fbe7d249c403ab6fa342ba9c3a`.
- Status: **REQUESTED / PENDING**.
- Implementation: **NOT AUTHORIZED / NOT STARTED**.
- Synthetic matrix: **74 CASES DESIGNED / NOT EXECUTED**.
- Workflows/artifacts: **NOT RUN / NONE**.

## 1. Revision 4 scope

Documentation-only corrections for:
- R-12: distinguish direct Binance USD-M REST depth responses from T1 locally reconstructed snapshots using separate source-kind-specific completeness contracts.
- R-13: remove “full-state anchor”; define snapshot only as a bounded/source-scoped anchor.
- R-14: separate immutable source-delivery retry locator from verified native event identity; stream epoch remains continuity provenance only.

## 2. Finding dispositions

| Finding | Revision 4 change | Residual limits |
|---|---|---|
| R-12 | Allowlist candidate source kinds `BINANCE_USDM_REST_DEPTH_RESPONSE_V1`, `T1_RECONSTRUCTED_LOCAL_BOOK_V1`; unknown kinds fail closed. Define independent REST and reconstructed-local-book manifests and acceptance proofs. | Current T1 CSV does not identify source kind or provide required completeness evidence; B-07/B-08/B-09/B-10/B-18 remain open. |
| R-13 | Replace full-state terminology with bounded snapshot anchor for returned/declared retained depth scope. | Derived-book top-N semantics remain bounded and source-evidence dependent. |
| R-14 | Retry source observation by immutable source-delivery locator; canonical dedupe by verified exchange namespace/native update range. Epoch excluded from both identities. | Update-ID uniqueness, source locator and epoch evidence remain open under B-04/B-05/B-06. |

## 3. Synthetic test matrix

- SD-05 aggregate trades: 14.
- SD-06 depth diffs: 28.
- SD-07 bounded snapshots: 24.
- Cross-domain cursor/checkpoint/recovery: 8.
- Total: **74 proposed cases**.
- Status: **DESIGNED ONLY / NOT EXECUTED**.
- New SD-06 cases cover missing epoch provenance, same native event replay across epochs and restart retry with changed process/session epoch.
- New SD-07 cases cover REST-specific evidence, reconstructed-local-book continuity proof, source-kind mismatch, unknown source kind and snapshots whose source history contains an unresolved gap.

## 4. Blockers

**B-01 through B-20 are intentionally preserved unchanged.** None is marked resolved, removed or owner-accepted. Reviewers should verify that the revision does not imply source evidence, numeric limits, protocol bridge, digest serialization, atomic persistence or API compatibility have been proven.

## 5. Reviewer checklist

1. Are REST response and locally reconstructed T1 snapshot source kinds sufficiently distinct?
2. Does each source-kind completeness contract require the right evidence without conflating REST response metadata with local reconstruction state?
3. Is the current T1 CSV correctly blocked because `event_type` does not prove source kind?
4. Is “bounded snapshot anchor” terminology consistent across sections and derived-book semantics?
5. Are source-delivery retry identity, canonical event identity and stream epoch/continuity provenance correctly separated?
6. Do the new synthetic cases expose false completeness, cross-kind metadata confusion, unresolved local-book gaps and epoch-related duplicate application?
7. Are all 74 proposed cases clearly design-only and NOT EXECUTED?
8. Are B-01..B-20 retained without unsupported closure?
9. Are all previous findings R-01..R-11 still accurately dispositioned and their residual evidence blockers retained?

## 6. Explicit exclusions

No code, DTO, parser, validator, adapter, fixtures, tests, workflows, DDL, database, data movement, network/exchange calls, credentials, T1 source/runtime changes, T1→T0/T2 connection, VPS/deployment, source deletion, Phase C, order submission or trading action is authorized.

T0 remains the sole canonical owner. T1 implementation remains in its own repository. Preserve raw source evidence. No delete-on-ack. Paper-first/no-live-trading guardrails remain unchanged.
