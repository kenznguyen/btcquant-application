# Kiri Linux package verification — 2026-11-20

## Status

**PASS — bounded package and lifecycle verification on isolated GitHub-hosted Ubuntu 24.04.5 runners.**

This does not approve installation on any project host, replacement of Docker Engine, or integration with BTCUSDT Quant System. No VPS was used. No T0/T1/T2, canonical SQLite, project runtime, deployment target, or real trading system was accessed.

## Owner-approved scope

- Verify the official Kiri Linux release/package provenance.
- Verify the publisher-signed Linux checksum manifest and exact package hashes.
- Inspect package metadata and maintainer scripts.
- Compare package maintainer scripts to the source files at the signed release tag.
- Install and exercise each package only on a disposable GitHub-hosted runner.
- Verify service start, Docker API smoke test, removal and purge behavior.
- Preserve exact source/workflow SHA, run IDs and job IDs.

Out of scope: VPS, persistent project host, Ubuntu 26.04.1, ARM64, RPM, application integration, Docker Compose/buildx compatibility, performance, load testing, full security penetration testing, deployment or production qualification.

## Source and release provenance

- Publisher repository: https://github.com/libracoder/kiri
- Release: https://github.com/libracoder/kiri/releases/tag/v0.2.2
- Tag: `v0.2.2`
- Signed annotated tag object: `0cd223cfb2c1038068b22000b973376c7231e7a4`
- Tag target source commit: `686bffa5f38ba6ecc3d086c36ec7148cd7fb976a`
- GitHub API reports tag signature verification: `verified=true`, reason `valid`.
- Release date: 2026-11-19.
- Vendor describes 0.2.2 as a security release. The GitHub Security tab showed no published security advisories at verification time; the release notes describe fixes but do not provide public advisory identifiers/details.

### Publisher-signed checksum manifest

Retrieved from the official Kiri download host:

- `https://download.runkiri.com/SHA256SUMS-linux`
- `https://download.runkiri.com/SHA256SUMS-linux.asc`
- `https://download.runkiri.com/kiri-archive-key.asc`

GPG verification returned **Good signature** from:

- UID: `Kiri Releases (Linux packages, download.runkiri.com)`
- Full fingerprint: `900CB63F75328B627AF5549353263AE758141A6B`
- Key type/size: RSA 4096
- Key creation: 2026-11-03
- Key expiry: 2031-11-02

The key fingerprint was pinned in CI before accepting the detached signature. The signed object is the checksum manifest, not a direct signature embedded in the Debian package. The .deb is authenticated by matching its SHA-256 against the verified manifest.

### Package hashes

| Package | Size | SHA-256 |
|---|---:|---|
| `kiri_0.2.2_amd64.deb` | 52,333,630 bytes | `639f64abb7f3bd063a80ed1744e891156351c56cf2ad502633c47536c397a961` |
| `kiri-lite_0.2.2_amd64.deb` | 2,877,882 bytes | `24798125ee50bb24db86594a9ee1469b1032d9b2ffd7da616b06e40763c723b9` |

Both package hashes matched:
1. The exact GitHub release asset digest.
2. The corresponding entry in the GPG-verified `SHA256SUMS-linux` manifest.
3. A fresh `sha256sum` calculation in CI.

### Maintainer-script provenance

The three package control scripts were extracted from each .deb and checked against the Git blob IDs from the signed v0.2.2 source tree:

- `postinst`: `72246f6b94cc17a5e59ffbdee21bf0abfc18cffa`
- `prerm`: `c5a8ec2a3f521957b2efd598d71b9fad32530f35`
- `postrm`: `9172a2bf9f4c14f27584197a6d131caa09d1112e`

Both `kiri` and `kiri-lite` matched all three expected blob IDs.

## CI implementation and exact evidence

Repository: `kenznguyen/btcquant-application`

Branch: `main`

Final tested source/workflow SHA: `fedb39fbb06d619ed2c30049946de58020dbe55d`

Workflow: `.github/workflows/kiri-linux-package-verification.yml`

Final workflow run: https://github.com/kenznguyen/btcquant-application/actions/runs/44666669891

- Run ID: `44666669891`
- Event: push
- Branch: `main`
- Exact head SHA: `fedb39fbb06d619ed2c30049946de58020dbe55d`
- Overall conclusion: **SUCCESS**

Jobs:

| Package | Job ID | Conclusion |
|---|---:|---|
| Kiri 0.2.2 full | `136057519290` | **SUCCESS** |
| Kiri Lite 0.2.2 | `136057519379` | **SUCCESS** |

Runner evidence for the final run:

- Ubuntu 24.04.5 LTS
- amd64
- Linux kernel `7.0.0-1017-azure`
- systemd `255.4-1ubuntu8.18`
- GitHub-hosted disposable VM
- Workflow permissions declared as empty; no repository checkout, project secrets, project data or deployment credentials used.

### Tests executed by both jobs

1. Record runner OS, architecture, kernel and systemd.
2. Download the pinned .deb over HTTPS.
3. Verify its pinned SHA-256.
4. Fetch the official checksum manifest, detached signature and publisher key.
5. Verify the pinned publisher key fingerprint.
6. Verify the GPG detached signature over the manifest.
7. Verify the package's manifest entry.
8. Verify the GitHub release tag signature via the GitHub API.
9. Compare extracted maintainer scripts against the source Git blob IDs.
10. Install package and assert `kiri.service` is neither active nor enabled immediately after fresh package installation.
11. Explicitly enable/start the service on the disposable runner.
12. Verify `/run/kiri/docker.sock` exists and has mode/owner/group `660:root:kiri`.
13. Query the Docker API and run `hello-world`.
14. Run `apt remove` and verify data remains.
15. Run `apt purge` and verify the test runner's Kiri data directories are deleted.

