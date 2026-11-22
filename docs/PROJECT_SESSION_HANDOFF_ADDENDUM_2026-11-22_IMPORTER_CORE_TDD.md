# Session Handoff Addendum — 2026-11-22
## Importer-Core synthetic in-memory TDD scope approval

Controlling decision: `docs/decisions/T0_IMPORTER_CORE_SYNTHETIC_TDD_SCOPE_APPROVAL_2026-11-22.md`.

- Decision commit: `89b9e41e3608f75839e7c5fae7a3a0691ee716b9`.
- Status: **OWNER-APPROVED — BOUNDED TDD IMPLEMENTATION ONLY**.
- Approved work: synthetic-only pure-Python importer-core normalization, row accounting, identical-duplicate/conflict reconciliation and explicit-grid coverage calculation, entirely in memory; focused unit tests; RED before GREEN; existing `ArchiveKlineRow` parser contract as input.
- Target branch: existing `main`; do not create a feature branch.
- The scope approval does not freeze stable provenance IDs, canonical serialization/digests, schema/DDL, database behavior or full persisted provenance contracts. Do not guess these; they remain under S1 contract/schema freeze.
- CI workflow edits/dispatch/artifact upload are not included. The approval permits source and unit-test TDD only. Record exact RED/GREEN source SHA and test evidence; if the current environment cannot execute exact-source tests, stop before claiming RED/GREEN or committing unverified behavior.
- No archive/sidecar access, network, filesystem/host preflight, SQLite, real-data importer, staging, Canonical T0/MAY-10, T1/T2, VPS/runtime/deployment, credentials, exchange connectivity, trading, deletion or cleanup.
- B3 real archive format and B5 source-derived coverage remain NOT VERIFIED. B8 SQLite/importer build remains NOT AUTHORIZED.

### Execution checkpoint — BLOCKED BEFORE RED

- Read-only inventory and capability checkpoint: `docs/evidence/T0_IMPORTER_CORE_TDD_EXECUTION_CHECKPOINT_2026-11-22.md`, commit `8368122a8b7f9daaee368e9323b0684c9bf49371`.
- Inspected `main` HEAD before the checkpoint: `e64a5526db0f1aaaf51cf634fb43092ddec3526f`. The checkpoint itself is the latest documentation-only commit; verify live HEAD before any subsequent work.
- Existing parser and B4 modules/tests were inspected. Importer-core source and focused tests are absent.
- No local checkout is mounted, and the available GitHub connection has no workflow dispatch or code-execution action. Consequently no exact-SHA RED could be run. No importer tests or implementation were committed; no tests/workflow were run.
- **Next:** obtain an exact-repository Python execution path. If a dedicated GitHub Actions workflow is needed, request separate approval before editing/dispatching it. Then run test-first RED at an exact source SHA, implement the minimum approved in-memory core, run GREEN and the complete `market_data` suite, and record exact evidence.
