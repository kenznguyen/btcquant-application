# Orchestration Policy V1

- **Policy ID:** ORCH-POLICY
- **Version:** 1.0.0
- **Status:** APPROVED
- **Policy owner:** Project Owner
- **Applies to:** Personal BTCUSDT Quant System engineering workflows
- **Canonical location:** `docs/governance/ORCHESTRATION_POLICY_V1.md`
- **Plugin integration:** Not authorized by this policy approval

## 1. Purpose

This policy establishes one central coordination model for installed Skills and connected engineering tools. It reduces duplicated workflows, makes evidence sources explicit, and preserves project-specific authorization and safety boundaries.

The policy governs workflow selection. It does not install, remove, modify, or automatically execute Skills or Plugins.

## 2. Core principles

1. **One task — one primary coordinating Skill.**
2. Specialist Skills are invoked only when their distinct capability is needed.
3. Do not run duplicate TDD or Code Review workflows for the same task without a documented reason.
4. GitHub and Graphify are independent evidence tools; neither replaces the other.
5. Superpowers is a reference workflow, not a second default orchestrator.
6. A Skill being available or read is not evidence that its workflow was executed.
7. Tool capability and execution must be reported only when directly verified.

## 3. Primary orchestrator

The default primary coordinating Skill is **`using-agent-skills`**.

It is responsible for:

- Classifying the task and its development phase.
- Selecting one primary workflow.
- Identifying the minimum necessary specialist Skills.
- Avoiding duplicate or conflicting workflow execution.
- Defining verification and completion criteria.
- Stopping when requirements, source state, or authorization are unclear.

No other Skill or workflow should independently start a competing coordination process for the same task.

## 4. Specialist Skill selection

Use specialist Skills according to the task's actual needs.

| Capability | Preferred specialist |
|---|---|
| Requirements and specification | `spec-driven-development` |
| Task decomposition | `planning-and-task-breakdown` |
| Context preparation | `context-engineering` |
| Architecture and API contracts | `api-and-interface-design` |
| Implementation | `incremental-implementation` |
| Test-driven development | `test-driven-development` |
| Debugging | `debugging-and-error-recovery` |
| Code review | `code-review-and-quality` |
| Simplification | `code-simplification` |
| Security | `security-and-hardening` |
| CI/CD | `ci-cd-and-automation` |
| Documentation and decisions | `documentation-and-adrs` |
| Git workflow | `git-workflow-and-versioning` |

This table is a selection guide, not a requirement to invoke every listed Skill. The primary orchestrator chooses only what the task needs.

## 5. Duplicate workflow prevention

### 5.1 TDD

- Select one primary TDD workflow for a task.
- Do not execute Agent Skills TDD and Superpowers TDD as parallel or competing workflows by default.
- A second TDD procedure is allowed only when it covers a distinct test boundary not covered by the primary procedure.
- Record the reason and distinct scope when a second procedure is necessary.
- Do not claim tests passed unless they were actually executed and their results inspected.

### 5.2 Code Review

- Select one primary Code Review workflow for a review task.
- Do not run multiple equivalent review Skills by default.
- Independent review is a separate governance requirement; it does not justify duplicating the same review automatically.
- Preserve project- and layer-specific review requirements and exceptions.
- Report reviewer identity/capability and evidence accurately. Do not label a self-review as independent review.

### 5.3 Sequential specialist workflows

Different Skills may be used sequentially when each performs a distinct function. For example:

`debugging-and-error-recovery → test-driven-development → code-review-and-quality`

This is not duplicate execution: diagnosis, regression proof, and review are separate responsibilities.

## 6. Superpowers policy

Superpowers may be consulted as a workflow reference when it contributes a procedure missing from, or materially improving, the selected primary workflow.

- Agent Skills remains the default coordination system.
- Do not automatically run Superpowers and Agent Skills workflows side by side.
- Do not duplicate brainstorming, planning, TDD, verification, or review steps.
- Record which Superpowers procedure was used and why it was needed.
- Do not claim subagent dispatch, parallel agent execution, or independent review unless the environment actually supports it and the action succeeded.

## 7. Code Assistant policy

Code Assistant is a specialist coding capability, not a competing default orchestrator.

It may provide implementation, explanation, debugging, architecture, or review assistance when needed. The primary orchestrator remains responsible for task coordination and duplicate-work prevention.

