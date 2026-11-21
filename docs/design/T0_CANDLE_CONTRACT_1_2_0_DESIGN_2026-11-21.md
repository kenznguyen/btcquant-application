# T0 Candle Contract 1.2.0 — Schema, API, Migration and Compatibility Design

**Date:** 2026-11-21  
**Repository:** kenznguyen/btcquant-application  
**Branch:** main  
**Status:** DESIGN PROPOSAL — OWNER DECISION B RECORDED; DESIGN REVIEW COMPLETE WITH OPEN GATES  
**Implementation:** NOT STARTED / NOT AUTHORIZED  
**Fixture access:** NOT AUTHORIZED; no representative fixture supplied

## 1. Scope and decisions

This document details the owner-selected option B:
- FIRST_OBSERVED: actual first-observation timestamp for live Feeder candles.
- BAR_CLOSE_BOUNDARY: deterministic exclusive close boundary for archive-derived candles; not a historical observation timestamp.

The owner provisionally approved the expected semantic mapping of the 12 Binance USD-M Kline CSV fields. Exact header/order/parser behavior remains unfrozen until an owner-approved representative fixture is supplied and verified.

This is design only. It authorizes no source changes, schema/API implementation, migration, fixture/archive access, materialization, database creation, import, runtime or deployment.

## 2. Existing implementation baseline

Current-main file blobs inspected:
- market_data/store.py: 4e1b0c54bd56455abe5be0e5c7d0807e63e0bc78
- market_data/api_contract.py: fb16b1d6a69fc35b3609758060d4992b91d25f37
- market_data/initialize_sqlite.py: 58bd2deba66cc667bad8d6446c5ff54e7f5dd240
- market_data/storage.py: ae03c5a1caf68bb292ca2903e187a2a3a2474938

Static observations:
- Candle has available_at_ms but no availability-kind field.
- Candle.as_dict() hardcodes availabilityKind=FIRST_OBSERVED and source=ccxt.binanceusdm.
- SQLite candles stores OHLCV and available_at_ms; primary key is (exchange, market_type, symbol, timeframe, open_time_ms).
- Initializer sets PRAGMA user_version=1.
- API envelope declares contractVersion=1.1.0 and schemaVersion=1.
- API freshness treats availableAtMs as observation time and computes observationAgeMs from it.
- API query parser uses a strict allowlist; this proposal uses HTTP content negotiation, not new query parameters.

These are static source observations, not runtime or migration evidence.

## 3. Proposed data model and SQLite schema

### 3.1 Candle semantics

Add a required typed field:
- availability_kind ∈ {FIRST_OBSERVED, BAR_CLOSE_BOUNDARY}.

Common validation remains unchanged: nonnegative signed-64-bit timestamps, timeframe-aligned open, closed candle, exact decimal OHLCV, valid OHLC bounds.

FIRST_OBSERVED:
- available_at_ms is the actual first-observation timestamp recorded by live ingestion.
- available_at_ms >= open_time_ms + interval_ms.
- Never fabricate this value for archive rows.

BAR_CLOSE_BOUNDARY:
- available_at_ms == open_time_ms + interval_ms.
- Allowed only for a row with validated archive/reconstruction provenance.
- Means bar completion/eligibility at the exclusive close boundary, not when a system first observed it.

Missing or unknown kind must fail closed. Never infer kind from timestamp equality, source filename or caller default.

Binance CSV is expected to carry inclusive millisecond close_time:
source_close_time_ms == open_time_ms + interval_ms - 1.
After validating that convention, derive the internal exclusive boundary:
bar_close_boundary_ms = source_close_time_ms + 1.
The actual fixture must confirm the archive convention before parser freeze.

### 3.2 SQLite schema version 2 proposal

Add one column to candles:

    availability_kind TEXT NOT NULL
        DEFAULT 'FIRST_OBSERVED'
        CHECK (availability_kind IN ('FIRST_OBSERVED', 'BAR_CLOSE_BOUNDARY'))

Set PRAGMA user_version=2. Keep the existing candle primary key and all existing OHLCV/available_at_ms columns. Do not add ancillary CSV fields to the hot candle table. Keep source-object and source-row provenance in a separate immutable reconstruction manifest/evidence set.

