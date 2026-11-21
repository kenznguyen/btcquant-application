# F4 workflow dependency path-filter correction — 2026-11-21

## Scope and approval

Owner approved a bounded workflow-only increment to close the F4 self-review Required finding. The only permitted implementation change was adding the two direct fixture dependencies to the F4 workflow `on.push.paths`.

## Change

Updated `.github/workflows/f4-pipeline-core-first-isolated.yml` to include:
- `paper_execution/account_history.py`
- `paper_execution/risk_contract.py`

No production source, tests, risk policy, T2/T0/T1, runtime, database, deployment, or trading code was changed.

## Source identity

- Base main SHA: `610d43125f8210a4a0e090306f75b8846a5d88d7`
- Updated main SHA: `c93f48b617e64ec69aeddc7c3c2c6bda0a7bf22a`
- Workflow blob SHA: `b425745fde77616e568eccffeb4918bcac603987`
- Commit: [c93f48b](https://github.com/kenznguyen/btcquant-application/commit/c93f48b617e64ec69aeddc7c3c2c6bda0a7bf22a)
- Commit diff verified: exactly one changed path, the F4 workflow.

## Validation

- Static path-filter inspection: **PASS** — both Required dependencies are present under `on.push.paths`.
- Scope/diff inspection: **PASS** — workflow-only; no other file changed.
- GitHub Actions execution for this push: **NOT VERIFIED** — the available GitHub status query returned no status entries, and no workflow run ID or artifact could be retrieved in this session.
- Dependency-only push trigger probes for each dependency: **NOT RUN** — no source-file probe commits were created because this increment is constrained to workflow-only changes.
- F4 47/47 result from run [44903612650](https://github.com/kenznguyen/btcquant-application/actions/runs/44903612650) remains historical evidence for the previous tested source SHA, not evidence for this workflow commit.

## Status

**PARTIAL / NOT VERIFIED**. The missing path declarations are corrected in the committed workflow. Runtime trigger behavior for isolated dependency-only pushes and the F4 run on the updated workflow SHA remain unverified.

## Next step

Obtain the Actions run for commit `c93f48b617e64ec69aeddc7c3c2c6bda0a7bf22a`, then run isolated dependency-only push probes for each listed dependency if a permitted workflow-only test mechanism is available. Record exact run IDs, results, and artifacts. Do not modify production code or risk policy.

## Restrictions retained

No production code, Shared Risk Engine, risk policy, T2, T0, T1, runtime, DB, VPS, deployment, exchange connection, paper execution, or real order behavior was changed or authorized.
