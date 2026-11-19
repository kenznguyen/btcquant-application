# F4 Read-only Source Audit — 2026-11-19

## 1. Scope and disposition

Owner-approved scope: audit all of F4.1 Shared Risk Engine, F4.2 Position & Portfolio Management, and F4.3 Risk Protection. This is a static/read-only audit only.

- Paper-only; no live trading, real orders, exchange execution, VPS/runtime, database mutation, schema migration, deployment, or T0/T1/T2 changes.
- No source, test, workflow, dependency, configuration, or data file was modified.
- Tests and workflows were NOT RUN in this audit.
- No workflow was dispatched and no artifact was produced by this audit.

Overall disposition: **BLOCKED for implementation/migration approval** pending the required findings below and exact-source CI verification.

## 2. Repository and source provenance

### Official application repository

- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Audited starting HEAD: `556f0e0749549da141993cc9edcc474de4265928`
- `docs/PROJECT_SESSION_HANDOFF.md` was read before source inspection.
- The official application tree inspected at this HEAD contains the T0 data foundation but does not contain the F4 implementation paths listed below. F4 is therefore **not verified as migrated** into the official application repository.

### Legacy/source repository used for the read-only audit

- Repository: `kenznguyen/btcusdt-telegram-signals2`
- Branch: `feature/t0-centralized-data-feeder-p1-20261101`
- Audit HEAD: `8623d1076d6b821091ff9da0d84033f48fd8ba7a`
- HEAD commit is a documentation-only T0 handoff update. No current combined commit statuses were returned for this HEAD.
- Current source blobs inspected at the audit HEAD:

| Path | Blob SHA |
|---|---|
| `paper_execution/risk_control.py` | `3c76e462b0b4d924c2418842d95ed74285e2315d` |
| `paper_execution/ledger.py` | `37c0aeb9dd28514dd19b87667b762c5592baf61f` |
| `paper_execution/equity.py` | `40d6566294355c646839614c92f8fba6116b582c` |
| `paper_execution/account_equity.py` | `9971dae4592f07fe7bd2315c0f1ec1daf97af8d1` |
| `paper_execution/daily_baseline.py` | `747808d9a68a70e9c2aa6f71f00aeeffb6682145` |
| `risk_policy.py` | `91b46513041033cbcd7e939ed081b71714c82ff3` |
| `pipeline/core_strategy.py` | `c14e76f2cecb9f8aca54db263ded1ff17881cb24` |
| `pipeline/core_signal.py` | `df5fbb59611bdd4fbb8224665f79655dd4433455` |
| `pipeline/decision.py` | `8720d8ab988529b1545a27aa0792beca9e6a84aa` |
| `pipeline/api.py` | `d0217944bbfa9b864b0f259e0091daf9a989d180` |
| `paper_execution/test_risk_control.py` | `69c9177a249369f52d0c81e442c9c4583c9f5b77` |
| `paper_execution/test_risk_limits.py` | `22645c481eea3f807fc72d659cdd05989f5673c5` |
| `paper_execution/test_ledger.py` | `0c05ae1ed0d9526978f8a90c983957dbd7baed5a` |
| `paper_execution/test_dual_ledger_red.py` | `2c2104ada5743cbf55f64c8bc9690a14142fe3e0` |
| `pipeline/test_api.py` | `4e2d92b24a7c8c0810ac5f2706707c5b9deb6fb2` |

## 3. Architecture and governance constraints

The current Core-First decision (2026-11-12) says Strategy Core (RSI + ADX + Smart DCA) is the only strategy in the paper-trading decision path. AI Strategy is offline research only and must not create AI Ledger entries or paper orders until a separate owner decision reopens that scope. `AI_EXECUTION_ENABLED=false` remains mandatory.

The risk authority must also remain a single source of truth: a simulated-account Ledger must obtain risk limits from the validated Account/Risk Contract and must not accept an independent set of values that can override or diverge from that contract.

This audit does not reopen AI execution or alter these decisions.

## 4. F4.1 — Shared Risk Engine

### Static implementation present

- Dual-strategy ledger writer uses `BEGIN IMMEDIATE` and computes account-wide gross exposure across strategy ledgers and active reservations.
- Opposite LONG/SHORT positions are counted as gross exposure rather than netted.
- ENTRY and exposure-increasing DCA use a fresh 1% of admission-time reconciled account equity as the margin budget.
- Core leverage is pinned to 13x. The AI ledger constructor checks 1x–3x, but AI admission remains blocked/deferred.
- New exposure checks risk readiness, mark freshness, funding provenance, daily baseline, drawdown, daily loss, gross exposure, liquidity/book validity, and Kill Switch.
- Concurrency, gross exposure, one-percent margin budget, missing account-risk inputs, and Kill Switch cases have named tests.

