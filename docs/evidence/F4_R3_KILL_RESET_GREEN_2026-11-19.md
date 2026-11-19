# F4-R3 Kill Switch reset/readiness — phase B GREEN evidence

Date: 2026-11-19  
Repository: `kenznguyen/btcquant-application`  
Branch: `main`  
Phase: B — bounded production correction and isolated regression verification

## Approval and scope

The owner explicitly approved F4-R3 phase B after phase-A RED evidence.

Implemented scope:
- `PaperLedger.reset_kill()` validates account-wide readiness and pending paper orders after acquiring the SQLite write lock.
- Account risk validation now accepts an existing SQLite connection, allowing the full authoritative snapshot to be evaluated on the same connection/transaction as the Kill Switch reset.
- The persisted Kill Switch row is validated before any reset update.
- The API no longer treats a legacy/non-Dual-Ledger branch as account-risk ready.
- API reset maps a readiness race discovered inside the transaction to HTTP 409 / `SYSTEM_NOT_READY`.
- Updated the paper API contract and focused regression tests.

Not performed:
- No F4-R1 or F4-R2 production source changes.
- No risk-limit changes, schema migrations, new tables, or dependencies.
- No T0, canonical DB, VPS, runtime, service, exchange or deployment access.
- No paper order submission or live trading.

## Production changes

### `paper_execution/ledger.py`

Blob: `9cc03db8b7506543f9eef2835eb5cb7cda701d6c`

`PaperLedger.reset_kill()` now:
1. Requires explicit acknowledgement and the existing compatibility `ready=True` argument; that argument is not accepted as proof.
2. Starts `BEGIN IMMEDIATE` before reading reset prerequisites.
3. Rejects any `OPEN` or `PARTIALLY_FILLED` row in `paper_orders`, including legacy/unassigned rows.
4. Requires all validated Dual Ledger migrations.
5. Calls `_read_account_risk_snapshot_connection()` on the same SQLite connection and requires `riskReady is True`. Missing, stale, invalid, unreconciled or incomplete account state is normalized to `ACCOUNT_RISK_NOT_READY`.
6. Calls `risk_control.snapshot(connection)` to validate the persisted latch row before clearing it.
7. Clears the latch and inserts `KILL_SWITCH_RESET` audit on the same transaction. An audit failure rolls back the latch update.

The existing read-only public `read_account_risk_snapshot(db_path, now_ms=...)` remains read-only; it now opens its own query-only read transaction and delegates to the shared connection-scoped validator.

### `pipeline/api.py`

Blob: `e60e9800e4735902ec46b3fe927d6108cac5b6c2`

- Missing/invalid Dual Ledger readiness is no longer promoted to READY by the legacy branch.
- Missing DB, invalid migration, read error, missing account risk state and other readiness errors fail closed.
- Candle/order-book preflight remains an additional external readiness gate.
- If account readiness or pending-order state changes after preflight, the transactional Ledger recheck rejects reset and API returns 409 `SYSTEM_NOT_READY`, with the failed check marked false.

### Contract

`pipeline/CONTRACTS.md` blob: `14368ea20d56879b9c9fc6c2eddf07e8c44ab5da`

The reset request contract is now `{acknowledge:true}`; client-supplied readiness is not accepted as evidence. The documented reset gate requires validated migrations, reconciled `riskReady=true`, no pending paper orders, and an atomic latch/audit transaction.

## F4-R3 GREEN matrix

Test file: `paper_execution/test_f4_r3_reset_red.py`  
Blob: `ea87e42b52889ed9fd926f3d647a9b8ca87d22df`  
Eight F4-R3 cases pass:

| Case | Verified behavior |
|---|---|
| Forged direct `ready=True` | Missing account readiness blocks reset |
| Pending paper order | OPEN/PARTIALLY_FILLED blocks reset |
| Legacy readiness fallback | Missing Dual Ledger cutover never reports account risk ready |
| Account risk preflight | `riskReady=False` blocks API reset |
| Direct transactional readiness | Snapshot is evaluated while the write transaction is active |
| API TOCTOU | Pending order inserted after preflight is caught before latch clear |
| Missing Kill Switch state | Missing latch row blocks reset and creates no reset audit |
| Audit failure | Latch update is rolled back atomically |

## Authoritative isolated GREEN run

