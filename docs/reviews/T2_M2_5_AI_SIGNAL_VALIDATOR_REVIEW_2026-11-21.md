# T2 M2.5 AI Signal Validator — Review Findings (2026-11-21)

Repository: `kenznguyen/btcquant-application`  
Reviewed implementation blob: `efb43ba777097e261c32671b9b37c24efad1a2e3`  
Reviewed GREEN tests blob: `71dcffa586ce785472f2c88e753e755cfe742bfc`  
Contract blob: `e5df7ec59c04a4f08b6ec0fc98e7e5702b3543dc`

## Review independence and scope

A separate adversarial review pass was performed after implementation and CI evidence inspection. This is **same-session review**, not a genuine independent second-person review. Independent reviewer sign-off remains **NOT VERIFIED**.

Review axes: contract correctness, input boundaries, fail-closed behavior, architecture, security/resource safety, determinism, and test coverage.

## Finding R1 — Required change: bound decimal rendering to prevent resource exhaustion

Location: `pipeline/ai_signal_contract.py`, accepted LONG/SHORT output field `calibratedConfidence` (the current implementation uses `format(confidence, "f")`).

The parser accepts finite Decimal values with arbitrarily large negative exponents. A report can supply a very small finite confidence such as `1e-1000000000`, while an explicit policy uses `confidenceMin = 0`. The value is within the contract's [0, 1] confidence domain and passes the current comparisons. Fixed-point formatting with `"f"` then attempts to materialize an output string containing roughly one billion fractional zeroes. This can exhaust memory or stall the caller even though the validator is intended to be fail-closed for untrusted reports.

Required remediation:
1. Add a regression test using a tiny exponent and zero threshold; assert validation remains bounded and output representation stays compact.
2. Change output serialization to a bounded canonical decimal representation (for example, general/scientific notation) or reject excessive exponent/precision before formatting. Keep confidence comparison exact and deterministic.
3. Run the original 10 M2.4 tests plus the updated GREEN suite in the pinned workflow at a new exact source SHA.

Severity: **HIGH — blocks M2.5 approval**.

## Other observations

- The validator is structurally isolated from Core and has no file, network, DB, model, or execution side effects.
- The public result shape is signal-only; no order intent, sizing, leverage, margin, reservation, ledger, or exchange instruction is emitted.
- The evidence envelope is only structurally checked, consistent with the contract's explicit exclusion of cryptographic verification and trust-root governance.
- The current tests cover LONG/SHORT independence, WAIT, policy bounds, market/time checks, provenance, calibration minimums/temporal order, evidence states, malformed values, immutability and determinism. They do not cover extreme Decimal exponents or bounded serialization.
- No full-repository regression was performed.

## Verdict

**REQUEST CHANGES — M2.5 NOT PASS.**

The focused GitHub Actions run and artifact are valid for the exact tested source SHA (details in the M2.5 evidence record), but R1 is a correctness/security resource-exhaustion blocker. Genuine independent second-person review also remains outstanding.

No source changes were made during this review. No Core, Shared Risk Engine, calibration registry, ledger, runner, runtime, database, T0/T1, VPS, deployment or trading behavior was touched.
