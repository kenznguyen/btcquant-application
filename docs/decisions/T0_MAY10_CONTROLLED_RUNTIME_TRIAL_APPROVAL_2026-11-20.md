# T0 MAY-10 Controlled Runtime Trial Approval — 2026-11-20

## Owner decision

The owner explicitly approved selecting a configuration, deploying and activating T0 on MAY-10 for a controlled test.

The owner subsequently confirmed the initial data mode:
- Create a **new, empty, isolated SQLite test database** on MAY-10.
- Start collecting **newly closed BTCUSDT USD-M M15 and H1 candles** from Binance through the existing CCXT public market-data path.
- Do not import the 404 archive objects, reconstruct historical data, restore the deleted database, or copy any prior Canonical SQLite asset into this test database.

## Approved test configuration

- Host: MAY-10, currently a Windows test PC.
- Proposed runtime: WSL2 Ubuntu, CPython 3.12, Linux x86_64, subject to read-only host preflight and successful platform/dependency qualification.
- Storage: SQLite only, at a new dedicated test-only path on the WSL Linux filesystem.
- Processes: one manually started T0 feeder and one local read-only FastAPI/Uvicorn API.
- API binding: loopback only; no public ingress and no LAN exposure.
- Data: Binance USD-M BTCUSDT, closed M15 and H1 candles only; public endpoints, no exchange API keys.
- Service control: manual start/stop only; no systemd, Windows service, Task Scheduler, login/startup autostart or persistent supervisor in this trial.
- Trading: no order placement; no T1/T2 connection; no Strategy Core or AI execution.

## Required gates before activation

1. Read-only MAY-10 preflight: Windows build, CPU architecture/virtualization, RAM, disk capacity, WSL2 state, distro/kernel, and filesystem location/permissions.
2. Verify exact application source SHA and clean checkout in the test environment.
3. Verify CPython 3.12 and hash-enforced dependency installation against the committed Linux x86_64 locks.
4. Verify the new database target is owner-controlled, local to the WSL Linux filesystem, separate from any prior/canonical/archive data, absent, and create-only.
5. Create only the new empty test SQLite database using the explicit empty-only initializer; verify schema, zero rows, and integrity.
6. Start exactly one feeder; verify lease ownership/fencing, heartbeat, recovery and new M15/H1 ingestion.
7. Start the read-only API on loopback; verify authentication and bounded candle reads.
8. Stop both processes manually and verify clean shutdown and restart behavior before any longer test window.

Any failed or unverifiable gate is BLOCKED; stop without selecting an alternate data path or silently weakening a control.

## Explicit exclusions

- No access to, modification of, migration of, or replacement of the former Canonical SQLite database.
- No Binance archive object retrieval/materialization, archive import, REST tail retry/bypass, or historical reconstruction.
- No PostgreSQL/Timescale activation.
- No Dropbox/OneDrive-synchronized database path.
- No T1 collector, T1 HTTP Provider, T2, dashboard, strategy execution, paper orders or real orders.
- No systemd, Windows service, Task Scheduler, autostart, persistent supervisor or unattended 24/7 operation.
- No public/LAN API binding, firewall exposure, reverse-proxy deployment or remote access.
- No deletion/cleanup of source data or test evidence.

## Current status at approval

- Owner authorization: **APPROVED** for the bounded MAY-10 controlled T0 runtime trial described above.
- Host preflight: **NOT RUN**.
- WSL2/Linux runtime qualification: **NOT VERIFIED**.
- Empty SQLite test database: **NOT CREATED**.
- Feeder/API: **NOT STARTED**.
- Live market-data ingestion: **NOT STARTED**.
- CI evidence: prior isolated Linux CI results remain CI-only and do not prove MAY-10 runtime success.
- Source provenance at decision recording: repository main HEAD observed as `44dd517887caf256f293fc502d56afbbba124d29`; this is not yet the deployed SHA.
- Workflow run/artifact: none for this decision.

## Next action

Run a read-only MAY-10 host preflight. Do not install WSL components, create directories/databases, install dependencies, or start services until the preflight is reviewed and the exact runtime target is confirmed.
