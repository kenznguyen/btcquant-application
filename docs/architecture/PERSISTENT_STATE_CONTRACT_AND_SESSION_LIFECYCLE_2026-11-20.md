# Persistent State Contract and Session Lifecycle — 2026-11-20

## Status and scope

- Status: **DESIGN REVIEWED / RECORDED**; implementation **NOT STARTED / NOT AUTHORIZED**.
- Mode: On-Demand Execution, manual Start/Stop; durable state between sessions.
- This is a logical contract, not a physical database schema or migration.
- No runtime, database, T0 Canonical data, Feeder, T1/T2 provider, VPS, scheduler, or trading system is activated or changed.
- T0 remains an independent data asset. Application-first delivery order remains controlling.

## 1. Design principles

1. Durable event history is authoritative; checkpoints are versioned recovery accelerators.
2. Persist a complete business transition, its event(s), idempotency claim, and checkpoint advancement atomically where the selected store supports transactions. Otherwise use a documented recoverable write protocol.
3. Core and AI have separate strategy identities, decision histories, position ledgers, and state namespaces. Neither may mutate the other's ledger.
4. Every proposed entry, add/DCA, reduction, or exit passes the same Shared Risk Engine and Kill Switch.
5. A failed or ambiguous restore/preflight blocks strategy admission. Never silently create a fresh state when prior persistent state exists or is expected.
6. Processing is at-least-once with atomic uniqueness/deduplication; do not claim distributed exactly-once execution.
7. Paper-only. No external order side effects are part of this contract.

## 2. Logical contract

Every persisted record carries, as applicable:

- `contract_name`, `schema_version`, `record_type`
- `account_scope_id` (local personal-account namespace; no multi-customer tenancy assumption)
- `session_id`, `event_id`, monotonically increasing `aggregate_version` / `event_sequence`
- `strategy_id` (`CORE` or `AI`), `strategy_version`, `model_version` where relevant
- `config_hash`, `risk_policy_version`
- `market_snapshot_id`, source/dataset identity, timeframe, candle boundary and data-as-of timestamp where relevant
- UTC `created_at` and `recorded_at`; preserve exchange/source timestamps separately
- integrity/checksum metadata for checkpoint payloads

Required logical aggregates:

| Aggregate | Required durable contents |
|---|---|
| Session | ID, lifecycle status, start/end, initiator, source snapshot, config and code/model versions, last committed event sequence |
| Strategy state | Strategy namespace, version, last evaluated candle, cooldown/eligibility and other state required for deterministic continuation |
| Position ledger | Separate Core/AI positions; position ID, side, quantity, average entry basis, realized accounting, fees/funding assumptions, lifecycle status |
| Smart DCA state | Core position reference, DCA level/count, cumulative added quantity/notional, next eligible level/price or trigger state, last DCA event, configured limits/version |
| Risk state | Kill-switch latch and reason, policy version, durable risk events and reservations; current capacity is recomputed at session start, not trusted from an old cached allowance |
| Decision/action history | Proposal, source strategy, signal direction/type, input snapshot, risk verdict/reasons, dedupe key, resulting paper-ledger event |
| Checkpoint | Schema version, checkpoint ID, covered event sequence, aggregate versions, payload checksum, creation time, source snapshot and strategy/config versions |

Persist only fields necessary to reproduce and audit state. Do not persist secrets or exchange credentials in strategy checkpoints.

## 3. Atomicity and checkpoint rules

- Event append, unique idempotency claim, ledger mutation and aggregate-version advance form one logical commit.
- A checkpoint is valid only if its payload checksum passes and its covered event sequence is known to be committed.
- Write checkpoint to a new immutable generation, verify it, then atomically advance the active-checkpoint pointer. Never overwrite the only known-good checkpoint in place.
- Recovery loads the last valid checkpoint and replays committed events after its sequence in strict order.
- If the event store and checkpoint store cannot commit atomically, the protocol must make incomplete generations detectable and safely ignorable.
- Checkpoint cadence is a tunable implementation detail; correctness must not depend on a particular cadence.

## 4. Idempotency contract

Use a stable intent identity derived from the logical decision, not the retry attempt. Proposed uniqueness dimensions:

`account_scope_id + ledger_id + strategy_id + strategy_version + market_snapshot_id + candle_open_time + action_kind + action_ordinal`.

