# T2 Selected Migration Manifest — Read-only Inventory

- Date: 2026-11-20
- Target repository: `kenznguyen/btcquant-application`
- Target branch: `main`
- Target inventory HEAD: `37a41a3178ee76a052d57c77f8f0b9f21218eaaf`
- Source repository: `kenznguyen/btcusdt-telegram-signals2`
- Source branch: `feature/core-operational-proof-20261112`
- Source inventory HEAD: `e6606e28a696374f31cd6db1ec0a1372d942d64d`
- Scope: read-only file inventory, blob-identity comparison, migration classification and dependency/architecture blockers.
- This document does **not** authorize source-code copying, source changes, runtime wiring, workflow execution, database access, paper orders or live trading.

## 1. Executive disposition

**Disposition: MANIFEST PREPARED — MIGRATION NOT STARTED — FUNCTIONAL PARITY NOT VERIFIED.**

The target already contains a selected F4 snapshot transfer of 39 files from the source repository at the older source HEAD `5223cef02f0e296c4f58afc5d7992b9c641ab208`. That transfer is documented in `docs/evidence/F4_SNAPSHOT_MIGRATION_2026-11-19.md` (target blob `6c79cce863928d5026a147b2e81ed1a75a5c1d54`). The report verified source/target blob identity at the time of that snapshot, but explicitly did not run tests or certify integration.

The current source branch has advanced to `e6606e28a696374f31cd6db1ec0a1372d942d64d`. Its current blobs differ from target blobs for several overlapping T2 files. Therefore:
- Do not copy the entire source branch.
- Do not merge or cherry-pick the branch history.
- Do not overwrite target files by path or by source-branch precedence.
- Preserve target-only risk-contract/F4 work.
- Resolve conflicting risk semantics before any code migration.

## 2. Exact inventory baseline

| Metric | Source | Target |
|---|---:|---:|
| Git tree entries (including directories) | 1,199 | 199 |
| Blob/file entries | 1122 | 185 |
| Shared file paths | 71 | 71 |
| Shared paths with identical blob SHA | 36 | 36 |
| Shared paths with different blob SHA | 35 | 35 |
| Source-only files | 1051 | — |
| Target-only files | — | 114 |

Both recursive trees reported `truncated=false`.

Source branch comparison against source `main`:
- Status: `diverged`
- Ahead: 4,667 commits
- Behind: 129 commits
- Merge base: `f5b74affb8777953fa66d241784965fbb0e577ba`

This divergence is a hard reason not to import branch history wholesale. The manifest uses exact source and target HEADs above; any later source or target commit invalidates the affected blob comparisons and requires a refreshed inventory.

## 3. Classification rules

| Label | Meaning |
|---|---|
| `KEEP` | Preserve the current target version. No source overwrite. |
| `RECONCILE` | Same path exists on both sides but blob SHA differs; review semantics and tests before deciding. |
| `MIGRATE-CANDIDATE` | Source-only file appears relevant to T2; not yet authorized to copy. |
| `EXCLUDE` | Legacy, T0-owned, T1-owned, deferred integration, or unrelated application component. |
| `NOT VERIFIED` | No exact-target-SHA tests/workflow/runtime evidence has been run for this manifest. |

## 4. RECONCILE — shared T2 paths with different blobs

These 18 paths must be reconciled individually. The target blob is not automatically correct in every case, but it must not be overwritten without an explicit source-level review and regression plan.

