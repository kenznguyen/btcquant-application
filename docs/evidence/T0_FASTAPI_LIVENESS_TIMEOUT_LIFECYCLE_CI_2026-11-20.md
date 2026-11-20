# T0 FastAPI liveness / timeout / lifecycle implementation evidence

Date: 2026-11-20
Decision: `docs/decisions/T0_FASTAPI_LIVENESS_TIMEOUT_LIFECYCLE_BASELINE_2026-11-20.md`

## Source and workflow provenance

- Repository: `kenznguyen/btcquant-application`, branch `main`.
- Test harness commit / exact source SHA: `66a6fcdecd5a8f1201a7dca2a6520a040ef2cb0d`.
- Harness file blob: `ecddcb63a9840867c46d0dd355a4bf87ba5a8be9`.
- Decision documentation commit: `99cb5b1327b2f14e43b392c17b58823cd4d81cd8`.
- Workflow: `.github/workflows/t0-fastapi-migration.yml`.
- Actions run [44691209612](https://github.com/kenznguyen/btcquant-application/actions/runs/44691209612), run 41, event `push`, conclusion **FAILURE**.

## Results

| Job | Result | Evidence |
|---|---|---|
| FastAPI contract tests | PASS | Job `136137170900` |
| Runtime-lock-only install + ASGI smoke | PASS | Job `136137170825` |
| Uvicorn process/socket + Nginx integration | **FAIL** | Job `136137170694` |

The integration job successfully built the isolated image and reached the process test. It failed at `market_data/uvicorn_nginx_smoke.py` after sending SIGTERM to Uvicorn: `uvicorn_proc.returncode` was not zero (assertion at line 195). Therefore the approved graceful SIGTERM lifecycle behavior is **NOT VERIFIED** and must not be treated as passing. The failure is preserved; do not weaken the assertion or relabel this run as PASS.

Artifacts:
- `t0-uvicorn-nginx-socket-integration`: ID `14609120411`, SHA-256 `a774f6308e37b5e229a28abc7de6ba42e0a4436e9f9ff0c441fbf97363c91c38`.
- `t0-fastapi-contract-evidence`: ID `14608891267`, SHA-256 `82321b4102d49a31f70e154ecc802053179de43b32c767071caabb3ac1ee1b05`.
- Artifacts expire 2026-12-04.

## Implemented test scope

The isolated harness now supplies:
- Nginx `proxy_connect_timeout 1s`, `proxy_send_timeout 5s`, `proxy_read_timeout 7s`, `client_header_timeout 5s`, `client_body_timeout 5s`.
- Uvicorn one worker, `--timeout-keep-alive 5`, `--timeout-graceful-shutdown 10`, `--limit-concurrency 16`.
- Nginx configuration validation with `nginx -t`.
- Process shutdown assertions and existing auth/proxy/upstream-down/token-redaction checks.

## Status

- Owner decisions: **APPROVED / RECORDED**.
- Decision document: **COMMITTED**.
- Contract tests and runtime-lock smoke: **PASS** on exact source SHA above.
- Nginx/Uvicorn lifecycle integration: **BLOCKED** by failed Uvicorn SIGTERM exit assertion.
- Timeout behavior: directives were supplied and Nginx configuration validation was added, but the integration job failed before its completion evidence; overall baseline is not yet PASS.
- Production runtime, VPS, canonical T0, persistent services, supervisor, systemd/autostart, public ingress, T1/T2 and trading: **NOT VERIFIED / NOT AUTHORIZED**.
- No production configuration was added. No canonical T0 data or credentials were accessed.

## Next step

Diagnose why Uvicorn exits with a nonzero signal return code in the isolated process harness. Preserve the failing assertion, add diagnostic capture, and rerun the same isolated GitHub Actions workflow on the resulting exact source SHA. Do not deploy or broaden scope.


## Follow-up diagnosis and successful rerun (2026-11-20)

- Diagnostic instrumentation commit: `bb454804c343497410c9b2022ce631e201996b88`; harness blob at that point `6cdb234cd959c89be9de1bb77a4eb254d9daf38a`.
- Diagnostic run [44691495222](https://github.com/kenznguyen/btcquant-application/actions/runs/44691495222), run 42, exact SHA `bb454804c343497410c9b2022ce631e201996b88`, failed at the same old assertion but preserved process logs in CI output and artifact.
- Root cause: Uvicorn did perform orderly shutdown. Captured logs show `Shutting down`, `Application shutdown complete.`, and `Finished server process`. Uvicorn then re-raises the captured SIGTERM after its graceful shutdown sequence; on POSIX, `subprocess.returncode` is therefore `-15`. The old test incorrectly required return code 0 and interpreted the expected signal exit as failure.
- Corrected regression assertion commit / exact source SHA: `da56b34acf1ef503a6b84dc897fad3de15fdc279`; `market_data/uvicorn_nginx_smoke.py` blob `c12ebb24c7d78a166413b0ae89a6fae78aff7cac`.
- Successful Actions run [44691581111](https://github.com/kenznguyen/btcquant-application/actions/runs/44691581111), run 43, event `push`, completed 2026-11-20 06:59:05Z, conclusion **SUCCESS**.
- Jobs: FastAPI contract tests `136138398424` PASS; runtime-lock-only install + ASGI smoke `136138398656` PASS; isolated Uvicorn/Nginx integration `136138398892` PASS.
- Integration assertions now require POSIX SIGTERM return code `-signal.SIGTERM` **and** both orderly-shutdown log markers (`Application shutdown complete.`, `Finished server process`). This validates graceful shutdown without mistaking Uvicorn's deliberate signal re-raise for a crash.
- Integration evidence lines: Nginx timeout configuration PASS; Uvicorn health/proxy, authorization forwarding, missing bearer rejection, unknown route, non-GET rejection PASS; Uvicorn SIGTERM exit signal SIGTERM; application shutdown complete PASS; graceful exit PASS; upstream-down 502 PASS; Nginx SIGTERM clean exit PASS; bearer token absent from Nginx logs PASS.
- Artifacts (expire 2026-12-04):
  - `t0-fastapi-contract-evidence`: ID `14608133886`, SHA-256 `9ff5e9c29db7c1897710cce28365f1cb7f23727f79f6c96c994e5d628f038a10`.
  - `t0-fastapi-runtime-lock-smoke`: ID `14608737662`, SHA-256 `c3b055411576b3b8a0c83fe3137c1c2daab2d998b1df331e3024bb7c670143f3`.
  - `t0-uvicorn-nginx-socket-integration`: ID `14608638099`, SHA-256 `626b76acba1c5ae02ed611d9bd1a0964c1b8e3f84a60aed829e80c4139ef07bd`.
- Scope remains isolated CI only: non-root container, read-only root, external network disabled, loopback listeners, temporary SQLite fixture. Canonical T0, VPS, credentials, exchange, T1/T2 and trading were not accessed.
- Updated status: **isolated CI PASS** for this exact source SHA and listed test coverage. Production deployment/readiness, supervisor/systemd, persistent lifecycle, public ingress and actual VPS runtime remain **NOT VERIFIED / NOT AUTHORIZED**.
