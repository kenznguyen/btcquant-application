# T0 Canonical Reconstruction Specification — Reuse SQLite-First Core

**Date:** 2026-11-21  
**Repository:** `kenznguyen/btcquant-application`  
**Status:** DESIGN DRAFT — OWNER-APPROVED DESIGN WORK ONLY  
**Execution:** NOT AUTHORIZED  
**Implementation:** NOT STARTED

## 1. Purpose and governing decision

This specification elaborates the owner-approved architecture in `docs/decisions/T0_CANONICAL_RECONSTRUCTION_REUSE_SQLITE_CORE_2026-11-21.md`:

**Reuse the reviewed T0 SQLite-first Core and design a new isolated reconstruction importer.**

The objective is to define a deterministic, auditable path for producing a new dataset labeled `RECONSTRUCTED — PARTIAL COVERAGE`. It is not recovery of the former Canonical database and does not itself confer Canonical designation.

This document is design-only. It authorizes no archive access/materialization, host or destination selection, preflight, importer implementation or execution, SQLite creation/write, runtime, deployment, or promotion.

## 2. Controlling source evidence and conflict resolution

Use the latest controlling handoff and owner decisions, not superseded execution-plan addenda.

- Historical archive inventory: 202 ZIP objects plus 202 paired checksum sidecars (404 identities).
- Historical ZIP validation evidence: 241,440 M15 rows and 60,360 H1 rows.
- Observed open-time bounds: M15 2019-12-31 00:00 UTC through 2026-11-18 23:45 UTC; H1 2019-12-31 00:00 UTC through 2026-11-18 23:00 UTC.
- Coverage label: **RECONSTRUCTED — PARTIAL COVERAGE**. These bounds do not prove earliest-ever history or data after the observed end.
- Archive inventory status is identity-complete but metadata-partial: individual sidecar byte sizes and sidecar SHA-256 values were not retained.
- Historical aggregate discrepancy: 11,277 bytes. Preserve the conflicting historical values; do not infer a correction.
- The old draft manifest contains REST-tail claims that are stale and must not be treated as approved source evidence. Current controlling status: REST-tail retrieval is closed by owner decision; no retry, bypass, or REST payload inclusion in this reconstruction baseline.
- The historical inventory does not prove that source objects remain currently accessible or immutable at a current source location.

If older planning text conflicts with these controlling facts, this specification follows the latest owner handoff/decision and records the conflict for reconciliation rather than silently combining evidence.

## 3. Reuse boundary: existing T0 components

The following existing components are reuse candidates, not automatically approved for every importer operation. Compatibility must be checked against the pinned source snapshot and this specification.

| Existing component | Intended responsibility | Constraint |
|---|---|---|
| `market_data/store.py` Candle / SQLite store primitives | Candle validation, decimal normalization, existing candle table/read contract | Existing `available_at_ms NOT NULL` and FIRST_OBSERVED semantics must be resolved before archive rows can be represented |
| `market_data/initialize_sqlite.py` | Explicit empty-only DB initializer | Must be invoked only after separate DB-creation approval; no current invocation |
| `market_data/api_contract.py` | Candle Contract 1.1.0 envelope/query/freshness | Reuse read contract; do not weaken freshness validation to accommodate incomplete historical metadata |
| `market_data/storage.py` | Backend selection / SQLite storage boundary | SQLite-only reconstruction; no PostgreSQL path |
| `market_data/write_gateway.py` | Fenced, transactional writes | Reuse only if importer writer semantics can satisfy lease/fencing invariants; otherwise define a separately reviewed offline-import boundary without bypassing safeguards |
| Existing T0 tests and workflows | Regression baseline and reusable test patterns | Historical runs remain tied to their exact SHAs; no claim of fresh full-suite verification |

Reviewed source snapshot for the expanded T0 review: `4d41294a7b82566666e50a79b87f62b668672077`. Relevant current source blobs were inspected from `main`; this is a reference baseline, not a new implementation approval.

### 3.1 Existing schema compatibility issue

The current candle table has the primary key:

`(exchange, market_type, symbol, timeframe, open_time_ms)`

and stores OHLCV and `available_at_ms`; the reviewed initializer sets `user_version=1` and creates `candles` plus `feeder_leases`.

The current Candle value object requires:
- aligned open time;
- `available_at_ms >= close_time_ms` (where the internal Candle close boundary is `open_time_ms + interval_ms`);
- exact decimal strings for OHLCV;
- valid OHLC bounds;
- closed candles only.