| Path | Source blob SHA | Target blob SHA |
|---|---|---|
|  `paper_execution/README.md`  | `448e21c4801f4b2b29340d14346984617cde7cd9` | `814f9f6e185cb38ef9dc7368b39f882307943a44` |
|  `paper_execution/__main__.py`  | `10d1e0fbc9a976c8f8d25bc6d2a8a690421990b9` | `1e6b49d253e46fe747a413d1e829e18002db8a64` |
|  `paper_execution/account_equity.py`  | `701bcc25e8c5850fdb9052fd7481996debb2e019` | `9971dae4592f07fe7bd2315c0f1ec1daf97af8d1` |
|  `paper_execution/funding.py`  | `03122cc7ddd81f284093bfea1daf5dbec5d9b02b` | `575758eb3223b4341ac37bad56d58e52539305c0` |
|  `paper_execution/ledger.py`  | `6ff1dd23295b931aad39f2416e81c1736fdc57d1` | `9cc03db8b7506543f9eef2835eb5cb7cda701d6c` |
|  `paper_execution/risk_control.py`  | `4f525ed937818d70dc428b60d5503b2621e63a2c` | `c8fe573a7a5b0716159e50a678423e402d7df3ba` |
|  `paper_execution/test_daily_baseline_persistence.py`  | `fcbfaac46ad5cb4edbb90446ebf86cba60be0c0b` | `7935111b7bb57e9558e88bef7a03ce425ebfccdb` |
|  `paper_execution/test_dual_ledger_migration_red.py`  | `6ec693cee45b8d2548a25b7f8cf3f24ca2522fa8` | `09320d363c8cb52806280c1de366895e09af3eeb` |
|  `paper_execution/test_dual_ledger_red.py`  | `8b71e8364b7476fb9454f5fd959a8df96a685c7c` | `0cf05418940a07a8357ee9d6039325a1efcb16f2` |
|  `paper_execution/test_dual_strategy_api_red.py`  | `24004438feb3b6a59a6c2ef4838190523b40652a` | `70eb419280717aa04560267e80716920844f8de1` |
|  `paper_execution/test_ledger.py`  | `c7aa7f0fcd97a9d66133c964b73c2e40d7ad02f8` | `71c7719d3e84be41bb7ca200b50fe6b5ee0f68e9` |
|  `paper_execution/test_risk_control.py`  | `d37c761fb1723d59383c97485ffca6a231f9ac8f` | `69c9177a249369f52d0c81e442c9c4583c9f5b77` |
|  `paper_execution/test_risk_limits.py`  | `22645c481eea3f807fc72d659cdd05989f5673c5` | `3dd3afb6e7b7d361829bae0355412c468cbbc313` |
|  `pipeline/CONTRACTS.md`  | `db00331a4d346314e8b059b702c2593fdd172f43` | `14368ea20d56879b9c9fc6c2eddf07e8c44ab5da` |
|  `pipeline/api.py`  | `bb89b0bdf196f64b3ab9d9ac15b6597f333c583e` | `e60e9800e4735902ec46b3fe927d6108cac5b6c2` |
|  `pipeline/core_strategy.py`  | `0be512d99b4302077ab79879184b74949f0feaaa` | `c14e76f2cecb9f8aca54db263ded1ff17881cb24` |
|  `pipeline/test_api.py`  | `706a091b9f93587dce4ad61167dec1202bb1c59d` | `3ddb51d763eb9bef836c5cf85a1ddc471bae0875` |
|  `risk_policy.py`  | `823d04748105b2996a28f2b09e3ce77bea073dce` | `91b46513041033cbcd7e939ed081b71714c82ff3` |

### Blocking semantic conflict: Core leverage

- Source `risk_policy.py` blob `823d04748105b2996a28f2b09e3ce77bea073dce`: `CORE_LEVERAGE=1`, `CORE_ROE_SIGNAL_MULTIPLIER=13`, `ORDER_MARGIN_BUDGET_PCT=0.01`.
- Target `risk_policy.py` blob `91b46513041033cbcd7e939ed081b71714c82ff3`: `CORE_LEVERAGE=13`, `ORDER_MARGIN_BUDGET_PCT=0.01`.
- Source `pipeline/core_strategy.py` blob `0be512d99b4302077ab79879184b74949f0feaaa` imports the multiplier and uses separate Core leverage/ROE scaling.
- Target `pipeline/core_strategy.py` blob `c14e76f2cecb9f8aca54db263ded1ff17881cb24` uses `CORE_LEVERAGE` directly and does not import that multiplier.

The source `AI_STRATEGY_CONTRACT.md` states Core remains pinned to 13x, while the source `CORE_SIZING_LEVERAGE_POLICY_PROPOSAL.md` says 13x is not approved merely because it exists in source and asks for an owner decision. These statements are inconsistent with the current source `risk_policy.py` value of 1x. **BLOCKER:** do not select a leverage implementation until the authoritative Core leverage and ROE-threshold semantics are explicitly resolved.

### Ledger / risk-control reconciliation

