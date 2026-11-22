# T0 B4 / B6 / B7 — Owner Acceptance Record

Date: 2026-11-22  
Decision: **ACCEPTED — DESIGN/POLICY ONLY**  
Repository: `kenznguyen/btcquant-application`, branch `main`

## Owner decision

The owner explicitly accepted all three proposals in `docs/design/T0_B4_B6_B7_RESOURCE_RETENTION_DESTINATION_DECISION_PACKAGE_2026-11-22.md`:

1. **B4 — Resource budget: ACCEPTED.** Accept the numeric ceilings and fail-closed controls in §3, including the 100 MiB cumulative received-response cap, ZIP/member/run decompression ceilings, bounded concurrency/retries/timeouts, 8 GiB workspace ceiling, 13 GiB preflight free-disk minimum, 5 GiB runtime disk reserve, and inode thresholds.
2. **B6 — Retention policy: ACCEPTED.** Preserve source archives, sidecars, private acquisition evidence, staging data and operational logs until a separate explicit deletion decision. Sanitized CI artifacts have a proposed maximum retention of 30 days. No automatic deletion of source/staging/private evidence is allowed.
3. **B7 — Destination strategy: OPTION A ACCEPTED.** Select an owner-controlled personal workstation with encrypted local volume, dedicated restricted account/root, isolated create-only run directories and manual/on-demand execution.

## Interpretation and limits

This acceptance freezes the B4/B6/B7 design policies only. It does NOT authorize:
- host/device access, SSH, filesystem or mount inspection, destination preflight, provisioning or path creation;
- selecting/inventing a concrete host, device or absolute destination path;
- archive/sidecar listing, inspection, download, decompression, parsing or source-format verification;
- workflow changes/dispatch, artifact upload or changing GitHub artifact retention settings;
- DDL, SQLite, importer, staging database creation/build, source-to-staging comparison or Canonical T0 access;
- automatic cleanup/deletion, lifecycle rules or retention jobs;
- T1/T2 runtime, VPS deployment, systemd/cron/autostart, credentials, exchange connectivity or trading.

The Option A selection does not establish that the workstation has the proposed disk/inode capacity or that the full archive set fits the approved resource budget. A later separately approved preflight must verify ownership, encryption, exact path, permissions, free disk/inodes and manual-only execution. If any property is unverified, preflight remains BLOCKED. No alternate host/path may be substituted.

B3 archive-format coverage remains NOT VERIFIED. B5 source-derived coverage remains NOT VERIFIED. B8 importer/build remains NOT AUTHORIZED. The former Canonical SQLite remains LOST; any future reconstructed output must be labelled `RECONSTRUCTED — PARTIAL COVERAGE`. MAY-10 remains excluded and REST tail remains closed by owner decision.

## Status

- B4: **OWNER ACCEPTED — DESIGN FROZEN; IMPLEMENTATION/ACQUISITION NOT AUTHORIZED**.
- B6: **OWNER ACCEPTED — POLICY FROZEN; NO DELETION OR ARTIFACT UPLOAD AUTHORIZED**.
- B7: **OPTION A OWNER-SELECTED — PREFLIGHT NOT AUTHORIZED / NOT PERFORMED; EXACT HOST/PATH NOT YET RECORDED**.
- S1.1 remains separately owner-accepted and frozen.
- No tests, workflow run/job/artifact, host preflight, archive access or data operation was performed for this acceptance record.
