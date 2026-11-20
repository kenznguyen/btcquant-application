# Kiri Lite 0.2.2 — Docker Compose, Buildx and Docker Engine coexistence

Date: 2026-11-20

## Final disposition

**PASS — bounded GitHub Actions CI smoke verification on Ubuntu 24.04.5 and Ubuntu 26.04.1 amd64.**

Kiri Lite 0.2.2 was installed on disposable GitHub-hosted runners, explicitly started, and accessed through its own Docker context/socket. Docker Compose and Buildx both completed bounded smoke workloads. The pre-existing Docker Engine remained available through its original socket, with its Engine ID and socket identity unchanged before and after Kiri start/workloads/remove/purge.

This is **not** a persistent-host compatibility certification or deployment approval. No VPS, persistent host, project secrets, T0 SQLite, T1/T2, Quant runtime, deployment target or trading system was accessed.

## Exact source and CI evidence

- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Workflow: `.github/workflows/kiri-lite-compose-buildx-coexistence.yml`
- Tested workflow/source commit SHA: `dce91fad64506ca1fbe09be1b51a55f0958b4153`
- Final GitHub Actions run: [44668934024](https://github.com/kenznguyen/btcquant-application/actions/runs/44668934024)
- Exact run head SHA: `dce91fad64506ca1fbe09be1b51a55f0958b4153`
- Overall conclusion: **SUCCESS**
- Final jobs:
  - Ubuntu 24.04.5: job `136065096664` — **SUCCESS**
  - Ubuntu 26.04.1: job `136065096922` — **SUCCESS**

### Retained Actions artifacts

| Runner | Artifact ID | SHA-256 digest | Result |
|---|---:|---|---|
| Ubuntu 24.04.5 amd64 | `14598393874` | `25f78a26739ffabf00847300fe4dceb227a3889141122412c3e9b98be1fc0650` | Uploaded |
| Ubuntu 26.04.1 amd64 | `14598463497` | `58a819c06a21ddf270e1f3444d23ff6925b5875717a6d7e681e01db895b0992c` | Uploaded |

Artifact links:
- [Ubuntu 24.04.5 evidence](https://github.com/kenznguyen/btcquant-application/actions/runs/44668934024/artifacts/14598393874)
- [Ubuntu 26.04.1 evidence](https://github.com/kenznguyen/btcquant-application/actions/runs/44668934024/artifacts/14598463497)

Artifacts are retained by GitHub Actions for 30 days from upload. The workflow run and job logs remain the primary evidence.

## Test subject and runner identity

Package under test:
- Kiri Lite release: `v0.2.2`
- Debian package: `kiri-lite_0.2.2_amd64.deb`
- SHA-256: `24798125ee50bb24db86594a9ee1469b1032d9b2ffd7da616b06e40763c723b9`
- Package digest was checked before installation on both runners.

| Property | Ubuntu 24.04.5 | Ubuntu 26.04.1 |
|---|---|---|
| Architecture | amd64 | amd64 |
| Kernel | `7.0.0-1017-azure` | `7.0.0-1020-azure` |
| Docker CLI / Engine | `28.0.4` | `29.4.2` |
| Docker Compose | `v2.38.2` | `v5.1.3` |
| Docker Buildx | `v0.38.2` | `v0.39.0` |
| Kiri Docker API server | `27.5.1` | `27.5.1` |
| BuildKit builder | `v0.34.2` | `v0.34.2` |

## Test design

The tests deliberately separated the two engines:

- Existing Docker Engine endpoint: `/run/docker.sock`, accessed with the default context.
- Kiri endpoint: `/run/kiri/docker.sock`, accessed with a dedicated Docker context named `kiri`.
- Kiri socket permissions asserted as `660:root:kiri`.
- Buildx builder: `kiri-build`, driver `docker-container`, endpoint/context `kiri`.
- Buildx inspection and build explicitly set `DOCKER_CONTEXT=kiri`, so image export/load targets Kiri rather than the runner's default Docker Engine.
- Docker Compose and Buildx were executed with explicit elevated privileges. No runner user was added to the `kiri` group.

Images used by the smoke tests were first retrieved through the runner's existing Docker Engine and then transferred to Kiri. This removes Kiri-side registry/DNS as a dependency of these tests and keeps the two compatibility questions independently testable.

## Results

### 1. Package install and service activation

| Test | Ubuntu 24.04.5 | Ubuntu 26.04.1 |
|---|---|---|
| Pinned package SHA-256 | **PASS** | **PASS** |
| Fresh install leaves service inactive | **PASS** | **PASS** |
| Fresh install leaves service disabled | **PASS** | **PASS** |
| Explicit `systemctl enable --now kiri.service` | **PASS** | **PASS** |
| Kiri service active | **PASS** | **PASS** |
| Kiri socket exists with `660:root:kiri` | **PASS** | **PASS** |
| Docker API identifies Kiri server | **PASS** | **PASS** |

### 2. Docker Engine coexistence

The workflow captured the pre-existing Docker Engine ID and `/run/docker.sock` device/inode/mode/owner/group before Kiri installation/start. It asserted those values were unchanged after Kiri started, after the Buildx/Compose workloads, and after Kiri removal/purge.

| Property | Ubuntu 24.04.5 | Ubuntu 26.04.1 |
|---|---|---|
| Original Docker Engine ID | `0fef2a29-aadb-43ca-98b5-edbc7a28f18a` | `636b573e-1748-48fb-a027-4a5f710f78e2` |
| Original socket identity before | `29:1067:660:root:docker` | `29:1532:660:root:docker` |
| Kiri server version | `27.5.1` | `27.5.1` |
| Original Docker Engine ID/socket after Kiri start | **UNCHANGED — PASS** | **UNCHANGED — PASS** |
| Original Docker Engine ID/socket after workloads | **UNCHANGED — PASS** | **UNCHANGED — PASS** |
| Original Docker Engine after Kiri remove/purge | **RESPONDS — PASS** | **RESPONDS — PASS** |

The existing Docker Engine and Kiri used separate data roots:
- Docker Engine: `/var/lib/docker`
- Kiri: `/var/lib/kiri`

No default Docker socket takeover or replacement was observed on these runners.

### 3. Docker Buildx

| Test | Ubuntu 24.04.5 | Ubuntu 26.04.1 |
|---|---|---|
| Dedicated `kiri` Docker context | **PASS** | **PASS** |
| Dedicated `kiri-build` builder | **PASS** | **PASS** |
| `docker-container` driver bootstrap | **PASS** | **PASS** |
| BuildKit v0.34.2 starts against Kiri | **PASS** | **PASS** |
| Build a local `FROM scratch` image using Buildx | **PASS** | **PASS** |
| Export/load image to Kiri context | **PASS** | **PASS** |
| Inspect image through Kiri context | **PASS** | **PASS** |
| Run image through Kiri context | **PASS** | **PASS** |

Container output on both runners: `KIRI_BUILDX_IMAGE_PASS`.

The test uses a minimal local Dockerfile with `FROM scratch` and `COPY` operations. It proves the dedicated Buildx builder can bootstrap, build, export/load, inspect and run an image on Kiri. It does not prove every BuildKit feature or full production build parity.

### 4. Docker Compose

| Test | Ubuntu 24.04.5 | Ubuntu 26.04.1 |
|---|---|---|
| Compose CLI/plugin available | **PASS** | **PASS** |
| Compose version command through Kiri context | **PASS** | **PASS** |
| `docker compose config` | **PASS** | **PASS** |
| Compose creates project network | **PASS** | **PASS** |
| Compose runs a preloaded BusyBox workload through Kiri | **PASS** | **PASS** |

Container output on both runners: `KIRI_COMPOSE_PASS`.

The Compose smoke is independent of the Buildx smoke: it transfers a known BusyBox image through the existing Docker Engine, loads it into Kiri, then runs the Compose service with `pull_policy: never`.

### 5. Removal and cleanup on disposable runners

- `apt remove kiri-lite` stopped and removed the Kiri service.
- `apt purge kiri-lite` removed Kiri state on the disposable runner.
- The original Docker Engine remained responsive with the same Engine ID after Kiri purge.
- All destructive purge operations were confined to disposable GitHub-hosted runners.

## Intermediate attempts and corrections

All intermediate attempts remain visible in GitHub Actions history. They are not treated as successful evidence:

1. Initial unprivileged CLI calls received `permission denied` because the runner user was not a member of the root-equivalent `kiri` group. The test was corrected to use explicit `sudo`; no user was added to the group.
2. The default Buildx builder did not establish the required Kiri endpoint. The test was corrected to create a dedicated `kiri` context and `kiri-build` builder using the `docker-container` driver.
3. Initial Buildx attempts tried resolving `alpine:3.21` through Kiri and encountered registry/DNS resolution errors. The final test preloads the BuildKit helper and local test images through the runner's existing Docker Engine, avoiding a Kiri-side registry pull.
4. A later Buildx run built and imported the image but failed the smoke assertion because the proof fixture wrote a literal backslash-n. The fixture was corrected to emit a real newline. Final run `44668934024` passed both OS jobs and all ten steps in each job.

## Security and interpretation limits

- Membership in Linux group `kiri` is root-equivalent. Do not add application or service users to this group casually.
- Kiri daemon runs as root. The Kiri socket is `root:kiri`, mode `0660`.
- The tests used `sudo`; they do not establish that an unprivileged application user should receive direct Kiri socket access.
- The runner already had a Docker Engine and an existing `/run/docker.sock`; coexistence is demonstrated only for these disposable runner images and their exact Docker versions.
- Images were preloaded from the runner's Docker Engine. Kiri-side external registry pulls, authentication, rate limits and DNS are **NOT VERIFIED** by the final run.
- Buildx coverage is a local scratch/COPY smoke. BuildKit `RUN`, cache import/export, remote cache, secrets/SSH forwarding, multi-platform builds, Bake, custom frontends and advanced exporter parity are **NOT TESTED**.
- Compose coverage is a single BusyBox service with project network creation. Multi-service dependency graphs, Compose build, volumes, secrets, profiles, health checks, watch, plugins and production Compose parity are **NOT TESTED**.
- No performance/load, failure-recovery, independent security audit, persistent-host coexistence or application-level integration test was performed.
- Linux containers share the host kernel; this is not VM isolation.

## Status matrix

| Scope | Status |
|---|---|
| Kiri Lite 0.2.2 package install/service lifecycle / Ubuntu 24.04.5 amd64 | **PASS — CI** |
| Kiri Lite 0.2.2 package install/service lifecycle / Ubuntu 26.04.1 amd64 | **PASS — CI** |
| Docker Compose smoke / Ubuntu 24.04.5 amd64 | **PASS — CI** |
| Docker Compose smoke / Ubuntu 26.04.1 amd64 | **PASS — CI** |
| Buildx local scratch build/load/run / Ubuntu 24.04.5 amd64 | **PASS — CI** |
| Buildx local scratch build/load/run / Ubuntu 26.04.1 amd64 | **PASS — CI** |
| Coexistence with existing Docker Engine on Ubuntu 24.04.5 runner | **PASS — CI** |
| Coexistence with existing Docker Engine on Ubuntu 26.04.1 runner | **PASS — CI** |
| Kiri-side external registry/DNS | **NOT VERIFIED** |
| Full Compose feature/workload parity | **NOT TESTED** |
| Full Buildx/BuildKit feature/workload parity | **NOT TESTED** |
| Persistent-host Docker Engine coexistence | **NOT TESTED** |
| ARM64 / RPM / Full Kiri on Ubuntu 26.04 | **NOT TESTED** |
| Performance, load, independent security audit | **NOT TESTED** |
| VPS/persistent-host installation | **NOT APPROVED** |
| Project T0/T1/T2 integration or trading runtime | **NOT APPROVED / NOT TESTED** |

## Recommendation

Kiri Lite 0.2.2 has passed bounded Compose, Buildx and coexistence smoke tests on GitHub-hosted Ubuntu 24.04.5 and 26.04.1 amd64 runners. It is reasonable to retain Kiri Lite as a candidate for a future separately approved persistent-host evaluation.

**Do not install it on the project VPS or any persistent host yet.** A separate approval and a dedicated persistent-host risk/compatibility plan are still required. No Docker Engine replacement, default socket takeover, project application integration or trading-runtime connection is authorized by this report.
