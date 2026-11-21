# F4 Account-Risk Fixture Increment — Self-Review — 2026-11-21

## Scope and reviewed source

Self-review of the bounded F4 account-risk fixture increment at exact tested source commit `3a7858f60cd236146407370ca87af6cd902455c5`.

Reviewed exact changed blobs:
- `pipeline/test_api.py`: `a7db4e1f2a4693f9bf60cd7ed574b96f0f550111`
- `.github/workflows/f4-pipeline-core-first-isolated.yml`: `e11ff55b6ef15351dc7c900aa496e5b851df8574`

Reviewed relevant dependencies:
- `paper_execution/account_history.py`: `2564555da5e66b224aef268762eff7a9b348c459`
- `paper_execution/risk_contract.py`: `7ae74740568e3bcad78acd928896ee363cc62613`
- `paper_execution/ledger.py`: `a90db5b1ca20a11eea06aaec18872bc2678a9a08`
- `paper_execution/mark_provenance.py`: `5f5ea7c7316ac5d839d0cb9068ded97b0b1cd809`

The reviewed commit is the tested source; current main at review time was `e458a683f578c104d1ca69b9fa876189c6e6c9a3`, two documentation-only commits ahead and zero behind. Compare showed no source/test/workflow changes after the tested SHA.

## Verdict

**REQUEST CHANGES — one Required workflow coverage finding.**

The fixture and test-contract changes are internally consistent with the existing dual-ledger account-risk snapshot contract. The reported isolated CI evidence is strong, but the workflow path filter does not watch two direct dependencies used by this test module. Consequently, changes to those dependencies can bypass the F4 regression workflow.

## Findings

### Required — F4 workflow omits direct account-risk test dependencies

File: `.github/workflows/f4-pipeline-core-first-isolated.yml`, `on.push.paths`.

The workflow watches `pipeline/test_api.py`, `paper_execution/ledger.py`, `paper_execution/mark_provenance.py`, and related paths, but omits:

- `paper_execution/account_history.py`: `enable_dual_ledger()` imports and calls `record_consumed_market_mark()` from this module. The helper enforces migration state, typed provenance validation, observation-time bounds, deterministic mark identity and persistence.
- `paper_execution/risk_contract.py`: the test module directly imports and exercises `provision_account_risk_contract`, `read_account_risk_contract`, and `update_account_risk_contract`; risk-contract behavior is part of the F4 API/decision regression coverage.

A push changing either dependency alone will not trigger this F4 workflow. The current 47/47 run proves the suite passes for the pinned snapshot; it does not prove future changes to these omitted dependencies will be tested.

**Required remediation:** add both paths to `on.push.paths`. Keep this as a separate bounded workflow-only increment, then verify dependency-only pushes trigger F4 and the pinned 47-test suite passes. Do not change production code or risk policy to address this finding.

## Five-axis assessment

- **Correctness:** Fixture constructs a complete synthetic PAPER state: bootstrap equity, Core/AI ledgers, exact closed canonical M15 window, typed consumed-mark provenance, funding coverage and account-equity cutover. The snapshot reader validates the consumed mark's payload hash, typed provenance, account equity reconciliation, ledger set, funding coverage and cutover before returning `riskReady`. The targeted readiness assertion is meaningful.
- **Test semantics:** Pause, dual-ledger response-shape and drawdown assertions now target the existing contract rather than the legacy aggregate row. Drawdown mutation is followed by the canonical equity reconciliation call. The tests assert observable API/risk behavior.
- **Readability and maintainability:** Helper setup is long but groups the account's required synthetic prerequisites in one named fixture method. No unnecessary abstraction or unrelated production branch was added.
- **Architecture:** Changes are confined to test fixture and CI workflow. Synthetic funding/cutover values remain test-only. No Shared Risk Engine bypass or risk-policy change was found in the reviewed diff.
- **Security and isolation:** Workflow uses read-only contents permission, immutable action/image references, checkout without persisted credentials, Docker network isolation, read-only workspace, dropped capabilities, no credentials and no canonical DB mount. Test uses temporary SQLite files and distinct T0/PAPER paths.
- **Performance:** Focused regressions run before the bounded 47-test API/decision suite; no material performance concern found.

## Verification evidence

Reported GitHub Actions run [44903612650](https://github.com/kenznguyen/btcquant-application/actions/runs/44903612650), job `136844482785`:
- Immutable source/blob verification: PASS
- Focused regressions: 2/2 PASS
- F4 API + decision suite: 47/47 PASS
- Artifact `14706609045`, SHA-256 `2f67b27534be42c1fee8697412aea1c50d318e338ceba53b5bdbf8fc35444609`

This review inspected source and CI metadata; it did not independently rerun the suite. Full repository regression remains NOT RUN.

## Boundaries and status

- F4 fixture implementation: PASS for the bounded test-only scope.
- F4 focused and full bounded suite: PASS, 2/2 and 47/47 at the exact tested SHA.
- Workflow dependency-trigger completeness: **BLOCKED pending Required finding**.
- Full repository regression: NOT RUN.
- Independent second-person review: NOT VERIFIED; this is same-session self-review only.
- T2 unchanged; T0/T1 unchanged.
- No production behavior, risk policy, database migration, runtime, deployment, exchange connection or trading action authorized or performed.

## Next step

Request approval for a bounded workflow-only correction adding `paper_execution/account_history.py` and `paper_execution/risk_contract.py` to the path filter, followed by dependency-only trigger verification. Preserve all existing source pins, test isolation and 47-test guard.
