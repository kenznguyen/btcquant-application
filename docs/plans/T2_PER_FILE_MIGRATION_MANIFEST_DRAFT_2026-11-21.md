# T2 M2.1 — Per-file migration disposition and target mapping

Date: 2026-11-21

## Scope

Read-only mapping of the pinned source tree to the target `main` tree. This is a migration manifest draft and disposition record, not authorization to copy code, add dependencies, run tests/workflows, or connect runtime services.

- Source repository: `kenznguyen/btcusdt-telegram-signals2`
- Source branch: `feature/core-operational-proof-20261112`
- Source HEAD: `e6606e28a696374f31cd6db1ec0a1372d942d64d`
- Target repository: `kenznguyen/btcquant-application`
- Target branch: `main`
- Target HEAD before this evidence commit: `bc4b65748976e5aa57d734fe482250271368e12a`

## Per-file manifest — Core adapter and shared primitives

| Source path (blob) | Target path/state | Disposition | Required gate |
|---|---|---|---|
| `core_runtime/adapter.py` (`9795c346d2eec4c78c22035c32f463af6b40b8f4`) | No adapter file; target has `pipeline/core_signal.py` (`df5fbb59611bdd4fbb8224665f79655dd4433455`) | Candidate for isolated adapter slice | Add target-owned contract tests; prove parity for BUY/SELL/CLOSE/WAIT, provenance preservation, malformed/missing report behavior |
| `pipeline/core_signal.py` (`df5fbb59611bdd4fbb8224665f79655dd4433455`) | Exact same target blob | Already present; do not copy | Preserve target contract; regression tests if caller changes |
| `pipeline/values.py` (`5576376454af129b944919fb588e26c0657a781e`) | Exact same target blob | Already present; do not copy | No migration work |
| `pipeline/decision.py` (`8720d8ab988529b1545a27aa0792beca9e6a84aa`) | Exact same target blob | Already present; do not copy | Keep target-owned dependency; note it imports `market_data.store`, so never transplant source `market_data/` |
| `pipeline/core_strategy.py` (`0be512d99b4302077ab79879184b74949f0feaaa`) | Target counterpart exists, different blob `c14e76f2cecb9f8aca54db263ded1ff17881cb24` | BLOCKED — semantic divergence | Reconcile signal ROE multiplier vs leverage/sizing semantics; preserve 1% order-margin cap and common Shared Risk Engine; owner contract and regression suite required |
| `risk_policy.py` source (`823d04748105b2996a28f2b09e3ce77bea073dce`) | Target counterpart blob `91b46513041033cbcd7e939ed081b71714c82ff3` | BLOCKED — conflicting Core leverage constants | No file overwrite; separately approved policy contract required |

## Per-file manifest — FreqAI bridge

| Source path (blob) | Target path/state | Disposition | Required gate |
|---|---|---|---|
| `freqai_bridge/http_candles.py` (`1f430c6d3a762deab9342e42072824661df3bf96`) | Directory absent in target | Candidate — isolated read-only adapter | Target T0 Candle Contract 1.2.0 is not implementation-ready; do not connect to T0; exact HTTP DTO/version gate required |
| `freqai_bridge/context.py` (`e87918cb1bbef9cbbb120181b70d17ef4ca36d8a`) | Directory absent | Candidate — research context builder | Depends on bridge exporter and target-owned `pipeline.values`; fixture tests required |
| `freqai_bridge/exporter.py` (`3b707174316d0c6b464ac947cbbe2d2fbee73682`) | Directory absent | Candidate — prediction/provenance artifact only | Target-owned tests; no paper admission or execution; preserve WAIT/fail-closed behavior |
| `freqai_bridge/ChartProFreqaiResearch.py` (`a7722f1148cf105c853deedaacb88edd14e671be`) | Directory absent | Defer — framework-bound research strategy | Freqtrade/FreqAI 2026.9 isolated dependency/image digest lock and framework load evidence required; prediction-only, no native orders |
| `freqai_bridge/config.research.json` (`2ddccabc8a88a66ace251070c03d8623214291ac`) | Directory absent | Defer — config, not copy-ready | Review paths, secrets, pair and dry-run controls against target config policy |
| `freqai_bridge/test_http_candles.py` (`8b38048e72d781d9219de1fe789e7078962c4824`) | No target equivalent | Candidate target-owned tests | Synthetic/fake HTTP only; no T0 network |
| `freqai_bridge/test_context_http.py` (`f19fe58c761d6f09d089e760951aa06ea1ab530f`) | No target equivalent | Candidate target-owned tests | Fake client only |
| `freqai_bridge/test_context_multi_timeframe.py` (`972fb70f7a3f6bc8b3929baac011152385029a9b`) | No target equivalent | Candidate target-owned tests | M15/H1 deterministic fixtures |
| `freqai_bridge/test_exporter.py` (`2d199db931ca4ab39548f88797672f7fbf0d85bc`) | No target equivalent | Candidate target-owned tests | Isolated pandas dependency and temporary output only |
| `freqai_bridge/t2_http_migration_acceptance.py` (`ae36ff07c7a72f6148b978d6b11aad8ee7a45c2e`) | No target equivalent | Defer until T0 contract gate | It must not imply runtime connectivity or accept stale contract semantics |

