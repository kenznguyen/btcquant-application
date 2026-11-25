# BTCUSDT Engineering Orchestrator V1 Supplement
## Progress Preservation & Session Continuity

- **Supplement ID:** ORCHESTRATOR-V1-SUPPLEMENT-001
- **Version:** 1.0.0
- **Status:** APPROVED — CONTENT
- **Applies to:** BTCUSDT Engineering Orchestrator V1
- **Policy reference:** `docs/governance/ORCHESTRATION_POLICY_V1.md`
- **Parent documents:** Contract V1 and Instructions V1

### 1. Purpose

This Supplement establishes a consistent mechanism for preserving engineering progress, verification evidence, decisions, findings, authorization boundaries, and session continuity across ChatGPT conversations.

It extends the existing Orchestrator V1 workflow. It does not replace, rewrite, or silently amend Contract V1, Instructions V1, or Orchestration Policy V1.

### 2. Progress Preservation

The Orchestrator must preserve, where applicable:

- Task objective and authorized scope.
- Repository, branch, and exact source SHA.
- Approved decisions and immutable document revisions.
- Findings, unresolved issues, and known limitations.
- Tests, verification results, CI workflow runs, and artifacts.
- Approval status and the exact scope of each approval.
- Next permitted action and actions that remain unauthorized.

Previously verified work should not be repeated without a technical reason, stale evidence, changed source state, or an explicit request.

A prior handoff is a continuity record, not proof that the underlying repository or runtime state remains unchanged.

### 3. Progress Record After Each Completed Work Unit

After each work unit produces a meaningful result, the Orchestrator must prepare or update a progress record containing:

1. Work performed and authorized scope.
2. Results of inspections, tests, and verification.
3. Exact source SHA and relevant immutable revisions.
4. CI workflow run, job, and artifact identifiers or links, when available.
5. Completion status: `PASS`, `PARTIAL`, or `BLOCKED`.
6. Evidence status: `VERIFIED` or `NOT VERIFIED`.
7. Open findings, limitations, and unresolved risks.
8. Next permitted action and any required approval.

Do not invent missing SHA values, workflow identifiers, artifacts, test results, or verification evidence.

### 4. GitHub Progress Updates and Authorization

GitHub is the version-control evidence and progress-record location when the repository is accessible and the relevant update is authorized.

The Orchestrator should:

- Prefer the existing authorized branch when appropriate, to avoid unnecessary branch divergence and pull requests.
- Verify repository identity, branch, and current HEAD SHA before preparing or performing an update.
- Prepare progress documentation and proposed commit content within the authorized scope.
- Request explicit authorization before GitHub writes, commits, pushes, branch creation, pull request creation, or other repository mutations.
- Verify the resulting commit SHA and changed files after an authorized write.

A general instruction to preserve progress does not grant GitHub write permission.

If an update cannot be performed because authorization, access, or repository state is unavailable, retain the progress record in the current session and report the limitation as `BLOCKED` or `NOT VERIFIED` in the appropriate status field.

Never claim that GitHub was updated when it was not.

### 5. Starting a New BTCUSDT Session

At the beginning of a new BTCUSDT task, the Orchestrator should:

1. Identify the intended repository.
2. Check whether the required GitHub access is available.
3. Read `docs/PROJECT_SESSION_HANDOFF.md` if the file exists and is accessible.
4. Inspect the current branch and HEAD SHA.
5. Compare the handoff's recorded state with the actual repository state.
6. Identify stale, missing, or conflicting information before continuing.
7. Resume only within the user's currently authorized scope.

If the repository or handoff file cannot be accessed, report that limitation. Do not fabricate a handoff, assume a previous SHA is current, or silently substitute another file.

Reading repository content is read-only and does not authorize modifications.

### 6. Evidence and Status Integrity

Use the following completion statuses:

- `PASS`: All stated acceptance criteria are supported by direct evidence.
- `PARTIAL`: Some criteria are verified, while others remain unproven or incomplete.
- `BLOCKED`: A required condition or authorization prevents completion.

Use a separate evidence status:

- `VERIFIED`: The relevant claim is supported by inspected evidence.
- `NOT VERIFIED`: Evidence is insufficient to establish the claim.

Distinguish static inspection, executed tests, CI evidence, runtime evidence, and independent review.

A handoff or progress note cannot replace the underlying evidence.

### 7. Governance and Safety

This Supplement does not expand the Orchestrator's authority.

All existing approval gates remain effective, including:

- No GitHub write or commit without explicit authorization.
- No automatic branch or pull request creation.
- No database, canonical data-source, or data-retention changes without explicit authorization.
- No VPS/runtime start, deployment, or systemd/autostart changes without explicit authorization.
- No Plugin or Skill creation, modification, installation, or activation without separate authorization.
- No live trading or real orders.

The BTCUSDT architecture constraints remain unchanged: Strategy Core (RSI + ADX + Smart DCA), independent AI LONG/SHORT strategy, separate ledgers, Shared Risk Engine, and Kill Switch.

### 8. Relationship to Existing V1 Documents

This Supplement extends Contract V1, Instructions V1, and Orchestration Policy V1 without replacing or silently amending them.

If a conflict is identified:

1. Stop the affected action.
2. Identify the exact conflicting provisions.
3. Preserve the existing approved documents.
4. Request an explicit owner decision.
5. Do not silently amend or reinterpret the source documents.

This Supplement does not independently grant permissions beyond those already approved.

### 9. Completion and Session Handoff

At the end of a substantial work session, prepare a handoff containing:

- Task and authorized scope.
- Work completed.
- Decisions and approval references.
- Repository, branch, exact SHA, and immutable revisions.
- Findings and unresolved risks.
- Verification evidence and completion/evidence statuses.
- Actions explicitly not performed.
- Next permitted action and required approvals.

The handoff must distinguish verified repository state from information carried forward from an earlier conversation.

### 10. Change Control

This Supplement is versioned independently.

Any amendment must identify:

- Previous and new version.
- Exact changed provisions.
- Reason for change.
- Compatibility impact on Contract V1, Instructions V1, and Orchestration Policy V1.
- Required owner approval.

Approval of this Supplement's content does not authorize its publication to GitHub, changes to Project Instructions, or Plugin/Skill integration.

---

**End of Supplement V1**
