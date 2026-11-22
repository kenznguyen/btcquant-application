# T0 S1.2 — Independent DDL & Compatibility Review

Date: 2026-11-22  
Repository: `kenznguyen/btcquant-application`  
Branch: `main`  
Review baseline HEAD: `3e178d5d4bd1bcb5bb652798ddadf31034b91580`  
S1.2 blob: `78ec1b642e9b5b5e4e161f7e4afdbfe3bccf0d3b`  
Review scope: read-only static review of DDL, FK/constraints, S3/V1 projection, duplicate/disposition rules and B8 execution model.

## Verdict

**DO NOT FREEZE S1.2 YET — REQUIRED DESIGN REVISIONS.**

The proposal is materially stronger than the earlier S1.1 logical-only specification. It resolves several conceptual gaps and preserves the important boundaries: no persistence implementation, no adapter, no adapter tests, no SQLite execution, no archive access and no runtime operation.

However, the current DDL has SQLite CHECK-constraint NULL loopholes, and the physical-to-S3/V1 projection is not yet exact. B8 is technically possible but is not sufficiently specified or approved as an execution/security boundary. These are design blockers, not reasons to start implementation.

This is a fresh review pass against the exact source snapshot. It is not represented as a second-human/external audit. No SQL was executed or parsed by SQLite; SQL runtime validity therefore remains NOT VERIFIED.

## Exact source reviewed

| Component | Path | Blob SHA |
|---|---|---|
| S1.2 proposal | `docs/design/T0_ARCHIVE_STAGING_S1_2_PROVENANCE_IMPORTER_PHYSICAL_SCHEMA_SPEC_2026-11-22.md` | `78ec1b642e9b5b5e4e161f7e4afdbfe3bccf0d3b` |
| S1.1 logical contract | `docs/design/T0_ARCHIVE_STAGING_S1_1_PROVENANCE_SCHEMA_RECONCILIATION_2026-11-22.md` | `209c9d10cc0e54dc90148efa9ef6884f74aa143d` |
| S3 contract | `docs/design/T0_PROVENANCE_VALIDATOR_S1_COVERAGE_AMENDMENT_2026-11-22.md` | `da89266c7c4d1394c731b1c2304cdb73b077d4f6` |
| V1 interface | `docs/design/T0_PROVENANCE_VALIDATOR_INTERFACE_V1_2026-11-22.md` | `632eb6d38461ea3c65638ca073abc5fe4ae98729` |
| S3 validator | `market_data/archive_provenance_validator.py` | `b94bac0f82ae141984552409f99a5cff70435b3b` |
| Importer core | `market_data/archive_importer_core.py` | `a7d7245fe7379f3d3b67c0a111e906a4364f6d10` |
| CSV parser | `market_data/archive_csv_parser.py` | `10fe2313103c45d5455f17ff71f3fd0af2e6f038` |

## Findings

### S12-01 — CRITICAL: SQLite CHECK constraints can accept missing VERIFIED fields

SQLite CHECK constraints reject an expression only when it evaluates to zero. An expression evaluating to NULL is accepted. Several S1.2 CHECK expressions use nullable comparisons without separately requiring the field to be non-NULL.

Affected examples:

- `archive_objects`: the VERIFIED branch uses `requested_key=object_key` and `exclusive_create=1`, while both fields are nullable. A NULL comparison can make the compound CHECK evaluate to NULL rather than false. The separate requested-key CHECK explicitly permits NULL.
- `archive_pairs`: the VERIFIED branch compares nullable `assertion_matches=1`, `zip_crc_ok=1`, `candidate_member_count=1` and `structural_ok=1` without explicit non-NULL guards. These can pass the compound CHECK through NULL semantics.
- `csv_members`: the VERIFIED branch uses nullable equality/ordering checks such as `encoding='UTF-8'`, `delimiter=','`, `parser_contract_id=...` and `data_row_count>0`. It also only requires `bom_present IS NOT NULL` and `newline IS NOT NULL`, not the exact S3 values.
- `source_rows`: the ACCEPTED branch compares nullable `exchange`, `market_type`, `symbol` and `timeframe` values without explicit non-NULL guards. The conjunction can evaluate to NULL and be accepted.

**Required revision:** make every required value explicitly non-NULL before equality/ordering checks, or wrap the full predicate in `COALESCE(predicate, 0)`. Prefer explicit `IS NOT NULL` plus exact-value checks for clarity. Also enforce exact VERIFIED member values (`encoding=UTF-8`, `bom_present=0`, `newline=LF`, delimiter, header contract and row-count rules). Do not rely on the later S3 validator to compensate for a DDL contract that labels invalid rows VERIFIED.

### S12-02 — CRITICAL: Attempt DDL vocabulary and columns do not directly project to S3/V1

The S1.2 `acquisition_attempts.outcome` CHECK permits:

