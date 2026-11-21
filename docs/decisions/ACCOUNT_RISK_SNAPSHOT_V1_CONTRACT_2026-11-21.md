# AccountRiskSnapshot V1 — contract and Provider boundary

Date: 2026-11-21
Status: **APPROVED DESIGN / CONTRACT IMPLEMENTATION SCOPE**
Repository: `kenznguyen/btcquant-application`, branch `main`

## Decision

Introduce an immutable, versioned, account-scoped `AccountRiskSnapshot` contract and a narrow Provider port. The Provider is responsible for producing one internally consistent, provenance-verifiable snapshot. `SharedRiskEngine` will consume this contract; it must not query a database, legacy PaperLedger, or market-data storage directly.

This decision does **not** select an authoritative equity/exposure source. The legacy repository's paper accounting implementation is reference material only; it is not adopted as the source of truth and does not represent exchange account equity.

## V1 contract

The snapshot carries:

- Contract schema version and unique snapshot identity.
- Account scope, session ID, and fencing generation.
- Provider generation time and source data `as_of` time.
- Quote asset and exact decimal strings for account equity, gross exposure, reserved margin, drawdown amount, and daily loss amount.
- Provenance: provider ID, source ID, source snapshot ID, source version, and SHA-256 of the exact source payload.
- Explicit verification and ledger-reconciliation outcomes.

All monetary values use canonical non-negative decimal strings; account equity must be strictly positive. Binary floats, NaN, Infinity, exponent notation, booleans in integer fields, malformed hashes, unsupported schema versions, and invalid time ordering are rejected.

`gross_exposure_quote` is gross absolute exposure (LONG and SHORT are not netted). `reserved_margin_quote` is separate from gross notional exposure. `drawdown_quote` and `daily_loss_quote` are non-negative loss magnitudes; zero means no loss at the snapshot time.

## Provider boundary

The Provider port accepts the exact `account_scope_id`, `session_id`, and `fencing_generation` requested by the caller and returns one `AccountRiskSnapshot`. It must not silently substitute another account, stale snapshot, data source, or partial result. Provider failure, unverified provenance, unreconciled ledgers, mismatched binding, or stale data must deny new ENTRY/ADD/DCA admission. Freshness limits remain policy-configured and are not hardcoded into this contract.

The Provider must obtain its values from a single consistent account-level read/snapshot and prove the relationship between source payload hash, source snapshot identity, and the values returned. The contract validates declared provenance; it cannot independently prove a Provider's claims.

## Separation of responsibilities

- Provider: source acquisition, consistent read, source provenance, reconciliation, snapshot identity.
- Contract: immutable typed values and structural validation only.
- Shared Risk Engine: freshness and policy evaluation, Kill Switch/session gates, exposure/drawdown/daily-loss/margin limits, and fail-closed admission.
- Strategy ledgers: remain separate for Core and AI. The snapshot is shared account-level evidence, not a merged strategy ledger.

## Implemented Shared Risk Engine integration — 2026-11-21

Status: **CONTRACT + PURE ADMISSION INTEGRATION IMPLEMENTED / CI PASS**.

- `persistent_state/risk_policy.py` defines immutable `VersionedRiskPolicy`. It has no production defaults: version, quote asset, maximum snapshot age, maximum drawdown, maximum daily loss, and maximum gross exposure must all be explicitly supplied. Limits are exact non-negative decimal strings; age is an explicit positive integer.
- `RiskAdmissionContext` now carries the exact account scope, session ID, fencing generation, `AccountRiskSnapshot`, versioned policy and evaluation timestamp. The previous independent `account_equity_quote` and `ledger_reconciled` inputs are removed.
- `RiskProposal` carries incremental gross exposure in quote units for ENTRY/ADD/DCA. This is intentionally distinct from requested margin; no leverage conversion is guessed by the engine.
- `SharedRiskEngine` requires a typed, verified, reconciled snapshot bound to the exact account/session/fencing generation; checks source as-of freshness and future timestamps; requires quote-asset and policy-version agreement; and cross-checks snapshot reserved margin against the current persistent risk state.
- For ENTRY/ADD/DCA, the engine enforces configured drawdown and daily-loss caps, current gross exposure plus requested incremental gross exposure against the configured gross-exposure cap, existing reserved-margin capacity, and the already-approved 1% per-order margin budget.
- REDUCE/EXIT still pass through session, Kill Switch, snapshot, binding, provenance, freshness, policy-version and reconciliation gates, but are not blocked by new-exposure caps and do not require positive new margin/exposure.
- Missing snapshot/policy, mismatched policy version, stale/future evidence, missing incremental exposure for new exposure, invalid exact decimals, or unreconciled reserved margin all fail closed.
- No threshold values for drawdown, daily loss or gross exposure were selected. A trusted policy configuration source remains unimplemented; callers must supply a complete policy object. The AccountRiskSnapshot Provider and authoritative equity/exposure source remain unimplemented.

### Verification

- TDD RED: workflow run [44858985565](https://github.com/kenznguyen/btcquant-application/actions/runs/44858985565), source SHA `0577e2204d9a668e34a5ef97e807033224b79505`, failed as expected because `persistent_state.risk_policy` did not yet exist.
- Final CI: workflow run [44859221549](https://github.com/kenznguyen/btcquant-application/actions/runs/44859221549), exact tested source SHA `7d2f96f0c924f251f9764399b50af61ffeb28e17`, job `136708505455`, **SUCCESS**.
- Persistent State contract suite: **175 tests PASS**. Adjacent paper ledger / strategy API regressions: **160 tests PASS**.
- Artifact `persistent-state-contract-test-evidence`: ID `14689466051`, SHA-256 `c26c944f6fe47c42c3b7456d14c7c4835293bb6bb7e92efcc9434e10759d518d`, expires 2026-12-05.
- CI tests are isolated; no canonical T0 DB, T0/T1 runtime, VPS, exchange credentials, or trading execution was accessed.

### Remaining gates

- B2 remains **BLOCKED** until an authoritative account-level equity/exposure source and a trusted, versioned policy configuration source are independently identified and verified.
- The pure SharedRiskEngine integration is implemented and tested; production Provider wiring, caller wiring, runtime integration, and end-to-end admission remain **NOT VERIFIED**.
- No paper/live runtime or automatic execution is authorized by this implementation.

## Explicit exclusions

No database/source selection, legacy PaperLedger adoption, T0 access/reconstruction, Feeder/VPS action, T1/T2 runtime connection, account API credentials, paper/live runtime, automatic execution, or real orders. No risk-policy thresholds are invented in this contract increment.

## Next gates

1. Implement and test the pure V1 contract and Provider protocol.
2. Select and independently verify an authoritative account-level source.
3. Integrate the snapshot into SharedRiskEngine with versioned policy thresholds and deterministic freshness tests.
4. Close B2 only after source, policy, and risk admission tests pass and independent review is recorded.
