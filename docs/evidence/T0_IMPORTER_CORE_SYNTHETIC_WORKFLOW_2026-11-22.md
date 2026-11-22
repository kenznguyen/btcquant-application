# T0 Importer-Core Synthetic TDD — Workflow and Execution Evidence

Date: 2026-11-22
Repository: `kenznguyen/btcquant-application`
Branch: `main`
Controlling approval: `docs/decisions/T0_IMPORTER_CORE_SYNTHETIC_TDD_SCOPE_APPROVAL_2026-11-22.md`
Separate workflow approval: explicit owner approval in conversation on 2026-11-22.

## 1. Dedicated workflow

- File: `.github/workflows/t0-importer-core-synthetic.yml`.
- Initial workflow commit: `84bcfc91ba08b21b96d699101548415d1f19821d`.
- Dependency/regression environment correction: commit `002e00679e7cb1e4ad09040a832ae416e597a300`; workflow blob `cb1434d5f68e526b8b8b2a4970218cd27684ea0c`.
- Push trigger: importer-core source/tests, the dedicated workflow itself, and committed FastAPI test-lock files. Manual dispatch accepts an optional exact 40-character SHA.
- Exact checkout is verified against `git rev-parse HEAD`.
- Focused importer-core tests run on CPython 3.13.
- Full `market_data` regression runs on CPython 3.12.16 after installing `requirements-market-data-fastapi-test.lock` with `--only-binary=:all: --require-hashes` and verifying `requirements-market-data-fastapi.sha256`.
- Permissions: `contents: read`. No secrets, database services, canonical data, archive access, exchange, or runtime integration.
- No artifacts are uploaded. Existing G1 workflow is unchanged.

## 2. TDD and CI chronology

| Stage | Exact source SHA | Workflow run / job | Result |
|---|---|---|---|
| Test-first RED | `ea670901974944ae71dab58241f0e4e2cbd1e85f` | [44992280345](https://github.com/kenznguyen/btcquant-application/actions/runs/44992280345) / `137115734474` | **RED confirmed** — importer module absent; exact SHA verified |
| Initial implementation | `cf95f5003c7cee91f3ff38feaa75b4e44a0bb189` | [44992374087](https://github.com/kenznguyen/btcquant-application/actions/runs/44992374087) / `137116017044` | Focused **16/16 PASS**; full suite blocked by 5 FastAPI import errors (missing CI dependency setup) |
| Locked dependency setup | `002e00679e7cb1e4ad09040a832ae416e597a300` | [44992456552](https://github.com/kenznguyen/btcquant-application/actions/runs/44992456552) / `137116277360` | Focused **16/16 PASS**; full suite **417/417 PASS** |
| Additional contract tests RED | `eda33259c8c98faf55187e959183ddd1560afad1` | [44992551765](https://github.com/kenznguyen/btcquant-application/actions/runs/44992551765) / `137116562471` | **RED confirmed** — 4 failures for empty range, stable ordering, normalized Decimal duplicate equality and timeframe-aligned row identity |
| Corrected implementation GREEN | `0fc21ac6ba91e82e531fe58a02f9303462c71ea7` | [44992591222](https://github.com/kenznguyen/btcquant-application/actions/runs/44992591222) / `137116685659` | **PASS** — focused **20/20**, full `market_data` **421/421** |

## 3. Final exact-SHA GREEN evidence

- Tested source SHA: `0fc21ac6ba91e82e531fe58a02f9303462c71ea7`.
- Workflow run: [44992591222](https://github.com/kenznguyen/btcquant-application/actions/runs/44992591222), run #5, event `push`, conclusion `success`.
- Workflow ID: `426569112`.
- Job: `Importer-core synthetic tests`, ID `137116685659`, conclusion `success`.
- Exact SHA verification: requested and checked-out SHA both `0fc21ac6ba91e82e531fe58a02f9303462c71ea7`.
- Focused command: `python -B -m unittest -v market_data.test_archive_importer_core` — **20/20 PASS**, CPython 3.13.18.
- Full command: `python -B -m unittest discover -v -s market_data -p 'test_*.py'` — **421/421 PASS**, CPython 3.12.16.
- Dependency manifest: both `requirements-market-data-fastapi.lock` and `requirements-market-data-fastapi-test.lock` SHA-256 checks returned OK. Test dependencies installed with hash enforcement and binary wheels only.
- No artifact produced or uploaded.

## 4. Source inventory

- Implementation: `market_data/archive_importer_core.py`, blob `a7d7245fe7379f3d3b67c0a111e906a4364f6d10`.
- Focused tests: `market_data/test_archive_importer_core.py`, blob `3dfc58b570789d8ea6d172e442266743b9157bf5`.
- Existing parser input: `market_data/archive_csv_parser.py`, unchanged blob `10fe2313103c45d5455f17ff71f3fd0af2e6f038`.
- Implementation behavior: immutable in-memory candidates, explicit identity, exact Decimal and raw source fields, parser-provided bar-close boundary, one-based opaque source references, accounting conservation, duplicate/conflict quarantine, deterministic candidate order, and explicit UTC-aligned non-empty half-open coverage.
- The importer does not assign `FIRST_OBSERVED`.

## 5. Self-review and scope inspection

| Review axis | Result |
|---|---|
| Correctness | PASS — focused and full exact-SHA suites pass; explicit edge-case REDs corrected |
| Readability | PASS — pure functions and frozen dataclasses; no new runtime dependency |
| Architecture | PASS — consumes existing parser contract; no persistence or orchestration layer |
| Security / side effects | PASS — source imports only stdlib plus existing parser; scan found no filesystem, ZIP, network, environment, clock, SQLite or database APIs |
| Performance | PASS for bounded synthetic unit-test use; no production-scale/performance claim made |

Test code also uses synthetic in-memory CSV strings only; no fixture file or real archive is opened.

## 6. Status and exclusions

- Synthetic importer-core in-memory TDD: **PASS**.
- Exact-SHA RED: **PASS**.
- Focused exact-SHA GREEN: **PASS 20/20**.
- Full `market_data` regression: **PASS 421/421**.
- Workflow and evidence tracking: **PASS**.
- Independent review: not represented as completed by this self-review.
- Artifact: not applicable; artifact upload excluded.
- B3 real archive format and B5 source-derived coverage remain **NOT VERIFIED**.
- B8 SQLite/importer build remains **NOT AUTHORIZED**.

Still excluded: archive/sidecar access, listing, retrieval, extraction or real-file parsing; REST/object-store/host/SSH/filesystem preflight; SQLite open/create/write/DDL/staging; stable provenance IDs, canonical digest framing, schema/DDL/fingerprint/indexes/FKs/user_version/transactions; real archive orchestration; Canonical T0/MAY-10; T1/T2; VPS/runtime/deployment; credentials/exchange/trading; deletion/cleanup/retention execution.

## 7. Next gate

Preserve this bounded in-memory implementation. Any S1 contract/schema freeze, real archive source validation, persistence, SQLite staging/build, or integration with Canonical T0 requires its own explicit approval and evidence plan.
