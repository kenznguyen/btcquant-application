# T0 Migration Provenance

- Target: https://github.com/kenznguyen/btcquant-application (PUBLIC; owner explicitly confirmed keep-public on 2026-11-19).
- Source: https://github.com/kenznguyen/btcusdt-telegram-signals2
- Source branch: `feature/t0-centralized-data-feeder-p1-20261101`
- Source docs/evidence HEAD: `8623d1076d6b821091ff9da0d84033f48fd8ba7a`
- Audited code baseline HEAD: `eb91528bab2b994f283dbe34cd7b0bcbfe406cb5`
- Migration method: selected-file snapshot; no legacy Git history imported.
- Scope: T0 feeder, storage, SQLite candle contract, read-only API, sync/write-gateway modules; selected focused contract tests; current handoff and two T0 evidence reports.
- Workflows: NOT COPIED and NOT DISPATCHED. The nine source workflows include connectivity, systemd and disposable-environment actions.
- Canonical SQLite/data payload and Actions artifacts: NOT COPIED.
- Tests/workflows: NOT RUN during migration.
- Current runtime: NOT VERIFIED. Former VPS deleted 2026-11-11.
- Source audit disposition: T0 PARTIAL / NOT VERIFIED; latest exact-HEAD CI NOT VERIFIED; runtime NOT VERIFIED; canonical OOS data BLOCKED; production NOT CERTIFIED.

## Per-file provenance

| Target path | Source blob SHA-1 | Target blob SHA-1 |
|---|---|---|
| `market_data/feeder.py` | `299a9b5a8b1ebd581eb620d5ee860d9f9ff5dc5c` | `299a9b5a8b1ebd581eb620d5ee860d9f9ff5dc5c` |
| `market_data/store.py` | `4e1b0c54bd56455abe5be0e5c7d0807e63e0bc78` | `4e1b0c54bd56455abe5be0e5c7d0807e63e0bc78` |
| `market_data/storage.py` | `13fe1ae01ebb5318b69e69eef3e512d207f74c49` | `13fe1ae01ebb5318b69e69eef3e512d207f74c49` |
| `market_data/postgres.py` | `2fe27fe2d066dda0c192a381b72d27404487b800` | `2fe27fe2d066dda0c192a381b72d27404487b800` |
| `market_data/api.py` | `81733c9b6de811cbebb2f5d472d41f37f337990c` | `81733c9b6de811cbebb2f5d472d41f37f337990c` |
| `market_data/sync.py` | `e7ad4e6f2074225957b01f74abb0befe37675ea2` | `e7ad4e6f2074225957b01f74abb0befe37675ea2` |
| `market_data/write_gateway.py` | `b2029d9db15fe39dcbe575acfeb6df1b16e16acd` | `b2029d9db15fe39dcbe575acfeb6df1b16e16acd` |
| `market_data/feeder_service.py` | `6d238a01f35003b943e2b22c8e05f05090ccb518` | `6d238a01f35003b943e2b22c8e05f05090ccb518` |
| `market_data/migrations.py` | `b4574f2a867b0dae7818cd39249cfd95fe0ce1f0` | `b4574f2a867b0dae7818cd39249cfd95fe0ce1f0` |
| `market_data/test_feeder_recovery.py` | `034c9e8f157b0750aaf856c122b00ef96c808ee8` | `034c9e8f157b0750aaf856c122b00ef96c808ee8` |
| `market_data/test_feeder_lease.py` | `9e3cef256ed55c9784d02e21f9ac30cf723c31b0` | `9e3cef256ed55c9784d02e21f9ac30cf723c31b0` |
| `market_data/test_write_gateway.py` | `131880b9110f5bb5780b411d348eae19acb6e14e` | `131880b9110f5bb5780b411d348eae19acb6e14e` |
| `market_data/test_storage.py` | `b2635f575323187f936360d033b4fc630d8138e0` | `b2635f575323187f936360d033b4fc630d8138e0` |
| `docs/evidence/T0_PROGRESS_AUDIT_2026-11-19.md` | `17cf8fa83e6a947affe4ed7ee9acb6b00a86e169` | `17cf8fa83e6a947affe4ed7ee9acb6b00a86e169` |
| `docs/evidence/T0_FEEDER_RUNTIME_VERIFICATION_20261109.md` | `ef632a53490e85d709026651c0af9a22d28883fb` | `ef632a53490e85d709026651c0af9a22d28883fb` |
| `docs/PROJECT_SESSION_HANDOFF.md` | `61f9eb2774307198f5449524400641e79d5d3c7c` | `61f9eb2774307198f5449524400641e79d5d3c7c` |

## Explicit omissions and limits

- Source repository was not modified.
- No legacy Git history was imported; this manifest retains source branch, commit and per-file blob provenance.
- No credentials, secrets, environment files, VPS state, canonical SQLite database, market-data payload, workflow artifacts or deployment configuration copied.
- PostgreSQL migration SQL assets and dependency lock/requirements files are not included; PostgreSQL runtime setup is incomplete in this snapshot.
- This snapshot does not establish completeness, execution, test success, deployment or production readiness.
- T0 remains an independent data foundation. Do not connect T1/T2 or enable paper/live execution based solely on this snapshot.
