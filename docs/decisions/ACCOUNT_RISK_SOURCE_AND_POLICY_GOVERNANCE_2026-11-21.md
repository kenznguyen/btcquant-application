# Account Equity/Exposure Source and Versioned Risk Policy Governance

Date: 2026-11-21
Repository: kenznguyen/btcquant-application
Branch: main
Status: READ-ONLY SOURCE AUDIT COMPLETE / PAPER SOURCE CONDITIONALLY IDENTIFIED / POLICY GOVERNANCE PROPOSED / PROVIDER NOT AUTHORIZED

## 1. Scope

Static inspection of the current application repository and existing risk-contract evidence only. No database was opened, no runtime or VPS was accessed, no exchange credentials were used, and no source/test/workflow/runtime code was changed.

Current main HEAD at audit: f8a5c0729feb4e8d2501375ea06551a79c517794.

## 2. Account equity/exposure source determination

### PAPER — application-owned account ledger is the candidate authority

The current application contains an account-wide accounting implementation:

- paper_execution/account_equity.py, blob 9971dae4592f07fe7bd2315c0f1ec1daf97af8d1.
- paper_execution/ledger.py, blob 9cc03db8b7506543f9eef2835eb5cb7cda701d6c.
- account_equity.record_account_mark() reconciles Core, AI and LEGACY_UNATTRIBUTED ledger rows; realized PnL, unrealized PnL, fees, funding, active reservations, reserved notional and reserved margin. Non-zero LEGACY_UNATTRIBUTED position is rejected.
- Equity formula: initial PAPER capital + realized PnL + legacy realized adjustments + unrealized PnL - fees - legacy fees - funding.
- Gross exposure is filled absolute exposure plus active/partial reserved notional. LONG and SHORT are not netted.
- ledger.read_account_risk_snapshot() opens SQLite with mode=ro, enables PRAGMA query_only=ON, begins one read transaction, validates required migration checksums, account cutover, mark freshness, funding provenance, daily baseline and ledger/reservation reconciliation.
- The read returns riskReady, account equity, gross exposure, reserved margin, drawdown, daily loss, mark time, dataset version, Kill Switch and positions. Missing cutover/funding evidence or invalid/stale state does not produce a risk-ready snapshot.

Disposition: CONDITIONALLY IDENTIFIED as the authoritative PAPER accounting source in application code. It is not a live exchange balance. It is not the old repository's legacy PaperLedger; the candidate is the current application-owned account ledger.

### Remaining PAPER source verification gaps

- No canonical PAPER database was opened or inspected in this audit. The existence, identity, migration state, cutover, current ledger population and runtime readiness of an actual account database are NOT VERIFIED.
- record_account_mark() receives mark price, candle close time, observed time and dataset version. It does not itself accept or bind the exact market-data source snapshot ID and payload hash used for that mark.
- account_history.record_market_mark_history() can record source, source snapshot ID, dataset version, payload hash and quality status, but the inspected account-mark path does not establish a verified one-to-one binding between the mark consumed by the equity calculation and that provenance record.
- The current read result exposes dataset version and mark timestamp, but not the complete source mark identity/hash chain required by AccountRiskSnapshot V1.
- The current PAPER account identity is a local account row (account_id=1); binding that identity to application account_scope_id, session and fencing generation remains Provider responsibility and must be verified, not inferred.
- The account snapshot code currently returns a dictionary, not the typed AccountRiskSnapshot V1 object.

Therefore this source is suitable as the PAPER accounting authority candidate, but it is not yet a verified AccountRiskSnapshot Provider source. The mark provenance and account/session/fencing binding gaps must be closed before Provider output can set verified=true.

### LIVE — no authoritative source found

Repository code search found no Binance USD-M account-balance/position connector or verified live equity/exposure source. The current account ledger explicitly identifies itself as PAPER and liveTradingSupported=False.

Disposition: LIVE equity/exposure source NOT FOUND / NOT VERIFIED. Do not infer live account equity from PAPER seed capital, market data, or exchange public market endpoints. LIVE remains outside current scope.

## 3. Versioned risk policy storage and publication

### Existing application implementation