- Source `paper_execution/ledger.py` blob `6ff1dd23295b931aad39f2416e81c1736fdc57d1`; target blob `9cc03db8b7506543f9eef2835eb5cb7cda701d6c`. Target imports `paper_execution.risk_contract.load_account_risk_contract`; source uses simulated-equity configuration paths. This is not a safe file replacement.
- Source `paper_execution/risk_control.py` blob `4f525ed937818d70dc428b60d5503b2621e63a2c`; target blob `c8fe573a7a5b0716159e50a678423e402d7df3ba`. Target contains later fail-closed behavior with exact-SHA GREEN evidence in target handoff; preserve target version pending review.
- Source `pipeline/api.py` blob `bb89b0bdf196f64b3ab9d9ac15b6597f333c583e`; target blob `e60e9800e4735902ec46b3fe927d6108cac5b6c2`. Target Core-First guard must remain controlling: AI paper execution disabled.
- Source `paper_execution/README.md`, `__main__.py`, `account_equity.py`, `funding.py` and affected tests also differ; reconcile individually rather than importing source versions.

## 5. KEEP — shared T2 paths with identical blobs

The following 18 paths have identical source/target blob SHA at the inventory HEADs. Keep the target copies; do not transfer duplicates.

| Path | Identical source/target blob SHA |
|---|---|
|  `paper_execution/__init__.py`  | `df25aa85d00c314e64dc60d8f5ae93185a931ceb` |
|  `paper_execution/account_history.py`  | `6163065798b2386e1c466650048e40b7eab0d2eb` |
|  `paper_execution/daily_baseline.py`  | `747808d9a68a70e9c2aa6f71f00aeeffb6682145` |
|  `paper_execution/daily_baseline_v1_recovery.py`  | `b1c7aa54af569428d2a2e04300fc59ff49fa7a74` |
|  `paper_execution/equity.py`  | `40d6566294355c646839614c92f8fba6116b582c` |
|  `paper_execution/replay_inputs.py`  | `e32ec695546086449b35e43d8ae0d51f4dc32c27` |
|  `paper_execution/replay_reconciliation.py`  | `68a59b3938a28055e4d2b27733efcdb643127ea8` |
|  `paper_execution/test_account_cutover_snapshot_v7.py`  | `0759e1cc350b4af92f41e80ae64ce47886ba553d` |
|  `paper_execution/test_account_history_replay_red.py`  | `9aa296ed2bc2c735ef98f28f44f486a58e911331` |
|  `paper_execution/test_daily_baseline_v1_recovery.py`  | `aa7f6339c090e2d826ac4683f5ada0f3a49372e4` |
|  `paper_execution/test_daily_equity_reconciliation.py`  | `94ac12762a715231ee7c9dc3abef30f45d09303b` |
|  `paper_execution/test_equity.py`  | `87eac43ff815903b1b8b7ea70dc3dcaeeb3abe43` |
|  `pipeline/core_signal.py`  | `df5fbb59611bdd4fbb8224665f79655dd4433455` |
|  `pipeline/decision.py`  | `8720d8ab988529b1545a27aa0792beca9e6a84aa` |
|  `pipeline/test_core_signal.py`  | `a946716604e2e1a74b0e32f0aae5d07b820f2cbf` |
|  `pipeline/test_core_strategy.py`  | `a0d5b46845d3fde006ed817fe21bdd8b6546c1d1` |
|  `pipeline/test_decision.py`  | `6781f26d66635f56662a627bdd3b4a63f26c1f28` |
|  `pipeline/values.py`  | `5576376454af129b944919fb588e26c0657a781e` |

## 6. KEEP — target-only T2 additions

These target-only files are absent from the current source branch tree. Preserve them; they include the target Account/Risk Contract and target-specific F4 regression specifications.

| Target-only path | Target blob SHA | Disposition |
|---|---|---|
|  `paper_execution/risk_contract.py`  | `7ae74740568e3bcad78acd928896ee363cc62613` | KEEP — target-only addition |
|  `paper_execution/test_f4_r1_account_contract.py`  | `e71cf941c7e59db44dcd7f3e0b948940e7f25cdc` | KEEP — target-only addition |
|  `paper_execution/test_f4_r3_reset_red.py`  | `ea87e42b52889ed9fd926f3d647a9b8ca87d22df` | KEEP — target-only addition |
|  `paper_execution/test_f4_risk_red.py`  | `7e03122ee72cb88cd039d99ca4a9ed6acfe1f656` | KEEP — target-only addition |