Both packages reported Kiri engine version 0.2.2 and passed the `hello-world` container smoke test.

### Package footprint and dependencies observed

**Full `kiri` package**

- Installed size: 167,288 KiB.
- Declared dependencies include `libc6 (>= 2.39)`, GTK 3 and WebKitGTK 4.1.
- On the Ubuntu 24.04.5 runner, apt installed 54 new packages and upgraded 4 packages; apt reported approximately 330 MB additional disk usage.
- Includes its own Docker CLI, Compose and buildx.

**`kiri-lite` package**

- Installed size: 8,928 KiB.
- Engine only; expects an existing Docker CLI.
- On the Ubuntu runner, apt installed only the `kiri-lite` package (no additional dependency packages).
- Passed the same service, socket, Docker API, hello-world, remove and purge lifecycle tests using the runner's preinstalled Docker CLI.

## Important behavior and security findings

1. A direct .deb installation creates the `kiri` group and installs the systemd unit, but the tested fresh installation did **not** start or enable `kiri.service`. Starting the engine requires a separate explicit setup/action.
2. The service runs the Kiri daemon as root. The Docker API socket is `/run/kiri/docker.sock`, mode `0660`, owner/group `root:kiri`.
3. Membership in the `kiri` group is root-equivalent: a member can create containers and mount arbitrary host paths. Do not add users casually.
4. The service unit may create a `/run/docker.sock` symlink to Kiri if that path is otherwise absent. Check the host's existing Docker socket/service before enabling Kiri.
5. `apt remove kiri` stops the service and retains images/containers/volumes under `/var/lib/kiri`.
6. `apt purge kiri` deletes `/var/lib/kiri`, `/var/lib/kiri-daemon`, `/run/kiri` and the `kiri` group. This is destructive to Kiri-managed container data.
7. Linux containers run on the host kernel; there is no VM boundary on Linux. Treat the runtime and its root-owned daemon as host-level infrastructure.
8. Avoid piping a remote installer directly into a shell for a controlled installation. Prefer downloading a pinned package, validating the signed manifest and package hash, inspecting it, then installing it explicitly.

## Recommended safe package for a future server evaluation

**Recommendation: prefer `kiri-lite` for a server that already has a Docker CLI.**

Reason: the CI proved the engine works through an existing Docker CLI, the package is substantially smaller, and it avoids the full package's GTK/WebKit dependency footprint. This is a package recommendation only, not authorization to install it on a project host.

Suggested sequence if a separate future installation approval is granted:

1. Download the exact `kiri-lite_0.2.2_amd64.deb` and the official checksum manifest, detached signature and public key.
2. Confirm the key fingerprint is exactly `900CB63F75328B627AF5549353263AE758141A6B`.
3. Verify the detached signature with `gpgv`.
4. Verify the exact package entry and run `sha256sum --check`.
5. Inspect `dpkg-deb --info`, `dpkg-deb --contents` and `dpkg-deb --control`.
6. Install with `sudo apt install ./kiri-lite_0.2.2_amd64.deb`.
7. Keep the service disabled until the operator explicitly approves runtime activation.
8. If activated, prefer a controlled privileged invocation through `DOCKER_HOST=unix:///run/kiri/docker.sock`; do not grant general `kiri` group membership without accepting its root-equivalent privilege.
9. Test an isolated container and verify host Docker socket behavior before considering any broader use.

Do not use `apt purge` unless deleting Kiri's images, containers, volumes and state is intended.

## Remaining verification gaps

- Ubuntu 26.04.1 compatibility: **NOT VERIFIED**.
- ARM64 Debian package: **NOT VERIFIED**.
- RPM packages: **NOT VERIFIED**.
- Docker Compose and buildx compatibility on this project's workloads: **NOT VERIFIED**.
- Existing Docker Engine coexistence on a real project host: **NOT VERIFIED**.
- T0/T1/T2 or application integration: **NOT TESTED / NOT AUTHORIZED**.
- Performance, load, kernel hardening and independent security audit: **NOT PERFORMED**.
- Persistent runtime, boot/autostart, deployment and production readiness: **NOT APPROVED / NOT VERIFIED**.

No separate workflow artifact was uploaded. The exact job logs and GitHub Actions run are the retained CI evidence.

## Final disposition

- Release/source provenance: **PASS**.
- Publisher-signed checksum manifest: **PASS**.
- Full .deb package integrity and source script parity: **PASS**.
- Kiri Lite .deb package integrity and source script parity: **PASS**.
- Ubuntu 24.04.5 amd64 install/service/container/uninstall lifecycle: **PASS — CI ONLY**.
- Kiri Lite suitability as the smaller server-oriented package: **RECOMMENDED FOR SEPARATE FUTURE EVALUATION**.
- Project VPS, project runtime, Docker replacement, T0/T1/T2, data and trading: **NOT TOUCHED**.
- Installation or deployment on any persistent host: **NOT APPROVED**.
