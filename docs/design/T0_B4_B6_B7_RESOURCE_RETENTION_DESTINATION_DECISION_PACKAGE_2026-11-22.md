# T0 B4 / B6 / B7 — Resource, Retention and Execution Destination Decision Package

Date: 2026-11-22  
Status: **PROPOSAL FOR OWNER DECISION — DESIGN ONLY**  
Repository: kenznguyen/btcquant-application, branch main

## 1. Purpose and significance

S1.1 has frozen the provenance/schema contract. Acquisition and staging must not begin until the system has explicit resource ceilings, a retention boundary and a real owner-controlled destination. These decisions prevent decompression bombs, uncontrolled disk/inode consumption, unbounded retries, accidental loss of source evidence, and writes to an unowned or stale host/path.

This document is a decision package only. Numeric values are proposals, not measurements of the 202 ZIP files or target host. No archive access, host preflight, data transfer, database operation, workflow dispatch or cleanup was performed.

## 2. Fixed inputs and boundaries

- Inventory scope remains exactly 404 objects: 202 ZIP archives and 202 .CHECKSUM sidecars.
- Preserve the previously recorded cumulative transferred-response ceiling of **100 MiB** as a hard cap; do not increase it implicitly.
- Count all received response bytes across every object and every attempt, including partial/failed responses and retries, against that cumulative cap. ZIP and sidecar bodies both count.
- The former Canonical SQLite is LOST. Any future output remains labelled exactly **RECONSTRUCTED — PARTIAL COVERAGE**.
- MAY-10 remains excluded. The REST tail remains closed by owner decision and must not be requested again.
- The former VPS was deleted. The prior /srv/btcquant/staging path is not an approved destination.
- T0 remains independent of T1/T2 runtime and trading. Manual/on-demand operation only; no autostart or unattended worker.
- S1.1 design is owner-accepted. This package does not amend S1.1, S3 R3–R6, V1, T0ENC1, identity prefixes, schema contract ID or user_version=2.

## 3. B4 — Proposed acquisition and decompression resource budget

### 3.1 Proposed hard ceilings

| Resource | Proposed ceiling | Enforcement / failure behavior |
|---|---:|---|
| Total received response bytes, all 404 objects and retries | **100 MiB cumulative** | Hard stop before accepting bytes beyond cap; preserve attempt evidence; run cannot become CANDIDATE |
| One ZIP response body | **64 MiB** | Abort transfer when streamed bytes exceed cap; quarantine object |
| One checksum sidecar body | **64 KiB** | Abort and quarantine |
| One ZIP entry count | **1,024 entries** | Reject/quarantine archive if central directory exceeds ceiling |
| One member uncompressed size | **256 MiB** | Stop reading member and quarantine pair |
| One ZIP aggregate uncompressed bytes | **512 MiB** | Stop processing archive and quarantine pair |
| Entire run aggregate uncompressed bytes | **4 GiB** | Hard stop and quarantine run |
| Compression ratio | **100:1 maximum per member** | Compute from measured compressed/uncompressed sizes; zero/unknown compressed size fails closed |
| Member path UTF-8 length | **1,024 bytes** | Reject member path exceeding ceiling |
| Concurrent network requests | **1** | Sequential acquisition only |
| Concurrent ZIP processing | **1** | One archive at a time; no parallel decompression |
| Attempts per object | **3 total** (initial + 2 retries) | Retry only transient connection failures, HTTP 408, 429 or 5xx; do not retry deterministic 4xx; UNKNOWN remains fail-closed |
| Retry backoff | **2 s then 10 s** | Fixed bounded backoff; no unbounded retry loop |
| Retry-After | **10 s maximum** | If server asks for longer, stop retrying and record the attempt; do not exceed the approved backoff ceiling |
| Connect timeout | **10 s** | Record failed attempt |
| Read-idle timeout | **30 s** | Abort attempt, count received bytes |
| Total timeout per attempt | **120 s** | Abort attempt, count received bytes |
| Per-ZIP processing wall time | **10 min** | Quarantine pair |
| Entire acquisition run wall time | **6 h** | Stop run; do not silently resume or reuse failed run |
| Workspace size | **8 GiB maximum** | Stop writes before exceeding ceiling |
| Free disk at preflight | **13 GiB minimum** | Refuse start if less; covers the 8 GiB workspace ceiling plus 5 GiB reserve |
| Free disk reserve during run | **5 GiB minimum** | Stop before reserve is breached |
| Free inodes at preflight | **10,000 minimum** | Refuse start if less |
| Free inode reserve during run | **5,000 minimum** | Stop before reserve is breached |

