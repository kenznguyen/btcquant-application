# T0 New SQLite Canonical Target — Owner Decision — 2026-11-22

## Decision

**APPROVED — ARCHITECTURE DIRECTION ONLY.**

The project goal is to build a **new SQLite dataset** from the already approved archive-only reconstruction design. The new database is initially a disposable staging/reconstruction asset and must be labeled:

`RECONSTRUCTED — PARTIAL COVERAGE`

It may be recognized as the new Canonical SQLite only after all required source-provenance, integrity, schema, coverage, gap, duplicate/conflict, deterministic-build, and read-only acceptance checks pass, followed by a separate explicit owner decision to promote it.

## Historical asset status

- Former Canonical SQLite: **LOST**.
- New reconstructed SQLite: **NOT CREATED**.
- The new dataset is not a recovery, restoration, or byte-for-byte replacement of the lost database.
- No claim of complete historical coverage is permitted unless separately evidenced and accepted.

## Basis and constraints retained

- Follow the owner-accepted S1.1 provenance/schema design; do not revive superseded S1 DDL where inconsistent.
- Preserve the archive-only boundary and the exact pinned 404-object inventory (202 ZIP + 202 paired .CHECKSUM sidecars).
- REST tail and MAY-10 remain excluded from this reconstruction scope.
- Use the accepted B4 resource ceilings, B6 retention policy, and B7 Option A destination model. The exact workstation/host and absolute path are still unspecified; preflight has not been run.
- Keep the output disposable and fail closed on missing or invalid provenance, unsupported archive formats, checksum/CRC/member failures, incomplete row lineage, conflicting duplicate identities, or unmeasured coverage.

## Approval boundary

This decision approves the **target architecture and lifecycle** only. It does NOT authorize any of the following:

- archive retrieval, network access, materialization, or source-host access;
- workstation preflight or destination creation;
- SQLite creation/open/write, DDL, schema migration, or `user_version` changes;
- importer implementation, execution, or build workflow;
- tests, workflow creation/dispatch, or CI artifact production;
- data validation using real archive payloads;
- deletion, retention execution, upload, or cleanup;
- Canonical promotion/cutover, T0 runtime/Feeder/VPS start, T1/T2 connection, deployment, exchange credentials, or trading.

Each such phase remains subject to its own bounded approval, with exact host/path, source identity, code SHA, tests/evidence, and exclusions stated as applicable.

## Next decision gate

Prepare a bounded implementation-readiness proposal for the next phase only. It must resolve the remaining archive-format evidence, exact owner-controlled workstation/path and preflight requirements, and the specific authorization needed for each action. Do not begin those actions while preparing the proposal.

## Status

- Architecture direction: **OWNER APPROVED**
- S1.1 design: **OWNER ACCEPTED / DESIGN FROZEN**
- Archive format coverage beyond M15 monthly 2022-08: **NOT VERIFIED**
- Actual source-derived coverage manifest: **NOT VERIFIED**
- Destination host/path and preflight: **PENDING / NOT RUN**
- SQLite: **NOT CREATED / NOT AUTHORIZED**
- Importer/build: **NOT IMPLEMENTED / NOT AUTHORIZED**
- Canonical promotion: **NOT AUTHORIZED**
- Runtime/deployment: **NOT AUTHORIZED**

No tests, workflows, jobs, artifacts, archive requests, data operations, database operations, or runtime actions were performed by this decision.
