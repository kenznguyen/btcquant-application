# T0 S1.2 — Synthetic SQLite Staging Schema V2 CI Evidence

Date: 2026-11-22
Repository: kenznguyen/btcquant-application
Branch: main
Scope: schema v2 module, synthetic-only tests, disposable SQLite databases, exact-SHA CI

## 1. Source and commit record

Test-first and implementation sequence:

- RED tests: `market_data/test_archive_staging_schema.py`, commit `bb4d743c151e387bbf1ca66fe6715680fb9a7fb3`.
- Workflow inclusion: `.github/workflows/t0-importer-core-synthetic.yml`, commit `d78170cf084f988ef83f8fe79ee85a1d43b1f584`.
- Initial schema implementation: commit `ec619151e33e6c924e2a3fa36b1a708db1c16b95`.
- NULL guards and composite same-object FK test hardening: commit `fd908d68ad443def7d5955b1784c4385959cd1f0`.
- Append-only triggers and exact schema-object/fingerprint verification: commit `9c250066905432753662d38a60d6227df731b8b8`.
- Database-level trigger proof: commit `1e96ed2bcf445c850c1a91193c5b67383f1bc79b`.
- Disposable file-backed database coverage: commit `6969769c602eca9e23bb613b52b590360d77177e`.
- SQLite STRICT runtime gate: commit `e8a6517ca1b7801e091bbedb35b107e343534093`.
- Lowercase digest regression tests: commit `d0fc2dac6fe12130352467ebe68f7f9b8a6c8f41`.
- Lowercase SHA-1/SHA-256 SQL grammar enforcement: commit `fdb4c0cde31d8a1a5b9a1079fa05fcbe5a82ba50`.

