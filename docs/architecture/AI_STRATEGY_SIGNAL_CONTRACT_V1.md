# AI Strategy Signal Contract V1

Status: **M2.4 OWNER-APPROVED CONTRACT — RED SPECIFICATION ONLY**
Date: 2026-11-21
Target: `kenznguyen/btcquant-application`, branch `main`

## 1. Purpose and separation

AI Strategy is an independent signal producer. It may publish LONG or SHORT while Strategy Core independently reports WAIT. AI signal evaluation MUST NOT require, read, infer, or mutate Core signal state, Core position, Core DCA state, Core PnL, or the Core ledger.

This increment defines only the AI signal-report boundary and its fail-closed validation contract. It does not implement a model, prediction engine, calibration registry, order intent, ledger writer, risk admission caller, or execution path.

Strategy Core (RSI + ADX + Smart DCA) is unchanged. Existing Core sizing/leverage semantics are outside this increment and remain governed by their separate unresolved review. No Core file is copied or modified.

## 2. Public interface to be implemented in a later GREEN increment

Target module: `pipeline/ai_signal_contract.py`

Expected pure function:

```python
validate_ai_signal(report: dict, now_ms: int, policy: dict) -> dict
```

The function is deterministic and side-effect free. It does not read environment variables, files, databases, network services, model artifacts, exchange state, or Core state.

The input is one AI-owned report plus an explicit versioned policy snapshot. A caller MUST NOT pass Core state as a prerequisite.

## 3. Input report

Required fields:

| Field | Contract |
|---|---|
| `schemaVersion` | Integer exactly `1`; booleans are invalid |
| `source` | Exactly `AI_STRATEGY` |
| `action` | `LONG`, `SHORT`, or `WAIT` |
| `exchange` | `binance` |
| `marketType` | `USDT_PERPETUAL` |
| `symbol` | `BTCUSDT` |
| `timeframe` | `15m` |
| `strategyVersion`, `modelVersion` | Non-empty bounded version identifiers |
| `datasetVersion`, `inputSnapshotId` | Non-empty provenance identifiers |
| `decisionAtMs`, `validUntilMs` | Positive integer UTC epoch milliseconds |
| `calibration` | Calibrated-confidence and provenance object for LONG/SHORT |

The calibration object must contain calibrated confidence, calibration version/method/artifact hash, calibration dataset version, sample count, calibration start/end/verified-at timestamps, label definition, forecast horizon, and matching model/strategy/training-dataset versions. It must also carry a calibration-evidence envelope with verified signature state, active registry state, trusted-time state, OOS evidence state, and manifest digest.

A `WAIT` report is diagnostic only. It does not create a signal candidate and does not require calibration to be trade-eligible.

## 4. Explicit policy input

The policy must be supplied on every call. No production defaults are permitted.

Required fields:
- `policyVersion`
- `confidenceMin` in [0, 1); a value of 1 is invalid because the leverage mapping denominator would be zero
- `minCalibrationSamples` as a positive integer
- `minCalibrationPeriodMs` as a positive integer
- `maxCalibrationAgeMs` as a positive integer
- `labelDefinition`
- `forecastHorizonMs`

The numerical `confidenceMin` remains unset for production. Test fixtures may use `0.6`; this is not an owner-selected production threshold.

## 5. Validation and fail-closed rules

For LONG/SHORT:
1. Validate schema, source, action, market identity, versions, provenance and timestamp types.
2. Require `decisionAtMs <= now_ms <= validUntilMs`; reject expired or future-dated reports. Signal validity window must be positive and no longer than 60 seconds.
3. Require calibrated confidence to be a finite decimal in [0, 1], not bool, NaN, Infinity, or malformed text.
4. Require an explicit policy and `confidence >= confidenceMin`; missing/invalid policy or below-threshold confidence yields WAIT.
5. Require calibration artifact/dataset provenance and model, strategy, training-dataset, label and forecast-horizon consistency.
6. Require calibration observations to be after the model training cutoff and available before the prediction; reject temporal leakage.
7. Require sample count and calibration duration to meet the explicit policy minimums, and calibration age not to exceed the policy maximum.
8. Require calibration evidence states to be verified/active/OOS-valid and a well-formed manifest digest. This module validates the evidence envelope; cryptographic verification and trust-root governance belong to a separately reviewed Calibration Registry.
9. Any missing, stale, mismatched, unverified or invalid evidence returns WAIT with no signal candidate.

Unknown actions, wrong market, malformed provenance, or invalid timestamps return WAIT. Validation must not raise input-derived exceptions to callers.

## 6. Output

Accepted LONG/SHORT:

```json
{
  "schemaVersion": 1,
  "source": "AI_STRATEGY",
  "action": "LONG",
  "reason": "AI_SIGNAL_VALIDATED",
  "signal": {
    "symbol": "BTCUSDT",
    "timeframe": "15m",
    "strategyVersion": "ai-strategy-v1",
    "modelVersion": "model-v1",
    "datasetVersion": "dataset-id",
    "inputSnapshotId": "snapshot-id",
    "decisionAtMs": 1800000000000,
    "validUntilMs": 1800000030000,
    "calibratedConfidence": "0.8",
    "calibrationVersion": "cal-v1",
    "calibrationManifestDigest": "sha256:<64-hex>"
  }
}
```

The action is LONG or SHORT according to the validated AI report. Output contains a signal only; it MUST NOT contain an order, execution intent, quantity, leverage, margin budget, reservation, ledger mutation, or exchange instruction.

Rejected/diagnostic output:

```json
{
  "schemaVersion": 1,
  "source": "AI_STRATEGY",
  "action": "WAIT",
  "reason": "AI_CALIBRATION_UNAVAILABLE",
  "signal": null
}
```

Reasons are stable, bounded machine-readable codes and must not include secrets, raw report values, filesystem paths, or exception text.

## 7. Shared Risk Engine boundary

A validated AI signal is not an admitted trade and is not an order intent. Any later conversion into an ENTRY or exposure-increasing DCA must be a separate, explicitly approved integration step and must pass the common account-scoped Shared Risk Engine and Kill Switch. Core and AI ledgers remain separate. A Risk Engine denial is final.

This M2.4 contract does not invoke Shared Risk Engine, create reservations, write either ledger, or authorize AI paper orders.

## 8. TDD acceptance tests for M2.4

RED tests are written against the public interface before any implementation:
- AI LONG validates without a Core signal input.
- AI SHORT validates without a Core signal input.
- Core WAIT or missing Core report does not suppress a valid AI signal.
- WAIT remains diagnostic and produces no signal.
- Missing/invalid calibration or policy fails closed.
- Below-threshold, non-finite, bool, malformed confidence fails closed.
- Missing/mismatched provenance, wrong market, invalid time window, expiry and future timestamps fail closed.
- Calibration leakage, stale evidence, insufficient samples/period, inactive registry, unverified signature/time/OOS state fail closed.
- Output never contains order/execution/sizing/ledger fields.
- Validation is deterministic and side-effect free.

## 9. Approval boundary

M2.4 authorizes this contract and test-only RED work. It does not authorize GREEN implementation, AI model training, calibration artifact signing/registry activation, numerical production confidence threshold selection, AI paper admission, ledger writes, Shared Risk Engine caller wiring, database migration, runtime/VPS changes, deployment, exchange connectivity, or live trading. Each requires separate approval and exact-SHA evidence.
