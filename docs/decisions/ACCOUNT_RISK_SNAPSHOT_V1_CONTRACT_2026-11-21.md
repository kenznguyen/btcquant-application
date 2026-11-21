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

## Explicit exclusions

No database/source selection, legacy PaperLedger adoption, T0 access/reconstruction, Feeder/VPS action, T1/T2 runtime connection, account API credentials, paper/live runtime, automatic execution, or real orders. No risk-policy thresholds are invented in this contract increment.

## Next gates

1. Implement and test the pure V1 contract and Provider protocol.
2. Select and independently verify an authoritative account-level source.
3. Integrate the snapshot into SharedRiskEngine with versioned policy thresholds and deterministic freshness tests.
4. Close B2 only after source, policy, and risk admission tests pass and independent review is recorded.
