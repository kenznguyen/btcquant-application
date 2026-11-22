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


## Dispatch verification and artifact upload defect — 2026-11-22

- Manual dispatch run: https://github.com/kenznguyen/btcquant-application/actions/runs/44989899852
- Run ID: `44989899852`; attempt: 1; event: `workflow_dispatch`; workflow file was loaded from main at dispatch time.
- Requested/tested source SHA: `88b855dc8cf1935be77edbc837274b4800b85b52`. Job ID: `137108445328`.
- Exact checkout guard: **PASS**; log confirms requested SHA equals checked-out SHA.
- Runtime: CPython `3.13.18`; linked SQLite library `3.45.1`; minimum policy `3.37.0` — **PASS**. Metadata only; no SQLite connection/database operation.
- Existing synthetic parser/header/provenance suite: **46 tests PASS** (`Ran 46 tests ... OK`).
- Overall run: **FAIL**, solely at artifact upload. The workflow wrote evidence under hidden directory `.g1-evidence/`, while upload-artifact defaults `include-hidden-files` to false. Log: “No files were found with the provided path: .g1-evidence/”. Artifact list: zero artifacts; no artifact ID or SHA-256 exists.
- Bounded workflow fix committed on `main`: `caefbfabebe3dfc09eec87981bac5591d450ea6b`; workflow blob SHA: `bb9ace12c3b857a4f85c2581d6ead099aad9b254`. Change explicitly sets `include-hidden-files: true` for the sanitized evidence directory. This fix has **NOT YET BEEN DISPATCHED/VERIFIED**.
- Current conclusion: exact-SHA checkout and existing 46-test baseline **PASS** at source SHA `88b855...`; evidence artifact upload **BLOCKED on original run / FIX COMMITTED BUT NOT VERIFIED**; overall G1 harness **PARTIAL**. This is not completion of G1; B4 resource policy and in-memory importer-core implementation/tests remain absent.
- Next: manually dispatch the updated workflow with `source_sha=caefbfabebe3dfc09eec87981bac5591d450ea6b`; verify tests, artifact existence, contents, retention and checksum. Do not rerun or claim success for the earlier run.


## Successful exact-SHA rerun and artifact verification — 2026-11-22

- Manual run: https://github.com/kenznguyen/btcquant-application/actions/runs/44990109927
- Run ID `44990109927`, run number 2, attempt 1, event `workflow_dispatch`, conclusion **SUCCESS**. Workflow dispatch ref HEAD: `1e19946bc5f627e96ef02e86600a86426a2964f6` (the run's workflow-dispatch branch head; distinct from the exact requested source checkout).
- Requested source SHA: `caefbfabebe3dfc09eec87981bac5591d450ea6b`. Job `137109083853`; log confirms requested SHA and checked-out HEAD both equal this exact SHA.
- Workflow blob recorded inside artifact: `bb9ace12c3b857a4f85c2581d6ead099aad9b254`; parser blob `10fe2313103c45d5455f17ff71f3fd0af2e6f038`; provenance validator blob `b94bac0f82ae141984552409f99a5cff70435b3b`.
- Runtime metadata: CPython `3.13.18`; linked SQLite `3.45.1`; minimum `3.37.0` — **PASS**, metadata only.
- Synthetic parser/header/provenance baseline: **46/46 PASS** (`Ran 46 tests`, `OK`).
- Artifact upload: **PASS**. Seven sanitized files; artifact ID `14741746213`; name `t0-g1-synthetic-only-44990109927`; size `2,631` bytes; GitHub digest and independently recomputed ZIP SHA-256: `db42f2763befe9fc8c294537b0dfac4e448adf736892f599f292ca98cc6e0071`; created `2026-11-22T05:36:12Z`; expires `2026-12-22T05:36:11Z` (30 days).
- Artifact ZIP inspected. It contains only parser/provenance/workflow blob SHA text files, runtime metadata, source SHA, test summary and synthetic test log. No archive, sidecar, SQLite database, candle rows, secrets or host paths observed. Contents are sanitized and consistent with approved scope.
- Overall result for this baseline harness: **PASS**. The previous run `44989899852` remains historical failure; this successful rerun verifies the committed hidden-file artifact fix.
- G1 full implementation remains **PARTIAL / NOT COMPLETE**: B4 resource-policy implementation/tests and in-memory importer-core implementation/tests are not included in this baseline workflow yet. No B4/importer or real-data acceptance may be inferred.
- No archive/sidecar access, filesystem extraction of source data, SQLite connection/database operation, real-data importer/build, Canonical T0 mutation, T1/T2 runtime, VPS/deployment, credentials, exchange connectivity or trading occurred.
