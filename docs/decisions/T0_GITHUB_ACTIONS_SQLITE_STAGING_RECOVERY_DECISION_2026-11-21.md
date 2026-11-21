# T0 GitHub Actions SQLite Staging Recovery Decision — 2026-11-21

## Owner decision

**APPROVED — ARCHITECTURE ONLY.**

GitHub Actions is the selected platform for the controlled recovery and validation process that may produce a disposable SQLite staging database from the approved Binance USD-M BTCUSDT archive inputs.

The long-term Canonical Data storage location and ownership arrangement are deliberately deferred until the SQLite staging result has passed its defined validation gates.

## Intended architecture

1. GitHub Actions provides a manually initiated, bounded, auditable recovery/validation pipeline.
2. Any future raw archive materialization and SQLite build occur only in an isolated, disposable staging workspace on a GitHub-hosted runner, subject to separate execution approvals and same-run preflight.
3. The staging SQLite and its evidence are validation outputs only. A workflow artifact is temporary evidence/transport, not durable Canonical storage.
4. After staging validation, the owner reviews the exact source SHA, workflow run, artifact identity/checksum, data coverage, integrity, provenance and validation results.
5. Only after a separate owner decision may a long-term Canonical storage target, ownership, backup/restore and operational lifecycle be selected.
6. Canonical T0 remains an independent data asset. Staging does not automatically become Canonical and must not overwrite, replace, merge into, or mutate any existing Canonical database.

## Approval boundaries

This decision does **not** authorize:
- creating or running any GitHub Actions workflow, including the previously proposed preflight-only workflow;
- downloading or materializing any archive object, making Binance/network requests, or creating raw staging files;
- creating, normalizing, migrating, modifying or validating a SQLite database against real archive payloads;
- using the previously approved `/srv/btcquant/staging/t0-reconstructed-btcusdt-20261120-run-001` target on an unidentified host, or treating the GitHub runner as an already-authorized replacement destination;
- using `MAY-10` (which remains excluded);
- accessing or changing Canonical T0 SQLite, Feeder, VPS, runtime, T1/T2, PostgreSQL/TimescaleDB, deployment or exchange credentials;
- promoting staging data to Canonical, choosing permanent Canonical storage, enabling automatic cleanup, or placing any order.

Each of workflow creation, preflight execution, archive materialization, SQLite construction/normalization, staging validation, and Canonical promotion/storage requires its own explicit scope approval where applicable.

## Current status

- Architecture selection: **APPROVED**.
- Permanent Canonical storage target: **DEFERRED**.
- Workflow creation: **NOT AUTHORIZED / NOT STARTED**.
- Preflight execution: **NOT RUN**.
- Archive materialization: **NOT AUTHORIZED UNDER THIS DECISION / NOT RUN**.
- SQLite staging construction: **NOT AUTHORIZED UNDER THIS DECISION / NOT RUN**.
- Staging validation: **NOT RUN**.
- Canonical promotion: **NOT AUTHORIZED**.

## Next bounded step

Prepare the detailed workflow design and execution gates for owner review. Do not create or run a workflow, download data, or create SQLite until the relevant separate approvals are recorded.
