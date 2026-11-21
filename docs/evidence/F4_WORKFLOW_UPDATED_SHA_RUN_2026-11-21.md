# F4 workflow verification on updated SHA — 2026-11-21

## Scope

Verify the F4 workflow after the approved workflow-only path-filter correction. No source, fixture, production, or risk-policy changes were made.

## Exact workflow run

- Workflow commit / tested SHA: `c93f48b617e64ec69aeddc7c3c2c6bda0a7bf22a`
- Workflow blob: `b425745fde77616e568eccffeb4918bcac603987`
- Run: [44904942269](https://github.com/kenznguyen/btcquant-application/actions/runs/44904942269)
- Event: `push`
- Run conclusion: **success**
- Job: `136848395225` — F4 API and decision, Python 3.12.16 isolated
- Job conclusion: **success**
- Run timestamp: 2026-11-21T12:38:47Z
- Job log confirms checkout/ref and `git rev-parse HEAD` both equal `c93f48b617e64ec69aeddc7c3c2c6bda0a7bf22a`.
- Immutable source/blob identity verification completed successfully.
- Focused provenance/account-risk regressions ran as part of the job.
- F4 suite: **47/47 PASS** (`Ran 47 tests`, `OK`).
- Test container: Python 3.12.16, Docker network disabled, read-only workspace, no credentials and no canonical DB mount.

## Artifact

- Artifact: `f4-pipeline-api-decision-evidence`
- Artifact ID: `14707626950`
- SHA-256 digest reported by GitHub: `870ad322253fde9c2c5269ac01989880ad2fcc8459ae9e34de9c57ba93d7b762`
- [Artifact/run page](https://github.com/kenznguyen/btcquant-application/actions/runs/44904942269)

## Path-filter trigger verification

- Static workflow inspection confirms both paths are listed under `on.push.paths`:
  - `paper_execution/account_history.py`
  - `paper_execution/risk_contract.py`
- The observed `push` run was triggered by the workflow-only commit itself. It proves the corrected workflow executes on that workflow-file push, **not** that each dependency path independently triggers it.
- Independent dependency-only push probes: **NOT RUN**. Creating those probes requires commits that modify one of the two production dependency files (even temporary whitespace-only edits), which exceeds the explicitly approved workflow-only scope. No such commits/branches were created.
- Therefore per-dependency GitHub event trigger behavior remains **NOT VERIFIED**. Do not represent static path inclusion or the workflow-file push run as proof of independent dependency triggers.

## Status

- Updated-SHA workflow execution: **PASS**
- F4 tests on updated SHA: **47/47 PASS**
- Artifact published: **PASS**
- Both required path declarations present: **PASS**
- Independent GitHub push trigger for each dependency: **NOT VERIFIED**
- Overall increment: **PARTIAL** — the workflow fix is validated and its F4 job passes; isolated path-trigger behavior remains unproven under the workflow-only restriction.

## Next step / limits

If the owner later authorizes temporary dependency-only probe commits on disposable branches, test each path independently and remove those branches afterward. Until then, retain NOT VERIFIED for independent trigger behavior. No production source, Shared Risk Engine, risk policy, T2, T0, T1, runtime, database, deployment, exchange, or trading behavior may be changed.
