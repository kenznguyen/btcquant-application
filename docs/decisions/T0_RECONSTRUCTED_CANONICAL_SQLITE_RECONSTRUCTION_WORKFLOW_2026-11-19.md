# T0 Reconstructed Canonical SQLite — Reconstruction Workflow and Validation Contract

Date: 2026-11-19

## Status and authority

- Design status: PROPOSED — DOCUMENTATION ONLY.
- Owner-approved coverage: Binance USD-M BTCUSDT, M15 and H1; each timeframe independently starts at the earliest candle actually available from Binance and ends at the latest fully closed candle at the recorded UTC retrieval cutoff.
- Lineage: RECONSTRUCTED. This process cannot recover or claim identity with the deleted historical Canonical SQLite database.
- Current authorization: Phase 1 design/static only.
- No Binance/API access, download, raw-data staging, SQLite initialization/write, snapshot, Dropbox operation, restore, VPS/runtime, feeder/writer, or cutover is authorized. Each execution phase requires separate explicit approval.

## 1. Design principles

1. Preserve source responses before transformation wherever the approved source format permits; record immutable chunk identity and checksum.
2. Treat every exchange response as untrusted input. Validate response shape, symbol, contract family, interval, timestamps, numeric fields and ordering.
3. Make retrieval resumable and idempotent. Persist a checkpoint only after a chunk is fully validated and durably staged.
4. Calculate the expected UTC open-time grid independently for M15 and H1. Row counts alone do not prove continuity.
5. Never synthesize, interpolate, forward-fill or silently discard a missing candle.
6. Separate source acquisition, normalization, validation, SQLite construction, snapshot publication and restore verification into independently gated stages.
7. Quarantine failed or ambiguous stages; they must not produce an eligible Canonical dataset.
8. Keep T0 independent of the application Git repository. Git stores code, contracts and evidence, not the operational database or bulk candle payload.

## 2. Source selection gate

Before retrieval, compare using current official Binance documentation:
- Binance USD-M public REST klines endpoint family;
- Binance public historical archive availability for USD-M klines;
- earliest available records, maximum page/chunk size, request weight/rate limits, timestamp units, pagination behavior, archive publication cadence, checksums where available, and correction/deletion policy.

The selected primary historical source and any tail-completion source must be explicit and versioned. Do not silently mix REST and archive records. If multiple source families are needed, preserve provenance per chunk and define deterministic overlap reconciliation before retrieval approval. Prefer public/no-key access; do not introduce API credentials for public market data.

Source selection must establish:
- exact endpoint/archive path and proof of USD-M perpetual BTCUSDT, not Spot or COIN-M;
- independent earliest-candle discovery for M15 and H1;
- latest fully closed candle at a recorded UTC cutoff;
- pagination cursor semantics and safe request bounds;
- how empty responses are distinguished from retention boundaries, transient failures, rate limits and malformed responses.

Until this gate is reviewed and approved, no source is selected for execution.

## 3. Retrieval plan and resumable chunk contract

Create an immutable retrieval plan before fetching:
- dataset ID and retrieval-plan version;
- symbol BTCUSDT, market family BINANCE_USDM;
- timeframe and interval milliseconds: M15 = 900000; H1 = 3600000;
- selected source family, endpoint/archive path and documented API version;
- planned UTC bounds and boundary-discovery method;
- requested cutoff UTC and closed-candle rule;
- maximum records/bytes per chunk, bounded concurrency and retry policy;
- expected cursor semantics, overlap policy and rate-limit budget.

For each chunk:
1. Request a bounded UTC range or archive object.
2. Record request parameters, retrieval timestamp, safe response metadata, response byte size and source object identity.
3. Save raw bytes to a unique staging object and calculate SHA-256. Never overwrite a prior chunk.
4. Parse and validate every record; reject wrong symbol/interval/product family, malformed values, out-of-order or unaligned timestamps, duplicate conflicting records, impossible OHLC relationships, negative volume or non-finite values.
5. Verify the next cursor strictly advances. Detect repeated pages, empty pages before the known upper boundary, truncated pages and pagination loops.
6. Commit chunk manifest/checkpoint only after raw bytes and validation result are durable. A crash before checkpoint permits safe retry; it must not create duplicate accepted rows.
7. Reconcile intentional page overlap by exact candle identity and payload equality. Conflicting values for the same identity cause quarantine pending investigation.

