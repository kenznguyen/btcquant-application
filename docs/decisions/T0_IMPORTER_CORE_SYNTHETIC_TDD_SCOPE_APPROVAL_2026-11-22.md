# T0 Importer-Core — Synthetic In-Memory TDD Scope Approval

Date: 2026-11-22
Repository: `kenznguyen/btcquant-application`
Branch: `main`
Status: **OWNER-APPROVED — BOUNDED TDD IMPLEMENTATION ONLY**

## 1. Approval

The owner approves the next TDD work item for the archive importer core, limited to deterministic, pure-Python, in-memory transformation and reconciliation over authored synthetic inputs.

This approval is a narrow implementation authorization. It does not approve archive acquisition, persistent staging, database behavior, or any runtime/data operation.

## 2. Approved behavior

Implement only the following importer-core behaviors, using the existing immutable `ArchiveKlineRow` contract from `market_data/archive_csv_parser.py` as the parsed-row input boundary:

1. **Input contract and normalization**
   - Accept explicitly supplied timeframe and source-batch metadata plus already parsed `ArchiveKlineRow` values.
   - Produce immutable normalized candle candidates without float coercion; preserve exact Decimal values and all 12 original source field strings.
   - Use the designed candle identity tuple: exchange, market_type, symbol, timeframe, open_time_ms. For this bounded BTCUSDT scope, exchange/market/symbol values must be explicit inputs or fixed validated constants; never infer them from filenames or source paths.
   - Preserve the archive semantic `BAR_CLOSE_BOUNDARY` and the parser-provided boundary timestamp. Do not synthesize `FIRST_OBSERVED`.

2. **Row accounting**
   - Account for every supplied source row exactly once as accepted, identical duplicate, or rejected/conflicting.
   - Return explicit counts and deterministic dispositions; no silent row omission.
   - Retain an in-memory association from every accepted/duplicate candidate to its caller-supplied opaque source reference and 1-based row ordinal. Do not invent a persistent provenance ID or digest format.

3. **Duplicate and conflict reconciliation**
   - Same natural candle identity + identical normalized payload: classify as identical duplicate and retain all contributing source references.
   - Same natural identity + different normalized payload: fail closed and mark the complete in-memory candidate batch quarantined; do not use first-write-wins or last-write-wins.
   - Results must be deterministic regardless of input batch ordering wherever the contract permits.

4. **Coverage-set calculation**
   - For explicit timeframe and caller-supplied UTC-aligned half-open bounds `[start_open_time_ms, end_open_time_ms)`, calculate expected timestamps, observed timestamps, missing timestamps and out-of-range timestamps.
   - Report gaps/extras as facts only. Do not declare a dataset complete or apply a production acceptance threshold.
   - Reject invalid timeframe, misaligned bounds, empty/reversed ranges and malformed row identities fail-closed.

5. **Purity and immutability**
   - No mutation of input rows, source references or caller-owned collections.
   - Stable immutable outputs and stable ordering.
   - No filesystem, ZIP, network, environment, clock, SQLite or other database access.

## 3. TDD sequence and acceptance

- Inspect existing parser, resource-policy and test conventions before coding.
- Add focused synthetic tests first and demonstrate RED on the pre-implementation source.
- Implement the smallest pure module/API to make those tests GREEN.
- Cover valid M15/H1 rows, exact Decimal preservation, BAR_CLOSE_BOUNDARY, accounting conservation, identical duplicates, conflicting duplicates, deterministic ordering, missing/extra grid points, invalid bounds/timeframes, malformed inputs and immutability.
- Run focused importer-core tests, then all `market_data` tests. Record exact commands and exit codes.
- Perform a self-review for scope creep and verify no filesystem/network/SQLite imports or side effects.
- Preserve existing parser and B4 tests/behavior unchanged.

## 4. Contract items deliberately deferred

The following are not frozen by this approval and must not be guessed or implemented:

- Stable archive/object/member/source-row/provenance identifiers.
- Canonical serialization, row/source/candle digest framing or hash algorithms.
- SQL DDL, schema fingerprint, indexes, foreign keys, SQLite `user_version`, transactions or persistence.
- Full `ArchiveObjectEvidence`, `ArchivePairEvidence`, `CsvMemberEvidence`, `SourceRowProvenance` and `CandleProvenanceLink` persistence contracts.
- Real-source header variants, real archive coverage, and source-derived row counts.
- Production completeness/acceptance thresholds or partial-object acceptance.

These remain subject to the separate S1 contract/schema freeze and later approval. The in-memory references in this scope are opaque caller-provided labels only, not a substitute for the future provenance contract.

## 5. Explicit exclusions

No:
- archive/sidecar listing, inspection, retrieval, download, extraction or parsing from real files;
- REST, object-store, host, SSH, local filesystem or destination preflight;
- SQLite open/create/write/DDL, schema migration, DB validation or staging build;
- importer orchestration over real archive paths or acquisition manifests;
- workflow YAML creation/edit, workflow dispatch/rerun, artifact upload or retention changes;
- Canonical T0 or MAY-10 access, mutation, migration, replacement or promotion;
- T1/T2, Feeder/Scheduler/API, VPS/runtime/deployment, credentials, exchange connectivity or trading;
- deletion, cleanup or retention execution.

## 6. Evidence and status rules

After implementation, record:
- RED source SHA and focused test output;
- implementation source SHA and changed-file list;
- focused and full `market_data` test commands/results;
- exact source/test blob SHAs;
- self-review and explicit side-effect/scope inspection;
- PASS / BLOCKED / NOT VERIFIED per acceptance item;
- next gate and all remaining exclusions.

No workflow/artifact evidence is presumed. CI execution and artifact upload require separate approval.

## 7. Approval boundary

**Approved now:** synthetic-only importer-core in-memory TDD source and unit tests as defined in sections 2–3, committed to the existing `main` branch with no branch divergence.

**Not approved:** any item in sections 4–5, workflow/dispatch/artifact operations, S1 schema freeze, or the subsequent SQLite/build/acquisition phases.

