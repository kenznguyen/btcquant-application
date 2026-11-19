# T0 SQLite isolated workflow rerun — 2026-11-19

## Scope
- Verify the Bash Step Summary fix in the isolated SQLite/API GitHub Actions workflow.
- Preserve the exact approved test source SHA and six-module scope.
- No application source, test source, SQLite schema/canonical data, PostgreSQL/TimescaleDB, Feeder/runtime, VPS, exchange, T1/T2 or trading changes/access.

## Workflow run
- Run: [44445216380](https://github.com/kenznguyen/btcquant-application/actions/runs/44445216380), attempt 1, event `workflow_dispatch`, branch `main`.
- Workflow: `.github/workflows/t0-sqlite-api-isolated.yml`.
- Workflow/head SHA: `6f31776ab51aeb6b872d3031fda692b6f44d277f`.
- Job: `Six-module SQLite/API suite`, job ID `135295597442`, conclusion **SUCCESS**.
- All substantive steps succeeded: exact checkout, source preflight, Docker/image preflight, Python/network isolation, test execution, artifact upload.

## Bash Step Summary verification
- Executed summary block uses `printf '%s\\n'` with no Markdown backticks in its arguments.
- Job log contains the executed `printf` block and append to `GITHUB_STEP_SUMMARY`.
- Job log search: `command not found` occurrences = **0**.
- The Step Summary generation step/job completed successfully. This resolves the prior shell command-substitution issue.

## Exact source and test result
- Checked-out test source SHA: `57b54116188167904e2a2a6020ab349588b42186` (verified in checkout logs and artifact metadata).
- Six approved modules: recovery, lease, write gateway, storage, sync, API.
- Result: **62 passed, 0 failed, 0 skipped**; `Ran 62 tests in 0.793s`; unittest result `OK`; test process exit code 0.
- F1 regression `test_gateway_rejects_valid_candles_schema_when_lease_table_is_missing`: **PASS**.
- Runner: GitHub-hosted `ubuntu-24.04`, Ubuntu 24.04.5, Linux x64; Docker 28.0.4.
- Test image: `python:3.12.16-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`; Python `3.12.16`.
- Docker test container used `--network none`; network interface probe **PASS (loopback only)**.
- No credentials passed to test container; no canonical database mount. Test source mounted read-only. Checkout/image pull/artifact upload are runner-side network operations outside the isolated test container.

## Artifact verification
- Artifact: `t0-sqlite-api-test-evidence`, ID `14492143534`, size 3,184 bytes, expiry `2026-12-03T02:33:54Z`.
- GitHub artifact digest: `sha256:c44d2b9915a8a2d7b1d198c6e254ce973e3ea8717157149be447ae9166425468`.
- Downloaded ZIP SHA-256 independently computed: `c44d2b9915a8a2d7b1d198c6e254ce973e3ea8717157149be447ae9166425468`; exact match **PASS**.
- ZIP inspected; five files: `container_image.txt`, `network_isolation.txt`, `python_version.txt`, `runner_metadata.txt`, `unittest.log`. Metadata and unittest log agree with the run and counts.

## Status
- Bash Step Summary fix execution: **PASS**.
- Exact source checkout: **PASS**.
- Isolated six-module SQLite/API suite: **PASS (62/62)**.
- F1 schema preflight regression: **PASS**.
- Network isolation probe: **PASS**.
- Artifact upload, download, payload inspection and SHA-256 verification: **PASS**.
- F2/F3/F4 broader feeder lifecycle/page-commit/real HTTP server coverage: **NOT VERIFIED**.
- Production/live runtime/canonical DB: **NOT CERTIFIED**.

## Scope limits and next step
No PostgreSQL/TimescaleDB expansion, no runtime/Feeder deployment, no canonical DB/data access, no exchange/VPS access, no T1/T2 integration, no strategy/risk/trading execution. Preserve this exact source SHA and evidence. Any broader T0 test coverage requires a separately bounded review/approval.
