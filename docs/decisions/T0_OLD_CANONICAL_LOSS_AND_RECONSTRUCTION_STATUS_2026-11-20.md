# T0 Old Canonical Loss & New Reconstruction Status — 2026-11-20

## Purpose

Remove ambiguity between the former Canonical SQLite asset and any future archive-derived database. This record reflects the owner's explicit statement on 2026-11-20 that **no copy of the old Canonical Data remains**.

## Authoritative status

| Asset / activity | Status | Meaning |
|---|---|---|
| Former Canonical SQLite | **LOST** | Owner confirms no remaining copy. It is not available for recovery or restore. |
| Recovery of former Canonical SQLite | **NOT POSSIBLE / NOT APPLICABLE** | No surviving copy is available to recover. Do not describe archive reconstruction as recovery. |
| Binance archive source evidence | **PRESERVE — IMMUTABLE** | Previously validated 202 ZIP objects and 202 paired checksum sidecars remain source evidence; this does not make them a copy of the former SQLite database. |
| New archive-derived SQLite | **NOT CREATED** | No reconstruction database has been created. |
| New archive-derived SQLite import | **NOT STARTED** | No archive import into SQLite has occurred. |
| New reconstructed dataset validation | **NOT RUN** | There is no reconstructed database to validate. |
| New reconstructed dataset designation | **RECONSTRUCTED — NOT YET BUILT** | Any future build must retain this identity and must not be labeled RECOVERED or the old Canonical. |
| Promotion to a future Canonical | **NOT AUTHORIZED** | Requires separate explicit approval after evidence review. |
| Deletion of old Canonical | **NOT APPLICABLE — NO COPY REMAINS** | No deletion operation is required or authorized against an asset whose existence is not established. |

## Non-equivalence rule

The former Canonical SQLite and a future archive-derived SQLite are different assets with different provenance:

- **OLD CANONICAL = LOST** — the former database has no remaining copy, per owner confirmation.
- **NEW RECONSTRUCTED DATA = NOT CREATED** — no replacement database currently exists.
- Binance ZIP/sidecar archives are source inputs for a possible future reconstruction. They are not a backup, replica, restore point, or recovered image of the old Canonical SQLite.
- A future reconstructed database must be labeled `RECONSTRUCTED`, with partial coverage boundaries and provenance recorded. It must never be represented as the recovered former Canonical.

## Execution boundaries

This status clarification is documentation-only. It does not authorize:
- archive download, copy, materialization or modification;
- destination preflight or creation;
- SQLite initialization, creation, opening for writes, import or normalization;
- Dropbox upload/snapshot, backup or restore drill;
- promotion, official designation, primary cutover or runtime;
- changes to the separate MAY-10 trial database;
- T1/T2, PostgreSQL/Timescale, trading or real orders;
- cleanup or deletion of archive/source evidence.

The Preserve & Reconstruct decision and bounded execution plan remain subject to their explicit approval gates. If an older staging/materialization document appears to grant broader authority, this status record and the controlling Preserve & Reconstruct decision govern; the older document must be treated as superseded/hold until formally reconciled.

## Work record

- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Change type: documentation-only status clarification based on owner confirmation.
- Tests/workflows: not run; no code behavior changed.
- Workflow run, job, artifact: none.
- Data operations: none. No archive, database, host, Dropbox or runtime was accessed or changed.
- Status: **OLD CANONICAL = LOST; NEW RECONSTRUCTED DATA = NOT CREATED**.
- Next: if reconstruction is later proposed, resolve the exact source, destination, coverage/gap policy, importer SHA and validation gates, then obtain separate explicit execution approval.
