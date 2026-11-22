# T0 G1 Synthetic-Only GitHub Actions Harness — 2026-11-22

Repository: `kenznguyen/btcquant-application`  
Branch: `main`  
Status: **WORKFLOW COMMITTED — MANUAL DISPATCH NOT YET RUN; G1 IMPLEMENTATION PARTIAL**

## Scope completed

Created `.github/workflows/t0-g1-synthetic-only.yml` as a manual-only exact-SHA GitHub Actions harness.

- Trigger: `workflow_dispatch` only.
- Required input: full 40-character lowercase hexadecimal `source_sha`.
- Checkout: exact requested SHA; the job compares `git rev-parse HEAD` to the requested value and fails closed on mismatch.
- Permissions: `contents: read` only.
- Runner: GitHub-hosted `ubuntu-24.04`; no self-hosted runner.
- Python: 3.13.
- Runtime metadata: Python implementation/version and linked SQLite library version; metadata-only, no SQLite connection or database operation.
- Current baseline tests: existing synthetic CSV parser, exact-header contract and provenance-validator GREEN tests.
- Artifact: sanitized test log, runtime metadata, source SHA and file blob SHA manifest; retention 30 days.
- No secrets are referenced.

## Exact source and workflow identity

- Workflow commit / current main HEAD: `88b855dc8cf1935be77edbc837274b4800b85b52`.
- Workflow blob SHA: `78a15fceffac1845f1454e36dbae4d37ddff7cb9`.
- Existing parser blob SHA: `10fe2313103c45d5455f17ff71f3fd0af2e6f038`.
- Existing provenance validator blob SHA: `b94bac0f82ae141984552409f99a5cff70435b3b`.
- Existing parser tests blob SHA: `50199cd168fd52314a846760cc4baf51a8cd5e9a`.
- Existing header-contract tests blob SHA: `fb102ace09f73e6233b5c577b6256665549c2ce0`.

## Verification

- Repository file creation/update: **PASS**.
- Exact-SHA input and checkout guard: present by source inspection; runtime verification **NOT RUN**.
- Workflow YAML/action runtime validation: **NOT RUN**.
- GitHub Actions workflow run/job: **NOT RUN**.
- Artifact ID, size, SHA-256 and expiry: **NOT AVAILABLE — no run**.
- Tests: **NOT RUN** in this session.
- The current workflow is a baseline harness only. B4 resource-policy implementation/tests and in-memory importer-core implementation/tests are not yet present; do not treat this workflow commit as completion of G1 or as proof of those contracts.

## Next step

Manually dispatch **T0 G1 synthetic-only exact-SHA CI** from GitHub Actions with `source_sha=88b855dc8cf1935be77edbc837274b4800b85b52`. Inspect the run, job log and sanitized artifact. Then extend the workflow to include the new B4 resource-policy and importer-core tests as those components are added using TDD.

## Explicit exclusions preserved

No archive or sidecar access; no filesystem extraction or host preflight; no SQLite open/create/write/DDL; no real-data parsing/import/build; no Canonical T0 mutation; no T1/T2 runtime connection; no VPS, deployment, credentials, exchange connectivity, or trading.
