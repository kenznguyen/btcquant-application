# T0 Post-S3 Blocker Audit — 2026-11-22

Repository: `kenznguyen/btcquant-application`
Branch: `main`
Audit type: read-only source/design/governance review
Status: **AUDIT COMPLETE — NEXT DESIGN FREEZE GATE REQUIRED**

## 1. Exact baseline

- Main HEAD at audit start: `0edc15faa3c519d127c0ac88cf64299d6ab4c446`.
- Latest exact-SHA S3 GREEN verification: source `d1651196af3059e00b22f65461dbd897e5c599df`, workflow run [44976543815](https://github.com/kenznguyen/btcquant-application/actions/runs/44976543815), job `137067027769`.
- S3 validator blob: `b94bac0f82ae141984552409f99a5cff70435b3b`; S3 tests `328442917535d555d09b18f0213e1ddfd75a9416`; S3 contract `da89266c7c4d1394c731b1c2304cdb73b077d4f6).
- S3 synthetic 30/30, V1 compatibility 24/24, full `market_data` 387/387: PASS. No full repository regression.
- S1 design proposal blob: `af7c90af0f0bcfa8d0b2143578222619af620197`.
- Provenance-first staging design blob: `7ed87e9e643a5ab91baffd420bf911642d0c40c9`.
- Header V1 parser evidence: exact tested SHA `54317ad0aaaa8d547889b41336c0aaed4b1d09bc`, 34/34 focused tests PASS; real-source format evidence covers only M15 monthly 2022-08.

## 2. Closed blockers

| Area | Disposition | Evidence / limit |
|---|---|---|
| S3 pure provenance validator | PASS | Eleven S3 diagnostics appended; deterministic in-memory validation; no I/O/input mutation |
| S4 synthetic specification | PASS | Positive valid fixture, isolated negative cases, aggregate order/dedup, permutation tests |
| V1 compatibility | PASS | Original RED/GREEN test blobs unchanged; 24/24 |
| S3/market_data CI | PASS | Exact-SHA run 44976543815; market_data 387/387 |
| CSV header parser implementation | PASS, narrow | Exact 12-column header verified only for M15 monthly 2022-08; 34/34 tests |

## 3. Remaining blockers

### B1 — S1 SQLite schema is not yet a coherent frozen contract (BLOCKING)

The S1 proposal's original DDL conflicts with its later failed/incomplete-evidence amendment:

- `archive_objects` DDL still requires measured size/hash, response status, local path and exclusive-create fields, while the amendment permits these to be NULL for incomplete/quarantined attempts.
- `archive_pairs` DDL forces assertion, CRC, structure and member count to success, while the amendment requires failed/partial pair evidence to be retained.
- `csv_members.pair_id UNIQUE` conflicts with the amendment allowing zero or multiple observed candidate members for a failed ZIP.
- The amendment requires append-only `acquisition_attempts`, but the original DDL does not yet include its complete table/index/constraints.
- The successful-attempt relationship is explicitly unresolved (circular FK versus separate relation).
- The S3 contract now freezes R4 expected-vs-measured object evidence, R5 `raw_fields_json`, and R6 coverage manifest semantics; the S1 persistence schema has not been reconciled to all three.
- The S1 design has no final persisted shape for the coverage manifest/run-level acceptance evidence.

Required resolution: a documentation-only S1.1 schema reconciliation. Freeze exact table shapes, nullable/failure semantics, attempt history and successful-attempt relationship, manifest persistence, and application-level cross-table constraints. No executable DDL or SQLite is included.

### B2 — SQLite runtime and STRICT compatibility (BLOCKING FOR DDL)

- S1 requires STRICT tables but does not pin a supported SQLite runtime.
- Minimum SQLite version for STRICT support must be explicit (SQLite 3.37.0 or later); the exact Python/runtime build and SQLite library version must be pinned and checked in a later separately approved CI implementation.
- Foreign-key enforcement is connection-local and must be verified on each writer and read-only validator connection.
- No SQLite runtime test or database creation is authorized by S3.

Required resolution: freeze the minimum version policy and exact runtime verification contract in S1.1; defer executable runtime smoke and DDL tests to a later approval.

### B3 — Real archive format coverage across 202 ZIPs (BLOCKING FOR FULL CANDIDATE)

- The strict header parser has one approved real-source sample: M15 monthly 2022-08.
- H1, daily/monthly variants, alternate member paths, encoding/BOM/newline details and header presence across the other 201 ZIPs remain NOT VERIFIED.
- The parser may fail closed and quarantine unsupported members; no format may be inferred from the single sample.

Required resolution: owner-approved, exact-key, bounded source-sample inspection or the later full acquisition run with per-member evidence. This is an archive-access gate, not solvable by synthetic tests alone.

### B4 — Decompression and local resource budget (BLOCKING FOR ACQUISITION)

Not frozen:
- per-member and aggregate uncompressed-byte ceilings;
- maximum compression ratio and ZIP entry-count/member-name/path constraints;
- safe extraction strategy and temporary-space accounting;
- minimum free-space reserve and disk/inode preflight;
- concurrency, per-object timeout, total run timeout, retry count/backoff;
- enforcement relationship to the existing 100 MiB cumulative transferred-response cap.

Required resolution: prepare explicit numeric proposals with worst-case arithmetic and fail-closed behavior, then obtain owner approval before workflow/acquisition implementation. Do not invent source sizes or claim the current runner/destination meets a budget.

### B5 — Coverage manifest values and actual archive completeness (BLOCKING FOR ACCEPTANCE)

- S3 R6 freezes the manifest shape and exact-set semantics, but no freshly measured archive-derived coverage manifest exists.
- Historical totals M15 241,440 / H1 60,360 and archive cutoffs are references, not fresh evidence.
- Earliest history and post-2026-11-18 tail remain unverified; REST tail is closed by owner decision and must not be retried.
- Actual gaps, extras, duplicates and conflicting natural keys require source-derived evidence.

Required resolution: only after a separately approved acquisition and offline parse, compute the actual coverage manifest. Keep the output labelled `RECONSTRUCTED — PARTIAL COVERAGE`.

### B6 — Retention and artifact policy (BLOCKING FOR ACQUISITION/ARTIFACT UPLOAD)

- Source archive retention, evidence artifact contents and artifact TTL remain separate owner decisions.
- No automatic deletion/cleanup is authorized.
- Artifact retention is temporary transport/review, not durable Canonical storage.

Required resolution: specify what is retained, where, for how long, who can access it, and the cleanup approval boundary before acquisition or artifact upload.

### B7 — Execution destination and ownership (BLOCKING FOR PREFLIGHT/ACQUISITION)

- The former VPS was deleted.
- The prior proposed `/srv/btcquant/staging/...` path is explicitly not an active approved destination.
- A new owner-controlled host/path and its ownership, mount, permissions, empty/create-only status and free-space evidence are not established.

Required resolution: owner identifies and separately approves an exact destination; preflight must STOP on any unverifiable property. No alternate path may be substituted.

### B8 — Importer and independent validation implementation (BLOCKING FOR DATA BUILD)

- Importer source SHA and dependency lock do not exist as an approved implementation baseline.
- Offline transformation, row accounting, duplicate reconciliation, coverage calculation and source-to-staging comparison are design-only.
- S3 validator is not an importer and does not prove a real archive or SQLite dataset is valid.

Required resolution: separately approve synthetic-only importer RED/GREEN, then separate DB/SQLite work, and finally a one-run acquisition/build/validation package. Each phase must have its own exact-SHA evidence.

### B9 — T0 application foundation independent review (SEPARATE TRACK)

- The active-scope index records independent review PR #3 and PR #4 as OPEN / UNMERGED with no genuine reviewer verdict.
- This is separate from the archive-staging S3 validator and is not closed by S3 GREEN.
- Do not merge review-only PRs as implementation.

Required resolution: obtain genuine second-person reviews against the current exact source snapshot or formally leave this track NOT VERIFIED. No code change is inferred.

## 4. Explicit non-blockers / immutable boundaries

- Former Canonical SQLite is LOST; no recovery or migration attempt is in scope.
- REST tail is NOT VERIFIED — CLOSED BY OWNER DECISION / NO FURTHER RETRIEVAL. It is an accepted coverage limitation for a partial reconstruction, not an actionable retrieval task.
- MAY-10 remains excluded.
- T0 remains independent from T1/T2 runtime and trading.
- No live orders, VPS deployment, systemd/autostart, Postgres activation, retention/deletion or promotion.
- The target label remains `RECONSTRUCTED — PARTIAL COVERAGE`; never call it recovered Canonical or complete history.

## 5. Recommended sequence

1. **S1.1 documentation-only reconciliation** — resolve B1/B2 and align original DDL proposal with the failure-evidence amendment and S3 R3–R6.
2. **Resource/retention/destination decision package** — propose explicit budgets and retention/destination controls for owner decision; no source access.
3. **Source-format verification gate** — request separate exact-scope approval for additional archive samples; do not dispatch or fetch without it.
4. **Synthetic-only importer design/tests** — request a separate approval; no archive files or DB.
5. **SQLite schema/build** — separate approval after S1.1 freeze and runtime policy; new disposable DB only.
6. **Acquisition + staging run** — separate explicit approval naming inventory, workflow/source SHA, destination, limits, retention, importer SHA and acceptance criteria.
7. **Read-only acceptance** — separate approval; no Canonical promotion.

## 6. Audit non-actions

This audit used repository documentation and source readback only. It did not:
- access, download, list or materialize archive/sidecar data;
- call Binance or retry the closed REST tail;
- access Canonical T0, MAY-10, SQLite files or a staging database;
- create/modify DDL, importer, runtime, workflow, VPS or deployment;
- change retention, delete data, access credentials or place orders.

## 7. Current disposition

- S3 GREEN: **PASS**.
- S1 schema freeze: **BLOCKED — DDL/amendment/S3 contract reconciliation required**.
- Real archive format compatibility: **NOT VERIFIED** beyond the single approved M15 monthly sample.
- Acquisition resource/retention/destination gates: **BLOCKED / OWNER DECISION REQUIRED**.
- Importer/SQLite staging/data build: **NOT AUTHORIZED / NOT IMPLEMENTED**.
- REST tail: **CLOSED — DO NOT RETRIEVE**.
- Recommended next bounded task: **S1.1 documentation-only schema reconciliation**, then request explicit owner approval for that design freeze. No later phase is implied.
