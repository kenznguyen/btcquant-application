# F4-R3 Kill Switch reset/readiness — phase A RED evidence

Date: 2026-11-19  
Repository: `kenznguyen/btcquant-application`  
Branch: `main`  
Phase: A — test-only specification and isolated RED execution  
Final implementation authority: **not granted**

## Approval and scope

The owner approved phase A for F4-R3 only.

Allowed:
- Add isolated tests specifying Kill Switch reset authorization, account readiness, pending-order blocking, time-of-check/time-of-use (TOCTOU) protection, and transaction rollback.
- Add a dedicated isolated RED workflow and evidence.
- Preserve the existing F4-R1 and F4-R2 source behavior.

Not allowed / not performed:
- No production source correction.
- No Ledger, Account Risk Contract, API, Kill Switch, T0 or runtime behavior changes.
- No canonical database, VPS, exchange, service or deployment access.
- No paper order submission or live trading.

## RED matrix

Test file: `paper_execution/test_f4_r3_reset_red.py`  
Blob: `89247eae792bfba48adea7648d3420c914545a5b`  
Test class: `F4KillResetAtomicReadinessRedTest`  
Total: 6 tests.

| Test | Result | Finding |
|---|---|---|
| `test_direct_reset_rejects_forged_ready_true_without_account_readiness` | RED | Direct Ledger reset accepts caller-supplied `ready=True` without deriving authoritative account readiness. |
| `test_reset_rejects_pending_orders_even_when_caller_claims_ready` | RED | Direct reset clears the latch while an OPEN paper order exists. |
| `test_legacy_readiness_fallback_does_not_promote_missing_cutover_to_ready` | RED | Legacy readiness branch reports `accountRiskReady=True` without Dual Ledger/account cutover proof. |
| `test_api_rechecks_readiness_after_stale_preflight_before_clearing_kill` | RED | API returns 200 and clears the latch after pending-order state changes between preflight and reset. |
| `test_authoritative_account_risk_not_ready_blocks_reset_preflight` | PASS | Existing Dual Ledger preflight rejects an authoritative account-risk snapshot with `riskReady=False`. The snapshot is mocked to isolate the API decision branch. |
| `test_audit_failure_rolls_back_kill_latch_clear_atomically` | PASS | Existing Ledger transaction rolls back the latch clear when reset audit insertion fails. |

Expected RED result: **4 failures, 2 passes, 0 errors**. This is intentional: four tests reproduce F4-R3 defects; two passing controls demonstrate existing fail-closed behavior that must be preserved.

## Authoritative isolated workflow

- Workflow: `.github/workflows/f4-r3-kill-reset-red.yml`
- Workflow blob: `7574a6d4bf8ab1954b8c6f7ec735178e5741403a`
- Workflow pin/update commit: `2e748c5e84441593a3ff2d312ec1ffe11058407d`
- Test file commit: `37d82cff0f5e9d0e487382b9959f6ce502f0da9d`
- Authoritative run: [44487694102](https://github.com/kenznguyen/btcquant-application/actions/runs/44487694102)
- Job ID: `135435198428`
- Workflow/source HEAD: `2e748c5e84441593a3ff2d312ec1ffe11058407d`
- Workflow conclusion: **SUCCESS** — the workflow verified exact source identities and confirmed the expected RED pattern.
- Result: `Ran 6 tests`; `FAILED (failures=4)`; 0 errors.
- Python: 3.12.16 image pinned by digest `sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`.
- Isolation: Docker `--network none`, read-only repository mount, non-root user, dropped capabilities, no-new-privileges, no credentials and no canonical DB mount.

### Exact source identities checked by the workflow

| File | Blob SHA |
|---|---|
| `paper_execution/test_f4_r3_reset_red.py` | `89247eae792bfba48adea7648d3420c914545a5b` |
| `paper_execution/ledger.py` | `9fbf195cd6b19bd4ce2217f3648b4722a2472dcb` |
| `paper_execution/risk_control.py` | `c8fe573a7a5b0716159e50a678423e402d7df3ba` |
| `paper_execution/risk_contract.py` | `7ae74740568e3bcad78acd928896ee363cc62613` |
| `pipeline/api.py` | `0c288741afe386cacaa8d2c7d3991274a00c43ef` |

## Artifact

- Name: `f4-r3-kill-reset-red-evidence`
- ID: `14510199597`
- Size: 1,695 bytes
- GitHub digest: `sha256:03165d9a6db7fab99ee1108835a8ece5ea9f663580c88b322c0edf418e807a09`
- Downloaded ZIP independently hashed: `03165d9a6db7fab99ee1108835a8ece5ea9f663580c88b322c0edf418e807a09`
- Artifact payload inspected; metadata and unittest output match the exact six-test run.

## Iteration and workflow notes

- Initial R3 workflow run `44487513363` stopped at identity preflight after the test file was separated from the F4-R2 suite; no tests ran. The workflow pin/path was corrected and the authoritative run `44487694102` verified exact identities and executed all six tests.
- The earlier shared-file run `44487453357` also recorded the same four-failure/two-pass RED pattern, but is superseded by the isolated test file and final run above.
- Restoring the original F4-R2 test file triggered its historical RED workflow `44487513396`; that workflow stopped at preflight because it pins the pre-F4-R2 production source blob, which is no longer current after F4-R2 implementation. No F4-R2 tests ran in that attempt.
- F4-R2 GREEN was re-executed on the restored test baseline at run `44487513293`: SUCCESS, seven tests passed, confirming the F4-R2 suite/source boundary remained intact.
- F4-R1 focused workflow run `44487513398`: SUCCESS. No F4-R1 source/test changes were made.

## Review and status

The test-only diff was reviewed for scope, behavioral assertions and isolation. The two passing controls guard against regressing existing account-risk preflight and SQLite transaction rollback. Four failing cases directly expose the reset-readiness defects and do not authorize or imply a production fix.

Statuses:
- F4-R3 phase A specification: **PASS**.
- Expected RED execution: **PASS — 4 failures / 2 passes / 0 errors**.
- Exact source/test identity verification: **PASS**.
- Artifact download and digest verification: **PASS**.
- F4-R3 production correction: **NOT AUTHORIZED / awaiting separate phase B approval**.
- F4-R1: preserved.
- F4-R2: preserved; GREEN regression re-run passed 7/7.
- Runtime, canonical DB, VPS, exchange and trading: **NOT ACCESSED**.
- Production operational readiness: **NOT CERTIFIED**.

## Required next gate

Report phase A and wait for the owner's separate approval before any F4-R3 production source implementation. Keep the fix narrowly scoped to authoritative readiness evaluation and Kill Switch reset atomicity. Do not modify F4-R1/F4-R2, change account-risk limits, start runtime, or infer trading readiness from these isolated tests.
