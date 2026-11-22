# T0 G1 Synthetic-Only CI — Implementation Readiness Inventory

Date: 2026-11-22
Repository: `kenznguyen/btcquant-application`
Branch inspected: `main`
Owner approval: `docs/decisions/T0_G1_SYNTHETIC_ONLY_CI_OWNER_APPROVAL_2026-11-22.md`
Approval commit: `119f0328f19293435c93575b203577f5026e0f06`

## Purpose and significance

This read-only inventory prevents duplicate parser/validator implementations and records the existing source contracts before the approved G1 synthetic-only changes. It is a source-inspection checkpoint, not implementation or test evidence.

## Existing source inventory

| Path | Observed state | Blob SHA |
|---|---|---|
| `market_data/archive_csv_parser.py` | Existing strict 12-column parser; `ARCHIVE_CSV_HEADER_V1`, immutable `ArchiveCsvDocument`, `parse_archive_csv_document`, legacy tuple API preserved | `10fe2313103c45d5455f17ff71f3fd0af2e6f038` |
| `market_data/test_archive_csv_parser.py` | Existing synthetic parser tests | `50199cd168fd52314a846760cc4baf51a8cd5e9a` |
| `market_data/test_archive_csv_header_contract.py` | Existing exact-header synthetic contract tests | `fb102ace09f73e6233b5c577b6256665549c2ce0` |
| `market_data/archive_provenance_validator.py` | Existing independent pure provenance validator; must not be duplicated in importer core | `b94bac0f82ae141984552409f99a5cff70435b3b` |
| `market_data/archive_resource_policy.py` | Not found on inspected `main` | — |
| `market_data/archive_importer_core.py` | Not found on inspected `main` | — |
| `.github/workflows/t0-g1-synthetic-only.yml` | Not found on inspected `main` | — |

The accepted B4 numeric policy is frozen in `docs/design/T0_B4_B6_B7_RESOURCE_RETENTION_DESTINATION_DECISION_PACKAGE_2026-11-22.md`: 100 MiB cumulative response bytes; 64 MiB ZIP body; 64 KiB sidecar; 1,024 ZIP entries; 256 MiB/member; 512 MiB/ZIP; 4 GiB/run uncompressed; 100:1/member compression ratio; 1,024-byte UTF-8 path; concurrency 1; 3 attempts/object; backoff 2s/10s; Retry-After max 10s; connect/read-idle/attempt timeouts 10s/30s/120s; ZIP/run wall-time 10m/6h. These are policy constants for synthetic metadata checks only, not observed source measurements.

## TDD implementation plan

1. Extend the existing parser additively for explicitly selected UTF-8 text/bytes decoding and BOM/newline synthetic cases; preserve strict header V1 and the legacy tuple API. Do not introduce aliases or heuristic header handling.
2. Add tests first for the pure resource-policy module, including below/equal/above limits, invalid types/overflow, safe-path and unsupported-entry classification, retry classification, attempts/backoff/Retry-After and timeout transitions.
3. Add tests first for a separate in-memory importer core. Keep it limited to deterministic normalization/accounting, duplicate/conflict classification and exact coverage-set calculations. Do not duplicate the provenance validator, persist anything, or access SQLite/filesystem/network.
4. Add the manual exact-SHA workflow only after the tests and pure modules are in place. Validate full lowercase SHA input, verify checkout HEAD, record file hashes/runtime/exit codes, and upload only the approved sanitized evidence set (retention <= 30 days).
5. Run focused tests, full `market_data` regression and scoped repository regression; record exact commit/blob SHAs, run/job/artifact metadata and checksums.

## Verification status

- Source inventory: **PASS — READ ONLY**.
- Existing parser/validator reuse assessment: **PASS — READ ONLY**.
- TDD RED: **NOT RUN**.
- New source/tests/workflow: **NOT CREATED**.
- GitHub Actions run/job/artifact: **NONE**.
- Implementation: **NOT STARTED**.
- No archive, sidecar, host, filesystem destination, SQLite, importer execution on real data, Canonical T0, T1/T2, VPS/runtime, deployment, credentials or trading action occurred.

## Execution blocker

The connected GitHub operations available in this session support repository file/commit operations and inspection of existing workflow runs/artifacts, but do not expose a `workflow_dispatch` action. No local checkout of this repository is mounted in the execution environment. Therefore exact-repository RED/GREEN/regression execution and the authorized manual workflow dispatch cannot currently be performed from this session. Do not claim TDD or CI PASS without those proofs. Resume source changes only when an exact-source test execution path is available; otherwise retain this checkpoint as BLOCKED rather than committing unexecuted behavior.
