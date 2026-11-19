# T0 Source-to-Target Parity Audit — 2026-11-19

## Scope and method

Read-only comparison of T0 test/documentation assets between:
- Source: `kenznguyen/btcusdt-telegram-signals2`, ref `feature/t0-centralized-data-feeder-p1-20261101`.
- Target: `kenznguyen/btcquant-application`, ref `main`.

The source branch was inspected by path and per-file Git blob SHA. This report does not claim a source branch commit SHA that was not independently resolved. Target HEAD at the start of this audit: `32b865b1ff6f05338354483eb69f7f61539e1036`.

No source/target code, tests, workflows, canonical data, runtime, VPS or database were changed. No workflow was dispatched.

## Test disposition

### A. Byte-identical source-to-target tests — KEEP; no recopy

| Test | Source blob | Target blob | Result |
|---|---|---|---|
| `test_api.py` | `49df7e0bec12908adae67f18a4aa19063e461093` | same | BYTE-IDENTICAL |
| `test_storage.py` | `b2635f575323187f936360d033b4fc630d8138e0` | same | BYTE-IDENTICAL |
| `test_store.py` | `df1554a365ff5d619498dc4b07f7a1a435e761df` | same | BYTE-IDENTICAL |
| `test_fenced_store.py` | `0573d0728f3e62a95b8d2a4f16359e33dd4789b4` | same | BYTE-IDENTICAL |
| `test_feeder_health.py` | `80e0b7d042c821d4814d626b69c3196853dc49d9` | same | BYTE-IDENTICAL |
| `test_feeder_retry.py` | `0c556f2954188e2bf3bd643aa217f71b9bd8ba2c` | same | BYTE-IDENTICAL |
| `test_feeder_scheduler.py` | `695c53548c58763cffecc86626171f6a691e75fd` | same | BYTE-IDENTICAL |
| `test_controlled_ingestion_acceptance.py` | `92c76fea839858f128ed228ac25b36b6bb8ec375` | same | BYTE-IDENTICAL |
| `test_t0_controlled_ingestion_acceptance.py` | `a26d9f44012452fa663553e292e273d68d625e88` | same | BYTE-IDENTICAL |
| `test_feeder_lease.py` | `9e3cef256ed55c9784d02e21f9ac30cf723c31b0` | same | BYTE-IDENTICAL |
| `test_feeder_recovery.py` | `034c9e8f157b0750aaf856c122b00ef96c808ee8` | same | BYTE-IDENTICAL |

These files already exist in the target. Do not copy them again.

### B. Adapted or intentionally distinct tests — KEEP TARGET VERSION

| Test | Source blob | Target blob | Disposition |
|---|---|---|---|
| `test_write_gateway.py` | `2c55dff1729cdfd11bd0ef2188e1e41756ed7692` | `231f5e0184821c78cda0ca5d03625f71fd3a4b71` | Target preserves existing cases and adds F1 missing/malformed lease-schema regressions plus target-specific Python `-S` fixture adaptation. Keep target version; do not replace with source. |
| `test_sync.py` | `319e084d9c0a9c5b0319e9bb7d1f93a930564dc8` | `7621c85a4c7eb2ad233de94da89e6fbb411ea534` | Byte-different. Target already has a distinct test version and aggregate coverage. No blind overwrite; retain difference pending a dedicated semantic diff only if a concrete contract gap is found. |
| `test_feeder_lifecycle.py` | `5797d51e3165721863ceacb1fac76f44055f18a7` | `f10de15b11ca00f6a4946c3877062cfb5dbd1442` | Different test modules. Target's existing lifecycle suite is retained; source's 34 service-composition/lifecycle tests were preserved separately as target `test_feeder_service_lifecycle.py`, blob `590c29a0fbf553d19582912a113a92bb74da083f`. Do not overwrite either suite. |

### C. Target-specific tests — KEEP

- `test_initialize_sqlite.py`: target empty-only initializer contract; tests disposable temporary paths only.
- `test_feeder_service_lifecycle.py`: separately preserved source lifecycle/service-composition contract suite, with target fixture adaptation.
- Other selected SQLite tests are already included in the explicit 191-test aggregate allowlist.

These are not reasons to import more source files.

### D. Source-only / separately gated — DO NOT MIGRATE INTO SQLITE ACCEPTANCE

- `market_data/binance_connectivity_probe.py`: manual public REST/WebSocket diagnostic; requires explicit network approval and is not an offline contract test.
- Process/SIGKILL restart and systemd/VPS integration: operational runtime assurance; not part of the SQLite-only test gate.
- PostgreSQL/TimescaleDB migrations, provider-specific tests and dependencies: optional backend parked/not qualified.
- Kraken Spot tests/modules: separate research domain, not canonical Binance USD-M BTCUSDT.
- T0-to-T2 E2E/parity: cross-layer integration; separate approval.
- Legacy dashboard health API tests: retired/legacy application boundary.
- Historical RED tests and superseded workflow fixtures: preserve as source history/evidence; do not count as active acceptance.