**Owner decision (2026-11-21): select option B — design an additive availability-kind distinction for the proposed Candle Contract 1.2.0.** This is a design decision only; it does not authorize implementation, schema migration, API rollout, or data import.

The proposed semantic variants are:
- `FIRST_OBSERVED`: `available_at_ms` is the actual timestamp when the ingestion system first observed the closed candle. This remains the live Feeder meaning and must not be fabricated for archive rows.
- `BAR_CLOSE_BOUNDARY`: for archive-derived candles only, `available_at_ms` is the deterministic exclusive close boundary `open_time_ms + interval_ms`. It means the bar became eligible/complete at its contract close boundary; it does **not** claim when any system first observed it.

The internal close boundary is exclusive. If the source CSV carries Binance's inclusive millisecond `close_time`, validate it against `open_time_ms + interval_ms - 1`; derive the contract boundary as `close_time + 1`. Do not conflate the two timestamp conventions.

Contract 1.2.0 design requirements:
- represent availability kind explicitly and validate the timestamp according to that kind;
- preserve `FIRST_OBSERVED` behavior for live Feeder data;
- permit `BAR_CLOSE_BOUNDARY` only for explicitly identified archive/reconstruction provenance;
- require consumers that depend on actual observation latency/first-seen semantics to filter for `FIRST_OBSERVED`; they must not silently treat `BAR_CLOSE_BOUNDARY` as first-observed evidence;
- preserve source-object and source-row provenance in a separate immutable reconstruction manifest/evidence set; the existing candle table does not retain that lineage;
- define additive/backward-compatible API/schema migration and consumer compatibility before implementation. Existing rows and clients must not be silently reinterpreted.

Do not silently rewrite the existing `Candle.as_dict()` behavior or database schema in this documentation increment. The current implementation emits `FIRST_OBSERVED` unconditionally, so it is not yet compatible with archive-derived `BAR_CLOSE_BOUNDARY` rows. A separately reviewed implementation and migration plan is required.

This decision resolves the semantic design blocker in favor of a proposed Contract 1.2.0 path; it does not establish that archive materialization, Importer implementation, SQLite creation, or import is authorized.

## 4. New isolated importer boundary

The importer is a future, separately approved component. It must be deterministic, offline with respect to exchanges/object stores, and accept only an explicit allowlist of already-approved local source files.

Proposed logical stages:

1. **Input inventory:** consume a pinned manifest; require exact object count, unique object keys, expected object kind, timeframe/partition and paired ZIP/sidecar relationship.
2. **Byte integrity:** calculate each ZIP and sidecar's own byte size and SHA-256 from the materialized bytes; parse each sidecar strictly; compare its asserted ZIP digest to the computed ZIP digest. Do not substitute the ZIP digest for the sidecar's own digest.
3. **Archive validation:** verify ZIP structure/CRC, exactly the expected CSV member(s), bounded decompression, expected header/column count and row structure. Reject path traversal, unexpected members, oversized expansion and malformed encodings.
4. **Normalization:** parse timestamps as UTC integer milliseconds and monetary/volume values as exact decimal text/Decimal; never use binary floating point.
5. **Contract validation:** validate Binance USD-M BTCUSDT identity, timeframe, timestamp grid, close boundary, OHLCV invariants and closed-candle eligibility.
6. **Identity reconciliation:** canonical identity is `(exchange, market_type, symbol, timeframe, open_time_ms)`. Sort deterministically by timeframe and open time.
7. **Provenance and reporting:** emit per-object results, source-to-row lineage, counts, bounds, duplicates, conflicts, gaps, rejected rows and aggregate hashes.
8. **Output gate:** produce a validated intermediate candidate only. Writing into SQLite is a separate later gate and requires a pinned importer SHA plus explicit execution approval.

The importer must not perform network requests, call Binance, access object storage, start a feeder, mutate source archives, clean up inputs, synthesize candles, interpolate, forward-fill, or silently drop malformed/conflicting rows.

## 5. Source-to-Candle mapping — owner-approved provisional mapping, fixture verification pending

**Owner decision (2026-11-21): approve the proposed semantic mapping below as the working design, but do not freeze the exact parser/header contract until an owner-approved representative archive CSV fixture has been inspected.** This is not approval to access the archive or materialize a fixture.

The expected Binance USD-M Kline 12-field order is:

