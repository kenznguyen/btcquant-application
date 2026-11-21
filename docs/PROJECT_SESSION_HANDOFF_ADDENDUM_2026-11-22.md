# PROJECT SESSION HANDOFF ADDENDUM — 2026-11-22

Repository: kenznguyen/btcquant-application
Branch: main
Related S1 design commit: 319d3db16da69c59b2efb9e9a0b4a7f5f7afe8e9

## T0 archive staging/importer S1

- Owner approved S1 only: freeze design-level provenance contracts and staging schema.
- S1 design document: `docs/design/T0_ARCHIVE_STAGING_S1_PROVENANCE_SCHEMA_FREEZE_2026-11-22.md`.
- Commit: `319d3db16da69c59b2efb9e9a0b4a7f5f7afe8e9`.
- Scope is documentation only; no code, tests, workflow, archive acquisition, SQLite or data operations.
- Frozen design baseline includes stable content-derived IDs for inventory/object/pair/member/source row/candle value/provenance link; domain-separated SHA-256 framing `T0ENC1`; explicit 12-field raw row preservation; separate natural candle identity and normalized value digest; provenance records for 404 objects, 202 pairs, expected 202 CSV members, every source row and every candle link; deterministic duplicate representative selection; all-or-nothing quarantine for incomplete provenance or conflicting duplicate values.
- Staging schema contract identifier: `T0_STAGING_SCHEMA_V2`; SQLite `user_version=2`; candle natural key retained; `availability_kind=BAR_CLOSE_BOUNDARY`; provenance stored in separate tables.
- Acceptance matrix and cross-record invariants are in the S1 design document. SQLite DDL remains design-only and requires later implementation/testing.
- S1 status: **DESIGN BASELINE COMMITTED; owner review of exact DDL/contracts pending**.
- S2 provenance validator RED tests: **NOT AUTHORIZED**.
- Importer, acquisition workflow, archive requests, staging SQLite, Canonical T0, MAY-10, REST tail, T1/T2, VPS/runtime, deployment and trading remain excluded/not authorized.
- Open gates remain: exact pinned SQLite runtime/STRICT support, cross-table validator invariants, acquisition attempt-history schema/manifest, compression/uncompressed/disk limits, artifact/source retention, and real header-mode verification across all 202 archives.
- Next: owner reviews S1 design. If accepted, request separate approval for S2 synthetic-only provenance validator RED tests. S2 must not access archives, create SQLite or implement importer.

## Repository handoff note

The existing `docs/PROJECT_SESSION_HANDOFF.md` is a very large append-oriented history file. This addendum records the latest state without replacing or truncating that history. At the next handoff maintenance opportunity, merge this addendum into the main handoff and retain this addendum as historical evidence.
