# T0 Canonical Data Preserve & Reconstruct Decision — 2026-11-20

## Decision
Owner approved the **Preserve & Reconstruct** design for eventual T0 Canonical SQLite reconstruction.

- Preserve the validated Binance USD-M BTCUSDT M15/H1 archive objects and their paired checksum sidecars as immutable source evidence.
- Reconstruct into a **new SQLite database** in a dedicated, isolated staging location.
- Never overwrite, mutate, move, or assume recovery of the former Canonical SQLite database.
- Keep the MAY-10 controlled runtime trial database separate; it is reserved for newly closed market data only and must not receive historical archive imports.
- Retain source-object identity, checksums, archive timeframe/date coverage, importer version/source SHA, schema/user_version, import manifest, and validation results as provenance.
- Validate SQLite integrity, schema, row counts, timestamp boundaries/order, duplicate handling, OHLC/numeric constraints, continuity/gap policy, and M15/H1 coverage before considering acceptance.
- Any reconstructed history must be labeled `RECONSTRUCTED`; it must not be described as recovery of the original Canonical database.
- Keep archive source objects unchanged and retained. No cleanup/deletion is authorized.
- Staging is not Canonical by default. Promotion, official designation, or change of primary storage location requires a separate explicit owner approval after review of the complete evidence.

## Approval boundary
This approval covers **design and procedure only**. It does not authorize:
- downloading or copying archive objects again;
- creating a reconstruction database;
- importing archive data;
- changing or initializing any existing database;
- Dropbox upload/snapshot operations;
- restore drills, primary cutover, or promotion;
- MAY-10 trial DB changes or runtime activation;
- T1/T2 integration, PostgreSQL/Timescale, trading, or real orders.

Execution must begin only after a separate, explicit approval identifies the exact staging destination, source archive inventory, coverage/gap acceptance policy, importer SHA, and validation gates.

## Current evidence and status
- Archive payload validation: PASS for 202 ZIP objects and 202 checksum sidecars; 241,440 M15 and 60,360 H1 rows; full historical completeness and REST tail remain NOT VERIFIED.
- Canonical SQLite reconstruction: NOT STARTED.
- Reconstructed staging database: NOT CREATED.
- Canonical promotion: NOT AUTHORIZED.
- MAY-10 runtime trial remains separately scoped and must not import archive history.

## Work record
- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Change type: documentation / owner decision record.
- Tests/workflows: not run; no code behavior changed.
- Workflow run, job, artifact: none for this documentation-only change.
- Status: decision recorded; implementation and reconstruction remain NOT AUTHORIZED.
- Next step: prepare a bounded reconstruction execution plan specifying exact staging destination, archive inventory, coverage/gap policy, importer identity, validation and rollback/retention controls. Submit it for separate approval before any data operation.
