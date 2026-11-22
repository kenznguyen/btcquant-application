# T0 B4 / B6 / B7 Decision Package — Same-Session Self-Review

Date: 2026-11-22  
Review type: **SELF-REVIEW**; not an independent second-person review.  
Scope: documentation-only proposal for acquisition resource ceilings, evidence retention and execution destination.

## Reviewed source

- Proposal: docs/design/T0_B4_B6_B7_RESOURCE_RETENTION_DESTINATION_DECISION_PACKAGE_2026-11-22.md
- Final proposal blob at review: 9119b5789825951e66a061e4b9d989256934adec
- S1.1 accepted design baseline: 209c9d10cc0e54dc90148efa9ef6884f74aa143d
- Post-S3 blocker audit: docs/reviews/T0_POST_S3_BLOCKER_AUDIT_2026-11-22.md

## Review checklist

### B4 — resource budget

- [x] Existing cumulative transferred-response cap is preserved at 100 MiB; retries and partial/failed responses count toward it.
- [x] Per-object ZIP/sidecar caps are subordinate to the cumulative cap.
- [x] Compressed and uncompressed byte ceilings are separate; member, archive and run limits are all present.
- [x] ZIP central-directory count, member path length, unsafe path types, encryption, symlinks, nested archives and duplicate normalized paths are addressed.
- [x] Concurrency is serial; retries and timeout classes are bounded.
- [x] Disk arithmetic is internally consistent: 8 GiB workspace ceiling + 5 GiB reserve = 13 GiB minimum free space at preflight.
- [x] Inode preflight and runtime reserve are specified.
- [x] Cap breaches fail closed; no silent skipping, automatic cap increase, run splitting or automatic resume.

### B6 — retention

- [x] Source archives, acquisition evidence and staging data are distinguished from temporary CI artifacts.
- [x] CI artifacts are limited to sanitized metadata/evidence and proposed 30-day expiry.
- [x] Raw archives, sidecars, full database, raw candle rows, secrets and unredacted HTTP material are excluded from CI artifacts.
- [x] No automatic deletion/cleanup of source, staging or private evidence is proposed.
- [x] Destructive cleanup requires a later explicit owner decision naming exact paths/data.

### B7 — destination

- [x] Options A/B/C and their trade-offs are stated.
- [x] Option A is recommended but not selected on the owner's behalf.
- [x] No old VPS or historical /srv/btcquant/staging path is reused.
- [x] Exact host/path remain owner inputs; no host or capacity is invented.
- [x] Future preflight is separate and fails closed on any unverified ownership, mount, encryption, permission, path, disk or inode condition.
- [x] Manual/on-demand operation only; no systemd, cron, autostart or unattended resume.

## Limitations and open evidence

1. Numeric resource ceilings are engineering proposals, not measured against the actual archive set. B3 remains NOT VERIFIED beyond the single previously inspected M15 monthly sample.
2. The 100 MiB cap may prevent completion of the 404-object inventory. That is an intentional stop condition, not permission to increase the cap.
3. The 4 GiB uncompressed run ceiling, compression ratio and per-member ceilings may quarantine legitimate inputs; no source-derived size/ratio evidence exists.
4. The 13 GiB free-disk preflight requirement is a proposed minimum only. No destination has been selected or inspected.
5. Retention periods and artifact contents are proposed. No GitHub workflow retention setting or artifact upload has been changed.
6. Option A requires local execution or a separately designed/approved transfer mechanism; no such mechanism is implemented or authorized.
7. No archive, sidecar, host, path, filesystem, SQLite database or credential was accessed. No tests, workflow, preflight or operational command was run.

## Verdict

**SELF-REVIEW PASS WITH LIMITATIONS — THE DECISION PACKAGE IS INTERNALLY CONSISTENT AS A PROPOSAL. B4, B6 AND B7 REMAIN OPEN UNTIL THE OWNER MAKES THE THREE SEPARATE DECISIONS.**

This is not an independent review and does not prove source compatibility, host capacity, SQL correctness or operational readiness. No implementation or data activity is authorized.