- Workflow: `.github/workflows/f4-r3-kill-reset-green.yml`
- Workflow blob: `46f0c4ca22278e6b31b76d1325fbbaa05cd8c8b4`
- Workflow/source HEAD: `d1bc142d6a7c73a4bbb6cbfec1a2442a48f32e2a`
- Run: [44488973265](https://github.com/kenznguyen/btcquant-application/actions/runs/44488973265)
- Job: `135439498934`
- Conclusion: **SUCCESS**
- Exact source/test identity preflight: **PASS**
- Test command: F4-R3 reset tests, F4-R2 Kill Switch regression tests, PaperLedger tests, Dual Ledger regression tests, Pipeline API tests.
- Result: **136 tests, 0 failures, 0 errors** (`Ran 136 tests in 2.303s`; `OK`).
- Python: 3.12.16, pinned image digest `sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`.
- Isolation: Docker `--network none`, read-only source, non-root user, dropped capabilities, no-new-privileges, no credentials, no canonical DB mount.

### Exact source identities

| File | Blob SHA |
|---|---|
| `paper_execution/ledger.py` | `9cc03db8b7506543f9eef2835eb5cb7cda701d6c` |
| `pipeline/api.py` | `e60e9800e4735902ec46b3fe927d6108cac5b6c2` |
| `paper_execution/test_f4_r3_reset_red.py` | `ea87e42b52889ed9fd926f3d647a9b8ca87d22df` |
| `paper_execution/test_ledger.py` | `71c7719d3e84be41bb7ca200b50fe6b5ee0f68e9` |
| `pipeline/test_api.py` | `3ddb51d763eb9bef836c5cf85a1ddc471bae0875` |
| `paper_execution/test_dual_ledger_red.py` | `0cf05418940a07a8357ee9d6039325a1efcb16f2` |
| `paper_execution/risk_control.py` | `c8fe573a7a5b0716159e50a678423e402d7df3ba` |
| `paper_execution/risk_contract.py` | `7ae74740568e3bcad78acd928896ee363cc62613` |

### Artifact

- Name: `f4-r3-kill-reset-green-evidence`
- ID: `14511358462`
- Size: 4,869 bytes
- GitHub digest: `sha256:100ae2fecb98f9d6fdf0a5409172d545ad8435f2341ecd81db4f97f186d706f0`
- Downloaded ZIP independently hashed: `100ae2fecb98f9d6fdf0a5409172d545ad8435f2341ecd81db4f97f186d706f0`
- Artifact metadata and unittest log inspected; source identities and 136-test result match the workflow.

## Preservation and adjacent regression gates

| Gate | Run | Result | Evidence |
|---|---:|---|---|
| F4-R1 Account Risk Contract | [44488980998](https://github.com/kenznguyen/btcquant-application/actions/runs/44488980998) | PASS — 151 tests | Artifact `14510979003`, SHA-256 `39e3a220862c4a566a0553ef1cc0ebab9218f47efc05374d729e6d2fe44308f5` |
| F4 Pipeline API/Decision | [44488667805](https://github.com/kenznguyen/btcquant-application/actions/runs/44488667805) | PASS — 42 tests | Artifact `14511966525`, SHA-256 `9680bdee81840be77af7501406bf6ea40c23a7243192bfeecaa451615caea3a6` |
| T0 SQLite API isolated regression | [44488980953](https://github.com/kenznguyen/btcquant-application/actions/runs/44488980953) | PASS | Artifact `14511133089`, SHA-256 `8cbc150673e3741c646848f397bb622e8a0a30f8873ea77c779eede0a19463be` |

F4-R1 production source and F4-R2 production source remain unchanged. R1 and Pipeline workflow source pins were refreshed only because their existing regression modules were adjusted to assert the new fail-closed reset contract. Their isolated workflows passed.

## Exploratory broad-suite result and limitation

An initial broader attempt, run `44488493506` at source HEAD `dbc7839d21bbf3de6a51c780b43e5c92bc34ac94`, executed 237 tests and ended with **3 errors**:
- `paper_execution.test_risk_control.PersistentRiskControlTest.test_new_database_starts_unpaused_and_not_killed`: expected legacy unlatched behavior conflicts with F4-R2's fail-closed missing-state behavior.
- Two `paper_execution.test_daily_baseline_persistence` tests attempted to mutate the immutable `MappingProxyType` returned by the Ledger.

These cases were not modified as part of F4-R3. They are not counted as passing. The final R3 gate was deliberately limited to the five directly relevant modules and passed 136/136. The dedicated F4-R2 seven-case suite is included in that final gate. The two daily-baseline tests and the separate legacy `test_risk_control` module remain **NOT VERIFIED / OUTSIDE THIS APPROVAL**.

## Review and final status

Scoped static review checked:
- reset ordering and SQLite `BEGIN IMMEDIATE` lock before authoritative account/pending-order reads;
- complete migration and account-risk contract validation;
- exact boolean readiness rather than truthy coercion;
- validation of persisted Kill Switch state;
- atomic latch clear + audit rollback;
- API fail-closed legacy behavior and 409 mapping;
- no schema, dependency, T0 or runtime changes.

Statuses:
- F4-R3 production correction: **PASS**.
- F4-R3 focused matrix: **PASS 8/8**.
- Combined R3/F4-R2/Ledger/Dual Ledger/API regression: **PASS 136/136**.
- F4-R1 regression: **PASS 151/151**.
- Pipeline API/Decision regression: **PASS 42/42**.
- T0 SQLite API regression: **PASS**.
- Exploratory 237-test broad run: **BLOCKED / 3 errors** as detailed above.
- Runtime, VPS, canonical DB, exchange, paper/live orders: **NOT ACCESSED**.
- Production operational readiness / live trading: **NOT CERTIFIED**.

## Next gate

F4-R3 code correction is complete under the approved scope. Do not infer runtime or trading readiness. Any separate effort to repair the three broader-suite errors or to activate runtime requires its own bounded scope and approval.