## 7. MIGRATE-CANDIDATE — source-only T2 code and tests

The following source-only files are candidates for selective migration. The table records exact source blob SHA. Candidate status is not permission to copy; each group requires import/dependency review and an approved target-side test gate.


### core_runtime/

MIGRATE-CANDIDATE — Core runtime and paper runner; orderbook HTTP consumer files require separate T1 boundary review.


| Source path | Source blob SHA |
|---|---|
|  `core_runtime/__init__.py`  | `4c0781247f6b7d9bd8e17a072bc107ea7705dc28` |
|  `core_runtime/__main__.py`  | `31fd90cf4b957aef91a4127d6df48715e2f07fb5` |
|  `core_runtime/adapter.py`  | `9795c346d2eec4c78c22035c32f463af6b40b8f4` |
|  `core_runtime/api_facade.py`  | `98dfc38008480a5bc686e9f03e4e09041b5ad54e` |
|  `core_runtime/bundle_inputs.py`  | `f78ebde30413a3329063a2c68c457fe862a50c5e` |
|  `core_runtime/bundle_provider.py`  | `9d67f1600d4177e6f9756e366af6ef9319b27c19` |
|  `core_runtime/continuous_cadence.py`  | `b0fed155918dd8b6943785da82a677cf4a9b1f07` |
|  `core_runtime/continuous_dry_run.py`  | `6adb9ecf436952b61c7e8b68acbe5075ef64d652` |
|  `core_runtime/continuous_journal.py`  | `ea91dd382c14704b489d2cc872f73bc83c800e8d` |
|  `core_runtime/continuous_runner.py`  | `a654d03bc2332eb14c0c2498a80882691920825c` |
|  `core_runtime/input_bundle.py`  | `19fb3065da1e7d40c8b4376fe3b51e11c8cc8f87` |
|  `core_runtime/ledger_path_guard.py`  | `f5b260165de7a5dd840f6d53a0e5ac59ee3ab328` |
|  `core_runtime/one_shot.py`  | `0bc72d0069880f5445a9d329c0cc660f67838197` |
|  `core_runtime/orderbook_contract.py`  | `1620c9f21b1f3df3c2fb65833f2afd80374bf6a5` |
|  `core_runtime/orderbook_http.py`  | `89e5129eea4c9e7ceaa4439a546daf112d15c3e3` |
|  `core_runtime/paper_ledger_preflight.py`  | `e5d4b26bc1a48a765d16a8cd6708dfdc83b12a88` |
|  `core_runtime/preflight.py`  | `3e179b75c09f1a0e1dc3bd8c595cda5afc9bc86f` |
|  `core_runtime/runtime_factory.py`  | `b2dbd2efe0076ad5e831682caea0bd5e4a4f8bd6` |
|  `core_runtime/test_api_facade.py`  | `f860d32c4047374dec4f574605a1c1b21ba1a58b` |
|  `core_runtime/test_bundle_inputs.py`  | `28a0204c57e9933f3527f1048fa71d3e5a9b6356` |
|  `core_runtime/test_bundle_provider.py`  | `4ba67df010b2bc98346da96ddbc4cbc325942d30` |
|  `core_runtime/test_continuous_cadence.py`  | `e06753d61aeea30fec039423d90a813a9ec11886` |
|  `core_runtime/test_continuous_dry_run.py`  | `cd8f95b346bb2ec60cfe2253f8c94b71cf0d1f73` |
|  `core_runtime/test_continuous_journal.py`  | `cbc07201d401dd74d6b42d7b7ef710bc4e1cd6ba` |
|  `core_runtime/test_continuous_runner.py`  | `90c8935d88359be720c19c424c46115ababab086` |
|  `core_runtime/test_input_bundle_contract.py`  | `e6c331ea791108b5b18eda0eae4cff91d314bd27` |
|  `core_runtime/test_orderbook_contract.py`  | `935a3f2c8467e4f56cc683a7c0afcaba8fbeee00` |
|  `core_runtime/test_orderbook_http.py`  | `6edb8dea8ea208c229439b2655f1ed03c173e055` |
|  `core_runtime/test_orderbook_http_integration.py`  | `eaa282ae4ea6fd0d7dba611a124eea36ad31c7d8` |
|  `core_runtime/test_paper_ledger_preflight.py`  | `e2909dd3a9b3e517ae72b53cc93cd9ab0d43a538` |
|  `core_runtime/test_runner_hardening.py`  | `e6736493f8cd73840c5c2bcf1c116a1bd739d9c8` |
|  `core_runtime/test_runtime_factory.py`  | `5ad2c786bbc84f2c0aed081e5bdb4bd3986c62a8` |
|  `core_runtime/test_terminal_order_recovery.py`  | `fa3def022b92214e897253d29b4c0c6f90518ca9` |

