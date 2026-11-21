# T2 M2.3 — Core Adapter → Validator parity tests — 2026-11-21

## Scope and approval

Owner approved a bounded TDD increment to add adapter-to-validator parity tests. Scope is limited to tests and their focused GitHub Actions workflow. No production behavior or risk policy changes were approved or made.

Repository: `kenznguyen/btcquant-application`  
Branch: `main`  
Final tested source SHA: `ca9f01902cd1e3b5f22ccecce7cd347077924f90`

## Exact files and blobs

- `core_runtime/adapter.py`: unchanged, blob `9795c346d2eec4c78c22035c32f463af6b40b8f4`
- `core_runtime/test_adapter_contract.py`: unchanged, blob `fbe6cc428fd7058a6dbefd9eaec1979a95638474`
- `core_runtime/test_adapter_validator_parity.py`: added, blob `8f3c4dfa29f371334ded3486ca83f9a5ea7f974e`
- `pipeline/core_signal.py`: unchanged, blob `df5fbb59611bdd4fbb8224665f79655dd4433455`
- `pipeline/values.py`: unchanged, blob `5576376454af129b944919fb588e26c0657a781e`
- `.github/workflows/t2-core-adapter-green.yml`: updated to pin the new parity-test blob and run both focused modules; blob `5a5b70d244debcf8f5eb55733eef14d6e9661e38`

Commits:
- Test addition: `50856abeb900a0bb1b0bf346ba7fea8aaee25a5b`
- Workflow update / tested HEAD: `ca9f01902cd1e3b5f22ccecce7cd347077924f90`

## Test coverage

Four new unittest methods cover:
1. BUY, SELL and CLOSE producer reports pass through the adapter and canonical validator with the expected PAPER intent, market identity and provenance.
2. WAIT remains non-intent through both layers.
3. Expired intent is denied by the canonical validator.
4. Wrong-symbol intent is denied by the canonical validator.

The six existing adapter-only tests remain in the same focused job. Total: 10 unittest methods.

## CI evidence

<badge>PASS</badge>

- GitHub Actions run [44896160495](https://github.com/kenznguyen/btcquant-application/actions/runs/44896160495)
- Workflow: T2 Core Adapter GREEN tests
- Run HEAD: `ca9f01902cd1e3b5f22ccecce7cd347077924f90`
- Job: `136822153930` — `core-adapter-contract`, conclusion `success`
- Log: all six existing tests and four new parity tests report `ok`; `Ran 10 tests`; `OK`
- Python image: `python:3.12.16-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`
- Artifact: `14703678692`
- Artifact SHA-256: `1ce726534fe995a3b0061a50d35a98618213135b2f12e1e84471df88a0d37ebe`
- Workflow execution used `--network none`, read-only workspace, no database mount, no exchange connection and no credentials passed into the test container.

## Verdict

**PASS — adapter-to-validator parity tests and focused CI.**

This closes the specific missing test-coverage finding from the technical review. It does not independently prove all Core producer behavior, does not constitute a genuine second-person review, and does not make the adapter slice fully independently approved.

## Remaining status and limits

- Independent second-person review: **NOT VERIFIED**.
- Full repository regression suite: **NOT RUN** in this increment.
- Optional malformed/unhashable action hardening: **NOT IMPLEMENTED**; outside the approved required parity-test scope.
- Core leverage/sizing semantics: **BLOCKED**, unchanged.
- Runner, Ledger, Shared Risk Engine integration, AI Strategy, T1/T0 integration, runtime, DB, deployment and trading: **NOT ACCESSED / NOT AUTHORIZED**.
- Next: request genuine second-person review of exact tested blobs `9795c346...`, `fbe6cc42...`, `8f3c4dfa...` and `df5fbb59...`. Any further behavior changes require separate bounded approval.
