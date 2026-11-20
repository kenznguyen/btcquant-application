# Decision: Docker remains standard; Kiri Lite evaluation-only

Date: 2026-11-20
Repository: `kenznguyen/btcquant-application`
Decision status: **APPROVED — GOVERNANCE / DOCUMENTATION ONLY**

## Decision

1. **Docker remains the standard container runtime** for this repository and the BTCUSDT Quant System.
2. **Kiri Lite remains evaluation-only**. It may be retained as a candidate for separately scoped, disposable-runner experiments.
3. This decision does not authorize installing, enabling, deploying, or operating Kiri on any persistent host, VPS, workstation used for project operations, or production environment.
4. This decision does not authorize replacing Docker, changing the default Docker context/socket, creating a `/var/run/docker.sock` symlink, granting application users membership in the root-equivalent `kiri` group, or connecting Kiri to application services.
5. No T0/T1/T2, canonical SQLite, Quant application, trading, deployment, or persistent runtime integration is authorized.

## Basis and evidence reviewed

- Kiri Lite package: `0.2.2`, package SHA-256:
  `24798125ee50bb24db86594a9ee1469b1032d9b2ffd7da616b06e40763c723b9`.
- Repository branch: `main`.
- Exact tested workflow/source SHA:
  `dce91fad64506ca1fbe09be1b51a55f0958b4153`.
- Workflow: `.github/workflows/kiri-lite-compose-buildx-coexistence.yml`.
- GitHub Actions run: [44668934024](https://github.com/kenznguyen/btcquant-application/actions/runs/44668934024), overall SUCCESS.
- Ubuntu 24.04.5 amd64 job `136065096664`: SUCCESS.
- Ubuntu 26.04.1 amd64 job `136065096922`: SUCCESS.
- Evidence report: [Kiri Lite Compose/Buildx/Docker coexistence](../evidence/KIRI_LITE_COMPOSE_BUILDX_DOCKER_COEXISTENCE_2026-11-20.md).
- Evidence report commit: `150616c3d6ef32e0793d35aeac11cfc53f387cfd`.

### Verified within the bounded CI scope

- Pinned Kiri Lite package checksum verified on both disposable GitHub-hosted runners.
- Kiri used its separate `/run/kiri/docker.sock`; the pre-existing Docker Engine ID and `/run/docker.sock` identity remained unchanged through Kiri startup, smoke workloads, and Kiri removal/purge.
- A bounded local Buildx scratch/COPY build, export/load, inspect and run passed on both runners.
- A bounded Compose BusyBox service/network smoke passed on both runners.
- No project VPS, persistent host, T0 SQLite, T1/T2, project secrets, Quant runtime or trading system was accessed.

### Reasons not to adopt Kiri now

- The tests establish bounded smoke compatibility and coexistence, not complete Docker/Compose/BuildKit feature parity.
- Registry pulls, Kiri-side DNS, registry authentication and rate-limit behavior were not verified; test images were preloaded through Docker.
- Persistent-host coexistence, long-duration stability, crash recovery, volume durability, performance/load and resource overhead were not tested.
- No independent security audit or host-specific threat assessment has been completed.
- On Linux, Kiri containers share the host kernel; Kiri's daemon runs as root and membership in group `kiri` is root-equivalent.
- The current evidence does not demonstrate a material operational advantage over the existing Docker baseline for this project.

## Review qualification

This decision is an evidence-based project governance decision following review of the workflow, retained CI artifacts and the recorded test limitations. The review performed in this conversation is not a separately commissioned human second-person security audit. Security certification and production readiness remain **NOT VERIFIED**.

## Status

| Area | Status |
|---|---|
| Kiri Lite package install/service lifecycle on tested CI runners | PASS — CI |
| Bounded Buildx smoke | PASS — CI |
| Bounded Compose smoke | PASS — CI |
| Docker coexistence on disposable CI runners | PASS — CI |
| Full Docker feature parity | NOT VERIFIED |
| Kiri registry/DNS/authentication | NOT VERIFIED |
| Persistent-host coexistence | NOT TESTED |
| Performance and long-duration stability | NOT TESTED |
| Independent security audit | NOT VERIFIED |
| Kiri installation on VPS/persistent host | NOT APPROVED |
| Docker replacement/default socket change | NOT APPROVED |
| T0/T1/T2 or trading-runtime integration | NOT APPROVED |

## Reconsideration gate

Any proposal to move beyond evaluation-only must be submitted as a new decision with a bounded scope, target host, rollback plan, socket/privilege model, persistent-data handling, security review, registry/network tests, functional parity matrix, performance/stability evidence and explicit owner approval. Passing CI smoke tests alone is insufficient.

No code, dependencies, Docker configuration, workflows, host runtime, market data, SQLite or trading behavior is changed or authorized by this decision.