- paper_execution/risk_contract.py, blob 7ae74740568e3bcad78acd928896ee363cc62613, stores one account-level policy row in paper_account_risk_contract.
- It canonicalizes JSON, validates the policy schema and SHA-256 digest, supports read-only loading, one-time idempotent provisioning, and explicit compare-and-swap revision using the expected prior contract hash.
- Each revision increments contract_version and writes a corresponding paper_account_risk_contract_audit record.
- PaperLedger consumes the shared persisted contract; per-caller overrides are rejected and order admission reloads the current contract inside its transaction.
- Historical bounded verification: F4-R1 workflow [44469872186](https://github.com/kenznguyen/btcquant-application/actions/runs/44469872186), source HEAD 12a2f53a21a0a9637d264d49f372e7dcf89fc730, job 135376446850, 151/151 PASS. The current risk_contract.py blob SHA matches the blob recorded in that evidence. This historical result does not prove the current full repository HEAD or the new V1 policy adapter.

### Gaps in the existing contract

- Its schema v1 limits are maxDrawdownPct, maxDailyLossUsdt, and maxExposureUsdt. The new VersionedRiskPolicy expects absolute max_drawdown_quote, max_daily_loss_quote, max_gross_exposure_quote, and max_snapshot_age_ms. These semantics cannot be silently mapped: percentage drawdown needs a defined denominator/high-water mark, and snapshot freshness is absent from the old contract.
- pipeline.api.ledger() can provision the initial contract from environment variables (PAPER_MAX_DRAWDOWN_PCT, PAPER_MAX_DAILY_LOSS_USDT, PAPER_MAX_EXPOSURE_USDT). Existing conflicting environment drift fails closed after provisioning, but automatic environment-based initial provisioning is not a sufficient governed publication mechanism for the new policy.
- The current database schema stores the current policy row and audit hashes; it does not retain a complete immutable copy of every historical policy payload in the audit table. Append-only protection of that audit table was not established by this static review.
- The current VersionedRiskPolicy is an immutable in-memory type only; no production configuration loader or publication source exists.

Disposition: the existing SQLite Account/Risk Contract is a useful active-account enforcement mechanism and validated precedent, but cannot be adopted unchanged as the complete authoring/version-publication source for VersionedRiskPolicy V1.

## 4. Recommended governance model

Use a two-stage, single-authority publication model for PAPER:

1. Authoring and approval source — versioned policy documents in this Git repository.
   - Store one immutable policy document per version under config/risk_policies/.
   - Store an active-policy manifest that references an exact policy version, schema version, file path and SHA-256.
   - A policy change is a reviewed Git commit on the existing branch; no environment-variable override and no mutable remote fetch at runtime.
   - The policy document is configuration, not a secret. No API keys or credentials belong in it.
   - Do not create a policy document with numeric thresholds until the owner has selected and approved those values.

2. Operational active copy — application PAPER database.
   - Keep the account-scoped persisted contract as the runtime active-policy record, but evolve it to retain the full canonical policy payload, schema version, policy version, payload hash, source Git commit SHA, activation timestamp, operator/reason and prior version/hash.
   - Preserve every published policy version immutably; use a separate active-version pointer updated transactionally with compare-and-swap.
   - Add database-enforced append-only audit protections and read-only runtime loading.
   - Publish only through an explicit manual operator action from a reviewed repository policy document. No implicit provisioning from environment variables.
   - At admission, resolve one policy snapshot for the account/session and ensure RiskState.risk_policy_version, policy version/hash and account scope all match. Core and AI receive the same policy version.
   - The database active copy is a materialized operational publication, not a second independent authoring source.

This model uses Git commit history/review for policy authorship and the account DB for atomic active-version selection. It avoids runtime dependence on GitHub availability and avoids divergent per-strategy environment values.

## 5. Required contract reconciliation before Provider implementation

The owner must approve the policy schema semantics before any adapter is built:

- Whether drawdown limit is quote-denominated absolute loss or percentage of high-water mark. Current V1 SharedRiskEngine uses absolute quote loss; current persisted contract v1 uses percentage. No implicit conversion is allowed.
- Snapshot freshness limit must be a required explicit policy field.
- Daily loss and gross exposure remain quote-denominated absolute amounts.
- The typed snapshot must expose sufficient verified mark/high-water-mark provenance for the selected drawdown semantics.
- A policy schema migration must preserve historical policy versions and prevent old environment values from silently provisioning a new schema.

No numeric risk thresholds are proposed in this audit.

## 6. Status

| Area | Status |
|---|---|
| Application PAPER ledger source candidate | CONDITIONALLY IDENTIFIED |
| PAPER accounting arithmetic and gross exposure semantics | STATICALLY VERIFIED IN SOURCE |
| Actual PAPER DB identity/cutover/current readiness | NOT VERIFIED |
| Market mark source snapshot/hash binding | GAP / NOT VERIFIED |
| Account/session/fencing binding at Provider source | NOT IMPLEMENTED |
| LIVE exchange account source | NOT FOUND / NOT VERIFIED |
| Existing SQLite risk contract and CAS revision | IMPLEMENTED; HISTORICAL F4-R1 CI PASS |
| Existing contract compatibility with VersionedRiskPolicy V1 | BLOCKED — SEMANTIC/SCHEMA MISMATCH |
| Recommended Git authoring + SQLite active-policy publication | PROPOSED / OWNER APPROVAL REQUIRED |
| AccountRiskSnapshot Provider | NOT IMPLEMENTED |
| Production caller wiring | NOT IMPLEMENTED |

## 7. Explicit boundaries

No database was opened or mutated. No Provider, source adapter, policy loader, migration, test, workflow, runtime caller or exchange connector was implemented. No T0/T1/T2 runtime, VPS, exchange credentials, paper execution, live execution or real orders were accessed or enabled.

Next gate: owner approval of (a) PAPER ledger as the PAPER source candidate subject to provenance/binding remediation, and (b) Git-reviewed policy authoring plus explicit SQLite active-policy publication. LIVE source remains out of scope and unresolved.


## 8. Owner approval — 2026-11-21

The owner explicitly approved both governance decisions:

1. **PAPER accounting authority:** the application-owned Paper Account Ledger is the official equity/exposure source for PAPER, conditional on closing and verifying exact consumed market-mark provenance and account/session/fencing binding. This approval does not authorize `verified=true` until those conditions are implemented and proven. It does not designate a LIVE source.
2. **Risk policy governance:** GitHub-reviewed, versioned policy documents are the authoring/approval source; an explicit manual publication operation materializes the selected immutable policy into the application SQLite active-policy store. SQLite retains full published policy versions and audit history, with transactional compare-and-swap activation. Runtime reads the active persisted policy; environment variables must not automatically provision or override this policy, and runtime must not fetch mutable policy from GitHub.

### Implementation gates still open

- Mark provenance must bind the exact source snapshot ID, source/version, dataset version and payload hash to the precise mark consumed by account-equity calculation, with integrity and atomic-consistency evidence.
- Provider must bind the local PAPER account identity to the requested account scope, session ID and fencing generation and reject mismatches/stale ownership. The snapshot must be built from one consistent read and emitted as typed AccountRiskSnapshot V1 only after every verification gate passes.
- Policy schema reconciliation remains unresolved: existing persisted contract v1 uses percentage drawdown while VersionedRiskPolicy V1 uses absolute quote drawdown. No implicit conversion or numeric thresholds are approved. Snapshot freshness remains an explicit required policy field. Define and test the migration before publication implementation; preserve old history and disable environment-based initial provisioning for the new governed path.
- Actual PAPER database identity/cutover/population/readiness remains NOT VERIFIED. No database was opened or modified as part of this approval record.
- Provider implementation and production caller wiring are NOT STARTED. B2 remains BLOCKED until provenance, binding, policy publication, Provider and caller tests pass and receive the required review.

### Scope boundary

This approval authorizes recording the decisions and proceeding with isolated, application-code-only design/implementation and deterministic tests for the listed gates. It does not authorize opening/mutating any operational database, accessing VPS/T0/T1/T2 runtime, starting services, enabling automatic execution, connecting a live exchange account, or placing paper/live orders. PAPER remains paper-first and on-demand; LIVE remains out of scope.

## Implementation and verification update — 2026-11-21

### Verified source and mark provenance — PASS

- The T0 datasetVersion is recomputed from the canonical source-window payload (venue, market type, symbol, timeframe, window bounds, asOfMs, and all candles); a caller-supplied digest is not trusted.
- M15 coverage and candle continuity are checked. The consumed mark must be the final candle, and its exact close price and close time must match the account mark.
- The typed provenance object validates its complete canonical source window itself, so callers cannot bypass validation by directly constructing the dataclass.
- The immutable consumed-mark row is linked to paper_account_risk_state.last_mark_id in the same SQLite transaction as the equity/exposure update.
- Snapshot reads revalidate the exact mark ID, payload hash, upstream dataset digest, source identity, mark timestamp, and price. Missing or corrupt provenance fails closed.
- The source snapshot ID (datasetVersion) and consumed-mark payload SHA-256 remain distinct values.

### Account, session, and fencing binding — PASS (isolated software contract)

- paper_execution/account_scope_binding.py adds an explicit, immutable mapping from PAPER account_id=1 to one account_scope_id. There is no inferred/default account scope and no automatic migration.
- SQLiteStateRepository.read_active_writer_binding() reads the RUNNING owner session and fencing generation in one read transaction.
- The resolver requires exact account scope, session ID, and fencing generation. Missing mapping, non-RUNNING session, stale owner, or generation mismatch is denied.
- The Provider checks the binding before and after its account snapshot read. A fence change during the read is denied.
- Actual application PAPER database migration was not run; only temporary test databases were used.

### Versioned policy and SQLite CAS — PASS (isolated software contract)

- Git-authored policy schema and manifest schema are defined under config/risk_policies/.
- SQLite publication stores canonical payload, immutable version history, source commit/path/file hash, operator/reason metadata, and an audited active pointer.
- Publication uses a transaction and compare-and-swap against the expected active payload hash. A concurrent two-publisher test proves exactly one publisher wins.
- Environment variables no longer automatically provision risk policy in the pipeline.api.ledger() path.
- PERCENT_HWM publication is rejected until the Shared Risk Engine supports that semantic; only explicit ABSOLUTE_QUOTE drawdown is currently admissible.
- No production threshold values or active policy were selected or published.
- The store records the Git commit and exact source file hash; a separate operator publication action must still verify that the named path and bytes belong to the reviewed GitHub commit before publication. No live GitHub publisher was run.

### Read-only AccountRiskSnapshot Provider — implemented and tested

- Added paper_execution/account_risk_provider.py.
- Provider reads the reconciled PAPER snapshot and active policy from the same read-only SQLite transaction.
- It emits a typed AccountRiskSnapshot, a typed VersionedRiskPolicy, and the verified account/session/fencing binding.
- Missing policy, non-ready ledger, future mark, mismatched provenance, or changed fencing is fail-closed.
- PaperAccountRiskBundle.admission_context() creates one immutable context that can be reused for both CORE and AI proposals. Tests confirm both strategies are evaluated against the same snapshot and policy version.
- Integration test uses a temporary dual-ledger PAPER database and a separate temporary SQLiteStateRepository; it does not access a real account database or VPS.

### CI evidence

- Tested source SHA: a4619ba8ec585e613a235cda446cb32a6546ed1a
- Workflow: https://github.com/kenznguyen/btcquant-application/actions/runs/44865380093
- Job: 136727747289 — SUCCESS
- Test suites: 179 + 179 = 358 PASS
- Artifact: persistent-state-contract-test-evidence, ID 14691124782
- Artifact SHA-256: 388e4152a901750f7504c2429e612211f2a98262310c4d2f7613a98a9bcb100e
- Artifact expiry: 2026-12-05

### Remaining caller integration blocker

The Provider and common Core/AI admission-context boundary are implemented, but the production Core/AI order callers are not yet wired. Repository inspection found:

1. pipeline.api does not instantiate or resolve a production SQLiteStateRepository, nor does it receive the active On-Demand session_id and fencing_generation.
2. RiskState currently exists as a typed contract and test fixture, but no production aggregate reader/writer or authoritative runtime source is wired. This is part of the previously blocked B3 Kill Switch/RiskState persistence work.
3. Existing POST /v1/paper/evaluate still follows the Core-first PaperLedger submission path; AI execution remains disabled. It does not yet invoke the new Provider + Shared Risk Engine as the final admission gate.
4. No actual PAPER DB account-scope migration or active policy publication has been performed.

Do not invent a runtime database path, session identity, fencing generation, or RiskState source. Caller integration remains BLOCKED until the authoritative Persistent State runtime configuration and durable RiskState source are approved and implemented. The Provider itself is software-tested and does not enable execution.