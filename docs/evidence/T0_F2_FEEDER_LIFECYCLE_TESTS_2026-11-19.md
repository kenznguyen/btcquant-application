# T0 F2 Feeder Lifecycle Test Coverage — 2026-11-19

## Approval and scope
- Owner explicitly approved **test-only F2** on the existing `main` branch.
- Authorized changes: add `market_data/test_feeder_lifecycle.py`, update the existing isolated SQLite/API workflow, execute CI, and preserve evidence/handoff.
- No application source behavior, runtime composition, storage schema, dependencies, canonical data or production configuration was changed.
- Excluded: PostgreSQL/TimescaleDB, Binance/exchange, canonical database, VPS/systemd/deployment, T1/T2, strategy/risk/ledger/trading.

## Implementation
- New test module: `market_data/test_feeder_lifecycle.py`.
- Final test source commit: `2668dd538a99d6021921432b3485f4ed84198364`.
- Test file blob: `f10de15b11ca00f6a4946c3877062cfb5dbd1442`.
- Source commit changed only that test file; no production source files changed.
- 28 new test methods:
  - RetryPolicy: 6 tests — transient/non-transient classification, bounded attempts, exponential delay, deterministic jitter/5xx, Retry-After authority and malformed Retry-After rejection.
  - FeederScheduler: 10 tests — close-grace boundary, independent M15/H1 watermarks, failed sync/gap behavior, partial timeframe success, duplicate admission, stop admission, idle/drain, background thread start/stop, and stopping while a sync is in flight.
  - FeederRuntime: 12 tests — lease unavailable, recovery fail-closed, startup order, startup exception cleanup, lease checks before run/write, heartbeat lease loss, health readiness transitions, shutdown drain ordering/timeout, fencing-generation safety, and retry re-authorization.
- Tests use deterministic clocks, fake collaborators, events and temporary/in-memory state. No production composition or external service is started. No new dependency was added.

## Workflow
- Existing workflow: `.github/workflows/t0-sqlite-api-isolated.yml`.
- Final workflow commit: `44ed95bf55903cc4055849e5d263d514dfa66ef0`.
- Workflow blob: `9d38afd7f1e686dda07a41465a2f4287526e9347`.
- Seven explicit modules; expected count 91 (prior 63 + 28 F2 cases).
- Exact checkout pin: `2668dd538a99d6021921432b3485f4ed84198364`.
- Existing manual `workflow_dispatch` and push-to-main trigger retained.
- GitHub-hosted `ubuntu-24.04`; Docker test container uses `--network none`, read-only source, non-root user, resource caps, no credentials and no canonical database mount.
- Python image pinned to `python:3.12.16-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`.

## Final verification — PASS
- GitHub Actions run [44447104778](https://github.com/kenznguyen/btcquant-application/actions/runs/44447104778), attempt 1, event `push`, branch `main`.
- Workflow/head SHA: `44ed95bf55903cc4055849e5d263d514dfa66ef0`.
- Job `Seven-module SQLite/API and feeder lifecycle suite`, ID `135301901223`: **SUCCESS**.
- Exact checked-out source SHA: `2668dd538a99d6021921432b3485f4ed84198364`.
- Runtime: Python `3.12.16`; Ubuntu `24.04.5`; Docker `28.0.4`.
- Result: **91/91 PASS**, 0 failures, 0 skipped; `Ran 91 tests in 1.609s`; exit code 0.
- Network probe: `PASS (loopback only)`; test container network mode `none`.
- Artifact: `t0-sqlite-api-test-evidence`, ID `14493447610`, 4,019 bytes.
- GitHub artifact digest: `sha256:f5fceef0b15c831c7fe050d4a563529d9a306c9f005624840af4fbc5f068eda0`.
- Downloaded ZIP SHA-256 independently computed and matched exactly: `f5fceef0b15c831c7fe050d4a563529d9a306c9f005624840af4fbc5f068eda0`.
- Artifact payload inspected: runner metadata, unittest log, network probe, Python version and image identity. Metadata confirms 7 modules, 91 tests, exact source SHA, exit 0, no credentials and no canonical DB mount.

## Iteration history retained
- Earlier run [44446709035](https://github.com/kenznguyen/btcquant-application/actions/runs/44446709035) and run [44446734889](https://github.com/kenznguyen/btcquant-application/actions/runs/44446734889) failed five scheduler fixture assertions because the initial test fixture initialized the scheduler watermark at the later test time. This was a test-fixture defect, not a production source defect.
- Corrected scheduler clock setup in test source commit `c664fa9a46ce415b42e1ae6368c205e37a6c9dfb`; subsequent run [44446757387](https://github.com/kenznguyen/btcquant-application/actions/runs/44446757387) passed 87/87.
- Expanded tests to cover real scheduler thread/drain and health callbacks; run [44446901653](https://github.com/kenznguyen/btcquant-application/actions/runs/44446901653) passed 90/90.
- Added explicit HTTP 5xx + deterministic jitter bound test; final source/workflow and final 91/91 run are recorded above. Earlier failed attempts remain visible and were not relabeled PASS.

## Review and limits
- Static review of the test-only change: PASS; no blocking issue identified. The suite exercises the declared RetryPolicy/Scheduler/Runtime contracts with fakes and deterministic controls.
- This verifies isolated tests and test harness behavior only. It does not certify canonical database state, live feeder runtime, Binance connectivity, actual deployment, HTTP server/proxy behavior, PostgreSQL/TimescaleDB, T1/T2 integration or trading.
- F2 status: **PASS within the approved test-only scope**.
- F1 and F3 remain PASS on their previously recorded source snapshots.
- F4 remains NOT VERIFIED. Production/runtime remains NOT CERTIFIED.
