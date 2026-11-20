# On-Demand Execution — Manual Start/Stop with Persistent State — 2026-11-20

## Owner decision

The owner selected:

- Execution mode: **On-Demand, manually started and stopped**.
- Cross-session state: **Persistent**.
- Runtime posture: **No 24/7 process, no automatic scheduler, no background/autostart service**.

This records an architecture decision only. It does not authorize implementation, runtime activation, database creation/migration, Feeder startup, T1/T2 runtime connection, deployment, or trading.

## Architecture

1. The user explicitly starts an analysis/execution session through an approved application entry point.
2. The Orchestrator creates a unique session identity and validates configuration, data availability/freshness, persisted state version/integrity, and prior-session closure.
3. Strategy Core (RSI + ADX + Smart DCA) and the independent AI Strategy execute as separate decision producers. Either may emit its own proposal; Core silence does not suppress an AI proposal.
4. Core and AI retain separate decision/position ledgers and provenance.
5. Every proposed entry/add/reduction/exit must pass the same Shared Risk Engine and Kill Switch. No strategy may bypass this gate.
6. The session persists its inputs/provenance, strategy outputs, risk decisions, paper-position changes, and a consistent checkpoint.
7. The session closes explicitly and the process exits. Durable state remains available for a later manually started session.

## Persistent-state contract — design requirements

Persistent state means durable business state, not a continuously running process.

- Persist paper positions, entry basis/average price, quantity, realized/unrealized accounting state, Smart DCA level/count/next eligibility, strategy-specific state, risk limits/usage, kill-switch state, and event/decision history as applicable.
- Keep Core and AI ledgers logically separate; do not merge ownership or attribution of positions.
- Store schema/version, session ID, event sequence or equivalent ordering, source/data snapshot identity, strategy/model/config version, and timestamps/provenance.
- Commit state transitions and their corresponding events atomically or through a recoverable append/checkpoint protocol. A partially persisted session must not be treated as a valid completed checkpoint.
- Make session replay/retry idempotent: repeated processing must not duplicate entries, DCA additions, exits, or accounting events.
- On restart, validate checkpoint compatibility and integrity before restoring. Unknown schema, corrupted/incomplete checkpoint, conflicting session, or missing required state must fail closed.
- Validate market-data freshness and coverage at each new session. Do not assume that the latest persisted candle is current. If required data is stale, incomplete, or inconsistent, do not admit new simulated trades.
- Persisted paper positions remain open in the ledger while the process is stopped; no monitoring or protective action occurs while stopped. This limitation must be visible in the UI and session report.
- State retention, backup/restore, encryption/access controls, and operator reset/correction procedures require a separate design and approval before implementation.

## Session lifecycle

IDLE -> START_REQUESTED -> PREFLIGHT -> RUNNING -> CHECKPOINTING -> CLOSED

Any failed preflight, risk-system unavailable state, persistence failure, or invalid checkpoint must transition to a non-trading failed/blocked state. Do not silently initialize a fresh state when persistent state was expected.

A process crash during RUNNING/CHECKPOINTING must leave enough durable evidence to classify the session as incomplete and recover safely; it must not be represented as CLOSED without verified checkpoint completion.

## Risk and strategy invariants

- Preserve Strategy Core: RSI + ADX + Smart DCA.
- AI Strategy remains independent and may produce LONG/SHORT proposals even when Core has no signal.
- Core and AI decisions/positions remain separately attributable.
- All proposed trading actions pass through the common Shared Risk Engine and Kill Switch.
- Preserve paper-first posture. No live orders or real trading.
- Do not carry forward an unsafe or stale risk allowance merely because it was persisted; risk capacity must be recomputed/validated for the new session using the approved account/equity snapshot and common policy.

## Benefits and limitations

Benefits:
- No always-on VPS/service requirement for the selected operating mode.
- Lower idle compute and operational overhead.
- Explicit operator control over when analysis runs.
- Durable paper-state continuity across sessions.

Limitations:
- No signal detection, data collection, monitoring, alerting, or risk intervention while stopped unless separately operated by an approved external process.
- Signals are produced only when a session is started and its preflight passes.
- Market data may be stale between sessions; every session must independently validate freshness.
- Persistent state increases the importance of atomic writes, versioned migrations, idempotency, recovery tests, and backups.

## Scope boundaries

This decision does not authorize:
- source-code implementation or schema migration;
- creation/opening/writing of any production or Canonical database;
- T0 reconstruction, archive access, Feeder startup, or changes to T0's independent data lifecycle;
- T1 provider activation or T1-to-T2 runtime connection;
- persistent service, systemd, autostart, scheduler, VPS deployment, or 24/7 runtime;
- integrated paper execution until separately approved;
- live trading or real orders.

The existing Application-first delivery order remains in force. Any implementation should be separately scoped, test-first, isolated, and evidenced before runtime approval.

## Verification record

- Work: evaluate and record the owner-selected On-Demand Execution architecture.
- Scope: decision/design documentation only.
- Tests/workflows: none; no source code or runtime changed.
- Source branch: main.
- Parent/source HEAD observed before this record: 71f01f2dd1d6cf29c7c09edb8126b8b91e6ea5b8.
- Actions run/job/artifact: none.
- Status: **ARCHITECTURE DECISION APPROVED / RECORDED**; implementation **NOT STARTED / NOT AUTHORIZED**; runtime **NOT STARTED / NOT AUTHORIZED**.
- Next: separately review a versioned persistent-state contract and session lifecycle test plan before authorizing implementation.
