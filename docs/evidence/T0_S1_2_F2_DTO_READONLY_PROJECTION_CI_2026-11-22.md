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


## S3/V1 payload assembly and graph validator — synthetic GREEN

- S3/graph test-first RED: commit/source SHA `d59ed7a0dbff8e3534e8d8419a424129c0db00aa`, run [45007382883](https://github.com/kenznguyen/btcquant-application/actions/runs/45007382883), job `137161868207`; exact checkout verified; expected missing API assertions failed.
- Initial implementation SHA `aee259f1f4442efd76c7f68d12b5854f4569baf6` failed because the module did not import `hashlib`; corrected by `1fcf708216bf52ba7807532bcd799e569aa8ca01`.
- First GREEN: run [45007483528](https://github.com/kenznguyen/btcquant-application/actions/runs/45007483528), job `137162183334`, SUCCESS; exact checked-out SHA matches; importer-core 20/20, adapter 20/20, schema 14/14, full regression 455/455 PASS.
- Complete synthetic physical-to-S3 integration test: test commit/source SHA `1fade80a7c57348a0da605fbc292ad0ceb9d5efe`; run [45007572947](https://github.com/kenznguyen/btcquant-application/actions/runs/45007572947), job `137162475080`, SUCCESS; exact checkout SHA matches; importer-core 20/20, adapter 21/21, schema 14/14, full regression 456/456 PASS.
- The complete synthetic S1 fixture contains 404 inventory objects, 404 attempts, 202 pairs, 202 members, 202 source rows, 202 candles and 202 links. Its physical DTO projection is converted to the unchanged S3/V1 collection/envelope shape; existing `validate_provenance()` accepts it; the added graph validator accepts its event/attempt/pair/member/source-row/candle/link/failure-observation graph.
- Artifact endpoints for both GREEN runs returned 0 artifacts.
- Implemented APIs: `build_s3_v1_payload(projection)`, `validate_staging_graph(projection)`, and `project_staging_s3_v1_payload(connection)`. The latter rejects any snapshot that does not pass both physical graph and existing S3/V1 validation.
- Remaining verification: the full fixture currently converts synthetic DTOs directly; populated SQLite row-to-DTO projection for every relation still needs a disposable DB integration test. Graph negative tests are not yet exhaustive for all contract invariants. Candidate snapshot digest binding and canonical coverage-manifest checks require additional explicit verification.
- F2 remains **PARTIAL**, despite these implementation and synthetic validation passes. S1.2 remains **NOT FROZEN**; independent review **NOT RUN**; B8 **NOT APPROVED**; real-data staging **NOT AUTHORIZED**.


## Populated SQLite → all eleven DTO relations — exact-SHA GREEN

- Test commit/source SHA: `6a71fe066e0ce80f9b3d580404682e5e2c216976`.
- Workflow run: [45007736688](https://github.com/kenznguyen/btcquant-application/actions/runs/45007736688).
- Job: `137162999481`, conclusion SUCCESS; exact requested and checked-out SHA match.
- Test blob: `69d708a198c201059df34e6210c699f9e533e2ac`; adapter source blob remains `78e82833fded534fc777dee2d2c7ed90dfd7ac61`.
- Runtime: CPython 3.13.18 / SQLite 3.45.1.
- Focused importer-core: 20/20 PASS; adapter: 22/22 PASS; staging schema: 14/14 PASS; full `market_data` regression: 457/457 PASS.
- Disposable in-memory schema-v2 test inserted synthetic rows across all eleven physical relations: reconstruction_run, run_events, archive_objects, acquisition_attempts, object_successful_attempt, archive_pairs, csv_members, source_rows, candles, candle_provenance_links, failure_observations.
- Verified DTO mapping values, deterministic ordering for objects/attempts/successful attempts, exact inventory BLOB bytes, exact raw_fields_json, and caller connection remains open/usable with transaction state unchanged.
- Artifact endpoint: 0 artifacts.
- This verifies populated DB→DTO projection for one complete synthetic graph sample. It does not prove all relation multiplicity/order edge cases, full event transition matrix, snapshot-digest binding, or all graph failure codes. F2 remains PARTIAL pending those cases and independent review.


## Coverage-manifest canonicalization and lifecycle binding — exact-SHA GREEN

- Canonical-manifest / VALIDATED-digest test RED: commit/source SHA `4752235995044868b5d059f5f9bd9661c5ce4f28`; run [45007845805](https://github.com/kenznguyen/btcquant-application/actions/runs/45007845805), job `137163340224`; two assertions failed as expected.
- Candidate/VALIDATED snapshot consistency RED: commit/source SHA `218790587755ad17ea318394c6a3335037596d70`; run [45007966306](https://github.com/kenznguyen/btcquant-application/actions/runs/45007966306), job `137163690155`; mismatch assertion failed as expected.
- GREEN source SHA: `589adf4124eb186df6f072069fdb5193a9953c3a`.
- Workflow run: [45008004977](https://github.com/kenznguyen/btcquant-application/actions/runs/45008004977), job `137163809455`, SUCCESS; exact requested and checked-out SHA match.
- Adapter source blob: `0ddd724c7e69d681333fa845c91a83852dd3420c`; adapter test blob: `0bcac7250f493e3a81cb57540f573bdee18bee1f`.
- Runtime: CPython 3.13.18 / SQLite 3.45.1.
- Focused importer-core: 20/20 PASS; adapter: 25/25 PASS; schema: 14/14 PASS; full `market_data` regression: 460/460 PASS.
- Added checks: coverage_manifest_json must equal deterministic compact UTF-8 JSON with sorted keys; VALIDATED event must include validator_payload_sha256; CANDIDATE and VALIDATED events must reference the same candidate_snapshot_sha256; no duplicate VALIDATED event.
- Artifact endpoint: 0 artifacts.
- Important unresolved contract gap: the design does not define the exact candidate snapshot digest preimage/serialization. The graph validator checks digest shape/presence and equality between CANDIDATE and VALIDATED events, but does **not** recompute the candidate snapshot SHA. Do not invent this formula. It needs an explicit owner-approved design amendment before digest recomputation can be implemented.
- F2 remains **PARTIAL** pending the digest formula decision, exhaustive graph negative tests, all F1–F7 re-verification and independent review.


## Expanded graph negative-invariant matrix — exact-SHA GREEN

- Test source SHA: `3e08ba4f9e326a9978d119cba54138cff0281f5e`.
- Workflow run: [45008115272](https://github.com/kenznguyen/btcquant-application/actions/runs/45008115272).
- Job: `137164142899`, SUCCESS; exact requested/checkout SHA match.
- Test blob: `d78c20e561fe921d73e9636a61fa7ca75f7b85cc`; adapter source blob remains `0ddd724c7e69d681333fa845c91a83852dd3420c`.
- Runtime CPython 3.13.18 / SQLite 3.45.1.
- Focused importer-core 20/20 PASS; adapter 33/33 PASS; schema 14/14 PASS; full `market_data` regression 468/468 PASS.
- New graph-negative tests cover nonmonotonic event timestamps, orphan failure observation, noncontiguous failure ordinals, missing successful-attempt relation, pair with missing object, member with missing pair, source row with missing member, and link/candle value mismatch.
- Artifact endpoint: 0 artifacts.
- Remaining: full multiplicity/ordering permutations, every failure branch and event transition combination; candidate snapshot digest formula still not defined by approved design and therefore not recomputed; F1–F7 complete regression after final source changes and independent review remain pending.


## Multi-row SQLite ordering — exact-SHA GREEN

- Test source SHA: `912ed3208851837302d979c4b4fa29f90e0effdf`.
- Workflow run: [45008220039](https://github.com/kenznguyen/btcquant-application/actions/runs/45008220039).
- Job: `137164470095`, SUCCESS; exact requested/checkout SHA match.
- Test blob: `e5019a825bb262f8f7f4173eb7568234dc836dfc`; adapter source blob remains `0ddd724c7e69d681333fa845c91a83852dd3420c`.
- Runtime CPython 3.13.18 / SQLite 3.45.1.
- Focused importer-core 20/20 PASS; adapter 33/33 PASS; schema 14/14 PASS; full `market_data` regression 468/468 PASS.
- SQLite rows are deliberately inserted in reverse order for objects, attempts, successful-attempt relations, run events and failure observations. Projection output remains deterministic by the specified order keys; failure observations are ordered by subject and failure ordinal.
- Artifact endpoint: 0 artifacts.
- Remaining ordering coverage: multi-row permutations for pairs, members, source_rows, candles and links are not yet individually exercised. The SQL has explicit ORDER BY keys for each relation, but those specific multi-row permutations remain NOT VERIFIED.


## F1–F7 synthetic closure pass and final exact-source CI — 2026-11-22

- Tested implementation source SHA: `d91c92a813ffe44c4ee786861e5e710654423c26`.
- Exact-SHA workflow run: [45010072833](https://github.com/kenznguyen/btcquant-application/actions/runs/45010072833).
- Job: `137170245583`, SUCCESS; workflow validated the requested SHA, checked out that exact SHA, and verified the checked-out SHA before running tests.
- Runtime: CPython 3.13.18 / SQLite 3.45.1 for focused suites; CPython 3.12.16 for full `market_data` regression.
- Results: importer-core 20/20 PASS; S1.2 adapter 43/43 PASS; SQLite staging schema 30/30 PASS; full `market_data` regression 494/494 PASS.
- Artifact endpoint: 0 artifacts.
- Source blob identities at tested SHA (verified equal to current main source blobs after documentation-only commits):
  - `market_data/archive_staging_schema.py`: `80393e2be87eafd0a2418dfbe48b91391712b8a2`
  - `market_data/test_archive_staging_schema.py`: `46eaf32514c5622b6f9fa7dacbdf4f1bc1a0a356`
  - `market_data/archive_staging_adapter.py`: `70bcf83c37936593e394c8476134046a7da70f4c`
  - `market_data/test_archive_staging_adapter.py`: `19cd18b40cb61252094b5805eb9d3cc35a7ff39b`
  - unchanged S3/V1 authority `market_data/archive_provenance_validator.py`: `b94bac0f82ae141984552409f99a5cff70435b3b`
  - shared synthetic S1 fixture `market_data/test_archive_provenance_validator_s1_red.py`: `41f5b21eaa418bb32f4f40e00de7e920ca39c4bf`
  - workflow `.github/workflows/t0-importer-core-synthetic.yml`: `0e319368fc36d8752f8e1640c3dd513dc18fd0ce`.
- F1: exact two append-only triggers are in the fingerprint and schema verification; tests reject missing, altered and extra triggers.
- F2/F3: all eleven DTO relation projections, populated SQLite→DTO integration, S3/V1 parity, reverse-insert ordering and additional graph negative invariants are synthetic GREEN.
- F4: singleton run envelope, initial BUILDING event and run lifecycle acceptance are synthetic GREEN.
- F5: lower-case hexadecimal digest/identity grammar is enforced at schema and DTO boundaries; malformed IDs/digests are rejected in tests.
- F6: file-backed test DB requires explicit opt-in, a new synthetic filename under a constrained temporary directory, exclusive creation, and rejects existing files/symlinks/alternate directories.
- F7: schema initialization is one BEGIN IMMEDIATE transaction; injected failures at table/index/trigger DDL and commit roll back all schema objects and user_version.
- Physical schema specification synchronized with Amendment A and B in documentation commit `f09136c563b026aa718629f6c774505f1b8362f3`; F2 implementation contract status updated in documentation commit `645d576be79533f187131207415e9b6b75b6cca7`. Current main HEAD at this evidence update is documentation-only beyond the tested source SHA; the seven code/workflow blobs above are identical at `d91c92a` and main.
- Remaining blocker: candidate snapshot digest preimage/serialization is not defined by the approved design. Current validator checks shape/presence and CANDIDATE↔VALIDATED equality; it does not recompute the digest. This requires a separate owner-approved design decision.
- Independent review has not yet run. S1.2 remains NOT FROZEN; B8 remains NOT APPROVED; real-data staging remains NOT AUTHORIZED.
