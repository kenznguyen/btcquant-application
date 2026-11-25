# T0 S1.2 — Compatibility Amendment B: append-only SQLite event triggers

Date: 2026-11-22  
Repository: kenznguyen/btcquant-application  
Branch: main  
Status: **OWNER-APPROVED DESIGN AMENDMENT — F1 RESOLVED AT DESIGN LEVEL; IMPLEMENTATION/VERIFICATION STILL REQUIRED**

## 1. Authority and scope

This amendment records the owner's approval to retain the two append-only SQLite triggers already present in the synthetic schema-v2 implementation and to amend §4.1 of:

`docs/design/T0_ARCHIVE_STAGING_S1_2_PROVENANCE_IMPORTER_PHYSICAL_SCHEMA_SPEC_2026-11-22.md`

It supersedes only the phrase in §4.1 that prohibits triggers. All other S1.2 requirements, Amendment A, scope limits, and approval gates remain unchanged. It does not authorize execution against real data, an existing database, Canonical T0, a workstation, host, runner, or production environment.

## 2. Replacement text for §4.1

Replace:

> No AUTOINCREMENT, rowid identities, triggers, views, virtual tables or generated columns.

With:

> No AUTOINCREMENT, rowid identities, views, virtual tables or generated columns. The schema MUST contain exactly the two append-only lifecycle triggers specified below and no other triggers. These triggers protect `run_events` against UPDATE and DELETE at the SQLite schema layer. All other trigger use is prohibited.

The remaining §4.1 preconditions are unchanged.

## 3. Normative trigger DDL

The complete and exact trigger statements are:

```sql
CREATE TRIGGER trg_run_events_no_update BEFORE UPDATE ON run_events
BEGIN SELECT RAISE(ABORT,'run_events are append-only'); END;

CREATE TRIGGER trg_run_events_no_delete BEFORE DELETE ON run_events
BEGIN SELECT RAISE(ABORT,'run_events are append-only'); END;
```

Required semantics:

- Any UPDATE affecting a `run_events` row aborts with `run_events are append-only`.
- Any DELETE affecting a `run_events` row aborts with the same message.
- INSERT remains permitted, subject to table constraints, foreign keys, and the application-level event-sequence/transition validator.
- The triggers do not establish valid event ordering or legal state transitions. Those remain graph/application-validator invariants.
- No trigger is added to any other table.
- Schema verification MUST require exactly these two trigger names and exact normalized DDL; missing, altered, or additional triggers fail verification.

## 4. Schema fingerprint contract

Both trigger DDL strings are part of the schema fingerprint manifest, in the `triggers` array, in this exact order:

1. `trg_run_events_no_update`
2. `trg_run_events_no_delete`

The fingerprint manifest therefore includes `schema_contract_id`, `user_version`, SQLite minimum version, ordered table DDL, ordered index DDL, ordered trigger DDL, and the `PRAGMA user_version=2;` pragma entry. The fingerprint framing remains `T0-SQLITE-SCHEMA-FINGERPRINT-V1` using T0ENC1 and SHA-256. This amendment does not change the schema contract ID, user_version, trigger SQL, manifest serialization algorithm, or fingerprint algorithm.

The connection authorizer that independently denies UPDATE/DELETE on `run_events` is a connection-level defense-in-depth control, not a SQLite schema object and not an entry in the schema fingerprint manifest. The triggers remain mandatory even when that authorizer is installed; tests must disable/remove the authorizer when proving that the triggers themselves enforce append-only behavior.

## 5. Required synthetic tests

The synthetic-only test suite MUST prove:

1. Both exact trigger definitions exist in `sqlite_schema`.
2. A direct UPDATE of an existing `run_events` row fails with the append-only abort.
3. A direct DELETE of an existing `run_events` row fails with the append-only abort.
4. INSERT remains possible when the row satisfies schema constraints and foreign keys.
5. Removing the connection authorizer does not disable either trigger.
6. Missing, altered, or extra triggers cause schema verification to fail.
7. The deterministic schema fingerprint changes if either trigger definition, trigger order, or trigger set changes.
8. The expected fingerprint is reproducible from the complete ordered manifest.

These tests use synthetic rows and disposable in-memory or temporary SQLite databases only. They must not open or inspect any pre-existing database.

## 6. Implementation alignment and remaining findings

The reviewed implementation at source SHA `d7cdea3a467aa0ee2a8b177aaec23fdfea3201ce` already declares the two trigger statements in `TRIGGER_DDL`, includes them in `_canonical_manifest_bytes()`, verifies their exact names/DDL, and has synthetic append-only tests. This amendment resolves the design/implementation contradiction identified as F1; it does not by itself certify that F1's required tests have been independently reviewed or re-run after this document is committed.

F2–F7 remain open exactly as recorded in:

`docs/reviews/T0_S1_2_SQLITE_STAGING_SCHEMA_SELF_REVIEW_D7CDEA3_2026-11-22.md`

S1.2 remains **NOT FROZEN**. Independent review remains **NOT RUN**. The next authorized work is to continue the previously approved synthetic-only sequence: complete immutable DTOs, DB-to-S3/V1 projection and graph validation; add TDD coverage for F1–F7; run exact-SHA CI and the complete `market_data` regression; then obtain independent review.

## 7. Explicit exclusions retained

This amendment does not authorize:

- B8 acquisition workflow changes, dispatch, runner installation/registration, or host/workstation preflight;
- real archive/sidecar listing, download, extraction, parsing, sampling, or access;
- real-data Historical build, real staging population, or archive coverage acceptance;
- uploads, retention changes, cleanup, or deletion of source/staging/private evidence;
- Canonical T0 recovery, creation, replacement, migration, merge, promotion, or cutover;
- MAY-10, REST tail, T1/T2 runtime, VPS, deployment, credentials, exchange access, or trading.

No DDL execution, SQLite connection, database access, archive access, workflow dispatch, or host operation is performed by this documentation amendment.
