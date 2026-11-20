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