The target currently has no `freqai_bridge/` directory and no `pipeline/calibration_registry.py`. Target `pipeline/decision.py` is identical to the pinned source blob and remains target-owned.

## Per-file manifest — AI calibration

| Source path (blob) | Target path/state | Disposition | Required gate |
|---|---|---|---|
| `pipeline/calibration_registry.py` (`691ef04d69b5aad6362fc9f2024ca300b39150e1`) | Absent | DEFER — cryptographic verifier | Dedicated dependency lock for `rfc8785` and `cryptography`; pinned trust root/key governance; manifest/signature/artifact tests; independent review |
| `pipeline/test_ai_calibration_registry.py` (`a5c36c7b32fc5bee16ca2c619c96f9270d22b8ff`) | Absent | Candidate tests only after verifier boundary approved | Test-only Ed25519 key must remain fixture-only; offline tests; no production key or registry activation |
| `pipeline/test_ai_strategy_contract_red.py` (`3592d7aa9edeb4eac039153f1e5c19a9bf3b5fcf`) | Absent | Preserve as RED specification evidence; do not represent as passing implementation | AI strategy API, independent LONG/SHORT signal contract, calibration threshold ownership and shared risk admission must be approved first |

No production `pipeline/ai_strategy.py` exists at the pinned source path; the AI Strategy contract tests are intentionally RED. This is not a completed AI signal producer. No calibrated AI signal admission, AI ledger writes, or paper orders are authorized.

## Per-file manifest — Core runtime orchestration

These modules are explicitly excluded from the first migration slices because they bind source-specific storage, process lifecycle, paper ledger, risk admission or persistent journal behavior:

