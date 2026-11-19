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



## SQLite API/Storage isolated gate — 2026-11-19

- Approved dedicated workflow: `.github/workflows/t0-sqlite-api-storage.yml`.
- Implementation commit / exact checked-out SHA: `dc7190e392de1b0bb940ba4acf9a1df0f44eb130`; workflow blob `48f06ecc27bba90fcd4d6d05ff7ed3158a0b7014`.
- Path-filtered push to `main` plus `workflow_dispatch`; exact checkout uses `${{ github.sha }}` and asserts `HEAD == GITHUB_SHA`.
- Explicit SQLite-only allowlist: 12 API test methods + 4 Storage test methods = 16. Excludes the API PostgreSQL-no-DSN method, all 3 PostgreSQL-specific Storage methods, and feeder lifecycle tests.
- Isolated exact-SHA run: [44496561587](https://github.com/kenznguyen/btcquant-application/actions/runs/44496561587), job `135465125699`, SUCCESS; `Ran 16 tests in 0.025s`; OK.
- Artifact `t0-sqlite-api-storage-evidence`, ID `14514253952`, SHA-256 `bd75b0a6053b4ea4a1558f85947cf28ba2b10667eb51fa64d710d9eed4a49870`, expires `2026-12-03T09:27:39Z`.
- Docker uses immutable Python 3.12.16 image, `--network none`, read-only source, non-root, no credentials, no canonical DB mount.
- Evidence report: `docs/evidence/T0_SQLITE_API_STORAGE_ISOLATED_GATE_2026-11-19.md`, commit `9879c8671342e948f7bd0317451c28fc283c0a40` (subsequently corrected with exact workflow blob metadata).
- Status: isolated SQLite API 12/12 PASS; SQLite Storage 4/4 PASS; combined 16/16 PASS. PostgreSQL, lifecycle, runtime, canonical data/recovery and production readiness remain NOT TESTED / OUT OF SCOPE / NOT CERTIFIED.


## SQLite feeder/sync/recovery regression and scoped dependency manifest — 2026-11-19

This addendum records a verified isolated CI run on the selected target repository. It does not change the historical source snapshot or imply full T0/runtime parity.

- Target repo/branch: `kenznguyen/btcquant-application` / `main`.
- Workflow: `.github/workflows/t0-sqlite-feeder-sync-recovery.yml`; workflow blob `71d7c0564918f1da2f31dd5853442fc6352d7444`.
- Exact-SHA workflow commit/checkout: `78e67b7bec139452d2cf6e6a6976dfcc96f69a1a`.
- Run [44500564066](https://github.com/kenznguyen/btcquant-application/actions/runs/44500564066), job `135478919064`: SUCCESS. Job checked out exactly the workflow commit SHA.
- Test command: `python -m unittest -v market_data.test_sync market_data.test_feeder_lease market_data.test_feeder_recovery`; actual output `Ran 31 tests in 0.458s`, `OK`, exit code 0. Breakdown: sync 11/11, lease/fencing 10/10, recovery planner/coordinator 10/10.
- Artifact `t0-sqlite-feeder-sync-recovery-evidence`, ID `14516972397`, 1,994 bytes; SHA-256 `b5e8f4ac1e5b2084d288daf8e167d47df2b6ca55255457b34ea080d4ae8a43a5`. Downloaded ZIP independently hashed to the same value and all three payload files inspected.
- Isolation: Python 3.12.16 immutable image digest `935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`; Docker `--network none`, read-only source, non-root, no credentials, no canonical DB mount. PostgreSQL and feeder service runtime excluded.
- Added `requirements-market-data.txt`, commit `78299c2357f5ef4d9bb27766a1c99646fed04efa`, blob `107b1bad04982506a8023cd784d5d0dafae3e41a`. It declares `ccxt==4.5.92` for Binance USD-M collection and `gunicorn==23.0.0` for WSGI serving. These direct pins are a starting baseline based on the previously recorded T0 environment, not a fresh-install compatibility claim.
- The isolated 31-test suite uses Python standard library only; it does not require either package. Flask is not included because the API is a direct WSGI application. `psycopg` and all PostgreSQL migration/runtime assets remain excluded pending separate approval.
- Evidence report: `docs/evidence/T0_FEEDER_SYNC_RECOVERY_AND_DEPENDENCIES_2026-11-19.md`, commit `59a442294657809957e2df02a8eba53480cdbb70`.
- Status: exact-SHA workflow PASS; selected SQLite regression PASS 31/31; artifact/digest/payload PASS; manifest content/blob readback PASS. Dependency resolver, installation, transitive lock, fresh-environment compatibility, runtime startup and minimum supported runtime Python remain NOT VERIFIED. PostgreSQL/TimescaleDB, canonical DB/recovery, feeder service runtime, VPS/deployment, T1/T2, trading and production readiness remain NOT TESTED / OUT OF SCOPE / NOT CERTIFIED.
- No source repository, T0 production source/tests, canonical data/database, PostgreSQL assets, runtime, VPS, T1/T2 or trading behavior changed/accessed. No package installation occurred.


## Deterministic feeder lifecycle contract test parity — 2026-11-19

This addendum preserves the source feeder/service lifecycle contracts without overwriting the target repository's existing lifecycle test module.

- Source repository/branch: `kenznguyen/btcusdt-telegram-signals2` / `feature/t0-centralized-data-feeder-p1-20261101`.
- Exact source HEAD inspected: `c0f48b8910655fdb40d14214ad048b1d3cfa7fe9`.
- Source `market_data/test_feeder_lifecycle.py` blob: `5797d51e3165721863ceacb1fac76f44055f18a7` (34 test methods).
- Existing target `market_data/test_feeder_lifecycle.py` remains unchanged at blob `f10de15b11ca00f6a4946c3877062cfb5dbd1442` (28 different test methods).
- New target path: `market_data/test_feeder_service_lifecycle.py`; final blob `590c29a0fbf553d19582912a113a92bb74da083f`. It preserves all 34 source test methods and adds a fixture helper to provision the exact F1 `feeder_leases` schema in disposable test DBs. This is test-only adaptation; production behavior is unchanged.
- Production `market_data/feeder.py` source/target blob: `299a9b5a8b1ebd581eb620d5ee860d9f9ff5dc5c` (byte-identical).
- Production `market_data/feeder_service.py` source/target blob: `6d238a01f35003b943e2b22c8e05f05090ccb518` (byte-identical).
- Dedicated workflow `.github/workflows/t0-feeder-lifecycle-unit.yml`: commit `6e921720d5e97727033516c386bce213e6930cf8`, blob `4f4b3e9a08caeaa3ee5b0ef1006697a19477d89c`. It runs the 28 existing target lifecycle tests plus 34 preserved source lifecycle/service contract tests (62 total) on exact `github.sha`.
- Authoritative run [44506249466](https://github.com/kenznguyen/btcquant-application/actions/runs/44506249466), job `135498576940`, exact checkout `9938b01b2b14b651dc7b65f70bef5a446d28594a`: SUCCESS, 62/62, 0 failures/errors.
- Artifact `t0-feeder-lifecycle-evidence`, ID `14519797216`, size 2,755 bytes, SHA-256 `80c29fbca88ade5ffc2cbb650f8fdbb64f03a689461a6ee223aacec073ed1cef`; downloaded ZIP independently hashed and payload inspected.
- Test container used immutable Python 3.12.16 image, Docker `--network none`, read-only source/root, non-root, no credentials and no canonical DB mount. Temporary SQLite databases and fake/synthetic exchange collaborators only; no systemd manager, production service, real exchange or network was invoked.
- Initial fixture attempts exposed six then one missing-F1-schema setup errors. The test-only fixture helper was corrected; the authoritative run passed. No production source was modified.
- Evidence report: `docs/evidence/T0_FEEDER_LIFECYCLE_CONTRACTS_2026-11-19.md`, commit `f8b10455018f248cc97019e00be28466683e7f80`.
- Status: deterministic lifecycle/scheduler/retry and feeder-service composition contracts PASS 62/62. Production feeder startup, systemd service operation, canonical DB/data, VPS/runtime, Binance connectivity, PostgreSQL and production readiness remain NOT VERIFIED / NOT AUTHORIZED.


## SQLite foundation expansion — 2026-11-19

Source repo/branch: `kenznguyen/btcusdt-telegram-signals2` / `feature/t0-centralized-data-feeder-p1-20261101`; exact source HEAD inspected: `c0f48b8910655fdb40d14214ad048b1d3cfa7fe9`.

The following selected SQLite-first T0 files were copied without content changes. Source and target blob SHA-1 values are identical:

| Target path | Source and target blob SHA-1 |
|---|---|
| `market_data/initialize_sqlite.py` | `58bd2deba66cc667bad8d6446c5ff54e7f5dd240` |
| `market_data/test_initialize_sqlite.py` | `9823f42fa1b346c7c5b96786eec7e996484b692d` |
| `market_data/test_store.py` | `df1554a365ff5d619498dc4b07f7a1a435e761df` |
| `market_data/test_fenced_store.py` | `0573d0728f3e62a95b8d2a4f16359e33dd4789b4` |
| `market_data/test_feeder_health.py` | `80e0b7d042c821d4814d626b69c3196853dc49d9` |
| `market_data/test_feeder_retry.py` | `0c556f2954188e2bf3bd643aa217f71b9bd8ba2c` |
| `market_data/test_feeder_scheduler.py` | `695c53548c58763cffecc86626171f6a691e75fd` |
| `market_data/test_controlled_ingestion_acceptance.py` | `92c76fea839858f128ed228ac25b36b6bb8ec375` |
| `market_data/test_t0_controlled_ingestion_acceptance.py` | `a26d9f44012452fa663553e292e273d68d625e88` |

The initializer is intentionally empty-only and refuses existing paths. It was tested only with disposable temporary SQLite paths; no canonical database was created and the initializer CLI was not run against a real data path.

The dedicated aggregate workflow `.github/workflows/t0-sqlite-aggregate.yml` was extended to an explicit 191-test allowlist:
- Workflow update commit / exact checked-out SHA: `42c8172a4b4b0234fa50e64eb6172f970f45ab66`.
- Workflow blob: `32be957fbad1b04161b621c7e1c95f20aa9d9cf9`.
- Run [44507725020](https://github.com/kenznguyen/btcquant-application/actions/runs/44507725020), job `135503600404`: SUCCESS, 191/191, 0 failures/errors.
- Artifact `t0-sqlite-aggregate-evidence`, ID `14520188043`, size 6,093 bytes, SHA-256 `0389c4fc4cab0190ea7ada4115b24b53095a9ffb035cba3f7b1dcd01b22ceacb`; downloaded ZIP and payload independently verified.
- Evidence report: `docs/evidence/T0_SQLITE_FOUNDATION_EXPANSION_2026-11-19.md`, commit `6c2df8129e336231ad0e55b39e844b14663244d5`.

Additional source-only files remain intentionally unported pending separate classification: legacy app health API tests, process/SIGKILL restart tests, T2 end-to-end/parity tests, explicit Binance connectivity probe, PostgreSQL/TimescaleDB assets/tests, Kraken-specific modules, and legacy static RED contract spec. No source repository changes or runtime/production actions occurred.


## T0 navigation documentation adaptation — 2026-11-19

The source T0 technical README and scope index were reviewed and adapted for the new application repository rather than copied verbatim because their original text contained legacy paths, requirements files, TimescaleDB workflow references and topology statements that are not verified/current in the target.

- Source `market_data/README.md` blob: `d90f84f8135c8ab9da1b57863e145d86565bf179`.
- Target `market_data/README.md` blob: `269c861b3c5f88fbd48c8c757a6ae587fa2486aa`.
- Source `docs/T0_ACTIVE_SCOPE_INDEX.md` blob: `70c13603ec4f9d499273f2412c4106fcbc346af2`.
- Target `docs/T0_ACTIVE_SCOPE_INDEX.md` blob: `9d33f36ada44e221b463e1114ed40c719aec699f`.
- Target docs explicitly scope SQLite-first T0, describe the committed CPython 3.12/Linux x86_64 lock and the 191-test exact-SHA gate, and state that canonical data, production runtime, PostgreSQL, external connectivity and production readiness remain unverified or separately gated.
- Target docs preserve the no-destructive-authority boundary: no automatic TTL/deletion-after-use/cleanup/compaction/vacuum/backup expiry without separate approval.
- The README's initializer description warns that its tests used disposable temporary paths only; it does not instruct users to initialize a canonical DB as part of this migration.
- Documentation commits: scope index `ef91391fc6a381981d8c0321dd5d196adadf006b`; README `bcca30363da1ac1de09d8e930bd336cec1b5afcd`.
- This is documentation adaptation, not byte-parity migration. No production source, test, workflow, canonical data or runtime was changed.


## T0 availability and freshness contract update — 2026-11-19

The target's read-only Candle API has an approved, tested target-specific contract update. The historical migration table above remains the original snapshot baseline; the following target blobs supersede the prior API/API-test blobs for current `main`:

- Source `market_data/api.py` blob: `81733c9b6de811cbebb2f5d472d41f37f337990c`; current target blob: `4f923d400b8e133a602cec7239982fdf357e9e21`.
- Source `market_data/test_api.py` blob: `49df7e0bec12908adae67f18a4aa19063e461093`; current target blob: `add00a2a91899d8e496df5b64c122442fc7c65c9`.
- API contract version: `1.1.0`; schema version remains 1. Freshness is anchored to `asOfMs` for point-in-time replay or `generatedAtMs` otherwise; future `asOfMs` is rejected. `evaluable` requires complete coverage, valid timestamps and a fresh latest closed candle.
- Exact final SHA: `8f49439fafc95186a8c854fe482aad707525a658`.
- Aggregate run [44515824622](https://github.com/kenznguyen/btcquant-application/actions/runs/44515824622): SUCCESS 196/196; artifact ID `14525622150`, SHA-256 `7437e8f5877d62f81066208cd031cebea40b4cd0138b7c791b380a824b300cba`.
- Dedicated API/Storage run [44515824664](https://github.com/kenznguyen/btcquant-application/actions/runs/44515824664): SUCCESS 21/21; artifact ID `14525821866`, SHA-256 `19d5d4e718d1310299667e7f11734437b1f23841129ebdc9a4f660cb4bea9468`.
- Detailed contract, RED/GREEN history, consumer review and limitations: [T0 Availability & Freshness Contract Audit](evidence/T0_AVAILABILITY_FRESHNESS_CONTRACT_AUDIT_2026-11-19.md).
- No writer, canonical data, storage schema, sync/recovery, feeder runtime, VPS, T1/T2 or trading behavior changed. External HTTP consumer compatibility and production readiness remain NOT VERIFIED / NOT CERTIFIED.


## External HTTP consumer compatibility audit — 2026-11-19

- Read-only audit report: `docs/evidence/T0_EXTERNAL_HTTP_CONSUMER_COMPATIBILITY_AUDIT_2026-11-19.md`.
- Official target T0 API is contract 1.1.0 at `btcquant-application/main` base HEAD `53e14e57f3b1ede5f3fbe34368621bf42f14fe01`; API blob `4f923d400b8e133a602cec7239982fdf357e9e21`.
- Active Core First source branch `feature/core-operational-proof-20261112` at `e6606e28a696374f31cd6db1ec0a1372d942d64d` still carries T0 API 1.0.0, strict 1.0.0 Candle HTTP client and 1.0.0 Core Bundle normalization.
- Confirmed direct consumers: Core Bundle provider, Common API `market_window`, and FreqAI research context. Android Five-Layer and Core dashboard consume the Common API indirectly.
- Compatibility verdict: **BLOCKED**. Strict version/freshness checks reject 1.1.0; generated-time calculations conflict with as-of anchored freshness; paged requests require every page to be evaluable; Core Bundle normalizer rejects 1.1.0.
- Older T0 branch `feature/t0-centralized-data-feeder-p1-20261101` at `c0f48b8910655fdb40d14214ad048b1d3cfa7fe9` has a separate 1.0.0 client copy.
- Audit was static only: no source, tests, workflows, endpoints, network, database, credentials, runtime, VPS, T0/T1/T2 or trading paths changed or accessed. Tests and workflows were not run.
- Do not connect until a separate TDD migration and exact-SHA CI/review close these compatibility gaps.
