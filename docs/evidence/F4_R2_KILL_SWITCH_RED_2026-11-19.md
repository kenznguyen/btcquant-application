# F4-R2 Kill Switch fail-closed — test-only RED evidence

Date: 2026-11-19  
Repository: `kenznguyen/btcquant-application`  
Branch: `main`  
Final source/workflow HEAD: `68419ae03f2af4e3b25899644b3db5f016ab8041`

## Approval and scope

The owner approved phase A only: complete the F4-R2 Kill Switch fail-closed RED test matrix, execute it in an isolated runner, and report results before requesting separate approval for phase B.

In scope:
- Add/complete test-only assertions for unavailable and malformed Kill Switch state.
- Add a dedicated isolated expected-RED workflow and preserve its evidence.
- Record exact source/test/workflow identities and test results.

Out of scope:
- Any production source change, including `paper_execution/risk_control.py`.
- Ledger, Account Risk Contract, API, F4-R1 or F4-R3 behavior changes.
- Reset semantics, runtime, canonical DB, VPS, exchange connectivity, paper order submission or live trading.
- GREEN implementation or any attempt to make the new RED tests pass.

## Exact source identities

| File | Blob SHA | Status |
|---|---|---|
| `paper_execution/risk_control.py` | `3c76e462b0b4d924c2418842d95ed74285e2315d` | Unchanged production source |
| `paper_execution/test_f4_risk_red.py` | `7e03122ee72cb88cd039d99ca4a9ed6acfe1f656` | Test-only additions |
| `.github/workflows/f4-r2-kill-switch-red.yml` | `7a673e95efd9975b5a379a2885301a64fe3aa81d` | Dedicated isolated RED gate |

Test-only commit: `2e4b28f73a2776c59ecedd1ea8c329a9b4643de7`.  
Workflow/evidence-gate final commit: `68419ae03f2af4e3b25899644b3db5f016ab8041`.

## RED matrix

The isolated test class `F4KillSwitchFailClosedRedTest` contains seven cases:

1. Missing `paper_risk_control` table must be rejected as `RISK_CONTROL_STATE_UNAVAILABLE`.
2. Non-numeric timestamp must be rejected as `RISK_CONTROL_STATE_INVALID`.
3. Existing table with no state row must be rejected as `RISK_CONTROL_STATE_UNAVAILABLE`.
4. Pause flag outside the boolean domain (integer 2) must be rejected as `RISK_CONTROL_STATE_INVALID`.
5. Kill flag outside the boolean domain (integer 2) must be rejected as `RISK_CONTROL_STATE_INVALID`.
6. Text pause flag (`"false"`) must be rejected as `RISK_CONTROL_STATE_INVALID`.
7. Text kill flag (`"false"`) must be rejected as `RISK_CONTROL_STATE_INVALID`.

These tests intentionally specify the target contract; they do not implement it.

## Authoritative isolated RED run

- Workflow: [F4 R2 Kill Switch expected RED](https://github.com/kenznguyen/btcquant-application/actions/runs/44485444946)
- Run ID: `44485444946`
- Job ID: `135427624721`
- Workflow/head SHA: `68419ae03f2af4e3b25899644b3db5f016ab8041`
- Conclusion: **SUCCESS — expected RED confirmed**
- Runner: GitHub-hosted Ubuntu 24.04.5; Python image `python:3.12.16-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`
- Exact command: `python -m unittest -v paper_execution.test_f4_risk_red.F4KillSwitchFailClosedRedTest`
- Test output: `Ran 7 tests in 0.002s`; `FAILED (failures=7)`; 7 expected assertion failures, 0 errors.
- Workflow verifies the exact checkout HEAD, production source blob and test blob before running.
- Isolation: Docker `--network none`, read-only repository mount, no credentials, no canonical DB mount, non-root user, dropped capabilities and no-new-privileges.
- Artifact: `f4-r2-kill-switch-red-evidence`, ID `14510895644`, size 1,559 bytes, SHA-256 `8981282a6f9efb06977b7fbc6875423e8248473f8df1dc28129d8c0d501b50d7`.

## Failure interpretation

The seven expected failures demonstrate the current source does not enforce the specified validation contract:
- Missing table is converted into an unlatched state (`paused=False`, `killed=False`).
- Malformed timestamp is returned without validation.
- Missing state row raises a generic `Risk control state is missing` database error rather than the specified stable unavailable-state code.
- Out-of-domain numeric flags are coerced through `bool(...)` instead of rejected.
- Text values such as `"false"` are also coerced through `bool(...)`, rather than rejected as malformed state.

The failures are deliberate RED evidence, not a failed implementation attempt.

## Iteration transparency

Earlier workflow attempts `44485036026`, `44485121025`, `44485200258` and `44485369179` stopped at the preflight blob-identity check due to an incorrectly transcribed source SHA pin. No tests ran in those attempts. The pin was corrected using the repository's exact blob SHA; final run `44485444946` passed preflight and executed the seven RED tests.

## Status and next gate

- F4-R2 phase A test specification: **PASS**.
- Expected RED execution: **PASS — 7/7 expected failures, 0 errors**.
- Production source preservation: **PASS — exact blob unchanged**.
- F4-R1: preserved; not modified.
- F4-R3: untouched / OPEN.
- F4-R2 implementation: **NOT AUTHORIZED**.
- Runtime, canonical DB, VPS, exchange and trading: **NOT ACCESSED**.

Next step: present this evidence to the owner and wait for separate approval of phase B. Do not modify production source or attempt GREEN until that approval is explicit.
