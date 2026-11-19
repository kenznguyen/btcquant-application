# F4-R1 Account Risk Contract — implementation and isolated verification

Date: 2026-11-19  
Repository: `kenznguyen/btcquant-application`  
Branch: `main`  
Verified source/workflow HEAD for R1: `a04faf10f96eb917a2e6bdf2ca7f4c632d78043a`

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
- `pipeline.api.ledger()` provisions the initial contract from the shared environment configuration only after dual-ledger readiness checks. Repeated identical config is idempotent; environment drift against an existing contract is fail-closed. API quality reporting reads the persisted contract rather than independently parsing environment values.
- API tests now use the explicit versioned contract update operation when simulating a risk-policy change.

## Source identities at verified HEAD

| File | Blob SHA |
|---|---|
| `paper_execution/risk_contract.py` | `7ae74740568e3bcad78acd928896ee363cc62613` |
| `paper_execution/ledger.py` | `5a04bbc27904dfab6ab139c6d5a47e538611405b` |
| `pipeline/api.py` | `986424f2f3631de367e56b33e50d47f4c0a4f263` |
| `paper_execution/test_f4_r1_account_contract.py` | `a8b8be332e2b8e0ec9d2707b0c7cb7334ca0e851` |
| `paper_execution/test_risk_limits.py` | `3dd3afb6e7b7d361829bae0355412c468cbbc313` |
| `paper_execution/test_ledger.py` | `d352303e2088cbba0538ac4709f92ab74952a4e9` |
| `paper_execution/test_dual_ledger_red.py` | `0cf05418940a07a8357ee9d6039325a1efcb16f2` |
| `pipeline/test_api.py` | `5481c3072c79891161f992299783a9ba5879f955` |
| `pipeline/test_decision.py` | `6781f26d66635f56662a627bdd3b4a63f26c1f28` |
| `.github/workflows/f4-r1-account-risk-contract.yml` | `1dcb951be8a15785e199717e4415b95a206ca8cc` |
| `.github/workflows/f4-pipeline-core-first-isolated.yml` | `62f60ea074784774855830ad4f85a04aed6d8de6` |

## TDD and CI evidence

### RED
- Regression specification was added before implementation.
- Run [44466409033](https://github.com/kenznguyen/btcquant-application/actions/runs/44466409033), job `135365143505`, confirmed the contract implementation was absent and the new cases failed. This was an intentional RED run, not final verification.

### R1 GREEN — authoritative
- Run [44468297408](https://github.com/kenznguyen/btcquant-application/actions/runs/44468297408), branch `main`, exact workflow/source HEAD `a04faf10f96eb917a2e6bdf2ca7f4c632d78043a`.
- Job `135371303499`: SUCCESS.
- Python `3.12.16`; pinned image `python:3.12.16-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`.
- Command: `python -m unittest -v paper_execution.test_f4_r1_account_contract paper_execution.test_risk_limits paper_execution.test_ledger paper_execution.test_dual_ledger_red pipeline.test_api pipeline.test_decision`.
- Result: `Ran 143 tests in 1.891s`; `OK`; 143/143 passed, 0 failures.
- Artifact: `f4-r1-account-risk-contract-evidence`, ID `14502489155`, SHA-256 `587649aafbe745b2fdad1485e2f7c6bfac3a382fdb3ba5987131e772e22ffbaa`.
- Workflow verified the exact test/source blob SHAs above. The test container ran with `--network none`, read-only source mount, non-root user, no credentials and no canonical database mount.

### API / Decision regression
- Run [44468155810](https://github.com/kenznguyen/btcquant-application/actions/runs/44468155810), exact workflow/source HEAD `7039524bd21c3320d8670be6177fd917be00bbdb`.
- Job `135370846697`: SUCCESS.
- Result: `Ran 41 tests in 0.176s`; 41/41 passed, 0 failures.
- Artifact: `f4-pipeline-api-decision-evidence`, ID `14502719378`, SHA-256 `75adca9397018fea9b970c8673334f120b348c14c1faed3ed655a9f07cfa0e02`.
- The API workflow checked out the exact source, verified source blobs, confirmed Python 3.12.16 and a loopback-only network probe, then ran the API/decision modules in a network-disabled Docker container.

## Review and limitations

- Correctness: covered initial provisioning, idempotent provisioning, shared Core/AI reads, caller override rejection, missing-contract admission denial, tamper detection, explicit revision, stale-hash rejection, audit recording and existing Ledger/API regressions.
- Architecture: account contract is persisted once and consumed by both strategy ledgers; policy updates require an explicit expected hash and reason. No per-strategy risk-limit source remains in the paper API path.
- Security: SQL uses parameterized statements; contract content is canonicalized and hash-checked; read-only lookup opens SQLite in read-only URI mode; tests run without network/secrets/canonical DB.
- Performance: one small contract read is performed inside each order-admission transaction. No external dependency was added.
- Full repository test suite: NOT VERIFIED. The 143-test result is the bounded impacted-module suite, not the full repository suite.
- F4-R2 and F4-R3: remain OPEN / NOT VERIFIED; their separate RED specifications were not included in the R1 suite.
- Runtime/deployment/VPS/canonical DB/exchange/trading: NOT ACCESSED / NOT VERIFIED. No real orders were placed.
- Paper path policy unchanged: Core-First only; AI offline research only; live trading prohibited.

## Status

- F4-R1 account risk contract: **PASS** within the bounded source and isolated regression scope.
- API/Decision regression: **PASS** (41/41).
- Full repository suite: **NOT VERIFIED**.
- F4-R2/R3: **OPEN / NOT VERIFIED**.
- Runtime, deployment and production readiness: **NOT VERIFIED / NOT CERTIFIED**.

## Next step

Preserve this evidence and handoff. Any F4-R2/R3 work, full-repository test expansion, runtime/database access, deployment, AI execution or live trading requires a separate bounded approval.