| Ordinal | Expected source field | Destination / disposition | Required handling |
|---:|---|---|---|
| 1 | `open_time` | `open_time_ms` | Parse as UTC Unix milliseconds; validate timeframe alignment |
| 2 | `open` | Candle `open` | Exact decimal text; no binary float |
| 3 | `high` | Candle `high` | Exact decimal text; validate OHLC bounds |
| 4 | `low` | Candle `low` | Exact decimal text; validate OHLC bounds |
| 5 | `close` | Candle `close` | Exact decimal text; validate OHLC bounds |
| 6 | `volume` | Candle `volume` | Exact decimal text; no binary float |
| 7 | `close_time` | Validation / derived close boundary | Validate source inclusive close timestamp equals `open_time_ms + interval_ms - 1`; contract exclusive boundary is +1 ms |
| 8 | `quote_asset_volume` | Audit/provenance | Preserve source value; not mapped to current Candle schema |
| 9 | `number_of_trades` | Audit/provenance | Parse/validate as an integer; preserve source value |
| 10 | `taker_buy_base_asset_volume` | Audit/provenance | Preserve source value; not mapped to current Candle schema |
| 11 | `taker_buy_quote_asset_volume` | Audit/provenance | Preserve source value; not mapped to current Candle schema |
| 12 | `ignore` | Audit/provenance | Preserve raw source value; no Candle destination |

Market identity is supplied by verified manifest metadata, not guessed from CSV values: `exchange=BINANCE`, `market_type=USD-M`, `symbol=BTCUSDT`, and timeframe `15m` or `1h`. Each metadata value must be checked against the approved source inventory/partition identity.

Fixture verification must establish the exact header presence/absence, ordinal order, encoding, delimiter, row shape, timestamp units/conventions, empty/null behavior, numeric grammar and whether the twelfth field is present as expected. If the archive format differs, stop and return for a mapping decision; do not silently adapt.

The mapping record must retain exact header/name and ordinal, source parser/type, destination or explicit disposition, null/empty handling, validation rules, and audit/provenance retention. Numeric values must be parsed from source text using exact decimal/integer parsing, never binary floating point. No source field may be silently discarded.

### 5.1 `available_at_ms` — owner selected Contract 1.2.0 design path

The owner selected option B: distinguish actual first-observation time from archive bar-close eligibility using an explicit availability-kind discriminator.

- Live Feeder rows: `FIRST_OBSERVED`; timestamp is the actual first-observed time.
- Archive-derived rows: `BAR_CLOSE_BOUNDARY`; timestamp is the exclusive close boundary `open_time_ms + interval_ms`, derived only after validating the source close timestamp convention.
- `BAR_CLOSE_BOUNDARY` is not a historical first-observation claim and must not be used for first-seen latency analysis.
- Consumers requiring first-observation semantics must explicitly require `FIRST_OBSERVED`.
- Source-object/CSV-row lineage remains in a separate immutable reconstruction manifest/evidence set.

The existing implementation emits `FIRST_OBSERVED` unconditionally and the current schema/API do not yet encode this distinction. A Contract 1.2.0 additive schema/API design, migration/backward-compatibility plan, validation rules and consumer impact review are therefore required before implementation. No contract or database changes are made by this decision record.

## 6. Deterministic duplicate, conflict and gap policy

- **Identical duplicate:** same canonical identity and identical normalized contract values. Candidate policy: retain one candle row and record every contributing source object in lineage.
- **Conflicting duplicate:** same canonical identity but any normalized contract value differs. Quarantine the entire candidate dataset; no source precedence or last-write-wins.
- **Gap:** missing expected open time within the explicitly accepted observed coverage interval. Emit a machine-readable gap record; never synthesize a candle.
- **Out-of-range row:** row outside the declared source partition/coverage bounds, or with invalid timeframe alignment. Reject/quarantine with source location and reason.
- **Malformed source/object:** checksum, archive, CSV, encoding, row-shape or validation failure. Quarantine the entire run; do not produce a promotable candidate.
- **Partial coverage:** accepted output remains explicitly partial. No assertion of full history or post-cutoff completeness.

Exact duplicate handling, accepted gap thresholds and whether any gap is tolerable must be approved before implementation. The default safety posture is fail closed on unresolved conflicts and preserve all gap evidence.

## 7. Provenance and reproducibility artifacts

A future successful candidate must retain, outside the application Git repository and alongside the staged dataset:

- source inventory revision and exact 404 object identities;
- each ZIP and sidecar byte size and SHA-256 recomputed from materialized bytes;
- paired checksum assertion and verification result;
- archive member identity and source CSV row ordinal;
- normalized candle identity and source lineage;
- importer source commit SHA, dependency lock/hash and invocation parameters;
- Candle Contract/schema version and any separately approved mapping/policy version;
- per-timeframe counts, observed bounds, expected-grid counts and gap/duplicate/conflict reports;
- candidate dataset manifest, database file hash and validation logs;
- UTC timestamps, tool versions and PASS/FAIL/QUARANTINED outcomes.

