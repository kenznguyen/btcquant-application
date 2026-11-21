# E2B Usage Policy — GitHub Actions First, E2B Exception Only

**Date:** 2026-11-21  
**Status:** OWNER APPROVED — ARCHITECTURE / PROCESS DECISION ONLY  
**Repository:** `kenznguyen/btcquant-application`  
**Base source HEAD inspected:** `df3ce2338ff098331668bf6e82f7afdd896b6131`

## 1. Decision

The project adopts **GitHub Actions First — E2B Exception Only**.

- GitHub Actions remains the default CI system, default test runner, and primary source of official verification evidence.
- E2B is an optional, isolated supplementary environment. It may be considered only for a specific test or investigation that GitHub Actions cannot run or cannot adequately support.
- A test must not be moved to E2B merely because E2B can run it.
- A failed GitHub Actions run must not automatically be retried or transferred to E2B. Diagnose the failure first and establish that a concrete runner/environment limitation is responsible.
- E2B is not a second CI system and does not replace, shadow, or weaken GitHub Actions quality gates.

## 2. Eligible exception cases

E2B may be proposed only when a concrete limitation of GitHub Actions has been identified, for example:
- a required Linux/Python/package environment that the available Actions runner cannot provide;
- a sandbox-specific terminal or filesystem interaction that cannot be adequately exercised by the Actions runner;
- an isolated long-running or hard-to-reproduce investigation that is impractical or unsupported in Actions;
- a dependency/runtime compatibility investigation requiring a distinct disposable environment;
- AI research or experimental execution requiring a separate sandbox.

These are candidate cases, not blanket authorization. Each use requires a written reason explaining why GitHub Actions is insufficient, the exact test scope, data classification, environment, and expected evidence.

## 3. Responsibility and execution model

- ChatGPT may help analyze requirements, prepare code/tests, review logs, and interpret evidence.
- The owner manually supplies the approved source snapshot and receives the resulting evidence.
- E2B execution is independent and on-demand; it is not automatically connected to GitHub.
- Persistent project/session state must be stored in approved durable project records, not assumed to survive in an ephemeral E2B sandbox.
- No OpenAI API, MCP server, AI controller, or automated GitHub integration is required or authorized by this decision.

## 4. Isolation and prohibited access

E2B must not:
- write to the canonical repository, push commits, open/merge PRs, or mutate GitHub state;
- connect to VPS or any project runtime;
- connect T0, T1, or T2 runtime components;
- access or mutate the independent Canonical T0 database or production-like market-data store;
- receive Binance API secrets, exchange credentials, trading tokens, or other execution credentials;
- submit, simulate through live endpoints, or place real exchange orders;
- alter Shared Risk Engine, risk policy, Kill Switch, account state, or execution settings.

Only explicitly approved, minimized fixtures or research copies may be supplied. Do not copy the complete Canonical SQLite database into E2B. T0 remains an independent data asset.

## 5. Evidence requirements

Every approved E2B test must record:
- exact source commit SHA and relevant file/blob SHAs;
- test purpose and why GitHub Actions is insufficient;
- sandbox image/runtime, dependency versions, and relevant configuration;
- exact command and test selection;
- start/end status, exit code, logs, and generated artifacts;
- SHA-256 for each retained artifact;
- data/credential access boundaries and confirmation that prohibited resources were not accessed.

E2B evidence is supplementary and must be labeled as such. It does not replace a GitHub Actions run, does not make an unverified change PASS, and does not imply runtime or production readiness.

## 6. Approval and repository update procedure

Before each E2B use, obtain explicit owner approval for its bounded scope. After execution, inspect and verify the evidence before proposing any repository update. GitHub updates follow the project governance sequence:
1. record work and exact scope;
2. preserve test results and evidence;
3. record source SHA, workflow run and artifact identifiers where applicable;
4. assign PASS / BLOCKED / NOT VERIFIED accurately;
5. state next steps and unapproved boundaries;
6. commit on the existing approved branch where practical, avoiding unnecessary branch divergence.

No automatic commit or upload from E2B is permitted.

## 7. Current implementation status

- Architecture/policy decision: **APPROVED**.
- E2B account, plan, and sandbox availability: **NOT VERIFIED**.
- E2B sandbox creation or execution: **NOT STARTED**.
- GitHub/E2B integration: **NOT IMPLEMENTED / NOT AUTHORIZED**.
- GitHub Actions remains the active default CI path.
- No tests or workflows were run for this documentation-only decision; no workflow run or test artifact exists for this record.

## 8. Explicit non-authorization

This decision does not authorize source-code changes, workflow changes, E2B provisioning, repository integration, data export, VPS/runtime activity, deployment, trading execution, or real orders. Each requires a separate bounded approval.