- Enforce uniqueness with a storage-level unique constraint or equivalent atomic compare-and-insert.
- Same key + same canonical payload hash: return/reuse the previously recorded outcome; do not apply another ledger mutation.
- Same key + different payload hash: reject as an idempotency conflict and block that action for review.
- Concurrent duplicate claims: one wins atomically; the other observes the committed/in-progress result and cannot execute a second mutation.
- An explicit re-evaluation under changed strategy/model/config must be recorded as a new evaluation, not silently overwrite the old one. It must not create a second paper action for the same logical candle/action unless a separately approved re-arm policy allows it.
- Keep dedupe records at least as long as the corresponding event/ledger history can be replayed. No short TTL that can expire while old events remain replayable.
- This guarantees deduplicated paper-state transitions, not exactly-once behavior across external exchanges.

## 5. Smart DCA recovery

Restore Smart DCA only from a validated Core ledger aggregate and its event history. Validate:

- position is open and belongs to Core;
- side, quantity and average basis reconcile with entry and DCA events;
- DCA count/level and cumulative additions reconcile with ledger totals;
- next eligibility/trigger is derived from the persisted policy version and valid position state;
- configured maximum DCA levels, exposure and risk constraints are not exceeded;
- last processed candle/event sequence is consistent.

If any invariant fails, mark Core state `RESTORE_BLOCKED`; do not reset DCA count, infer missing additions, or continue adding. AI positions never inherit Core DCA state. Any future AI averaging/addition policy must have its own explicitly versioned state contract and still pass Shared Risk Engine.

## 6. Session lifecycle

`IDLE -> START_REQUESTED -> PREFLIGHT -> RESTORING -> READY -> RUNNING -> CHECKPOINTING -> CLOSED`

Non-success terminal states: `BLOCKED_PREFLIGHT`, `BLOCKED_RESTORE`, `INTERRUPTED`, `FAILED_PERSISTENCE`, `ABORTED`.

- Only one writer session may own the persistent state scope at a time. Acquire ownership atomically with a monotonically increasing fencing generation; stale sessions cannot commit after ownership changes.
- A manual Start creates a new session ID and records the request before strategy evaluation.
- Preflight validates configuration, data, schema compatibility, checkpoint/event integrity and prior-session status.
- Restore reconstructs Core and AI independently, then recomputes risk capacity from the approved current account/equity snapshot and current risk policy.
- READY is reached only after all required checks pass. Only then may Core and AI evaluate.
- On normal Stop, stop accepting new proposals, finish/abort in-flight paper transitions deterministically, commit final events and checkpoint, verify them, then mark CLOSED.
- A session is CLOSED only after checkpoint verification and durable closure record. Process exit alone is not proof of closure.

## 7. Crash and interrupted-session recovery

- On next manual Start, any prior `START_REQUESTED`, `PREFLIGHT`, `RESTORING`, `READY`, `RUNNING`, or `CHECKPOINTING` session without a verified CLOSED record is classified as `INTERRUPTED`.
- Do not resume execution from the last in-memory instruction. Recover from last valid checkpoint plus committed event tail.
- Replay is idempotent. An event already committed is not applied again; an uncommitted partial transaction is ignored/rolled back by the store.
- If there is an ambiguous action outcome, missing event sequence, checksum mismatch, conflicting writer generation, or unreconciled ledger, fail closed and require an explicit recovery/correction procedure.
- Never automatically discard or reset an interrupted session. Preserve forensic event history.
- Recovery must be deterministic for the same checkpoint, event tail, strategy/config versions and market snapshot.

## 8. Market-data preflight before every new session

Preflight must independently verify:

1. Source identity and dataset/contract version are approved for the requested analysis.
2. Required BTCUSDT timeframes (currently M15/H1 where the strategy requires both) are present and schema-valid.
3. Only fully closed candles are admitted; forming candles are excluded.
4. Candle timestamps are UTC-aligned, strictly ordered, unique, and OHLCV values pass the data contract.
5. Required lookback coverage is sufficient for RSI, ADX, Smart DCA and AI features; no silent fallback to synthetic, venue-local, stale cache or another exchange source.
6. Gaps, duplicates, conflicts and late corrections are evaluated against an explicitly approved policy. Unresolved material gaps block affected strategy/timeframe.
7. Freshness is calculated against the latest closed candle and current session start/as-of time. Thresholds must be configured per timeframe and approved; no new numeric threshold is established by this design.
8. M15/H1 snapshot boundaries are mutually consistent and each input snapshot is recorded for reproducibility.
9. If data is stale, incomplete, inconsistent, unavailable, or cannot be proven, session remains `BLOCKED_PREFLIGHT`; no new paper action is admitted.

