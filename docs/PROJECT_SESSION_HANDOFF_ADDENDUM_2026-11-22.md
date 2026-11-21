# PROJECT SESSION HANDOFF ADDENDUM — 2026-11-22

Repository: kenznguyen/btcquant-application
Branch: main
Related S1 design commit: ee30e4bcb1e1118901e372f642f368e4f4578649

## T0 archive staging/importer S1

- Owner approved S1 only: freeze design-level provenance contracts and staging schema.
- S1 baseline: `docs/design/T0_ARCHIVE_STAGING_S1_PROVENANCE_SCHEMA_FREEZE_2026-11-22.md`.
- Original S1 design commit: `319d3db16da69c59b2efb9e9a0b4a7f5f7afe8e9`.
- Owner approved a documentation-only amendment to resolve three review findings: preserving failed/incomplete evidence, adding append-only acquisition-attempt history, and aligning nullable evidence fields with quarantine states.
- Amended S1 design commit: `ee30e4bcb1e1118901e372f642f368e4f4578649`.
- Amendment freezes `AcquisitionAttemptEvidence`, stable attempt IDs, explicit attempt outcomes (including UNKNOWN), partial-body versus complete-object digest semantics, conditional VERIFIED/QUARANTINED constraints, and pair/member failure evidence retention.
- The original DDL is a design baseline only. The amendment specifies exact changes required before any future executable DDL; no DDL was implemented or tested.
- S1 status: **DESIGN BASELINE AMENDED AND COMMITTED; DOCUMENTATION ONLY**.
- Importer, acquisition workflow, archive requests, staging SQLite, Canonical T0, MAY-10, REST tail, T1/T2, VPS/runtime, deployment and trading remain excluded/not authorized.
- Remaining open gates: exact pinned SQLite runtime/STRICT support; complete cross-table validator test design; compression/uncompressed-size/disk-reserve limits; artifact/source retention; real header-mode verification across all 202 archives.
- Main `docs/PROJECT_SESSION_HANDOFF.md` was not rewritten because it is a large append-oriented history file; this addendum remains the latest handoff record.

## Evidence and verification

- Scope: documentation-only S1 amendment.
- Design review findings addressed: (1) success-only CHECK constraints had prevented retention of failed evidence; (2) acquisition retries lacked a frozen append-only attempt contract; (3) measured object fields were NOT NULL despite incomplete/quarantined evidence states.
- Verification: content-level consistency review only; no code tests, SQL execution, SQLite creation, archive access, workflow run or artifact.
- Workflow run/job/artifact: **NONE**.
- S1 amendment source commit: `ee30e4bcb1e1118901e372f642f368e4f4578649`.
- Status: **COMMITTED — DESIGN ONLY**; implementation/test status **NOT RUN / NOT AUTHORIZED**.

## T0 archive staging/importer S2 — synthetic provenance validator RED

- Owner approved S2 limited to synthetic-only Provenance Validator RED tests; this approval does not authorize GREEN implementation.
- Added `market_data/test_archive_provenance_validator_red.py`, 12 unittest methods; final blob SHA `abbaeab16f026757923c679330f124a3d99e0774`.
- Test contract covers T0ENC1 framing, deterministic acquisition attempt IDs, inventory/object allowlist, QUARANTINED evidence, UNKNOWN/partial transfer evidence, pair/member cardinality, source-row/link cardinality, conflicting candle values and BAR_CLOSE_BOUNDARY semantics.
- Expected future module/API is documented in the test file: `market_data.archive_provenance_validator` with `encode_t0enc1`, `derive_attempt_id`, and `validate_provenance`.
- Test commit history: initial `a27d303e981da94f3c379672fb2c2c452cd08d99`; assertion correction `69a97d0c4dce7e85a00a1f49b5e0f25eb28bcc20`.
- Evidence record initially committed at `97455de1fd1d849b84aa7961d03436eee89a472b`; updated exact-source execution evidence commit: `b657c21d4f84cddce9c5ebff816267299e049f38`.
- User-provided ZIP has no `.git` metadata. Four file blobs were checked against the exact target commit and matched; whole-tree commit identity is not independently provable from this ZIP alone.
- Exact command: `python -B -m unittest -v market_data.test_archive_provenance_validator_red`.
- Local isolated execution on CPython 3.13: **12 tests run; 12 errors; exit code 1**. Every error is `ModuleNotFoundError` for the intentionally absent `market_data.archive_provenance_validator` raised in `setUp()`; no business assertion ran. The missing-module RED state is runtime-proven; the 12 invariants are **NOT VERIFIED**.
- GitHub Actions run/job/artifact: **NONE**. Full repository regression: **NOT RUN**.
- Bounded interface review found S1 does not independently freeze the validator result DTO (`valid`, `error_codes`), complete validator-level error-code catalogue, or deterministic error ordering/aggregation. Individual codes embedded in tests do not constitute a reviewed complete interface contract.
- S2 disposition: **PARTIAL — expected RED reproduced; validator assertions NOT VERIFIED; GREEN BLOCKED pending API/error-code contract freeze**.
- Next: define and review the exact result shape and stable error-code catalogue as a documentation-only interface decision. A separate owner approval is required before GREEN validator implementation.
- No production code, DDL, SQLite, importer, archive retrieval, workflow, Canonical T0/MAY-10/REST tail, VPS/runtime, T1/T2, deployment, cleanup or trading operation occurred.

## Handoff correction

This section supersedes the earlier S2 statements in this addendum that said RED execution was NOT RUN. The test execution described above occurred after the exact-source ZIP was supplied. The older wording is retained only as historical state before execution.
