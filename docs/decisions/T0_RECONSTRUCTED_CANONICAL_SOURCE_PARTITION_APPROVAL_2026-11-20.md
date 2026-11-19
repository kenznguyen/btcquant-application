# T0 Reconstructed Canonical — Source Partition Approval

Date: 2026-11-20

## Owner decision

The owner approved the proposed source partition after reviewing the read-only Binance Public Data object-listing evidence.

**Decision: APPROVED — SOURCE PARTITION ONLY.**

For Binance USD-M BTCUSDT klines, independently for M15 and H1:

1. Use monthly archive objects as the default bulk source for full months **2020-01 through 2026-10**.
2. Use daily archive objects for the boundary date **2019-12-31** and the current partial-month range **2026-11-01 through 2026-11-18**.
3. Retain daily objects as a targeted fallback/diagnostic source if later payload validation identifies missing or conflicting candles in monthly objects.
4. Whenever both daily and monthly payloads are retrieved for an overlapping date, compare complete normalized candle payloads. Exact duplicates may be deduplicated while retaining both source references. Any conflicting candle payload must be quarantined; never silently prefer one source.
5. REST `GET /fapi/v1/klines` may be considered separately for the tail after the latest eligible archive candle through a separately approved UTC retrieval cutoff. No REST request is authorized by this decision.

## Evidence basis

Read-only archive metadata evidence:
- `docs/evidence/T0_BINANCE_UM_BTCUSDT_ARCHIVE_METADATA_INSPECTION_2026-11-20.md`
- Monthly listings: 82 ZIP + 82 matching `.CHECKSUM` keys per timeframe; continuous month filenames 2020-01–2026-10.
- Daily listings: 2,515 ZIP + 2,515 matching `.CHECKSUM` keys per timeframe; continuous date filenames 2019-12-31–2026-11-18.
- Daily/monthly filename coverage overlaps 2020-01–2026-10.

This evidence proves object-key coverage only. It does not prove checksum validity, candle-level completeness, actual first/last candle timestamps, row counts, intra-file gap absence, or candle closed state.

## Authorization boundary

This decision authorizes **documentation of the source partition only**. It does not authorize:
- downloading any ZIP or `.CHECKSUM` object body;
- calling Binance REST Klines or any other market-data endpoint;
- creating raw staging files/directories or retrieving market data;
- initializing, creating, modifying or writing SQLite;
- Dropbox upload, snapshot, restore or cutover;
- VPS/runtime, writer, feeder, lease or deployment activity.

A separate explicit approval is required for a bounded archive payload retrieval/validation task. That approval must specify exact object scope, raw staging destination, byte/request/time budgets, checksum handling, retry/resume behavior and cleanup/retention. Any REST probe or tail retrieval requires its own explicit scope and approval.

## Preserved acceptance rules

- Dataset remains Binance USD-M BTCUSDT M15/H1; no Spot, COIN-M, mark/index/continuous-contract substitution.
- Lineage is `RECONSTRUCTED`, never recovery of the deleted historical database.
- Preserve immutable per-object provenance, retrieval timestamp, object key, LastModified, byte size, sidecar identity and locally verified SHA-256.
- Validate candle timestamps against expected timeframe grids; enumerate all gaps, duplicates and conflicts.
- No synthetic candles, interpolation, forward-fill or silent omission.
- Gap disposition and OFFICIAL acceptance remain separate owner gates.

## Status

- Owner source partition decision: **APPROVED**.
- Archive object listing: **PASS — metadata only**.
- ZIP/checksum payload validity: **NOT VERIFIED**.
- Candle-level completeness and earliest/latest candle boundaries: **NOT VERIFIED**.
- REST tail: **NOT INSPECTED / NOT AUTHORIZED**.
- Reconstruction, SQLite, Dropbox, restore, VPS/runtime, writer/feeder and cutover: **NOT AUTHORIZED**.
- Tests/workflows: **NOT RUN**; no run, job or artifact exists for this documentation-only decision.

Next step: request separate bounded approval for archive ZIP/checksum payload retrieval and validation, without implying REST, SQLite, Dropbox or runtime authorization.