Existing rows are proposed to retain the historical 1.1.0 interpretation and migrate as FIRST_OBSERVED. This assumption must be confirmed against the exact target DB and historical producer behavior before migration approval.

The SQL default is only for preserving old-row interpretation during explicit migration. New application writes must supply availability_kind explicitly. Archive writes must explicitly set BAR_CLOSE_BOUNDARY and prove reconstruction provenance.

A simple enum CHECK cannot express timeframe-dependent equality between available_at_ms and open_time_ms + interval_ms. Enforce that invariant in the canonical Candle validator; all writes must pass through it. Do not add a trigger without a separate design need and review.

## 4. Proposed API Contract 1.2.0

### 4.1 Version negotiation

Keep 1.1.0 behavior for old clients. New clients opt in using:

    Accept: application/vnd.btcquant.candles+json;version=1.2.0

Legacy requests with no version continue to request 1.1.0. Unsupported explicit versions return HTTP 406 with a stable machine-readable error. Do not loosen the strict query parser.

### 4.2 1.2.0 response

Keep the existing envelope and fields; set contractVersion=1.2.0 and schemaVersion=2.

Each candle returns:
- availableAtMs: timestamp interpreted according to availabilityKind.
- availabilityKind: FIRST_OBSERVED or BAR_CLOSE_BOUNDARY.
- source: ccxt.binanceusdm for FIRST_OBSERVED; binance.usdm.archive for BAR_CLOSE_BOUNDARY.

Top-level source is mixed when both kinds occur; otherwise it is the single source label. Archive object key, ZIP/sidecar hashes, CSV member and row ordinal remain in the immutable provenance manifest. Do not expose a provenance reference until its format and access rules are separately designed.

### 4.3 Legacy 1.1.0 safety

A 1.1.0 client interprets availability as first-observed. It cannot truthfully represent BAR_CLOSE_BOUNDARY.

- If the requested result contains only FIRST_OBSERVED rows, serve the unchanged 1.1.0 envelope.
- If any returned row is BAR_CLOSE_BOUNDARY, return HTTP 406, code CONTRACT_VERSION_REQUIRED. Do not downgrade, relabel or silently omit rows.
- A 1.2.0 client must inspect availabilityKind. Consumers requiring observation latency or first-seen semantics must require FIRST_OBSERVED.

This is deliberately fail-closed for legacy consumers.

## 5. Freshness and evaluability

observationAgeMs is meaningful only for FIRST_OBSERVED.

For 1.2.0:
- Compute observationAgeMs only when the latest returned candle is FIRST_OBSERVED; otherwise return null.
- Add latestAvailabilityKind.
- Add freshnessReason with at least: FRESH_FIRST_OBSERVED, STALE_FIRST_OBSERVED, LATEST_BAR_CLOSE_BOUNDARY, NO_CANDLES, INVALID_TIMESTAMP_GRID, INCOMPLETE_COVERAGE.
- Latest BAR_CLOSE_BOUNDARY is never fresh/evaluable for a real-time strategy decision, even if it is the latest expected bar.
- If latest is FIRST_OBSERVED, retain existing freshness age/close-lag thresholds and contiguous-grid checks. Earlier archive candles may be indicator history, but remain typed BAR_CLOSE_BOUNDARY.
- evaluable=true requires complete requested coverage, valid contiguous timestamps, latest FIRST_OBSERVED and existing freshness conditions.
- Offline research/backtesting may explicitly opt into archive availability semantics and must retain provenance/coverage labels. This does not authorize live trading.

No existing threshold is changed by this design.

## 6. Migration and rollback plan — design only

### 6.1 Preconditions

Before implementation or execution:
- Read-only inventory of exact deployed schema and user_version in a separately approved environment.
- Confirm old rows truly represent FIRST_OBSERVED under the 1.1.0 producer semantics. If not provable, stop for owner decision; never infer from timestamps.
- Pin source SHA, migration SQL SHA, dependency lock and rollback procedure.
- Verify backup using the approved SQLite backup procedure.
- Stop writers and establish maintenance/lease-fencing plan.
- Obtain separate approval for target DB and migration execution.

The former Canonical SQLite is LOST and no new reconstruction DB exists. This document does not authorize opening, creating or migrating any DB.

