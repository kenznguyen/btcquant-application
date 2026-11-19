# T0 dependency resolver and fresh-environment compatibility gate — 2026-11-19

## Scope and decision

- Repository: `kenznguyen/btcquant-application`, existing branch `main`.
- Scope is limited to the two direct dependencies in `requirements-market-data.txt`: `ccxt==4.5.92` and `gunicorn==23.0.0`.
- Standardized verification target: Python 3.12.16, matching the existing isolated T0 CI baseline.
- PostgreSQL/TimescaleDB, runtime startup, Binance network connectivity, feeder service, canonical DB/data, VPS, deployment, T1/T2 and trading are excluded.
- No production environment package installation was performed.

## Implementation

- Workflow: `.github/workflows/t0-dependency-compatibility.yml`.
- Final workflow blob: `a020aaaf8be8cce3d89e89369872f2c1f79fd66c`.
- Workflow implementation/update commits on `main`:
  - `b9388d7ecfffd570fa42291a1e2869b8aa947d6c` — initial workflow.
  - `7af2c1aac33b84c627caf6ba916ff14fad409eb7` — invoke Gunicorn through Python.
  - `80b9df9556f073a46020b09ac74b8e21889e3148` — invoke pip-compile through Python.
  - `f49fcf57c700ac85f9015230e45ce4732b0281ae` — shell-safe Python assertions.
  - `52f4dd2224bedf543816d6b145331d116c926f20` — preserve Python quoting through the shell.
  - `3a4435939e1e369c9dae82f8195d3d3de466900e` — use a separate executable tmpfs for native wheel imports.
- Workflow triggers only for changes to the T0 dependency manifest/workflow on `main`, or manual dispatch.
- Checkout is pinned to the triggering `github.sha` and checks `HEAD == GITHUB_SHA`.
- Resolver phase uses the immutable Python 3.12.16 image and configured PyPI index; `pip-tools==7.4.1` is a build-time resolver only.
- Resolver generates a SHA-256 hash-locked requirements file and downloads a wheel-only wheelhouse.
- A separate clean container installs only from that lock/wheelhouse with Docker network disabled, then runs `pip check`, exact-version assertions, imports and adapter/CLI checks.
- Both containers run non-root with read-only root filesystems, constrained resources and no credentials. The fresh-install container has no network.

## Authoritative verification

- Final workflow run: [44503844968](https://github.com/kenznguyen/btcquant-application/actions/runs/44503844968).
- Job: `135490200282`.
- Exact workflow/source checkout SHA: `3a4435939e1e369c9dae82f8195d3d3de466900e`.
- Result: **SUCCESS**. Exact checkout, dependency resolution, wheel download, offline fresh install, checks and artifact upload all completed successfully.
- Runtime image: `python:3.12.16-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`.
- Actual image ID: `sha256:313cf8f190a1abab00472c1f0c950c10486c22114bcd8aef2a8198fb587a6d18`.
- Resolver: Python 3.12.16, pip 25.0.1, pip-tools 7.4.1.
- Resolved lock: `requirements-market-data.lock`; SHA-256 `31ae8c26b418fcd21978f13fa2bf93ff14f71146c8f17ec47c685dd1df1e79b6`.
- Wheelhouse: 25 wheels; each wheel checksum was included in `wheelhouse.sha256`.
- Fresh install: `pip install --no-index --find-links ... --require-hashes`; `pip check` reported `No broken requirements found.`
- Compatibility assertions: Python 3.12.16; CCXT 4.5.92; Gunicorn 23.0.0; `ccxt.binanceusdm` available; Gunicorn import available; `python -m gunicorn --version` reported 23.0.0.
- Installed transitive package inventory and full logs are retained in the workflow artifact.

## Artifact

- Name: `t0-dependency-compatibility-evidence`.
- Artifact ID: `14518521692`.
- Size: 21,633,527 bytes.
- SHA-256: `888e942658985567b5af0b2b053fd88c269d1132634cf493038dede8ca8eaf1f`.
- Expiry: 2026-12-03T10:15:28Z.
- Artifact contains the generated lock, lock checksum, 25-wheel wheelhouse, wheel checksums, Python/container metadata, resolver log and fresh-install log. The downloaded ZIP was independently hashed; the lock SHA and wheelhouse checksums were independently verified.

## Iterations and failure analysis

The first four attempts exposed CI harness issues, not dependency conflicts. Each was corrected before the authoritative run:

1. Run `44503160449`: pip-tools console script could not execute from the user-base path. Changed invocation to `python /tmp/userbase/bin/pip-compile`.
2. Run `44503275818`: an indented here-document terminator caused a Python indentation error. Replaced it with a single-line Python assertion command.
3. Run `44503535494`: nested shell quoting removed Python string quotes. Escaped the quotes at the shell boundary.
4. Run `44503676441`: native cryptography extension could not be memory-mapped from the temporary filesystem. Moved the fresh environment's user site to a separate executable tmpfs at `/opt/venv`.
5. Run `44503844968`: final authoritative run passed all stages.

The four failed attempts are preserved as iteration history and are not acceptance evidence. No dependency incompatibility was observed in the final run.

## Status

- **PASS** — exact-SHA checkout.
- **PASS** — resolver completed for the two declared direct dependencies and their transitive dependencies.
- **PASS** — wheel-only downloads and SHA-256 lock generation.
- **PASS** — clean offline installation with hash enforcement.
- **PASS** — `pip check`, exact package versions, imports and CCXT USD-M adapter availability.
- **PASS** — artifact upload and independent artifact/lock/wheel checksum verification.
- **NOT VERIFIED** — runtime startup, actual Binance REST/WebSocket connectivity, API/feeder lifecycle, other Python versions, PostgreSQL/TimescaleDB, VPS/deployment and production readiness.

The generated lock is retained inside the run artifact rather than committed as a repository lock file in this increment. The artifact has a 14-day retention window; preserving a permanent source-controlled lock remains a separate follow-up if required.

No T0 production source, canonical data, runtime, VPS, deployment, T1/T2 or trading path was changed or accessed. No live orders were submitted.
