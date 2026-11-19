# F4 Pipeline API and decision Core-First test / enforcement — 2026-11-19

## Scope and approvals
- Original task: isolated import and regression verification for `pipeline/test_api.py` and `pipeline/test_decision.py`; do not automatically install packages or run CI.
- Owner approved test-only alignment with Core-First, then separately approved the production API correction that enforces AI offline-only behavior.
- Scope is limited to the API paper-evaluation boundary and corresponding API regression tests. No T0, DB schema, dependency, workflow, deployment, runtime, exchange or live-trading changes.

## Exact Git evidence
- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Prior test alignment commit: `9223d3ce72669b4916f717ca1e43f3b80e8c996c`
- Test isolation follow-up: `4d4a43427b587ff16e8a890c5d75a43678b1e1e6`
- Test/initial enforcement commit: `0c6c063b272fe34dd6072022b89f757ee2fb7804`
- Core-only cleanup commit: `191b8edb310335d7e242f701bd3e57ce6916f7ba`
- Current HEAD at evidence preparation: `191b8edb310335d7e242f701bd3e57ce6916f7ba`
- Current tree: `0f6b8015d4de04c3b9567aa6a8a073265ded43f3`
- `pipeline/api.py` final blob: `0301bbec82f99253b8a4c69e09db53ad108df686`
- `pipeline/test_api.py` final blob: `30dd11a50c63f27680f7c65c4339ad955e586476` (26 test methods).
- `pipeline/test_decision.py` unchanged blob: `6781f26d66635f56662a627bdd3b4a63f26c1f28` (15 test methods).

## Production API correction
- `POST /v1/paper/evaluate` now defaults an omitted source to Strategy Core.
- An explicit `{"source":"AI"}` receives HTTP 403 / `AI_EXECUTION_DISABLED` before dual-ledger readiness checks, Ledger construction, AI candidate evaluation, mark writes or order submission.
- AI research remains available through the offline `GET /v1/decision` endpoint.
- Paper evaluation path now constructs only the Strategy Core decision and Core ledger path; unreachable AI evaluation/ledger submission branches were removed.
- Unknown sources remain rejected by the existing payload validation.
- No AI Ledger write or AI order is authorized by this change.

## Test changes
- Six API tests that previously routed AI candidates into paper Ledger/risk/kill-switch paths now exercise Strategy Core.
- Missing calibration, missing prediction and corrupt/stale model cases use the offline `/v1/decision` route.
- Added `test_ai_paper_execution_is_disabled_under_core_first_policy`: explicit AI source must receive 403/`AI_EXECUTION_DISABLED` and the SQLite table set must remain unchanged.
- `pipeline/test_decision.py` unchanged; it remains offline AI decision/candidate coverage.

## Static verification
- GitHub read-back confirmed exact current API/test blobs and current branch HEAD.
- Static source review confirms explicit AI rejection precedes `dual_ledger_ready` and any Ledger initialization.
- Static source review confirms omitted source defaults to Core and the paper-evaluation branch no longer contains AI candidate evaluation.
- Static test inventory: 26 API tests + 15 decision tests.
- These are static/source checks only; they are not runtime import or regression test results.

## Dependency and environment
- SQLite fixture path requires Python standard-library `unittest` and `sqlite3`; selected target remains Python 3.12.16, standard library only.
- Do not install `psycopg`, `ccxt`, pytest or Hummingbot dependencies. PostgreSQL, network, exchange credentials and Hummingbot services remain excluded.
- Local environment previously inspected: Python 3.13.5 only; exact local checkout unavailable. A read-only shallow clone attempt failed due DNS resolution for github.com.
- No package installation performed.

## Execution status
- Core-First API source correction: COMMITTED; static verification PASS.
- API test alignment: COMMITTED; static inventory PASS.
- Runtime imports: NOT RUN.
- `pipeline/test_api.py`: NOT RUN.
- `pipeline/test_decision.py`: NOT RUN.
- Compile/build: NOT RUN.
- CI/workflow: NOT RUN.
- No source/test execution was claimed. Exact Python 3.12.16 isolated runner and local checkout remain unavailable.
- No runtime, canonical database, VPS, exchange or trading path accessed.

## Final status
- Core-First API enforcement: PASS — static inspection only; runtime behavior NOT VERIFIED.
- Test alignment: PASS — static inspection only.
- Import and 41 regression tests: NOT VERIFIED / BLOCKED by runner/checkout availability.
- Package installation and CI: NOT RUN, as requested.
- Paper trading remains paper-only; AI paper execution disabled; live trading PROHIBITED.

## Next step
Provision or make available an exact repository checkout with Python 3.12.16 and standard library only, network disabled. Then run the two isolated unittest modules and capture exact command/output. Do not install packages or run CI without separate approval.


## Runner availability recheck — 2026-11-19
- Re-read `docs/PROJECT_SESSION_HANDOFF.md` before continuing; current starting HEAD was `d7636fe1bb8f619cf61f69b60464903c740091c9`.
- Checked installed Python interpreters with `uv python list --only-installed`: only CPython 3.13.5 is present (`/usr/bin/python3.13`, `/usr/bin/python`). Python 3.12.16 is not installed or cached as an installed interpreter.
- Retried read-only Git remote discovery using `git ls-remote https://github.com/kenznguyen/btcquant-application.git refs/heads/main`; failed with `Could not resolve host: github.com`.
- No interpreter was installed/downloaded; no package was installed; no repository clone or checkout was created; no source or tests were executed. No CI/workflow was started.
- Result: exact Python 3.12.16 checkout/runner remains BLOCKED by unavailable interpreter and DNS/network resolution. The prior source-only static PASS remains unchanged; import and 41 regression tests remain NOT RUN.
