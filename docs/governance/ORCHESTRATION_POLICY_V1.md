# Orchestration Policy V1

- **Policy ID:** ORCH-POLICY
- **Version:** 1.1.0
- **Status:** APPROVED
- **Policy owner:** Project Owner
- **Applies to:** Personal BTCUSDT Quant System engineering workflows
- **Canonical location:** `docs/governance/ORCHESTRATION_POLICY_V1.md`
- **Plugin integration:** Not authorized by this policy approval

## 1. Purpose

This policy establishes one central intelligence and coordination model for engineering work, with AntiGem operating only as an execution environment. It also governs the selection of installed Skills and the use of connected engineering tools.

The model preserves ChatGPT's strengths in reasoning, context management, architecture, planning, review, and risk control while using AntiGem for authorized repository and development-environment operations. It reduces duplicated workflows, makes evidence sources explicit, and preserves project-specific authorization and safety boundaries.

The policy governs workflow selection and role boundaries. It does not install, remove, modify, or automatically execute Skills or Plugins. Approval of this policy does not authorize repository changes beyond this policy document, Plugin integration, deployment, runtime changes, or live trading.

## 2. Core principles

1. **Project Owner retains final authority.**
2. **ChatGPT is the Intelligence & Engineering Orchestrator.**
3. **AntiGem is an Execution Environment, not an independent orchestrator or decision authority.**
4. **`using-agent-skills` remains the sole primary coordinating Skill.**
5. Specialist Skills are invoked only when their distinct capability is needed.
6. Do not run duplicate TDD or Code Review workflows for the same task without a documented reason.
7. GitHub and Graphify are complementary evidence tools; neither replaces the other.
8. Superpowers is a reference workflow, not a second default orchestrator.
9. A Skill being available or read is not evidence that its workflow was executed.
10. Tool capability and execution must be reported only when directly verified.
11. Approval is specific to the stated repository, scope, files, actions, and purpose; it must not be inferred or expanded.

## 3. Operational roles and authority

### 3.1 Project Owner — final authority

The Project Owner:

- Owns project objectives, scope, and acceptance decisions.
- Approves or rejects plans and actions that require explicit authorization.
- Decides changes to repository scope, permissions, architecture baselines, and release boundaries.
- Retains final authority over commits, pushes, pull requests, merges, deployments, runtime changes, and other approval-gated actions.
- Resolves conflicts between proposed engineering approaches and project constraints.

Neither ChatGPT nor AntiGem may represent a proposal as owner-approved without explicit approval.

### 3.2 ChatGPT — Intelligence & Engineering Orchestrator

ChatGPT is responsible for the engineering intelligence and coordination layer:

- Interpret requests and maintain relevant project context, decisions, constraints, and handoffs.
- Analyze requirements, repository evidence, technical problems, and root causes.
- Define scope, assumptions, acceptance criteria, and verification requirements.
- Own the proposed architecture, technical design, implementation plan, and rollback strategy.
- Select and coordinate the primary Skill and only the necessary specialists.
- Review proposed diffs, implementation results, test output, CI evidence, and reported findings.
- Identify contradictions, risks, missing evidence, and approval requirements.
- Present decisions and unresolved issues to the Project Owner.

ChatGPT must distinguish verified facts from assumptions and AntiGem-reported results. It must not claim that repository inspection, a command, a test, or a workflow succeeded unless supported by evidence available in the conversation or retrieved through an authorized tool.

### 3.3 AntiGem — Execution Environment

AntiGem provides the technical environment in which authorized engineering operations may be performed. Its permitted functions, when within the approved scope, include:

- Inspecting repositories, files, source code, configuration, and development environments.
- Collecting technical facts and diagnostic output for ChatGPT's analysis.
- Preparing proposed patches and diffs that conform to the approved design.
- Applying approved code or documentation changes.
- Running specifically authorized commands, builds, tests, and validation procedures.
- Collecting logs, exact commit SHAs, CI run/job references, artifacts, and other evidence.
- Reporting actual changes, results, errors, limitations, and blockers.

AntiGem must not:

- Act as a competing or independent project orchestrator.
- Replace ChatGPT's architecture, planning, or review responsibilities with autonomous decisions.
- Change an approved design or acceptance criterion without returning the proposed change to ChatGPT for review and, where required, Project Owner approval.
- Expand repository, file, branch, or operational scope.
- Treat tool availability, agent capability, or a successful command as permission to perform an otherwise unauthorized action.
- Approve its own work or declare an approval-gated action authorized.
- Commit, push, create or merge pull requests, change CI/CD, deploy, modify runtime or database state, or perform live trading unless that exact action is explicitly authorized.
- Report unexecuted tests, inferred results, or unverified claims as evidence.

AntiGem may identify a better approach and submit it as a proposal. A proposal is not permission to implement it.

### 3.4 Relationship between ChatGPT and `using-agent-skills`

ChatGPT is the overall intelligence and engineering coordination authority in the assistant workflow. Within the Skills system, **`using-agent-skills` remains the sole primary coordinating Skill**.

The Skill orchestrates the selection and sequencing of specialist Skills. It does not replace Project Owner authority, and it does not create a second independent decision-making authority alongside ChatGPT. AntiGem is not a Skill orchestrator.

## 4. Primary coordinating Skill

The default primary coordinating Skill is **`using-agent-skills`**.

It is responsible for:

- Classifying the task and its development phase.
- Selecting one primary workflow.
- Identifying the minimum necessary specialist Skills.
- Avoiding duplicate or conflicting workflow execution.
- Defining verification and completion criteria.
- Stopping when requirements, source state, or authorization are unclear.

No other Skill or workflow should independently start a competing coordination process for the same task.

