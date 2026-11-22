# Session Handoff Addendum — 2026-11-22
## Importer-Core synthetic in-memory TDD and dedicated workflow

Controlling TDD decision: `docs/decisions/T0_IMPORTER_CORE_SYNTHETIC_TDD_SCOPE_APPROVAL_2026-11-22.md`, commit `89b9e41e3608f75839e7c5fae7a3a0691ee716b9`.

### Approved TDD scope
- Synthetic-only pure-Python in-memory normalization, row accounting, duplicate/conflict reconciliation and coverage calculation using existing `ArchiveKlineRow`.
- Tests first, exact-SHA RED, minimum implementation, exact-SHA GREEN and full `market_data` regression.
- Existing branch `main`; do not create a feature branch.
- No stable provenance IDs/digest framing/schema/DDL/database behavior; those remain S1 contract/schema freeze.

### Dedicated workflow approval and implementation
- Owner explicitly approved creation of a dedicated GitHub Actions workflow for synthetic importer-core tests.
- Workflow: `.github/workflows/t0-importer-core-synthetic.yml`.
- Workflow commit: `84bcfc91ba08b21b96d699101548415d1f19821d`.
- Workflow blob: `97941bc97cc8f9ac5d447218145232db0daf776e`.
- Scope/evidence: `docs/evidence/T0_IMPORTER_CORE_SYNTHETIC_WORKFLOW_2026-11-22.md`, commit `9ef7d719f1a0fb3868fbb4b07d6cb83bd5bff13b`.
- Push trigger is limited to changes in importer-core source or its focused test module on `main`; manual dispatch accepts optional exact SHA. Workflow verifies checkout SHA, uses Python 3.13, runs focused tests then all `market_data` tests, read-only contents permission, no artifact upload.
- Existing G1 workflow unchanged.

### Execution state
- Current main HEAD before this handoff update: `6799c624729f2db1a57cc4e218b71020b00868a2`.
- Workflow file and evidence record verified on `main`.
- Importer-core source and test module have not yet been added.
- No workflow run dispatched/observed. RED: NOT VERIFIED. GREEN/full regression: NOT RUN.
- Next: add focused synthetic tests only; push to `main`; verify the workflow run checked out the exact test commit and produced RED. Then implement only the approved in-memory core and verify GREEN plus full `market_data` suite.

### Exclusions
No real archive/sidecar access, retrieval, extraction or parsing; no network acquisition; no filesystem/host preflight; no SQLite open/create/write/DDL; no staging or real-data importer; no S1 schema/provenance freeze; no Canonical T0/MAY-10, T1/T2, VPS/runtime/deployment, credentials, exchange connectivity, trading, deletion or cleanup. No artifacts or retention changes.
