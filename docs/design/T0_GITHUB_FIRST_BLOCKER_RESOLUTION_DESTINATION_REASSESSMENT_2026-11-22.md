# T0 GitHub-First Blocker Resolution — Destination Reassessment Proposal

Date: 2026-11-22  
Repository: `kenznguyen/btcquant-application`  
Baseline main HEAD before this proposal: `da9497c4d684c6b95efba70579ab831b7015ed7b`  
Status: **PROPOSAL ONLY — NOT OWNER-ACCEPTED — NO WORKFLOW OR DATA EXECUTION AUTHORIZED**

## 1. Purpose

Reassess whether the project must select a personal workstation or VPS now, and determine which remaining T0 archive-reconstruction blockers can be closed using GitHub as the governance, source-control, test and evidence platform.

The latest owner decision approves a new SQLite reconstruction target as architecture only. It does not authorize archive retrieval, host preflight, SQLite, importer, tests/workflow creation or dispatch. The previous B7 decision selected Option A as a destination strategy, but did not identify a concrete device or absolute path. This proposal does not silently reverse that accepted decision; it recommends deferring concrete destination selection until a real-data execution phase is justified.

## 2. Recommendation

Adopt a **GitHub-first, destination-deferred** operating model:

1. Use the existing GitHub repository and `main` as the authoritative place for decisions, design contracts, implementation, test source, exact-SHA evidence summaries, workflow metadata and blocker tracking.
2. Use GitHub Actions hosted runners only for bounded source-code checks and synthetic-fixture tests after a separate workflow approval.
3. Do not select a workstation, provision a VPS, or create a persistent staging location now.
4. Keep all archive-dependent work BLOCKED until a suitable execution/storage destination is selected and separately approved.
5. Do not store raw ZIP archives, CHECKSUM sidecars, full reconstructed SQLite databases, raw candle rows, credentials or private acquisition evidence in GitHub Actions artifacts or the repository. The accepted B6 policy allows only sanitized CI evidence artifacts with a maximum 30-day retention; source/staging/private evidence must be preserved until a separate explicit deletion decision.

This allows software/design progress without pretending that GitHub is a durable archive vault or a verified data-processing host.

## 3. What GitHub can resolve without a data destination

| Blocker/work item | GitHub-first action | What can be claimed after evidence | Limit |
|---|---|---|---|
| S1.1 schema/provenance contract | Version-controlled design, schema-to-contract traceability, change review | Design consistency / documented decision | No executable DDL or SQLite until separately approved |
| S3 provenance validator | Exact-SHA source and synthetic regression workflows | Pure in-memory validator PASS | Does not validate real ZIPs or a database |
| B8 importer design | Specify deterministic importer contract and build synthetic fixtures/tests after approval | Synthetic importer behavior only | No real archive parse, SQLite build or staging |
| Runtime reproducibility | Pin Python and SQLite versions in a CI matrix; assert SQLite >= 3.37.0 and foreign_keys=ON per connection in isolated tests after approval | CI runtime compatibility for tested image/SHA | Does not establish the future host's exact runtime |
| B4 budget enforcement | Unit-test byte counters, ZIP metadata limits, path validation, timeout/retry state machines using synthetic inputs | Enforcement logic behaves as specified | Does not prove a runner or future destination has sufficient disk/inodes |
| B6 evidence policy | Keep sanitized summaries, SHA manifests, workflow/job IDs and test results in GitHub; configure artifact retention only after approval | Traceable, time-bounded CI evidence | GitHub artifact is not source/staging retention |
| B7 destination selection | Defer concrete host/path; document a future destination capability contract | No machine decision required for design/CI work | Does not authorize or satisfy preflight |

## 4. GitHub-hosted runner suitability

GitHub's current documentation lists standard Linux hosted runners with 14 GB SSD. Standard jobs run in a fresh runner instance. For private repositories, the standard Ubuntu runner is listed with 2 CPUs, 8 GB RAM and 14 GB SSD; larger managed runners are a separate offering with plan/availability/cost dependencies.

The accepted B4 policy requires at least 13 GiB free disk at preflight, in addition to an 8 GiB workspace ceiling and a 5 GiB runtime reserve. The 14 GB published SSD capacity is total runner storage, not a guarantee of 13 GiB free after the runner image and toolchain are present. Therefore:

