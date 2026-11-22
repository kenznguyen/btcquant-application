# T0 G1 B4 Resource Policy — implementation checkpoint — 2026-11-22

## Scope
Implemented only `market_data/archive_resource_policy.py` on `main`, following the already verified B4 synthetic test contract. No test, workflow, parser, provenance, importer, data, runtime, or deployment files were changed by the source implementation commits.

## Source identity
- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Exact implementation SHA: `9c47817bfaea9e4bf830aa812508ae1ef4796e20`
- Parent: `d7932f826b16ba0abad4d14f8aac0822c09cc525`
- Changed source path: `market_data/archive_resource_policy.py`
- Final source blob: `87743432ec273bf5bd737d26bf2d489cc9fb34cf`
- Source scope: pure metadata validation, ZIP member classification, bounded retry-delay selection, and strict single-request/single-ZIP concurrency validation.

## TDD provenance
- RED source SHA: `d5db3e8af76c44d75c00bd457b3dccabba762f50`
- RED workflow run: [44990722096](https://github.com/kenznguyen/btcquant-application/actions/runs/44990722096)
- RED job: `137110968023`
- RED result: expected missing-module import error; existing parser/header/provenance tests 46/46 PASS.
- RED artifact: `14742195259`; SHA-256 `fbc3947a9e68c6a9a3a8cf4e34452e868169e294c0bf6ed9737a424a8433d4ae`.

## GREEN verification
**PASS — exact implementation SHA verified.**
- Workflow run: [44991196748](https://github.com/kenznguyen/btcquant-application/actions/runs/44991196748), run #4, attempt 1, `workflow_dispatch`; overall conclusion `success`.
- Job: `Synthetic-only tests`, job ID `137112408904`, conclusion `success`. All checkout, exact-SHA verification, test, summary and artifact-upload steps completed successfully.
- Requested source SHA: `9c47817bfaea9e4bf830aa812508ae1ef4796e20`; checked-out HEAD independently printed by runner: same exact SHA. The workflow run's dispatch branch HEAD is `b3dbda87c8cbb78d43906d040120823b05062af5`; this is not the tested source identity. The explicit source_sha input and checkout log establish the exact tested commit.
- Runtime: CPython 3.13.18; SQLite library 3.45.1; metadata-only SQLite minimum-version policy check PASS (3.45.1 >= 3.37.0; no database opened).
- Test result: **60/60 PASS** in 0.023s: parser 19, header contract 15, provenance validator 12, B4 resource policy 14. Log ends `Ran 60 tests`, `OK`.
- Artifact: ID `14741792967`, name `t0-g1-synthetic-only-44991196748`, 3,250 bytes, 8 files, expires `2026-12-22T05:51:50Z`; SHA-256 `97f2864bebe506b045dc3ab4224d5ca747eae94a421f19adc124eed65c0977e0`. ZIP downloaded and inspected. It contains only source/blob SHA manifests, runtime metadata, summary and test log.
- Artifact source identity manifest records requested and checked-out SHA both `9c47817bfaea9e4bf830aa812508ae1ef4796e20`. Source blob: `87743432ec273bf5bd737d26bf2d489cc9fb34cf`; parser blob `10fe2313103c45d5455f17ff71f3fd0af2e6f038`; provenance blob `b94bac0f82ae141984552409f99a5cff70435b3b`; B4 test blob `d9a4e8975cdba58eee5546818114442abf7dcab8`; workflow blob `a3067442ca30b2579e8c70c507f1a94ce29392e7`.
- Note: the workflow's historical step and summary labels still say `RED`, but they do not match this run's actual evidence: the checked-out B4 implementation exists, all 60 tests passed, and the workflow/run/job conclusions are success. Treat the actual checked-out SHA, test log, job and artifact as authoritative; clean up the stale labels in a separately scoped workflow/evidence change later.

## Guardrails preserved
No archive/sidecar reads, host or filesystem preflight, network acquisition, SQLite open/create/write/DDL, real-data importer/build, Canonical T0 mutation/promotion, T1/T2 runtime, VPS/deployment, credentials, exchange connectivity, or trading.

## Status
- B4 source implementation: **COMMITTED**
- RED provenance: **PASS**
- GREEN on exact implementation SHA: **PASS — 60/60**
- G1 B4 resource-policy test gate: **PASS**
- This closes the B4 implementation and exact-SHA GREEN gate only; it does not authorize archive access, preflight, importer-core, real-data import, Canonical T0 mutation/promotion, runtime, deployment, or trading.
- Next: preserve evidence and request the next separately approved scope before implementation.
