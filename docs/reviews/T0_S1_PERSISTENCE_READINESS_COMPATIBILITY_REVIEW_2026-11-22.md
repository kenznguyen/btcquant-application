# T0 S1 Persistence-Readiness Compatibility Review — 2026-11-22

Repository: `kenznguyen/btcquant-application`
Branch: `main`
Review type: same-session read-only design/code review (not independent)
Baseline `main` HEAD: `08ae0a8d9d0c595b188e3f158b4db7733f0de11f`

## 1. Executive disposition

**BLOCKED BEFORE PERSISTENCE — S1.1 is owner-accepted and design-frozen at the logical contract level, but the frozen design is not yet fully reconciled with the completed synthetic importer-core and is not an executable persistence specification.**

This review does not reopen the accepted S1.1 design wholesale. It identifies the narrow contract bridges and schema details that must be explicitly reconciled before any persistence implementation is proposed.

No source, tests, workflow, DDL, SQLite, archive, staging, Canonical T0, runtime or data were changed or accessed in this review.

## 2. Reviewed source baseline

| Component | Path | Blob SHA |
|---|---|---|
| S1.1 logical persistence design | `docs/design/T0_ARCHIVE_STAGING_S1_1_PROVENANCE_SCHEMA_RECONCILIATION_2026-11-22.md` | `209c9d10cc0e54dc90148efa9ef6884f74aa143d` |
| S1.1 prior self-review | `docs/reviews/T0_S1_1_SCHEMA_RECONCILIATION_SELF_REVIEW_2026-11-22.md` | `a46dd4ce9b64bad09a6ccec078476fa10dc67a65` |
| S3 validator coverage contract | `docs/design/T0_PROVENANCE_VALIDATOR_S1_COVERAGE_AMENDMENT_2026-11-22.md` | `da89266c7c4d1394c731b1c2304cdb73b077d4f6` |
| S3 validator implementation | `market_data/archive_provenance_validator.py` | `b94bac0f82ae141984552409f99a5cff70435b3b` |
| Synthetic importer core | `market_data/archive_importer_core.py` | `a7d7245fe7379f3d3b67c0a111e906a4364f6d10` |
| CSV parser | `market_data/archive_csv_parser.py` | `10fe2313103c45d5455f17ff71f3fd0af2e6f038` |
| Importer-core focused tests | `market_data/test_archive_importer_core.py` | `3dfc58b570789d8ea6d172e442266743b9157bf5` |

S1.1 is recorded as owner accepted/design frozen in the controlling handoff. Its own final section still says “DRAFT COMMITTED FOR OWNER ACCEPTANCE”, and the earlier self-review says acceptance is pending. These are stale contradictory status statements and should be corrected in documentation only; the current handoff records the owner acceptance.

## 3. Blocking contract mismatches

### B1 — Canonical market_type token mismatch

- S1.1/S3 require `market_type="usdm"` for the supported Binance USD-M BTCUSDT dataset.
- The importer-core synthetic tests use `market_type="usd_m"`; the core accepts any non-empty caller-provided string and does not enforce the S1 canonical token.
- Consequence: the natural key and `candle_value_id` would differ if persisted without a mapping decision.

**Required resolution:** explicitly choose the canonical persisted token from the already-approved Candle Contract 1.2.0 vocabulary, then add a boundary mapping/validation contract. Do not silently rewrite the current importer-core identity.

### B2 — Duplicate equality is not aligned

- Importer core compares a payload containing OHLCV plus source close time, quote volume, trade count, taker-buy values and the source `ignore` field.
- S1/S3 duplicate semantics compare the normalized candle tuple/value ID: natural identity plus normalized OHLCV and availability boundary/kind. All contributing source rows remain linked even when they are identical normalized candle values.
- Thus two rows with the same candle value but a different source-only field (for example `ignore`, quote volume or trade count) are currently marked CONFLICTING by importer core, although S1's candle-level rule would treat them as the same normalized candle value with separate source provenance.