- Standard hosted runner: **NOT VERIFIED / presumed unsuitable for the complete archive acquisition-and-staging workload** until a separately approved live preflight proves the exact free disk/inode values. Fail closed if the 13 GiB free-disk and 10,000 free-inode thresholds are not met.
- Larger hosted runner: possible future candidate only if the repository/account plan exposes a suitable size, its cost is accepted, and a separate preflight demonstrates the accepted B4 thresholds. No entitlement or availability is assumed.
- Self-hosted runner: not a shortcut; it still requires an owner-controlled host, encrypted storage, exact path, security controls and preflight. It would reintroduce the destination decision.
- GitHub repository/artifacts: not an acceptable persistent source archive or staging database location under the accepted B6 policy.

References:
- GitHub Docs — Choosing the runner for a job: https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job
- GitHub Docs — GitHub-hosted runners reference: https://docs.github.com/en/actions/reference/runners/github-hosted-runners

## 5. Blocker classification and next safe sequence

### GitHub-resolvable (documentation/source/CI only, each implementation phase still gated)

- Maintain a single blocker register with owner decision, exact source SHA, workflow run/job/artifact/checksum and PASS/BLOCKED/NOT VERIFIED status.
- Complete synthetic-only importer contract and RED/GREEN tests after explicit approval.
- Add deterministic schema/runtime compatibility tests after explicit approval.
- Add adversarial synthetic tests for B4 counters and fail-closed behavior after explicit approval.
- Add a sanitized evidence manifest format and artifact-content allowlist; do not upload artifacts until separately authorized.
- Keep T0 application foundation review PR #3/#4 as a separate track; do not treat archive-staging CI as closing those reviews.

### Requires real source evidence

- **B3:** H1/daily/monthly archive variants, member paths, encoding/BOM/newline/header evidence across the archive inventory. Synthetic fixtures can test parser behavior but cannot prove the actual source formats.
- **B5:** actual M15/H1 coverage, gaps, extras, duplicates and conflicting natural keys. These require source-derived parsing evidence. Historical row totals are not fresh evidence.
- REST tail remains closed by owner decision; MAY-10 remains excluded.

### Requires an execution/storage destination later

- Host/device ownership, encrypted volume, absolute root path, permissions, disk/inode capacity and manual-only execution preflight.
- Acquisition and source retention.
- Real SQLite staging build and read-only acceptance.
- Any Canonical promotion remains a separate owner decision after all acceptance gates.

## 6. Proposed phased plan

| Phase | Work | Destination | Approval status |
|---|---|---|---|
| G0 | Documentation, blocker register, exact-SHA source readback | GitHub repository | Documentation work only |
| G1 | Synthetic importer/parser/resource/runtime tests and isolated CI | GitHub Actions hosted runner | **Separate explicit approval required before workflow/test implementation or dispatch** |
| G2 | Bounded read-only source-format sampling and evidence capture | Not selected | **BLOCKED; requires source-access and destination decision** |
| G3 | Real acquisition and disposable SQLite reconstruction | Not selected | **NOT AUTHORIZED; requires destination/preflight and separate execution approval** |
| G4 | Read-only acceptance and possible promotion request | Approved staging location | **NOT AUTHORIZED; separate acceptance and promotion decisions** |

## 7. Security, ownership and non-actions

- No raw source archives, CHECKSUM sidecars, full SQLite files, raw candle data, secrets, signed URLs or unredacted HTTP payloads in GitHub repository/artifacts.
- No artifact retention changes or artifact upload without separate approval.
- No archive listing, inspection, download, decompression or parsing.
- No host/SSH/mount/filesystem access, provisioning, path creation or preflight.
- No workflow YAML changes, workflow dispatch, tests or CI artifact production under this proposal.
- No DDL, SQLite creation/open/write, importer implementation/execution, staging build or Canonical promotion.
- No deletion, cleanup, lifecycle rule, T1/T2 runtime, VPS deployment, systemd/autostart, exchange credentials, exchange connectivity or trading.
- Former Canonical SQLite remains LOST. Any future reconstruction starts as `RECONSTRUCTED — PARTIAL COVERAGE`.
- B4/B6 accepted policies remain unchanged. This proposal does not change B7's accepted Option A strategy; it recommends postponing selection of a concrete host/path and reassessing whether a larger managed runner could be a future bounded execution candidate.

## 8. Decision requested

Approve or reject the **GitHub-first, destination-deferred operating model** as an architecture/governance direction.

If approved, request a separate bounded implementation approval for **G1 synthetic-only CI**. That later request must specify exact files, tests, workflow permissions, source-SHA input, artifact allowlist/30-day retention, expected run/job evidence and exclusions.

No archive/data/SQLite/host/workflow action is authorized by approving this proposal alone.
