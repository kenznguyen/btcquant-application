# T0 G1 Synthetic-Only CI — Owner Approval

Date: 2026-11-22
Repository: `kenznguyen/btcquant-application`
Approval request: `docs/requests/T0_G1_SYNTHETIC_ONLY_CI_IMPLEMENTATION_APPROVAL_REQUEST_2026-11-22.md`
Approval-request blob: `f66c21b7c81b9eabe0ffba33c673cfaa76d219fa`
Parent architecture acceptance: `cf7df375d2afbcaa5b6f86fb5130f8f121733de3`

## Decision

**APPROVED — FULL G1 SCOPE, BOUNDED TO THE REQUEST.**

Purpose: establish reproducible, exact-source-SHA synthetic CI for pure Python resource-policy, parser and in-memory importer-core contracts before any real-source/data-build phase.

Significance: validates deterministic fail-closed software behavior and CI provenance without accessing real archives, creating a database, or selecting/using a persistent host.

## Authorized scope

1. Pure Python B4 resource-limit, safe-entry/path classification, concurrency assertions, retry/backoff/timeout policy helpers using synthetic metadata only.
2. Synthetic CSV parser tests/fixtures for authored header/mapping variants, BOM, encoding, newline, malformed/duplicate/missing columns, unsafe paths, unsupported members and deterministic row parsing. No actual archive input.
3. Pure in-memory importer-core behavior for normalization, accounting, duplicate/conflict classification and coverage-set calculations.
4. Python interpreter and linked SQLite library version metadata checks only. SQLite minimum policy remains >= 3.37.0. No SQLite connection or database operation.
5. Deterministic tests using TDD RED → GREEN, focused tests, full `market_data` regression and only the explicitly scoped repository regression.
6. Create the manual `workflow_dispatch` exact-SHA workflow, with caller-supplied full 40-character lowercase SHA validation, exact checkout verification, minimal `contents: read`, no secrets, no self-hosted runner, and no automatic triggers.
7. Manual dispatch of the resulting workflow for the exact approved source SHA after implementation is ready; one or more dispatches are authorized within this G1 scope.
8. Upload only sanitized test logs, source/test SHA manifest and test summary as CI evidence artifacts, with retention no longer than 30 days. Artifact upload is authorized only for these sanitized evidence files.

Final file names may be adjusted after inspecting existing modules to avoid duplicate implementations. Preserve existing S3/V1 behavior and tests; no unrelated refactor.

## Explicit exclusions — remain unauthorized

- Any real archive/sidecar listing, inspection, retrieval, download, decompression or parsing; no claims about actual 404 ZIP formats.
- SQLite open/create/write, DDL, schema migration, `user_version`, FK connection tests or database build.
- Filesystem extraction, persistent workspace, destination creation, host/device preflight or host access.
- Actual acquisition, source-derived coverage manifest, real row/candle evidence, staging build or importer execution on real data.
- Raw archives, sidecars, SQLite, candle rows, secrets, signed URLs, environment dumps, raw HTTP headers/bodies or private host paths in artifacts.
- Artifact use as durable source/staging storage; retention/deletion/cleanup of source or private evidence.
- Canonical promotion/replacement, T1/T2 runtime connection, VPS deployment, systemd/autostart, credentials, exchange connectivity, live/paper order execution or trading.

## Required evidence and status discipline

Record exact source commit SHA; tested file blob SHAs; Python and linked SQLite versions; workflow run and job IDs; artifact ID/name/size/SHA-256/expiry; test commands and exit codes. A passing run proves only the exact tested SHA and synthetic fixtures. B3 actual archive format coverage and B5 source-derived coverage remain **NOT VERIFIED**. SQLite runtime/DDL and staging build remain **NOT AUTHORIZED / NOT VERIFIED**. B7 concrete destination remains **DEFERRED / NOT SELECTED**.

Implementation may begin in the existing repository branch after checking the live HEAD and existing modules. Follow TDD and do not expand beyond this approval.