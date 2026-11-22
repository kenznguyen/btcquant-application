# Owner Decision — Approve 101 Isolated T0 Phase B Synthetic Cases

- Decision date: 2026-11-22
- Decision: **APPROVED — BOUNDED SYNTHETIC TEST SCOPE**
- Approver: project owner (explicit approval in project conversation)
- Governing consolidated candidate: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_REVISION_11_2026-11-22.md`
- Revision 11 source commit at approval record: `0ac119c7cd31ba63d5aead6796c7b5560abf2a18`
- Revision 11 document blob: `9d9639b4d26b42a90929f50a32b801e359b23197`
- Immutable source baselines: Revision 10 commit/blob `b32d9af088099f92b09d113ecfa27056cfd9b83d` / `a8934cb862c330f1d1fa72aa1f3fdb2b22f9ac96`; DTO proposal blob `594066d98201a8cf0940b62fc36d9358033f06e0`.

## Approved scope

Owner explicitly approves creation of isolated, test-only synthetic fixtures/DTO-validator-persistence harness and execution of the existing 101-case matrix:

| Domain | Approved cases |
|---|---:|
| SD-05 aggregate trades | 14 |
| SD-06 depth diffs | 31 |
| SD-07 snapshots | 46 |
| Cross-domain persistence/recovery | 10 |
| **Total** | **101** |

Expected outcomes must remain unchanged unless a defect is documented and brought back for owner review. Failures must be retained as evidence; tests must not be weakened or removed to manufacture PASS.

## Execution boundary and sequencing

1. Review the exact Revision 11 commit/blob independently before creating fixtures or executing the matrix. This sequencing preserves the user's requested order: consolidate Revision 10, then request independent review on the new SHA.
2. After the independent review is recorded, implement only disposable synthetic fixtures and test-only validators/persistence harness needed to exercise the 101 cases. No production runtime implementation is authorized.
3. Use no production market data, credentials, exchange connectivity, T1/T0 runtime, VPS, mounted canonical database, or private source evidence.
4. Do not modify the T1 collector repository or connect T1 to T0/T2.
5. Do not create or mutate production DDL/database; no import, promotion, cutover, migration, or data movement.
6. Do not enable order execution, submit orders, or change strategy/runtime.
7. Do not delete source evidence or implement delete-on-ack.
8. Record exact source SHA/blob, test command, case counts, per-case failures, workflow run/job IDs, artifact IDs and logs. If CI is not run or an artifact is unavailable, state that explicitly.

## Approval does not authorize

- Contract Freeze or production DTO/parser/validator/persistence implementation.
- Production schema/DDL/database changes, canonical data writes, import or migration.
- T1 source changes, collector activation, T1→T0 or T1→T2 runtime connection.
- T2 integration, VPS deployment, autostart/systemd, or live trading.

## Current status at decision recording

- Approval: **APPROVED**.
- Revision 11: consolidated candidate; exact commit/blob above.
- Independent second-person review: **NOT YET REQUESTED**.
- Fixtures/tests: **NOT CREATED / NOT RUN**.
- Workflow run/job/artifact: **NONE**.
- Contract Freeze: **NOT APPROVED**.
- Production implementation/runtime: **NOT AUTHORIZED**.

## Next step

Request independent review of the exact Revision 11 source commit/blob above. After review findings are resolved and recorded, proceed with the approved isolated 101-case test scope under these restrictions.


---

## Sequencing amendment after Revision 11 review — 2026-11-22

The original 101-case owner approval remains in force and the approved case counts/scope are unchanged. PR #9 completed Codex review with three P2 findings. Revision 12 addresses those findings and is now the current review candidate.

- Revision 11 reviewed target: `0ac119c7cd31ba63d5aead6796c7b5560abf2a18` / `9d9639b4d26b42a90929f50a32b801e359b23197`.
- Revision 11 review findings record: `docs/reviews/T0_PHASE_B_REVISION_11_CODEX_REVIEW_FINDINGS_2026-11-22.md`.
- Current candidate Revision 12: `docs/design/T0_PHASE_B_DETAILED_SCHEMA_AND_CANONICAL_CONTRACT_DESIGN_REVISION_12_2026-11-22.md`, source commit `29c47fcf9a761af00f72c043142ac2cca7b708ab`, blob `0c726fc05e76c41986130f8ee165d3dc67ce7044`.
- Follow-up independent re-review: [PR #10](https://github.com/kenznguyen/btcquant-application/pull/10), OPEN / NOT MERGED; Codex review status RUNNING at amendment time.
- Fixture creation and execution are now sequenced after a satisfactory independent review of exact Revision 12 SHA/blob, not the superseded Revision 11 SHA/blob.
- The 101-case approval remains valid. No additional owner approval is required merely to proceed with the same bounded synthetic-only test scope after the review gate is satisfied. Any scope expansion still requires separate approval.
- Tests/fixtures remain NOT CREATED / NOT RUN. Contract Freeze remains NOT APPROVED; production implementation/runtime remains NOT AUTHORIZED.
