# F4-R1 Account Risk Contract — implementation and isolated verification

Date: 2026-11-19  
Repository: `kenznguyen/btcquant-application`  
Branch: `main`  
Verified source/workflow HEAD for R1: `12a2f53a21a0a9637d264d49f372e7dcf89fc730`

## Approval and scope

The owner approved the bounded F4-R1 implementation: make the validated account-level risk contract the only source of risk limits, reject strategy/caller overrides, add regression tests first, and verify using isolated GitHub Actions.

In scope:
- Persist, validate, read and explicitly revise the account-level risk contract.
- Bind PaperLedger instances to that persisted contract.
- Load the current contract within each order-admission transaction.
- Update impacted API and test fixtures.
- Add isolated CI evidence and record exact source/workflow/artifact identities.

Out of scope:
- F4-R2 Kill Switch malformed/missing-state correction and F4-R3 atomic reset-readiness correction.
- Full repository suite, T0/T1/T2 integration, production runtime, deployment, VPS, canonical DB, exchange connectivity and real trading.
- AI paper execution. Core-First remains controlling: Strategy Core only in the current paper path; AI offline research only; `AI_EXECUTION_ENABLED=false`.

## Implementation

- Added `paper_execution/risk_contract.py`:
  - `provision_account_risk_contract`: initial one-time account contract creation; identical repeat provisioning is idempotent; conflicting values are rejected.
  - `load_account_risk_contract`: validates schema, required limit fields, canonical JSON and SHA-256 integrity.
  - `read_account_risk_contract`: read-only lookup; does not create or migrate a database.
  - `update_account_risk_contract`: explicit compare-and-swap revision requiring the expected current hash, non-empty source/reason and timestamp; increments contract version and records an audit event.
- `PaperLedger` no longer accepts caller-provided `risk_limits`; a non-null value raises `ACCOUNT_RISK_CONTRACT_CALLER_LIMITS_FORBIDDEN`.
- Ledger instances expose a read-only mapping snapshot of contract limits. Order admission reloads the current contract inside the transaction so a stale per-strategy in-memory value cannot override the account contract.
- Missing limits reject new exposure with `RISK_LIMITS_UNCONFIGURED`; malformed/tampered contract state raises `ACCOUNT_RISK_CONTRACT_INVALID`; conflicting provisioning raises `ACCOUNT_RISK_CONTRACT_CONFLICT`; stale revision hashes raise `ACCOUNT_RISK_CONTRACT_VERSION_CONFLICT`.
- `pipeline.api.ledger()` provisions the initial contract from the shared environment configuration only after dual-ledger readiness checks. Repeated identical config is idempotent; environment drift against an existing contract is fail-closed. API quality reporting reads the persisted contract rather than independently parsing environment values; malformed contract state is surfaced as an INVALID quality stream rather than an unhandled server error.
- API tests now use the explicit versioned contract update operation when simulating a risk-policy change.

## Source identities at verified HEAD

| File | Blob SHA |
|---|---|
| `paper_execution/risk_contract.py` | `7ae74740568e3bcad78acd928896ee363cc62613` |
| `paper_execution/ledger.py` | `9fbf195cd6b19bd4ce2217f3648b4722a2472dcb` |
| `pipeline/api.py` | `0c288741afe386cacaa8d2c7d3991274a00c43ef` |
| `paper_execution/test_f4_r1_account_contract.py` | `e71cf941c7e59db44dcd7f3e0b948940e7f25cdc` |
| `paper_execution/test_risk_limits.py` | `3dd3afb6e7b7d361829bae0355412c468cbbc313` |
| `paper_execution/test_ledger.py` | `9606db101989cb50fd7104b930b35faa3fce671e` |
| `paper_execution/test_dual_ledger_red.py` | `0cf05418940a07a8357ee9d6039325a1efcb16f2` |
| `pipeline/test_api.py` | `f7bd8ff60b489ac309b20ea78f37b0708d7bba9a` |
| `pipeline/test_decision.py` | `6781f26d66635f56662a627bdd3b4a63f26c1f28` |
| `.github/workflows/f4-r1-account-risk-contract.yml` | `45339636a058850858698e6e637c6f114cd512f1` |
| `.github/workflows/f4-pipeline-core-first-isolated.yml` | `929ce3ca1030f5f5b5516812fb2590c562c9ab2f` |

