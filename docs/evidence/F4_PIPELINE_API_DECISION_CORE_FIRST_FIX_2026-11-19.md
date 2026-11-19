# F4 Pipeline API / Decision — Core-First enforcement fix and isolated verification

Date: 2026-11-19  
Repository: `kenznguyen/btcquant-application`  
Branch: `main`

## Approved scope

Owner approved two bounded corrections:

1. The AI offline-research regression now captures the SQLite table set before calling `GET /v1/decision`, then verifies the decision returns `WAIT` with no intent and that the table set remains unchanged. It also verifies `paper_orders` is not created. The fixture deliberately has no initialized Paper Ledger, so `GET /v1/paper` is not a valid source of a position snapshot in this test.
2. The Core-First API guard now rejects an exact `{"source":"AI"}` request to `POST /v1/paper/evaluate` immediately after request-body parsing, before store checks, `control_permit()`, Ledger initialization, or strategy evaluation.

The AI paper-denial regression asserts HTTP 403 `AI_EXECUTION_DISABLED`, no calls to `control_permit()`, `ledger()`, `decide()`, or `core_decide()`, and no SQLite table-set changes.

## Final source and workflow provenance

- Implementation commit: `41612cd29cf64f197e407bd89b69844329aa1504`.
  - `pipeline/api.py` blob: `57b9c1ee3f09eef2691d3967ec5fb06665c2712f`.
- Final regression-test and workflow commit: `dacb488869d000346de0b51ec96a0efa027c04a0`.
  - Parent: `9b91ac93d1b929f1fe40f8158101e9fe27a0e278`.
  - Final `pipeline/test_api.py` blob: `4fb30360d49d4d6645cfc0ff55792769aaa697c3`.
  - Final workflow blob `.github/workflows/f4-pipeline-core-first-isolated.yml`: `f2bceb682dea2cfaeaa8d85b6e2826f193327f11`.
  - `pipeline/test_decision.py` unchanged blob: `6781f26d66635f56662a627bdd3b4a63f26c1f28`.
- The workflow checks out the exact event commit via `github.sha`, verifies the eight expected source-file blob SHAs, and records the same exact source/workflow HEAD: `dacb488869d000346de0b51ec96a0efa027c04a0`.

## Final GitHub Actions verification

- Workflow run: [44462955773](https://github.com/kenznguyen/btcquant-application/actions/runs/44462955773)
- Job ID: `135353879032` — SUCCESS.
- Run HEAD / exact checked-out source: `dacb488869d000346de0b51ec96a0efa027c04a0`.
- Runner: GitHub-hosted `ubuntu-24.04`, observed Ubuntu `24.04.5`; Docker `28.0.4`.
- Test image: `python:3.12.16-slim-bookworm`, immutable digest `sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`; runtime Python `3.12.16`.
- Exact source commit and all eight source blob checks: PASS.
- Imports `pipeline.api`, `pipeline.test_api`, `pipeline.test_decision`: PASS.
- Test-container network isolation probe (loopback only): PASS. Test container used `--network none`, read-only source mount, non-root user, no secrets and no canonical DB mount.
- Command: `python -m unittest -v pipeline.test_api pipeline.test_decision`.
- Result: `Ran 41 tests in 0.180s`; `OK`; 41 passed, 0 failed.
- AI paper-denial regression: PASS.
- AI offline research WAIT/no-intent/no-SQLite-table-mutation regression (baseline captured before the request): PASS.
- Artifact: `f4-pipeline-api-decision-evidence`; ID `14500971316`; size 2,686 bytes; SHA-256 `219cd239ea34cac795a5ead12b794fce5a27e64fbbd99cbee0f2893badeb6764`; expires `2026-12-03T05:07:38Z`.
- Artifact URL: https://github.com/kenznguyen/btcquant-application/actions/runs/44462955773/artifacts/14500971316

## Diagnostic attempts and supersession

- Run [44461789268](https://github.com/kenznguyen/btcquant-application/actions/runs/44461789268), old pinned source `290bbefb3bfe98f6a13c053ec181ec3d556f27c0`: 39/41 passed, two failures. One exposed the early SQLite rate-budget write before the AI guard; the other used a stale response assumption.
- Run [44462551878](https://github.com/kenznguyen/btcquant-application/actions/runs/44462551878), source `41612cd29cf64f197e407bd89b69844329aa1504`: 40/41 passed; the updated test assumed a dual-ledger response not present in this uninitialized fixture.
- Run [44462689960](https://github.com/kenznguyen/btcquant-application/actions/runs/44462689960), source `ce5da75a164dbcf5b541bdd558daa370a4637d73`: 41/41 passed, but final review found the research test captured its SQLite baseline after the request. That run is superseded as proof of no request-side mutation.
- The final test moved the baseline capture before `GET /v1/decision`; run [44462955773](https://github.com/kenznguyen/btcquant-application/actions/runs/44462955773) is the authoritative exact-SHA PASS.

## Status and limits

- Core-First API AI-paper rejection ordering: PASS (isolated regression evidence).
- AI paper execution remains disabled; AI remains offline research only.
- Strategy Core paper path is unchanged by this correction.
- Import verification and the 41-test API/decision suite: PASS on exact SHA.
- Full repository suite, full F4 risk-engine/ledger/Kill Switch audit, T0/T1/T2 integration, runtime, deployment, VPS, canonical database, exchange connectivity, paper trading and production readiness: NOT VERIFIED / OUT OF SCOPE.
- No dependencies were installed. No canonical T0 data, database, runtime, VPS, exchange or real-order path was accessed or changed.
- Live trading remains prohibited. `AI_EXECUTION_ENABLED=false` remains mandatory.

## Next step

Preserve this evidence on `main`. Do not expand into F4-R1/R2/R3, runtime, deployment, T0/T1/T2 integration, or paper operation without a separate bounded approval.