### freqai_bridge/

MIGRATE-CANDIDATE — offline FreqAI prediction bridge; isolated Freqtrade 2026.9 dependency only.


| Source path | Source blob SHA |
|---|---|
|  `freqai_bridge/ChartProFreqaiResearch.py`  | `a7722f1148cf105c853deedaacb88edd14e671be` |
|  `freqai_bridge/README.md`  | `380a2c6abdfc2bc8b42281558f8a137d059c4820` |
|  `freqai_bridge/config.research.json`  | `2ddccabc8a88a66ace251070c03d8623214291ac` |
|  `freqai_bridge/context.py`  | `e87918cb1bbef9cbbb120181b70d17ef4ca36d8a` |
|  `freqai_bridge/exporter.py`  | `3b707174316d0c6b464ac947cbbe2d2fbee73682` |
|  `freqai_bridge/http_candles.py`  | `1f430c6d3a762deab9342e42072824661df3bf96` |
|  `freqai_bridge/t2_http_migration_acceptance.py`  | `ae36ff07c7a72f6148b978d6b11aad8ee7a45c2e` |
|  `freqai_bridge/test_context_http.py`  | `f19fe58c761d6f09d089e760951aa06ea1ab530f` |
|  `freqai_bridge/test_context_multi_timeframe.py`  | `972fb70f7a3f6bc8b3929baac011152385029a9b` |
|  `freqai_bridge/test_exporter.py`  | `2d199db931ca4ab39548f88797672f7fbf0d85bc` |
|  `freqai_bridge/test_http_candles.py`  | `8b38048e72d781d9219de1fe789e7078962c4824` |
|  `freqai_bridge/test_multi_timeframe.py`  | `610a1bf75f13b9802eda6bf77bc29cbf039f816d` |

### pipeline/

MIGRATE-CANDIDATE — AI calibration/OOS/lifecycle contracts and tests; shared paths with different blobs are RECONCILE.


| Source path | Source blob SHA |
|---|---|
|  `pipeline/calibration_registry.py`  | `691ef04d69b5aad6362fc9f2024ca300b39150e1` |
|  `pipeline/lifecycle_disposition.py`  | `cf22385a718c6b5b08cd50c2a45578b4180c2c4d` |
|  `pipeline/oos_evaluation.py`  | `756f7d2707051cb7f90bd5b7c62ff4d6f269f21d` |
|  `pipeline/synthetic_contract.py`  | `f114bd08de56ff641e29697f63ac6d11d127e3cc` |
|  `pipeline/test_ai_calibration_registry.py`  | `a5c36c7b32fc5bee16ca2c619c96f9270d22b8ff` |
|  `pipeline/test_ai_strategy_contract_red.py`  | `3592d7aa9edeb4eac039153f1e5c19a9bf3b5fcf` |
|  `pipeline/test_api_t0_http_boundary.py`  | `936e9c8114921450e86718a1b74729f31104b2a8` |
|  `pipeline/test_core_runtime_adapter_contract.py`  | `fbe6cc428fd7058a6dbefd9eaec1979a95638474` |
|  `pipeline/test_core_runtime_contract.py`  | `f6a365509d9821f5284323cb7e7ff4073621628d` |
|  `pipeline/test_core_runtime_one_shot.py`  | `5b2d302458e5aba66fb4b902cf15502fe6ca2d09` |
|  `pipeline/test_core_sizing.py`  | `0ec23eecaf0f1b130b9dce51ff9cee16cad35cfb` |
|  `pipeline/test_lifecycle_disposition.py`  | `d54d0523d6388df448cbec7c2fb9e2e092f72920` |
|  `pipeline/test_oos_evaluation.py`  | `df99039702d23cf01f39aaa35536e0fbf8920d2a` |
|  `pipeline/test_paper_storage_isolation.py`  | `be83620121903fbecab7ca1c577cf014fafff410` |
|  `pipeline/test_synthetic_contract.py`  | `4125d56f94ea4c06df6fa6f3c02232e23ec61108` |

