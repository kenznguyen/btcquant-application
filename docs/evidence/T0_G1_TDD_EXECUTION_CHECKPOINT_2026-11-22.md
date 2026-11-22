# T0 G1 TDD Execution Checkpoint — 2026-11-22

## Scope requested
Continue the owner-approved G1 scope: test-first B4 Resource Policy; implement pure-Python helpers over synthetic metadata; test-first in-memory Importer Core; implement pure in-memory normalization/accounting/duplicate-conflict/coverage behavior; extend exact-SHA GitHub Actions to run focused tests and regressions.

## Authority and source
- Owner approval: `docs/decisions/T0_G1_SYNTHETIC_ONLY_CI_OWNER_APPROVAL_2026-11-22.md`, blob SHA `9f2dc8096c0a7b1c14cecc900bdfcd209a85fcca`; approval is full G1 scope bounded to the request.
- Current branch: `main`.
- Current source HEAD at inspection: `ab372a70db33a052ace8c0ebeb83e23caae44371`.
- Existing successful baseline CI: run `44990109927`, tested source SHA `caefbfabebe3dfc09eec87981bac5591d450ea6b`; 46/46 existing parser/header/provenance tests PASS and sanitized artifact verified. This is historical baseline evidence, not evidence for new B4/importer behavior.
- Existing strict parser blob: `10fe2313103c45d5455f17ff71f3fd0af2e6f038`.
- Existing provenance validator blob: `b94bac0f82ae141984552409f99a5cff70435b3b`.
- B4/B6/B7 frozen policy document blob: `948842998984b5b98d07a91ace82d2f822383932`.
- B4 resource policy and in-memory importer core modules are absent at inspected HEAD.

## Contract findings
- B4 numeric ceilings are fixed policy constants only; they are not source measurements. Helpers may validate synthetic metadata but must not perform host/disk/inode preflight or inspect archives.
- Safe-member classification must fail closed for absolute/drive paths, parent traversal, NUL, symlink, encrypted entries, duplicate normalized names and unsupported compression.
- Retry policy is limited to transient connection errors, HTTP 408, 429 and 5xx; maximum 3 attempts total; fixed 2s/10s backoff; Retry-After ceiling 10s; connect/read-idle/attempt timeout 10s/30s/120s; ZIP/run wall limits 10m/6h.
- Importer core must preserve all source rows, normalize exact S1.1 candle identity/value semantics, choose UNIQUE representative by lexicographic source_row_id, retain equal-value duplicates as IDENTICAL_DUPLICATE, and fail closed on conflicting values. Coverage calculations are exact timestamp-set operations, not inferred source coverage.
- Existing provenance validator must be reused, not duplicated.
- No SQLite, filesystem, network, archive, sidecar or real-source operation is within this work.

## Execution result
**BLOCKED BEFORE TDD RED.** No source, test or workflow file was changed in this checkpoint.
- The connected GitHub tools permit repository file reads/writes and inspection of Actions runs/artifacts, but expose no workflow-dispatch or arbitrary code/test execution action.
- No repository checkout is mounted in the execution container. Attempting a shallow clone failed because the container cannot resolve github.com.
- Therefore no exact-source RED test, syntax check, focused test, GREEN test, market_data regression, or repository regression could be executed. No unexecuted implementation or tests were committed, and no PASS is claimed.

## Required next step
Provide an execution path that can run the exact repository checkout and tests, or manually dispatch a test-only RED commit after it is prepared. Once execution is available, follow strict TDD:
1. Add B4 tests only; run them and capture RED.
2. Implement the pure resource-policy helpers; run focused GREEN.
3. Add importer-core tests only; run them and capture RED.
4. Implement pure in-memory importer core; run focused GREEN.
5. Extend the workflow to include both suites and the explicitly scoped `market_data` regression; run exact-SHA CI and inspect sanitized artifact.
6. Record exact source SHA, tested blob SHAs, commands, exit codes, workflow/job/artifact IDs and SHA-256.

## Status
- Baseline CI harness: **PASS** (historical exact SHA only).
- B4 tests / implementation: **NOT STARTED — BLOCKED**.
- In-memory importer tests / implementation: **NOT STARTED — BLOCKED**.
- Expanded workflow and regression: **NOT STARTED — BLOCKED**.
- G1 full scope: **PARTIAL / NOT COMPLETE**.

All existing exclusions remain in force: no archive/sidecar access, no filesystem extraction or host preflight, no SQLite open/create/write/DDL, no real-data importer/build, no Canonical T0 mutation/promotion, no T1/T2 runtime, no VPS/deployment, no credentials, exchange connectivity or trading.
