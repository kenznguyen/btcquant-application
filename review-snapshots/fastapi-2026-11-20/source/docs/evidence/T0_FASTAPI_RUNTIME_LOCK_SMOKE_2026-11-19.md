# T0 FastAPI Runtime-Lock-Only Smoke — 2026-11-19

## Scope

Close D1 by proving that the committed FastAPI **runtime** lock installs by itself in a clean CPython 3.12.16 environment, without installing the test lock, and that the resulting environment can import the ASGI application and serve the health route in-process.

This is a bounded CI verification only. It does not authorize or perform Uvicorn process startup, socket/network access, Nginx validation, VPS access, deployment, endpoint exposure, canonical database access, credentials, exchange access, or trading.

## Changes

- Added `market_data/runtime_smoke.py` as a standard-library-only ASGI smoke harness. It imports `market_data.fastapi_app.app`, sends one synthetic ASGI GET `/health` request directly to the app, and asserts HTTP 200, the exact JSON body, `Cache-Control: no-store`, and the expected JSON content type. It opens no socket.
  - Commit: `e50c5d83437d6db1b6eb15f8b75267575acde041`.
- Added an independent GitHub Actions job `runtime-lock-smoke` to `.github/workflows/t0-fastapi-migration.yml`.
  - Commit: `fe5f99d31aac832f85c1aab9ca007bd70386d9fe`.
- The job downloads wheels for `requirements-market-data-fastapi.lock` only, verifies committed lock hashes, then installs the lock offline into a new virtual environment inside a clean CPython 3.12.16 container.
- The smoke container uses `--network none`, a read-only root filesystem, non-root UID, dropped capabilities, no-new-privileges, resource bounds, and a bounded writable `/tmp`. The test lock is not installed or mounted. The repository is mounted read-only. No canonical database, credentials, exchange or external service is provided.

## Exact-SHA CI evidence

All three workflow runs below checked out exact source SHA:

`fe5f99d31aac832f85c1aab9ca007bd70386d9fe`

### D1 runtime-only install and ASGI smoke

- Workflow run [44536493461](https://github.com/kenznguyen/btcquant-application/actions/runs/44536493461).
- Job `135603190576`: **success**.
- Runtime artifact ID: `14535727293`.
- Artifact SHA-256: `607771298cf289ab9af7f8bf7918d9738fff2d400be45e3e25bba388959042da`.
- Job log confirms:
  - all 14 runtime-lock packages installed from the offline wheelhouse;
  - `pip check`: “No broken requirements found”;
  - `runtime_lock_install=PASS`;
  - `asgi_import=PASS`;
  - `in_process_health=PASS`;
  - `network_socket=not_used`;
  - `canonical_database=not_accessed`;
  - `credentials=none`.

### FastAPI contract and parity regression

- Same workflow run [44536493461](https://github.com/kenznguyen/btcquant-application/actions/runs/44536493461).
- Job `135603189986`: **26/26 PASS**.
- Artifact ID: `14536536165`.
- Artifact SHA-256: `dbdbcc79ecd8495d91d39e14160187dbda6b9618f08d501f96cf4a6111dd02cd`.
- Log confirms the same-fixture WSGI–FastAPI differential case passed and ends with `Ran 26 tests` / `OK`.

### SQLite aggregate regression

- Workflow run [44536493268](https://github.com/kenznguyen/btcquant-application/actions/runs/44536493268).
- Job `135603190883`: **196/196 PASS**.
- Artifact ID: `14536651799`.
- Artifact SHA-256: `fb0b74ec9276c7fc96c95e6c67b642079644d32d8329cb1efea9eb324462522a`.
- Log ends with `Ran 196 tests` / `OK`.

The runtime lock SHA-256 was checked against `requirements-market-data-fastapi.sha256`; expected runtime-lock digest remains `fb4cf8f63131cb36636b3c3230378a49bfb2d3a56b8750778ed5b3b5dac8d786`.

## Disposition

- D1 runtime-lock-only clean installation and in-process ASGI health smoke: **CLOSED / PASS** for the stated checks.
- FastAPI contract/parity regression: **26/26 PASS**.
- SQLite aggregate regression: **196/196 PASS**.
- Independent second-person review: **PENDING**. This implementation and CI evidence do not constitute independent review.
- WSGI/Gunicorn retirement: **NOT APPROVED**.
- Uvicorn process/socket startup, Nginx, VPS/systemd, endpoint/runtime qualification and deployment: **NOT VERIFIED / NOT AUTHORIZED**.
- Production readiness: **NOT CERTIFIED**.

## Next step and restrictions

Send the updated exact-SHA review package to a reviewer who did not author the implementation or these self-reviews. Do not remove WSGI/Gunicorn or perform endpoint/runtime/deployment work until the independent review is accepted and separate owner approval is recorded. Keep T0 canonical SQLite, writer/lease/feeder/recovery, T1/T2, PostgreSQL, retention/deletion and trading outside this change.
