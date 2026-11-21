# T2 M2.2 — Core Adapter Isolated Slice Evidence (2026-11-21)

## Scope and approval

Implemented only the approved pure Strategy Core producer-report adapter slice in
`kenznguyen/btcquant-application` on the existing `main` branch.

Included:
- Target-owned six-case contract test module.
- Pure `core_runtime/adapter.py` translator.
- Isolated GitHub Actions RED and GREEN verification.

Explicitly excluded:
- `one_shot.py`, runners, orchestration, ledgers, risk policy, Shared Risk Engine changes.
- FreqAI, AI Strategy, AI calibration, T1 orderbook consumer/provider, T0 integration.
- Database, VPS, deployment, paper order submission, exchange access, live trading.

## Source and commit evidence

Repository: `kenznguyen/btcquant-application`  
Branch: `main`

| Change | Commit |
|---|---|
| Target-owned RED contract tests | `f685dd77088dcc7eb0b40f01a489d24bb295e741` |
| Isolated RED workflow | `db589c7d04f84ba7b0c76b5e7c9859a4e617eb3a` |
| Pure adapter implementation | `3c9724267e0acd5b6b1a9d1dec98875c5931f15c` |
| GREEN workflow/test configuration | `593488fdfb078fa3b0d01f04316017fce26b4a98` |
| Superseded RED workflow cleanup | `b54a84aebe21667fa5792f767875be3de05c5e17` |
| GREEN workflow trigger finalization | `2a30d0da92531f7f520717cb2977c7146f428a9a` |

Final repository HEAD recorded after this slice: `2a30d0da92531f7f520717cb2977c7146f428a9a`.

Source adapter blob SHA: `9795c346d2eec4c78c22035c32f463af6b40b8f4`  
Target test blob SHA: `fbe6cc428fd7058a6dbefd9eaec1979a95638474`

The adapter blob is identical to the reviewed source adapter blob from pinned source
commit `e6606e28a696374f31cd6db1ec0a1372d942d64d`.

## Test evidence

### RED

- Workflow run: [44895676994](https://github.com/kenznguyen/btcquant-application/actions/runs/44895676994)
- Run HEAD: `db589c7d04f84ba7b0c76b5e7c9859a4e617eb3a`
- Result: expected RED accepted by workflow.
- Six tests were discovered; all six failed because `core_runtime.adapter` did not yet exist.
- The workflow checked the exact expected `ModuleNotFoundError`; unrelated failures would not be accepted.
- Artifact ID: `14703494036`
- Artifact SHA256: `5f4804dc00a8efefdaaf110333734ec0fb2cf403aa45a41bac94465885c58f9d`

### GREEN

- Final isolated workflow run: [44895903601](https://github.com/kenznguyen/btcquant-application/actions/runs/44895903601)
- Run HEAD: `b54a84aebe21667fa5792f767875be3de05c5e17`
- Conclusion: `success`
- Exact adapter and test blob identities were checked before test execution.
- Python image: `python:3.12.16-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`
- Test command: `python -m unittest -v core_runtime.test_adapter_contract`
- Result: `Ran 6 tests`, `OK` (6/6 PASS).
- Artifact ID: `14703892144`
- Artifact SHA256: `c6a716385cc485936d5e9e539b2f30d214756edd4872253cb6abb1ab0c261664`

Both workflows used a read-only test workspace, a network-disabled Docker test container,
no database mount, no exchange connection, and no credentials supplied to the test
container. The Python image and GitHub Actions used by the workflows were pinned.

## Contract behavior verified

1. BUY maps to LONG and preserves producer provenance fields.
2. SELL maps to SHORT.
3. CLOSE maps to FLAT.
4. WAIT preserves its reason and does not create an intent.
5. Report/intent action disagreement is rejected.
6. Missing provenance is rejected; the adapter does not synthesize it.

The adapter is a pure translator only. It does not admit signals, calculate risk, mutate
ledgers, synthesize timestamps, or execute orders.

## Status

**PASS — isolated pure Core Adapter slice.**

This PASS applies only to the six target-owned adapter contract tests and the immutable
source/blob checks in the recorded workflow. It is not an independent code review, full
repository regression, runtime integration, or trading authorization.

## Next step and limits

- Request independent review of the pure adapter slice and review its boundary against
  the existing target `pipeline/core_signal.py` validator.
- Preserve the unresolved Core leverage/sizing semantic conflict; this slice does not
  change it.
- Do not start T1 consumer work, AI Strategy implementation, Shared Risk Engine changes,
  runner/ledger integration, runtime execution, or trading without separate approval.
