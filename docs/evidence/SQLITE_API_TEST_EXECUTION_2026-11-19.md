# T0 SQLite/API Isolated Test Execution — 2026-11-19

## Run identity

- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Workflow: `T0 SQLite API isolated tests`
- Run: [44443686889](https://github.com/kenznguyen/btcquant-application/actions/runs/44443686889)
- Run ID: `44443686889`
- Event: `workflow_dispatch`
- Workflow HEAD / run head SHA: `f024a233c6756e219c645083dc41cc6caa8f5967`
- Workflow file: `.github/workflows/t0-sqlite-api-isolated.yml`
- Workflow file blob: `53411a017a977108f4ef4710647701f38147f8fe`
- Exact checked-out test source SHA: `32aaa78a6a8da2ef04c98c7f5ef4c7a4be2afb6f`
- Run attempt: 1
- Started: `2026-11-19T02:21:17Z`
- Completed: `2026-11-19T02:21:29Z`
- Workflow conclusion: `success`
- Job ID: `135290502856`; job conclusion: `success`
- Runner: GitHub-hosted `ubuntu-24.04`, Ubuntu `24.04.5`, Linux x64; runner image `20261111.370.1`.

## Pinned execution inputs and preflight

- Python image: `python:3.12.16-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`.
- Pulled image identity: `sha256:313cf8f190a1abab00472c1f0c950c10486c22114bcd8aef2a8198fb587a6d18`; RepoDigest matches the pinned index digest.
- Python runtime: `3.12.16`.
- Docker server: `28.0.4`.
- Checkout action commit: `3d3c42e5aac5ba805825da76410c181273ba90b1`.
- Upload-artifact action commit: `cf430e030ddbb5b0abf93d22962f4752f3646cd9`.
- Exact source SHA checkout and verification: PASS.
- Docker image pull and immutable digest check: PASS.
- Network probe: PASS; test container exposed loopback only; test execution used Docker `--network none`.
- Test container also used read-only root/source, UID `65534:65534`, dropped capabilities, no-new-privileges, bounded memory/CPU/PIDs and temporary filesystem.
- No credentials were passed into the test container; no canonical database mount.
- Checkout, Docker image pull and artifact upload occurred outside the isolated test container and required runner network. Do not characterize the entire GitHub job as network-disabled.

## Test scope and results

Command:
```bash
python -m unittest -v \
  market_data.test_feeder_recovery \
  market_data.test_feeder_lease \
  market_data.test_write_gateway \
  market_data.test_storage \
  market_data.test_sync \
  market_data.test_api
```

| Module | Tests |
|---|---:|
| `market_data.test_feeder_recovery` | 10 |
| `market_data.test_feeder_lease` | 10 |
| `market_data.test_write_gateway` | 11 |
| `market_data.test_storage` | 7 |
| `market_data.test_sync` | 10 |
| `market_data.test_api` | 13 |
| **Total** | **61** |

Runtime summary from artifact `unittest.log`:
```
Ran 61 tests in 0.796s

OK
```

- Discovered/executed: 61
- Passed: 61
- Failed: 0
- Skipped: 0
- Test process exit code: 0
- Workflow/job conclusion: SUCCESS.

## Artifact and payload verification

- Artifact name: `t0-sqlite-api-test-evidence`
- Artifact ID: `14491519041`
- Size: 3,153 bytes
- GitHub artifact digest: `sha256:15449d69e5295c6f399fd8a4b588c4fa15ef539b40faf413301f7497143cba86`
- Downloaded ZIP payload was inspected and locally hashed; SHA-256 matches GitHub artifact digest.
- Expiry: `2026-12-03T02:21:26Z`
- ZIP contents: `container_image.txt`, `network_isolation.txt`, `python_version.txt`, `runner_metadata.txt`, `unittest.log`.
- Artifact payload confirms source SHA, run ID, Python version, network probe, 61 tests and exit code 0.

## Scope boundaries and interpretation

This PASS applies only to the six named SQLite/API unittest modules at the exact source SHA above, executed in the recorded disposable container.

Not tested or certified by this run:
- T0 live Feeder/API runtime or current VPS state.
- Canonical T0 database integrity, contents, freshness or production data.
- PostgreSQL/TimescaleDB migrations or integration tests.
- Binance connectivity, exchange ingestion or live market-data collection.
- T1/T2 integration, Shared Risk Engine, ledgers, strategy behavior or trading.
- Deployment, production readiness or live execution.

No source code, tests, dependencies, workflow, schema, canonical data, runtime, VPS or trading behavior was modified by this execution.

## Verdict

- Workflow execution: PASS.
- Exact source checkout: PASS.
- Docker/Python preflight: PASS.
- Test-container network isolation probe: PASS.
- Six-module SQLite/API suite: PASS — 61/61.
- Artifact download and payload digest verification: PASS.
- T0 runtime/canonical data/production: NOT VERIFIED / NOT CERTIFIED.
- PostgreSQL/TimescaleDB: OUT OF SCOPE / NOT RUN.

## Next step

Record this run and artifact in the active handoff. Preserve the exact source SHA and test scope. Any broader T0 runtime, canonical-data, PostgreSQL, integration or production validation requires its own bounded review and approval.
