# T0 Phase B Revision 4 — Design Review

- Review date: 2026-11-22
- Exact reviewed design commit: `f4ab46715657675d15c907faeff8aa545c7cb161`
- Exact reviewed design blob SHA: `90bdb1495770f977cb3ef1d307b28189a2478c2c`
- Reviewed path: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_2026-11-22.md`
- Scope: exact-commit documentation review of SD-05, SD-06, SD-07, prior findings R-01..R-14, the 74-case proposed matrix and B-01..B-20 preservation.
- Method: read exact design blob; compare revision 4 dispositions with the revision 3 review; inspect relevant sections on snapshot identity/completeness, source-delivery retry, epoch provenance, cursor separation, synthetic cases and blockers.
- Tests/workflows/artifacts: NOT RUN / NONE. This is a design review, not runtime or implementation verification.

## Verdict

**REQUEST CHANGES — PHASE B REVISION 4 NOT APPROVED.**

Revision 4 materially improves R-12, R-13 and R-14, but the snapshot identity contract still contains an unresolved source-capability contradiction. A smaller terminology inconsistency also remains in the retry contract. Contract freeze is NOT APPROVED. Implementation, database, runtime and Phase C remain NOT AUTHORIZED.

## Findings

### R-15 — HIGH: REST snapshot requires a source-generated capture ID without identifying a source field or issuer

**Location:** §5.2 candidate snapshot identity; §5.3 minimum future acceptance evidence; §5.2 REST source-kind contract.

The design requires `snapshot_capture_id` to be source-generated and immutable, and includes it in the candidate snapshot identity. However, the `BINANCE_USDM_REST_DEPTH_RESPONSE_V1` contract describes a direct Binance REST depth response but does not identify a Binance-native capture-ID field in that response or name a source-side component that issues one.

This creates an unresolved acceptance contradiction:
- If the REST response does not provide a capture ID, the direct REST path cannot satisfy the stated hard gate.
- If T1 or T0 generates the ID, it is a collector/T0 capture identity, not an exchange-native/source-provided identity; the contract must say so and define its issuer, uniqueness scope, immutability and binding to the exact request/response evidence.
- A generated ID must not be mistaken for exchange-native event identity or used to conceal a missing native update anchor.

**Required correction:** distinguish at least (1) exchange-native response/event identity, (2) collector capture identity, and (3) T0 import/delivery identity. For direct REST, explicitly state whether Binance supplies an identifier; if not, define a collector-issued capture ID with a collision-safe generation scope and bind it to the exact request parameters, response anchor, immutable raw response bytes/digest and capture provenance. For reconstructed local books, define the T1-issued capture ID and bind it to the upstream snapshot anchor, stream epoch, last contiguous applied update and local-book generation. Keep the T0 delivery locator separate from both. If the required proof cannot be supplied, retain the source-kind-specific NOT_CANONICAL_ACCEPTABLE outcome.

**Synthetic coverage required:** add cases for missing/duplicate collector capture IDs, same REST response captured twice, distinct responses with colliding IDs, ID reuse across restart/process epochs, and mismatch between capture ID and immutable response evidence. The test oracle must distinguish replay of the same capture from two captures that happen to share lastUpdateId/timestamp.

### R-16 — MEDIUM: residual retry identity wording remains ambiguous

**Location:** §4.5 final bullet; compare §4.8, §8 and SD-06 synthetic case 21.

Revision 4 correctly separates the immutable source-delivery locator from canonical exchange-event identity in §4.8 and §8. However, §4.5 still says “Lost acknowledgement retries the same immutable message identity.” This phrase does not identify whether “message identity” means the source-delivery locator, the exchange-native update range, or a raw-message identifier. That ambiguity is exactly what R-14 was intended to remove.

**Required correction:** replace the phrase with the exact term “same immutable source-delivery locator” and state that canonical deduplication is independently performed by the verified native exchange namespace/update range. Align the wording in the synthetic matrix and checkpoint sections.

## Disposition of prior findings

| Finding | Review disposition |
|---|---|
| R-01 | Conceptually addressed; update-ID uniqueness namespace remains blocked by B-05 |
| R-02 | Source-kind-specific completeness is materially improved; capture identity/completeness evidence remains blocked, with R-15 added |
| R-03 | q/nq distinction retained; quantity-to-q remains NOT VERIFIED |
| R-04 | Ordinary depth remains explicitly non-RPI; RPI-inclusive depth remains out of scope |
| R-05 | E/T/receive/T0 clocks remain distinct; source fidelity remains blocked |
| R-06 | Bounded reorder/gap/recovery and fail-closed behavior retained; exact bridge and numeric limits remain blocked |
| R-07 | E=event time and T=trade time distinction retained |
| R-08 | Bounded top-N semantics retained; no full-book claim |
| R-09 | Source-delivery cursor and book-sequence watermark remain separate |
| R-10 | Byte/level/token/parser/group resource categories retained; numeric ceilings remain unfrozen |
| R-11 | q mapping remains consistently candidate/NOT VERIFIED |
| R-12 | Addressed at design level for separate REST and reconstructed-local-book contracts; R-15 exposes unresolved capture-ID issuer semantics |
| R-13 | Addressed; bounded/source-scoped snapshot anchor terminology is consistent in the inspected sections |
| R-14 | Materially addressed; R-16 identifies one remaining ambiguous phrase |

## Positive observations

- The REST and reconstructed-local-book variants now have separate candidate completeness contracts; `event_type` is not treated as proof of source kind.
- Current T1 CSV snapshots remain NOT_CANONICAL_ACCEPTABLE until source-kind and completeness evidence exist.
- Snapshot semantics consistently describe only returned/declared retained depth, not the unseen full exchange book.
- Stream epoch remains continuity/session provenance rather than canonical event identity.
- The design distinguishes source-delivery cursor from book-sequence watermark and does not equate durable quarantine acknowledgement with book continuity.
- The 74 proposed cases are clearly marked DESIGNED ONLY / NOT EXECUTED.
- B-01..B-20 remain present and open in the reviewed design; none is represented as resolved or owner-accepted.

## Blocker and scope verification

- B-01..B-20: retained; all remain open pending evidence or bounded owner acceptance.
- Synthetic matrix: 74 proposed cases (SD-05 14, SD-06 28, SD-07 24, cross-domain 8); NOT EXECUTED.
- Tests/workflows/artifacts: NOT RUN / NONE.
- Independent second-person reviewer identity: NOT VERIFIED; this review must not be represented as external second-person approval.
- Contract freeze: NOT APPROVED.
- Implementation/database/runtime/Phase C: NOT AUTHORIZED.
- Review scope is documentation-only. No code, DTO, parser, validator, fixture, test, DDL, database, data movement, T1 source/runtime, network, credentials, T1→T0/T2 runtime, VPS/deployment, source deletion or trading action occurred.

## Next step

Revise only the Phase B design and proposed synthetic matrix for R-15 and R-16. Preserve B-01..B-20 unchanged and open. Submit a new exact design commit/blob for review. Do not freeze contracts or begin implementation/Phase C before separate owner approval.
