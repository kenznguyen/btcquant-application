# PAPER_DB Isolation and Core Runtime / F4 Integration Plan — 2026-11-20

## 1. Scope and disposition

This increment separates the application Paper Ledger from the independent T0 canonical candle database and records the next Core Runtime integration boundary.

- Target repository: `kenznguyen/btcquant-application`
- Target branch: `main`
- Code baseline before this increment: `54ab5e3b36c079d698c220c6c3481ab01b203c4d`
- Current target HEAD at plan creation: `ded86af644edd3cd0b38ce3ffd9a028213db00e4`
- Source/reference repository: `kenznguyen/btcusdt-telegram-signals2`
- Source/reference branch: `feature/core-operational-proof-20261112`
- Exact source HEAD: `e6606e28a696374f31cd6db1ec0a1372d942d64d`

Disposition:
- PAPER database separation: **PASS** — implemented and covered by isolated F4 regression workflows.
- Core Runtime / F4 integration design: **PLAN COMPLETE** — static dependency and boundary analysis only.
- Core Runtime code migration: **NOT STARTED**.
- Core Runtime execution or paper submission: **NOT AUTHORIZED by this plan**.
- T1 Provider: **PAUSED**; no provider, network client, endpoint, or runtime activation is authorized.
- AI execution: remains disabled; no AI ledger admission or AI paper order is enabled.
- Live trading: prohibited.

## 2. PAPER_DB isolation contract

### 2.1 Database ownership

The application now has two explicit SQLite ownership domains:

| Purpose | Environment variable | Owner | Permitted access |
|---|---|---|---|
| Canonical BTCUSDT candles | `MARKET_DATA_DB` | T0 | T0 storage factory / read-only candle contract |
| Paper account, ledgers, risk, Kill Switch, audit, equity, write budget | `PAPER_DB` | T2 application | Paper API / Paper Ledger |
| T0 feeder lease | `T0_FEEDER_LEASE_DB` | T0 | T0 lease owner only |

Recommended layout:

```text
.data/
  t0/
    market-data.sqlite3
    feeder-lease.sqlite3
  paper/
    paper-ledger.sqlite3
```

The paths must resolve to different files and inodes. Separate directories are recommended for operational clarity. T0 remains an independent data asset; this change does not copy, migrate, open, or rewrite a canonical T0 database.

### 2.2 Enforced path checks

New module: `paper_execution/database_paths.py`

Blob SHA: `aa813461d607069872960f1d55d6b29667a87642`

`resolve_paper_db_path()` is a path-only validator. It does not create directories, files, tables, or SQLite connections. It rejects:

- Missing or blank `PAPER_DB`.
- A Paper path that resolves to `MARKET_DATA_DB`.
- A Paper path that aliases `T0_FEEDER_LEASE_DB`.
- Same-file aliases detected through `os.path.samefile` (including hard links).
- Canonical path aliases such as `sub/../file`.
- A symlink at the final `PAPER_DB` path.
- Non-file paths and missing files when `require_exists=True`.
- A configured legacy `PAPER_TRADING_DB` value that does not resolve to the same Paper path.

The API requires an existing Paper database. It does not silently create a new account when a Paper endpoint is read or written. Explicit local initialization uses `python -m paper_execution --db "$PAPER_DB"`; the CLI requires `PAPER_DB`, checks that `--db` resolves to it, and applies the same T0 alias checks.

### 2.3 API routing

`pipeline/api.py` now resolves all Paper-owned storage through `PAPER_DB`:

- Paper Ledger construction and submission.
- Account Risk Contract reads/provisioning.
- Core and strategy-ledger snapshots.
- Kill Switch and reset readiness.
- Paper write-rate budget.
- Account equity and marks.
- Paper audit history.
- Quality reporting of shared risk limits.

T0 candle reads remain behind `market_data.storage.create_store_from_env()` and the existing Candle Contract. The API imports `candle_query` from `market_data.api_contract`, the current contract module used by the FastAPI T0 adapter. The obsolete `market_data.api` import was removed; no candle schema or query semantics were changed.

The API module has no direct `MARKET_DATA_DB` access. The path validator reads the T0 environment values only to reject aliases; it never opens the T0 database.

### 2.4 Relevant target blobs

