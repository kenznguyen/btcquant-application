# T0 Reconstructed Canonical Market-Data Coverage Decision — 2026-11-19

## Owner decision

Approved target coverage for a future, separately authorized reconstruction:

- Market: Binance USD-M BTCUSDT.
- Timeframes: M15 and H1.
- Start: the earliest candle open time actually available from Binance for each timeframe, determined and recorded during the future retrieval; do not assume the two timeframes have identical start boundaries.
- End: the latest fully closed candle available at the recorded retrieval cutoff for each timeframe. Record the UTC retrieval cutoff and exact first/last candle open times.
- Scope: all exchange history available under the selected Binance USD-M historical-data interface at retrieval time, subject to documented endpoint limits and retention/availability constraints.
- Lineage: RECONSTRUCTED. This is not recovery of the deleted historical Canonical SQLite database.

## Gap and boundary handling

- Record every missing expected candle interval independently for M15 and H1, including UTC start/end, duration, count, and retrieval evidence.
- Do not synthesize, interpolate, forward-fill, or silently omit missing candles.
- Record partial boundary treatment and any exchange/API limitation that prevents retrieval.
- A gap is not silently considered acceptable: every gap must be explicitly reported and dispositioned under the later validation/owner-acceptance gate. The approved history target does not itself waive gap review or authorize OFFICIAL / VERIFIED status.
- Preserve raw retrieval provenance, request windows, pagination/cursor continuity, retrieval timestamps, retries/rate-limit outcomes, source endpoint family, and dataset checksums in the mandatory external manifest.

## Authorization boundary

This decision resolves the target historical coverage definition only. It authorizes documentation updates in Phase 1. It does not authorize Binance access/download, data reconstruction, SQLite initialization or writes, canonical acceptance, Dropbox operations, snapshot, restore drill, VPS/runtime, feeder/writer, or cutover. Each remains subject to separate explicit approval.

## Status

- Coverage target: OWNER APPROVED.
- Gap reporting: REQUIRED; automatic gap repair/fill: NOT AUTHORIZED.
- Gap acceptability and final official acceptance: PENDING validation evidence and owner disposition.
- Reconstruction and data access: NOT AUTHORIZED.
