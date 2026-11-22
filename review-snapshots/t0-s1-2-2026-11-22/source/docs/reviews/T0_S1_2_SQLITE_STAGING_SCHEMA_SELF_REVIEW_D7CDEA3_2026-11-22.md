# T0 S1.2 — Read-only self-review on exact source SHA d7cdea3

Date: 2026-11-22
Repository: `kenznguyen/btcquant-application`
Target branch at review time: `main`
Reviewed source SHA: `d7cdea3a467aa0ee2a8b177aaec23fdfea3201ce`
Review type: same-session read-only SELF-REVIEW; not independent review.

## 1. Verdict

**BLOCKED — do not proceed to real-data build, SQLite persistence, staging population, or S1.2 freeze.**

This review inspected the exact source tree at the specified SHA. It did not modify or execute code, open SQLite, inspect archives, access a host/workstation, or read/write real data. Previously reported synthetic CI PASS results remain historical evidence for this SHA; this review did not rerun them.

## 2. Reviewed files and exact blobs

| File | Blob SHA |
|---|---|
| `market_data/archive_staging_schema.py` | `56e7600fcf0d200098cfd4b875359b204956eb79` |
| `market_data/test_archive_staging_schema.py` | fetched at exact SHA; current test file content inspected |
| `market_data/archive_staging_adapter.py` | `9d61bb36cfb2ff80c0a1b303e52f34d8d44d2b28` |
| `.github/workflows/t0-importer-core-synthetic.yml` | exact-SHA workflow inspected |
| `docs/design/T0_ARCHIVE_STAGING_S1_2_PROVENANCE_IMPORTER_PHYSICAL_SCHEMA_SPEC_2026-11-22.md` | exact-SHA design inspected |
| `docs/design/T0_ARCHIVE_STAGING_S1_2_COMPATIBILITY_AMENDMENT_A_2026-11-22.md` | blob `6f9476f696962c88f27421cdf83fb42a6b4f794f` |

## 3. Findings

### F1 — Required: implementation/schema contract drift

The physical schema implementation creates two append-only triggers and includes them in the schema fingerprint manifest. The controlling physical schema specification §4.1 explicitly states that triggers are prohibited, and the DDL candidate does not include them. The code therefore implements a materially different physical schema without a corresponding approved design amendment. Keeping `T0_STAGING_SCHEMA_V2` and `user_version=2` does not resolve this discrepancy.

**Required:** reconcile the design and implementation explicitly; obtain owner approval for the exact trigger/authorizer policy and fingerprint manifest; add contract tests that compare the complete approved manifest to the implementation. Do not silently alter either side.

### F2 — Critical: complete DB ↔ S3/V1 adapter and graph validator are absent

The adapter currently defines only `AttemptRecord`, `SourceRowRecord`, and `PairRecord`, with three projection helpers and an attempt-summary helper. It does not implement the complete run/object/member/candle/link/failure/event DTO set, a read-only SQLite row projection, complete S3/V1 payload assembly, or the application graph validator required by Amendment A S12-02 and S12-07.

The existing helpers also leave material validation gaps: attempt workflow-event/outcome details, pair digest syntax and IDs, source-row ID/member ID/raw-row digest/ordinal relationships, and several required identity fields are not comprehensively validated by the projection boundary.

**Required:** complete the immutable DTO contract and deterministic read-only DB→S3/V1 projection; implement graph validation for all S12-07 invariants; prove fail-closed behavior with synthetic fixtures before any persistence attempt.

### F3 — Critical: database constraints alone do not establish cross-record acceptance

The schema does not itself establish several required relationships, including object expected-vs-measured equality, successful-attempt outcome and digest equality with its object, reciprocal ZIP/sidecar kinds and pairing, source-row-to-candle value consistency, exactly one UNIQUE link per candle, and exact run event sequence/transitions. Amendment A assigns these to the application graph validator, which is not present in the reviewed adapter.

**Required:** implement and test the graph validator; do not treat `PRAGMA integrity_check`, `foreign_key_check`, or the current schema verifier as provenance acceptance.

### F4 — Required: run-envelope acceptance is not implemented

`verify_staging_database()` verifies structural schema, integrity, foreign keys, and any present run fingerprint, but it does not require exactly one run envelope or exactly one initial BUILDING event. An empty initialized database can pass this schema verifier. That is acceptable only as a schema-level check; it is not the S12-05 run acceptance validator promised by the design.

