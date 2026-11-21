# T0 Canonical Reconstruction — Reuse SQLite-First Core Decision

**Date:** 2026-11-21  
**Repository:** `kenznguyen/btcquant-application`  
**Decision status:** OWNER APPROVED — ARCHITECTURE / DESIGN ONLY  
**Implementation status:** NOT STARTED

## 1. Owner decision

The owner approves the architecture:

**Reuse the reviewed T0 SQLite-first Core and build a new, isolated Canonical Reconstruction Importer.**

The intent is to preserve validated T0 components and avoid rewriting the storage/API foundation. New work should be limited to reconstruction-specific behavior and evidence that the existing Core does not already provide.

This approval is not authorization to execute reconstruction, materialize archives, create or modify a database, start runtime services, or deploy anything.

## 2. Reuse boundary

Subject to compatibility checks against the new reconstructed dataset, the following existing components are candidates for reuse:

- SQLite schema, Candle Contract and validation primitives.
- `market_data/api_contract.py`.
- `market_data/storage.py` and `market_data/store.py`.
- `market_data/write_gateway.py`, preserving transaction and lease-fencing guarantees.
- `market_data/sync.py`, only where its behavior is applicable and without reopening the owner-closed REST-tail retrieval path.
- FastAPI read-only API and existing T0 test/CI suites, after compatibility verification.

The existing T0 source review snapshot is `4d41294a7b82566666e50a79b87f62b668672077`. Review conclusions and limitations are recorded in `docs/reviews/T0_AI_ASSISTED_SOURCE_REVIEW_2026-11-21.md`. Historical CI results remain bound to their exact source SHAs and are not evidence of a fresh full-suite run on current HEAD.

## 3. New reconstruction-specific work

Design and, only after separate implementation approval, implement:

- An isolated importer for the approved archive inputs.
- Per-object archive and checksum-sidecar verification and retained provenance.
- Explicit source-to-Candle-Contract field/timestamp mapping, including `available_at_ms` semantics.
- Deterministic duplicate, conflict, gap and partial-coverage policies.
- Reconstruction manifest/metadata and reproducible import evidence.
- Isolated fixtures and acceptance tests covering integrity, schema, candle validity, coverage, provenance and repeatability.

The importer must not silently fabricate missing candles, infer unavailable history, or treat partial coverage as full coverage.

## 4. Data and state separation

- Former Canonical SQLite remains **LOST**; do not attempt recovery or assume its runtime state is available.
- New reconstructed Canonical database remains **NOT CREATED**.
- Historical lease, writer, cursor and recovery state must not be carried forward as live state.
- MAY-10 controlled runtime trial DB remains a separate asset and must not receive archive history.
- The historical archive inventory (202 ZIPs and 202 paired checksum sidecars) is evidence only; fresh per-object metadata and materialization evidence are still required before any future build request.
- REST-tail retrieval remains **CLOSED BY OWNER DECISION**. No retry or bypass.

## 5. Explicit exclusions

This decision does not authorize:

- Selecting a staging host or absolute destination.
- Destination preflight, DNS/object-store requests, archive downloads or materialization.
- SQLite database creation, importer execution, database writes or cleanup.
- Feeder/Writer/runtime startup, VPS provisioning, deployment or cutover.
- PostgreSQL/TimescaleDB activation or migration.
- T1/T2 runtime integration, exchange credentials, paper/live execution or orders.

PostgreSQL remains **PARKED**; PG-REQ-01 must be resolved before any future PostgreSQL activation proposal.

## 6. Required gates before execution can be reconsidered

1. Owner selects and approves the current host/environment and exact absolute staging destination.
2. Current immutable archive source location/access is confirmed.
3. Fresh per-object archive and sidecar size/hash metadata and materialization evidence are retained.
4. Candle Contract mapping and `available_at_ms` policy are specified.
5. Importer design, dependency lock, source SHA and deterministic policies are reviewed.
6. Independent validation/acceptance plan and evidence requirements are defined.
7. A separate explicit owner approval authorizes the exact bounded execution scope.

Until all gates are met and separately approved, reconstruction remains **DESIGN APPROVED / EXECUTION NOT AUTHORIZED**.

## 7. Next step

Prepare the Canonical Reconstruction Specification and importer/test design as documentation or other explicitly approved design-only work. Preserve the current repository branch and do not change application source, tests, workflows, data or runtime under this decision.