Do not invoke a Code Assistant workflow that duplicates an already active specialist workflow without a distinct, documented purpose.

## 8. Evidence tools: GitHub and Graphify

GitHub and Graphify provide different, complementary evidence.

### 8.1 GitHub

Use GitHub for repository and version-control evidence, including:

- Repository, branch, and commit state.
- Exact commit SHA and source-file contents.
- Pull request state, reviews, and merge status.
- CI workflow runs, jobs, statuses, and artifacts when available.

### 8.2 Graphify

Use Graphify for repository-structure evidence, including:

- Indexed repository identity and indexed SHA.
- Symbol definitions and relationships.
- Callers, dependencies, and code impact.
- Structural navigation and graph-based analysis.

### 8.3 Evidence integrity

- GitHub does not replace Graphify; Graphify does not replace GitHub.
- Verify that the Graphify index corresponds to the source SHA being analyzed. If it does not, mark graph findings stale or refresh the index when authorized.
- Tie source claims to an exact GitHub commit whenever possible.
- Distinguish observed production call paths from test-only callers.
- Empty or missing tool results are not proof of failure or absence unless the query's coverage is established.
- Clearly distinguish static inspection, executed tests, CI evidence, runtime evidence, and independent review.

## 9. Standard task lifecycle

Apply the relevant gates for each task; do not run unnecessary stages.

1. **Scope Gate:** Define the requested outcome, boundaries, source repository/SHA, and authorization.
2. **Coordination Gate:** Select exactly one primary coordinating Skill.
3. **Specialist Gate:** Select only the specialist Skills needed for distinct capabilities.
4. **Execution Gate:** Perform only the authorized work; stop on unresolved requirements or permission boundaries.
5. **Evidence Gate:** Use GitHub and/or Graphify as appropriate, keeping their evidence roles distinct.
6. **Verification Gate:** Verify acceptance criteria using evidence appropriate to the task.
7. **Review Gate:** Apply the required review process and any layer-specific independent-review requirement.
8. **Completion Gate:** Report status, exact SHA, actions actually performed, evidence, findings, and unresolved risks.

For read-only tasks, execution must remain read-only: do not modify files, run tests, create commits, deploy, or change runtime state unless separately authorized.

## 10. BTCUSDT project safety and governance

This policy preserves the existing project constraints:

- The project is personal-use, not a SaaS or multi-customer service.
- Paper-first: no live trading and no real orders.
- No deployment, runtime start, systemd/autostart changes, or VPS operation without explicit approval.
- No database, canonical data-source, or data-retention changes without explicit approval.
- Preserve immutable revisions, exact SHA evidence, and approval gates.
- Preserve separation between Strategy Core and the independent AI strategy, their ledgers, Shared Risk Engine, and Kill Switch.
- Do not bypass shared risk admission or fail-closed controls.
- Preserve the existing T0 independent-review exception; do not extend it to other layers.
- Do not expand scope through unsolicited refactoring or adjacent changes.

## 11. Completion status and reporting

Use these statuses:

- **PASS:** The stated acceptance criteria are supported by direct evidence.
- **PARTIAL:** Some criteria are verified, while others remain unproven or incomplete.
- **BLOCKED:** A required condition or authorization prevents completion.

For substantial tasks, report:

- Repository, branch, and exact source SHA.
- Primary coordinating Skill and specialist Skills actually used.
- Tools actually invoked and the purpose of each.
- Tests and CI actually executed, including run/job evidence when available.
- Review status and whether it was independent.
- Findings, limitations, and unresolved risks.
- Required approval for the next action.

Never imply that a tool, Skill, test, reviewer, CI workflow, or runtime action succeeded without direct evidence.

## 12. Policy change control and Plugin boundary

- This file is the central reference for Orchestration Policy V1.
- Changes must be made through a versioned update or explicit amendment; do not silently alter the policy.
- Policy approval does not automatically change installed Skills, Plugin instructions, or runtime behavior.
- Plugin integration requires a separate design proposal, compatibility testing, and explicit owner approval.
- This policy does **not** authorize Plugin creation, modification, installation, activation, or deployment.
- No Plugin integration or deployment may proceed solely on the basis of approval of this document.

---

**End of Orchestration Policy V1**