Final tested source SHA (workflow run #16): `fdb4c0cde31d8a1a5b9a1079fa05fcbe5a82ba50`.

Final source blobs:
- `market_data/archive_staging_schema.py`: `463a0cb564d2061437a1a9a5a78eca67789c9a36`.
- `market_data/test_archive_staging_schema.py`: `779ea6de4a1b26283d3c43de9ca45dd6462ea219`.
- `.github/workflows/t0-importer-core-synthetic.yml`: `0e319368fc36d8752f8e1640c3dd513dc18fd0ce`.

## 2. RED evidence

Workflow run [45000748833](https://github.com/kenznguyen/btcquant-application/actions/runs/45000748833), job `137141528897`, tested exact source SHA `d78170cf084f988ef83f8fe79ee85a1d43b1f584`.

- Exact SHA validation and checkout: PASS.
- Existing importer-core and adapter focused suites: PASS.
- New schema test suite: expected RED; import failed with `ModuleNotFoundError: No module named 'market_data.archive_staging_schema'`.
- Full regression steps correctly skipped after focused test failure.

This proves the schema test suite was present and failed because its implementation module had not yet been added.

## 3. GREEN and final regression evidence

Final workflow run [45001365840](https://github.com/kenznguyen/btcquant-application/actions/runs/45001365840), run #16, push on `main`.

- Job: `Importer-core synthetic tests`.
- Job ID: `137143405676`.
- Job conclusion: **SUCCESS**.
- Exact requested SHA = exact checked-out SHA = `fdb4c0cde31d8a1a5b9a1079fa05fcbe5a82ba50`.
- Runner: Ubuntu 24.04.5.
- Python focused suites: CPython 3.13.18.
- SQLite runtime: **3.45.1**, above the required 3.37.0 minimum.
- Importer-core focused suite: **20 tests — PASS**.
- S1.2 adapter focused suite: **10 tests — PASS**.
- SQLite staging schema focused suite: **10 tests — PASS**.
- Hash-locked test dependencies installed for Python 3.12.16.
- Complete `market_data` regression suite: **441 tests — PASS**.
- All workflow steps, including exact-SHA validation, checkout, runtime gate, focused suites, dependency hash verification/install and full regression: **SUCCESS**.
- Artifact API: **0 artifacts**. No artifact ID, checksum or downloadable artifact is available; test evidence is in the Actions job log.

The schema suite exercises STRICT tables, foreign-key enablement, NULL-safe VERIFIED/ACCEPTED checks, cross-object composite FK rejection, append-only triggers after removing the connection-local authorizer, deterministic schema fingerprint, integrity_check, foreign_key_check, and an isolated file-backed temporary database.

## 4. Implementation summary

- Controlled initializer refuses non-empty databases and nonzero user_version; it does not migrate an existing DB.
- SQLite minimum is 3.37.0; runtime was 3.45.1.
- Schema uses 11 STRICT tables, 8 indexes and 2 append-only run-event triggers.
- One-run-per-database is limited by singleton key 1; exactly one run plus initial BUILDING event remains an application-level acceptance invariant.
- Composite `(object_id, attempt_id)` FK prevents cross-object successful-attempt references.
- VERIFIED object/pair/member and ACCEPTED source-row CHECK branches explicitly guard mandatory values against NULL.
- Persisted SHA-1/SHA-256 values are constrained to exact lowercase hexadecimal grammar.
- Schema fingerprint uses T0ENC1 + SHA-256 over the canonical manifest, including exact table/index/trigger DDL and user_version pragma.
- Read-only verifier checks exact schema object set, STRICT declarations, user_version, stored fingerprint, integrity_check and foreign_key_check.
- Full graph validation and S3/V1 replay remain separate adapter/validator responsibilities.

## 5. Review and remaining limits

- Exact-SHA CI: **PASS**.
- Synthetic SQLite schema and full market_data regression: **PASS**.
- Static self-review: completed for this implementation increment; no independent second-human review is claimed.
- S1.2 freeze: **NOT APPROVED / NOT FROZEN**. Independent review, complete DB-to-S3/V1 projection/graph validation and final physical-schema closure remain outstanding.
- A later design amendment records that the executable fingerprint manifest includes trigger DDL because triggers enforce append-only semantics.
- No raw archives, sidecars, real historical rows, Canonical T0, MAY-10, REST tail, B8 runner, host/workstation, T1/T2, VPS, deployment, credentials, exchange or trading state was accessed or changed.
- No staging data build, real-data import, upload, retention change, deletion or cleanup occurred.


## 6. Final exact-SHA verification after digest/status hardening

A final verification run supersedes the earlier run #16 checkpoint:

- Workflow run [45001567714](https://github.com/kenznguyen/btcquant-application/actions/runs/45001567714), run #18.
- Job: `Importer-core synthetic tests`, ID `137144031470`, conclusion **SUCCESS**.
- Exact requested and checked-out source SHA: `2844e51dfe2a6a9ab0f02376a722cce257019faa`.
- CPython 3.13.18 / SQLite 3.45.1; STRICT runtime gate PASS.
- Importer-core: 20 tests PASS.
- S1.2 adapter: 10 tests PASS.
- SQLite staging schema: **13 tests PASS**. Added tests reject malformed lowercase-hex digests, invalid HTTP status values 99/600, invalid attempt expected SHA and invalid run-event snapshot digest.
- Complete `market_data` regression: **444 tests PASS**, CPython 3.12.16 with hash-locked dependencies.
- All job steps, including exact checkout, focused suites, dependency verification/install and full regression: SUCCESS.
- Artifact endpoint: 0 artifacts.

Final follow-up commits:
- Digest/HTTP status implementation: `96b80530938b34f0c67ea2139e144835fbdc6f1b`.
- Final digest/status tests: `2844e51dfe2a6a9ab0f02376a722cce257019faa`.
- Executable implementation amendment update: `02c31307494ad70b83ac70170cacdc7d88925a34`.

The initial schema RED evidence remains run #9 at `d78170cf084f988ef83f8fe79ee85a1d43b1f584`. The additional digest/status tests were committed before their final implementation verification, but their individual pre-fix RED run was not captured as a separate Actions run; their final GREEN behavior is confirmed by run #18.


## 7. Final exhaustive NULL-matrix verification

The NULL guard tests were expanded to exercise every mandatory field in the VERIFIED object, VERIFIED pair, VERIFIED member and ACCEPTED source-row branches individually.

- Final workflow run [45001731289](https://github.com/kenznguyen/btcquant-application/actions/runs/45001731289), run #21.
- Job: `Importer-core synthetic tests`, ID `137144538991`, conclusion **SUCCESS**.
- Exact requested and checked-out SHA: `d7cdea3a467aa0ee2a8b177aaec23fdfea3201ce`.
- CPython 3.13.18 / SQLite 3.45.1; STRICT gate PASS.
- Importer-core: 20 tests PASS.
- S1.2 adapter: 10 tests PASS.
- SQLite staging schema: **14 tests PASS**, including the per-field NULL matrix.
- Complete `market_data` regression: **445 tests PASS**, Python 3.12.16, hash-locked test dependencies.
- All workflow steps succeeded; artifacts endpoint returned 0 artifacts.
- Final test blob: `market_data/test_archive_staging_schema.py` = `324637a40abe1e3f387b9f16f7ba1e4aa621c317`. Schema module blob remains `56e7600fcf0d200098cfd4b875359b204956eb79`; workflow blob remains `0e319368fc36d8752f8e1640c3dd513dc18fd0ce`.

Test-fixture correction history:
- Run #19 `45001675277` and run #20 `45001691290` failed only in the newly expanded NULL-matrix test because synthetic object-key suffixes collided (UNIQUE constraint). Existing importer-core and adapter suites passed; the full regression was skipped.
- The fixture keys were made unique in commit `d7cdea3a467aa0ee2a8b177aaec23fdfea3201ce`.
- Run #21 confirms the corrected NULL matrix and full regression PASS.

The exhaustive NULL matrix now attempts NULL in each mandatory acceptance field for the four branches named above. This closes the prior representative-only test coverage caveat for those branch fields; it does not replace the application-level graph validator or S3/V1 replay.