## TDD and CI evidence

### RED
- Regression specification was added before implementation.
- Run [44466409033](https://github.com/kenznguyen/btcquant-application/actions/runs/44466409033), job `135365143505`, confirmed the contract implementation was absent and the new cases failed. This was an intentional RED run, not final verification.

### R1 GREEN — authoritative
- Run [44469872186](https://github.com/kenznguyen/btcquant-application/actions/runs/44469872186), branch `main`, exact workflow/source HEAD `12a2f53a21a0a9637d264d49f372e7dcf89fc730`.
- Job `135376446850`: SUCCESS.
- Python `3.12.16`; pinned image `python:3.12.16-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`.
- Command: `python -m unittest -v paper_execution.test_f4_r1_account_contract paper_execution.test_risk_limits paper_execution.test_ledger paper_execution.test_dual_ledger_red paper_execution.test_dual_ledger_migration_red pipeline.test_api pipeline.test_decision`.
- Result: `Ran 151 tests in 1.996s`; `OK`; 151/151 passed, 0 failures.
- Artifact: `f4-r1-account-risk-contract-evidence`, ID `14503362815`, SHA-256 `b0f6e2770fbb723a2e85c93e2b6788c2318324bc45d4eb14a6d169363eb3b922`.
- Workflow verified the exact test/source blob SHAs above. The test container ran with `--network none`, read-only source mount, non-root user, no credentials and no canonical database mount. The suite includes legacy dual-ledger migration fixtures, now seeded with an account contract and equity baseline before simulated orders.

### API / Decision regression
- Run [44468781493](https://github.com/kenznguyen/btcquant-application/actions/runs/44468781493), exact workflow/source HEAD `ff0c644a6143400735f271b8073253d545ba3606`.
- Job `135372900876`: SUCCESS.
- Result: `Ran 42 tests in 0.191s`; 42/42 passed, 0 failures.
- Artifact: `f4-pipeline-api-decision-evidence`, ID `14502974074`, SHA-256 `19d0b652584f3717104a97b13b929505eeb69d70c487e9f068ea872da8a11289`.
- The API workflow checked out the exact source, verified source blobs, confirmed Python 3.12.16 and a loopback-only network probe, then ran the API/decision modules in a network-disabled Docker container. Added coverage verifies a tampered contract produces an INVALID quality stream without crashing the API. The same API/decision modules are also included in the final 151-test R1 run at the latest R1 source SHA.

## Review and limitations

- Correctness: covered initial provisioning, idempotent provisioning, shared Core/AI reads, caller override rejection, missing-contract admission denial, tamper detection, explicit revision, stale-hash rejection, audit recording and existing Ledger/API regressions.
- Architecture: account contract is persisted once and consumed by both strategy ledgers; policy updates require an explicit expected hash and reason. No per-strategy risk-limit source remains in the paper API path.
- Security: SQL uses parameterized statements; contract content is canonicalized and hash-checked; read-only lookup opens SQLite in read-only URI mode; tests run without network/secrets/canonical DB.
- Performance: one small contract read is performed inside each order-admission transaction. No external dependency was added.
- Fixture correction: run `44469280970` exposed missing equity baselines in legacy `PaperLedger` tests after making the contract mandatory. Test fixtures were updated to provision the shared contract and a valid equity baseline; the production risk behavior was not weakened. Final run `44469440356` passes all 150 cases.
- Full repository test suite: NOT VERIFIED. The 151-test result is the bounded impacted-module suite, not the full repository suite.
- F4-R2 and F4-R3: remain OPEN / NOT VERIFIED; their separate RED specifications were not included in the R1 suite.
- Runtime/deployment/VPS/canonical DB/exchange/trading: NOT ACCESSED / NOT VERIFIED. No real orders were placed.
- Paper path policy unchanged: Core-First only; AI offline research only; live trading prohibited.

- Additional exact blobs: `paper_execution/test_dual_ledger_migration_red.py` `09320d363c8cb52806280c1de366895e09af3eeb`; `paper_execution/README.md` `814f9f6e185cb38ef9dc7368b39f882307943a44`; `pipeline/CONTRACTS.md` `b513eb99bcf95817b6b27a5f2d62fb750fd10c5d`.

## Status

- F4-R1 account risk contract: **PASS** within the bounded source and isolated regression scope.
- API/Decision regression: **PASS** (42/42 dedicated run; also rerun in final 150-test suite).
- Full repository suite: **NOT VERIFIED**.
- F4-R2/R3: **OPEN / NOT VERIFIED**.
- Runtime, deployment and production readiness: **NOT VERIFIED / NOT CERTIFIED**.

## Next step

Preserve this evidence and handoff. Any F4-R2/R3 work, full-repository test expansion, runtime/database access, deployment, AI execution or live trading requires a separate bounded approval.


## 2026-11-19 — Final call-site audit and CI evidence-gate hardening

- Read-only review confirmed the current source remained unchanged after the 151-test implementation run; the three commits between source HEAD `12a2f53a21a0a9637d264d49f372e7dcf89fc730` and the prior docs-updated `main` changed only this evidence report and the project handoff. Current verified source files retain the exact blob SHAs listed above.
- Audited every indexed `PaperLedger(` call site in the repository. The production API factory `pipeline.api.ledger()` provisions/verifies the shared account contract before constructing the strategy ledger. The local CLI is initialization/snapshot-only; it does not submit orders. The README instructs contract provisioning before any order submission. Test-only constructors without a contract are used for initialization, migration, or read-only setup; the order-admission path loads the persisted contract inside the transaction and unconditionally blocks increased exposure when the contract/required fields are absent (`RISK_LIMITS_UNCONFIGURED`).
- The dual-strategy API RED specification file contains setup-only `PaperLedger` constructions and no direct `.submit(` calls; it was not added to the bounded R1 suite because it is outside the selected risk-contract admission regression set. F4-R2/R3 specifications remain outside this approval.
- Corrected the R1 workflow's artifact metadata so the recorded test command includes all seven executed modules, including `paper_execution.test_dual_ledger_migration_red`. Added an explicit assertion that the expected test count is exactly 151, preventing a zero/partial discovery run from being accepted as successful. No application source or test fixture was changed in this follow-up.
- Latest workflow blob: `.github/workflows/f4-r1-account-risk-contract.yml` `df7a70a2574dda9bf3e2334122538bc7979a95db`. Source HEAD used by the run: `12a2f53a21a0a9637d264d49f372e7dcf89fc730`; workflow commit/run HEAD: `4dd18e66d8236e6864e572516eb5f406cf56bd00`.
- Latest authoritative isolated run [44484095453](https://github.com/kenznguyen/btcquant-application/actions/runs/44484095453), job `135423149350`: SUCCESS; `Ran 151 tests in 1.990s`; `OK`; 151/151 PASS. The workflow now records `expected_test_count=151` and enforces that count before success.
- Latest artifact: `f4-r1-account-risk-contract-evidence`, ID `14508928592`, SHA-256 `53960f83ef40d4a287a236509a81f44aaa7775bd23935845400586717a4f5dbc`.
- Current `main` after workflow update: `4dd18e66d8236e6864e572516eb5f406cf56bd00`. No application source changed in this commit; only the R1 workflow's metadata and test-count gate changed.
- Status remains: F4-R1 PASS within bounded source and isolated regression scope. Full repository suite NOT VERIFIED. F4-R2/R3 OPEN / NOT VERIFIED. Runtime, deployment, VPS, canonical DB, exchange connectivity and production readiness NOT VERIFIED / NOT CERTIFIED.
