# F4 API Mark Provenance Propagation — TDD Evidence — 2026-11-21

## Scope and decision

Owner approved a bounded TDD increment on existing `main` for:
1. Propagate typed canonical market-mark provenance through both account-mark writes in `POST /v1/paper/evaluate`.
2. Add a focused API regression test.
3. Correct the F4 workflow path filters, immutable source pins and test-count reporting.

No T2 source, tests or workflow were changed. No risk-policy, Shared Risk Engine, Kill Switch, Core strategy, T0/T1, runtime, database, deployment or trading behavior was intentionally changed.

## Exact final tested source

- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Tested source SHA: `941337c74d77d15d979adccb86ac42fe84cb3771`
- `pipeline/api.py` blob: `3133a6865282fd353d48a4c0c938c0741cf5d49b`
- `pipeline/test_api.py` blob: `67f9b668632f0dd294a38e67ffae566ba44874fc`
- `.github/workflows/f4-pipeline-core-first-isolated.yml` blob: `f360358d8007eafabb2b5bb7e4250ec58cf84666`
- Compare from prior main `76e32a0d07ce82732218a72c2bb1b8a0b2316d7e`: 13 commits ahead, 0 behind; exactly three changed paths above. No T2 paths changed.

## TDD evidence

### RED

- F4 run [44902397355](https://github.com/kenznguyen/btcquant-application/actions/runs/44902397355), commit `9ab80aeb174b9eda31abb06ac9f4333eaa97dfbd`.
- New regression test failed before the API fix with HTTP 400 `INVALID_INPUT`.
- The failure reproduced the missing typed `mark_provenance` propagation.

### GREEN — focused regression

- Final F4 run [44902800155](https://github.com/kenznguyen/btcquant-application/actions/runs/44902800155), job `136842060442`, exact tested SHA `941337c74d77d15d979adccb86ac42fe84cb3771`.
- Isolated regression: `pipeline.test_api.FiveLayerApiTest.test_paper_evaluate_records_typed_canonical_mark_provenance` — **1/1 PASS**.
- Test verifies the API returns both `decision` and `order`, the consumed canonical mark provenance is persisted, and the order remains rejected when the test fixture lacks verified account/funding cutover. This preserves fail-closed Shared Risk Engine behavior; no risk bypass is introduced.
- The same typed provenance object is built from the exact `mark_window` and passed to both pre-submit and post-submit `record_account_mark` calls.

## F4 workflow correction and suite result

- Workflow path filters now include `pipeline/api.py`, `pipeline/test_api.py`, `paper_execution/ledger.py`, `paper_execution/account_equity.py`, and `paper_execution/mark_provenance.py`.
- Immutable blob verification covers those files plus the existing pinned F4 dependencies; source verification passed on the final run.
- Test count is consistently 46 in the guard, metadata and summary. The focused provenance test runs separately before the full F4 suite.
- Final run [44902800155](https://github.com/kenznguyen/btcquant-application/actions/runs/44902800155): isolated provenance test **1/1 PASS**; full F4 suite **BLOCKED**, 46 tests run with 5 failures.
- Remaining failures:
  - `test_api_kill_switch_requires_control_token_and_blocks_core_paper_evaluation`
  - `test_core_and_ai_signals_are_independent_and_share_the_risk_gate`
  - `test_kill_switch_cannot_be_cleared_by_generic_resume_or_malformed_reset`
  - `test_pause_is_persistent_and_distinct_auth_is_required`
  - `test_risk_limit_breach_auto_kills_new_core_paper_intents`
- These failures return `RISK_INPUTS_UNAVAILABLE` rather than the tests' expected Kill Switch/Pause/drawdown/FILLED outcomes. The fixture does not establish the verified account/funding cutover required by current risk admission. Do not weaken the risk engine or alter policy as part of this increment.
- Artifact: `f4-pipeline-api-decision-evidence`, ID `14706726809`, SHA-256 `a3cdf304773c20a3bc4c8f305ce9230d9ed8e70f81c23e6364bf29f78f12a6ac`.

## Status

| Part | Status |
|---|---|
| API provenance propagation | **IMPLEMENTED** |
| Focused provenance regression | **PASS — 1/1** |
| F4 workflow paths, pins and count guard | **IMPLEMENTED / SOURCE VERIFICATION PASS** |
| Full F4 suite | **BLOCKED — 5 failures / 46 tests** |
| Full repository regression | **NOT RUN** |
| T2 | **UNCHANGED** |
| Runtime, DB, deployment, exchange and live trading | **NOT ACCESSED / NOT AUTHORIZED** |

## Next step and limits

Next separate increment should diagnose and repair only the F4 test fixture's account-risk readiness (verified cutover/funding provenance) or update the affected test contracts after explicit owner approval. Preserve Shared Risk Engine fail-closed behavior. No runtime, DB, T0/T1 integration, T2 change, order execution or deployment is authorized by this evidence.