Retries:
- Retry only documented transient failures (network interruption, 5xx, rate limit after server-directed delay).
- Use bounded exponential backoff with jitter and a maximum attempt/time budget.
- Do not retry authentication/permission failures, invalid parameters or schema violations as transient.
- Record every attempt and final outcome. Exhausted retries leave the chunk incomplete; never advance the checkpoint.

## 4. Normalized candle contract

Canonical identity: (venue, market, symbol, timeframe, open_time_ms).

Required normalized fields must match the approved Candle Contract and existing SQLite schema after a future compatibility review. Validation needs at minimum:
- venue/product identity proving Binance USD-M;
- symbol and timeframe;
- UTC-aligned open_time_ms;
- OHLC values;
- base/quote volume and trade count where provided by source/contract;
- source close time and closed-candle status;
- available_at_ms semantics distinct from candle open time;
- source chunk ID and lineage in the external provenance manifest (do not assume current candle table stores provenance).

Do not change the existing SQLite schema in this design phase. Before implementation, compare the exact Candle Contract version, SQLite columns, constraints, indexes and PRAGMA user_version. Any migration proposal requires separate review/approval.

## 5. Coverage and gap algorithm

For each timeframe independently:
- Establish first available open time from source evidence, not a guessed date.
- Establish last fully closed open time at the recorded retrieval cutoff.
- Generate the expected open-time sequence at the exact interval.
- Compare expected identities with accepted records.
- Emit every missing interval as a structured gap record: timeframe, first/last missing open time, missing count, UTC start/end, adjacent known candle identities, source requests/chunks examined, retry/exhaustion state and suspected classification.
- Classifications such as SOURCE_UNAVAILABLE, RETRIEVAL_INCOMPLETE, RATE_LIMIT_EXHAUSTED, MALFORMED_SOURCE, CONFLICTING_SOURCE and UNKNOWN are evidence labels, not automatic waivers.
- Record leading/trailing boundary uncertainty separately from internal gaps.
- A gap closes only with additional authentic source evidence or explicit owner disposition. Never fabricate rows.
- Keep all gaps visible in manifest and validation report, including gaps later dispositioned as accepted limitations.

Per timeframe report: first/last open time, UTC range, expected/observed/missing counts, duplicate/conflicting/out-of-order/invalid counts and coverage ratio. Coverage ratio alone is never a pass criterion.

## 6. Validation gates

### Gate A — source and retrieval integrity
- Source explicitly proves USD-M BTCUSDT and selected source/version is recorded.
- Every planned chunk has a terminal outcome; no unexplained missing chunk or cursor discontinuity.
- Raw chunk checksums and byte sizes verify.
- Retries, rate limits, empty responses and source boundaries are accounted for.

### Gate B — candle semantic integrity
- Exact schema/types; no NaN/Infinity; valid decimal precision/ranges.
- Timestamp alignment and expected interval grid.
- OHLC consistency: low <= open/close <= high and low <= high.
- Non-negative volume/trade count where applicable.
- Unique canonical identity; identical overlaps may be deduplicated with evidence; conflicting overlaps fail.
- Closed-candle rule enforced; no forming candle included.

### Gate C — temporal coverage
- First/last boundary evidence exists for each timeframe.
- Expected vs observed identities computed independently for M15 and H1.
- Every gap and boundary limitation enumerated.
- No unexplained cursor holes, page truncation or unprocessed chunks.
- Gap acceptance is an explicit owner decision after evidence review, not an implementation-invented numeric threshold.

### Gate D — SQLite staged database (future phase only)
- Construct only at an approved isolated staging path, never at live operational primary.
- Use existing approved initializer/schema only after compatibility review; refuse any existing path.
- Insert in deterministic order and bounded transactions; enforce uniqueness.
- Close all connections; run PRAGMA integrity_check; inspect user_version, tables, columns, indexes and constraints.
- Re-query counts, min/max open times, duplicates, semantic constraints and gap inventory from staged DB; compare with source-derived manifest.
- Any mismatch quarantines staged DB. No writer/feeder/lease activation.

