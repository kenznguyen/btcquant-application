# T0 FastAPI — Committed Offline Locks, Adapter Review and Paired CI Evidence

- Date: 2026-11-19
- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Exact paired source SHA: `6558141e7de20c30447cdb9705583e05a7d80592`

## 1. Paired CI results

| Suite | Run | Result | Job |
|---|---:|---:|---:|
| FastAPI Candle Contract 1.1.0 | [44526822603](https://github.com/kenznguyen/btcquant-application/actions/runs/44526822603) | **25/25 PASS** | `135569565169` |
| SQLite-only T0 aggregate | [44526822322](https://github.com/kenznguyen/btcquant-application/actions/runs/44526822322) | **196/196 PASS** | `135569525255` |

Both workflows checked out the same exact source SHA above.

Artifacts:
- FastAPI: ID `14533180068`, SHA-256 `43b551482bc7952dd92063067413e0464b3bc5680102e1084282bd28a44e6be5`.
- SQLite aggregate: ID `14532985102`, SHA-256 `3a7d5b948d32c08ec53e527cbeac6c214009f01dba4a4df301bce1ee49f9d3d4`.

## 2. Committed target dependency locks

Target: CPython 3.12.16, Linux x86_64, wheel-only, exact SHA-256.

- Runtime lock: `requirements-market-data-fastapi.lock`
  - SHA-256: `fb4cf8f63131cb36636b3c3230378a49bfb2d3a56b8750778ed5b3b5dac8d786`
  - Commit: `a4c0d146e4153fbea010a97163630e483a0c98f5`
- Test lock: `requirements-market-data-fastapi-test.lock`
  - SHA-256: `2916098771a482a21637b94fff1f79afc0ddeb37a2a01fdae05032509a889cb6`
  - Commit: `f55168aafacd4b220bd029b500886eb3a16f0860`
- Manifest: `requirements-market-data-fastapi.sha256`
  - Commit: `2af56e3448f06e836c8ce203b7dd6f3f599325ed`

The latest workflow ran `sha256sum -c requirements-market-data-fastapi.sha256` and both committed lock checks returned **OK**. It downloaded the exact target wheels to an ephemeral wheelhouse, then installed the test environment with `--no-index --require-hashes` inside a test container configured with `--network none`. No credentials or canonical database were mounted.

## 3. Adapter and architecture corrections

- Shared `candle_query` and `_freshness` logic was extracted into `market_data/api_contract.py`; the FastAPI adapter no longer imports the WSGI module.
- FastAPI route handlers remain synchronous so blocking SQLite reads do not run directly in an async event loop.
- A read-only middleware rejects all non-GET methods before route matching, including extension verbs, with the established 405 response and `Allow: GET`.
- FastAPI responses preserve `Cache-Control: no-store` and the existing `Content-Type: application/json; charset=utf-8`.
- FastAPI docs/OpenAPI endpoints remain disabled.
- No write, ingestion, lease, initialization, migration, order or trading endpoint was added.

## 4. Internal code review

Review axes: correctness, readability, architecture, security and performance.

- **Correctness:** PASS for the covered Candle Contract 1.1.0 behaviors; 25 ASGI tests and 196 SQLite aggregate tests pass on the same SHA.
- **Architecture:** PASS for the initial adapter boundary after extracting shared contract logic. T0 storage remains the existing read-only provider.
- **Security:** PASS for reviewed HTTP boundary controls: constant-time Bearer comparison, no query-string token, no-store responses, fail-closed store behavior, bounded query, all non-GET rejection, offline test network and no secrets/data mounts in CI.
- **Performance:** PASS for the route execution model; SQLite reads stay in synchronous route handlers.
- **Readability:** PASS with minor cleanup opportunities (type annotations for shared contract helpers can be added separately without changing behavior).

### Required review gate still open

This is an internal review, not an independent second-reviewer sign-off. Independent code review remains **PENDING**. Do not remove the WSGI entrypoint or Gunicorn until that review accepts the adapter and the migration diff.

## 5. Current migration status

- FastAPI adapter and focused ASGI contract tests: **PASS 25/25**.
- Existing SQLite aggregate: **PASS 196/196**, same exact SHA.
- Runtime/test dependency locks: **COMMITTED, HASH-VERIFIED, OFFLINE INSTALL PASS**.
- WSGI-to-ASGI migration: **PARTIAL**. `market_data/api.py` still exposes the WSGI `application` and `market_data/test_api.py` still tests that entrypoint. No runtime switch has occurred.
- Independent code review: **PENDING**.
- Runtime, endpoint probe, Nginx/VPS/systemd/deployment: **NOT AUTHORIZED / NOT VERIFIED**.
- PostgreSQL/TimescaleDB: **PARKED**.
- T1/T2 connection and trading: **NOT AUTHORIZED**.
- Production readiness: **NOT CERTIFIED**.

## 6. Next bounded steps

1. Obtain independent code review for the FastAPI adapter, shared contract module, tests, dependency locks and workflows.
2. After review acceptance, prepare a small WSGI-removal change: migrate/retire the WSGI-only test entrypoint, remove WSGI serving code and Gunicorn dependency, and retain the shared Candle Contract 1.1.0 helpers.
3. Run the full ASGI suite and the 196-test SQLite aggregate on the same exact SHA after WSGI removal.
4. Record independent review, exact SHA, workflow IDs, artifact IDs and hashes.
5. Request separate approval before endpoint probes, Nginx routing, process startup, VPS or deployment.

No canonical SQLite data/schema, writer/lease/feeder/recovery, retention/deletion, T1/T2, PostgreSQL or trading behavior changed.


## 7. Final hardened test-container verification — 2026-11-19

- Latest paired source SHA: `0a4432d8d101381e8b07c88a1a65bbf1ee3a787f`.
- FastAPI run [44527300856](https://github.com/kenznguyen/btcquant-application/actions/runs/44527300856), job `135571152796`: **25/25 PASS**, artifact `14532510818`, SHA-256 `563e4841b1139c16f55198407a890f6ea60400564c8c2b2cc1641576267ad49c`.
- SQLite aggregate run [44527300813](https://github.com/kenznguyen/btcquant-application/actions/runs/44527300813), job `135571149659`, same exact SHA: **196/196 PASS**, artifact `14533320216`, SHA-256 `6ef67fb1512cb06a62a35d74a5c34e333814cf33c865f58c4200ea5f206f7f23`.
- Both committed lock files were verified by `sha256sum -c` in the FastAPI run.
- Test container hardening: non-root UID 65534, read-only root filesystem, all Linux capabilities dropped, `no-new-privileges`, bounded PIDs/CPU/memory, `--network none`, source/artifact/wheelhouse mounted read-only, and a dedicated executable temporary filesystem for SQLite temp files and native Python extensions.
- The first non-root attempt failed because the temporary filesystem did not allow native shared-library mapping; the next commit added the narrowly scoped `exec` flag to the temporary filesystem, and the final 25-test run passed. The failed run is retained as evidence, not hidden.
- This final checkpoint supersedes the earlier paired run SHA `6558141e7de20c30447cdb9705583e05a7d80592` for current adapter/CI status. Independent code review remains pending; WSGI entrypoint remains present.
