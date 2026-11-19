# T0 Legacy SQLite/API Workflow Trigger Isolation — 2026-11-19

Repository: `kenznguyen/btcquant-application`
Branch: `main`
Workflow: `.github/workflows/t0-sqlite-api-isolated.yml`

## Scope

Owner authorized isolation of the pre-existing T0 SQLite/API workflow before further SQLite API and Storage parity work.

In scope:
- Remove automatic `push` trigger from the legacy seven-module workflow.
- Keep `workflow_dispatch` as the only trigger.
- Replace the fixed historical checkout SHA with the exact workflow-dispatch SHA (`github.sha`).
- Verify the checked-out commit against `GITHUB_SHA`.
- Remove the fixed 91-test assertion because the workflow now targets the exact current dispatch commit; retain a non-empty unittest summary check.
- Preserve the existing seven test modules and Docker isolation controls.

Out of scope:
- No changes to application production code or tests.
- No changes to source repository `kenznguyen/btcusdt-telegram-signals2`.
- No PostgreSQL/TimescaleDB, canonical database/data, VPS, runtime, T1/T2, paper/live trading or execution changes.

## Change

Commit: `91f89424da0e8c00ca56397b72364dab678eb32d`
Message: `ci(t0): isolate legacy SQLite API workflow triggers`

Workflow blob before: `9d38afd7f1e686dda07a41465a2f4287526e9347`
Workflow blob after: `b3816e2b8dfa77e39cc5b1dbc7d4fb4e8baaf391`

Changes:
1. `on` now contains only `workflow_dispatch`; the unrestricted `push: branches: [main]` trigger is removed.
2. Checkout now uses `${{ github.sha }}`; the pre-existing pinned SHA `2668dd538a99d6021921432b3485f4ed84198364` is removed.
3. Preflight verifies `git rev-parse HEAD == GITHUB_SHA`.
4. The seven test modules remain unchanged, including `market_data.test_feeder_lifecycle`. They can run only when an operator manually dispatches this legacy workflow.
5. The fixed 91-test inventory assertion is removed; the workflow still fails if unittest exits non-zero or does not report a test count.
6. Existing Python 3.12.16 image pin, Docker `--network none`, read-only source mount, non-root execution, no credentials and no canonical DB mount remain unchanged.

## Static verification

Fetched the committed workflow back from `main` and checked:
- workflow_dispatch-only trigger: PASS
- no push trigger: PASS
- checkout ref uses `github.sha`: PASS
- checkout identity compared to `GITHUB_SHA`: PASS
- old fixed SHA absent: PASS
- lifecycle module retained but manual-only: PASS
- Docker network isolation and pinned Python image retained: PASS

Commit diff confirms only `.github/workflows/t0-sqlite-api-isolated.yml` changed in the implementation commit.

## Execution status

No workflow was dispatched as part of this change. This was deliberate: the workflow contains feeder lifecycle tests and is now manual-only. Therefore:
- Workflow configuration/static isolation: PASS
- Runtime execution of the revised seven-module workflow: NOT RUN / NOT VERIFIED
- No new workflow run ID or artifact exists for this increment.

Historical incidental run `44494340918` remains evidence only of the old behavior: it ran 91 tests against the hard-coded older checkout SHA. It is not current-HEAD verification and is not acceptance evidence for this change.

## Status and next step

- CI trigger isolation: PASS (static inspection of committed workflow).
- Exact-SHA checkout contract: PASS (static inspection; runtime not yet exercised).
- Legacy lifecycle suite: preserved, manual-only.
- SQLite API/Storage parity: NOT VERIFIED; proceed with read-only source-to-target inventory only after this isolation record.
- No source repo, production code, test files, PostgreSQL, canonical DB, VPS, runtime, T1/T2 or trading execution changed or accessed.