- `STARTED`
- `HTTP_FAILED`
- `TRANSFER_FAILED`
- `TRANSFERRED`
- `VALIDATION_FAILED`
- `UNKNOWN`

The current S3 validator recognizes `STARTED`, `TRANSFERRED`, and the failure outcomes `FAILED` / `UNKNOWN`. It does not recognize the three S1.2-specific failure tokens. They reach the unsupported-outcome branch and invalidate the attempt history.

The DDL also does not persist attempt-level `expected_size_bytes` or `expected_sha256`, while S3 validates those fields on each transferred attempt against the object-level expectations. They may be projected from `archive_objects`, but S1.2 does not specify that projection or prove that it is truthful for every retry.

Additional projection aliases/derivations need to be explicit:
- physical `candidate_member_count` → S3 `member_count`;
- physical `raw_fields_json` → S3's exact 12-string `raw_fields` array;
- the S3 `importer_contract_id` field, which is not a physical `source_rows` column;
- object `attempt_count` and `successful_attempt_id`, derived from attempt history and `object_successful_attempt`.

**Required revision:** add a complete physical-row-to-S3/V1 field projection matrix. Define exact type, alias, derivation, null behavior and failure behavior for every field. Either store attempt expected values or explicitly define their immutable derivation from the object record. Map physical failure subtypes to the unchanged S3/V1 outcome vocabulary without losing the subtype (for example, preserve it in a stable physical failure code while projecting the V1-compatible `FAILED`). Do not change S3/V1 identifiers or meanings implicitly.

### S12-03 — REQUIRED: Headerless parser output conflicts with current S3 member/ordinal rules

S1.2 B5 and the DDL allow `header_present=0`, with physical ordinal equal to data ordinal. The DDL's VERIFIED member branch does not prohibit this.

The current S3 validator, however, requires:
- `header_present == 1`;
- `header_contract_id == T0_ARCHIVE_CSV_HEADER_V1`;
- `physical_record_ordinal == data_row_ordinal + 1`.

Therefore a headerless document accepted by the parser cannot be projected as a VERIFIED S3 member/source-row set under the unchanged S3 contract. S1.2 currently claims parser and S3/V1 compatibility without resolving this case.

**Required revision:** given the explicit no-S3/V1-change boundary, define headerless members as QUARANTINED / not eligible for CANDIDATE until the validator contract is separately versioned and approved; tighten the DDL so a VERIFIED member cannot be headerless. Alternatively, request a separately versioned S3 contract change. Do not silently make the S3 projection invent a header or offset.

### S12-04 — REQUIRED: Conflict disposition can assign a false candle-conflict reason

Importer core's duplicate payload includes source-only fields (close time, quote volume, trade count, taker-buy values and `ignore`). A difference in one of those fields can cause `RowDisposition.CONFLICTING` and quarantine the batch even when the S3 normalized candle tuple is identical.

S1.2 correctly says that source-only fields do not participate in candle-value equality and also says a core-quarantined batch must remain quarantined. That conservative fail-closed choice is acceptable. But B3 currently maps every core `CONFLICTING` row to `REJECTED` with `CANDLE_IDENTITY_CONFLICT`. That code is inaccurate when the conflict came only from source-only fields and S3 would see one normalized candle value.

**Required revision:** distinguish an importer-core payload conflict from an S3 normalized candle identity/value conflict. Preserve whole-batch quarantine, but use a truthful stable internal rejection/failure reason for the source-only-field case. Reserve the S3 candle-conflict meaning for genuinely different normalized candle tuples. State explicitly that this conservative core behavior may reduce accepted coverage.

### S12-05 — REQUIRED: The one-run-per-database invariant is not enforced by the DDL

S1.1 defines exactly one `reconstruction_run` envelope per staging database. S1.2's DDL gives `run_id` a primary key but permits multiple rows. Child evidence tables are not keyed by `run_id`; they are linked through object/pair/member/source relationships and the inventory ID.

A database containing multiple run rows could therefore mix run envelopes without a physical constraint identifying which run owns the shared evidence.

**Required revision:** enforce a singleton run envelope (for example, a fixed singleton key constrained to one value) or explicitly define a separate per-run database invariant that is verified before any evidence is written and again by read-only acceptance. The DDL and acceptance contract must not leave this implicit.

### S12-06 — REQUIRED: B8 is technically feasible but not yet a sufficiently safe/complete execution contract

A manually started ephemeral self-hosted runner can technically receive a `workflow_dispatch` job and provide genuine workflow/run provenance. It is compatible with manual/on-demand operation in principle. It is not equivalent to a sandbox merely because it is ephemeral.