The 64 MiB single-ZIP ceiling is subordinate to the 100 MiB cumulative response cap. An object may be below its individual cap and still be rejected because earlier objects/attempts consumed the cumulative allowance.

### 3.2 ZIP handling and path safety

- Inspect the central directory before member reads. Do not extract the archive tree to disk.
- Stream the candidate CSV member through a bounded reader; enforce per-member, per-ZIP and run-wide uncompressed counters while reading, not only from untrusted ZIP metadata.
- Reject encrypted members, symbolic links, absolute paths, drive-prefixed paths, NUL bytes, parent-directory components, duplicate normalized member paths and unsupported compression methods.
- Do not recursively unpack nested archives.
- Preserve every observed central-directory candidate and deterministic candidate identity under S1.1. A malformed candidate is evidence, not a reason to invent a valid member.
- A ZIP with zero or multiple candidate members may be represented as evidence but cannot pass the S1.1 verified-pair rule.
- Do not follow symlinks or write member paths to the filesystem. No path from an archive may select an output path.

### 3.3 Accounting and fail-closed rules

- Count response bytes as they arrive. Include failed HTTP bodies, interrupted bodies and retries; never reset the cumulative counter on retry.
- Check declared Content-Length as an early rejection hint, but enforce actual streamed byte count independently.
- If any cap, timeout, disk reserve or inode reserve is hit, stop the current run, preserve safely recordable attempt/failure evidence, mark the run QUARANTINED, and do not reuse the run ID or destination.
- Never auto-raise a cap, split a run to bypass the cap, skip an oversized archive, or silently continue with incomplete inventory.
- A new run after failure requires a new run ID and a separately approved scope/destination. No automatic resume is proposed.
- No source-derived archive sizes, compression ratios or target-host capacity are asserted by this proposal. Caps must be checked against approved source evidence and actual destination preflight before acquisition.

### 3.4 Trade-offs and recommendation

The proposed limits favor safety over guaranteed completion. A 100 MiB cumulative transfer ceiling may stop a run before all 202 ZIPs are transferred. A 4 GiB aggregate uncompressed ceiling may quarantine a legitimate archive set if actual data exceeds the proposal. This is preferable to silently expanding resource use.

**Recommendation:** approve the ceilings as hard initial limits for one bounded acquisition attempt, conditional on later source-format evidence and destination preflight. If the source set cannot fit, stop and return a measured blocker report; request a new explicit owner decision rather than increasing limits automatically.

## 4. B6 — Proposed source, staging and evidence retention policy

### 4.1 Data classes and proposed treatment

| Data class | Contents | Proposed location | Proposed retention |
|---|---|---|---|
| Source archive set | Original ZIPs and matching .CHECKSUM sidecars | Owner-controlled encrypted source directory | Retain until owner explicitly approves deletion; no automatic expiry |
| Acquisition evidence | Inventory raw bytes/hash, per-attempt records, HTTP status/byte counts, complete/partial digests, workflow/run/job/source SHAs | Private evidence directory; sanitized summary committed to GitHub | Private evidence retained with source set until explicit deletion approval; non-sensitive decision/evidence summaries remain in Git history |
| Staging dataset | Reconstructed SQLite database and related manifest | Separate owner-controlled staging directory, isolated by run ID | Retain until acceptance/rejection decision and any later explicit deletion approval; no automatic expiry |
| CI workflow artifact | Test logs, source/blob SHA manifest, checksums, sanitized run metadata | GitHub Actions artifact | **30 days maximum**; not durable data storage |
| Operational logs | Sanitized process logs and resource-limit events | Private run evidence directory | Retain with corresponding run evidence; no automatic cleanup |
| Credentials/secrets | Tokens, private keys, authenticated URLs | Protected secret storage only | Never place in artifacts, logs, Git, inventory or staging database |