### Gate E — snapshot and restore (future separately approved phases)
- Use SQLite Online Backup API to staging outside Dropbox sync.
- Close, validate and SHA-256 finalized snapshot.
- Upload create-only to a new version path; record Dropbox file ID/revision; read back exact revision and verify byte size and SHA-256.
- Restore only to a new empty isolated path; verify bytes before opening; validate read-only.
- Upload success is not restore verification. No primary cutover is implied.

## 7. Mandatory external manifest

The external manifest is mandatory and is the provenance authority. Suggested contract fields:
- manifest format identifier and semantic version;
- dataset ID and snapshot ID (snapshot ID only after snapshot stage);
- lineage exactly RECONSTRUCTED;
- market BINANCE_USDM and symbol BTCUSDT;
- source family, product/endpoint path, API/schema version, retrieval method and documented source limits;
- retrieval UTC start/end/cutoff/creation, software/source-adapter version, request/chunk counts, retry/rate-limit summary;
- M15 and H1 interval_ms, first/last open time, expected/observed/missing counts, coverage ratio, gap records and boundary treatment;
- immutable chunk IDs, source object/request identity, request range/cursor, retrieved_at, byte size, SHA-256, validation state and record count;
- validator version, Candle Contract version, semantic checks, and SQLite integrity/schema/user_version results when applicable;
- SQLite filename, byte size, SHA-256, schema version and user_version when a database exists;
- Dropbox path, file ID, revision, server size and modification metadata only after upload;
- restore destination identity, exact source revision, checksum and read-only validation evidence only after restore;
- explicit owner dispositions for each gap/limitation, timestamp and evidence reference.

Never store access tokens, API secrets, personal credentials or secret-bearing request headers. Reject missing required fields, malformed enums, digest mismatches and inconsistent counts.

## 8. State machine and fail-closed behavior

Recommended states:
PLANNED → RETRIEVING → RAW_STAGED → SOURCE_VALIDATED → CANDLES_VALIDATED → GAPS_REVIEW_PENDING → GAPS_DISPOSITIONED → SQLITE_STAGED → SQLITE_VALIDATED → SNAPSHOT_UPLOADED_NOT_RESTORE_VERIFIED → RESTORE_VERIFIED → OFFICIAL.

- OFFICIAL requires every mandatory gate, successful restore drill and explicit owner acceptance.
- Invalid chunk, source conflict, unexplained pagination discontinuity, missing manifest, checksum mismatch, schema mismatch or DB validation failure transitions to QUARANTINED.
- A gap cannot be dispositioned without explicit owner decision and evidence reference.
- No automatic OFFICIAL transition; no state implies runtime activation or permission to trade.

## 9. Separate execution approvals

- Phase 1 — design/static: currently authorized; documentation only.
- Phase 2 — source-selection review: approve source comparison and, if needed, bounded metadata-only probe. No bulk download.
- Phase 3 — reconstruction: approve exact source, retrieval window, limits, local staging destination, disk and network budgets before fetching market data.
- Phase 4 — validation and SQLite construction: approve isolated staging DB creation/write and exact schema contract.
- Phase 5 — Dropbox snapshot: approve Dropbox folder/account access, immutable upload and read-back verification.
- Phase 6 — restore drill: approve isolated restore destination and read-only validation.
- Phase 7 — Canonical acceptance: owner reviews evidence, gap dispositions, lineage and restore result. Operational primary/writer/runtime activation remains separately gated.

## 10. Open decisions before implementation

1. Select authoritative historical source family and any permitted tail source after checking current official Binance documentation.
2. Approve chunk size, request concurrency, retry/backoff budget and local disk/network budget based on source limits and machine resources.
3. Approve destination for raw immutable chunks and intermediate evidence, separate from Dropbox final snapshot repository.
4. Review exact Candle Contract and current SQLite schema compatibility; no schema changes are presumed.
5. Define evidence used to propose gap classifications; only owner can disposition gaps.
6. Define retention for raw source chunks and manifests without automatic deletion of canonical data.

## Final disposition

DESIGN DRAFT RECORDED — NOT IMPLEMENTED / NOT EXECUTED. The coverage target is approved, but source selection, resource budgets, schema compatibility, gap disposition and all execution approvals remain open. No market data has been fetched and no SQLite database has been created or modified by this design.
