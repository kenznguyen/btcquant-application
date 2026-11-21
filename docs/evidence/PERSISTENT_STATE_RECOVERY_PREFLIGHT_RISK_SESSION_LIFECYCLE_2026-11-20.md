# D5 implementation increment — repository evidence gates, durable audit and SessionOrchestrator — 2026-11-21

## Status

**PASS — repository-level preflight/READY gates, durable evidence persistence, explicit operator Resume audit, and SessionOrchestrator contract tests.**

**Runtime integration: BLOCKED / NOT VERIFIED.** The orchestrator prepares a session to READY and supports an explicitly approved transition to RUNNING. It does not start Core/AI workers or execute paper orders.

## Exact source and CI evidence

- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Exact tested source SHA: `64001345c5e41089b4e75f2bb075067386543f35`
- Workflow: [44856004749](https://github.com/kenznguyen/btcquant-application/actions/runs/44856004749) — **SUCCESS**
- Job: `136698296005` — **PASS**
- Persistent State contract suite: **144 tests PASS**
- Adjacent Paper Ledger / Strategy API regressions: **160 tests PASS**
- Artifact: `persistent-state-contract-test-evidence`
  - ID: `14687805995`
  - SHA-256: `e7ccede1d2ee572ef64d2c135ada41d1fc85fe1813242ca8662c3e9bb03ecc93`
  - Expires: 2026-12-05.

## Implemented

### Repository transition enforcement

- `PREFLIGHT -> RESTORING` requires a typed, passing `PreflightAttestation` bound to session ID, account scope, fencing generation, config hash and source snapshot.
- `RESTORING -> READY` requires a complete `ReadyEvidenceBundle`: preflight, restore and risk readiness attestations.
- The repository performs validation inside the same SQLite transaction that writes evidence and advances the session. A direct generic transition without evidence is rejected.
- Validation checks exact session/account/fence/config/snapshot binding, evidence timestamps, event head, Core and AI ledger reconciliation, risk ledger reconciliation and Kill Switch latch.
- The orchestrator also compares the restore attestation event head, aggregate-version map and checkpoint identity against deterministic replay output before READY.

### Durable evidence and schema compatibility

- Added append-only `ps_session_attestations` and `ps_session_operator_actions` with SHA-256 payload checksums and update/delete prevention triggers.
- Preflight evidence is persisted before RESTORING. Restore and risk evidence are persisted atomically with READY.
- The additive extension retains schema `user_version=1`; existing v1 databases remain readable for base operations and require explicit `migrate_v1_session_evidence()` before gated transitions. No implicit migration or schema creation occurs during startup.
- `claim_writer` seeds a new session's committed event head from the account's persisted event history so recovery evidence is checked against the actual replay boundary.

### Operator-only Resume and orchestration

- READY cannot transition to RUNNING without `OperatorResumeConfirmation`, a fresh passing risk attestation, and an append-only operator action record.
- `SessionOrchestrator.start()` claims a manual session, performs preflight, invokes deterministic repository recovery, obtains restore/risk attestations and stops at READY. It does not auto-resume or start strategy workers.
- `prepare_resume()` performs the fresh risk check before operator confirmation. `resume()` requires an injected operator-approval verifier and persists the confirmation audit.
- Tests cover direct PREFLIGHT/READY bypass, missing/mismatched evidence, evidence persistence/reopen/checksum, additive v1 migration, restart recovery, mismatched replay attestation, blocked preflight/restore, unauthenticated Resume and successful audited Resume.

## Remaining blockers and limits

- **B1 Evidence gates: PASS at repository lifecycle boundaries** for PREFLIGHT -> RESTORING, RESTORING -> READY and READY -> RUNNING. Independent code review remains **NOT VERIFIED**.
- **B2 Full risk policy integration: BLOCKED.** This increment verifies typed risk-readiness evidence; it does not complete drawdown, daily-loss, exposure and margin policy integration end-to-end.
- **B3 Kill Switch persistence: BLOCKED.** Latch/reset/audit across real application restarts is not yet verified end-to-end.
- **B4 Strategy restoration: BLOCKED.** Core/AI reconciliation is represented by attestation fields and provider ports; actual independent Core/AI ledger restoration is not integrated.
- **B5 Market-data preflight: PARTIAL.** The orchestrator requires a provider-produced attestation, but the production adapter must still calculate feature-specific lookback from actual strategy configuration. No live T0 data was available or accessed.
- The operator approval verifier is an injected port. Production authentication/API/UI wiring is **NOT VERIFIED**; CI uses an isolated test verifier.
- No Canonical T0 database, reconstructed database, Feeder, VPS, T1/T2 runtime, exchange credentials, account or execution was accessed. All SQLite integration tests use temporary test databases and synthetic fixtures only.

---

# Session readiness evidence contract increment — 2026-11-21

## Status

**PASS — typed evidence contracts and isolated contract tests.**

**B1 Evidence gates: PARTIAL / NOT CLOSED.** This increment adds immutable typed attestations and a pure validator for matching session, account, config, source snapshot and fencing generation. The repository's generic `advance_session` method still permits direct status transitions; repository-level enforcement and the SessionOrchestrator are not yet implemented. Do not treat this increment as proof that callers cannot bypass the validator.

## Exact source and CI evidence

- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Exact tested source SHA: `bd3ade272a226799e34699e49f3d22de1067bc94`
- Commits in this increment:
  - `ca858faa73659a493bd6c2e61f9cd6a8779ab7ca` — add RED contract tests.
  - `0e3cf13e9ff0017c5a37da3241e041bae3d7cc51` — include the new test module in the isolated workflow.
  - `bd3ade272a226799e34699e49f3d22de1067bc94` — implement typed evidence contracts.
- Workflow run: [44853569768](https://github.com/kenznguyen/btcquant-application/actions/runs/44853569768) — **SUCCESS**
- Job: `136690345154` — **PASS**
- Persistent State tests: **130 tests PASS** (7 new evidence contract tests).
- Adjacent Paper Ledger / Strategy API regressions: **160 tests PASS**.
- Artifact: `persistent-state-contract-test-evidence`
  - ID: `14686312334`
  - SHA-256: `d213583eb6280a8e139a870138fc2499968026ba2666c231155e0ae45181968d`
  - Expires: 2026-12-05.

## Implemented

- `persistent_state/evidence.py`: immutable `EvidenceBinding`, `PreflightAttestation`, `RestoreAttestation`, `RiskReadinessAttestation`, and `validate_ready_evidence`.
- Enforces successful outcomes, exact config/source binding, session/account/fencing-generation binding, timestamps not preceding session start, preflight M15/H1 lookback shape, restore event-head match, Core + AI ledger reconciliation, and unlatched Kill Switch.
- `persistent_state/test_evidence.py`: 7 deterministic tests for success, missing evidence, stale session/fence, config/snapshot mismatch, failed attestations, Kill Switch latch and Core/AI reconciliation.
- `.github/workflows/persistent-state-contracts.yml` now includes the new test module.

## Isolation

- CI uses isolated Python 3.12 contract tests and the existing no-network disposable container for adjacent regressions.
- No Canonical T0 database, reconstructed T0 database, T0 provider, Feeder, VPS, T1/T2 runtime, account credentials, exchange or order execution accessed.
- No production database created and no runtime started.

## Remaining work

1. Enforce evidence requirements at the repository transition boundary so generic callers cannot bypass READY gates.
2. Implement SessionOrchestrator with explicit preflight, restore, evidence verification and operator-only Resume.
3. Close full risk-policy, Kill Switch persistence/audit and strategy-specific restoration blockers with dedicated tests and review.

---

# Persistent State recovery, preflight, risk admission and lifecycle evidence — 2026-11-20

## Status

**PASS — bounded contract-first/test-first implementation and isolated verification.**

**Integration readiness: BLOCKED / NOT VERIFIED.** The contracts and pure admission/preflight/recovery components are not yet wired into a single application session orchestrator or Core/AI runtime. Runtime activation remains outside the approved scope.

## Exact tested source and CI

- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Exact tested source SHA: `4a4bc03e36b499a810a58a10ca39f39ba24326cb`
- Workflow: [44721296830](https://github.com/kenznguyen/btcquant-application/actions/runs/44721296830) — **SUCCESS**
- Job: `136237504513` — **PASS**
- Persistent State test suite: **123 tests PASS**
- Adjacent Paper Ledger / Strategy API regression suite: **160 tests PASS**
- Artifact: `persistent-state-contract-test-evidence`
  - ID: `14621542945`
  - SHA-256: `98b326831b66df378929ee9235a2c5d9d31d05556f3b299f3af9eed145b0da17`
  - Expires: 2026-12-04

## Implemented and verified

### Crash/restart recovery and checkpoint reconciliation

- `persistent_state/recovery.py`, blob `fc0ad00fbed4fca2886ae44a0fe6ba1190334f7c`
- `persistent_state/test_recovery.py`, blob `007143d44bc06068877ccb3f9610a8a4af843439`
- Persisted event projection includes aggregate identity and immutable post-transition aggregate-state snapshot.
- Recovery validates contiguous account event sequence, per-aggregate version continuity, aggregate identity and canonical state snapshots.
- When no checkpoint exists, replay starts from the empty aggregate envelope and replays the full event history.
- When a checkpoint exists, recovery independently replays the event prefix and requires exact checkpoint payload and aggregate-version reconciliation before replaying the tail.
- Final replayed aggregate state/version must match materialized SQLite aggregates.
- Repeated recovery is deterministic and read-only.
- Manual restart test reopens the temporary SQLite database, marks the previous unfinished session INTERRUPTED through a new writer claim, and restores the verified checkpoint plus committed tail.

### M15/H1 market-data preflight

- `persistent_state/preflight.py`, blob `472e9eaffa51e24a6c265a8296a9e387829b0b5b`
- `persistent_state/test_preflight.py`, blob `98ddf54b24a167cdb4aa678d910809de811e0fda`
- Pure validation over deterministic synthetic fixtures only.
- Enforces BTCUSDT USDT perpetual, approved Binance USD-M source `ccxt.binanceusdm`, same source identity and common `asOfMs` across M15/H1.
- Enforces exact required lookback counts, complete coverage and explicit empty gap list.
- Validates aligned, ordered, unique, closed candles; first-observed timestamp must be at/after close and no later than the captured preflight clock.
- Validates finite decimal OHLCV and OHLC bounds.
- Freshness is measured from the latest candle close: M15 <= 20 minutes; H1 <= 70 minutes.
- Produces deterministic snapshot identity from source, timeframe dataset versions, candle ranges and common as-of time.

### Shared Risk Engine / Kill Switch admission

- `persistent_state/risk_admission.py`, blob `fe2804fe3e7929f4bf5043e64c742c9d27ec88ec`
- `persistent_state/test_risk_admission.py`, blob `3a67dc9d57e26b6cd161d28d6facd90b53ccdf12`
- Core and AI proposals use the same admission engine and account-scoped RiskState.
- Fail-closed for non-RUNNING sessions, unavailable risk engine/state, unreconciled ledger, account-scope mismatch and latched Kill Switch.
- Enforces the current 1% per-new-order margin budget and rejects total reserved-plus-requested margin above account equity.
- Rejects binary floats, non-finite and non-positive accounting inputs.

### Full session lifecycle review

- `persistent_state/lifecycle.py`, blob `aef569186bf6e2d4886f0475c798274010b887ee`
- `persistent_state/test_lifecycle.py`, blob `14af04d926547152e8c85f3572369eef4847e11d`
- `persistent_state/test_session_fencing.py`, blob `0d0ba4c1f9faf7682938a8b3bc62b632e6b6f4eb`
- `persistent_state/repository.py`, blob `9d824c5fe8597e22ea4f676d0af453a7779bd4c2`
- Verifies the complete documented transition matrix and rejects undocumented transitions.
- Tests manual writer claim, monotonically increasing fencing generations, stale-writer rejection, and per-account isolation.
- Tests that no new paper transition commits after CHECKPOINTING begins.
- CLOSED requires a verified checkpoint from the current session at the latest committed event boundary; checkpoint checksum, active pointer and aggregate-version prefix are revalidated.
- Graceful Stop has a 30-second bound. A late checkpoint is rejected and an expired close becomes INTERRUPTED, never falsely CLOSED.
- BLOCKED_PREFLIGHT, BLOCKED_RESTORE, FAILED_PERSISTENCE and ABORTED are terminal and cannot resume.
- Tests preserve a cleanly CLOSED session when a later manual session starts.

## TDD and regression history

- Recovery RED: [44718714463](https://github.com/kenznguyen/btcquant-application/actions/runs/44718714463) — recovery module absent.
- Preflight RED: [44719626111](https://github.com/kenznguyen/btcquant-application/actions/runs/44719626111) — preflight module absent.
- Risk admission RED: [44720312968](https://github.com/kenznguyen/btcquant-application/actions/runs/44720312968) — risk admission module absent; the first fixture iteration also exposed a preflight timing mismatch.
- Session close reconciliation RED: [44720698433](https://github.com/kenznguyen/btcquant-application/actions/runs/44720698433) — reproduced that a checkpoint with tampered aggregate versions could otherwise close a session.
- Risk capacity RED: [44721171812](https://github.com/kenznguyen/btcquant-application/actions/runs/44721171812) — reproduced that a 1%-bounded new order could still exceed total equity when existing margin was nearly fully reserved.
- Final GREEN: [44721296830](https://github.com/kenznguyen/btcquant-application/actions/runs/44721296830) — exact source SHA above; 123 + 160 tests PASS.

## Code-review findings and integration blockers

The isolated components pass their current contract tests, but this is **not approval to integrate or activate a trading runtime**.

1. **Session evidence gates are not yet enforced by one orchestrator.** The repository state machine validates status order, but callers can still request PREFLIGHT -> RESTORING or RESTORING -> READY through the generic transition API without presenting a typed successful preflight/recovery attestation. Before integration, add durable evidence gates so READY cannot be reached by status sequencing alone.
2. **Risk admission is not yet wired to the existing complete account risk policy.** This new gate checks Kill Switch, reconciliation, per-order 1% margin and total equity capacity. It does not itself evaluate max drawdown, daily loss and max exposure. Those remain in the existing Paper Ledger risk contract and must be unified through one shared engine before Core/AI runtime wiring.
3. **Kill Switch persistence across application restart is not end-to-end verified.** RiskState contract and latch admission are tested, but the new repository does not yet provide an end-to-end risk-state restore/reset workflow with audit evidence.
4. **Strategy-specific restoration is not complete.** Generic aggregate replay is verified; Core Smart DCA event/ledger reconciliation and AI/Core cross-ledger recovery invariants still require dedicated integration tests.
5. **Market preflight is fixture-only.** No T0 HTTP/API or live data access was used. The strategy-specific required lookback counts must be supplied from approved Core/AI feature configuration at integration time.

## Isolation and limits

- All SQLite writes and recovery tests used disposable temporary directories.
- No production database, Windows known-folder path, Application Data directory or staging database was created/opened.
- No T0 Canonical, T0 feeder, Binance, T1/T2 runtime, VPS, network provider, credentials, exchange account or order execution was accessed.
- No scheduler, autostart, systemd service, background worker or 24/7 runtime was added.
- No live orders or real trading.
- No event/idempotency/checkpoint retention deletion or compaction.

## Next step

Keep runtime/integration **BLOCKED** until the five integration blockers above are closed with contract-first tests and an independent code review. Continue manual On-Demand / paper-only posture. T0 remains an independent data asset.
