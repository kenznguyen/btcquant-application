# T0 F1 SQLite Regression Parity — 2026-11-19

Target repository: `kenznguyen/btcquant-application`
Target branch: `main`
Source repository: `kenznguyen/btcusdt-telegram-signals2`
Source branch: `feature/t0-centralized-data-feeder-p1-20261101`
Source audited HEAD: `c0f48b8910655fdb40d14214ad048b1d3cfa7fe9`
Target tested HEAD: `b2bb35400ea1bb4fd0c9a54737ebdab5b6b8a838`

## Approval and bounded scope

Owner approved the F1 Regression Parity increment on target `main`:
- Add only the two missing regression cases to `market_data/test_write_gateway.py`: malformed `feeder_leases` schema rejection and SQLite dependency closure under Python `-S`.
- Preserve all target-only tests and behavior.
- Do not change production T0 code unless a demonstrated behavior gap is found.
- Run a dedicated, isolated SQLite write-gateway regression workflow and record exact-SHA evidence.

No PostgreSQL/TimescaleDB, dependency manifest, T1/T2, paper consumer, runtime/lifecycle, canonical database/data, VPS, deployment or trading behavior was approved.

## Source-to-target provenance

| Item | Source | Target |
|---|---|---|
| Source code HEAD | `c0f48b8910655fdb40d14214ad048b1d3cfa7fe9` | Target tested HEAD `b2bb35400ea1bb4fd0c9a54737ebdab5b6b8a838` |
| `market_data/write_gateway.py` | blob `585caf5250c7382f8e391533882f08c8ec97efaa` | blob `0a77df443ae1a817ea74946fac5dc0f3809ddd83` |
| `market_data/test_write_gateway.py` | blob `2c55dff1729cdfd11bd0ef2188e1e41756ed7692` | blob `231f5e0184821c78cda0ca5d03625f71fd3a4b71` |
| Dedicated workflow | N/A | `.github/workflows/t0-f1-regression-parity.yml`, blob `967e160d7edbf438db9a53a35e6f27c8cfc3f934` |

The target write-gateway implementation remains byte-different from the latest source. Static review confirms both implementations validate the exact ordered `feeder_leases` columns (`lease_name, owner, generation, expires_at_ms`) and primary key (`lease_name`) before gateway construction completes. The target implementation was retained; no production source edit was made.

The target test file was not overwritten by the source version. It preserves target-only tests, including the missing-lease-table regression, and adds the two approved checks. The dependency-closure fixture was adapted to the target's existing `create_store(...).initialize()` and `LeaseStore` setup; it does not import a source-only initializer absent from the target.

## Changes

1. Commit `f2981271d42b7c3baee8cc4de1c670e8a54cdd85` — `test(t0): add F1 SQLite regression parity checks`
   - Changed only `market_data/test_write_gateway.py`.
   - Added malformed `feeder_leases` schema rejection test.
   - Added Python `-S` test importing API, Feeder Service and Storage modules, creating a disposable SQLite DB, acquiring a lease, writing one candle and reading it back without site-packages.
   - Preserved target-specific test methods.

2. Commit `b2bb35400ea1bb4fd0c9a54737ebdab5b6b8a838` — `ci(t0): isolate F1 SQLite regression parity`
   - Added only `.github/workflows/t0-f1-regression-parity.yml`.
   - Workflow checks out exact triggering SHA, runs only `market_data.test_write_gateway` in a pinned Python 3.12.16 container with network disabled, read-only source, non-root user, no credentials and no canonical DB mount.
   - Enforces exactly 14 tests and uploads run metadata/log/image identity.

## Exact-SHA verification

Dedicated workflow:
- Run: [44494341100](https://github.com/kenznguyen/btcquant-application/actions/runs/44494341100)
- Job: `135457600070`
- Workflow commit and exact checkout SHA: `b2bb35400ea1bb4fd0c9a54737ebdab5b6b8a838`
- Result: SUCCESS
- Command: `python -m unittest -v market_data.test_write_gateway`
- Result: `Ran 14 tests in 0.338s`; `OK`; 14/14 PASS.
- New malformed-schema regression: PASS.
- New Python `-S` dependency-closure regression: PASS.
- Artifact: `t0-f1-regression-parity-evidence`, ID `14513793330`, size 1,293 bytes, expires `2026-12-03T09:13:02Z`.
- Artifact digest: `sha256:c778e6ab5f61de875c9ad585d05459c25fadb79bd344eee22841a55303e08876`.

## Incidental pre-existing workflow triggered by push

The target repository's pre-existing `.github/workflows/t0-sqlite-api-isolated.yml` has an unrestricted `push: branches: [main]` trigger and was also started by the two commits above. It is not the F1 acceptance workflow and was not modified.
- Run: [44494340918](https://github.com/kenznguyen/btcquant-application/actions/runs/44494340918)
- Job: `135457611993`
- Workflow head SHA: `b2bb35400ea1bb4fd0c9a54737ebdab5b6b8a838`
- Its own YAML pins the test checkout to older source SHA `2668dd538a99d6021921432b3485f4ed84198364`, not the triggering HEAD.
- Result: SUCCESS; 91/91 tests, including feeder lifecycle coverage, on that older pinned checkout.
- Network-isolation probe: PASS (loopback only); no canonical DB mount or credentials.
- Artifact: `t0-sqlite-api-test-evidence`, ID `14514950405`, size 4,019 bytes, digest `sha256:9784580ad46d8ec4687586096fa7d864390c593a1f0d12e585c7a081abd94a3a`.
- This run is recorded for transparency only. It is NOT evidence for the new target HEAD or F1 parity. The pre-existing workflow's broad push trigger and fixed old checkout remain a separate CI-scope issue; no change to it is made in this increment.

## Status

| Control | Status | Evidence |
|---|---|---|
| Target F1 production guard | PASS (behavioral parity) | Static comparison plus malformed-schema regression |
| Missing `feeder_leases` schema regression | PASS | Dedicated exact-SHA test |
| Malformed `feeder_leases` schema regression | PASS | Dedicated exact-SHA test |
| SQLite dependency closure without site-packages | PASS | Python `-S` exact-SHA test |
| Write-gateway regression module | PASS | 14/14 |
| Source/target byte parity for `write_gateway.py` | DIVERGED | Different implementation text retained intentionally |
| Full SQLite/API regression suite at current HEAD | NOT VERIFIED | Only write-gateway module ran at current HEAD |
| Pre-existing seven-module workflow at current HEAD | NOT VERIFIED | It checked out fixed older SHA |
| Runtime/lifecycle, canonical recovery/data, PostgreSQL | OUT OF SCOPE / NOT VERIFIED | Not accessed |
| Production readiness | NOT CERTIFIED | Not evaluated |

## Change boundaries

- No source repository changes.
- No production T0 source changes in target.
- No dependencies or manifests changed or installed.
- No PostgreSQL/TimescaleDB files copied.
- No workflow from the source repository copied.
- No canonical DB/data, runtime, VPS, credentials, exchange or trading path accessed.
- No branch created; no merge, rebase, cherry-pick, reset or force-push.
- Target branch remains `main`.

## Next bounded step

Keep this target F1 increment closed as PASS. Before the next target-wide T0 regression, separately review and approve the pre-existing broad-trigger workflow so it checks out the intended exact HEAD and does not silently include runtime/lifecycle tests in a SQLite-only gate. Then proceed with read-only API and storage/initialization parity, without PostgreSQL or runtime expansion.