A data preflight PASS means inputs meet the approved contract for that session; it does not make the reconstructed T0 dataset Canonical. Former Canonical remains LOST; reconstructed SQLite remains NOT CREATED and NOT AUTHORIZED.

## 9. Risk and strategy continuity

- Strategy Core remains RSI + ADX + Smart DCA.
- AI remains an independent LONG/SHORT proposal producer and may signal when Core is silent.
- Keep decision/position ledgers separate and preserve provenance.
- Shared Risk Engine and Kill Switch are mandatory for every proposed action.
- Persist Kill Switch latch and audit reason; clearing it requires an explicit authorized action. Do not clear it merely because a new session starts.
- Recompute available risk capacity from current approved equity/position snapshot; persisted risk reservations must be reconciled, not blindly reused.
- Existing risk policy remains the controlling policy; this document does not change position sizing, margin caps or leverage.
- Paper positions remain open in durable records while the process is stopped, but receive no monitoring, protective action, or intervention during downtime. The UI/session report must disclose this.

## 10. Failure matrix and required behavior

| Condition | Required behavior |
|---|---|
| Unknown schema version | BLOCKED_RESTORE; no automatic destructive migration |
| Corrupt/missing checkpoint but valid event history | Rebuild only if deterministic replay is complete; otherwise block |
| Event gap or checksum mismatch | BLOCKED_RESTORE; preserve evidence |
| Duplicate intent | Return existing outcome; no second ledger mutation |
| Same idempotency key, different payload | Reject conflict; block action |
| Concurrent/stale writer | Reject stale fencing generation |
| Smart DCA reconciliation failure | Block Core continuation and additions |
| Stale/incomplete market data | BLOCKED_PREFLIGHT; no new actions |
| Shared Risk Engine/Kill Switch unavailable | No action admitted |
| Persistence failure during action | Do not report success; recover from durable commit state |
| Crash during checkpoint | Ignore incomplete checkpoint generation; recover last verified checkpoint + committed events |

## 11. Contract test plan (design only)

Before implementation approval, isolated tests must cover:

- schema version compatibility, unknown version fail-closed and non-destructive migration rules;
- checkpoint checksum, partial-write and pointer-swap crash windows;
- event/checkpoint atomicity and event-tail replay;
- Core/AI namespace and ledger isolation;
- Smart DCA exact restoration and arithmetic reconciliation;
- duplicate retry, concurrent duplicate, same-key/different-payload conflict and replay after restart;
- crash injection at every lifecycle transition and during persistence/checkpoint;
- stale writer/fencing-token rejection;
- M15/H1 closed-candle, freshness, lookback, gap, duplicate, ordering and snapshot consistency checks;
- risk-policy reload, Kill Switch persistence and risk-capacity recomputation;
- no strategy action before READY and no action when Shared Risk Engine is unavailable;
- repeated recovery produces identical state and no duplicate paper actions.

Use deterministic synthetic fixtures only for isolated tests, clearly labelled test-only. Do not use or create T0 Canonical data for these tests.

## 12. Open decisions before implementation

The following remain deliberately unspecified and require separate review/approval:
- physical persistence backend and exact file/database location;
- concrete schema encoding and migration policy;
- event retention, checkpoint cadence, backup/restore and encryption/access controls;
- exact freshness thresholds and permitted gap policy per timeframe;
- account/equity snapshot source and semantics for recomputing risk capacity;
- explicit operator recovery/correction and Kill Switch reset procedure;
- whether manual Stop waits for a bounded graceful completion or offers a controlled abort;
- any future integration of T1/T2 runtime or external order systems.

## Verification and authorization record

- Work: design and record Persistent State Contract, recovery semantics, idempotency, crash handling and session lifecycle.
- Scope: documentation only; no source code, tests, workflows, database, market data, host, VPS or runtime changed/accessed.
- Source branch: `main`.
- Parent/source HEAD before this decision record: `ac7fc0c641c67a66743c3ac8568454a94cd9c180` (previous on-demand decision commit; latest handoff content was inspected before this write).
- Tests/workflows/Actions run/job/artifact: none.
- Status: **DESIGN REVIEWED / RECORDED**; implementation **NOT STARTED / NOT AUTHORIZED**; runtime **NOT STARTED / NOT AUTHORIZED**.
- Next: review the open decisions and approve a separately bounded contract-first implementation/test task. No database or runtime work is implied.
