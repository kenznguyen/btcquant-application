# Persistent State contracts — implementation evidence — 2026-11-20

## Status

**PASS — contract types and pure validators implemented; isolated CI verified.**

This milestone implements only the typed/versioned contract boundary. It does not implement persistence, database access, session orchestration, recovery, risk admission or runtime integration.

## Source identity

- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Exact source SHA tested: `37d27f5dbfa4956a5ac2bfb51e243da036dbcf1b`
- `persistent_state/contracts.py` blob: `3795e6de3e7b083388e34499d1b31adcc86ac4ff`
- `persistent_state/test_contracts.py` blob: `e7fadae7728a0e90c40e7eee4711c383be7cae38`
- `persistent_state/__init__.py` blob: `74f7350899839f6a44f08c3095f562d697443320`
- `.github/workflows/persistent-state-contracts.yml` blob: `a10edc3908274a18e30ca3e3af80820970f56fd5`

## Implemented contract types

- `SessionRecord` and the versioned manual Start/Stop lifecycle status enum.
- `EventRecord`, including account-level events that are not attributed to Core or AI.
- `StrategyState`, with independent Core/AI namespaces.
- `PositionLedger`, with strategy ownership and exact decimal-string accounting.
- `SmartDCAState`, Core-only with level/count/notional/trigger reconciliation.
- `RiskState`, with durable Kill Switch latch/reason and exact reserved margin.
- `IdempotencyClaim`, with a deterministic SHA-256 key derived from logical intent dimensions and a separately validated payload hash.
- `Checkpoint`, with canonical JSON payloads, version maps and verified SHA-256 payload checksum.

All contracts are immutable dataclasses. Construction performs pure validation: schema version, identifiers, lifecycle invariants, UTC epoch-millisecond integer fields, exact decimal strings (no binary float), canonical JSON objects, hash formats, Core/AI attribution and DCA/Kill Switch/checkpoint invariants. Importing the package does not open files, databases, network connections or exchange interfaces.

## TDD and CI evidence

- RED test commit: `5b94a9a81d212014e42a186396998b44891ac9f0`.
- RED workflow run: [44714082922](https://github.com/kenznguyen/btcquant-application/actions/runs/44714082922), conclusion **FAILURE as expected** because `persistent_state.contracts` did not yet exist (`ModuleNotFoundError`). This confirms the tests preceded the implementation.
- Initial GREEN run: [44714305899](https://github.com/kenznguyen/btcquant-application/actions/runs/44714305899), exact SHA `e47754e324a9e435442b0a57fd52c2ed52d77ed3`, 27 contract tests PASS.
- Expanded contract run: [44714607056](https://github.com/kenznguyen/btcquant-application/actions/runs/44714607056), exact SHA `54fd7ecf2c482511cd28995f2afe624fe8f63043`, 32 contract tests PASS.
- Final isolated CI run: [44714758403](https://github.com/kenznguyen/btcquant-application/actions/runs/44714758403), exact SHA `37d27f5dbfa4956a5ac2bfb51e243da036dbcf1b`, conclusion **SUCCESS**.
  - Job `136215182291`: **PASS**.
  - Contract suite: **32 tests PASS**.
  - Adjacent paper-ledger/strategy API regression suite: **160 tests PASS**.
  - Runtime: Python 3.12 on GitHub Actions; adjacent regression ran in a pinned Python 3.12.16 container with network disabled, read-only workspace, non-root user and bounded resources.
- Evidence artifact: `persistent-state-contract-test-evidence`, ID `14618857418`, SHA-256 `f5ef3d29ccd3b8d3f10f8ac1cd50bb98d71f0e965fd27169f52e7a154d4a1578`, expires 2026-12-04.

## Scope and safety record

- Tests are deterministic and do not connect to market data, T0, Binance, T1/T2, VPS, staging or external services.
- No SQLite database was opened or created by this milestone.
- No production path, Windows known folder, Application Data directory or filesystem location was selected, created or probed.
- No source code outside the new `persistent_state` package and its dedicated workflow was changed.
- No scheduler, autostart, background service, exchange credential, external order or live trading behavior was added.
- Existing paper execution and pipeline regression suites passed; their implementation was not modified.

## Next bounded step

Implement the SQLite repository boundary and atomic event/idempotency/ledger/aggregate-version transaction semantics. All database tests must use explicitly created temporary test directories and disposable test databases. Do not add a default database path, connect to T0, or create/open/migrate/write any real or staging database.

The remainder of the approved contract-first/test-first scope (replay, checkpoint publication, fencing, recovery harness, market-data preflight fixtures and risk-admission interface tests) remains pending.
