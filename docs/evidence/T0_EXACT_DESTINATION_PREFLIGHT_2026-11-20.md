# T0 Exact Destination Preflight — 2026-11-20

Date: 2026-11-20
Repository: `kenznguyen/btcquant-application`
Branch: `main`
Status: **BLOCKED — EXACT DESTINATION NOT VERIFIED; NO MATERIALIZATION**

## 1. Scope and authorization

This was limited to the read-only destination preflight defined in:
- `docs/plans/T0_RECONSTRUCTED_PARTIAL_SQLITE_STAGING_PLAN_2026-11-20.md` (blob `b35e25d5d52a09dc73cfb1ced91b408a4979b045`).
- `docs/decisions/T0_RECONSTRUCTED_ARCHIVE_MATERIALIZATION_APPROVAL_2026-11-20.md` (blob `87a2be9ea1ca16f1ce3d5a27a9349c1132da698b`).

Exact approved destination:
`/srv/btcquant/staging/t0-reconstructed-btcusdt-20261120-run-001`

No alternative destination was considered or used.

## 2. Execution environment qualification

The available command execution environment for this attempt was an isolated ChatGPT container, not the owner-controlled host/filesystem named by the approval. The read-only inspection returned:
- Effective identity: `uid=0(root) gid=0(root)` in the isolated container; this does not establish the intended owner identity on the approved host.
- `/`: directory, mode 0755, uid/gid 0:0.
- `/srv`: directory, mode 0755, uid/gid 0:0.
- `/srv/btcquant`: MISSING.
- `/srv/btcquant/staging`: MISSING.
- Exact target: MISSING.
- `findmnt -T` could not resolve the target because the parent path is absent.
- `df` byte and inode capacity checks could not run for the absent staging mount.
- `namei -l` stopped at the absent `/srv/btcquant` component.
- No directory was created and no filesystem was mounted.

These observations describe only the isolated ChatGPT container. They are not evidence about the owner-controlled staging host and must not be used to infer that the approved destination is absent on that host.

## 3. Preflight gate results

| Required check | Result | Evidence / limitation |
|---|---|---|
| Owner-controlled intended filesystem | NOT VERIFIED | Available container is not established as the approved owner host |
| Mount point, device/volume, filesystem type and options | NOT VERIFIED | Exact path is absent in the available container |
| Owner UID/GID, mode and ACL on target parents | NOT VERIFIED | Target parent chain absent; container root identity is irrelevant to target host |
| lstat of every component on approved host | NOT VERIFIED | Only isolated container inspected |
| Canonical path and no-symlink proof on approved host | NOT VERIFIED | Cannot resolve target on approved host |
| Outside Dropbox-synchronized roots | NOT VERIFIED | Host mount layout and Dropbox roots unavailable |
| Outside operational T0/database paths | NOT VERIFIED | Host filesystem topology unavailable |
| Target new/empty/create-only on approved host | NOT VERIFIED | Target state on approved host unknown |
| Free bytes/inodes and safety reserve | NOT VERIFIED | Target filesystem unavailable |
| Parent permissions prevent substitution | NOT VERIFIED | Approved host permissions/ACL unavailable |

**Gate verdict: BLOCKED / NOT VERIFIED.** The exact preflight has not passed. This is an access/environment limitation, not a finding that the approved destination itself is unsafe.

## 4. Explicit non-actions

- No DNS lookup, bucket listing, archive/object request or network transfer.
- No directory, file or mount was created or changed.
- No SQLite file was created, opened, initialized, written, imported or validated.
- No feeder, writer, lease, scheduler, API, VPS or runtime was started or accessed.
- No T1/T2 connection, Dropbox operation, restore, deployment, cleanup, retention or cutover.
- No alternate path was selected.

## 5. Required next step

Run this same read-only preflight from the actual owner-controlled host that owns the approved destination, capturing the host identity, mount/device/filesystem/options, lstat/no-follow inspection of every path component, Dropbox/T0 separation evidence, target state, byte/inode capacity, owner/mode/ACL and anti-substitution permissions.

If any required property fails or remains unverifiable, stop and obtain a new owner decision. Do not transfer any of the 404 archive objects until every exact-target preflight item is PASS and recorded.

Even after a successful preflight, this authorization covers only the approved raw archive materialization. SQLite creation/open/write/import remains separately NOT AUTHORIZED.

## 6. Verification metadata

- Preflight execution: read-only inspection in isolated ChatGPT container.
- Repository plan blob: `b35e25d5d52a09dc73cfb1ced91b408a4979b045`.
- Owner decision blob: `87a2be9ea1ca16f1ce3d5a27a9349c1132da698b`.
- GitHub Actions run/job/artifact: none; no workflow was run.
- Source/runtime SHA: no application source was executed or changed by this preflight.


## 7. Repeat preflight attempt (2026-11-20)

A second read-only attempt was performed in the available command container (hostname `12a89ff72da3`, effective identity `uid=1000(oai) gid=1000(oai_shared)`). This is still not established as the owner-controlled host named in the approval.

Observed in this container:
- `/` and `/srv` exist; `/srv` is mode 0755, uid/gid 0:0.
- `/srv/btcquant`, `/srv/btcquant/staging`, and the exact target do not exist.
- `stat` and `namei -l` confirm the path is unresolved at `/srv/btcquant`.
- `findmnt -T` cannot resolve the target.
- `df -B1` and `df -i` cannot inspect capacity for the absent target.
- A bounded search under `/srv` found no directory with a Dropbox-like name; this does not establish Dropbox separation on the actual owner host.

This second attempt does not improve the target-host evidence. All host-specific gates remain **NOT VERIFIED** and the verdict remains **BLOCKED**. No network requests, filesystem mutations, directory creation, SQLite operations or runtime actions were performed. No GitHub Actions run was triggered.