| Path | Blob SHA |
|---|---|
| `paper_execution/database_paths.py` | `aa813461d607069872960f1d55d6b29667a87642` |
| `pipeline/api.py` | `2c5c35951dbe902e2553ad186bedaf0ca22b29e0` |
| `pipeline/test_api.py` | `f665944247f63ddc4c135099a91ad0637b02d597` |
| `paper_execution/test_database_paths.py` | `36b45c10c58d79eb84c5c3a072e15131c05d036d` |
| `paper_execution/__main__.py` | `91369f314e0c047fb6f79b91e9256d119a8654b4` |
| `paper_execution/test_ledger.py` | `b1b170bd890ec2cc64bf70079651f1fbf1274573` |
| `paper_execution/test_f4_r3_reset_red.py` | `c98ead20d50497dd668673a38bb83359ea0687a7` |
| `paper_execution/README.md` | `2a9cd6b6e9d714c1ac8483e2fc89bf54763549bc` |

The existing target `paper_execution/ledger.py`, `risk_control.py`, and `risk_contract.py` were not rewritten in this increment. F4 account-risk and Kill Switch semantics remain controlling.

## 3. F4 verification evidence

### 3.1 TDD RED evidence

The focused regression specifications first reproduced the storage-boundary defect before implementation:

- F4 Pipeline RED run: [44685167233](https://github.com/kenznguyen/btcquant-application/actions/runs/44685167233), commit `cb3317c0a46625c03afc24a9bd6b3b19b0504460`. The 44-test suite exposed Paper state being written/read through the T0 path and failure to reject a PAPER/T0 path alias.
- F4 R1 RED run: [44685167199](https://github.com/kenznguyen/btcquant-application/actions/runs/44685167199), same commit. The path-guard module was not yet implemented and the API isolation regressions failed.

These RED runs are historical test-first evidence only, not final status.

### 3.2 GREEN evidence

All three final isolated gates passed against the exact code blobs listed above. They use Python 3.12.16, a network-disabled container, no credentials, and no canonical database mount.

| Gate | Workflow run | Result | Test count | Artifact ID | Artifact SHA-256 |
|---|---|---|---:|---:|---|
| F4 Pipeline API / Decision | [44686288070](https://github.com/kenznguyen/btcquant-application/actions/runs/44686288070) | PASS | 44 | `14606367905` | `1c9ac26fa5779bc6e49bc06f2631182d0a3ae7da6940286cdf232f4878c85471` |
| F4 R3 Kill Reset | [44686288058](https://github.com/kenznguyen/btcquant-application/actions/runs/44686288058) | PASS | 145 | `14605749902` | `e9c7e65fc1d8b99f901afe6cfb18d2b247bd70247ac7cd079bc6b3297be69996` |
| F4 R1 Account Risk Contract | [44686406898](https://github.com/kenznguyen/btcquant-application/actions/runs/44686406898) | PASS | 160 | `14606572771` | `77b83d89b647610a0c09652de08b0a25b34406e6b9279c513664a82f74d2bd45` |

The R1 workflow count gate was updated to 160 after adding seven path-guard tests and two API isolation tests. Its final run is the authoritative R1 result. The workflow-only count correction did not change application code.

## 4. Core Runtime source inventory and dependency findings

The source branch at exact HEAD `e6606e28a696374f31cd6db1ec0a1372d942d64d` contains 33 files under `core_runtime/`. The target repository currently has no `core_runtime/` or `freqai_bridge/` directory. Source code remains read-only reference material; no source files were copied.

Important source module identities:

| Source module | Source blob SHA | Finding |
|---|---|---|
| `core_runtime/input_bundle.py` | `19fb3065da1e7d40c8b4376fe3b51e11c8cc8f87` | Bundle validation; imports `rfc8785` and the T1 book contract |
| `core_runtime/bundle_inputs.py` | `f78ebde30413a3329063a2c68c457fe862a50c5e` | Normalizes M15/H1 and order-book inputs |
| `core_runtime/bundle_provider.py` | `9d67f1600d4177e6f9756e366af6ef9319b27c19` | Injected T0/T1 clients; reads Paper risk and strategy state |
| `core_runtime/preflight.py` | `3e179b75c09f1a0e1dc3bd8c595cda5afc9bc86f` | Read-only account readiness; has source-specific path guard |
| `core_runtime/paper_ledger_preflight.py` | `e5d4b26bc1a48a765d16a8cd6708dfdc83b12a88` | Read-only Paper readiness gate |
| `core_runtime/one_shot.py` | `0bc72d0069880f5445a9d329c0cc660f67838197` | Core producer preview and optional direct Ledger submission |
| `core_runtime/continuous_runner.py` | `a654d03bc2332eb14c0c2498a80882691920825c` | Continuous loop and journal integration |
| `core_runtime/runtime_factory.py` | `b2dbd2efe0076ad5e831682caea0bd5e4a4f8bd6` | Builds T0 and T1 HTTP clients; cannot be migrated unchanged |
| `core_runtime/orderbook_http.py` | `89e5129eea4c9e7ceaa4439a546daf112d15c3e3` | T1 HTTP client; imports `requests` |
| `core_runtime/orderbook_contract.py` | `1620c9f21b1f3df3c2fb65833f2afd80374bf6a5` | Pure T1 snapshot validator; no provider activation by itself |
| `core_runtime/ledger_path_guard.py` | `f5b260165de7a5dd840f6d53a0e5ac59ee3ab328` | Source path isolation; target helper now provides the canonical PAPER path check |
| `freqai_bridge/http_candles.py` | `1f430c6d3a762deab9342e42072824661df3bf96` | T0 read-only HTTP client; imports `requests` |

The source runtime has two third-party dependency requirements visible in the reviewed import closure:

- `rfc8785`: canonical JSON used by bundle identity, bundle validation and one-shot logic.
- `requests`: T0 HTTP candle client and T1 HTTP order-book client.

The target has a dedicated FastAPI T0 lock but no Core Runtime dependency lock containing these packages. A dedicated, hash-pinned Core Runtime dependency closure is therefore required. Do not add these packages to the T0 lock or global dependencies without a separate dependency review.

## 5. Required F4 Account Risk Contract integration

The target F4 contract remains authoritative. Core Runtime must integrate with the target APIs rather than copy the source simulated-account risk model.

Target contract and ledger interfaces:

- `paper_execution.risk_contract.load_account_risk_contract(connection)`
- `paper_execution.risk_contract.read_account_risk_contract(PAPER_DB)`
- `paper_execution.ledger.read_account_risk_snapshot(PAPER_DB, now_ms=...)`
- `paper_execution.ledger.read_snapshot(PAPER_DB, strategy_id="STRATEGY_CORE")`
- Target `PaperLedger.submit(...)` as the final transactional admission boundary.

Required behavior:

1. Resolve `PAPER_DB` only through `resolve_paper_db_path(require_exists=True)`. If source config retains `ledger_path`, it must canonicalize to the same path; it must not override the environment or point at T0.
2. Preflight is read-only. It may inspect the persisted F4 contract, account-risk snapshot, Core ledger snapshot, pending orders, and Kill Switch. It must not provision or update the risk contract.
3. Missing, corrupt, hash-mismatched or unavailable Account Risk Contract must fail closed.
4. Require `mode=PAPER`, `liveTradingSupported=false`, `riskReady=true`, `killed=false`, and `paused=false` before a new ENTRY/DCA cycle.
5. Use the target Account Equity and reservation state. Do not accept a second `risk_limits` object from Core Runtime config or environment.
6. Final ENTRY/DCA admission must execute through target PaperLedger and its transaction-bound F4 contract/risk checks. Core Runtime preflight is not a replacement risk engine.
7. Keep Core and AI ledger ownership separate. This integration scope is Core-only; AI execution stays disabled.

### Source behavior that must not be copied unchanged

Source `core_runtime/one_shot.py` detects a simulated account through `paper_execution.simulated_equity.is_simulated_account`, reads a source simulated capital contract, and conditionally passes `simulated_contract_bytes` or `risk_limits` into `PaperLedger`.

The target does not contain that source simulated-equity module and already has the F4 Account Risk Contract. Do not import the source simulated-equity or simulated-origin code blindly, and do not pass a parallel risk-limit object into target PaperLedger. Reconcile the source simulated capital origin/seed invariants separately: F4 risk limits alone do not prove all simulated-capital provenance requirements.

Replace source `ledger_path_guard.py` with the target `paper_execution.database_paths.resolve_paper_db_path` contract (or a thin wrapper over it); do not maintain two independent path-validation implementations.

## 6. T1 Provider isolation — explicit non-activation boundary

Source `runtime_factory.py` currently requires:

- `T0_CANDLE_API_BASE_URL`, `T0_CANDLE_API_TOKEN`, `T0_CANDLE_MAX_LAG_MS`
- `T1_ORDERBOOK_API_BASE_URL`, `T1_ORDERBOOK_API_TOKEN`

It constructs both `CandleHttpClient` and `OrderBookHttpClient`. That factory must not be copied or invoked unchanged while T1 Provider remains PAUSED.

For the initial Core Runtime integration:

- No `T1_ORDERBOOK_API_BASE_URL` or T1 token is configured or read.
- No `OrderBookHttpClient` is constructed.
- No T1 HTTP request, socket connection, retry, provider process or collector activation occurs.
- Bundle tests inject a deterministic in-memory order-book fixture through the existing provider interface.
- Without an approved production T1 snapshot provider, production bundle readiness remains WAIT/BLOCKED. Do not substitute stale, synthetic or venue-fallback data.

T1 provider/transport integration requires a separate owner approval and separate contract, dependency, security and workflow review.

## 7. Staged implementation sequence

| Stage | Scope | Required evidence | Execution boundary |
|---|---|---|---|
| M2.1 | Migrate Core Runtime pure validators and adapter interfaces; replace source path guard with target PAPER_DB helper | Exact source-to-target manifest, dependency closure, import tests | No API route, no runtime |
| M2.2 | Adapt read-only preflight to F4 Account Risk Contract and target Core ledger snapshot | Missing/tampered contract, risk-unready, Kill Switch, paused, pending-order, T0 alias regressions | Read-only only |
| M2.3 | Integrate T0 Candle HTTP client and Bundle V1 using injected T1 fixture | Network-disabled fixture tests, Candle Contract parity, immutable bundle digest | No T1 provider |
| M2.4 | Core producer preview through `one_shot(submit=False)` or an equivalent preview adapter | Core signal parity, PAPER_DB byte-identity before/after, no AI execution | Preview only |
| M2.5 | PaperLedger F4 admission adapter | Contract hash, account-wide equity, reservation and 1% order-margin regressions | Requires separate explicit paper-execution approval |
| M2.6 | Continuous runner / runtime factory | Lifecycle, restart, idempotency, journal and kill/reset evidence | Not authorized now |
| M2.7 | T1 production snapshot provider | Separate T1 owner approval and provider verification | Not authorized now |

Do not migrate the 33-file `core_runtime/` tree as a bulk copy. Classify files individually. The T1 HTTP client and source runtime factory are excluded from the initial integration; the continuous runner and CLI remain dormant. The T0 HTTP candle client is a selective migration candidate only after dependency-lock review.

## 8. Test and review gates for the next increment

Required tests before any Core Runtime code migration is proposed:

- PAPER_DB missing, same path, normalized alias, symlink, hard-link and T0 lease alias all fail closed.
- F4 Account Risk Contract missing, tampered, hash-invalid and contract-version conflict all block Core admission.
- Account equity unavailable, stale mark, funding provenance incomplete, legacy unattributed exposure, pending reservation, Kill Switch killed or paused all block new ENTRY/DCA.
- Preflight and bundle preview leave PAPER_DB bytes unchanged.
- Core snapshot reads only `STRATEGY_CORE`; it cannot consume AI ledger state as Core-owned position state.
- T0 candle client has no direct SQLite fallback and no synthetic/venue fallback.
- T1 test fixture is injected; tests assert no external network/socket activity.
- Final PaperLedger admission is the only authority for new exposure and uses the persisted F4 contract within the target transaction.

Every test/workflow must record exact source SHA, blob identities, run ID, artifact ID/digest, PASS/BLOCKED status and residual limitations.

## 9. Current boundaries and next action

- T0 canonical SQLite: not accessed or modified by this increment.
- T1 collector/provider: not accessed or activated; remains PAUSED.
- Core Runtime: source inventory only; target migration not started.
- Account Risk Contract: target F4 remains authoritative.
- AI execution: disabled; no AI Ledger submission.
- Paper execution: PAPER_DB storage isolation is implemented and regression-verified; this does not authorize Core Runtime submission.
- Live orders/exchange credentials: prohibited and not used.

Next permitted work: M2.1 read-only dependency closure and per-file migration manifest for Core Runtime, followed by an explicit review of the F4 adapter design. Do not copy or activate runtime code in that increment.
