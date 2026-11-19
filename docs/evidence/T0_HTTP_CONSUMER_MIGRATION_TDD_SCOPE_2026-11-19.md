# T0 HTTP Consumer Migration — TDD Scope — 2026-11-19

## 1. Approval and boundary

Status: **APPROVED FOR SCOPE PREPARATION ONLY**.

This approval authorizes documenting the TDD migration scope for the active Core First HTTP consumers from T0 Candle API contract 1.0.0 to the official T0 contract 1.1.0. It does not authorize implementation, test execution, CI dispatch, endpoint probing, runtime connection, deployment, activation, data mutation, strategy execution or trading.

Official target repository: `kenznguyen/btcquant-application`, branch `main`.
Active consumer source: `kenznguyen/btcusdt-telegram-signals2`, branch `feature/core-operational-proof-20261112`, inspected HEAD `e6606e28a696374f31cd6db1ec0a1372d942d64d`.
T0 contract authority: official target `market_data/api.py`, contract `1.1.0`, blob `4f923d400b8e133a602cec7239982fdf357e9e21`.
Compatibility evidence: [T0 External HTTP Consumer Compatibility Audit](T0_EXTERNAL_HTTP_CONSUMER_COMPATIBILITY_AUDIT_2026-11-19.md).

## 2. Objective

Make the active Core First HTTP consumer path correctly interpret contract 1.1.0 while preserving the contract's distinction between:
- per-page timestamp validity and coverage;
- freshness of the final/assembled requested window at its evaluation anchor;
- ingestion lag policy configured by the consumer;
- strategy readiness/evaluability.

The server's 1.1.0 semantics are authoritative. Do not downgrade T0, widen validation by silently accepting unknown contract versions, infer freshness from response generation time when an explicit evaluation anchor exists, or fabricate `evaluable=true`.

## 3. In-scope components

On the active Core First source branch only:
1. `freqai_bridge/http_candles.py` — shared HTTP client and page validation/aggregation.
2. `core_runtime/bundle_inputs.py` — Core Bundle contract/envelope normalization.
3. Contract fixtures and focused tests for the above.
4. `core_runtime/bundle_provider.py` and `core_runtime/runtime_factory.py` — inspect and test call-path compatibility; change only if required by the contract.
5. `pipeline/api.py` — Common API gateway path through the shared client; verify bounded window behavior.
6. Android Five-Layer and Core dashboard consumer tests/fixtures for additive response shape and explicit quality metadata behavior. Do not redesign either UI in this scope.

The separate older T0 branch `feature/t0-centralized-data-feeder-p1-20261101` is not an implementation target unless a later explicit scope selects it. The official `btcquant-application` local-Storage API is not an HTTP consumer and is not to be modified for this migration.

## 4. Required RED test matrix

Tests must be deterministic and use synthetic payloads, fake HTTP responses and temporary/in-memory data only.

### Contract and freshness envelope
- Accept exactly contract version `1.1.0`; reject unsupported versions.
- Require the exact 1.1.0 freshness field set, including `evaluationTimeMs`, `evaluationAnchor`, `timestampValid`, `fresh` and `evaluable`.
- Validate types, nullability and consistency of the freshness fields.
- Verify `generatedAtMs` is not substituted for `evaluationTimeMs` when the response is anchored by `asOfMs`.
- Reject future `asOfMs` and malformed/mismatched evaluation anchors.
- Reject `timestampValid=false`, invalid candle timestamps and invalid first-observed availability.
- Reject incomplete coverage; preserve the distinction between complete coverage and freshness.

