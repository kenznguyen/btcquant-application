# Independent Multi-Source Data Foundation — Owner-Approved Architecture Decision

- Decision ID: `INDEPENDENT_MULTI_SOURCE_DATA_FOUNDATION`
- Record date: 2026-11-22 (owner reconfirmation and correction of repository record)
- Repository: `kenznguyen/btcquant-application`
- Status: **OWNER-APPROVED ARCHITECTURE**
- Implementation status: **NOT IMPLIED / SEPARATELY GATED**

## 1. Decision and authority

The owner confirms that **Independent Multi-Source Data Foundation** was approved. This record restores that decision to the repository's controlling architecture record. It corrects prior summaries that described the direction as merely proposed or treated T0 and T1 as independent competing canonical stores.

The exact date and commit of the original approval could not be established from the current `main` handoff and decision records during this reconciliation. The owner's explicit confirmation on 2026-11-22 is the authority for recording the approval status here. Do not invent an earlier approval SHA or claim that this documentation update proves implementation.

## 2. Approved target architecture

**T0 is the independent, multi-source Data Foundation and the single canonical ownership boundary for accepted market data.** It receives data from specialized collectors/source adapters, validates and normalizes it under versioned contracts, and governs canonical persistence, provenance, quality, coverage, gaps, recovery and dataset versions.

- **T0 — Independent Multi-Source Data Foundation:** owns canonical accepted market-data records across supported domains, not only OHLCV candles. It owns source registration, normalization/validation contracts, lineage/provenance, quality state, canonical dataset identity and read interfaces.
- **T1 — Specialized market-microstructure collector:** remains a separately owned collector implementation/repository. It collects its specialized feeds and supplies source data to T0 through a separately specified and approved ingestion/import boundary. T1 is not a competing canonical data foundation.
- **Other source adapters/collectors:** follow the same pattern; source-specific collection may remain independently implemented, while accepted canonical data is governed by T0.
- **T2 — Strategy and AI consumers:** read approved canonical datasets through versioned consumer contracts. Strategy Core (RSI + ADX + Smart DCA) and the independent AI Strategy may derive features/views for analysis, but those derived artifacts do not become competing authoritative copies of source data.
- **Risk and execution:** all Core and AI trade intents remain subject to the shared risk authority and existing paper-first/execution-disabled restrictions.

## 3. Data ownership and anti-fragmentation rules

1. One canonical ownership boundary: T0. A source collector may retain operational/raw capture needed for collection, replay, audit or recovery, but it must not establish a parallel canonical dataset for the same accepted domain.
2. Preserve source identity and provenance through ingestion: source/collector identity, event or observation time, receive/availability time where evidenced, schema/contract version, validation outcome, source object identity/checksum where applicable, and ingestion/dataset version.
3. Raw source evidence and canonical normalized records are distinct lifecycle stages, not competing sources of truth. Do not discard raw evidence merely because canonical ingestion or feature generation succeeded.
4. T2 feature tables, caches, training bundles, backtest inputs and strategy-specific projections are derived/consumer artifacts. They must retain dataset/version lineage and must not silently become alternate canonical stores.
5. Avoid duplicate ingestion and conflicting identities through explicit idempotency, deduplication, conflict and gap policies in the relevant source contracts.
6. Do not force unrelated operational state (paper ledgers, orders, risk decisions, control state) into the market-data canonical store.

## 4. Repository and implementation boundaries

- T1 collector implementation remains in `kenznguyen/binance-futures-collector`; do not copy/fork the full collector into the application repository.
- `btcquant-application` may own T0 canonical foundation code and approved source-facing contracts, DTOs, validation, adapters, importer interfaces and deterministic fixtures.
- T1 raw capture and collection implementation remain in the T1 repository. The application repository must not duplicate T1's collector internals, raw capture engine, Orderbook Manager or replay implementation.
- The earlier T1 repository-ownership decision remains valid for code ownership. Its statements that T0/T1 are independent data assets or that no T1-to-T0 data path is part of the architecture are superseded by this decision to the extent they conflict with the approved multi-source foundation.
- T1 HTTP Provider approval, provider implementation status and T1-to-T2 runtime authorization are separate questions. This decision does not activate a provider or connect T1 directly to T2.

## 5. Compatibility with existing T0 records

This is a higher-level architecture decision; it does not erase or retroactively rewrite historical evidence.

- SQLite remains the currently recorded T0 canonical-storage technology direction. This decision does not authorize creating, replacing, migrating, promoting or cutting over any database.
- The former Canonical SQLite status recorded in current T0 evidence remains **LOST**. The new reconstructed SQLite remains **NOT CREATED** unless later evidence changes that status.
- Existing reconstruction decisions, archive coverage limitations, S1.1/S1.2 schema contracts and staging gates continue to apply to their stated scopes. A reconstructed dataset is not automatically promoted to canonical.
- The multi-source ingestion contracts, schemas, storage partitioning, source onboarding sequence and operational transport must be designed and separately reviewed before implementation.

## 6. Explicit approval boundary

This architecture approval does **not** authorize:
- T0 database creation, replacement, migration, merge, promotion or cutover;
- Canonical SQLite access or mutation, archive acquisition, real-data staging or importer execution;
- T1 provider activation, new endpoint implementation, T1-to-T0 runtime connection or T1-to-T2 runtime connection;
- new source onboarding, network access, credentials, VPS deployment, services/autostart or runtime changes;
- retention/deletion/cleanup, data uploads, or changes to existing data lifecycle controls;
- strategy execution changes, live trading or real orders.

Each implementation or runtime phase requires a bounded approval, source SHA, contracts, tests/evidence and explicit exclusions.

## 7. Reconciliation findings and status

Repository evidence checked on 2026-11-22:
- `docs/PROJECT_SESSION_HANDOFF.md` and `docs/T0_ACTIVE_SCOPE_INDEX.md`;
- `docs/decisions/T0_CANONICAL_DATA_PRESERVE_AND_RECONSTRUCT_DECISION_2026-11-20.md`;
- `docs/decisions/T0_NEW_SQLITE_CANONICAL_TARGET_OWNER_DECISION_2026-11-22.md`;
- `docs/decisions/T0_CANONICAL_RECONSTRUCTION_REUSE_SQLITE_CORE_2026-11-21.md`;
- `docs/decisions/T1_REPOSITORY_OWNERSHIP_AND_CONSUMER_BOUNDARY_2026-11-20.md`;
- `docs/architecture/CORE_FIRST_ARCHITECTURE_DECISION_2026-11-12.md`.

The inspected records establish the SQLite reconstruction/storage direction and T1 code-repository ownership, but do not themselves contain the Independent Multi-Source approval. The owner has now explicitly confirmed that approval; this ADR records it without fabricating the original approval's date or commit.

- Architecture: **OWNER-APPROVED**
- T0 multi-source canonical implementation: **NOT VERIFIED / NOT COMPLETE**
- Source-specific T0 ingestion contracts: **NOT VERIFIED / NOT COMPLETE**
- T1-to-T0 runtime ingestion: **NOT AUTHORIZED BY THIS ADR**
- New Canonical SQLite: **NOT CREATED** (per latest T0 status record)
- Database promotion/cutover: **NOT AUTHORIZED**
- Tests/workflows: **NOT RUN**; documentation-only
- Workflow run/job/artifact: **NONE**

## 8. Next step

Reconcile the detailed T0/T1 source-domain inventory and define the canonical ingestion contract boundary for each source as a design-only task. Do not implement ingestion, create or mutate databases, connect runtimes, or change data lifecycle behavior without separate owner approval.