**Required:** add a separate run-acceptance validator enforcing one envelope, one initial BUILDING event, legal append-only event sequence/transitions, and terminal-state/digest bindings.

### F5 — Required: digest and identity grammar is not consistently enforced at the SQL boundary

Several physical columns constrain digest length but not lowercase hexadecimal grammar (for example source-row parser/importer SHA fields); candle value IDs in the candle/link tables constrain prefix and length but not the digest suffix. Some checks are delegated to adapters, but those adapters are incomplete and not a substitute for the approved DB+graph acceptance boundary.

**Required:** create a field-by-field digest/identity grammar matrix from S1/S3 and Amendment A, then test every required malformed value at both SQL and adapter boundaries. Do not widen the scope beyond frozen contracts.

### F6 — Required safety boundary: staging initializer accepts arbitrary explicit paths

`connect_staging_database(database)` accepts any supplied string or Path and opens it with `sqlite3.connect`; it does not prove that the target is a disposable synthetic path. It refuses a non-empty database but can create an empty database at an unintended path. The docstring's “disposable” wording is not an enforcement boundary.

**Required:** before any persistence authorization, separate the low-level connection initializer from a guarded disposable-test helper, or add an explicit caller-supplied policy that restricts allowed temporary locations. Real staging must use a separately approved builder entry point and path policy.

### F7 — Required: initialization is not atomic

Schema DDL, indexes, triggers and `user_version` are applied statement by statement without an explicit transaction/rollback boundary. A failure partway through initialization can leave a partially created database. The initializer closes the connection on error but does not explicitly roll back the partially applied schema.

**Required:** define and test atomic initialization semantics on disposable DBs, including injected failure after each DDL phase and proof that no partial schema is left behind.

## 4. Positive observations

- Exact source SHA was used for read-only inspection.
- Schema checks use STRICT tables and enable/read back foreign-key enforcement.
- SQL checks explicitly guard many mandatory VERIFIED/ACCEPTED fields against NULL; tests enumerate substantial null cases.
- Composite `(object_id, attempt_id)` foreign key prevents a successful-attempt link from pointing to another object's attempt.
- Run-event UPDATE/DELETE protection exists through triggers and a connection authorizer, but this implementation conflicts with the current design statement prohibiting triggers and must be reconciled.
- The CI workflow verifies exact checkout SHA and runs focused schema/adapter/core suites plus full `market_data` regression.

## 5. Verification limits

- Review mode: read-only source/design/test/workflow inspection.
- No local test execution or new workflow run was performed during this review.
- No independent reviewer was involved.
- Existing workflow PASS is not proof of the missing graph/projection contract or real archive compatibility.
- No real archive variants beyond the previously recorded coverage baseline are accepted by this review.
- No actual source-derived coverage, host path, encryption, disk/inode capacity, or acquisition provenance is verified.

## 6. Gate disposition

| Gate | Status |
|---|---|
| Synthetic schema and focused/full CI evidence previously reported | PASS at the recorded exact SHA |
| Same-session code/design self-review | BLOCKED with findings F1–F7 |
| Complete DB↔S3/V1 projection | NOT IMPLEMENTED |
| S12-07 graph validator | NOT IMPLEMENTED |
| S1.2 physical-schema compatibility closure | BLOCKED |
| Independent review | NOT RUN |
| Real archive format/coverage validation | NOT VERIFIED |
| B8 acquisition runner/workflow | NOT APPROVED |
| Host/workstation/path preflight | NOT APPROVED / NOT VERIFIED |
| Real-data build or SQLite persistence | NOT AUTHORIZED by this review |

## 7. Next permitted sequence

1. Resolve F1 schema/design drift by an explicit design amendment and owner decision.
2. Complete DTOs, deterministic DB→S3/V1 projection and S12-07 graph validator using synthetic fixtures only.
3. Add test-first coverage for F1–F7, including atomic schema initialization and guarded disposable paths.
4. Run exact-SHA synthetic CI and full `market_data` regression; record SHA, run/job, logs and artifact metadata.
5. Obtain an independent review of the reconciled source and design.
6. Separately approve B8 acquisition execution, real archive compatibility/coverage validation, host/path preflight, and real-data staging build. These are distinct gates; approval of one does not imply the others.
7. Canonical T0 promotion remains a later, separate decision.

**Disposition: SELF-REVIEW COMPLETE — BLOCKED BEFORE REAL-DATA BUILD/PERSISTENCE. S1.2 NOT FROZEN.**
