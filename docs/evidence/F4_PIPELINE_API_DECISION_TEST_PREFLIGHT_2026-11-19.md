# F4 Pipeline API and decision Core-First test alignment — 2026-11-19

## Scope and approval
Owner approved a test-only adjustment so API regression expectations conform to Core-First. Production source must remain untouched. Objective remains isolated import/regression verification for `pipeline/test_api.py` and `pipeline/test_decision.py`. No automatic package installation and no CI/workflow execution.

## Exact source baseline and test-only commits
- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Test alignment commit: `9223d3ce72669b4916f717ca1e43f3b80e8c996c`
- Follow-up assertion-isolation commit: `4d4a43427b587ff16e8a890c5d75a43678b1e1e6`
- Current HEAD at report preparation: `4d4a43427b587ff16e8a890c5d75a43678b1e1e6`
- `pipeline/test_api.py` final blob: `5cc04ccebf16a04a3289fc9fb4ecc3138b876c83` (26 test methods).
- `pipeline/test_decision.py` unchanged blob: `6781f26d66635f56662a627bdd3b4a63f26c1f28` (15 test methods).
- `pipeline/api.py` remains unchanged at blob `d0217944bbfa9b864b0f259e0091daf9a989d180`.

## Test-only changes
- Converted six API test cases that previously injected AI candidates into paper evaluation and asserted ledger/risk/kill-switch/order outcomes to use Strategy Core intents. This retains regression coverage for Core idempotency, pause, risk limits and kill-switch behavior.
- Recast the missing-calibration test as an offline AI research decision test using `/v1/decision`; it no longer routes AI through paper execution.
- Added `test_ai_paper_execution_is_disabled_under_core_first_policy`. It submits an AI candidate to the paper evaluation endpoint and asserts HTTP 403 / `AI_EXECUTION_DISABLED`, while verifying that the SQLite table set is unchanged.
- `pipeline/test_decision.py` remains unchanged because it tests offline AI decision/candidate logic and does not write to the Paper Ledger.
- No production source, dependency, workflow, runtime configuration, T0 asset or database payload was changed.

## Static Core-First conflict — implementation blocker
The unchanged `pipeline/api.py` currently:
1. Reads `dual_ledger_ready`.
2. When the dual ledger is not active, constructs the default `ledger()` even for `source == "AI"`.
3. Rejects an AI intent with `AI_ADMISSION_NOT_ESTABLISHED` only when the dual ledger is active.
4. Otherwise continues to the shared intent submission path.

The isolated test fixture creates a SQLite candle database without dual-ledger migrations, so the static branch appears to permit the AI request to reach ledger setup/submission rather than return the newly specified Core-First 403. This is a **static source finding, not a test execution result**. The new test intentionally guards the Core-First contract; it is expected to expose this source-path mismatch if executed against the current source. Production correction is outside this test-only approval and requires separate approval.

## Minimum dependency/environment decision
- Test framework and direct test imports: Python standard-library `unittest`; SQLite fixture uses standard-library `sqlite3`.
- Minimum target: Python 3.12.16, standard library only; no third-party packages required for the SQLite fixture path.
- Do not install `psycopg`, `ccxt`, pytest or Hummingbot dependencies. PostgreSQL, network, exchange credentials and Hummingbot service remain excluded.
- Use temporary test databases only, no canonical DB mount, credentials or network.

## Execution status and evidence
- Static test-file review: PASS — 26 API tests and 15 decision tests; AI-to-Ledger expectations were removed from the six Core paper-control tests.
- Core-First AI-denial regression assertion: ADDED; runtime result NOT VERIFIED. Static source inspection indicates current API source does not yet enforce the expected denial on the non-dual-ledger branch.
- Direct runtime imports: NOT RUN.
- `pipeline/test_api.py` execution: NOT RUN.
- `pipeline/test_decision.py` execution: NOT RUN.
- Local container has Python 3.13.5, not the selected Python 3.12.16. Exact source checkout is unavailable locally; read-only clone previously failed due DNS resolution failure for github.com.
- No package installed; no CI/workflow run; no compile/build/test/import command run.
- No runtime, production database, VPS, exchange or trading path accessed.

## Status
- Test-only Core-First alignment: PASS (source diff/structure reviewed).
- Test API expected Core-First rejection: ADDED / NOT VERIFIED; static source mismatch BLOCKED.
- Minimum dependency decision: PASS (static).
- Runtime imports and regression execution: NOT VERIFIED / BLOCKED by local environment and checkout availability.
- Production Core-First API enforcement: BLOCKED pending separate authorization; no source edit made.
- Paper execution remains NOT AUTHORIZED; live trading PROHIBITED.

## Next gate
1. Provide an exact repository checkout and Python 3.12.16 isolated runner, network disabled.
2. Obtain separate approval before any production API change to enforce AI offline-only behavior in the non-dual-ledger path.
3. After that source contract is resolved, run the approved import checks and the two isolated unittest modules, capture exact output and update this evidence. Do not install packages or run CI without separate approval.
