> **Architecture boundary update (2026-11-22):** T1's repository/code ownership decision remains valid: the collector stays in this repository and is not copied into the application repository. The later owner-approved Independent Multi-Source Data Foundation decision supersedes any interpretation that T0 and T1 should maintain competing canonical data stores: T0 owns accepted canonical multi-source data; T1 remains a specialized collector/source and is intended to feed T0 through separately approved ingestion contracts. This notice does not authorize T1→T0 runtime connectivity, provider activation, storage migration, data copy, or T1→T2 runtime connectivity. See [controlling decision](INDEPENDENT_MULTI_SOURCE_DATA_FOUNDATION_OWNER_DECISION_2026-11-22.md).

---

# T1 Repository Ownership and Consumer Boundary Decision — 2026-11-20

## Decision

**APPROVED — KEEP T1 IMPLEMENTATION IN ITS EXISTING REPOSITORY; DO NOT COPY OR FORK THE FULL T1 REPOSITORY INTO THE APPLICATION REPOSITORY.**

- T1 implementation remains owned by `kenznguyen/binance-futures-collector`.
- Quant application remains owned by `kenznguyen/btcquant-application`.
- The application repository may contain only the T1-facing consumer-side artifacts that are independently needed and separately scoped: versioned data contracts/interfaces, DTOs, schema validation, consumer adapters, and deterministic test fixtures/mocks.
- Do not duplicate T1 collector implementation, raw storage, Orderbook Manager, capture/replay pipeline, or provider implementation in the application repository.
- T1 HTTP Provider remains **PAUSED**. Its existing commits are preserved; this decision does not authorize extension, activation, endpoint additions, or runtime use.
- T1 → T2 runtime connectivity remains **NOT APPROVED**.
- No T1 database/storage migration or data copy is authorized.
- T0 remains an independent data asset. No Canonical SQLite change, copy, initialization, writer/feeder action, or runtime change is included.
- No real orders or live trading. Existing paper-first and execution-disabled guardrails remain unchanged.

## Repository boundaries

| Concern | Owning repository |
|---|---|
| T0 canonical market-data foundation and its application-side client/contracts | `kenznguyen/btcquant-application` (T0 data asset remains independently owned; no database payload migration implied) |
| T1 collector, raw capture/storage, orderbook processing, replay and provider implementation | `kenznguyen/binance-futures-collector` |
| T1 consumer contract, DTO, validation, consumer adapter and fixtures when separately approved | `kenznguyen/btcquant-application` |
| T2 Strategy Core, independent AI Strategy, shared risk engine, paper execution, dashboard/application | `kenznguyen/btcquant-application` |

## Provenance snapshot

- Application repository: `kenznguyen/btcquant-application`, branch `main`, pre-decision HEAD observed as `0844e16b08d52fa7cf6ed001d7c260ee6bde1ff8` (2026-11-20).
- T1 repository: `kenznguyen/binance-futures-collector`, default branch `main`; latest commit observed during this decision record: `c91a8c22d3b6236c98ab9a4d4d69b25d47f7f738` (2026-11-18, “docs: record verify-data correctness review”).
- These SHAs identify the inspected repository snapshots for this decision. They do not claim that every file or runtime state was independently audited in this documentation-only step.

## Status and verification

- Architecture decision: **APPROVED / RECORDED**.
- T1 implementation duplication: **PROHIBITED BY THIS DECISION**.
- Consumer-side T1 integration artifacts: **NOT IMPLEMENTED / FUTURE SEPARATE SCOPE**.
- T1 HTTP Provider: **PAUSED**.
- T1 → T2 runtime connection: **NOT APPROVED**.
- T1 storage/data migration: **NOT AUTHORIZED**.
- T0 Canonical SQLite modification: **NOT AUTHORIZED BY THIS DECISION**.
- Tests/workflows: **NOT RUN**; no Actions run, job, or artifact was generated for this documentation-only change.
- Runtime, VPS, exchange, database, and trading behavior: **NOT ACCESSED OR CHANGED**.

## Next permitted step

If T2 later requires T1 data, first define and review a versioned consumer contract and its validation/fixture requirements inside `btcquant-application`. Any live transport, provider activation, T1 → T2 runtime connection, storage migration, or data movement requires a separate explicit owner decision.

## Change control

This decision does not authorize broad cleanup, repository consolidation, Git history migration, branch rewriting, T1 provider development, T0/T1/T2 runtime deployment, or trading execution. Preserve existing repository histories and current branches.