### Required findings

**F4-R1 — Risk limits are not sourced exclusively from the validated Account/Risk Contract. Severity: HIGH / REQUIRED.**

`PaperLedger.__init__` accepts caller-supplied `risk_limits`; `pipeline/api.py::ledger()` obtains values from environment parsing and passes them to each ledger instance. The scoped writer then uses `self.risk_limits` for account-wide max drawdown, daily loss, and exposure admission. The policy is therefore instance/config supplied, not loaded and verified from one immutable account-level contract. Separate Core and AI writer instances can be configured with different limits, allowing one writer to admit exposure that another would reject. This conflicts with the single-source-of-truth architecture constraint.

Required correction: make the account risk contract the only source of limits; bind a version/hash to the account and reservation; reject missing, invalid, stale, or conflicting contract state. Do not implement in this audit.

**F4-R2 — Missing Kill Switch table is interpreted as an unlatched system. Severity: HIGH / REQUIRED.**

`risk_control.snapshot()` returns `paused=false` and `killed=false` when `paper_risk_control` does not exist. The scoped API ledger factory uses `apply_migrations=false` and returns after migration readiness checks, before `risk_control.ensure()`. The dual-ledger migration readiness check does not require the risk-control table. A missing/corrupt latch can consequently be treated as a clear latch instead of a fail-closed state.

Required correction: missing or malformed latch state must block new exposure and report unavailable/corrupt risk state. Add regression coverage for missing table, missing row, malformed values, and concurrent latch changes.

## 5. F4.2 — Position & Portfolio Management

### Static implementation present

- Separate strategy ledgers exist for `STRATEGY_CORE`, `AI_FREQAI`, and `LEGACY_UNATTRIBUTED`.
- Position ownership is strategy-scoped; one strategy cannot mutate another strategy's position/order.
- Shared account equity reconciles capital, realized/unrealized PnL, fees, funding, legacy adjustments, marks, and reservations.
- Reservations persist account/strategy/intent identity, remaining notional/margin, leverage, equity basis, risk-config version, and expiry.
- Fill events are journaled per level in the order transaction; idempotency and SQLite writer serialization protect against duplicate fills.
- Shared book depth is reserved across Core/AI and legacy consumption.
- Smart DCA state is strategy-scoped and the current ledger enforces one DCA use per position.
- Current dual CANCEL helper resolves and validates owner inside `BEGIN IMMEDIATE`; it checks reservation/order identity, validates expiry sweep ownership, uses guarded row-count updates, and records audit in the same transaction. Current tests include missing reservation, ownership mismatch, expiry rollback, repeated cancel, and audit-failure rollback cases.

### Conditional gaps

- The current Core-First decision defers AI from all paper-submit paths. The current API blocks AI when dual-ledger mode is active and admission is unavailable, but retains a legacy fallback when dual-ledger readiness is false: AI evaluation can be routed through the MANUAL ledger. The decision function currently returns WAIT without an admission context, but the fallback remains a latent route; API tests can inject a valid AI decision and exercise that path. There is no explicit `AI_EXECUTION_ENABLED=false` enforcement at this API routing boundary. This must be closed before any F4 source migration or runtime use.
- TP/SL decisions are produced in Strategy Core; the paper ledger applies the resulting target-position intent. No separate F4 TP/SL manager was identified. Confirm that this division of responsibility is intentional in the final architecture rather than assuming an independent F4 stop engine exists.
- Account snapshots expose per-strategy initial margin and aggregate remaining reservation margin, but there is no single explicit aggregate used-plus-reserved margin field. Confirm whether the account contract requires a first-class aggregate field or whether summing the per-ledger and reservation fields is the intended interface.

## 6. F4.3 — Risk Protection

### Static implementation present

- Persistent pause/kill latch with explicit acknowledgement.
- Kill latch blocks exposure increases while valid reductions remain permitted.
- Max drawdown and daily-loss breaches latch Kill Switch.
- Account mark/equity uses a shared account transaction, 30-minute freshness checks, dataset identity, funding provenance, and one-time account cutover.
- Funding gaps, stale marks, unreconciled equity, missing cutover, and invalid daily baseline block new exposure.
- Daily baseline has immutable audit/replay validation and UTC rollover checks.
- Tests cover Kill Switch persistence, priority, risk-limit breaches, account cutover, funding provenance, daily baseline rollover, and reduction-only behavior.

### Required finding

**F4-R3 — Kill Switch reset trusts caller-supplied readiness and is not atomic with readiness evaluation. Severity: HIGH / REQUIRED.**