The source scope index also identifies a separate Evidence Object/Checkpoint assurance workstream. Preserve it in its own assurance scope; do not inflate the minimum SQLite acceptance denominator with those requirements.

## Documentation disposition

| Document | Source state | Target state | Decision |
|---|---|---|---|
| `market_data/README.md` | Contains historical TimescaleDB workflow, Codemagic fallback and legacy integration/run instructions | Target README is rewritten for SQLite-first scope, current lock, 191-test gate and exclusions | KEEP target adaptation; do not copy source README |
| `docs/T0_ACTIVE_SCOPE_INDEX.md` | Source index dated 2026-11-10, reflects earlier governance and runtime scope | Target index dated 2026-11-19, explicitly scopes selected SQLite-first target | KEEP target index; source is historical context only |
| `docs/PROJECT_SESSION_HANDOFF.md` | Source handoff is an extensive historical record; its 2026-11-11 governance override differs in wording from target's current no-automatic-deletion boundary | Target handoff records current SQLite-first migration and evidence | Do not copy source handoff wholesale. Retain source history; use target handoff and current explicit approvals as authority |
| Source T0 progress/runtime/probe reports | Mix of historical runtime observations and support diagnostics | Selected evidence is linked from target docs; no runtime proof is claimed | Preserve at source; link only when a specific historical claim is needed |

The target README was read in full. Its verification section points to the SQLite-only aggregate and correctly excludes PostgreSQL, network connectivity, production startup and VPS/runtime claims. No stale TimescaleDB workflow instructions were found in the target README.

## Evidence and status

- Target selected SQLite aggregate: run [44507725020](https://github.com/kenznguyen/btcquant-application/actions/runs/44507725020).
- Exact tested target SHA: `42c8172a4b4b0234fa50e64eb6172f970f45ab66`.
- Result recorded by the target handoff: **191/191 PASS**.
- This audit itself was read-only and did not rerun tests. The 191/191 result is evidence for the exact tested SHA above, not a new run on the audit/report commit.
- No workflow run or artifact was created by this audit.
- Source-to-target disposition for the inspected SQLite test set: **PASS for presence and identified blob parity/adaptation; PARTIAL for semantic parity of the byte-different sync test pending need-based review**.
- Documentation disposition: **PASS for target-specific README and scope index; historical source handoff intentionally not copied**.
- Overall T0 parity: **PARTIAL**, not full repository parity and not production certification.

## Next bounded step

No additional source files should be copied now. If future review is needed, perform a focused semantic diff of source/target `test_sync.py` only against a named contract gap. Keep PostgreSQL, Kraken, connectivity, process/systemd/VPS, T0-to-T2 and legacy app tests separately gated. Update the target handoff with this report's commit/SHA; do not change source branch, workflows, canonical data or runtime.


## Semantic review of `test_sync.py` — 2026-11-19

### Compared artifacts

- Source test blob: `319e084d9c0a9c5b0319e9bb7d1f93a930564dc8`.
- Target test blob: `7621c85a4c7eb2ad233de94da89e6fbb411ea534`.
- Source implementation `market_data/sync.py` blob: `e7ad4e6f2074225957b01f74abb0befe37675ea2`.
- Target implementation `market_data/sync.py` blob: same `e7ad4e6f2074225957b01f74abb0befe37675ea2`.

### Finding

The test difference is additive and narrowly scoped:
- Target imports the existing `Candle` model.
- Target adds `test_second_page_write_conflict_rolls_back_page_without_removing_first_page`.
- The pre-existing source test cases and assertions remain present in the target version; no source test behavior was removed in the reviewed diff.
- Source and target `sync.py` implementations are byte-identical.

The added test seeds a conflicting closed candle, returns a valid new candle followed by the conflicting candle on page 2, and asserts:
1. Page 1's 1,000 committed candles remain.
2. The new candle earlier in failed page 2 is rolled back.
3. The pre-existing conflicting candle is not overwritten.
4. The conflict raises `ValueError`.

The target `SQLiteWriteGateway.write_batch` implementation uses `BEGIN IMMEDIATE`, performs writes inside one transaction, commits only after lease revalidation, and rolls back on every exception. The new test directly exercises this page-level atomicity contract through `sync_window`, which commits each fetched page using one `write_batch` call. It is not a redundant implementation-detail test: it protects the externally relevant boundary between a previously committed page and a later failed page.

### Verdict

**SEMANTIC REVIEW PASS.** Keep the target `test_sync.py` as-is. Do not copy the source version over it. No code/test change is needed.

This was static source review only. No test was executed and no workflow was dispatched. The existing 191/191 aggregate evidence remains tied to exact tested SHA `42c8172a4b4b0234fa50e64eb6172f970f45ab66`.

### Updated disposition

- SQLite test parity for the reviewed sync contract: **PASS**.
- No remaining test-only source file is currently justified for copying into the target by this review.
- Overall scope remains deliberately narrower than full source-repository parity; separately gated runtime, PostgreSQL, Kraken, connectivity and T0→T2 work remain excluded.
- Production readiness remains **NOT CERTIFIED**.
