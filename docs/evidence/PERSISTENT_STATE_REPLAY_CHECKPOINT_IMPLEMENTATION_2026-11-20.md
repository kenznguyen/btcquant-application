# Persistent State replay and checkpoint publication — evidence — 2026-11-20

## Status

**PASS — deterministic event replay and immutable checkpoint publication verified against temporary SQLite databases.**

## Exact source

- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Exact tested source SHA: `bb64e0c196d5d1536f9704d9abdc79263b14671c`
- `persistent_state/repository.py` blob: `b14d7f63793991ed28c06c6d1ffb41101a7d80c7`
- `persistent_state/replay.py` blob: `e94e94a2e62943f63641e97911655e043e9a873b`
- `persistent_state/test_replay_checkpoint.py` blob: `b7dead609d4cb0adf9ee79ac977b2c4094e96027`
- `persistent_state/contracts.py` blob: `3222360843292a4d0e34c29d019007d71d6ab335`
- Workflow blob: `5d484d37006ed47b2a81c87844bbdf22be07037e`

## Implemented

- Pure replay from canonical checkpoint state + contiguous committed event tail.
- Replay validates account scope, sequence continuity/order, duplicate event IDs, reducer output shape and canonical state serialization.
- Deterministic repeated replay is covered by tests.
- Checkpoint generations are immutable and append-only; checksum and contract validation are repeated on read.
- Checkpoint publication rejects uncommitted coverage and aggregate-version maps that do not match the committed event prefix.
- Active checkpoint pointer advances only to a newer event boundary; it cannot move backwards or be replaced by a different checkpoint at the same boundary.
- Checkpoint generation insert and active-pointer advancement are one SQLite transaction. Failure injection proves both roll back together.
- No pruning API exists; verified generations are retained.
- Canonical persisted JSON rejects binary floating-point values; accounting values remain exact decimal strings or integer-scaled representations.

## TDD / CI evidence

- Test-first commit: `5a503adda8577cdc6713313441b69b7ed546ee6a`.
- RED workflow run: [44716033557](https://github.com/kenznguyen/btcquant-application/actions/runs/44716033557), failure because the replay module had not yet been implemented.
- Initial implementation run [44716243668](https://github.com/kenznguyen/btcquant-application/actions/runs/44716243668) exposed two test-fixture issues: the corruption test removed a required schema trigger without restoring it, and the replay reducer assumed a state key absent from the checkpoint fixture. Both were corrected; production logic was not weakened.
- Final isolated CI run: [44716717988](https://github.com/kenznguyen/btcquant-application/actions/runs/44716717988), exact source SHA above, **SUCCESS**.
  - Job `136221915283`: **PASS**.
  - Contract + repository + replay/checkpoint suite: **67 tests PASS**.
  - Adjacent paper-ledger/strategy API regressions: **160 tests PASS**.
- Artifact: `persistent-state-contract-test-evidence`, ID `14619991744`, SHA-256 `953606cd4fcf927c0c76f3901b062a816cf152831098fde8d4ff8851fe311df6`, expires 2026-12-04.

## Isolation and limits

- All SQLite operations occurred only in disposable `TemporaryDirectory` test paths.
- No production database path, Windows known folder or Application Data directory was selected, created or opened.
- No T0 Canonical, feeder, Binance, market-data source, T1/T2, VPS, staging, credentials, exchange, runtime or trading access.
- No production migration, backup/restore, checkpoint scheduler, 100-event cadence, session lifecycle, fencing, recovery or risk-admission integration is claimed complete.

## Next bounded step

Implement session ownership/fencing-generation checks and deterministic session crash/restart recovery using only temporary test databases and synthetic fixtures. Keep manual Start/Stop; no scheduler, autostart or runtime activation.
