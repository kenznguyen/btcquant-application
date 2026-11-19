# F4 Selected Snapshot Migration — 2026-11-19

## Decision and scope
Owner approved a provenance-controlled F4 snapshot transfer from the legacy repository to the official application repository. This preserves source bytes; it does not correct or certify F4 behavior.

- Target: `kenznguyen/btcquant-application`, existing branch `main`.
- Target parent before migration: `a55ecccde7fd3e308fd54223f947cd3820ac7ac0`.
- Source: `kenznguyen/btcusdt-telegram-signals2`, branch `feature/t0-centralized-data-feeder-p1-20261101`, exact source HEAD `5223cef02f0e296c4f58afc5d7992b9c641ab208`.
- Transferred: complete `paper_execution/` package, directly required `pipeline/` API/Core/decision/value contracts and tests, `risk_policy.py`, and controlling Core-First architecture records.
- Excluded: legacy Git history, legacy workflows, dependency manifests, DB/data payloads, runtime configuration, and unrelated Telegram/dashboard/backtest components.
- No source repository mutation. Existing target T0 assets were not changed.

## Per-file provenance
Each source blob SHA equals the corresponding target blob SHA, preserving the file bytes exactly.

| Target path | Source and target blob SHA |
|---|---|
| `paper_execution/README.md` | `3f8fd2d51f945c27d9af866b7f2636b8d174dd4d` |
| `paper_execution/__init__.py` | `df25aa85d00c314e64dc60d8f5ae93185a931ceb` |
| `paper_execution/__main__.py` | `1e6b49d253e46fe747a413d1e829e18002db8a64` |
| `paper_execution/account_equity.py` | `9971dae4592f07fe7bd2315c0f1ec1daf97af8d1` |
| `paper_execution/account_history.py` | `6163065798b2386e1c466650048e40b7eab0d2eb` |
| `paper_execution/daily_baseline.py` | `747808d9a68a70e9c2aa6f71f00aeeffb6682145` |
| `paper_execution/daily_baseline_v1_recovery.py` | `b1c7aa54af569428d2a2e04300fc59ff49fa7a74` |
| `paper_execution/equity.py` | `40d6566294355c646839614c92f8fba6116b582c` |
| `paper_execution/funding.py` | `575758eb3223b4341ac37bad56d58e52539305c0` |
| `paper_execution/ledger.py` | `37c0aeb9dd28514dd19b87667b762c5592baf61f` |
| `paper_execution/replay_inputs.py` | `e32ec695546086449b35e43d8ae0d51f4dc32c27` |
| `paper_execution/replay_reconciliation.py` | `68a59b3938a28055e4d2b27733efcdb643127ea8` |
| `paper_execution/risk_control.py` | `3c76e462b0b4d924c2418842d95ed74285e2315d` |
| `paper_execution/test_account_cutover_snapshot_v7.py` | `0759e1cc350b4af92f41e80ae64ce47886ba553d` |
| `paper_execution/test_account_history_replay_red.py` | `9aa296ed2bc2c735ef98f28f44f486a58e911331` |
| `paper_execution/test_daily_baseline_persistence.py` | `7935111b7bb57e9558e88bef7a03ce425ebfccdb` |
| `paper_execution/test_daily_baseline_v1_recovery.py` | `aa7f6339c090e2d826ac4683f5ada0f3a49372e4` |
| `paper_execution/test_daily_equity_reconciliation.py` | `94ac12762a715231ee7c9dc3abef30f45d09303b` |
| `paper_execution/test_dual_ledger_migration_red.py` | `a2182cf8c39f2d36c16d371ba81348425153560e` |
| `paper_execution/test_dual_ledger_red.py` | `2c2104ada5743cbf55f64c8bc9690a14142fe3e0` |
| `paper_execution/test_dual_strategy_api_red.py` | `70eb419280717aa04560267e80716920844f8de1` |
| `paper_execution/test_equity.py` | `87eac43ff815903b1b8b7ea70dc3dcaeeb3abe43` |
| `paper_execution/test_f4_risk_red.py` | `5f0fe7af4677047f789b761d62a07389436bae72` |
| `paper_execution/test_ledger.py` | `0c05ae1ed0d9526978f8a90c983957dbd7baed5a` |
| `paper_execution/test_risk_control.py` | `69c9177a249369f52d0c81e442c9c4583c9f5b77` |
| `paper_execution/test_risk_limits.py` | `22645c481eea3f807fc72d659cdd05989f5673c5` |
| `pipeline/CONTRACTS.md` | `db00331a4d346314e8b059b702c2593fdd172f43` |
| `pipeline/api.py` | `d0217944bbfa9b864b0f259e0091daf9a989d180` |
| `pipeline/core_signal.py` | `df5fbb59611bdd4fbb8224665f79655dd4433455` |
| `pipeline/core_strategy.py` | `c14e76f2cecb9f8aca54db263ded1ff17881cb24` |
| `pipeline/decision.py` | `8720d8ab988529b1545a27aa0792beca9e6a84aa` |
| `pipeline/values.py` | `5576376454af129b944919fb588e26c0657a781e` |
| `pipeline/test_api.py` | `4e2d92b24a7c8c0810ac5f2706707c5b9deb6fb2` |
| `pipeline/test_core_signal.py` | `a946716604e2e1a74b0e32f0aae5d07b820f2cbf` |
| `pipeline/test_core_strategy.py` | `a0d5b46845d3fde006ed817fe21bdd8b6546c1d1` |
| `pipeline/test_decision.py` | `6781f26d66635f56662a627bdd3b4a63f26c1f28` |
| `risk_policy.py` | `91b46513041033cbcd7e939ed081b71714c82ff3` |
| `docs/architecture/CORE_FIRST_ARCHITECTURE_DECISION_2026-11-12.md` | `aa67dec436aa0c5b04031b9b313136e60602342f` |
| `docs/architecture/CORE_FIRST_READINESS_PLAN_2026-11-12.md` | `37dcc8b4de1fb9b10344da9be235a9b44244a7b2` |

## Known limitations carried forward
- F4-R1: risk limits remain caller/instance supplied rather than exclusively sourced from one validated Account/Risk Contract.
- F4-R2: missing or malformed Kill Switch state has not been proven fail-closed.
- F4-R3: Kill Switch reset readiness is caller-supplied and not atomically verified against authoritative account state.
- Core-First remains controlling: Core is the only paper decision path; AI is offline research only; no AI Ledger writes or paper orders; `AI_EXECUTION_ENABLED=false`.
- RED tests are specifications only, not GREEN evidence. Exact-target-SHA compile/tests/CI were not run.
- Dependency closure and integration compatibility remain NOT VERIFIED. No dependency installation or workflow changes were made.

## Verification and status
- Exact source branch/HEAD read: PASS.
- Transferred source files fetched at exact source ref: PASS.
- Blob identity: PASS (source and target SHA-1s match for all 39 files).
- Tests/workflows: NOT RUN.
- Runtime/database/VPS/exchange: NOT ACCESSED.
- Paper execution: NOT AUTHORIZED.
- Live trading: PROHIBITED.

**Disposition: MIGRATED — NOT VERIFIED.** This records source presence only, not functional readiness or authorization to execute.
