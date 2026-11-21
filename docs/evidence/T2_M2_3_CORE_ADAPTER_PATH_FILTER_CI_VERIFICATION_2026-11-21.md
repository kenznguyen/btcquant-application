# T2 Core Adapter CI path-filter correction — verification evidence

Date: 2026-11-21
Repository: `kenznguyen/btcquant-application`
Branch: `main`

## Scope

Verify the bounded workflow-only correction that adds `pipeline/core_signal.py` and `pipeline/values.py` to the `on.push.paths` filter for `.github/workflows/t2-core-adapter-green.yml`.

No production code, tests, risk policy, runner, ledger, T0/T1, AI, database, runtime, deployment or trading behavior was changed in this increment.

## Source identity

- Workflow correction commit / tested HEAD: `3455d126688b827be4ad4819d1a3695af4997899`
- Workflow blob: `88a2ff4c2795e0fffd5977ce21372219952f364a`
- Parent: `77531b34f8a8e0befe0ef11c2039f8437de0a949`
- Commit diff: exactly two additions, zero deletions; adds only `pipeline/core_signal.py` and `pipeline/values.py` to `on.push.paths`.

## GitHub Actions evidence

- Run: [44899616076](https://github.com/kenznguyen/btcquant-application/actions/runs/44899616076)
- Event: `push`
- Workflow: `T2 Core Adapter GREEN tests`
- Status / conclusion: `completed / success`
- Run HEAD SHA: `3455d126688b827be4ad4819d1a3695af4997899`
- Job: `core-adapter-contract`, ID `136832564520`, success.
- Steps: checkout exact source, verify immutable blobs, pull pinned Python image, run tests, upload evidence — all completed successfully.
- Test result: **10/10 PASS**.
  - Six Core Adapter contract tests.
  - Four Adapter → canonical Validator parity tests.
  - Includes BUY/SELL/CLOSE mapping, WAIT non-intent, expired-intent denial and wrong-market denial.
- Test command: `python -m unittest -v core_runtime.test_adapter_contract core_runtime.test_adapter_validator_parity`
- Python image: `python:3.12.16-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`
- Container restrictions: `--network none`, read-only root/workspace, no credentials, no database mount, no exchange access; capabilities dropped, no-new-privileges, resource limits applied.
- Exact asserted source blobs:
  - Adapter: `9795c346d2eec4c78c22035c32f463af6b40b8f4`
  - Contract tests: `fbe6cc428fd7058a6dbefd9eaec1979a95638474`
  - Parity tests: `8f3c4dfa29f371334ded3486ca83f9a5ea7f974e`

## Artifact

- Name: `t2-core-adapter-green-evidence`
- Artifact ID: `14705387230`
- Size: 982 bytes
- SHA-256: `2ae613a169847afad52b8de9a6274a22484ec36adb46aec5dda36db678ea8c4a`
- Download URL: https://github.com/kenznguyen/btcquant-application/actions/runs/44899616076/artifacts/14705387230
- Artifact downloaded and independently hashed; local SHA-256 matched GitHub's artifact digest. Contents: `green-test.log` and `metadata.txt`; both confirm 10 tests, PASS, exact HEAD and isolation metadata.
- Retention expiry reported by GitHub: 2026-12-05T11:33:03Z.

## Verdict and limits

- Workflow correction source: **PASS** — both required dependency paths are present in the exact workflow blob.
- Workflow execution on the correction commit: **PASS** — run 44899616076 completed successfully.
- Focused Adapter/Validator tests on the correction commit: **PASS — 10/10**.
- CI path-filter behavioral exercise: **PARTIAL / NOT DIRECTLY VERIFIED**. The run was triggered by a push changing the workflow file itself; it did not simulate a separate push changing only `pipeline/core_signal.py` or only `pipeline/values.py`. Their inclusion in the exact workflow configuration is verified, but a dedicated trigger exercise was not performed.
- Full repository regression: **NOT RUN**.
- Genuine independent second-person review: **NOT VERIFIED**. This evidence closes the specific missing-path review finding at source/config level; it is not a human independent review.
- Optional malformed/unhashable action hardening: **NOT IMPLEMENTED** and remains outside this approval.
- No runtime, DB, T0/T1 integration, AI admission, paper order submission, live trading or real orders are authorized by this CI result.

## Next

Preserve the bounded PASS evidence. Before treating trigger behavior as fully exercised, separately approve and run a controlled path-filter trigger test (or equivalent workflow-level test) for dependency-only changes. Do not expand into runtime, ledger, risk policy or trading work without separate approval.
