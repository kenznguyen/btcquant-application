# T0 G1 B4 Resource Policy — RED dispatch checkpoint — 2026-11-22

## Purpose
Prepare the first exact-source GitHub-hosted Actions execution for the owner-approved G1 TDD sequence. This checkpoint adds only synthetic B4 tests and wires them into the existing manual exact-SHA workflow. It intentionally does not add the resource-policy implementation, so the focused suite is expected to fail at import until GREEN implementation follows an observed RED run.

## Authority and branch
- Owner approval: `docs/decisions/T0_G1_SYNTHETIC_ONLY_CI_OWNER_APPROVAL_2026-11-22.md`; full bounded G1 scope approved.
- Repository: `kenznguyen/btcquant-application`.
- Branch: `main`; no feature branch or PR created.
- Previous HEAD before this checkpoint: `a8bebfe3b040b4dcac9af2cdde36ce28e72f8f63`.
- Test-only commit: `b436b29761ad10f6435a2bb4d0062fdedd69c972`.
- Workflow-wired commit / exact source SHA to dispatch: `d5db3e8af76c44d75c00bd457b3dccabba762f50`.
- Workflow blob at target source: `a3067442ca30b2579e8c70c507f1a94ce29392e7`.
- Test file: `market_data/test_archive_resource_policy.py` (introduced in test-only commit; source module `market_data/archive_resource_policy.py` intentionally remains absent).
- Workflow: `.github/workflows/t0-g1-synthetic-only.yml`, manual `workflow_dispatch` only, exact 40-char lowercase SHA validation and checkout verification, hosted `ubuntu-24.04`, minimal read-only contents permission, sanitized artifact retention 30 days.

## Test scope
Synthetic metadata only:
- frozen byte/entry/decompression/path ceilings;
- at/below and above-ceiling boundaries;
- compression-ratio and zero-compressed-size fail-closed cases;
- UTF-8 byte length for multibyte paths;
- malformed/missing/boolean/float/negative/overflow metadata;
- absolute, drive, traversal, NUL and duplicate path classification;
- symlink, encrypted and unsupported-compression rejection;
- transient vs deterministic HTTP status retry classification;
- max three attempts, Retry-After <=10s, fixed backoff;
- network and ZIP-processing concurrency exactly one.

Expected helper interface is defined by the test imports/assertions:
`RESOURCE_LIMITS`, `validate_resource_metadata`, `classify_zip_member`, `retry_delay_seconds`, `validate_concurrency`.
No implementation has been added yet.

## Execution status
**READY FOR MANUAL RED DISPATCH — NOT YET RUN.**
- This session can commit repository files and inspect Actions evidence but does not expose the GitHub Actions `workflow_dispatch` POST operation. Do not claim a RED result until the hosted run log records the expected import failure for the absent implementation module.
- Exact source SHA to dispatch in GitHub Actions UI: `d5db3e8af76c44d75c00bd457b3dccabba762f50`.
- Workflow should run the existing parser/provenance suite and the new B4 suite. Existing baseline tests should remain green; B4 should fail because implementation is intentionally absent.
- Expected outcome: overall workflow failure is the intended TDD RED signal. The artifact upload step runs with `if: always()` and should produce sanitized logs and SHA manifest. Verify exact checked-out SHA, job ID, test count/failure cause, artifact ID/name/size/digest/expiry before proceeding.
- If any failure occurs before the B4 test import (checkout, metadata, existing tests, runner setup), it is not a valid RED result; diagnose before changing implementation.

## Next step
Manually run workflow `T0 G1 synthetic-only exact-SHA CI` from the repository Actions tab with `source_sha=d5db3e8af76c44d75c00bd457b3dccabba762f50`. Share the resulting run URL/ID. After verifying the RED run and artifact, implement only the approved pure-Python B4 helpers, then add importer-core tests in a separate test-first step.

## Guardrails
No real archives or sidecars; no filesystem or host preflight; no network acquisition; no SQLite connection/create/write/DDL; no real-data importer/build; no Canonical T0 mutation/promotion; no T1/T2 runtime; no VPS/deployment; no credentials, exchange connectivity or trading. B3 archive format and B5 source-derived coverage remain NOT VERIFIED. G1 remains PARTIAL / NOT COMPLETE.


## Verified GitHub-hosted RED execution — 2026-11-22

- Run: [44990722096](https://github.com/kenznguyen/btcquant-application/actions/runs/44990722096), run #3, attempt 1, event `workflow_dispatch`; overall conclusion **FAILURE — expected for TDD RED**.
- Dispatch branch HEAD: `42ae329460c964550124d4812b75556084ca2d2f`. Explicit requested source SHA and checked-out HEAD both equal `d5db3e8af76c44d75c00bd457b3dccabba762f50`; validation, checkout and exact-SHA verification steps all **PASS**.
- Job ID: `137110968023`, `Synthetic-only tests`.
- CPython `3.13.18`; linked SQLite library `3.45.1`; metadata-only minimum-version check **PASS** (no SQLite connection/database operation).
- Existing parser, exact-header and provenance tests: **46/46 PASS**.
- B4 RED: suite load fails exactly at import of intentionally absent `market_data.archive_resource_policy` with `ModuleNotFoundError`. Total: 47 tests discovered, 1 expected import error. No implementation behavior was executed. This is the intended RED signal; not a GREEN or overall CI PASS.
- Artifact: ID `14742195259`; name `t0-g1-synthetic-only-44990722096`; 3,177 bytes; 8 files; created `2026-11-22T05:45:03Z`; expires `2026-12-22T05:45:02Z`. GitHub SHA-256 and independently recomputed ZIP SHA-256 match: `fbc3947a9e68c6a9a3a8cf4e34452e868169e294c0bf6ed9737a424a8433d4ae`.
- Artifact ZIP inspected. It contains only source/workflow/test blob SHA manifests, runtime metadata, source SHA, sanitized summary and test log; no archive/sidecar, raw market data, credentials, private host path or database content.
- Blob manifest values: parser `10fe2313103c45d5455f17ff71f3fd0af2e6f038`; provenance validator `b94bac0f82ae141984552409f99a5cff70435b3b`; B4 test `d9a4e8975cdba58eee5546818114442abf7dcab8`; workflow `a3067442ca30b2579e8c70c507f1a94ce29392e7`.
- Evidence assessment: **B4 RED VERIFIED; artifact integrity/sanitization PASS; G1 PARTIAL / NOT COMPLETE**. Do not mark overall workflow PASS because the expected RED import failure makes the run conclusion FAILURE.
- Next: implement only the approved pure-Python B4 resource-policy helpers against this test contract, preserve all existing contracts, then dispatch the exact implementation SHA for GREEN. Do not start importer-core tests until B4 GREEN is observed.