| Source path (blob) | Main imports / side-effect boundary | Disposition |
|---|---|---|
| `core_runtime/input_bundle.py` (`19fb3065da1e7d40c8b4376fe3b51e11c8cc8f87`) | `rfc8785`, orderbook contract | Defer; T0 1.2.0 and T1 DTO gates |
| `core_runtime/bundle_inputs.py` (`f78ebde30413a3329063a2c68c457fe862a50c5e`) | `rfc8785`, input bundle, orderbook contract | Defer; dependency and T0/T1 envelope gates |
| `core_runtime/orderbook_contract.py` (`1620c9f21b1f3df3c2fb65833f2afd80374bf6a5`) | stdlib validator, but defines T1→T2 contract | Separate T1 consumer contract review |
| `core_runtime/orderbook_http.py` (`89e5129eea4c9e7ceaa4439a546daf112d15c3e3`) | `requests`, T1 contract, network HTTP | Defer until T1 consumer boundary approval; no provider connection |
| `core_runtime/bundle_provider.py` (`9d67f1600d4177e6f9756e366af6ef9319b27c19`) | T0/T1 clients, `rfc8785`, source config, PAPER DB readers, path guard | Exclude from code-only first slice; would access external runtime and PAPER state |
| `core_runtime/preflight.py` (`3e179b75c09f1a0e1dc3bd8c595cda5afc9bc86f`) | source config and ledger/path guard | Defer; adapt to target-owned PAPER_DB resolver and AccountRiskSnapshot boundary |
| `core_runtime/paper_ledger_preflight.py` (`e5d4b26bc1a48a765d16a8cd6708dfdc83b12a88`) | source Paper Ledger and path guard | Defer; no ledger path or state access authorized |
| `core_runtime/one_shot.py` (`0bc72d0069880f5445a9d329c0cc660f67838197`) | adapter, preflight, ledger/risk/submit caller | Exclude; must be re-designed around target Shared Risk Engine and On-Demand lifecycle |
| `core_runtime/continuous_journal.py` (`ea91dd382c14704b489d2cc872f73bc83c800e8d`) | SQLite durable journal, file/path isolation | Exclude; persistence schema and ownership need target review; no DB creation |
| `core_runtime/continuous_runner.py` (`a654d03bc2332eb14c0c2498a80882691920825c`) | journal, bundle, preflight, one-shot caller | Exclude; process lifecycle conflicts with approved manual On-Demand model unless explicitly adapted |
| `core_runtime/continuous_dry_run.py` (`6adb9ecf436952b61c7e8b68acbe5075ef64d652`) | source config and runner policy | Defer; not a substitute for target static admission contract |
| `core_runtime/__main__.py` (`31fd90cf4b957aef91a4127d6df48715e2f07fb5`) | CLI, signals, runtime factory and runners | Exclude; explicit process entrypoint not part of pure code migration |

Target does not currently contain these `core_runtime/` paths. Do not create the directory by copying the source tree wholesale.

## Dependency policy

- Do not modify T0/global dependency locks.
- `rfc8785`, `cryptography`, `requests`, `pandas`, Freqtrade/FreqAI and LightGBM require isolated, exact-version/hash-locked dependency plans before installation.
- No package installation or dependency lock changes were performed.
- Existing target `pipeline/decision.py` imports target-owned `market_data.store`; no source `market_data/` file is in scope.

## Status and next gates

- Source/target tree mapping: **PASS — STATIC FOR LISTED PATHS**
- Adapter pure slice: **CANDIDATE; target tests absent**
- Existing shared primitives: **ALREADY IDENTICAL; NO COPY**
- FreqAI bridge: **DEFERRED; offline research-only candidate**
- AI calibration: **DEFERRED; cryptographic dependency/trust-root gates**
- AI Strategy: **NOT IMPLEMENTED; RED contract only**
- Core strategy/leverage: **BLOCKED**
- T1 orderbook: **SEPARATE REVIEW PENDING**
- Runtime/persistent orchestration: **EXCLUDED**
- Tests/workflows/artifacts: **NOT RUN / NONE**
- Source code migration: **NOT STARTED**
- T0/T1 runtime, databases, model training, paper orders, live trading: **NOT ACCESSED / NOT AUTHORIZED**

Next: submit this manifest for owner review. After approval, the first implementation slice may be limited to the pure Core adapter plus target-owned tests, with TDD (RED→GREEN) and no runner, ledger, dependency or runtime changes. All other modules require their own gates.


---

## Addendum — M2.4 AI Strategy Signal Contract RED (2026-11-21)

Owner approved the bounded M2.4 contract + test-only RED scope. This addendum supersedes the earlier manifest line that AI Strategy was only a source-side RED contract and target work had not started; it does not authorize GREEN implementation or runtime integration.

| Deliverable | Target path | Blob SHA / status |
|---|---|---|
| AI signal contract | `docs/architecture/AI_STRATEGY_SIGNAL_CONTRACT_V1.md` | `e5df7ec59c04a4f08b6ec0fc98e7e5702b3543dc` |
| Target-owned RED tests | `pipeline/test_ai_signal_contract_red.py` | `bd4c6325739a7d1eadf5ced64c71e7e4742e7a31` |
| Expected-RED workflow | `.github/workflows/t2-ai-signal-contract-red.yml` | `d8323caa1bc96f909219afd1028923971a247ad4` |
| Evidence | `docs/evidence/T2_M2_4_AI_SIGNAL_CONTRACT_RED_2026-11-21.md` | recorded on main |

