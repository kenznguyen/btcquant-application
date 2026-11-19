# F4-R2 Kill Switch fail-closed — phase B implementation evidence

Date: 2026-11-19  
Repository: `kenznguyen/btcquant-application`  
Branch: `main`  
Final verified HEAD: `0d7d8074f1aa23735f9451190044e86aebf002fa`

## Approval and scope

The owner explicitly approved phase B implementation after phase A's seven-case RED matrix was recorded.

In scope:
- Implement fail-closed validation in `paper_execution/risk_control.py`.
- Preserve the seven phase-A RED cases unchanged and turn them GREEN.
- Add a dedicated isolated Python 3.12.16 GREEN workflow.
- Record exact source/test/workflow identities, CI run and artifact.

Out of scope:
- Ledger, Account Risk Contract, API, strategy logic, risk sizing and order flow.
- F4-R1 and F4-R3 behavior; especially kill reset/readiness/atomicity semantics.
- Runtime, canonical DB, VPS, exchange connectivity, paper order submission and live trading.

## Implementation

`risk_control.snapshot()` now:
- Rejects a missing `paper_risk_control` table with `RISK_CONTROL_STATE_UNAVAILABLE`.
- Rejects a missing state row with `RISK_CONTROL_STATE_UNAVAILABLE`.
- Normalizes SQLite query failures while reading the state row to `RISK_CONTROL_STATE_UNAVAILABLE`.
- Requires `paused` and `killed` to be exact integer values in the domain `{0,1}`; malformed values raise `RISK_CONTROL_STATE_INVALID`.
- Validates `updated_at_ms` using the shared `stamp()` contract; invalid timestamps raise `RISK_CONTROL_STATE_INVALID`.
- Rejects a non-string, non-null reason as `RISK_CONTROL_STATE_INVALID`.
- Returns booleans only after validating persisted values, rather than coercing arbitrary values with `bool()`.

The production change is confined to the risk-control state reader. Kill reset logic and its separate F4-R3 test were not changed.

## Exact identities and commits

| Item | Identity |
|---|---|
| Production source blob `paper_execution/risk_control.py` | `c8fe573a7a5b0716159e50a678423e402d7df3ba` |
| RED test file blob `paper_execution/test_f4_risk_red.py` | `7e03122ee72cb88cd039d99ca4a9ed6acfe1f656` (unchanged) |
| GREEN workflow blob `.github/workflows/f4-r2-kill-switch-green.yml` | `4b6b9d75a981673e1a7e8761c424a3a808a2abd6` |
| Source implementation commit | `be5326f3f34a49d7b7c3b53ccd62fdb903a6b841` |
| GREEN workflow creation commit | `fb646cb9b1297fd5db5b8f809cdcb31bc4485e25` |
| Corrected exact source-blob pin commit | `0d7d8074f1aa23735f9451190044e86aebf002fa` |
| Final main HEAD | `0d7d8074f1aa23735f9451190044e86aebf002fa` |

All commits were made sequentially on the existing `main` branch; no branch or PR divergence was introduced.

## GREEN verification

- Workflow run: [44486561151](https://github.com/kenznguyen/btcquant-application/actions/runs/44486561151)
- Run attempt: 1; workflow run number: 2
- Job ID: `135431373983`
- Conclusion: **SUCCESS**
- Exact workflow/source HEAD: `0d7d8074f1aa23735f9451190044e86aebf002fa`
- Preflight verified source blob `c8fe573a7a5b0716159e50a678423e402d7df3ba` and test blob `7e03122ee72cb88cd039d99ca4a9ed6acfe1f656`.
- Command: `python -m unittest -v paper_execution.test_f4_risk_red.F4KillSwitchFailClosedRedTest`
- Result: **7/7 PASS**, 0 failures, 0 errors; `Ran 7 tests in 0.001s`; `OK`.
- Python: 3.12.16 container pinned by image digest `sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`.
- Isolation: Docker `--network none`, repository mounted read-only, non-root user, dropped capabilities, no-new-privileges, no credentials and no canonical DB mount.

Artifact:
- Name: `f4-r2-kill-switch-green-evidence`
- ID: `14510194136`
- Size: 1,180 bytes
- GitHub digest: `sha256:6946394a2a02a8baea772d708c59b1fe6b94951dc5a33d36a1c10dea9b72cfd9`
- Independently downloaded ZIP SHA-256: `6946394a2a02a8baea772d708c59b1fe6b94951dc5a33d36a1c10dea9b72cfd9`
- Artifact payload inspected; metadata and full unittest output confirm the exact seven tests passed.

## Iteration transparency

The first GREEN workflow run, [44486491736](https://github.com/kenznguyen/btcquant-application/actions/runs/44486491736), stopped at source-identity preflight because the initial expected Git blob pin was incorrect. No tests ran and no artifact was produced. The source blob was re-read from GitHub, the workflow pin was corrected in commit `0d7d8074f1aa23735f9451190044e86aebf002fa`, and authoritative run `44486561151` then passed source/test identity checks and all seven tests.

## Independent review and status

Review of the source diff against the seven-case contract:
- Missing state is no longer interpreted as unlatched.
- Flags are validated before boolean interpretation.
- Timestamp validation uses the existing shared timestamp validator.
- The code change is localized; no new dependency or schema migration was introduced.
- F4-R3 reset/readiness behavior and its test remain unchanged.

Statuses:
- F4-R2 implementation: **PASS**.
- Seven-case fail-closed regression suite: **PASS — 7/7**.
- Exact source/test identity preflight: **PASS**.
- Isolated CI and artifact verification: **PASS**.
- F4-R1: preserved; not modified.
- F4-R3: **OPEN / NOT VERIFIED / untouched**.
- Runtime, canonical DB, VPS, exchange and trading: **NOT ACCESSED**.
- Production operational certification: **NOT GRANTED**.

Next: treat F4-R2 as implemented and isolated-test verified. Keep F4-R3 as a separate review/approval gate. Do not infer runtime or trading readiness from this test result.