### 4.2 Artifact contents and exclusions

A GitHub Actions artifact may contain only:
- exact requested and checked-out source SHA;
- workflow run/job IDs and workflow event;
- pinned source/test/workflow blob SHA values;
- runtime identity when a later approved SQLite phase exists;
- test results, exit codes and sanitized logs;
- SHA-256 checksums and artifact file inventory;
- bounded resource counters and failure classifications.

It must not contain:
- raw ZIP archives or checksum sidecars;
- full reconstructed database or raw candle/source-row data;
- credentials, bearer tokens, signed URLs, environment dumps or secret values;
- unredacted HTTP headers or response bodies;
- private hostnames, account identifiers or filesystem paths unless specifically approved and necessary for a private evidence package.

CI artifact retention should be set explicitly to 30 days. Before expiry, required non-sensitive evidence must already be committed to the repository. The artifact is temporary verification transport, not durable source or staging storage.

### 4.3 Deletion and cleanup authority

- No automatic deletion, TTL cleanup job, lifecycle rule, cleanup-on-success/failure, or log rotation that destroys required evidence is authorized by this proposal.
- Expiry of a GitHub Actions artifact is the only proposed automatic expiry, and applies only to the sanitized CI artifact described above.
- Deletion of source archives, sidecars, acquisition evidence or staging data requires a separate explicit owner decision naming the exact run/object/path and confirming that required evidence has been preserved.
- Failed/quarantined run directories must not be reused. They remain preserved until explicit deletion approval.
- No deletion is performed by preparing or accepting this policy.

### 4.4 Alternatives

1. **Preserve until explicit deletion approval (recommended):** strongest audit/recovery posture; uses more private storage and requires manual cleanup decisions.
2. **Fixed 180-day retention followed by a deletion request:** reduces long-term storage but still avoids automatic deletion; requires a future reminder/review mechanism, not authorized here.
3. **Automatic deletion after successful validation:** lowest storage use but risks destroying provenance and reproducibility; **not recommended**.

## 5. B7 — Execution destination decision

### 5.1 Options

| Option | Benefits | Risks / costs | Assessment |
|---|---|---|---|
| A. Owner-controlled personal workstation with encrypted local volume | Direct ownership, no new VPS, low recurring cost, manual/on-demand operation | Must remain powered during run; local disk capacity and backup are owner responsibilities; workflow must execute locally or transfer evidence through a separately approved mechanism | **Recommended for this personal-use project**, conditional on capacity and security preflight |
| B. Newly provisioned owner-controlled VPS with encrypted attached volume | Predictable availability and isolated environment | Recurring cost, provisioning/security work, remote attack surface; former VPS is deleted and cannot be reused | Viable fallback only with new explicit host/provisioning approval |
| C. Private object storage | Durable and scalable; lifecycle/access controls may be available | Third-party account, recurring egress/storage cost, credential and ownership dependencies; does not by itself provide a safe decompression/build host | Not recommended as first execution destination |

### 5.2 Recommended layout (logical only; no path is selected)

On Option A, the owner would select one dedicated root directory on an encrypted local volume. The following is a logical proposal, not an approved literal path:

    <OWNER_APPROVED_ROOT>/
      source/
        <inventory_id>/
          *.zip
          *.CHECKSUM
      runs/
        <run_id>/
          staging/
          manifest/
          logs/
          attempts/
      evidence/
        <run_id>/

