# T2 M2.1 Read-only Scope Reconciliation — 2026-11-21

## 1. Owner authorization and scope

- Owner approved reopening T2 migration on 2026-11-21 with a **code-only** boundary.
- This record covers an initial read-only reconciliation of the selected source/target snapshots and the first-pass dependency/boundary review for M2.1.
- No source code was copied or modified. No tests or workflows were run. No database, T0 archive, VPS, runtime, exchange credential, paper execution, or order path was accessed.
- The existing staged migration plan remains controlling: complete the read-only dependency closure and per-file manifest before source edits. Runtime activation and execution are outside this approval.

## 2. Exact repository snapshots

| Role | Repository | Branch/ref | Exact commit |
|---|---|---|---|
| Target | `kenznguyen/btcquant-application` | `main` | `328436b8462ec23c783af6cea339f070fdba8404` |
| Source reference | `kenznguyen/btcusdt-telegram-signals2` | `feature/core-operational-proof-20261112` | `e6606e28a696374f31cd6db1ec0a1372d942d64d` |

The target commit is the latest commit observed during this review. The source branch is pinned to the exact branch snapshot used by the prior migration inventory; the source repository's newer `main` commit `d362fcf4984b7813f86914245cbef82f5e5861da` is not a substitute for that branch.

The existing migration manifest `docs/plans/T2_SELECTED_MIGRATION_MANIFEST_2026-11-20.md` has blob SHA `033cfa24c678c8539f809da304c5688d36217161`. It records an older target inventory HEAD `37a41a3178ee76a052d57c77f8f0b9f21218eaaf`; therefore its target-side blob comparisons are stale and must be refreshed before copying.

## 3. First-pass M2.1 file findings

| Source path | Source blob SHA | First-pass disposition | Dependency/boundary finding |
|---|---|---|---|
| `core_runtime/adapter.py` | `9795c346d2eec4c78c22035c32f463af6b40b8f4` | M2.1 candidate | Pure producer-report translation; imports Python standard library only. No I/O, risk admission, ledger mutation or order execution. |
| `core_runtime/input_bundle.py` | `19fb3065da1e7d40c8b4376fe3b51e11c8cc8f87` | Candidate, dependency gate | Pure bundle validation, but imports third-party `rfc8785` and the T1 order-book contract. Requires an isolated, version/hash-pinned T2 dependency decision and T1 contract compatibility review. |
| `core_runtime/bundle_inputs.py` | `f78ebde30413a3329063a2c68c457fe862a50c5e` | Candidate, dependency/contract gate | Normalizes T0 candles and T1 book snapshots; imports `rfc8785` and other Core Runtime modules. Its current T0 envelope assumptions must be checked against the target contract before migration. |
| `core_runtime/orderbook_contract.py` | `1620c9f21b1f3df3c2fb65833f2afd80374bf6a5` | Separate T1 boundary review | Pure validator with standard-library imports, but it defines the T1→T2 consumer contract. Do not treat purity as permission to freeze or activate the T1 provider. |
| `core_runtime/preflight.py` | `3e179b75c09f1a0e1dc3bd8c595cda5afc9bc86f` | Defer to F4 adaptation | Reads the Paper ledger and uses source-specific `ledger_path_guard`; cannot be copied unchanged into the target. |
| `core_runtime/paper_ledger_preflight.py` | `e5d4b26bc1a48a765d16a8cd6708dfdc83b12a88` | Defer to F4 adaptation | Reads target-sensitive ledger state through source imports and source path guard. Must be adapted to the target PAPER_DB resolver and current typed account-risk boundary. |

Target-side path authority already exists at `paper_execution/database_paths.py` through `resolve_paper_db_path()`; the source `ledger_path_guard.py` must not become a second independent path authority. Target Shared Risk Engine and AccountRiskSnapshot contracts are newer than the source Core Runtime's dictionary-based risk assumptions; caller adaptation must use the target contracts rather than copy source risk handling.

## 4. Blocking reconciliation findings

### 4.1 Core leverage semantics conflict

- Target `risk_policy.py` blob `91b46513041033cbcd7e939ed081b71714c82ff3` defines `CORE_LEVERAGE = 13`.
- Source `risk_policy.py` blob `823d04748105b2996a28f2b09e3ce77bea073dce` defines `CORE_LEVERAGE = 1` and a separate `CORE_ROE_SIGNAL_MULTIPLIER = 13`.
- Source `pipeline/core_strategy.py` blob `0be512d99b4302077ab79879184b74949f0feaaa` uses the separate ROE signal multiplier; target `pipeline/core_strategy.py` blob `c14e76f2cecb9f8aca54db263ded1ff17881cb24` uses the leverage value directly.
- The current owner direction does not authorize restoring a fixed 13x Strategy Core leverage. Do not copy either conflicting risk-policy implementation or overwrite the target Core strategy until the intended signal-threshold and sizing semantics are represented in an approved contract and regression tests.

### 4.2 Risk and execution boundary

- Target Shared Risk Engine is the common admission authority; Core and AI must not create parallel risk gates.
- Target account-risk source/provider and production caller wiring remain separately gated. Source preflight and one-shot code cannot bypass these target-side requirements.
- Core/AI ledgers remain separate. AI execution remains disabled; this migration approval does not authorize AI ledger admission, paper order submission, live trading, or any runtime execution.

### 4.3 T0/T1 boundary

- Do not copy or modify `market_data/` or T0-owned data/storage.
- T0 Candle HTTP client and bundle envelope must be checked against the current target T0 API contract and its explicit version gates. No SQLite fallback, synthetic fallback, venue fallback, REST-tail retry, or T0 runtime connection is allowed.
- T1 provider/runtime connection remains outside this code-only migration increment. T1 snapshot fixtures may be used only as deterministic offline test inputs after their consumer contract is reviewed.

### 4.4 Dependency boundary

- `rfc8785` is a direct dependency of the candidate bundle validators.
- Do not add it to the T0 dependency lock or a global dependency set. Any use requires a dedicated T2 lock with exact compatible versions and hashes, plus an isolated offline installation/test gate.
- No dependency was installed or changed in this review.

## 5. Current status

| Work item | Status |
|---|---|
| Owner approval to reopen code-only T2 migration | **APPROVED** |
| Target/source snapshot pinning | **PASS — INITIAL SNAPSHOTS PINNED** |
| Existing migration manifest freshness | **BLOCKED — TARGET BASELINE STALE** |
| M2.1 dependency closure | **PARTIAL — FIRST-PASS REVIEW ONLY** |
| Per-file migration manifest | **NOT COMPLETE** |
| Leverage semantics reconciliation | **BLOCKED — OWNER CONTRACT REQUIRED** |
| Source code copy / implementation | **NOT STARTED** |
| Tests / workflows / artifacts | **NOT RUN** |
| T0/T1/T2 runtime connection or execution | **NOT AUTHORIZED** |

## 6. Next bounded step

1. Refresh the source/target tree and blob comparison against the exact pinned refs above.
2. Complete import closure and test inventory for the M2.1 candidate files; record all internal modules, third-party dependencies and target-side equivalents.
3. Reconcile Core signal-threshold semantics separately from leverage/sizing; preserve the 1% order-margin cap and the target Shared Risk Engine.
4. Submit the refreshed per-file manifest and adapter boundary for review before any source-code copy.

No archive retrieval, database creation/migration, T0/T1 provider activation, runtime startup, deployment, paper order submission, exchange credential use or live trading is included.