## 5. Specialist Skill selection

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

This table is a selection guide, not a requirement to invoke every listed Skill. ChatGPT, using the primary coordinating Skill, selects only what the task needs.

## 6. Duplicate workflow prevention

### 6.1 TDD

- Select one primary TDD workflow for a task.
- Do not execute Agent Skills TDD and Superpowers TDD as parallel or competing workflows by default.
- A second TDD procedure is allowed only when it covers a distinct test boundary not covered by the primary procedure.
- Record the reason and distinct scope when a second procedure is necessary.
- Do not claim tests passed unless they were actually executed and their results inspected.

### 6.2 Code Review

- Select one primary Code Review workflow for a review task.
- Do not run multiple equivalent review Skills by default.
- Independent review is a separate governance requirement; it does not justify duplicating the same review automatically.
- Preserve project- and layer-specific review requirements and exceptions.
- Report reviewer identity/capability and evidence accurately. Do not label a self-review as independent review.

### 6.3 Sequential specialist workflows

Different Skills may be used sequentially when each performs a distinct function. For example:

`debugging-and-error-recovery → test-driven-development → code-review-and-quality`

This is not duplicate execution: diagnosis, regression proof, and review are separate responsibilities.

## 7. Superpowers and Code Assistant policy

### 7.1 Superpowers

Superpowers may be consulted as a workflow reference when it contributes a procedure missing from, or materially improving, the selected primary workflow.

- Agent Skills remains the default coordination system.
- Do not automatically run Superpowers and Agent Skills workflows side by side.
- Do not duplicate brainstorming, planning, TDD, verification, or review steps.
- Record which Superpowers procedure was used and why it was needed.
- Do not claim subagent dispatch, parallel agent execution, or independent review unless the environment actually supports it and the action succeeded.

### 7.2 Code Assistant

Code Assistant is a specialist coding capability, not a competing default orchestrator.

It may provide implementation, explanation, debugging, architecture, or review assistance when needed. ChatGPT remains responsible for task coordination and duplicate-work prevention.

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
- Treat AntiGem's report as an execution report; verify material claims against the relevant source, logs, test results, or GitHub/Graphify evidence.
- Record the exact source SHA associated with each material verification result.

## 9. Standard engineering lifecycle

Use this nine-step lifecycle for engineering tasks. Apply the relevant work at each step, but do not bypass approval gates.

1. **Inspect:** Establish repository, branch, source SHA, working state, relevant files, and current evidence. AntiGem may gather repository facts within the authorized access scope.
2. **Understand:** ChatGPT consolidates the evidence, project context, constraints, and actual problem. Separate facts from assumptions.
3. **Define:** ChatGPT defines the outcome, exact scope, acceptance criteria, non-goals, risks, and verification requirements.
4. **Plan:** ChatGPT owns the technical design, implementation sequence, test strategy, and rollback approach. AntiGem may provide technical observations and proposed diffs as input.
5. **Review:** ChatGPT reviews the plan for correctness, consistency, security, scope, and compliance with existing decisions. Resolve contradictions before implementation.
6. **Approve:** The Project Owner explicitly approves actions that require authorization. No approval may be inferred from silence, tool availability, or an earlier approval for a different scope.
7. **Implement:** AntiGem performs only the approved actions, against the approved repository and scope. Any material deviation or newly discovered approval boundary stops execution and returns to ChatGPT and, where required, the Project Owner.
8. **Verify:** AntiGem executes only authorized verification and collects direct evidence. ChatGPT evaluates whether the evidence satisfies the acceptance criteria. Build success alone does not prove runtime or emulator acceptance.
9. **Report:** ChatGPT provides the consolidated outcome, exact SHA, actions performed, evidence, findings, limitations, and required next decision. AntiGem supplies factual execution details and evidence.

For read-only tasks, the entire lifecycle remains read-only: do not modify files, run tests, create commits, deploy, or change runtime state unless separately authorized. Preparing a plan or patch for review does not authorize applying it.

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

This policy applies to the BTCUSDT engineering workflows identified above. It does not automatically amend governance, instructions, permissions, or approval boundaries for another repository or project.

## 11. Completion status and reporting

Use these statuses:

- **PASS:** The stated acceptance criteria are supported by direct evidence.
- **PARTIAL:** Some criteria are verified, while others remain unproven or incomplete.
- **BLOCKED:** A required condition or authorization prevents completion.

For substantial tasks, report:

- Repository, branch, and exact source SHA.
- Primary coordinating Skill and specialist Skills actually used.
- AntiGem execution environment/actions actually used, when applicable.
- Tools actually invoked and the purpose of each.
- Tests and CI actually executed, including run/job evidence when available.
- Review status and whether it was independent.
- Findings, limitations, and unresolved risks.
- Required approval for the next action.

Never imply that a tool, Skill, test, reviewer, CI workflow, or runtime action succeeded without direct evidence. Distinguish an AntiGem-reported result from a result independently verified by ChatGPT.

## 12. Policy change control and Plugin boundary

- This file is the central reference for Orchestration Policy V1.
- Changes must be made through a versioned update or explicit amendment; do not silently alter the policy.
- Version 1.1.0 formalizes the approved ChatGPT-led engineering model: ChatGPT is the Intelligence & Engineering Orchestrator, AntiGem is the Execution Environment, and the Project Owner retains final authority.
- Policy approval does not automatically change installed Skills, Plugin instructions, repository permissions, or runtime behavior.
- Plugin integration requires a separate design proposal, compatibility testing, and explicit owner approval.
- This policy does **not** authorize Plugin creation, modification, installation, activation, or deployment.
- No Plugin integration or deployment may proceed solely on the basis of approval of this document.

---

**End of Orchestration Policy V1**
