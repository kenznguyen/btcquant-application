# GitHub Actions Execution Environment Decision — 2026-11-19

## Decision

The owner designates **GitHub Actions** as the intended execution environment for the approved isolated SQLite/API test suite in `kenznguyen/btcquant-application`.

This is an environment selection and documentation record only. It does not create or dispatch a workflow.

## Scope

- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Intended workload: six T0 SQLite/API `unittest` modules, 61 statically inventoried test methods.
- Required source revision for the previously approved test execution: exact commit `32aaa78a6a8da2ef04c98c7f5ef4c7a4be2afb6f`, subject to rechecking current main and selecting the exact immutable SHA immediately before any run.
- Test command candidate: `python -m unittest discover -s market_data -p 'test_*.py' -v`.

## Required workflow properties before execution

A future workflow must be explicitly reviewed and approved before creation/dispatch, and must:

1. Run on GitHub-hosted ephemeral runner; no self-hosted runner, VPS or persistent service.
2. Checkout the exact approved immutable commit SHA and report it in the run output.
3. Use Python >=3.10; pin a specific supported interpreter version in the workflow after owner review.
4. Run only the six approved SQLite/API test modules.
5. Avoid network access during test execution (use runner-level network isolation where available; if this cannot be guaranteed, report the limitation and do not claim fully isolated execution).
6. Use a clean environment with no inherited T0 database path, PostgreSQL DSN, API token, exchange credentials or trading configuration.
7. Ensure SQLite test files are created only in test-owned temporary directories.
8. Not install application/runtime dependencies speculatively. The reviewed test paths currently indicate standard-library-only dependencies; if a missing dependency is demonstrated, stop and request approval for the exact package/version.
9. Exclude PostgreSQL/TimescaleDB tests, exchange access, Feeder/API service startup, canonical data, VPS/runtime operations and all trading/execution paths.
10. Preserve workflow run URL/ID, exact source SHA, runner/OS, Python version, command, exit code, discovered/passed/failed/skipped counts and logs/artifacts.

## Current repository state

- At the latest inspected target HEAD `7d927ed2dd6b35f5eaad59ee306e2f6e04269a6a`, `.github/workflows/` does not exist.
- Therefore GitHub Actions is the selected target environment but is **NOT CONFIGURED** in this repository.
- No workflow was created, edited or dispatched in this decision record.
- No test was run and no package was installed.
- The previous execution attempt remains BLOCKED before checkout due container DNS failure; see `docs/evidence/SQLITE_API_TEST_EXECUTION_ATTEMPT_2026-11-19.md`.

## Status

- Execution environment decision: **RECORDED / PASS**
- GitHub Actions workflow: **NOT CONFIGURED**
- Workflow creation/dispatch: **NOT AUTHORIZED by this documentation-only decision**
- Tests: **NOT RUN**
- Runtime/canonical DB/exchange/VPS/live trading: **NOT ACCESSED**

## Next gate

Prepare a minimal workflow proposal for owner review. Do not create or dispatch it until separately approved. Preserve the six-module scope and all guardrails above.
