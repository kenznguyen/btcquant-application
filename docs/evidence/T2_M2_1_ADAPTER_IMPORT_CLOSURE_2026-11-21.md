# T2 M2.1 — Core producer adapter import-closure review

Date: 2026-11-21

## Scope and immutable inputs

Read-only semantic/import-closure review only. No source copy, application code edit, dependency change, test execution, workflow dispatch, runtime, database, T0/T1 integration, or order execution.

- Target repository: `kenznguyen/btcquant-application`
- Target branch: `main`
- Target HEAD: `49110121e0b54b5e96e05f6efbf2624a947956c8`
- Target handoff blob: `docs/PROJECT_SESSION_HANDOFF.md` — `f4684958b0411d363d81ec2c067bb9e2adfeadcb`
- Source repository: `kenznguyen/btcusdt-telegram-signals2`
- Source branch: `feature/core-operational-proof-20261112`
- Source HEAD (pinned migration input): `e6606e28a696374f31cd6db1ec0a1372d942d64d`

## Reviewed source files

| Path | Source blob | Static result |
|---|---|---|
| `core_runtime/adapter.py` | `9795c346d2eec4c78c22035c32f463af6b40b8f4` | Pure report translator; imports only `collections.abc.Mapping`; no third-party dependency or I/O |
| `pipeline/test_core_runtime_adapter_contract.py` | `fbe6cc428fd7058a6dbefd9eaec1979a95638474` | Six focused contract tests; validates BUY/SELL/CLOSE/WAIT mapping, action mismatch and missing provenance |
| `core_runtime/one_shot.py` | `0bc72d0069880f5445a9d329c0cc660f67838197` | Caller imports adapter; broader runner is not a standalone adapter migration |
| `pipeline/core_signal.py` | source path absent from source-only list; target counterpart reviewed below | Source report validator boundary |
| `core_runtime/input_bundle.py` | `19fb3065da1e7d40c8b4376fe3b51e11c8cc8f87` | Depends on `rfc8785` and T1 orderbook contract; defer from this adapter slice |
| `core_runtime/bundle_inputs.py` | `f78ebde30413a3329063a2c68c457fe862a50c5e` | Depends on `rfc8785`, input-bundle and orderbook modules; defer |
| `core_runtime/orderbook_contract.py` | `1620c9f21b1f3df3c2fb65833f2afd80374bf6a5` | Pure stdlib validator, but T1→T2 consumer contract; separate T1 boundary review required |

## Target-side comparison

| Target path | Target blob | Finding |
|---|---|---|
| `pipeline/core_signal.py` | `df5fbb59611bdd4fbb8224665f79655dd4433455` | Existing target validator consumes a validated signal report and returns BUY/SELL/CLOSE intent form |
| `pipeline/core_strategy.py` | `c14e76f2cecb9f8aca54db263ded1ff17881cb24` | Current Core producer imports `CORE_LEVERAGE`; target constant remains 13 and is a separate unresolved policy conflict |
| `risk_policy.py` | `91b46513041033cbcd7e939ed081b71714c82ff3` | `CORE_LEVERAGE=13`; do not migrate or overwrite under this review |
| `persistent_state/risk_admission.py` | `2c90c2f012bad133b2f5872cdbce8b569427feee` | Target has a common AccountRiskSnapshot-backed SharedRiskEngine; Core/AI admission must converge here |
| `pipeline/test_core_runtime_adapter_contract.py` | not present on target main | Focused source tests are not yet represented in target |

The adapter's output is shaped for the target `pipeline.core_signal.validate` contract: it converts producer BUY/SELL/CLOSE to LONG/SHORT/FLAT while preserving producer-supplied provenance and never synthesizing missing values. Its imports are stdlib-only. The source one-shot runner then validates this adapted signal before continuing into its source-side PaperLedger path.

## Disposition

- `core_runtime/adapter.py`: **MIGRATE-CANDIDATE — APPROVE FOR A FUTURE ISOLATED PURE-ADAPTER SLICE**, conditional on adding the six source contract tests (or equivalent target-owned tests) and proving exact parity against target `pipeline.core_signal.validate`.
- Do not copy the source `one_shot.py` as part of this slice. Its preflight, ledger, risk and submit path must be separately adapted to the target Shared Risk Engine, AccountRiskSnapshot, persistent state and manual/on-demand lifecycle.
- Do not migrate `input_bundle.py`, `bundle_inputs.py`, or `orderbook_contract.py` in this slice. Their dependency and T1/T0 contract closures require separate reviews.
- Do not change Core leverage/sizing semantics. The target's 13x leverage constant conflicts with the approved direction and must be resolved in a separate owner-approved contract before Core strategy migration.
- This adapter is Core-specific; it does not implement independent AI signal production. AI signal generation and AI paper admission remain separately gated. Every eventual Core/AI proposal must pass the same target Shared Risk Engine; no parallel risk gate is acceptable.

## Status

- Exact source/target references: **PASS — PINNED FOR THIS REVIEW**
- Adapter import closure: **PASS — STDLIB ONLY**
- Target semantic parity: **PARTIAL — STATIC SHAPE MATCH; TESTS NOT RUN**
- Target-side adapter tests: **NOT PRESENT**
- Core leverage semantics: **BLOCKED**
- Caller/ledger/risk migration: **DEFERRED**
- Tests/workflows/artifacts: **NOT RUN / NONE**
- Code migration: **NOT STARTED**
- Runtime, DB, T0/T1 connection, paper execution and live trading: **NOT ACCESSED / NOT AUTHORIZED**

## Next permitted step

Continue read-only import and test inventory for the remaining M2.1 candidates, then submit a refreshed per-file migration manifest and adapter boundary for review. No source code copy or workflow execution is authorized by this report.
