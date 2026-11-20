# Kiri Lite 0.2.2 compatibility verification — Ubuntu 26.04.1 — 2026-11-20

## Final disposition

**PASS — Ubuntu 26.04.1 LTS / amd64 GitHub-hosted runner, CI ONLY.**

Kiri Lite 0.2.2 installed, started explicitly, served the Docker API, ran two test containers, and completed remove/purge lifecycle checks on a disposable GitHub-hosted runner.

This does not authorize or imply installation on the project VPS, any persistent host, or the BTCUSDT Quant System. No VPS, project host, T0 SQLite, T1/T2, project secrets, deployment target, or real trading system was accessed.

## Exact source and CI evidence

- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Workflow: `.github/workflows/kiri-linux-package-verification.yml`
- Final tested workflow/source SHA: `9639f08648697d146ae4ce0b7c93b300d8cc777e`
- Final Actions run: [44667282678](https://github.com/kenznguyen/btcquant-application/actions/runs/44667282678)
- Run ID: `44667282678`
- Exact head SHA: `9639f08648697d146ae4ce0b7c93b300d8cc777e`
- Branch/event: `main` / push
- Overall run conclusion: **SUCCESS**

Final run jobs:

| Job | Job ID | Conclusion |
|---|---:|---|
| Kiri Lite 0.2.2 / Ubuntu 24.04 | `136060570044` | **SUCCESS** |
| Kiri Lite 0.2.2 / Ubuntu 26.04.1 | `136060571687` | **SUCCESS** |
| Full Kiri 0.2.2 / Ubuntu 24.04 | `136060628718` | **SUCCESS** |

No Actions artifact was uploaded. The exact run page and job logs are the retained evidence.

## Runner identity observed in the Ubuntu 26.04.1 job

- Runner label: `ubuntu-26.04`
- OS: `Ubuntu 26.04.1 LTS`
- Codename: `resolute`
- Architecture: `amd64` / x86_64
- Kernel: `7.0.0-1020-azure`
- systemd: `259.9-0ubuntu0.1`
- Docker CLI: `29.4.2`
- systemd runtime directory: `/run/systemd/system` present

The job asserted Ubuntu `VERSION_ID=26.04`, amd64, active systemd runtime, systemd version >=259, and an available Docker CLI before proceeding.

## Package and provenance verification

- Release: Kiri `v0.2.2`
- Package: `kiri-lite_0.2.2_amd64.deb`
- Package SHA-256: `24798125ee50bb24db86594a9ee1469b1032d9b2ffd7da616b06e40763c723b9`
- Official publisher checksum manifest: PASS
- Detached GPG signature: **Good signature**
- Pinned publisher key fingerprint: `900CB63F75328B627AF5549353263AE758141A6B`
- Signed Git tag `v0.2.2`: PASS
- Tag object: `0cd223cfb2c1038068b22000b973376c7231e7a4`
- Tag target commit: `686bffa5f38ba6ecc3d086c36ec7148cd7fb976a`
- Package control scripts `postinst`, `prerm`, `postrm`: all matched the expected pinned source Git blob IDs.

## Runtime and lifecycle tests

| Test | Result |
|---|---|
| Fresh package installation | **PASS** |
| Service not auto-started | **PASS** |
| Service not auto-enabled | **PASS** |
| Explicit `systemctl enable --now kiri.service` | **PASS** |
| `/run/kiri/docker.sock` exists | **PASS** |
| Socket permissions `660:root:kiri` | **PASS** |
| systemd service active | **PASS** |
| Docker API `docker version` through Kiri socket | **PASS** |
| `hello-world` container | **PASS** |
| Alpine 3.21 container execution | **PASS** |
| `apt remove kiri-lite` stops service | **PASS** |
| `apt remove` retains `/var/lib/kiri` data | **PASS** |
| `apt purge kiri-lite` removes `/var/lib/kiri` and `/var/lib/kiri-daemon` | **PASS** |

Runtime log explicitly recorded:
- Docker server: `Kiri`
- `Hello from Docker!`
- `KIRI_CONTAINER_EXECUTION_PASS`
- Kiri state retained after remove.
- Kiri state deleted after purge on the disposable runner.

## Failed attempts and corrections — preserved for provenance

1. Run `44667151168`, head SHA `e7af3defbb5178df95e2e0b9a5777900285c5c6a`: Ubuntu 26.04 job reached the correct Ubuntu 26.04.1 image but preflight failed because the `systemd` executable was not available under that command name in PATH. This was a test harness/preflight issue, not a Kiri package failure. The probe was corrected to use `systemctl --version`.
2. Run `44667282678`, head SHA `9639f08648697d146ae4ce0b7c93b300d8cc777e`: Ubuntu 26.04.1 Kiri Lite job passed all steps. A separate Ubuntu 24.04 Kiri Lite job transiently received HTTP 403 from GitHub API during signed tag retrieval; only that failed job was rerun. The rerun succeeded. The final workflow run concluded SUCCESS with all three jobs successful.

## Security and scope limits

- The runner was disposable and hosted by GitHub. No persistent host was used.
- The test explicitly started the service only after package installation and inert-state assertions.
- Kiri daemon runs as root. Membership in the `kiri` group is root-equivalent; do not grant it casually.
- The Kiri socket is `root:kiri`, mode `0660`.
- Linux containers share the host kernel; this test is not a VM isolation/security audit.
- `apt purge` destroys Kiri images, containers, volumes and state. It was executed only on the disposable runner.
- No Docker Engine replacement, socket integration with project applications, or persistent data migration was performed.

## Status matrix

| Scope | Status |
|---|---|
| Kiri Lite 0.2.2 / Ubuntu 24.04 amd64 | **PASS — CI** |
| Kiri Lite 0.2.2 / Ubuntu 26.04.1 amd64 | **PASS — CI** |
| Full Kiri 0.2.2 / Ubuntu 24.04 amd64 | **PASS — CI** |
| Full Kiri / Ubuntu 26.04.1 | **NOT TESTED** |
| Ubuntu 26.04 ARM64 | **NOT TESTED** |
| RPM packages | **NOT TESTED** |
| Compose/buildx workload parity | **NOT VERIFIED** |
| Existing Docker coexistence on a persistent host | **NOT VERIFIED** |
| Performance, load and independent security audit | **NOT TESTED** |
| Project VPS / persistent host installation | **NOT APPROVED** |
| T0/T1/T2 integration or project runtime | **NOT APPROVED / NOT TESTED** |

## Recommendation

Kiri Lite 0.2.2 has passed the bounded Ubuntu 24.04 and Ubuntu 26.04.1 amd64 GitHub Actions package/lifecycle checks. Keep it as a candidate for a future, separately approved evaluation. Do not install it on the project VPS or any persistent host without a new explicit owner approval.
