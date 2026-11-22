# G1 Synthetic-Only CI — Implementation Approval Request

Date: 2026-11-22  
Repository: `kenznguyen/btcquant-application`  
Status: **REQUEST FOR OWNER APPROVAL — NOT AUTHORIZED**

## 1. Parent decision

This request follows the owner-accepted GitHub-first, destination-deferred model recorded in:

`docs/decisions/T0_GITHUB_FIRST_DESTINATION_DEFERRED_OWNER_ACCEPTANCE_2026-11-22.md`

GitHub is the control plane. No concrete machine/path is selected. This G1 request is deliberately limited to synthetic, source-code-only validation and does not require archive access or a persistent data destination.

## 2. Objective

Create a reproducible exact-SHA GitHub Actions gate to test pure Python components that can be validated without real archive files, SQLite, network access, or a host destination.

The goal is to retire software-contract uncertainty before asking the owner to authorize any real-source sampling or data-build phase.

## 3. Proposed bounded scope

Subject to approval, G1 may:

1. Add pure functions for enforcing the already accepted B4 numeric policy against synthetic metadata/counters:
   - cumulative response-byte and per-object limits;
   - ZIP entry count, member and aggregate uncompressed-byte ceilings;
   - compression-ratio and UTF-8 member-path limits;
   - safe-path/unsupported-entry classification;
   - concurrency policy assertions;
   - retry classification, maximum attempts, backoff and timeout state transitions.
2. Add synthetic-only parser tests for:
   - CSV header and column mapping variants represented by authored fixtures;
   - BOM, encoding and newline cases;
   - malformed headers, duplicate/missing columns, unsafe paths and unsupported members;
   - deterministic row parsing and source-row identity inputs where no real archive is read.
3. Add synthetic-only importer-core tests that validate row normalization, row accounting, duplicate/conflict classification and coverage-set calculations **in memory only**.
4. Add static/runtime metadata checks for the Python interpreter and report the linked SQLite library version without opening or creating a SQLite database. The minimum SQLite policy remains >= 3.37.0. Actual SQLite connection/DDL/FK behavior is excluded from G1.
5. Add deterministic unit tests and a manual `workflow_dispatch` workflow that checks out one caller-supplied full 40-character lowercase source SHA and records the exact checked-out SHA and tested file hashes.

## 4. Proposed files (final names to be confirmed during implementation)

- `market_data/archive_resource_policy.py` — pure resource-limit and retry/timeout policy helpers.
- `market_data/test_archive_resource_policy.py` — synthetic resource-policy tests.
- `market_data/archive_csv_parser.py` — pure parser core over supplied bytes/text/records; no filesystem/network access.
- `market_data/test_archive_csv_parser.py` — synthetic parser tests.
- `market_data/archive_importer_core.py` — pure in-memory row normalization/accounting/coverage core; no SQLite or filesystem access.
- `market_data/test_archive_importer_core.py` — synthetic importer-core tests.
- `.github/workflows/t0-g1-synthetic-only.yml` — manual exact-SHA workflow.
- `docs/evidence/T0_G1_SYNTHETIC_ONLY_CI_2026-11-22.md` — evidence record after an authorized run.
- Update `docs/PROJECT_SESSION_HANDOFF.md`, `docs/PROJECT_SESSION_HANDOFF_ADDENDUM_2026-11-22.md` and `docs/T0_ACTIVE_SCOPE_INDEX.md` after completion.

The implementation must first inspect existing parser/validator/test modules and avoid duplicate implementations. The proposed paths are not authorization to create them.

## 5. TDD and acceptance criteria

- Preserve existing S3/V1 behavior and tests unchanged unless a separately reviewed compatibility defect requires a new approval.
- Write failing synthetic tests before implementation (RED), then implement only the smallest pure-function behavior to pass (GREEN).
- Test each B4 ceiling at below/equal/above boundaries; invalid and overflow values; deterministic fail-closed outcomes.
- Test retryable vs non-retryable statuses, exact attempt count, Retry-After boundary, connect/read/total timeout decisions and run/object time budget transitions.
- Test parser encoding/BOM/newline/header cases, malformed input and path traversal rejection.
- Test importer-core deterministic row accounting, natural-key sets, gaps/extras/duplicates/conflicts and stable output independent of input order where contract requires it.
- Test no mutation of input payloads and no filesystem/network/SQLite side effects in pure modules.
- Run focused tests, full `market_data` regression, and any explicitly scoped repository regression.
- Workflow must fail if the checked-out SHA differs from the requested SHA or if the workflow is not running on the expected repository/ref policy.
- Record exact source SHA, tested file blobs, Python version, run ID, job ID, artifact ID/name/size/SHA-256/expiry where an artifact is approved, and all exit codes.
- A successful workflow wrapper must not hide failing test exit codes.

## 6. Workflow security and artifact policy

Proposed workflow controls:
- `workflow_dispatch` only; no schedule, push, pull-request or automatic trigger.
- Minimal `contents: read` permission.
- No secrets, credentials, network egress for test payloads, external services, exchange connectivity or private archive URLs.
- Checkout exact caller-supplied full SHA; validate input before checkout; log requested SHA and actual HEAD.
- No self-hosted runner.
- No upload of raw archive, sidecar, SQLite, candle rows, secrets, signed URLs, environment dumps, raw HTTP headers/body or private host paths.
- If an evidence artifact is approved, upload only sanitized test logs, source/test SHA manifest and test summary; retention <= 30 days. Artifact upload itself is part of this approval request and must be explicitly accepted.
- No artifact is to be treated as durable source/staging storage.

## 7. Explicit exclusions

G1 does not include:
- real archive/sidecar listing, inspection, retrieval, download, decompression or parsing;
- source-format claims about the 404 actual ZIPs;
- SQLite open/create/write, DDL, schema migration, `user_version`, FK connection tests or database build;
- filesystem-based extraction, persistent workspace, destination creation or host preflight;
- actual acquisition, source-derived coverage manifest or real row/candle evidence;
- workflow dispatch until this request is approved;
- Canonical promotion, retention/deletion/cleanup, T1/T2 runtime, VPS deployment, systemd/autostart, credentials, exchange connectivity or trading.

## 8. Expected status changes if G1 passes

- Synthetic resource-policy implementation/tests: PASS for tested code only.
- Synthetic parser/importer-core behavior: PASS for authored fixtures only.
- Exact-SHA CI reproducibility: PASS for the tested source SHA only.
- B3 actual archive format coverage: remains NOT VERIFIED.
- B5 actual source-derived coverage: remains NOT VERIFIED.
- SQLite runtime/DDL and staging build: remain NOT AUTHORIZED / NOT VERIFIED.
- B7 concrete destination and preflight: remains DEFERRED / NOT SELECTED.

## 9. Owner decision requested

Please approve or reject this exact G1 scope, including:
- the pure Python implementation and synthetic tests described in sections 3–5;
- creation of the manual exact-SHA workflow described in section 6;
- one or more manual workflow dispatches for the resulting exact source SHA;
- sanitized evidence artifact upload with maximum 30-day retention.

A partial approval must identify which numbered sections/items are accepted. No implementation, workflow creation, dispatch or artifact upload begins until explicit owner approval is recorded.

No code, tests, workflows, artifacts, archive requests, host operations, SQLite/database operations or runtime actions were performed in preparing this request.