`risk_control.reset_kill(connection, acknowledge, ready, at_ms)` only checks that the caller passes `acknowledge is True` and `ready is True`; it does not verify account risk readiness or pending orders itself. `PaperLedger.reset_kill()` exposes that parameter directly. The API performs `control_readiness()` on separate reads before opening the write transaction, leaving a time-of-check/time-of-use gap. In the non-dual/legacy branch, `control_readiness()` sets `accountRiskReady=True` without verifying account-level cutover/risk readiness.

Required correction: readiness must be computed from authoritative state inside the same write transaction that clears the latch. The legacy fallback must not promote missing Dual Ledger/account risk state to READY. Add tests for direct reset attempts with forged readiness, risk state becoming stale between check and reset, missing account cutover, pending orders, and legacy fallback.

## 7. AI boundary — explicit non-authorization

- The Core-First architecture decision remains controlling.
- AI calibration, trusted admission, account-equity sizing, and AI 1x–3x leverage admission are not verified as complete.
- Current `pipeline/decision.py::evaluate()` requires an admission context; `pipeline/api.py::decide()` does not supply one, so the ordinary decision path returns WAIT.
- The legacy API fallback still makes AI paper submission structurally reachable if an intent is supplied; it is not acceptable under the Core-First decision.
- Do not connect AI to F4, create AI orders, run AI paper execution, or enable AI execution under this audit.

## 8. Test and CI evidence

Historical evidence exists, but it does not prove the current audited source:

- DS-03 source SHA: `6ef0d7456b2791fae73bfea8855ee30482774673`.
- Historical workflow: run `42975606884`; documented result 237/237 focused tests and 300/300 full `paper_execution` regression tests PASS; artifact ID `13834194926`; SHA-256 `66403ab6b9c8079e2d9f3b04dcfc650709a64abd77e62554e6a54c2c101cd5c4`.
- The audited current source blobs differ from that historical source: current `ledger.py` blob is `37c0aeb9dd28514dd19b87667b762c5592baf61f` versus the DS-03 blob `21ff7ce8446381baaa4102553fc8f69a8bbacbb3`; current `pipeline/api.py` is `d0217944bbfa9b864b0f259e0091daf9a989d180` versus `d3f587c795daa89b54beb5783b89f14acc189df0`; current dual-ledger test blob is `2c2104ada5743cbf55f64c8bc9690a14142fe3e0` versus `2be7188537911615b7df387d33835c281878ecc7`.
- Current audit HEAD `8623d1076d6b821091ff9da0d84033f48fd8ba7a`, latest relevant source commits, and the current source blobs had no combined commit statuses returned in the inspected GitHub status lookups.
- Therefore current exact-source compile, focused tests, full regression, workflow run, and artifact are **NOT VERIFIED**. No workflow or tests were run in this audit.

## 9. Status matrix

| Scope | Static source inventory | Audit disposition | Current exact-SHA CI |
|---|---|---|---|
| F4.1 Shared Risk Engine | PASS | **BLOCKED** — risk-limit authority and missing-latch fail-open findings | NOT VERIFIED |
| F4.2 Position & Portfolio | PASS | CONDITIONAL PASS — core ledger/cancel controls present; AI fallback and architecture boundary unresolved | NOT VERIFIED |
| F4.3 Risk Protection | PASS | **BLOCKED** — reset readiness not independently/atomically verified | NOT VERIFIED |
| F4 overall | PASS — source exists in legacy repo | **BLOCKED** for migration/implementation approval | NOT VERIFIED |
| Official application repo | F4 source not found in inspected tree | NOT MIGRATED / NOT VERIFIED | NOT VERIFIED |
| Runtime / DB / VPS / exchange | Not inspected or changed | NOT RUN / NOT AUTHORIZED | N/A |
| Live trading | Not in scope | PROHIBITED | N/A |

## 10. Next bounded steps

1. Define and approve a bounded TDD correction for F4-R1, F4-R2, and F4-R3. Keep changes in the existing legacy source branch; do not create a parallel PR or migrate source yet.
2. Add an explicit Core-First AI deny rule at every paper-submit entry point, including the legacy fallback. Preserve AI offline signal/research artifacts without AI Ledger writes.
3. Add RED tests for risk-contract divergence, missing/malformed Kill Switch state, direct/forged reset readiness, readiness TOCTOU, and AI fallback submission.
4. After separate implementation approval, run the existing isolated GitHub Actions workflow at an exact SHA; record source SHA, run ID, job conclusions, test counts, artifact ID/name/digest. No persistent DB, runtime, exchange or live-order actions.
5. Only after source fixes and exact-SHA GREEN evidence, prepare a separate migration proposal for the official application repository with source SHA/file provenance. Do not migrate legacy history or activate runtime as part of this audit.

Audit conclusion: **static source inventory PASS; F4.1 BLOCKED; F4.2 CONDITIONAL PASS; F4.3 BLOCKED; overall F4 BLOCKED; exact-SHA CI NOT VERIFIED.**
