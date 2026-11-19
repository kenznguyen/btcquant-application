# F4 Pipeline API / Decision — Core-First enforcement fix and isolated verification

Date: 2026-11-19  
Repository: `kenznguyen/btcquant-application`  
Branch: `main`

## Approved scope

Owner approved the two bounded corrections after static diagnosis:

1. Align the AI offline-research test with the actual test fixture contract. The fixture does not initialize a paper Ledger, so `GET /v1/paper` is not a valid source for a position snapshot in this test. The regression now verifies that an AI research decision which returns `WAIT` with no intent does not create or mutate SQLite tables and does not create `paper_orders`.
2. Enforce Core-First denial before any paper write-budget or Ledger side effect. An exact `{"source":"AI"}` request to `POST /v1/paper/evaluate` now returns HTTP 403 `AI_EXECUTION_DISABLED` immediately after body parsing, before checking the store, calling `control_permit()`, initializing a Ledger, or evaluating either strategy.

The AI denial regression asserts that `control_permit`, `ledger`, `decide`, and `core_decide` are not called and that the SQLite table set is unchanged.

## Source and workflow provenance

- Initial implementation commit: `41612cd29cf64f197e407bd89b69844329aa1504`.
  - `pipeline/api.py` blob: `57b9c1ee3f09eef2691d3967ec5fb06665c2712f`.
  - Initial `pipeline/test_api.py` blob: `cd651a2a9d9d4f4aa0a3b5276d7ff557d31ebe5f`.
  - Workflow blob at that commit: `db929bd719afd3aed648c51a9db497167c5d1324`.
- Follow-up test-contract correction and final workflow commit: `ce5da75a164dbcf5b541bdd558daa370a4637d73`.
  - Parent: `41612cd29cf64f197e407bd89b69844329aa1504`.
  - Final `pipeline/test_api.py` blob: `087a77717541ddfe888ceb3832f5b734364dac65`.
  - Final workflow blob `.github/workflows/f4-pipeline-core-first-isolated.yml`: `69b4c0c18af8e2c2309f8feb1c74185b2167db75`.
  - `pipeline/test_decision.py` unchanged blob: `6781f26d66635f56662a627bdd3b4a63f26c1f28`.
- Final workflow checks out the exact event commit via `github.sha` and verifies eight source-file blob SHAs. The checked-out source SHA and workflow HEAD SHA are both `ce5da75a164dbcf5b541bdd558daa370a4637d73`.

## GitHub Actions verification

<badge>Not part of evidence file</badge>

- Workflow run: [44462689960](https://github.com/kenznguyen/btcquant-application/actions/runs/44462689960)
- Job ID: `135353019491` — SUCCESS.
- Run HEAD / exact checked-out source: `ce5da75a164dbcf5b541bdd558daa370a4637d73`.
- Runner: GitHub-hosted `ubuntu-24.04`, observed Ubuntu `24.04.5`; Docker `28.0.4`.
- Test image: `python:3.12.16-slim-bookworm`, immutable digest `sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`; runtime Python `3.12.16`.
- Exact source commit and all eight source blob checks: PASS.
- Python imports `pipeline.api`, `pipeline.test_api`, `pipeline.test_decision`: PASS.
- Test-container network isolation probe (loopback only): PASS. Test container used `--network none`, read-only source mount, non-root user, no secrets and no canonical DB mount.
- Command: `python -m unittest -v pipeline.test_api pipeline.test_decision`.
- Result: `Ran 41 tests in 0.240s`; `OK`; 41 passed, 0 failed.
- AI paper denial regression: PASS.
- AI offline research WAIT/no-intent/no-Ledger-mutation regression: PASS.
- Artifact: `f4-pipeline-api-decision-evidence`; ID `14500632811`; size 2,685 bytes; SHA-256 `f3bf50e38bed7f475291b5bd20cc9f65b15567bf1a47a97fcb62398378fe4fdf`; expires `2026-12-03T05:05:20Z`.
- Artifact URL: https://github.com/kenznguyen/btcquant-application/actions/runs/44462689960/artifacts/14500632811

## Diagnostic retry retained

- First implementation run [44462551878](https://github.com/kenznguyen/btcquant-application/actions/runs/44462551878) at source commit `41612cd29cf64f197e407bd89b69844329aa1504`: 40/41 passed, one test errored because the fixture had no `strategyCore` Ledger snapshot. This was a test-contract mismatch, not evidence of a production API regression.
- The test was corrected to assert offline research does not initialize or mutate Ledger tables; the final exact-SHA run above passed 41/41.

## Status and limits

- Core-First API enforcement fix: PASS (isolated regression evidence).
- AI paper execution remains disabled; AI stays offline research only.
- Strategy Core paper path is unchanged by this correction.
- Import verification and the 41-test API/decision suite: PASS on exact SHA.
- Full repository suite, full F4 risk-engine/ledger/Kill Switch audit, T0/T1/T2 integration, runtime, deployment, VPS, canonical database, exchange connectivity, paper trading and production readiness: NOT VERIFIED / OUT OF SCOPE.
- No dependencies were installed. No canonical T0 data, database, runtime, VPS, exchange or real-order path was accessed or changed.
- Live trading remains prohibited. `AI_EXECUTION_ENABLED=false` remains mandatory.

## Next step

Preserve this evidence on `main`. Do not expand into F4-R1/R2/R3, runtime, deployment, T0/T1/T2 integration, or paper operation without a separate bounded approval.