### paper_execution/

MIGRATE-CANDIDATE — only source-only funding/simulated-equity/bootstrap/dual-ledger related files; shared paths with different blobs are RECONCILE.


| Source path | Source blob SHA |
|---|---|
|  `paper_execution/binance_public_funding.py`  | `018d86732af1bcfd5e8dc8825188aa24895d82be` |
|  `paper_execution/bootstrap.py`  | `2a75724d0071ecc340617bfc52f4198c09926c92` |
|  `paper_execution/contracts/simulated_capital_v1.json`  | `fa2d02fa6b47429896df1faec674728151820b04` |
|  `paper_execution/funding_evidence_package.py`  | `cf7ebddafb88b88f9d5ae38cd998508c74ab7837` |
|  `paper_execution/funding_evidence_package_builder.py`  | `eb41e7634a745645c95e68a4bcb51e0cbc0f53ae` |
|  `paper_execution/funding_lineage.py`  | `d677c7d101fd3c659e7c73785d9735dd2ff692d4` |
|  `paper_execution/funding_model.py`  | `128619ba92ab5b46ff8f5b9fa4a61991f7c0faf1` |
|  `paper_execution/funding_position_projection.py`  | `2be3289bbd139c08cc2717680608db82202ffdb5` |
|  `paper_execution/funding_provenance.py`  | `55250d7e5d205b4b29446048859eaa724491529e` |
|  `paper_execution/funding_reconciliation.py`  | `4a25b4f2a672add9d4d51f96f794996046c19d48` |
|  `paper_execution/kill_reset_service.py`  | `965ef11a07840b7e3c17664494b14978e14bdb56` |
|  `paper_execution/owner_attestation.py`  | `5032cc32264f2603f541db0606a03a7131d579a2` |
|  `paper_execution/paper_funding_posting.py`  | `89be68471c6e21c9acf573201037a725e926cd74` |
|  `paper_execution/simulated_capital.py`  | `b3d23a212ba8c75cb49b7967654dfe6a67167cb6` |
|  `paper_execution/simulated_daily_baseline.py`  | `bf3a0bb56d8e12e26f529b258d430dd35c7f88c3` |
|  `paper_execution/simulated_equity.py`  | `24e17df782d90a229097fb0244c5d37877c756c7` |
|  `paper_execution/simulated_origin.py`  | `ae93276d86eb01695ea363a337eafbbed44de227` |
|  `paper_execution/test_account_risk_snapshot_read_only.py`  | `a3b460c356cebe49bfa89edfa8202fed5edf513b` |
|  `paper_execution/test_binance_public_funding.py`  | `e86c09a2116129e8d47ee9a270a5b49a36dada7a` |
|  `paper_execution/test_core_first_operational.py`  | `edd604af75ce0933251a3c099d878798ba4da961` |
|  `paper_execution/test_core_runner_ledger_integration.py`  | `c8ee43a61b10c1bbc91139db27f0344c29473f3a` |
|  `paper_execution/test_core_short_lifecycle.py`  | `15dadc5a9087a203de91b3e7c0658b711756118b` |
|  `paper_execution/test_dual_ledger_bootstrap.py`  | `e58f1bc0a51758090036a7757b8038f14dad8cae` |
|  `paper_execution/test_dual_ledger_owner_attestation.py`  | `9f74c9b63fa004cfc0a73433ec825e808480157b` |
|  `paper_execution/test_funding_evidence_package.py`  | `cd54795d59443c4c90f701fb7379cb980434d055` |
|  `paper_execution/test_funding_evidence_package_builder.py`  | `5a89a8140ff43d6b75c36b9858a9bb87b1baa72c` |
|  `paper_execution/test_funding_lineage.py`  | `fecf05e172ec3460f1cef9610823dd1ccaab6455` |
|  `paper_execution/test_funding_model.py`  | `e9948c74d3a75e518e4d0ea0ab45966957ec91c4` |
|  `paper_execution/test_funding_position_projection.py`  | `cd37504603cb46553a23c03a4a1f1203e1b18d08` |
|  `paper_execution/test_funding_position_projection_db.py`  | `efa2f743610637777990694907d1f8afabe404ad` |
|  `paper_execution/test_funding_provenance.py`  | `bbc7f5d9fd0bc15983f67b2b5c820a2116e28309` |
|  `paper_execution/test_funding_reconciliation.py`  | `5b61f6a7ad5c3eedb027a055b43cd1562ba43370` |
|  `paper_execution/test_funding_reconciliation_persistence.py`  | `ec0d61b1e085b4900eb6b0fda2c55f3ff6041f4a` |
|  `paper_execution/test_paper_funding_end_to_end.py`  | `adfa8f6db5cd680084c15bf587114f62b2227009` |
|  `paper_execution/test_partial_fill_process_crash.py`  | `e0847a38c9c6680c63b090c2fe6018d9fba9c947` |
|  `paper_execution/test_simulated_capital_contract.py`  | `b259a53ebe3580f34ebabb45eab65fb4e14c15a0` |
|  `paper_execution/test_simulated_equity.py`  | `e2aacddc899102a89f8aee19337ecaf35465513a` |
|  `paper_execution/test_simulated_order_admission.py`  | `bbd6192dd296e7794ae8d335c9ce21ea99ddee26` |
|  `paper_execution/test_simulated_origin.py`  | `ea53ed0540ba9f84ec1c1f5e69b40014e79a62f2` |
|  `paper_execution/test_support.py`  | `e095c28da2a99fed5061f4a93db229a6c834b3f9` |