### 6.2 Migration sequence proposal

A future migration should:
1. Require user_version=1 and exact expected table/column/primary-key shape; otherwise fail closed.
2. Run in one explicit transaction with no active writer.
3. Add availability_kind with NOT NULL, enum CHECK and migration default FIRST_OBSERVED.
4. Verify every old row is FIRST_OBSERVED; verify row count, primary key, columns, indexes/triggers and existing values are unchanged.
5. Set user_version=2 only after successful verification.
6. Commit atomically; any error rolls back and retains the pre-migration DB.
7. Be idempotent only for the exact fully migrated v2 schema. Partial or ambiguous state fails closed.

The exact SQL strategy (ALTER TABLE versus table rebuild) must be tested against the pinned SQLite runtime and actual schema before implementation. No migration SQL is created here.

### 6.3 Rollback

Preferred rollback is restore of the verified pre-migration backup under an approved maintenance procedure. Do not implement a destructive downgrade that drops availability_kind after archive rows may exist. After v2 archive rows exist, restore/forward-fix must preserve kind and provenance; never coerce BAR_CLOSE_BOUNDARY to FIRST_OBSERVED.

## 7. Backward-compatibility matrix

| Stored row / producer | API 1.1.0 client | API 1.2.0 client |
|---|---|---|
| Existing v1 row migrated as FIRST_OBSERVED | Unchanged 1.1.0 response | Explicit FIRST_OBSERVED |
| New live Feeder FIRST_OBSERVED | Unchanged 1.1.0 response | Explicit FIRST_OBSERVED |
| Archive BAR_CLOSE_BOUNDARY | 406 CONTRACT_VERSION_REQUIRED | Explicit BAR_CLOSE_BOUNDARY |
| Mixed live + archive window | 406 if any archive row is returned | Both kinds; freshness depends on latest kind |
| Unknown kind/schema mismatch | Fail closed | Fail closed |

Existing 1.1.0 clients work for first-observed-only data. Legacy clients are never silently exposed to archive rows under false semantics. No automatic consumer upgrade or T2 runtime connection is included.

## 8. Importer interaction and fixture gate

Importer must create archive candidates with explicit BAR_CLOSE_BOUNDARY; validate source inclusive close_time against the timeframe grid; attach verified source-object and source-row provenance; preserve all 12 fields in raw-row audit evidence or explicit dispositions; and refuse to emit a contract-valid candidate if kind or source mapping is unresolved.

No representative fixture was supplied or accessed in this work item. Exact header, delimiter, encoding, member naming, row width, numeric grammar, timestamp units and close_time convention remain NOT VERIFIED / NOT FROZEN. No archive or fixture materialization is authorized.

## 9. Design review — AI-assisted static review

Review dimensions: correctness, simplicity, architecture, security, performance, compatibility and verification evidence.

### Required gates before implementation

1. Legacy row semantics: migration tagging old rows FIRST_OBSERVED is consistent with 1.1.0 but must be confirmed against the exact target DB and producer history. If not provable, stop for owner decision.
2. Source/availability coupling: source label is derived from availability kind only while FIRST_OBSERVED means live Feeder and BAR_CLOSE_BOUNDARY means archive. A new producer requires a separate source-kind design.
3. Freshness: current freshness code treats every available timestamp as observation time. Kind-aware logic and tests are required before 1.2.0 consumers rely on it.
4. SQLite migration: ALTER TABLE/default/CHECK behavior, transaction rollback and schema-drift fail-closed cases must be tested on the pinned SQLite runtime.
5. HTTP negotiation: FastAPI and WSGI adapters must enforce identical version negotiation and 406 behavior through the shared contract builder.
6. CSV: no approved representative fixture was provided. The provisional 12-field order and timestamp convention are not verified.

### Positive design properties

- No archive timestamp is mislabeled as observation time.
- Existing 1.1.0 clients retain behavior on first-observed-only data.
- Legacy clients fail closed rather than consume archive rows with false semantics.
- Candle identity and OHLCV validation remain unchanged.
- Provenance stays outside the hot Candle row.
- Migration is explicit, version-checked, transactional and rollback-oriented.
- No new dependency is proposed.

### Verdict

**DESIGN REVIEW: PASS WITH REQUIRED GATES / NOT IMPLEMENTATION-READY.**

