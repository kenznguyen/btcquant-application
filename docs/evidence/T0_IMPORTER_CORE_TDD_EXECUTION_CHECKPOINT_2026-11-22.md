# T0 Importer-Core TDD Execution Checkpoint — 2026-11-22

Repository: `kenznguyen/btcquant-application`
Branch: `main`
Inspected HEAD: `e64a5526db0f1aaaf51cf634fb43092ddec3526f`
Scope authority: `docs/decisions/T0_IMPORTER_CORE_SYNTHETIC_TDD_SCOPE_APPROVAL_2026-11-22.md`
Approval commit: `89b9e41e3608f75839e7c5fae7a3a0691ee716b9`

## Purpose

Begin the separately approved synthetic-only importer-core TDD phase while preserving the strict RED-before-GREEN evidence rule and avoiding unverified source changes.

## Read-only inventory

- `market_data/archive_csv_parser.py` exists; blob `10fe2313103c45d5455f17ff71f3fd0af2e6f038`.
- `market_data/test_archive_csv_parser.py` exists; blob `50199cd168fd52314a846760cc4baf51a8cd5e9a`.
- `market_data/archive_resource_policy.py` exists; blob `87743432ec273bf5bd737d26bf2d489cc9fb34cf`.
- `market_data/test_archive_resource_policy.py` exists; blob `d9a4e8975cdba58eee5546818114442abf7dcab8`.
- Parser contract is already implemented and existing parser/resource-policy tests are present. The inspected `market_data` directory listing did not contain `archive_importer_core.py` or an importer-core test module.
- Existing parser API and B4 resource policy were read for compatibility. No changes were made to them.
- Existing G1 workflow is present at `.github/workflows/t0-g1-synthetic-only.yml`, blob `a3067442ca30b2579e8c70c507f1a94ce29392e7`; however, workflow modification or dispatch is explicitly outside this approval.

## Execution capability check

**BLOCKED BEFORE RED.**

- The connected GitHub tools available in this session provide repository reads and GitHub Contents API writes, but no `workflow_dispatch`, Actions workflow creation, or code execution operation.
- No local repository checkout is mounted in the execution environment. A filesystem check found no project checkout.
- Therefore, the exact repository source and proposed tests cannot be executed here. A GitHub source write alone would not prove the required RED result.
- No importer-core tests were added, no implementation source was written, no tests were run, and no workflow was dispatched.
- Do not infer RED from a missing module import without actually running the focused tests at the exact source SHA.

## Status

| Item | Status |
|---|---|
| Owner scope approval | PASS |
| Main HEAD inspected | PASS — `e64a5526db0f1aaaf51cf634fb43092ddec3526f` |
| Existing parser/B4 source inventory | PASS |
| Importer-core test-first RED | BLOCKED — no exact-source execution path |
| Importer-core implementation | NOT STARTED |
| GREEN / market_data regression | NOT RUN |
| Workflow / artifact | NOT AUTHORIZED and NOT RUN |
| Source/runtime/data side effects | NONE |

## Next step

Obtain an exact-repository execution path that can run the checked-out `main` source (for example, an owner-provided local checkout with Python execution, or a separately approved importer-core test workflow). Once available, add only the focused synthetic importer-core tests, run them at the exact pre-implementation SHA to capture RED, then implement the minimum pure in-memory module and run GREEN plus the complete `market_data` suite.

If a workflow is proposed, request separate approval first because workflow edits/dispatch/artifacts are excluded from the current source-and-unit-test authorization.

## Exclusions reaffirmed

No real archive/sidecar access, network acquisition, host/filesystem preflight, SQLite open/create/write/DDL, staging, real-data importer, Canonical T0/MAY-10, T1/T2, VPS/runtime/deployment, credentials, exchange connectivity, trading, deletion or cleanup.