- Final exact tested target SHA: `6fa66d2855a0d0804da6cee9ed37a723bbaf03d9`.
- Workflow run [44914696468](https://github.com/kenznguyen/btcquant-application/actions/runs/44914696468), job `136877715288`: SUCCESS as an expected-RED verification wrapper.
- 10 unittest methods ran; 27 expanded subtest error cases all showed the expected missing module `pipeline.ai_signal_contract`.
- Artifact ID `14711520763`; SHA-256 `822c74c766555c60e1f0f2c88af4f325aba8e7dafba3bd8d1b613287314018f0`.
- M2.4: **PASS — contract + RED specification**. GREEN implementation **NOT IMPLEMENTED / NOT AUTHORIZED**. Full repository regression and independent second-person review remain **NOT VERIFIED**.
- The signal report is AI-owned and independent of Core; validated output is signal-only. It is not an order, intent, reservation or ledger mutation. Every future exposure-increasing trade remains subject to the common Shared Risk Engine and Kill Switch.
- Next permitted increment: separate owner approval for M2.5 pure validator GREEN implementation. Do not add calibration registry cryptographic implementation, AI paper admission, dual-ledger writes, runner, runtime, DB, T0/T1 connection, deployment or trading under M2.4.


---

## Addendum — M2.5 AI Strategy Signal Validator GREEN implementation (2026-11-21)

Owner approved the pure validator GREEN implementation against the M2.4 AI Strategy Signal Contract V1 and its existing RED tests. This is a bounded implementation increment only.

| Deliverable | Target path | Blob SHA |
|---|---|---|
| Pure AI signal validator | `pipeline/ai_signal_contract.py` | `efb43ba777097e261c32671b9b37c24efad1a2e3` |
| Existing M2.4 contract RED tests | `pipeline/test_ai_signal_contract_red.py` | `bd4c6325739a7d1eadf5ced64c71e7e4742e7a31` — unchanged |
| Additional GREEN tests | `pipeline/test_ai_signal_contract_green.py` | `71dcffa586ce785472f2c88e753e755cfe742bfc` |
| Isolated GREEN workflow | `.github/workflows/t2-ai-signal-contract-green.yml` | `4fd7e23d9e12f97bc01940873267824aeafc651c` |
| Evidence | `docs/evidence/T2_M2_5_AI_SIGNAL_VALIDATOR_GREEN_2026-11-21.md` | latest evidence commit `b347788d3a34672df3920b71e77f32328eb64963` |

- Implementation commit: `ae11175bdb61880bb5351fd129428c40d8ec0071`.
- Test commit: `aba767e27cc728e6c83e9b3abf734cab1bf6e113`.
- Workflow/source commit: `04820704b88f143575f0ebbb582ac515b2e47aed`.
- Additional local scratch test methods: 12/12 PASS. The isolated GitHub workflow is configured to execute 22 tests total (10 existing M2.4 contract tests + 12 additional tests) in a pinned, network-disabled container.
- GitHub Actions run ID, job conclusion and artifact: **NOT VERIFIED**. Do not mark M2.5 PASS until exact run and artifact are inspected.
- M2.5 disposition: **PARTIAL — pure validator and additional tests committed; CI NOT VERIFIED**. Full repository regression and independent review remain NOT VERIFIED.
- Validator is pure and signal-only; WAIT is diagnostic. It performs no cryptographic verification, risk admission, sizing, reservation, ledger write or execution.
- No Core, Shared Risk Engine, Kill Switch, calibration registry implementation, ledger, runner, runtime, DB, T0/T1, VPS, deployment, exchange or trading behavior was changed or invoked.
- Next: inspect exact workflow run/artifact and review exact tested blobs. Any follow-up validator correction must use TDD and exact-SHA CI. Calibration Registry, risk admission, ledgers, runtime, DB, T0/T1 integration and execution require separate owner approvals.
