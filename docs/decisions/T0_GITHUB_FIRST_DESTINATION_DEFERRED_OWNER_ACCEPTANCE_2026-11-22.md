# T0 GitHub-First, Destination-Deferred — Owner Acceptance

Date: 2026-11-22  
Repository: `kenznguyen/btcquant-application`

## Owner decision

**ACCEPTED — ARCHITECTURE / GOVERNANCE DIRECTION.**

The owner accepts the GitHub-first, destination-deferred operating model described in:

`docs/design/T0_GITHUB_FIRST_BLOCKER_RESOLUTION_DESTINATION_REASSESSMENT_2026-11-22.md`

GitHub is the authoritative control plane for project decisions, source control, design contracts, synthetic test source, approved CI execution, exact-SHA evidence summaries and blocker tracking.

A concrete workstation, VPS or persistent staging host/path is **not selected at this stage**. The accepted B7 Option A preference remains the preferred future destination strategy; this decision defers identifying a specific device and absolute path until real-data execution is justified. This decision does not establish that GitHub-hosted runners are suitable for archive acquisition or SQLite staging.

## Permitted direction

- Continue documentation and source-control work in the existing repository and `main`.
- Use GitHub Actions as a candidate environment for bounded synthetic/source-code CI, subject to a separate implementation approval.
- Maintain exact source SHA, workflow run/job/artifact/checksum and PASS/BLOCKED/NOT VERIFIED records.
- Keep archive-dependent work gated until source-access and destination requirements are separately approved.

## Explicitly not authorized

This acceptance does **not** authorize:
- G1 test/importer/parser/resource/runtime implementation or workflow YAML changes;
- workflow dispatch, CI artifact production or artifact-retention setting changes;
- archive/sidecar listing, inspection, retrieval, download, decompression or parsing;
- host/SSH/mount/filesystem access, provisioning, destination creation or preflight;
- DDL, SQLite creation/open/write, importer execution or staging build;
- raw ZIP, CHECKSUM, full SQLite/raw candle data or private acquisition evidence upload to GitHub;
- deletion, cleanup, retention execution, Canonical promotion, T1/T2 runtime, VPS deployment, systemd/autostart, exchange connectivity, credentials or trading.

B4 numerical resource limits and B6 evidence-retention policy remain unchanged. The 100 MiB cumulative response cap and other B4 limits remain design-frozen, not execution-tested. B6 remains: preserve source/staging/private evidence until a separate explicit deletion decision; sanitized CI artifacts maximum 30 days, but no artifact upload is authorized by this decision.

## Blocker status

- GitHub-first governance/control-plane direction: **OWNER ACCEPTED**.
- Concrete execution destination: **DEFERRED / NOT SELECTED**.
- Standard GitHub-hosted runner for full acquisition/staging: **NOT VERIFIED**; published total disk capacity does not prove the accepted free-disk/inode preflight thresholds.
- Synthetic-only G1 implementation: **NOT AUTHORIZED — REQUIRES SEPARATE OWNER APPROVAL**.
- B3 real archive-format coverage: **NOT VERIFIED**.
- B5 source-derived coverage: **NOT VERIFIED**.
- B8 real importer/SQLite build: **NOT AUTHORIZED**.
- Former Canonical SQLite: **LOST**. Any future reconstruction must remain labelled `RECONSTRUCTED — PARTIAL COVERAGE` until separately accepted.

## Next gate

Prepare a bounded G1 implementation request for owner review. It must enumerate exact files, tests, workflow permissions, exact-SHA inputs, artifact allowlist and retention behavior, expected evidence, and all exclusions. Preparing that request does not authorize implementation or dispatch.

No tests, workflows, jobs, artifacts, archive requests, host operations, database operations or runtime actions were performed by this owner acceptance.
