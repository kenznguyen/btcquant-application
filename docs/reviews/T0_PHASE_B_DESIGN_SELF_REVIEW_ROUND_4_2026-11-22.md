# T0 Phase B Revision 4 — Documentation Self-Review

- Date: 2026-11-22
- Exact design commit: `f4ab46715657675d15c907faeff8aa545c7cb161`
- Exact design blob SHA: `90bdb1495770f977cb3ef1d307b28189a2478c2c`
- Scope: documentation-only resolution of R-12, R-13, R-14 and related synthetic test design.
- Baseline reviewed: revision 3 design commit `98cde283e9b2dc2d0201e4359e3f1195016ff0ea`.
- Verification: GitHub readback and deterministic text/section consistency checks. No test code, fixtures, CI, workflow or runtime test was created or executed.

## Self-review verdict

**READY TO SUBMIT FOR NEXT DESIGN REVIEW — CONTRACT FREEZE NOT APPROVED.**

This self-review is not independent second-person review and is not owner approval.

## Finding dispositions

### R-12 — Addressed at design level; source evidence remains blocked

- Added explicit candidate source-kind allowlist:
  - `BINANCE_USDM_REST_DEPTH_RESPONSE_V1`
  - `T1_RECONSTRUCTED_LOCAL_BOOK_V1`
  - `UNSUPPORTED_OR_UNKNOWN` (reject by default).
- Direct REST contract binds exact endpoint, request limit, response anchor, E/T when supplied, counts, immutable response evidence, digest and completion.
- Reconstructed local-book contract separately binds upstream snapshot anchor, stream epoch, last contiguous applied diff, continuity state, retained-depth policy, generation, counts, digest and completion.
- Clarified that current T1 `event_type` values describe lifecycle intent and do not prove source kind.
- Current T1 CSV snapshots remain `NOT_CANONICAL_ACCEPTABLE` until source-kind and variant-specific completeness evidence exist.
- B-07, B-08, B-09, B-10 and B-18 remain unchanged and open.

### R-13 — Addressed

- Replaced “full-state anchor” with bounded/source-scoped snapshot anchor wording.
- Clarified that snapshot anchors only returned/declared retained depth; it cannot prove unseen exchange levels or full-book state.
- Aligned §5, §6, synthetic matrix and derived-book semantics.

### R-14 — Addressed

- Replaced same-epoch retry rule with immutable source-delivery locator for delivery retry and verified native exchange namespace/update range for canonical event deduplication.
- Epoch remains continuity/session provenance, not canonical identity or retry identity.
- Split missing native event identity from missing stream epoch/continuity provenance.
- Added cases for missing epoch, same native range replayed across epochs, and restart retry with changed process/session epoch.

## Synthetic matrix

- SD-05: 14 cases.
- SD-06: 28 cases.
- SD-07: 24 cases.
- Cross-domain cursor/checkpoint/recovery: 8 cases.
- Total: **74 proposed cases**.
- Status: **DESIGNED ONLY / NOT EXECUTED**.
- Added SD-06 cases 26–28 for epoch provenance, cross-epoch replay and restart retry.
- Added SD-07 cases 20–24 for direct REST source proof, reconstructed local-book continuity proof, cross-kind mismatch, unknown source kind and pre-existing unresolved gap.
- Text checks confirmed all four sections are present and the stated total is 74.

## Blocker preservation check

The complete B-01..B-20 table was compared against the exact revision 3 baseline. It is byte-identical: **20 blockers retained, none marked resolved, removed or owner-accepted**.

## Scope and quality gates

- Documentation-only changes.
- No code, DTO, parser, validator, fixtures, tests, DDL, database, data movement, T1 source/runtime, network, credentials, VPS/deployment, T1→T0/T2, Phase C or trading action.
- Tests/workflows/artifacts: **NOT RUN / NONE**.
- Independent second-person review: **PENDING**.
- Contract freeze: **NOT APPROVED**.
- Implementation/database/runtime/Phase C: **NOT AUTHORIZED**.

## Next step

Submit exact design commit/blob above for another design review. Preserve B-01..B-20 until evidence-backed resolution or explicit bounded owner acceptance.
