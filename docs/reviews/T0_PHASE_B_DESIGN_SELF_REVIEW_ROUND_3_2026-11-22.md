# T0 Phase B — Revision 3 Self-Review

- Date: 2026-11-22
- Reviewed design commit: `98cde283e9b2dc2d0201e4359e3f1195016ff0ea`
- Reviewed design blob: `2e61e13ec8dc42a37ea03130edc1491b73a903bc`
- Prior design commit: `75e593517ec31d2e2a75ed0050e80ab5dd52edf2`
- Review type: author self-review; **not an independent second-person review**.
- Scope: documentation-only review of R-01..R-11 closure, Phase B mapping/identity, bounded snapshot semantics, cursors, resource limits and synthetic matrix.
- Verdict: **READY TO SUBMIT FOR INDEPENDENT DESIGN REVIEW — CONTRACT FREEZE NOT APPROVED**.

## 1. Findings disposition

| Finding | Revision 3 disposition | Remaining blocker |
|---|---|---|
| R-01 — canonical identity vs stream epoch | **DESIGN GAP CLOSED; ACCEPTANCE BLOCKED**. Stream epoch remains provenance/continuity only; canonical update-range candidate excludes it; cross-epoch replay/conflict behavior retained. | B-05: prove update-ID uniqueness scope across reconnects/restarts. Until then quarantine cross-epoch identity and do not canonically accept SD-06. |
| R-02 — snapshot capture identity/completeness | **DESIGN GAP CLOSED; SOURCE CONTRACT BLOCKED**. Capture ID, framing, expected count, finalized digest and manifest are required; manifest now binds endpoint/source kind, limit, bid/ask/total counts, capture identity and completion. | B-07/B-08/B-10/B-18: current T1 CSV lacks these fields/proofs; no snapshot from that schema version is canonically acceptable. |
| R-03 — aggTrade q/nq | **DESIGN GAP CLOSED; MAPPING UNVERIFIED**. q/nq are separate; nq is never derived; CSV quantity→q consistently marked candidate/NOT VERIFIED. | B-01/B-15/B-17: inspect pinned T1 parser/source and decide raw-only vs versioned canonical nq. |
| R-04 — RPI depth scope | **ADDRESSED WITH EXPLICIT LIMITATION**. SD-06/SD-07 are ordinary non-RPI only; no claim of all displayed liquidity. | B-16: any RPI source/merge remains separately scoped and out of Phase B. |
| R-05 — event/transaction clocks | **DESIGN GAP CLOSED; SOURCE FIDELITY BLOCKED**. SD-05 E=event time, T=trade time; CSV timestamp is candidate T only, E unavailable. SD-06 E/T separate, current CSV T unavailable. SD-07 optional REST E/T separate from CSV capture time; preserve if captured, otherwise unavailable. | B-06/B-15/B-17: verify exact T1/raw-source retention and source variant. |
| R-06 — reordering/gaps/checkpoints | **DESIGN GAP CLOSED; NUMERIC/TRANSACTION FREEZE BLOCKED**. Count, age, bytes, levels, token/precision and snapshot group limits defined as independent categories; gap recovery is fail-closed. | B-12/B-14/B-19/B-20: numeric values, atomic persistence and measured limits remain open. |
| R-07 — aggTrade E/T reversed | **ADDRESSED**. E is event time; T is trade time; CSV timestamp_ms is candidate T, never E; missing E is unavailable. | Source/parser fidelity remains unverified. |
| R-08 — snapshot full-depth overclaim | **ADDRESSED**. Complete means all rows in the exact bounded response; manifest binds endpoint/source, requested limit, returned bid/ask counts, total rows, digest and non-RPI scope. Derived book remains bounded and cannot claim unseen levels/full-book ranking. | Source-generated manifest and endpoint behavior remain unimplemented/unverified. |
| R-09 — source cursor vs book watermark | **ADDRESSED**. Separate source-delivery/import cursor and contiguous book-sequence watermark, including restart/replay and quarantine acknowledgement semantics. | B-12 physical atomicity/recovery protocol remains unfrozen. |
| R-10 — resource limits | **ADDRESSED AT DESIGN LEVEL**. Independent raw bytes, levels, numeric token/precision, buffer bytes, snapshot rows/bytes and parser-structure ceilings added; fail-closed bounded rejection defined. | Numeric ceilings require measurement and owner approval; no tests executed. |
| R-11 — q mapping inconsistency | **ADDRESSED**. All CSV quantity→q references consistently state candidate/NOT VERIFIED; no assertion that the published CSV schema proves native q. | Same source verification dependency as R-03. |

## 2. Five-axis self-review

| Axis | Result | Assessment |
|---|---|---|
| Correctness | **PASS WITH OPEN CONTRACT BLOCKERS** | E/T mapping corrected; snapshot scope bounded; cursor semantics separated; no fabricated source fields. |
| Readability/consistency | **PASS** | Candidate vs verified mappings are explicitly distinguished; matrix counts reconcile to 66. |
| Architecture | **PASS WITH OPEN EVIDENCE** | T0 remains canonical owner; T1 remains source collector; source history and derived book remain distinct. |
| Security/robustness | **PASS AT DESIGN LEVEL** | Untrusted input is bounded before/while parsing; oversized observations fail closed with bounded evidence references. |
| Performance/resource safety | **PARTIAL** | Resource dimensions are specified, but numeric ceilings and empirical source measurements remain unresolved. |

## 3. Synthetic matrix

- SD-05: 14 proposed cases.
- SD-06: 25 proposed cases.
- SD-07: 19 proposed cases.
- Cross-domain cursor/checkpoint/recovery: 8 proposed cases.
- Total: **66 proposed cases**.
- Execution status: **NOT EXECUTED**. No test code, fixtures, CI workflow or artifacts were created.

## 4. Remaining blockers and exclusions

- B-01..B-20 remain open unless independently evidenced or explicitly accepted by the owner. The revision does not claim contract freeze.
- SD-06 canonical acceptance remains blocked pending update-ID uniqueness proof.
- SD-07 canonical acceptance remains blocked for the current T1 CSV version pending source-generated capture identity and completeness evidence.
- q mapping, raw E/T retention, resource numeric ceilings, digest encoding and atomic checkpoint protocol remain unfrozen.
- Independent second-person review: **NOT PERFORMED**.
- Tests/workflows/artifacts: **NOT RUN / NONE**.
- No code, DTO, parser, validator, fixtures, tests, DDL, database, data movement, T1 source/runtime, network, credentials, VPS, deployment, Phase C or trading action.

## 5. Self-review verdict

**READY TO SUBMIT FOR INDEPENDENT DESIGN REVIEW.** This is not a design approval, contract freeze or implementation authorization. The reviewer should assess the exact design commit/blob above and specifically challenge the residual B-01..B-20 evidence dependencies.