## 8. MIGRATE-CANDIDATE — architecture and evidence documents

The following source documents are absent from the target tree at the inventory HEAD. They may be transferred as provenance-preserving design references after status reconciliation.

| Source document | Source blob SHA | Disposition |
|---|---|---|
|  `docs/architecture/AI_STRATEGY_CONTRACT.md`  | `5b91fce68e1697e562d0cf1440426d8a2910eb9d` | MIGRATE-CANDIDATE — design only; preserve Core-first / AI-offline status. |
|  `docs/architecture/DUAL_LEDGER_CONTRACT.md`  | `a8d1d7542b370f8088ea422e6e98fb1e7bd7e8ed` | MIGRATE-CANDIDATE — design contract only; no AI paper execution authorization. |
|  `docs/architecture/AI_STRATEGY_RESEARCH_EVALUATION_CONTRACT.md`  | `cda4cb6c82100ec5e6c2f977451a51d6ec058838` | MIGRATE-CANDIDATE — offline research protocol; training/production not authorized by this file. |
|  `docs/architecture/AI_CALIBRATION_ARTIFACT_CONTRACT.md`  | `bcd63e458164bf8668644d341d8b71a41f59b370` | MIGRATE-CANDIDATE — calibration trust/evidence contract; not an implementation. |
|  `docs/architecture/CORE_SIZING_LEVERAGE_POLICY_PROPOSAL.md`  | `cc150b732dfaf46d64e2ce745897e3c26d6f97de` | RECONCILE — conflicts with other Core leverage statements; do not adopt as authoritative without decision. |
|  `docs/evidence/CORE_FIRST_RELEASE_READINESS_AND_DUAL_STRATEGY_PLAN_2026-11-12.md`  | `836ccac125ad18a2d0c0c2cfa6c9d0adedbe0f94` | MIGRATE-CANDIDATE — historical evidence only; its exact tested SHA is not current branch HEAD. |

Important source-side status from `docs/PROJECT_SESSION_HANDOFF.md` (last updated 2026-11-18):
- Core First is the active priority.
- Strategy Core (RSI + ADX + Smart DCA) is the only paper-executable strategy.
- AI is observation/research only; `AI_EXECUTION_ENABLED=false`.
- The source handoff says not to begin Dual-Strategy Intelligence implementation until Core First closeout and separate owner approval.
- AI Strategy Contract is a design contract; AI research evaluation is offline research scope; neither authorizes AI paper execution.
- Historical test evidence is tied to its recorded source SHA, not automatically to current source HEAD `e6606e28a696374f31cd6db1ec0a1372d942d64d`.

The user's desired end-state remains Dual-Strategy Intelligence, but this manifest authorizes only migration planning. AI signal production, AI ledger admission and AI paper execution remain separate work items requiring their own approval and tests.

## 9. EXCLUDE / KEEP IN OWNER REPOSITORY — no blanket transfer