### Page-aware pagination
- Windows of 1, 32, 33, 96, 100 and 3,000 candles.
- Complete historical earlier pages may have `evaluable=false) / `fresh=false` while still being structurally valid pages; they must not be rejected solely for not being the final fresh page.
- Final page stale or non-evaluable must make the assembled window non-evaluable.
- Any page with invalid timestamps or incomplete coverage must fail the assembled result.
- Verify stable ordering, no duplicate/missing candle opens, cursor progression, page boundaries and bounded maximum window.
- Verify the final assembled freshness verdict is evaluated against the same requested evaluation anchor, including explicit `asOfMs`.
- Verify empty, short, malformed, repeated-cursor and inconsistent-page responses fail closed.

### Core Bundle and call paths
- Core Bundle normalizer accepts valid 1.1.0 envelope and rejects invalid/malformed envelope.
- Core Bundle preserves the authoritative evaluation anchor and quality fields without rewriting them.
- Core M15 and H1 provider paths use the same semantics.
- Common API candle route propagates correct success/failure and does not turn an invalid T0 window into a successful response.
- Ingestion `max_lag_ms` remains a separate policy based on availability versus close time; it must not be conflated with `fresh`/`evaluable`.

### Downstream consumers
- Android Five-Layer parser remains compatible with additive 1.1.0 fields and candle/coverage parsing.
- Explicitly test and document whether Android consumes/displays `timestampValid`, `fresh`, and `evaluable`; it must not be treated as the authoritative strategy-readiness gate if it ignores them.
- Core dashboard 96-bar response shape remains parseable through the gateway.
- Neither UI may represent a structurally parsed payload as strategy-ready unless it checks the required quality verdict.

## 5. Implementation sequence after scope review

1. Pin the exact source HEAD and verify the active branch has not moved; do not overwrite uncommitted or later work.
2. Inspect repository test conventions and commands before editing.
3. Add focused RED tests first; record the failing exact-SHA test evidence.
4. Implement the smallest page-aware client change and Core Bundle normalization change.
5. Run focused tests, then the repository-approved isolated synthetic test suite.
6. Run static/code review of the changed call paths and downstream parsing behavior.
7. Record exact source SHA, workflow/run/job, artifacts and checksums where available; distinguish PASS, BLOCKED and NOT VERIFIED.
8. Commit evidence and handoff updates to the existing approved branch. Do not create a parallel branch or PR without separate reason/approval.

## 6. Acceptance criteria

- Exact 1.1.0 contract acceptance and fail-closed invalid-envelope behavior.
- Correct page-aware validation: historical pages need valid timestamps and complete coverage; final assembled window must satisfy freshness/evaluability at the correct anchor.
- No weakened T0 server semantics and no hidden fallback to contract 1.0.0.
- Core Bundle, Core Runtime M15/H1 and Common API gateway tests pass.
- Android/dashboard response-shape behavior is covered and quality-consumption limitations are explicit.
- Focused and approved aggregate tests pass at an exact recorded SHA.
- Independent review finds no contract downgrade, stale-page acceptance, clock-anchor mismatch or accidental runtime activation.

## 7. Explicit exclusions / gates

Not authorized by this scope:
- Any live T0 HTTP endpoint probe or connection.
- Starting, stopping or configuring T0/T1/T2 services; VPS, systemd, autostart or deployment.
- Canonical SQLite/database/data access or mutation.
- Exchange connectivity, credentials or API key use.
- AI execution enablement, Strategy Core behavior changes, order routing, paper/live order submission or trading.
- T1 Orderbook HTTP Provider integration.
- Migration of the older T0 source branch or unrelated Telegram/Chart-Pro/legacy consumers.
- PostgreSQL/TimescaleDB, data retention/deletion, backup/restore or storage changes.

A separate owner approval is required after source-level GREEN and review before any read-only endpoint probe or runtime connection.

## 8. Initial status

| Work item | Status |
|---|---|
| Static external consumer inventory | PASS (see compatibility audit) |
| Active Core First 1.1.0 compatibility | BLOCKED |
| TDD migration scope preparation | APPROVED |
| Source implementation | NOT STARTED / NOT AUTHORIZED BY THIS SCOPE |
| RED/GREEN tests and CI | NOT RUN |
| Endpoint/runtime compatibility | NOT VERIFIED; connection prohibited |
| Production readiness | NOT CERTIFIED |

Next step: review this bounded scope against the active Core First branch and then request/record separate implementation authorization if required.