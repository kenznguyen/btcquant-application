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
**BLOCKED / NOT VERIFIED.**
- The current session's GitHub integration supports reading workflow runs/logs/artifacts but does not expose the `workflow_dispatch` action.
- No GREEN workflow run, job, or artifact exists for exact source SHA `9c47817bfaea9e4bf830aa812508ae1ef4796e20`.
- No test result is claimed. An empty commit-status response is not evidence of GREEN.
- Required owner action: GitHub Actions → `T0 G1 synthetic-only exact-SHA CI` → Run workflow; set `source_sha=9c47817bfaea9e4bf830aa812508ae1ef4796e20`. Then inspect exact checkout, all 60 expected tests (46 baseline + 14 B4), job conclusion, and sanitized artifact/digest. Treat this count as an expectation until the actual log confirms it.

## Guardrails preserved
No archive/sidecar reads, host or filesystem preflight, network acquisition, SQLite open/create/write/DDL, real-data importer/build, Canonical T0 mutation/promotion, T1/T2 runtime, VPS/deployment, credentials, exchange connectivity, or trading.

## Status
- B4 source implementation: **COMMITTED**
- RED provenance: **PASS**
- GREEN on exact implementation SHA: **NOT VERIFIED / BLOCKED**
- G1: **PARTIAL / NOT COMPLETE**
- Next: manually dispatch the exact-SHA workflow above, verify logs and artifact, then update this record and the session handoff with the run/job/artifact IDs and final status.
