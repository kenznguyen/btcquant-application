# Decision: replace GitHub-only validation with two independent validation tracks

- Date: 2026-11-19
- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Approval: **APPROVED BY OWNER**
- Supersedes: the prior decision to use GitHub Actions as the only integration-validation environment for Uvicorn + Nginx.

## Decision

Validation is split into two separately governed tracks. Neither track substitutes for, inherits the status of, or certifies the other.

### Track A — isolated CI integration

- Continue the existing GitHub Actions Uvicorn + Nginx integration job.
- Preserve its exact-SHA evidence, artifacts, test scope and isolation.
- Existing result remains **PASS — CI ONLY** on source/workflow SHA `65661cd4a2492f9552fe05186581c66d14fbe293`.
- CI results must not be represented as proof of VPS runtime behavior.

### Track B — VPS runtime integration

- Maintain a distinct runtime-validation record and evidence set for the intended VPS test environment.
- Current status is **NOT VERIFIED / NOT RUN**.
- This decision does not authorize an immediate VPS probe, SSH session, process launch, Nginx configuration change, service installation, persistent process, systemd/autostart, public listener, DNS, TLS or deployment.
- Any actual runtime-validation session requires a separate, explicit owner authorization defining its exact scope and permitted operations.
- Runtime evidence must independently record environment/host identity at an appropriate non-secret level, source SHA, configuration fingerprint with secrets excluded, test time, commands/checks, logs/artifact references, results and limitations.
- Runtime PASS applies only to the checks and environment actually observed. It does not certify production readiness.

## Separation and reporting rules

1. CI and VPS runtime retain independent statuses, evidence and acceptance criteria.
2. Do not merge their results into a single PASS.
3. A CI PASS cannot establish VPS process/socket startup, actual Nginx behavior, service persistence, restart behavior, host permissions, firewall behavior or production readiness.
4. A VPS runtime result does not replace CI regression evidence.
5. Keep unperformed checks explicitly **NOT VERIFIED**; do not infer success.
6. No runtime validation is performed as part of recording this decision.

## Scope restrictions preserved

- No source code, tests, workflow, dependency or runtime configuration changes are authorized by this decision.
- No canonical T0 SQLite access or mutation; no feeder, writer, lease, scheduler or recovery changes.
- No T1/T2, PostgreSQL, data retention/deletion, strategy, risk-engine or trading changes.
- No real orders; paper-first remains in force and `ai_execution_enabled=false`.
- No production deployment, public ingress, TLS, systemd/autostart or persistent service authorization.

## Evidence baseline

- Existing CI integration report: [T0 Uvicorn + Nginx Isolated Integration](../evidence/T0_UVICORN_NGINX_ISOLATED_INTEGRATION_2026-11-19.md).
- Tested source/workflow SHA: `65661cd4a2492f9552fe05186581c66d14fbe293`.
- FastAPI workflow run: [44550458804](https://github.com/kenznguyen/btcquant-application/actions/runs/44550458804), overall **SUCCESS**; Uvicorn/Nginx job `135652465869` **SUCCESS**.
- Integration artifact: `14543536038`; SHA-256 `af07b99fa0a53ff315bad148c508533ea0e808d6365fc2c81faafa11ebe8c872`.
- SQLite aggregate workflow run: [44550458851](https://github.com/kenznguyen/btcquant-application/actions/runs/44550458851), **SUCCESS**.
- VPS/Scaleway runtime and Nginx: **NOT VERIFIED**.

## Next step

No runtime action is authorized now. If runtime validation is later desired, first obtain a separate owner-approved, narrowly scoped runtime test plan. Until then, preserve Track A as CI-only PASS and Track B as NOT VERIFIED.
