# Maximum Automation — Explicit Approval for Permission Expansion

Date: 2026-11-22
Repository: `kenznguyen/btcquant-application`
Branch: `main`
Decision status: **OWNER APPROVED — GOVERNANCE POLICY**
Decision scope: governance and workflow policy only; existing technical approval boundaries remain in force.

## 1. Decision

Adopt **Maximum Automation — Explicit Approval for Permission Expansion**.

The project should automate the maximum practical amount of work within permissions and scope already approved by the owner. The system should not request repeated approval for routine substeps that are clearly necessary, bounded, reversible where applicable, and already covered by an active approval.

When the next useful step requires a new permission, broader scope, protected resource, or higher-risk operation, the system must prepare a specific approval request and wait for the owner's explicit decision before crossing that boundary.

This policy replaces a per-small-step approval habit with scope-based authorization. It does not grant blanket authority over the project.

## 2. Work that may be automated within existing authorization

Subject to repository permissions, active scope, and applicable safety constraints, automate:

- Read-only repository, branch, commit, documentation, issue, workflow and evidence inspection.
- Requirements analysis, planning, dependency mapping, risk assessment and identification of blockers.
- Implementation planning and preparation of code, tests and documentation.
- Source changes and refactoring explicitly covered by an active owner-approved scope.
- TDD, focused tests, approved regression suites, static checks and approved CI workflows.
- Bounded diagnosis and correction of failures within the approved scope.
- Evidence collection, integrity checks, concise evidence summaries and progress records.
- Updating handoff/evidence/decision records when supported by the approved work.
- Git commits on the existing approved branch when the change is within scope and repository policy permits it.
- Routine verification of commit SHA, workflow run/job, artifact metadata and resulting repository state.

Do not ask for a new approval merely because the approved task has multiple ordinary implementation, test, review or documentation steps.

## 3. Permission expansion protocol

When work cannot safely or correctly continue within current authorization:

1. Continue all independent work that remains within the approved scope.
2. Stop before the unapproved action or protected boundary.
3. Identify the exact additional permission required and why it is necessary.
4. Prepare a bounded approval request containing:
   - objective and reason;
   - exact repositories, files, resources, hosts, paths, datasets or services involved;
   - proposed actions and explicit exclusions;
   - data classification and security/privacy impact;
   - risk, failure behavior, rollback/recovery plan where applicable;
   - tests and evidence expected;
   - source SHA and branch baseline;
   - time/run limits and whether the permission is one-time or reusable.
5. Present the request as **REQUESTED — NOT AUTHORIZED**.
6. Wait for explicit owner approval, rejection or amendment.
7. Execute only the approved delta. An approval does not imply permission for adjacent or future work.
8. Record the decision and execution evidence in GitHub.

Silence, ambiguity, prior unrelated approval, successful tests, or technical capability are not approval.

## 4. Approval levels and boundaries

### Level A — Existing-scope autonomy

Routine actions already covered by a valid approval may proceed without another approval. Examples include source inspection, implementation, tests, bounded fixes, documentation and evidence updates within that scope.

### Level B — Permission expansion request

A new or broader scope must be proposed explicitly. Examples include a new data source, new host/path, new service, new dependency with material security impact, new workflow permission, new external integration, or access to a protected dataset.

No expanded action may start until the owner approves it.

### Level C — Protected/high-impact actions

The following always require explicit, specific owner approval unless a future decision names an exact bounded authorization:

- Accessing, downloading, parsing or transferring real source archives or private datasets.
- Opening, creating, modifying, migrating, promoting or deleting Canonical or other protected databases.
- Host, workstation, VPS, filesystem, mount, SSH, provisioning or deployment operations.
- Creating or changing credentials, secrets, permissions, external integrations or network exposure.
- Enabling services, background workers, autostart, scheduled execution or unattended operation.
- Deleting source data, private evidence, staging data or backups; changing retention or lifecycle behavior.
- Connecting T0/T1/T2 runtime components or changing their ownership/data boundaries.
- Changing Shared Risk Engine, Kill Switch, execution policy, account state or exchange connectivity.
- Paper/live order submission, live trading or any real financial transaction.
- Any irreversible, destructive, externally visible or materially security-sensitive action.

This list is a mandatory approval boundary, not an exhaustive grant of permissions.

## 5. Failure handling and bounded autonomy

- Use only approved commands, environments, data and resources.
- Retries must be bounded and follow the approved retry policy.
- Do not silently increase resource ceilings, change destinations, bypass tests, weaken checks, skip evidence, or transfer execution to another environment to get a passing result.
- If a test fails, diagnose and correct only within the approved scope. If correction requires expanded permissions, request them.
- Fail closed when scope, provenance, ownership, data integrity or authorization is uncertain.
- Never represent unverified work as PASS.
- Do not run unbounded agents, loops, jobs or background processes.

## 6. Evidence and GitHub governance

Automation does not reduce evidence integrity requirements. Use the minimum sufficient evidence package, while retaining all information needed to reproduce and audit the result.

For each meaningful work increment, record:

1. Work objective and exact scope.
2. Source commit SHA and relevant file/blob SHAs.
3. Commands, tests, results and exit codes.
4. Workflow run/job and artifact identifiers/digests/expiry when applicable.
5. PASS / BLOCKED / NOT VERIFIED status.
6. Next step and remaining unauthorized boundaries.
7. Approval request/decision reference whenever permission was expanded.

Do not fabricate workflow or artifact identifiers. If no artifact is produced, record that accurately. Keep sensitive data and raw source datasets out of public repository records and CI artifacts.

Commit on the existing approved branch where practical; avoid unnecessary branch divergence and do not force-push or bypass repository protections.

## 7. Relationship to existing decisions

This policy changes the **way approved work is carried out**, not the technical boundaries or outcomes of prior decisions.

- Existing owner approvals remain limited to their exact scopes and exclusions.
- GitHub Actions First remains the default CI policy; E2B remains an exception requiring its own bounded approval.
- B4 resource ceilings remain fixed unless separately changed by the owner.
- B6 source/staging/private evidence retention remains preserve-until-explicit-deletion-approval; CI artifact retention remains at most 30 days where applicable.
- B7 destination and preflight requirements remain unchanged.
- T0 remains independent of T1/T2 runtime unless separately approved.
- No archive access, real-data build, protected SQLite/Canonical operation, host preflight, deployment, credential use, runtime integration, exchange connectivity, trading or deletion is authorized by this governance decision.
- Existing manual/on-demand and no-autostart restrictions remain unchanged unless explicitly amended by a separate owner decision.

Where an older process required repeated approval for ordinary substeps already included in an approved scope, this policy supersedes that procedural friction. Where an older decision explicitly prohibits an action or reserves it for separate approval, that restriction remains effective.

## 8. Current implementation status

- Governance decision: **OWNER APPROVED**.
- Repository policy record: to be committed on `main`.
- Automatic enforcement across all workflows/tools: **NOT VERIFIED / NOT IMPLEMENTED**.
- Existing technical approvals: unchanged; must be checked before each bounded workstream.
- No source-code behavior, CI workflow, secrets, permissions, runtime, data, host, database or trading configuration is changed by this decision.

## 9. Operating rule

**Automate everything already authorized. When more authority is needed, prepare the smallest precise approval request, wait for the owner's decision, then continue automatically within the newly approved boundary.**