**Required resolution:** freeze the exact distinction between source-row equality and candle-value equality. Preserve every raw source row; determine duplicate/conflict at the normalized candle tuple boundary specified by S3. No first/last-write-wins.

### B3 — Row disposition and provenance-link disposition differ

- Importer core exposes row dispositions `accepted`, `identical_duplicate`, `rejected`, `conflicting`.
- S1.1 `source_rows` uses `ACCEPTED` or `REJECTED`; each accepted source row has one link. Duplicate role is represented on the link as `UNIQUE` or `IDENTICAL_DUPLICATE`.
- A source row classified as `IDENTICAL_DUPLICATE` by importer core currently has no direct, frozen mapping to S1's accepted-row/link model. Conflict rows also have no frozen persisted disposition mapping.

**Required resolution:** define one mapping table from in-memory row outcomes to persisted source-row disposition, rejection code, candle existence and link disposition. Define how conflicting rows are retained in a quarantined run without manufacturing a valid candle/link.

### B4 — Coverage boundary convention differs

- Importer core calculates half-open ranges `[start_open_time_ms, end_open_time_ms)`.
- S3 R6 coverage manifest uses inclusive `end_open_time_ms`.
- These are both valid conventions but are not interchangeable without a deterministic adapter. A direct field copy causes an off-by-one-candle error.

**Required resolution:** define the adapter formula and overflow/empty-range behavior explicitly (for example, derive inclusive end from the last expected open time), and test boundary cases before persistence. Do not change either frozen contract implicitly.

### B5 — Opaque importer references are not S1 provenance IDs

- Importer core retains caller-provided opaque `source_ref` plus one-based `row_ordinal`.
- S1.1 requires inventory/object/pair/candidate/member/source-row identities, physical and data row ordinals, exact raw fields, T0ENC1 raw-row digest, parser contract/source SHA and importer source SHA.
- The importer-core approval explicitly deferred stable IDs and digest framing, so this is an expected scope boundary, not a defect in the bounded core.

**Required resolution:** define a separate provenance adapter from verified object/member context and parser row metadata into the frozen S1 IDs and source-row records. Preserve the current core's opaque reference as non-authoritative context only. Define physical ordinal vs data ordinal, including header offset.

### B6 — Parser failure model cannot yet persist every rejected data row

- The current parser returns a complete tuple only when the entire CSV document parses successfully; malformed row input raises `ArchiveCsvError`.
- S1.1 requires row-level accepted/rejected provenance for data records considered, with no silent skip, and retains rejected-row evidence.
- On a parser exception, the current interface does not return a partial result containing the failing row's raw fields/ordinal and any later rows that can still be safely framed.

**Required resolution:** decide whether parser-level malformed input is recorded only as member-level quarantine (with no row records for an unparseable member), or introduce a separately approved row-diagnostic parser contract that can retain raw record/ordinal/error without weakening strict parsing. The rule must distinguish malformed CSV framing/encoding from a validly framed but semantically invalid 12-field row.

### B7 — Run lifecycle conflicts with append-only/no-update rule

- S1.1 defines `BUILDING → CANDIDATE → VALIDATED` or terminal `QUARANTINED`.
- It also says immutable/append-only behavior has no update/delete path.
- A single `reconstruction_run.status` column cannot both transition through these states and remain immutable if the same row is updated.

**Required resolution:** choose an append-only run-event/status-history model and derive the current status, or explicitly authorize a narrowly constrained status-only transition while all evidence rows remain immutable. Define who records CANDIDATE and VALIDATED, and how validation result/source SHA is bound to the exact closed database snapshot.

### B8 — Acquisition-attempt identity assumes GitHub workflow provenance

- S1.1 attempt identity includes `workflow_run_id`, `workflow_job_id` and `trigger_sha`; these fields participate in the stable `att1:` digest.
- The accepted B7 destination strategy is an owner-controlled encrypted personal workstation with manual/on-demand execution. A local invocation does not inherently have GitHub workflow/job IDs.
- Substituting placeholders such as “manual” would misrepresent workflow provenance and could create ambiguous attempt identities.

