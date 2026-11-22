# T0 SQLite Staging Schema V2 — Executable Implementation Amendment

Date: 2026-11-22
Repository: kenznguyen/btcquant-application
Branch: main
Status: IMPLEMENTATION DETAIL — SYNTHETIC TEST SCOPE ONLY; S1.2 NOT FROZEN

This note records the executable details used by `market_data/archive_staging_schema.py`. It supplements the S1.2 physical schema specification and Compatibility Amendment A. It does not approve real-data acquisition, a Historical build, B8, or Canonical T0 operations.

## 1. Append-only event enforcement

The physical schema installs exactly two database triggers:

- `trg_run_events_no_update`: rejects every UPDATE on `run_events`.
- `trg_run_events_no_delete`: rejects every DELETE on `run_events`.

The connection helper also installs a connection-local SQLite authorizer as defense in depth. The triggers are the durable database-level guard and are tested after removing the authorizer. Event ordering and legal state transitions remain application-validator responsibilities; triggers do not claim to validate the run state machine.

## 2. Fingerprint manifest extension

The base S1.2 §5 manifest lists tables, indexes and pragmas. Because append-only behavior is implemented by schema triggers, the executable V2 manifest additionally includes the exact ordered `triggers` DDL array. This ensures that changing or removing either append-only trigger changes the schema fingerprint.

The manifest remains deterministic UTF-8 compact JSON with sorted object keys, no BOM and no trailing newline. Its value domain is restricted to strings, integers, arrays and objects, so the implementation's sorted-key compact JSON encoding is the RFC 8785-compatible subset for this manifest. The T0ENC1 framing and SHA-256 formula remain unchanged:

```text
SHA256(T0ENC1(
  "T0-SQLITE-SCHEMA-FINGERPRINT-V1",
  "T0_STAGING_SCHEMA_V2",
  2,
  canonical_schema_manifest_utf8_bytes
))
```

The fingerprint covers exact table, index and trigger DDL plus `PRAGMA user_version=2;`. It identifies schema only, not database contents.

## 3. Persisted digest grammar

All persisted SHA-256 and SHA-1 digest fields use exact lowercase hexadecimal grammar, not length-only checks. SQL constraints require the expected length and reject any character outside `[0-9a-f]`. Optional digest fields may be NULL only where their evidence state permits it. VERIFIED object, VERIFIED pair/member and ACCEPTED source-row branches still require their mandatory evidence explicitly non-NULL.


- HTTP `response_status`, when present, is constrained to the valid 100–599 range; the VERIFIED object branch separately requires it to be non-NULL.
- Run-event candidate snapshot and validator payload digests use the same exact lowercase SHA-256 grammar.

SQLite STRICT INTEGER storage supplies the signed 64-bit storage boundary; nonnegative field constraints reject negative sizes, ordinals, counts and timestamps where the contract requires nonnegative values.

## 4. Controlled initialization and verification

- Initialization requires an explicit caller-supplied database path/connection.
- Tests use `:memory:` or a disposable temporary directory only.
- The initializer refuses a database with any existing user schema object or nonzero `user_version`; it is not an in-place migration mechanism.
- SQLite runtime must be at least 3.37.0 for STRICT tables.
- Each managed connection enables and verifies `PRAGMA foreign_keys=ON`.
- Read-only verification checks exact expected tables/indexes/triggers, STRICT table declarations, `user_version=2`, exact schema fingerprint, `PRAGMA integrity_check` equal to `ok`, and an empty `PRAGMA foreign_key_check`.
- The singleton primary key permits at most one run envelope. Exactly one run envelope and exactly one initial BUILDING event before evidence/acceptance remain application-level validation rules.
- Cross-table graph invariants and S3/V1 replay remain the responsibility of the separate immutable adapter/validator; successful SQLite integrity/FK checks alone do not imply provenance acceptance.

## 5. Scope and status

The implementation and tests are restricted to synthetic fixtures and disposable databases. No archive/sidecar, real historical rows, Canonical T0, MAY-10, REST tail, B8 runner, host/workstation, T1/T2, VPS, deployment, credentials, exchange or trading state is accessed or changed.

This amendment is an implementation record, not a declaration that S1.2 is frozen. Independent review and complete DB-to-S3/V1 adapter validation remain outstanding.
