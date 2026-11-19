# F4 Pipeline API and decision isolated import/regression preflight — 2026-11-19

## Scope
Read-only preflight for `pipeline/test_api.py` and `pipeline/test_decision.py` in `kenznguyen/btcquant-application`, branch `main`. Objective: settle the minimum test dependency/environment and identify blockers before isolated execution. No automatic package installation and no CI/workflow execution were authorized or performed.

## Exact source baseline
- Repository HEAD: `8c618e4587857dfbdcbd91bf58f21fd801fea1e1`
- `pipeline/test_api.py`: blob `4e2d92b24a7c8c0810ac5f2706707c5b9deb6fb2`; 25 test methods.
- `pipeline/test_decision.py`: blob `6781f26d66635f56662a627bdd3b4a63f26c1f28`; 15 test methods.
- `pipeline/api.py`: blob `d0217944bbfa9b864b0f259e0091daf9a989d180`.
- `pipeline/decision.py`: blob `8720d8ab988529b1545a27aa0792beca9e6a84aa`.
- `pipeline/values.py`: blob `5576376454af129b944919fb588e26c0657a781e`.
- `market_data/store.py`: blob `4e1b0c54bd56455abe5be0e5c7d0807e63e0bc78`.
- `market_data/storage.py`: blob `13fe1ae01ebb5318b69e69eef3e512d207f74c49`.
- `market_data/postgres.py`: blob `2fe27fe2d066dda0c192a381b72d27404487b800`.
- `futures_intelligence/import_collector.py`: blob `5effe6540b86edcb190456c95b6bb11456aec099`.
- `integrations/hummingbot_bridge.py`: blob `aa9db7522ffb7ce911c7fbbdc73a7f9b47401331` (dormant; import is lazy in `book_snapshot`).

## Minimum dependency and environment decision
- Both test modules use Python standard-library `unittest`; their direct imports are standard library plus repository modules.
- Static inspection of the test entry points and key transitive paths (`pipeline.api`, `pipeline.decision`, `market_data`, `futures_intelligence`, `paper_execution`, `risk_policy`) did not identify a required third-party package for the SQLite fixture path.
- `psycopg` is imported lazily only when the PostgreSQL connection context is entered. PostgreSQL is excluded; do not install `psycopg`.
- `ccxt` is not required by these two test entry points; do not install it.
- Hummingbot adapter uses standard-library modules and is imported lazily. No Hummingbot service, credentials, network, or exchange is required for these fixture tests.
- Selected target environment: **Python 3.12.16**, standard-library `sqlite3` and `unittest`, no third-party dependencies. This matches the already-used pinned Python test baseline in the repository's isolated test evidence. The test process should use a temporary directory/database, no canonical DB mount, no credentials, and network disabled.
- This is a static dependency decision, not proof of successful runtime imports. Exact transitive import execution remains NOT VERIFIED.

## Core-First compatibility finding — BLOCKER
The current API test file contains AI candidate-to-ledger expectations that conflict with the controlling Core-First decision (Strategy Core only in the paper path; AI offline research only; no AI Ledger writes/orders; `AI_EXECUTION_ENABLED=false`):
- `test_retries_do_not_duplicate_positions_or_fees` (line 118) patches `api.decide` with an AI intent and expects an order to be created.
- `test_pause_is_persistent_and_distinct_auth_is_required` (line 140) sends a patched AI intent through paper evaluation.
- `test_risk_limit_breach_auto_kills_new_paper_intents` (line 316) and `test_unconfigured_risk_limits_fail_closed` (line 324) route patched AI intents through the ledger/risk path.
- `test_api_kill_switch_requires_control_token_and_blocks_paper_evaluation` (lines 341 and 351) expects a patched AI intent to be rejected by the kill switch and, after reset, filled.
- `test_kill_switch_cannot_be_cleared_by_generic_resume_or_malformed_reset` (line 366) also routes an AI intent through paper evaluation.
- Static source review of `pipeline/api.py` shows the default paper-evaluation source is AI, and when the dual ledger is not active the branch can construct the default ledger for that AI path. This is inconsistent with the Core-First prohibition and must not be normalized by simply running the legacy assertions.
- Other AI tests that only verify a research decision returns WAIT/no intent (for example missing calibration context) are not equivalent to AI Ledger execution and can remain candidates for offline research validation.
- `pipeline/test_decision.py` exercises the offline decision evaluator and candidate intent construction; it does not itself write to the paper Ledger. It is compatible with offline research testing, subject to the isolated fixture/environment gate.

Required before running the full API module: owner-approved test/source scope to make AI paper-path assertions enforce Core-First denial (or explicitly select only Core-compatible test cases while recording exclusions). Do not change production source or rewrite tests under this preflight.

## Execution attempt and evidence
- Container Python available: `3.13.5`; Python 3.12.16 interpreter/image is not present locally.
- `pytest` happens to be present but is not required; tests are `unittest` modules.
- `psycopg` and `ccxt` are absent; neither was installed.
- Read-only shallow clone attempt to obtain the exact source for local execution was blocked by DNS resolution failure for `github.com`. No checkout was created.
- No test, import, compile, build, workflow, or CI command was run. No package was installed. No source/test/workflow/dependency files were changed. No runtime, database, VPS, exchange, or trading path was accessed.

## Status
- Static direct import review: PASS.
- Minimum dependency proposal: DECIDED — Python 3.12.16 + standard library only for SQLite fixture path.
- Exact runtime import verification: NOT RUN / NOT VERIFIED.
- `pipeline/test_decision.py` regression execution: BLOCKED pending exact local checkout/Python 3.12.16 environment.
- `pipeline/test_api.py` full regression execution: BLOCKED by Core-First incompatible AI-to-Ledger assertions, in addition to environment availability.
- Package installation: NOT PERFORMED.
- CI/workflow: NOT RUN.
- Runtime/production: NOT VERIFIED / NOT CERTIFIED.

## Next gate
1. Provide an exact local checkout or a permitted isolated runner with Python 3.12.16 and no network.
2. Separately approve a narrow Core-First-compatible treatment of the six AI-to-Ledger API test methods before executing the full API module.
3. Then run import checks and the approved isolated `unittest` modules without package installation or CI, capture exact output, and update this evidence with PASS/BLOCKED status.
