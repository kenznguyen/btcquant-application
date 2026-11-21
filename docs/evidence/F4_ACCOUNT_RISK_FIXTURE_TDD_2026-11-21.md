# F4 Account-Risk Fixture Readiness — TDD Evidence — 2026-11-21

## Scope and approval

Owner approved a separate bounded increment to diagnose and correct the F4 test fixture's account-risk readiness. The implementation is test-only:
- Establish the complete synthetic PAPER account state required by the existing dual-ledger contract: canonical consumed mark provenance, explicit account-equity cutover, and funding-coverage evidence.
- Correct assertions to the existing dual-ledger API/risk-control contract.
- Keep the F4 workflow's source pinning, isolated focused regressions, 47-test guard, and failure-log retention accurate.

No production API, ledger, Shared Risk Engine, risk policy, Core strategy, AI strategy, T0/T1/T2 implementation, runtime or database was changed.

## TDD sequence

### RED — incomplete fixture

- Run [44903282774](https://github.com/kenznguyen/btcquant-application/actions/runs/44903282774), commit `863d2e26f86dfa9ab89576f6245b5890b297af21`.
- The new fixture-readiness regression failed with `ACCOUNT_RISK_MARK_PRICE_INVALID`: the previous helper created the dual-ledger schema but did not seed a canonical consumed mark or account cutover.
- Artifact `14707076404`, SHA-256 `ddbe514fab3b2ee438028983132715f6edc10e55a9dc1792d37a9df4557cff75`.

### GREEN — complete fixture and corrected contracts

- Final F4 run [44903612650](https://github.com/kenznguyen/btcquant-application/actions/runs/44903612650), job `136844482785`.
- Tested source SHA: `3a7858f60cd236146407370ca87af6cd902455c5`.
- Immutable source/blob verification: **PASS**.
- Targeted regressions: **2/2 PASS**:
  - `test_paper_evaluate_records_typed_canonical_mark_provenance`
  - `test_dual_ledger_fixture_establishes_verified_account_risk_cutover`
- Full F4 API + decision suite: **47/47 PASS** (`Ran 47 tests`, `OK`).
- Python `3.12.16`; Docker image pinned by digest; network disabled in test container; no credentials or canonical database mounted.
- Artifact `14706609045`, SHA-256 `2f67b27534be42c1fee8697412aea1c50d318e338ceba53b5bdbf8fc35444609`. Downloaded artifact digest was independently recomputed and matched the GitHub artifact digest.

## Fixture correction

`enable_dual_ledger()` now:
1. Creates a legacy bootstrap equity observation for the synthetic account.
2. Initializes Core and AI strategy ledgers.
3. Reads the exact closed canonical T0 M15 mark window from the isolated test database.
4. Builds typed `MarketMarkProvenance`, persists the consumed mark and links its ID to account risk state.
5. Records explicit fixture funding coverage and establishes the account-equity cutover using reconciled fixture totals.
6. Exposes the Core/AI ledgers to the test.

The new fixture test asserts the account risk snapshot is available and `riskReady=true`, with no unavailable reason, account equity 100 and daily loss 0.

## Test contract corrections

- Pause rejection in the dual-ledger Core path is asserted as `RISK_PAUSED`, matching the existing Shared Risk Engine risk-control reason.
- `GET /v1/paper` assertions now use the dual-ledger response shape: `strategyCore.positionBase`, `account.riskReady`, and `account.killSwitch.killed`.
- Drawdown fixture mutates the strategy-scoped account ledger's realized PnL, not the legacy aggregate `paper_state` compatibility row; it then calls the canonical equity endpoint to reconcile and persist the account mark before evaluating the next intent. The test verifies the existing max-drawdown latch behavior without changing thresholds or risk policy.

## Workflow correction

- Exact test source pin: `pipeline/test_api.py` blob `a7db4e1f2a4693f9bf60cd7ed574b96f0f550111`.
- F4 workflow blob: `e11ff55b6ef15351dc7c900aa496e5b851df8574`.
- Expected count is 47 in both metadata and the test execution guard.
- Focused regression output is retained and printed on failure.
- The count guard is defined in the same shell step that consumes it, avoiding cross-step shell variable scope errors.

## Change boundary and review

- Base main SHA before this increment: `298a4ece5c0c1bba1834e4996e597b87fa73dbc7`.
- Tested source SHA: `3a7858f60cd236146407370ca87af6cd902455c5`.
- Compare: 11 commits ahead, 0 behind; exactly two changed paths: `pipeline/test_api.py` and `.github/workflows/f4-pipeline-core-first-isolated.yml`.
- Review: focused self-review completed across correctness, test semantics, architecture boundary, security and workflow evidence. No production behavior or risk policy changed. Independent second-person review: **NOT VERIFIED**.

## Status

| Item | Status |
|---|---|
| Canonical mark + funding + account cutover fixture | **PASS** |
| Targeted provenance and fixture regressions | **PASS — 2/2** |
| F4 API/decision isolated suite | **PASS — 47/47** |
| Source/blob verification and evidence artifact | **PASS** |
| Full repository regression | **NOT RUN** |
| T2 | **UNCHANGED** |
| Production/runtime/DB/deployment/trading | **NOT ACCESSED** |

## Next step and limits

F4's bounded API/decision test suite is now green. Preserve the synthetic fixture as test-only. Do not reuse its synthetic funding/cutover evidence in any runtime or real account. T2 remains unchanged. No runtime integration, real database migration, T0/T1 connection, deployment, exchange connection or order execution is authorized by this increment.
