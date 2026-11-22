# T0 S1.2 — F2 DTO and read-only projection CI evidence

Date: 2026-11-22  
Repository: kenznguyen/btcquant-application  
Branch: main

## Scope

This increment implements the first F2 slice only:
- eleven frozen/slotted DTOs matching the physical S1.2 evidence relations;
- immutable `StagingProjection` result;
- `project_staging_database(connection)` accepting only a caller-owned `sqlite3.Connection`;
- explicit-column SELECTs with deterministic ordering for all eleven relations;
- schema/integrity/fingerprint verification and exactly-one-run plus initial BUILDING-event checks;
- no implicit path discovery, connection creation, archive access or external I/O.

Not yet implemented:
- full S3/V1 payload assembly and unchanged public-envelope projection;
- graph validator and cross-record invariants;
- complete runtime behavior tests for row-to-DTO mapping, read-only preservation, transaction behavior and all rejection paths;
- independent review.

## TDD evidence

### RED

- Test-only commit/source SHA: `a834c36a66653d3a859a02965eba29fb3bb0c3d6`.
- Workflow run: [45006770201](https://github.com/kenznguyen/btcquant-application/actions/runs/45006770201).
- Job: `137159996999`, `Importer-core synthetic tests`.
- Exact requested and checked-out SHA: `a834c36a66653d3a859a02965eba29fb3bb0c3d6`.
- Existing importer-core: 20/20 PASS.
- Adapter: 12 test cases; 11 DTO-presence subtests and projection-entrypoint assertion failed as expected.
- Full regression skipped because focused adapter RED stopped the workflow.
- RED is verified; this is an expected TDD failure, not a CI GREEN.

### GREEN

- Tested source SHA: `70f9a7759be1fb5279d6b0f1d82a38cb27cce951`.
- Workflow run: [45006885910](https://github.com/kenznguyen/btcquant-application/actions/runs/45006885910).
- Job: `137160352768`, `Importer-core synthetic tests`, conclusion SUCCESS.
- Exact requested/run/job checkout SHA matches: `70f9a7759be1fb5279d6b0f1d82a38cb27cce951`.
- Runtime: CPython 3.13.18; SQLite 3.45.1.
- Focused importer-core: 20/20 PASS.
- Focused S1.2 adapter: 12/12 PASS.
- Focused SQLite staging schema: 14/14 PASS.
- Complete `market_data` regression: 447/447 PASS (Python 3.12.16).
- Artifact endpoint: 0 artifacts; no artifact ID/digest.

## Exact source files at GREEN SHA

- `market_data/archive_staging_adapter.py`: blob `3c7e0237c57f4d2dbf8beb8e38cc6582f75a2171`.
- `market_data/test_archive_staging_adapter.py`: blob `5bbe9bf62838eb41954153af28e47175a79c1fe4`.
- `market_data/archive_staging_schema.py`: blob `56e7600fcf0d200098cfd4b875359b204956eb79`.
- `.github/workflows/t0-importer-core-synthetic.yml`: blob `0e319368fc36d8752f8e1640c3dd513dc18fd0ce`.

## Status

- DTO inventory and projection API surface: **PASS** at exact SHA.
- Synthetic CI and full market_data regression: **PASS** at exact SHA.
- Actual DB-to-DTO mapping semantics: **PARTIAL / NOT FULLY VERIFIED**; tests so far assert DTO immutability metadata and API signature, while broader row-mapping/read-only tests remain to be added.
- S3/V1 payload assembly: **NOT IMPLEMENTED**.
- Graph validator: **NOT IMPLEMENTED**.
- F1–F7 complete remediation: **NOT COMPLETE**.
- S1.2: **NOT FROZEN**.
- Independent review: **NOT RUN**.
- B8 and real-data staging: **NOT APPROVED**.

## Next step

Add synthetic tests for row projection correctness, read-only connection behavior, exact raw-byte/raw-JSON preservation, singleton/run-event rejection, and deterministic ordering. Then implement unchanged S3/V1 payload assembly and the pure graph validator with invariant-by-invariant RED/GREEN. Continue to record exact-SHA CI evidence.

## Exclusions

No archive/sidecar listing, download, extraction, parsing or sampling; no host/workstation/SSH/filesystem/disk/encryption/runner preflight; no B8 acquisition workflow/dispatch or runner registration; no real-data staging build/persistence; no upload, retention, deletion or cleanup; no Canonical T0 recovery/create/replace/migration/merge/promotion/cutover; no MAY-10, REST tail, T1/T2 runtime, VPS, deployment, credentials, exchange access or trading.


## Follow-up projection behavior tests — exact-SHA PASS

- Test commit/source SHA: `2b0c06cc3db6a73d5573dc75f7188306553bac13`.
- Workflow run: [45006997612](https://github.com/kenznguyen/btcquant-application/actions/runs/45006997612).
- Job: `137160698731`, conclusion SUCCESS; requested and checked-out SHA exactly match.
- Test blob: `c70c6e5b11b37e11bc6ef0695aede77c9d0cd6b0`.
- Focused importer-core: 20/20 PASS.
- Focused adapter: 15/15 PASS. New tests verify exact inventory_raw_bytes preservation, initial BUILDING event mapping, empty relation mapping, missing singleton rejection, missing initial BUILDING rejection, no implicit sqlite3.connect, connection remains usable and transaction state is unchanged.
- Focused schema: 14/14 PASS.
- Full `market_data` regression: 450/450 PASS.
- Artifact endpoint: 0 artifacts.
- This closes the immediate behavioral-test gap for empty/singleton-run projection and connection ownership. It does not yet verify populated mapping for all eleven relation DTOs, ordering with multiple rows, all SQL read-only mutation guards, or complete S3/V1 payload assembly.
- F2 remains PARTIAL: S3/V1 payload assembly and graph validator are still NOT IMPLEMENTED; independent review NOT RUN; S1.2 NOT FROZEN.


## Strict DTO field validation — exact-SHA GREEN

- Test-first RED commit/source SHA: `88e214e0e02a5dbbfe5d3839bac3953b92251fd7`; run [45007175284](https://github.com/kenznguyen/btcquant-application/actions/runs/45007175284), job `137161232664`; exact checkout verified. Four focused assertions failed because bool/zero/negative integer and empty/incorrectly typed required fields were accepted.
- GREEN source SHA: `a5f628b1c85c33879a9469ee1a6f90577f53d5d1`; run [45007240516](https://github.com/kenznguyen/btcquant-application/actions/runs/45007240516), job `137161422988`, SUCCESS; exact checkout SHA matches.
- Adapter source blob: `c29463798b5e21f0421ab1433a2f2de2a7f23a84`; adapter test blob: `13f48580d447239a6d7011b18e652bba082e7c9e`.
- Runtime: CPython 3.13.18 / SQLite 3.45.1.
- Focused importer-core: 20/20 PASS; adapter: 18/18 PASS; staging schema: 14/14 PASS; full `market_data` regression: 453/453 PASS.
- Artifact endpoint: 0 artifacts.
- DTO constructor validation now rejects nulls in required columns, non-text fields, non-bytes inventory BLOB, bool/negative/out-of-range SQLite integers, zero positive ordinals, invalid flag values, invalid singleton key, invalid HTTP status and malformed SHA-1/SHA-256 text.
- This is still not full F2. Populated relation mapping, all digest/ID recomputation, S3/V1 payload assembly, graph validation and independent review remain open.
