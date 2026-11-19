# GitHub Actions Workflow Proposal — Isolated T0 SQLite/API Tests

Date: 2026-11-19

## 1. Purpose and authority boundary

This is a **review proposal only**. It is not an active workflow and does not authorize creating `.github/workflows/`, enabling Actions, dispatching a run, installing packages, or expanding the test scope.

Repository: `kenznguyen/btcquant-application`  
Branch: `main`  
Repository HEAD inspected for this proposal: `99aa7f8922168eb7c7a7f14416ef4ef6a8f1fa64`  
Previously owner-approved test source SHA: `32aaa78a6a8da2ef04c98c7f5ef4c7a4be2afb6f`

## 2. Exact workload

Run only these six unittest modules:

1. `market_data.test_feeder_recovery`
2. `market_data.test_feeder_lease`
3. `market_data.test_write_gateway`
4. `market_data.test_storage`
5. `market_data.test_sync`
6. `market_data.test_api`

Static inventory: 61 test methods. The count must be rediscovered and reported by the actual run; 61 is not a test result.

Proposed command:

```bash
python -m unittest -v \
  market_data.test_feeder_recovery \
  market_data.test_feeder_lease \
  market_data.test_write_gateway \
  market_data.test_storage \
  market_data.test_sync \
  market_data.test_api
```

No PostgreSQL/TimescaleDB test, exchange test, integration against a running service, or other test module is in scope.

## 3. Proposed execution design

- Trigger: manual `workflow_dispatch` only. No push, pull-request, schedule or deployment trigger.
- Runner: GitHub-hosted ephemeral `ubuntu-24.04`; never self-hosted or VPS.
- Permissions: `contents: read` only; no repository secrets or environment secrets.
- Checkout: exact approved immutable source SHA `32aaa78a6a8da2ef04c98c7f5ef4c7a4be2afb6f`; verify `git rev-parse HEAD` equals that SHA before tests.
- Test runtime: run Python in a Docker container with `--network none`, read-only workspace mount, read-only container root, temporary `/tmp`, no credentials, and resource limits. This isolates the test process and child processes from external networking. Checkout and image retrieval happen before test execution on the hosted runner; artifact upload happens after execution. Do not describe the entire job as network-disabled.
- Python: minimum requirement is >=3.10 based on static syntax inspection. Proposed interpreter line is Python 3.12, but the exact patch image and immutable image digest must be selected and verified before workflow approval. No dependency installation is proposed.
- Docker image: use an official Python slim image pinned by immutable digest, not a floating tag. The digest is deliberately unresolved in this proposal.
- Environment: do not pass `MARKET_DATA_TOKEN`, `DATABASE_URL`, PostgreSQL DSN, exchange API credentials, trading flags or any secrets. Do not mount host home, Docker socket, canonical database, runtime directories or external volumes.
- SQLite: tests may write only to their test-owned temporary directories inside the container's temporary filesystem.
- Logs: retain complete unittest output as a workflow artifact; report discovered, passed, failed, skipped counts and process exit code.

## 4. Workflow skeleton — NOT READY TO INSTALL

The following is design pseudocode, not a valid deployable workflow. Action references and image digest must be pinned before use.

```yaml
name: T0 SQLite API Isolated Tests

on:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  sqlite-api-tests:
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    steps:
      - name: Checkout approved source
        uses: actions/checkout@<PINNED_COMMIT_SHA>
        with:
          ref: 32aaa78a6a8da2ef04c98c7f5ef4c7a4be2afb6f
          persist-credentials: false

      - name: Verify exact source revision
        shell: bash
        run: |
          test "$(git rev-parse HEAD)" = "32aaa78a6a8da2ef04c98c7f5ef4c7a4be2afb6f"

      - name: Prepare isolated test output
        run: mkdir -p "$RUNNER_TEMP/t0-test-artifacts"

      - name: Run only approved tests without network
        shell: bash
        run: |
          docker pull python:3.12-slim@sha256:<VERIFIED_IMAGE_DIGEST>
          docker run --rm --network none \
            --read-only --cap-drop ALL --security-opt no-new-privileges \
            --pids-limit 128 --memory 2g --cpus 2 \
            --tmpfs /tmp:rw,nosuid,nodev,size=256m \
            -e HOME=/tmp -e PYTHONDONTWRITEBYTECODE=1 \
            -e PYTHONPATH=/workspace \
            -v "$GITHUB_WORKSPACE:/workspace:ro" \
            -v "$RUNNER_TEMP/t0-test-artifacts:/artifacts:rw" \
            -w /workspace \
            python:3.12-slim@sha256:<VERIFIED_IMAGE_DIGEST> \
            sh -lc 'python -m unittest -v market_data.test_feeder_recovery market_data.test_feeder_lease market_data.test_write_gateway market_data.test_storage market_data.test_sync market_data.test_api 2>&1 | tee /artifacts/unittest.log'

      - name: Upload test log
        if: always()
        uses: actions/upload-artifact@<PINNED_COMMIT_SHA>
        with:
          name: t0-sqlite-api-test-log
          path: ${{ runner.temp }}/t0-test-artifacts/unittest.log
          if-no-files-found: error
```

Implementation review must additionally ensure shell pipeline failure propagation (`set -o pipefail`), correct artifact path expression, action commit pins, image digest, and a trustworthy test-count summary. Do not copy this skeleton directly into the repository.

## 5. Preconditions / unresolved items

| Item | Current status |
|---|---|
| Exact test source SHA | Known: `32aaa78a6a8da2ef04c98c7f5ef4c7a4be2afb6f` |
| Six module paths | Present in current main inventory |
| Static test inventory | 61 methods; runtime discovery not verified |
| Python minimum | Static inference >=3.10 |
| Exact Python patch release | NOT VERIFIED |
| Official image immutable digest | NOT VERIFIED |
| GitHub Action immutable commit pins | NOT VERIFIED |
| Docker availability on selected hosted runner | Must be preflighted; fail closed if unavailable |
| Network isolation of test process | Proposed via Docker `--network none`; must be verified in workflow |
| Test execution | NOT RUN |
| CI workflow | NOT CREATED |

## 6. Evidence to retain

For any separately approved run, record:
- workflow file commit SHA and workflow run ID/URL;
- exact checked-out source SHA;
- runner image/OS and Python image digest/version;
- exact command and test discovery count;
- passed/failed/skipped counts, exit code and complete log artifact;
- evidence that the test container had no network and had no credentials or canonical DB mounts.

A green workflow badge alone is insufficient evidence.

## 7. Status and next gate

- Proposal preparation: **PASS**
- Workflow implementation: **NOT AUTHORIZED**
- Workflow dispatch: **NOT AUTHORIZED**
- Test execution: **NOT RUN**
- Runtime/canonical DB/exchange/VPS/live trading: **NOT ACCESSED**
- Production readiness: **NOT CERTIFIED**

Next gate: owner reviews and explicitly approves this exact workflow design, including Python image digest, action commit pins and the network-isolation preflight. Only then may the workflow file be created on the existing `main` branch. No branch/PR is proposed.
