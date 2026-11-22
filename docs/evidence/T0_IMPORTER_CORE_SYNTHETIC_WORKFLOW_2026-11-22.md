# Importer-Core Synthetic GitHub Actions Workflow Approval & Implementation — 2026-11-22

Repository: `kenznguyen/btcquant-application`
Branch: `main`
Owner authorization: explicit approval in conversation on 2026-11-22 to create a dedicated GitHub Actions workflow for synthetic importer-core tests.
Prior implementation scope: `docs/decisions/T0_IMPORTER_CORE_SYNTHETIC_TDD_SCOPE_APPROVAL_2026-11-22.md`.

## Approved workflow scope

Create one isolated workflow that:
- runs on pushes to `main` only when `market_data/archive_importer_core.py` or `market_data/test_archive_importer_core.py` changes;
- supports manual `workflow_dispatch` with an optional exact 40-character source SHA;
- checks out the requested commit and verifies `git rev-parse HEAD` equals it;
- uses pinned checkout and setup-python actions and Python 3.13;
- runs the focused synthetic importer-core unittest module first;
- runs the complete `market_data` unittest discovery suite only after the focused suite passes;
- has read-only repository permissions, no secrets, no services, no network access by test code, no SQLite database connection, no archive access and no runtime integration.

## Explicit non-scope

- No changes to the existing G1 workflow.
- No workflow artifacts, artifact upload/download, retention changes or evidence bundle upload.
- No archive/sidecar listing, retrieval, extraction, parsing from real files or network acquisition.
- No filesystem preflight or host inspection. GitHub Actions checkout and Python's normal test runner are used only for source checkout and test execution.
- No SQLite open/create/write/DDL, staging, real-data importer or provenance/schema freeze.
- No Canonical T0/MAY-10, T1/T2, VPS, deployment, credentials, exchange connectivity, trading, deletion or cleanup.
- Workflow creation does not itself prove RED or GREEN. Exact-SHA test execution evidence is still required.

## Implementation

- Workflow: `.github/workflows/t0-importer-core-synthetic.yml`.
- Commit: `84bcfc91ba08b21b96d699101548415d1f19821d`.
- Existing branch: `main`; no feature branch created.
- Existing workflow `.github/workflows/t0-g1-synthetic-only.yml` was not changed.
- No importer-core source or test module was added in this workflow-creation commit.
- No workflow run was dispatched or observed in this step. The available GitHub connection supports repository file operations and run inspection but exposes no workflow-dispatch action. Push-triggered RED will occur when the separately scoped test-first commit adds `market_data/test_archive_importer_core.py`; later importer implementation changes will trigger the same workflow for GREEN.
- No artifacts are produced or uploaded.

## Status

| Item | Status |
|---|---|
| Owner approval for dedicated workflow | PASS |
| Workflow YAML created on existing main | PASS |
| Exact-SHA checkout and verification configured | PASS — execution pending |
| Focused synthetic tests | NOT RUN — test module not yet committed |
| RED evidence | NOT VERIFIED |
| GREEN / full market_data regression | NOT RUN |
| Workflow run / artifact | NOT RUN / NOT APPLICABLE (artifact upload excluded) |
| Excluded data/runtime operations | NONE performed |

## Next step

Add only the focused synthetic importer-core tests, commit them to `main`, and inspect the push-triggered run. Confirm its checked-out SHA exactly equals the test commit and capture the expected RED. Only then implement the minimum approved in-memory importer core and inspect the subsequent exact-SHA GREEN run plus complete `market_data` regression.


## Test-first RED evidence — 2026-11-22

- Test-only commit / exact tested source SHA: `ea670901974944ae71dab58241f0e4e2cbd1e85f`.
- Test file blob: `e0537c9e74a652009961cb79bdd3e873118fc2dd`.
- Workflow run: [44992280345](https://github.com/kenznguyen/btcquant-application/actions/runs/44992280345), run #1, event `push`, conclusion `failure`.
- Workflow ID: `426569112`.
- Job: `Importer-core synthetic tests`, ID `137115734474`, conclusion `failure`.
- Exact-SHA verification step passed: requested SHA and `git rev-parse HEAD` both equal `ea670901974944ae71dab58241f0e4e2cbd1e85f`.
- Python: CPython 3.13.18.
- Focused test failed as intended during import because `market_data.archive_importer_core` does not yet exist (`ModuleNotFoundError`). This is a valid RED proving the missing implementation boundary; it is not evidence that individual behavioral assertions have run yet.
- Full `market_data` regression was skipped because the focused test step failed.
- No artifacts were uploaded or produced.
- RED status: **PASS — exact-SHA RED confirmed**.

## Next implementation gate

Implement only `market_data/archive_importer_core.py` to satisfy the approved in-memory contract and this focused test suite. Then verify the push-triggered GREEN run checks out the exact implementation commit and completes the full `market_data` suite.