This is AI-assisted static design review, not human independent review or runtime evidence. No code, schema, API, migration SQL, tests or workflows were changed or executed.

## 10. Acceptance-test design required before implementation

Required cases:
- Missing/unknown availability kind rejects.
- FIRST_OBSERVED preserves actual observation semantics and lower bound.
- BAR_CLOSE_BOUNDARY equals exactly open + interval and requires archive provenance.
- Inclusive Binance close_time validates exactly; off-by-one/timeframe mismatch rejects.
- v1→v2 migration preserves rows, PK and values while assigning FIRST_OBSERVED.
- Migration rejects wrong user_version, schema drift, partial migration and invalid rows.
- Injected migration failure rolls back to original schema/data.
- 1.1.0 unchanged for first-observed-only rows; returns 406 if any archive row is returned.
- 1.2.0 exposes per-candle kind and correct source.
- Mixed windows never report BAR_CLOSE_BOUNDARY as observationAgeMs.
- Latest BAR_CLOSE_BOUNDARY forces fresh=false/evaluable=false with LATEST_BAR_CLOSE_BOUNDARY.
- Latest FIRST_OBSERVED retains existing freshness behavior.
- FastAPI and WSGI negotiation/error behavior is identical.
- Contract/schema version mismatch fails closed.

No tests are created or run in this documentation-only increment.

## 11. Status and next gates

| Work item | Status |
|---|---|
| Owner option B decision | APPROVED — DESIGN |
| 12-column semantic mapping | PROVISIONALLY APPROVED |
| Exact CSV fixture verification | BLOCKED — NO APPROVED FIXTURE PROVIDED |
| Contract 1.2.0 schema/API design | DESIGN REVIEW PASS WITH GATES |
| Migration SQL/code | NOT CREATED |
| Acceptance tests | DESIGN ONLY / NOT CREATED |
| Implementation approval | NOT REQUESTED / NOT GRANTED |
| Importer | NOT STARTED |
| New SQLite | NOT CREATED |
| Archive access/materialization | NOT AUTHORIZED |
| Runtime/deployment/trading | NOT AUTHORIZED |

Next permitted work: obtain owner approval for a specific representative fixture and its source-access/materialization scope; verify and freeze CSV mapping. Separately, owner may review this Contract 1.2.0 design and resolve required gates. Implementation requires separate explicit approval after design acceptance.

## 12. Work record

- Documentation-only design and static review.
- No archive/object-store request, download, fixture access or materialization.
- No host/path preflight or filesystem/database access.
- No SQLite creation, migration or write.
- No source/test/workflow/dependency changes.
- No test or workflow run; no run/job/artifact evidence.
- No Feeder, T1/T2, VPS, PostgreSQL, deployment, exchange or trading operation.


---

## 13. Synthetic CSV fixture availability — 2026-11-21

Owner approved creation of synthetic offline CSV fixtures. The following files are now committed:

- `tests/fixtures/t0/binance_um_btcusdt_m15_synthetic.csv`
- `tests/fixtures/t0/binance_um_btcusdt_h1_synthetic.csv`
- `tests/fixtures/t0/README.md`

Each timeframe fixture contains two invented, consecutive rows, headerless, with 12 fields following the provisional mapping. The README records field order, constructed inclusive close-time values and strict limitations.

**What this enables:** offline parser/test development against deterministic examples for row width, field positions, decimal/integer parsing, timeframe alignment, OHLC envelope, non-negative volume, taker-buy bounds and inclusive-close arithmetic.

**What this does not establish:** actual Binance archive CSV header presence/absence, encoding, delimiter behavior, ZIP member name, source numeric grammar, empty/null behavior, or real-source timestamp conventions. No real archive CSV or representative source fixture was supplied or accessed.

Therefore:
- Synthetic fixture creation: **PASS**.
- Synthetic fixture content read-back: **PASS**.
- Real archive format compatibility: **NOT VERIFIED**.
- Parser contract freeze: **BLOCKED** pending independently approved real-source evidence or a revised owner decision accepting the residual compatibility risk.
- No parser/importer implementation, test suite, workflow, archive retrieval, SQLite or Canonical T0 operation is authorized by this fixture approval.
