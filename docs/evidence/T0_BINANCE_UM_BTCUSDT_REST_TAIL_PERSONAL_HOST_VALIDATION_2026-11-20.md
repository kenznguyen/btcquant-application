# T0 Binance USD-M BTCUSDT REST Tail — Personal Host Retrieval and Offline Validation

**Date:** 2026-11-20  
**Repository:** `kenznguyen/btcquant-application`  
**Branch:** `main`  
**Validator source HEAD reported by the local operator:** `04a0a6275ff44da20f0a40e11ab541f9c112459f`  
**Validator implementation blob:** `3437e7a9181611cfed77eab59afee27136472963`  
**Regression test blob:** `293d9a605b6ec6498d551504fda04eecf298601f`

## 1. Approved scope

One bounded retrieval from the user's personal Windows host for Binance USD-M public REST klines, symbol BTCUSDT, intervals M15 and H1. Preserve exact response bodies locally, record response metadata and SHA-256, then run the existing offline read-only validator against the saved payloads.

No retries or alternate routes on refusal/error. No archive retrieval, SQLite access/write, T0 reconstruction, VPS/runtime, T1/T2, credentials, or trading.

## 2. Retrieval evidence

Endpoint: `https://fapi.binance.com/fapi/v1/klines`  
Query window: `startTime=1795046400000` through `endTime=1795161735852` (exclusive API end bound).  
Cutoff used by validator: `2026-11-20T08:02:15.852Z`.  
Retrieval occurred after the cutoff; the fixed cutoff was intentionally retained to validate the same historical window as the earlier probe.

| Field | M15 | H1 |
|---|---:|---:|
| HTTP status | 200 | 200 |
| Retrieval time (UTC) | 2026-11-20T08:16:35.864034Z | 2026-11-20T08:16:36.131662Z |
| Content-Length header | 18,102 | 4,740 |
| Bytes saved (reported by retrieval script) | 18,102 | 4,740 |
| Binance request ID | `36cab00e-0a9b-49e3-9c6c-d26840d10b1e` | `777005bd-6054-4386-9f98-50f00512317c` |
| CloudFront POP | `SGN50-P3` | `SGN50-P3` |
| SHA-256 (reported by retrieval script) | `b83d2a860af5fcb67dde7c51c004a2b307c91a4bd3a43c54216d83058c84b6e3` | `033bf0ae6b8b68cf6e2d488422e82031e2481cf1326bd0b254c76c1acedc2d6b` |
| Local payload | `%USERPROFILE%\btcquant-rest-tail-20261120\m15.json` | `%USERPROFILE%\btcquant-rest-tail-20261120\h1.json` |

The retrieval script also wrote `metadata.json` in the same local directory. The user supplied the script output; the files themselves were not uploaded to GitHub. Hashes are recorded as reported by the local script and have not been independently recomputed in this repository session.

## 3. Offline validator result

Command executed from the repository root:

```powershell
py -3 -m market_data.rest_tail_validator `
  --m15 "$env:USERPROFILE\btcquant-rest-tail-20261120\m15.json" `
  --h1 "$env:USERPROFILE\btcquant-rest-tail-20261120\h1.json" `
  --cutoff-ms 1795161735852
```

Actual validator output:

```json
{
  "15m": {
    "closed_rows": 128,
    "errors": [],
    "first_closed_open_ms": 1795046400000,
    "forming_rows_excluded": 1,
    "gaps": [],
    "last_closed_open_ms": 1795160700000,
    "ok": true,
    "raw_rows": 129
  },
  "1h": {
    "closed_rows": 32,
    "errors": [],
    "first_closed_open_ms": 1795046400000,
    "forming_rows_excluded": 1,
    "gaps": [],
    "last_closed_open_ms": 1795158000000,
    "ok": true,
    "raw_rows": 33
  }
}
```

### Result

- M15: **PASS** — 129 raw rows; 128 closed rows; 1 forming row excluded; no validator errors; no missing grid intervals.
- H1: **PASS** — 33 raw rows; 32 closed rows; 1 forming row excluded; no validator errors; no missing grid intervals.
- Both intervals report `ok: true`.
- First closed open time for both: 2026-11-19 00:00:00 UTC.
- Last closed M15 open: 2026-11-20 07:45:00 UTC.
- Last closed H1 open: 2026-11-20 07:00:00 UTC.
- The validator's implemented checks cover kline row shape, timestamps/alignment/close time, ordering, duplicate opens, missing grid intervals, finite numeric values, OHLC envelope, volume/trade constraints and forming-candle exclusion.

## 4. Regression suite and source identity

Before payload validation, the user ran:

```powershell
py -3 -m unittest market_data.test_rest_tail_validator -v
```

Result: **10/10 tests PASS** in 0.014 seconds.

Local Git evidence supplied by the user:
- Branch: `main`.
- `git rev-parse HEAD`: `04a0a6275ff44da20f0a40e11ab541f9c112459f`.
- `git status --short` initially showed only generated `market_data/__pycache__/`; the user subsequently removed it and reported clean output.
- CLI `--help` completed successfully.

No GitHub Actions workflow, run, job, or artifact was produced for this personal-host validation. The ad hoc retrieval script was outside the repository and has no repository SHA.

## 5. Scope and limitations

**Overall result: PASS — bounded personal-host REST retrieval and offline validation of the supplied M15/H1 payloads.**

This proves only the retrieved window and the validator's implemented checks. It does not establish earliest-ever history, full historical completeness, data beyond the cutoff, or future endpoint availability. It does not reconstruct or restore the former Canonical SQLite database and does not change T0 ownership or provenance.

No payload JSON or metadata file is committed. They remain local to the user's machine.

No SQLite database was opened or written. No archive was downloaded. No VPS, feeder, API service, T1/T2 provider, runtime, systemd/autostart, exchange credentials, or trading execution was accessed or changed.

## 6. Next step

Record this evidence and update the session handoff. Keep archive completeness and Canonical SQLite reconstruction as separate, currently uncompleted work requiring their own approved plan and gates.
