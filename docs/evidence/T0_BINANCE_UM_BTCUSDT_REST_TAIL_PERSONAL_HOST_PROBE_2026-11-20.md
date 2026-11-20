# T0 Binance USD-M BTCUSDT REST tail probe — personal Windows host — 2026-11-20

## Work and scope
- Scope: record the owner-supplied output from the bounded, direct REST probe run on the owner's personal Windows machine.
- Endpoint used by the previously supplied script: `https://fapi.binance.com/fapi/v1/klines`.
- Symbol: BTCUSDT. Intervals: M15 then H1. Start: 2026-11-19 00:00:00 UTC. Retrieval cutoff: 2026-11-20 08:02:15.852 UTC.
- No API key, proxy, VPN, retry, alternate endpoint, SQLite, archive transfer, import, or runtime action was involved.
- This report records the PowerShell output pasted by the owner; the assistant did not execute the request on the personal machine.

## Environment
- Windows PowerShell prompt: `C:\Users\Administrator`.
- `python --version`: Python 3.14.10.
- `py -3 --version`: Python 3.14.10.
- Script invoked: `py -3 .\t0_rest_tail_probe.py`.
- The script was not committed to the repository and its local file hash was not supplied. Exact script SHA is therefore NOT VERIFIED.

## Results
### M15
- HTTP status: 200.
- Response Content-Length: 18,098 bytes.
- Binance request ID: `001f145a-806b-435e-888b-86f23bae3617`.
- CloudFront POP: `SGN50-P3`.
- Rows returned: 129.
- First open: 2026-11-19 00:00:00 UTC.
- Last open: 2026-11-20 08:00:00 UTC.
- Last row closeTime: 2026-11-20 08:14:59.999 UTC.
- JSON array parsing: PASS.

### H1
- HTTP status: 200.
- Response Content-Length: 4,736 bytes.
- Binance request ID: `47fded5c-5dba-463e-b5e0-13499218c98b`.
- CloudFront POP: `SGN50-P3`.
- Rows returned: 33.
- First open: 2026-11-19 00:00:00 UTC.
- Last open: 2026-11-20 08:00:00 UTC.
- Last row closeTime: 2026-11-20 08:59:59.999 UTC.
- JSON array parsing: PASS.

## Interpretation and verification limits
- **PASS — endpoint reachability** from the personal Windows host for both M15 and H1 at the recorded time.
- **PASS — HTTP 200 and JSON array parsing** for both responses.
- The last returned row in each interval was still forming at the retrieval cutoff. It MUST NOT be treated as a closed candle:
  - M15 last fully closed candle at cutoff: open 2026-11-20 07:45 UTC; close 07:59:59.999 UTC.
  - H1 last fully closed candle at cutoff: open 2026-11-20 07:00 UTC; close 07:59:59.999 UTC.
- The probe only printed row count and first/last timestamps. It did not verify every row's schema, OHLCV validity, interval alignment, monotonicity, duplicates, missing intervals, or closed-candle completeness. Those checks remain **NOT VERIFIED**.
- The output does not preserve the response payload itself. Re-running or using a separately approved bounded validator would be needed for full row-level evidence.
- The successful personal-host response does not establish the root cause of the earlier HTTP 451 from the separate Firecrawl environment. That 451's root cause remains **NOT VERIFIED**.
- No GitHub Actions workflow, run, job, or artifact was produced by this personal-machine probe.
- No source-code SHA or workflow SHA is applicable/available for this local execution; local probe script SHA is **NOT VERIFIED**.

## Status
- Personal-host REST connectivity M15/H1: **PASS**.
- HTTP response and JSON parse: **PASS**.
- Complete REST tail integrity/continuity and closed-candle validation: **NOT VERIFIED**.
- Reconstructed SQLite: **NOT CREATED**.
- Archive import, DB writes, promotion, T0 runtime activation, T1/T2 connection, and trading: **NOT AUTHORIZED / NOT PERFORMED**.

## Next step
Prepare a separately scoped, read-only validator that retains no database state and validates every returned row, excluding the still-open candle at the cutoff. Do not create or modify SQLite, download archives, or activate runtime without separate explicit approval.
