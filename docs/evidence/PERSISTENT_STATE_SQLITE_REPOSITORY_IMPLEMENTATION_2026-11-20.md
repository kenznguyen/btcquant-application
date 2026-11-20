# Persistent State SQLite repository — implementation evidence — 2026-11-20

## Status

**PASS — isolated SQLite repository boundary and atomic transition semantics implemented and CI verified.**

This milestone is limited to a manually invoked repository API. It is not wired into the application runtime and does not select or create a production database path.

## Source identity

- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Exact tested source SHA: `f3973c4c269316a9fe486ed1776cc0f10e428082`
- `persistent_state/repository.py` blob: `fb919209714be8cf3a75368eeb7f33466e3c2f5b`
- `persistent_state/test_repository.py` blob: `e889b8429ecd524a6d39afeffc59f0040d4fa14f`
- Workflow blob: `5e333fbcc216e037cbd939d7e19f1fe707405775`

## Implemented

- Explicit filesystem path is mandatory; no default path and no import/constructor I/O.
- Database creation occurs only after an explicit `initialize()` call. Parent directory must already exist.
- SQLite `user_version=1`; unknown/newer schema, incomplete v1 schema and unversioned non-empty databases fail closed. No automatic migration or adoption.
- Append-only `ps_events` and `ps_idempotency_claims`; aggregate state is versioned separately.
- `BEGIN IMMEDIATE` transaction atomically appends the event, claims the idempotency key, applies the aggregate mutation and advances aggregate version.
- Event sequence is contiguous per account scope; aggregate versions use compare-and-swap semantics.
- Same idempotency key + same payload hash returns the original result without another mutation. Same key + different payload hash raises conflict.
- Core/AI strategy ownership and account scope are checked across event, claim and aggregate mutation.
- Read APIs do not initialize or create a missing database.
- Repository interface is a protocol; SQLite implementation has no T0, market-data, network or exchange dependency.

## TDD and CI evidence

- RED test-first commit: `fbe226ab9e6cd8e323e87d13704cd66800845c42` (repository tests added before implementation).
- RED workflow run: [44715319436](https://github.com/kenznguyen/btcquant-application/actions/runs/44715319436), conclusion **FAILURE as expected** because `persistent_state.repository` did not yet exist; adjacent regression step was skipped after the focused RED failure.
- Initial implementation run: [44715544146](https://github.com/kenznguyen/btcquant-application/actions/runs/44715544146), exact SHA `de675960a8720edb656e3c53e792da7e3424f185`, conclusion **SUCCESS**; 47 focused tests and 160 adjacent regression tests PASS.
- Final run after public-contract validation cleanup: [44715599693](https://github.com/kenznguyen/btcquant-application/actions/runs/44715599693), exact SHA `f3973c4c269316a9fe486ed1776cc0f10e428082`, conclusion **SUCCESS**.
  - Job `136218055853`: **PASS**.
  - Contract + repository tests: **47 tests PASS**.
  - Adjacent paper-ledger/strategy API regression: **160 tests PASS**.
- Artifact: `persistent-state-contract-test-evidence`, ID `14618583925`, SHA-256 `09823d5a2917d0bf731bafe2fe3b9899e4cd060c1874b7d878e40d319d8c7f60`, expires 2026-12-04.

## Isolation and limits

- All repository tests use `TemporaryDirectory` and disposable SQLite files under test-owned temporary paths.
- No production path or Windows known folder was selected, created, probed or opened.
- No T0 Canonical database, T0 feeder, market-data provider, Binance, T1/T2, VPS, staging, credentials or exchange was accessed.
- No app runtime, session runner, scheduler, autostart, service or trading integration was added.
- No retention deletion, compaction, checkpoint persistence, event replay, fencing or recovery behavior is claimed by this milestone.

## Next bounded step

Implement deterministic event replay and checkpoint validation/publication against temporary test databases, preserving event history as authoritative. Then implement fencing/session recovery harnesses, fixture-only market-data preflight and fail-closed risk admission tests. Production database path, migration, deployment and runtime remain outside this milestone.
