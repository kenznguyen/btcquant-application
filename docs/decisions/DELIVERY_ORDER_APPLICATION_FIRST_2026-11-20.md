# Application-First Delivery Order — 2026-11-20

## Owner decision

The owner approved **Option A — Application-first** for the BTCUSDT Quant System.

Complete the application/software foundations before restarting the Feeder or creating a new T0 Canonical dataset. This is a sequencing decision; it does not authorize every implementation, data, runtime, integration, or trading operation listed below.

## Approved delivery order

1. **T0 Application Foundation**
   - Continue the application-side API, versioned data contracts, validation, and isolated regression/integration harnesses.
   - Use deterministic fixtures or explicitly identified reference data for tests.
   - Keep test evidence distinct from production/canonical market data.

2. **T1 Collector**
   - Keep the collector implementation and ownership in `kenznguyen/binance-futures-collector`.
   - Application repository may contain only separately approved consumer contracts, DTOs, validation, adapters, and deterministic fixtures.
   - T1 HTTP Provider remains PAUSED; T1-to-T2 runtime connection remains NOT APPROVED.

3. **T2 Strategy Development**
   - Preserve Strategy Core: RSI + ADX + Smart DCA.
   - Develop the independent AI Strategy capable of producing its own LONG/SHORT signals, including when Strategy Core has no signal.
   - Keep Core and AI decision/position ledgers separate.
   - Both strategies must pass the common Shared Risk Engine before any simulated trade admission.

4. **Shared Risk Engine**
   - Continue contract-level and isolated tests for common risk admission, sizing, limits, and kill-switch behavior.
   - Keep paper-first controls. No live orders or real trading.

5. **Deferred data/runtime operations**
   - Feeder startup, new T0 Canonical reconstruction, database creation/import/promotion, VPS or persistent runtime activation, T1/T2 runtime connection, and integrated paper trading are deferred until their own prerequisites and explicit approvals are satisfied.

## Data classification

- Deterministic fixtures and synthetic data are test inputs only.
- Binance reference/tail data is source evidence only unless separately reconciled and approved for a specific dataset.
- Neither fixtures nor unreconciled reference data may be represented as T0 Canonical Data.
- T0 remains an independent data asset; application repository lifecycle does not own or redefine its data lifecycle.

## Status and restrictions at decision time

- Former T0 Canonical SQLite: **LOST**.
- New reconstructed T0 Canonical SQLite: **NOT CREATED**.
- Feeder: **NOT STARTED**.
- T0 reconstruction: **BLOCKED / NOT AUTHORIZED** pending the existing source, destination, reconciliation, importer, validation, and execution gates.
- T1 provider/runtime connection: **PAUSED / NOT APPROVED**.
- Live trading: **PROHIBITED**; paper-first only.
- No source-code change, test, workflow, deployment, data access, database operation, or runtime operation is authorized merely by this sequencing decision.

## Verification record

- Work: record owner-approved delivery sequencing and boundaries.
- Scope: documentation/decision only.
- Tests/workflows: none; no runtime or data operation performed.
- Source SHA: `cfa9b6fd1d0e04032c31715bf74e5c4fb34db70e`.
- Actions run/job/artifact: none.
- Status: **DECISION APPROVED / RECORDED**; implementation progress remains governed by each component's own evidence and approval gates.
- Next: continue with separately scoped application/software work that does not require Feeder startup, Canonical data access, staging, persistent runtime, T1/T2 runtime connection, or trading.