The 11,277-byte historical aggregate discrepancy must be preserved in the evidence and separately explained by fresh per-object measurement; never rewrite the historical inventory to make totals appear consistent.

## 8. Acceptance test design (specification only)

No tests are created or executed by this document. Future isolated tests should cover at least:

### Input and archive safety
- exact allowlist and object count; missing, extra and duplicate object identities;
- ZIP/sidecar pairing, strict sidecar parser, per-object size/hash and asserted digest mismatch;
- corrupt ZIP/CRC, unexpected member, multiple CSVs, traversal names, decompression limits;
- malformed encoding, header mismatch, wrong column count, truncated row and extra row fields.

### Normalization and contract
- UTC millisecond parsing, timeframe alignment and close boundary;
- exact decimal parsing, precision/exponent bounds and rejection of float conversion;
- OHLC inequalities, zero/nonzero volume rules, non-finite values and negative values;
- unsupported market/symbol/timeframe and forming/unclosed candle rejection;
- explicit tests that `available_at_ms` cannot be guessed or backdated.

### Reconciliation
- identical duplicates with complete multi-source lineage;
- conflicting duplicates quarantine the whole candidate;
- missing timestamps produce exact gap intervals;
- deterministic ordering and stable output hash across repeated runs;
- no synthesis, interpolation, forward-fill or silent row loss;
- partial coverage labels and exact per-timeframe boundaries.

### Output and failure safety
- no output promotion on any failed gate;
- source archives and sidecars remain byte-for-byte unchanged;
- bounded memory/transaction behavior on large inputs;
- interrupted run is marked incomplete/quarantined and cannot be mistaken for PASS;
- SQLite output (only after separate approval) has exact schema/user_version, unique keys, integrity check and source-to-database equivalence;
- read-only T0 API can read an accepted test database without changing Candle Contract semantics.

Tests must use synthetic fixtures or explicitly approved staged copies; they must not access live source locations or create the actual reconstruction database.

## 9. Execution gates and non-actions

Before any execution proposal can be considered, all of the following must be separately resolved:

1. Owner-approved current host/environment and exact absolute staging path.
2. Confirmed immutable source location/access and explicit permission to materialize the exact allowlist.
3. Fresh per-object ZIP and sidecar size/hash evidence.
4. Exact CSV header/column mapping from a representative approved fixture.
5. Owner-approved `available_at_ms` semantics compatible with the Candle Contract.
6. Approved duplicate/conflict/gap and partial-coverage acceptance policy.
7. Importer design, dependency lock, source SHA and reproducible invocation.
8. Acceptance/validation plan, quarantine and immutable-retention controls.
9. Separate explicit owner approval naming the exact inputs, destination, importer SHA and permitted operations.

Until then:
- former Canonical SQLite: **LOST**;
- new reconstructed database: **NOT CREATED**;
- importer: **DESIGN ONLY / NOT IMPLEMENTED**;
- archive materialization: **NOT AUTHORIZED**;
- database creation/import/write: **NOT AUTHORIZED**;
- PostgreSQL/TimescaleDB: **PARKED**;
- Feeder/runtime/VPS/deployment/T1/T2/trading: **NOT AUTHORIZED**.

## 10. Work record

- Change type: documentation-only specification.
- Source implementation/tests/workflows/dependencies: unchanged.
- Tests/workflows: not run.
- Workflow run/job/artifact: none.
- No archive, object store, host, filesystem, database, VPS, runtime or exchange was accessed.
- Next: owner review of this specification, especially source-column mapping and `available_at_ms` semantics. Any implementation or data operation requires a separate explicit approval.


## 11. Owner decision update — 2026-11-21

- `available_at_ms`: **OPTION B SELECTED**. Design Contract 1.2.0 with explicit `FIRST_OBSERVED` and `BAR_CLOSE_BOUNDARY` semantics as specified in §§3.1 and 5.1. This is design approval only; implementation/schema/API migration remains unapproved.
- CSV 12 columns: **PROVISIONAL MAPPING APPROVED** as specified in §5; exact header/parser mapping remains **NOT FROZEN** until an owner-approved representative fixture is available and verified. This approval does not authorize archive access or fixture materialization.
- Importer implementation: **NOT STARTED**.
- Tests/workflows: **NOT RUN**.
- No archive/object-store/host/filesystem/database/VPS/runtime/exchange was accessed. No SQLite was created or written. No execution was performed.
