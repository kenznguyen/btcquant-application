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
- Next: inspect current live `main` HEAD and source tree, then perform test-first importer-core TDD only within the approved contract above. After completion, commit evidence and update the handoff; request separate approval for any next phase.