**Required resolution:** either explicitly require archive acquisition to run inside a GitHub workflow (which is not currently approved), or define a truthful execution-context contract for local/manual runs and amend the attempt identity inputs/version accordingly. Do not fabricate workflow IDs.

### B9 — S1.1 is logical schema design, not a complete executable DDL contract

- S1.1 explicitly labels its model normative but not executable SQL; the original success-only DDL is historical and superseded where it conflicts.
- The schema ID `T0_STAGING_SCHEMA_V2` and `user_version=2` are retained, but a single reconciled executable schema definition, complete PK/FK/UNIQUE/CHECK/index set, deterministic schema fingerprint algorithm and exact table/column ordering are not frozen in the S1.1 reconciliation itself.
- The S1.1 self-review correctly states that it does not prove SQL validity or SQLite compatibility.

**Required resolution:** prepare a separate S1.2 DDL contract derived from S1.1, including exact table/column types/nullability, primary/foreign/unique constraints, indexes, CHECK constraints, allowed status transitions, schema fingerprint bytes/algorithm and migration prohibition. Review it against the S3 payload projection before any DDL implementation.

### B10 — Failure evidence cardinality needs an explicit representation

S1.1 requires retaining every known failure and S3 can emit multiple stable error codes, while some logical evidence records describe a singular `failure_code`. Define whether a record can carry multiple deterministic failure codes or whether a normalized append-only failure-observation relation is required. Avoid silently dropping secondary failures.

## 4. Other readiness gates (not design defects)

| Gate | Current state | Effect |
|---|---|---|
| B3 real archive format coverage | NOT VERIFIED beyond M15 monthly 2022-08 | Blocks real-source compatibility/acceptance |
| B4 resource budgets | Owner accepted as design; implementation not authorized | Limits acquisition implementation |
| B5 actual source-derived coverage | NOT VERIFIED | Blocks coverage/completeness claims |
| B6 retention | Owner accepted preserve-until-explicit-delete; no deletion/upload authorized | No cleanup/artifact action |
| B7 destination | Option A selected; exact device/path and preflight pending | Blocks host execution |
| SQLite/Python exact runtime pins | Deferred to later implementation approval | Blocks reproducible SQLite build |
| Independent review | Not claimed; same-session self-review only | Review evidence must retain correct label |

These gates are not reasons to reopen S1.1's accepted principles; they are execution prerequisites or separately scoped decisions.

## 5. Recommended next sequence

1. Keep S1.1 accepted principles frozen; do not alter its identifiers, T0ENC1 framing, S3 error catalogue or `T0_STAGING_SCHEMA_V2` by implication.
2. Approve a documentation-only S1.2 compatibility amendment resolving B1–B10, including explicit mapping tables and exact run/attempt provenance semantics.
3. Produce a single exact logical-to-physical schema matrix and executable DDL specification with deterministic schema fingerprint; record it as design only.
4. Review the importer/parser-to-S1 adapter contract, then request separate approval for synthetic-only adapter tests/implementation.
5. Only after adapter contracts and runtime pins are accepted, request a separate SQLite schema/build scope. This review grants no such authority.
6. Keep archive access, real-source parsing, acquisition, destination preflight, staging execution, Canonical promotion and runtime excluded until their own approvals.

## 6. Verification and status

- Read-only source/document inspection at baseline main HEAD `08ae0a8d9d0c595b188e3f158b4db7733f0de11f`.
- Reviewed exact source blobs listed in §2.
- No code, test, workflow, schema, DDL, SQLite, archive, host, data, Canonical T0, runtime or deployment changes.
- No tests or workflow runs were executed.
- Review verdict: **SELF-REVIEW — BLOCKED BEFORE PERSISTENCE; S1.1 PRINCIPLES ACCEPTED, S1.2 COMPATIBILITY/PHYSICAL SCHEMA CLOSURE REQUIRED**.