| Source paths / area | Disposition | Reason |
|---|---|---|
| `market_data/` | EXCLUDE from T2 migration | T0 code/data boundary; target already has the current T0 implementation. Do not overwrite or duplicate canonical T0 assets. |
| `futures_intelligence/collector_sidecar_writer/` | EXCLUDE | Collector-sidecar implementation belongs with T1 ownership; no duplicate collector implementation in application repo. |
| `futures_intelligence/connection_events.py` and related tests | Separate review only | Do not assume these are T2 consumers without a precise interface contract. |
| `integrations/hummingbot_bridge.py` | KEEP dormant in target | Hummingbot integration is deferred; no activation, dependency or runtime wiring. |
| `.github/workflows/*` | EXCLUDE from bulk copy | Create target-specific isolated workflows only after migration scope and exact source pins are approved. Relevant source workflow names include: `.github/workflows/ai-strategy-contract-red.yml`, `.github/workflows/core-live-data-operational-proof.yml`, `.github/workflows/dual-ledger-bootstrap-contract.yml`, `.github/workflows/dual-ledger-owner-attestation.yml`, `.github/workflows/dual-ledger-red.yml`, `.github/workflows/paper-ledger-t1-compatibility.yml`, `.github/workflows/t1-t2-orderbook-contract.yml`, `.github/workflows/t2-freqtrade-2026-9-strategy-smoke.yml`, `.github/workflows/t2-http-consumer-red.yml`. |
| `ci/*` | EXCLUDE from bulk copy | Mixed T0/T1/T2, Android and historical CI tooling; select only after reviewing what a target-specific gate needs. |
| `android-app/`, `control_dashboard/`, `dashboard/`, Codemagic files | EXCLUDE | Outside the selected T2 application migration scope or retained legacy surfaces. |
| `bot.py`, Telegram command/scanner/backtest artifacts and legacy workflow/dependency files | EXCLUDE | Retired legacy scope; do not reintroduce into the Quant application. |
| `synthetic_evidence/`, `t0_signature_stage1/`, `d07_9_lineage/` | EXCLUDE from T2 code migration | Independent evidence/provenance workstreams; preserve their ownership and scope. |

## 10. Migration sequence and gates

1. **M1 — Resolve source/target conflicts.** Decide Core leverage/ROE semantics; review the 18 shared T2 path differences; preserve target Account/Risk Contract and F4 corrections.
2. **M2 — Core runtime candidate review.** Review `core_runtime/` import closure, ledger path guard, preflight, dry-run runner and recovery behavior. Orderbook HTTP consumer files require T1 boundary review. No runtime activation.
3. **M3 — T0/T1 consumer boundary.** Verify read-only T0 HTTP contract and T1 consumer contracts. No canonical SQLite access or T1 provider activation.
4. **M4 — AI research bridge.** Review `freqai_bridge/`, calibration/OOS/lifecycle contracts and isolated Freqtrade 2026.9 dependency. Offline research only; no AI paper order path.
5. **M5 — Shared Risk / Dual Ledger.** Reconcile ledger, account risk contract, Kill Switch, Core/AI ledger isolation, aggregate exposure and concurrent admission. Require dedicated RED/GREEN evidence before any AI paper admission.
6. **M6 — Target CI and handoff.** Add only target-specific workflows, pin exact source/test blobs, record run IDs and artifacts, and update the project handoff after each approved increment.

## 11. Verification and current status

| Check | Result |
|---|---|
| Source and target repository/branch refs | PASS — exact HEADs recorded |
| Recursive Git tree retrieval | PASS — both `truncated=false` |
| File/blob inventory | PASS — 1122 source and 185 target blob entries |
| Shared-path blob comparison | PASS — 36 identical, 35 different |
| T2 migration classification | PARTIAL — candidates and blockers recorded; individual semantic review remains |
| Tests | NOT RUN |
| Workflows | NOT RUN |
| Source/target dependency closure | NOT VERIFIED |
| Runtime/database/VPS/exchange | NOT ACCESSED |
| Code migration | NOT STARTED |
| Paper execution | NOT AUTHORIZED |
| Live trading | PROHIBITED |

**Next permitted action:** continue read-only semantic review of M1 conflicts and dependency/import closure. Do not copy files, edit production code, add dependencies, dispatch workflows, touch T0/T1 runtime, or enable AI/Core execution under this manifest alone.