Requirements:
- Dedicated non-root OS account; restrictive permissions (target directory mode 0700, files 0600 or equivalent ACL).
- Encrypted volume mounted before run; no fallback to an unencrypted root filesystem.
- Owner-controlled filesystem and mount; no network share or synchronized consumer folder unless separately reviewed.
- Create-only run directory; fail if run path already exists, is a symlink, or resolves outside approved root.
- Source directory is immutable after checksum verification; staging and source are separate.
- No credentials in the directory. No public/shared link.
- Manual invocation only. No service, systemd unit, cron, autostart, unattended worker or automatic resume.

### 5.3 Destination acceptance checklist (future preflight only)

A future separately approved preflight must verify and record:
1. Owner identity/ownership of host and filesystem.
2. Host OS/runtime and dedicated execution account.
3. Exact absolute root path and canonical resolved path.
4. Encrypted volume and mount source; fail if not mounted.
5. Directory owner, group, permissions and ACL.
6. Path is not a symlink; no path traversal; run directory is new/create-only.
7. At least 13 GiB free disk before start, at least 5 GiB reserve maintained, at least 10,000 free inodes and at least 5,000 reserve.
8. Workspace quota at or below 8 GiB and no other workload shares the reserved workspace.
9. No existing Canonical database or unrelated data will be overwritten.
10. No network exposure, public sharing or unapproved cloud synchronization.
11. Manual-only operation and no background/autostart process.

Any missing or unverifiable property means **PREFLIGHT BLOCKED**. Do not substitute another host, path, mount or storage provider.

### 5.4 Owner inputs still required

This package deliberately does not invent:
- host/device name or OS;
- exact absolute encrypted-volume mount path;
- available disk/inode capacity;
- whether local execution is feasible for the complete bounded run;
- whether a new VPS or private object storage is preferred instead.

Option A is recommended, but B7 remains OPEN until the owner identifies the exact host and path and a later separately approved preflight verifies them.

## 6. Decision summary

| Decision | Recommendation | Current status |
|---|---|---|
| B4 resource ceilings | Adopt §3 as initial hard caps; fail closed, no implicit expansion | **PROPOSED — OWNER DECISION REQUIRED** |
| B6 retention | Preserve source/staging/private evidence until explicit deletion approval; CI artifact 30 days, sanitized only | **PROPOSED — OWNER DECISION REQUIRED** |
| B7 destination | Option A: owner-controlled encrypted personal workstation; dedicated root/run layout; manual-only | **PROPOSED — OWNER IDENTIFICATION AND LATER PREFLIGHT REQUIRED** |

## 7. Scope and non-authorization

This document authorizes no operational activity. It does not authorize:
- archive listing, inspection, download, decompression or parsing;
- source-format verification or inventory acquisition;
- host provisioning, SSH, mount inspection, filesystem creation, permission changes or preflight;
- workflow YAML changes, workflow dispatch, artifact upload or retention setting changes;
- SQLite, DDL, importer, staging build, source-to-staging comparison or Canonical T0 access;
- automatic cleanup/deletion, retention jobs or lifecycle rules;
- T1/T2 runtime, VPS deployment, systemd/autostart, credentials, exchange connectivity or trading.

B3 archive format coverage and B5 source-derived coverage remain NOT VERIFIED. B8 importer/build remains NOT AUTHORIZED. Every later implementation, preflight, acquisition, build and acceptance phase requires its own explicit approval.

## 8. Decision requested from owner

Please decide each item independently:

1. **B4:** Accept, modify or reject the numeric hard ceilings in §3.1–3.3. Acceptance means design policy only; it does not authorize acquisition.
2. **B6:** Accept, modify or reject the retention proposal in §4. Acceptance does not authorize deletion or artifact upload.
3. **B7:** Select Option A, B or C. If Option A, provide the owner-controlled host/device and exact encrypted-volume root path in a later secure operational planning step. This selection alone does not authorize host access or preflight.

If any proposal is deferred, the corresponding blocker remains OPEN and acquisition remains blocked. No limits will be relaxed and no alternate destination will be substituted by inference.