Missing decisions/specification include:
- exact meaning and acquisition method for `workflow_job_id` (GitHub's job key/context and the numeric Actions job ID are distinct identifiers);
- minimum GitHub token permissions/API call needed to obtain the chosen job ID;
- runner group restricted to this repository, exact approved branch/ref and source SHA, labels, single-job/concurrency policy and workflow permissions;
- how the runner process and working directory are isolated from the workstation's personal files, credentials and unrelated projects;
- cleanup/revocation after success, failure, cancellation or host crash; `--ephemeral` unregisters a runner after a job but does not by itself sanitize the host or remove all local state;
- network egress and filesystem mount boundaries for the acquisition job.

**Assessment:** B8 preserves the existing S3/V1 attempt identity without fabricating IDs, but it adds GitHub as an execution orchestrator and a self-hosted code-execution surface on the owner workstation. That is a material operational/security decision, not a mere provenance mapping. It is not ready to freeze. A disposable, encrypted, tightly restricted VM/runner environment would be safer than running repository workflow code directly in the owner's normal workstation session, but that choice itself needs owner approval and preflight.

**Required revision:** specify the trust boundary and exact job-ID provenance, then obtain explicit owner acceptance of this execution model. If direct local Python execution remains preferred, do not fabricate workflow IDs; propose a separately versioned S3/V2 execution-context contract and attempt-ID scheme for owner review.

### S12-07 — REQUIRED: Cross-table relationship enforcement remains partly application-only

Some relationships are represented by independent foreign keys rather than composite constraints. In particular, `object_successful_attempt` separately references `object_id` and `attempt_id`, so SQLite can accept a relation whose attempt belongs to a different object. The design says the application validator must catch this; that is safe only if the future adapter/acceptance contract proves it and the relationship is tested.

Other cross-record invariants (inventory ownership, pair object kinds/reciprocal pairing, member-to-pair cardinality, row-to-member disposition, link-to-source/candle value equality, failure subject existence) are also not all expressible by the current local constraints.

**Required revision:** decide which invariants should be strengthened with composite UNIQUE/FK constraints (especially same-object successful attempt) and list every remaining application-only invariant with its authoritative validator check. Do not treat `foreign_key_check` alone as proof of graph consistency.

### S12-08 — OPTIONAL: Bound SQLite INTEGER values explicitly

Importer/core and S3 work with Python integers, while SQLite INTEGER is signed 64-bit. S1.2 currently specifies non-negative/aligned integers but no explicit upper bound for timestamps, byte counts, ordinals and counts. Values outside signed 64-bit can fail during binding rather than producing a deterministic validation/quarantine result.

**Suggested revision:** define `0 <= value <= 2^63-1` at the adapter boundary for every persisted INTEGER field and specify the fail-closed diagnostic.

## Assessment by requested focus

| Focus | Result |
|---|---|
| DDL correctness | **BLOCKED** — CHECK NULL loopholes; singleton run invariant missing |
| Foreign keys and constraints | **PARTIAL** — basic graph FKs present; same-object and several cross-record relationships rely on application validation |
| Exact S3/V1 compatibility | **BLOCKED** — attempt outcome/field projection and headerless behavior unresolved |
| Duplicate and row disposition | **PARTIAL** — deterministic representative rule is good; source-only core conflicts need truthful reason mapping |
| B8 feasibility and fit | **TECHNICALLY FEASIBLE / NOT READY TO FREEZE** — owner security/execution decision and provenance details missing |

## What is already sound

- S1.2 retains S1.1/S3/V1 precedence and does not mutate the S3/V1 public API.
- `usdm` is explicitly required for persisted BTCUSDT USD-M candles; the generic core is not silently rewritten.
- Source-row identity is separated from normalized candle-value identity.
- S3 R6's UTF-8-byte ordering for the single UNIQUE duplicate representative is retained.
- Half-open to inclusive coverage conversion is explicit and can be checked by exact expansion.
- Parser failure is honestly modeled as member-level quarantine; no partial rows are fabricated.
- Append-only run events are a better model than updating a mutable status column.
- The proposal correctly keeps B3/B5 real-source coverage, exact runtime pins, workstation preflight, adapter, adapter tests and SQLite implementation as separate gates.

## Verification boundary

- Exact baseline source inspected: `3e178d5d4bd1bcb5bb652798ddadf31034b91580`.
- DDL was reviewed statically only. No SQLite connection, DDL execution, SQL parser, schema creation, adapter, test or workflow was run.
- No archive/sidecar, filesystem, workstation, runner, Canonical T0, MAY-10, T1/T2, VPS, runtime, credential, exchange or trading operation occurred.
- Workflow run/artifact: **NONE** for this review.
- SQL syntax/runtime compatibility and actual `foreign_key_check` behavior: **NOT VERIFIED**.

## Recommendation

Keep S1.2 as a design proposal and request a narrowly scoped documentation-only revision addressing S12-01 through S12-07. S12-08 can be included in the same amendment if the owner wants the integer boundary frozen now.

Do not freeze S1.2 yet. Do not begin adapter, adapter tests, SQLite DDL execution/implementation, or B8 runner provisioning. After the revised S1.2 is reviewed against the same exact S3/V1 and importer/parser SHAs, make a separate owner decision on design freeze. Every later implementation gate remains separate.
