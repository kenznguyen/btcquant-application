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


## F1 SQLite regression parity addendum — 2026-11-19

The selected-file snapshot above remains the historical migration baseline. This addendum records the separately approved F1 regression parity increment; it does not imply full source parity or T0 completion.

- Source repository/branch: `kenznguyen/btcusdt-telegram-signals2` / `feature/t0-centralized-data-feeder-p1-20261101`.
- Exact source HEAD inspected: `c0f48b8910655fdb40d14214ad048b1d3cfa7fe9`.
- Source `market_data/write_gateway.py` blob: `585caf5250c7382f8e391533882f08c8ec97efaa`.
- Target `market_data/write_gateway.py` blob: `0a77df443ae1a817ea74946fac5dc0f3809ddd83`. These files are byte-different; static comparison and the new malformed-schema regression confirm equivalent F1 schema-rejection behavior. Target production source was retained unchanged.
- Source `market_data/test_write_gateway.py` blob: `2c55dff1729cdfd11bd0ef2188e1e41756ed7692`.
- Target `market_data/test_write_gateway.py` blob after parity increment: `231f5e0184821c78cda0ca5d03625f71fd3a4b71`. Target-specific tests were preserved; two regression tests were added, with the Python `-S` fixture adapted to the target's existing initialization API.
- Target test commit: `f2981271d42b7c3baee8cc4de1c670e8a54cdd85`.
- Dedicated workflow: `.github/workflows/t0-f1-regression-parity.yml`, blob `967e160d7edbf438db9a53a35e6f27c8cfc3f934`, commit `b2bb35400ea1bb4fd0c9a54737ebdab5b6b8a838`.
- Exact-SHA run: [44494341100](https://github.com/kenznguyen/btcquant-application/actions/runs/44494341100), job `135457600070`, checkout SHA `b2bb35400ea1bb4fd0c9a54737ebdab5b6b8a838`, SUCCESS, 14/14 tests.
- Artifact: `t0-f1-regression-parity-evidence`, ID `14513793330`, digest `sha256:c778e6ab5f61de875c9ad585d05459c25fadb79bd344eee22841a55303e08876`.
- Detailed report: `docs/evidence/T0_F1_SQLITE_REGRESSION_PARITY_2026-11-19.md`, report commit `ec0896c6ebd28dff850f8860926ff7f25485daab`.

The pre-existing `.github/workflows/t0-sqlite-api-isolated.yml` also ran due its broad main-push trigger (run `44494340918`). It checked out fixed older source SHA `2668dd538a99d6021921432b3485f4ed84198364`, passed 91 tests, and is recorded only as incidental evidence—not as validation of the current target HEAD or F1 parity. That workflow was not modified.

F1 target status: PASS within the isolated write-gateway regression scope. Full T0/API/storage parity remains PARTIAL / NOT VERIFIED. Runtime, canonical data/recovery, PostgreSQL/TimescaleDB and production readiness remain OUT OF SCOPE / NOT VERIFIED / NOT CERTIFIED.



## Read-only SQLite API/Storage parity inventory — 2026-11-19

This is a read-only parity record, not a new source-to-target copy or a runtime acceptance claim.

- Source repo/branch: `kenznguyen/btcusdt-telegram-signals2` / `feature/t0-centralized-data-feeder-p1-20261101`.
- Source HEAD inspected: `c0f48b8910655fdb40d14214ad048b1d3cfa7fe9`.
- Target repo/branch: `kenznguyen/btcquant-application` / `main`.
- Target HEAD inspected: `c80aa8e31481d237cb8d17ab547d65e7e790976a`.

| Target path | Source blob SHA-1 | Target blob SHA-1 | Result |
|---|---|---|---|
| `market_data/api.py` | `81733c9b6de811cbebb2f5d472d41f37f337990c` | same | byte-identical |
| `market_data/storage.py` | `13fe1ae01ebb5318b69e69eef3e512d207f74c49` | same | byte-identical |
| `market_data/test_api.py` | `49df7e0bec12908adae67f18a4aa19063e461093` | same | byte-identical; 13 test methods |
| `market_data/test_storage.py` | `b2635f575323187f936360d033b4fc630d8138e0` | same | byte-identical; 7 test methods |
| `market_data/store.py` | `4e1b0c54bd56455abe5be0e5c7d0807e63e0bc78` | same | byte-identical |
| `market_data/feeder.py` | `299a9b5a8b1ebd581eb620d5ee860d9f9ff5dc5c` | same | byte-identical |
| `market_data/sync.py` | `e7ad4e6f2074225957b01f74abb0befe37675ea2` | same | byte-identical |
| `market_data/postgres.py` | `2fe27fe2d066dda0c192a381b72d27404487b800` | same | byte-identical; no PG behavior tested |
| `market_data/write_gateway.py` | `585caf5250c7382f8e391533882f08c8ec97efaa` | `0a77df443ae1a817ea74946fac5dc0f3809ddd83` | byte-different |

The API and Storage implementation/test files are byte-identical at the inspected source and target refs. The only byte divergence among the inspected dependency set is the write gateway. Source and target use different implementation shapes for exact `feeder_leases` schema inspection; target F1 behavior was separately covered by the malformed-schema regression and 14-test exact-SHA gate. No production file was changed in this inventory.

Static contract notes and limitations are in `docs/evidence/T0_SQLITE_API_STORAGE_READONLY_PARITY_2026-11-19.md`, created by commit `73376e93e7edf4e5eecb09ba50b2ae696ff10c52`.

Status: direct API, Storage and their test specifications PASS byte-parity; inspected shared dependencies PASS except the documented write-gateway byte divergence. No API/Storage test was run. Runtime behavior, full T0 parity, canonical data/recovery, PostgreSQL runtime, lifecycle and production readiness remain NOT VERIFIED / NOT CERTIFIED.
