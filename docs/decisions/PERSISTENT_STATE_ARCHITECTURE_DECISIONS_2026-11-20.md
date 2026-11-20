# Persistent State Architecture Decisions — 2026-11-20

## Status

- Owner requested review and closure of the open architecture decisions.
- These decisions close the design questions sufficiently to define a contract-first, test-first implementation scope.
- They do not authorize implementation, database creation/open/write, migration, runtime, VPS, T0 reconstruction, Feeder, T1/T2 runtime, deployment, or trading.
- Execution remains manual Start/Stop with durable state between sessions; paper-only.

## Decisions

| Topic | Decision |
|---|---|
| Persistence backend | Application-owned SQLite database, separate from every T0 database and T0 Canonical asset. No PostgreSQL in the first implementation. |
| Physical location | OS user-data/application-data directory outside the Git repository and outside T0 storage. Resolve the exact absolute path only after target OS/environment is explicitly selected. No staging path is implied. |
| Schema | Normalized SQLite tables for sessions, events, aggregate versions, strategy states, Core/AI ledgers, idempotency claims, risk events, checkpoints and checkpoint generations. Versioned canonical JSON payloads for extensible event/checkpoint bodies. |
| Numeric representation | Financial quantities/prices use exact decimal strings or integer-scaled units; never binary floating-point as persisted accounting truth. Timestamps are UTC epoch milliseconds; preserve source/exchange timestamps separately. |
| Migration | Explicit, forward-only, versioned migrations. Take and verify a SQLite Online Backup API backup before migration. Unknown/newer schema or failed migration => fail closed; no destructive auto-reset or downgrade. |
| Atomic commit | SQLite transaction atomically records event, unique idempotency claim, ledger mutation and aggregate-version advance. Checkpoint generation is immutable and published by an atomic active-pointer update only after verification. |
| Checkpoint policy | Create a verified checkpoint on clean session close and at least every 100 committed state events. Event replay remains authoritative; cadence is not a correctness dependency. Retain at least the latest 3 verified checkpoint generations. |
| Event retention | Retain event and idempotency history indefinitely in the initial personal deployment. No TTL/automatic purge in v1. Any later compaction/deletion requires separate review and proof that replay/deduplication guarantees remain intact. |
| Backup/security | Use SQLite Online Backup API for consistent backups; keep at least 3 verified rolling backups, separate from the active DB. Require OS-level full-disk encryption for persistent deployment. Never store exchange/API secrets in state or checkpoints. Backup restore is an explicit operator action, never automatic on startup. |
| Market-data freshness | At session start, latest fully closed M15 candle age must be <= 20 minutes and H1 <= 70 minutes, measured against one captured UTC preflight time. Forming candles excluded. Thresholds are conservative v1 defaults and must be config-versioned; inability to prove freshness blocks the session. |
| Market-data gaps | No missing/duplicate/conflicting candle within the full required lookback for any active Core/AI feature. A gap outside all active lookbacks may be tolerated only if explicitly reported and proven irrelevant. No synthetic or alternate-venue fallback. |
| Snapshot consistency | M15/H1 inputs must be from the approved source/dataset identity and have a reproducible common as-of boundary. Record exact candle ranges and snapshot IDs for each strategy evaluation. |
| Paper equity source | No exchange account connector in v1. User-configured initial paper equity is recorded as an immutable session/account seed; thereafter paper equity and available capacity are derived from the paper ledger and the current approved risk policy. Missing/ambiguous seed or ledger reconciliation blocks new actions. |
| Recovery authority | Automatic recovery is limited to deterministic replay from verified checkpoint + committed events. Ambiguous/corrupt state enters BLOCKED_RESTORE and requires explicit operator review/correction. Never auto-reset or silently fork a new paper account. |
| Kill Switch | Persist latch and reason. A new session never clears it. Reset requires an explicit manual operator action with an audit event; no strategy/model may clear it. |
| Graceful Stop | Stop accepting new proposals immediately; finish the current atomic paper-state transaction, then checkpoint and close. Allow a 30-second graceful-stop window. If it cannot reach a verified safe boundary, mark/leave the session INTERRUPTED; do not force CLOSED or discard in-flight evidence. |
| T1/T2 and external orders | Not part of v1 persistent-state implementation. No T1 runtime connection, T2 live runtime integration, exchange account/order connector, or real-order side effect. Use only separately approved data contracts/fixtures until separately authorized. |

## Contract-first, test-first implementation scope

The next implementation authorization, if granted, should be limited to the following isolated software work:

1. Define typed/versioned contracts and validators for Session, Event, StrategyState, PositionLedger, SmartDCAState, RiskState, IdempotencyClaim and Checkpoint.
2. Define SQLite repository interfaces and transaction semantics without opening or creating any real T0 or staging database.
3. Implement deterministic event replay, checkpoint validation/publication, idempotency conflict handling and fencing-generation checks against temporary test databases only.
4. Implement Core/AI ledger isolation and Smart DCA state reconciliation with deterministic synthetic fixtures explicitly labelled test-only.
5. Implement session state machine and crash/restart recovery harness with failure injection at every commit/checkpoint boundary.
6. Implement market-data preflight as a pure validation boundary over supplied contract fixtures; do not connect to T0, Binance, T1 or a live provider in this phase.
7. Implement risk admission interface tests proving no action is accepted before READY or when Shared Risk Engine/Kill Switch is unavailable. Do not implement trading/exchange execution.
8. Add contract and regression tests before implementation (TDD RED → GREEN → REFACTOR), run focused tests then full repository suite, and record CI evidence against the exact commit SHA.

### Explicit exclusions

- No production database file/path creation, migration, opening or writing.
- No T0 Canonical access/reconstruction, archive import, Feeder startup or data promotion.
- No staging/VPS/host/network/provider access.
- No systemd, autostart, scheduler, background service or 24/7 process.
- No T1 collector/provider changes or T1-to-T2 runtime wiring.
- No live market-data fetch; fixture-only tests.
- No exchange credentials, account connector, external order, live trading or integrated paper runtime.
- No retention deletion/compaction in v1.

## Verification record

- Source branch: main.
- Parent/source HEAD: `62296dc9626ae611f68386d66172bafb6e16eeb1` (Persistent State Contract/Handoff design commit).
- Work performed: architecture decision documentation only.
- Tests/workflows/Actions run/job/artifact: none.
- Status: **OPEN ARCHITECTURE DECISIONS CLOSED FOR SCOPE PLANNING**; implementation **NOT STARTED / NOT AUTHORIZED**; runtime **NOT STARTED / NOT AUTHORIZED**.
- Next: owner review of the bounded implementation scope and separate explicit authorization before any source changes.
