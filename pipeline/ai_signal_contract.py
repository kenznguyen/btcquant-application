"""Pure, fail-closed validation for the independent AI Strategy signal report."""
from decimal import Decimal, InvalidOperation
import re

_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_MAX_ID_LENGTH = 256
_MAX_REASON = 64
_ALLOWED_ACTIONS = {"LONG", "SHORT", "WAIT"}


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _nonempty_string(value):
    return isinstance(value, str) and 0 < len(value.strip()) <= _MAX_ID_LENGTH


def _positive_int(value):
    return _is_int(value) and value > 0


def _decimal(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        return None
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None
    if not parsed.is_finite():
        return None
    return parsed


def _wait(reason):
    return {
        "schemaVersion": 1,
        "source": "AI_STRATEGY",
        "action": "WAIT",
        "reason": reason[:_MAX_REASON],
        "signal": None,
    }


def _valid_policy(policy):
    if not isinstance(policy, dict):
        return None
    if not _nonempty_string(policy.get("policyVersion")):
        return None
    confidence_min = _decimal(policy.get("confidenceMin"))
    if confidence_min is None or confidence_min < 0 or confidence_min >= 1:
        return None
    for key in ("minCalibrationSamples", "minCalibrationPeriodMs",
                "maxCalibrationAgeMs", "forecastHorizonMs"):
        if not _positive_int(policy.get(key)):
            return None
    if not _nonempty_string(policy.get("labelDefinition")):
        return None
    return confidence_min


def _valid_market_report(report, now_ms):
    if not isinstance(report, dict):
        return False
    if not _is_int(report.get("schemaVersion")) or report.get("schemaVersion") != 1:
        return False
    if report.get("source") != "AI_STRATEGY":
        return False
    if report.get("exchange") != "binance" or report.get("marketType") != "USDT_PERPETUAL":
        return False
    if report.get("symbol") != "BTCUSDT" or report.get("timeframe") != "15m":
        return False
    for key in ("strategyVersion", "modelVersion", "datasetVersion", "inputSnapshotId"):
        if not _nonempty_string(report.get(key)):
            return False
    if not _positive_int(now_ms):
        return False
    decision = report.get("decisionAtMs")
    expiry = report.get("validUntilMs")
    if not _positive_int(decision) or not _positive_int(expiry):
        return False
    if not (decision <= now_ms <= expiry):
        return False
    if expiry <= decision or expiry - decision > 60_000:
        return False
    return True


def _valid_calibration(report, policy, now_ms, confidence_min):
    calibration = report.get("calibration")
    if not isinstance(calibration, dict):
        return None
    confidence = _decimal(calibration.get("calibratedConfidence"))
    if confidence is None or confidence < 0 or confidence > 1 or confidence < confidence_min:
        return None

    for key in ("calibrationVersion", "calibrationMethod", "calibrationDatasetVersion",
                "modelVersion", "strategyVersion", "trainingDatasetVersion"):
        if not _nonempty_string(calibration.get(key)):
            return None
    if not _SHA256_RE.fullmatch(calibration.get("calibrationArtifactHash", "")):
        return None
    if calibration.get("modelVersion") != report.get("modelVersion"):
        return None
    if calibration.get("strategyVersion") != report.get("strategyVersion"):
        return None
    if calibration.get("trainingDatasetVersion") != report.get("datasetVersion"):
        return None
    if calibration.get("labelDefinition") != policy.get("labelDefinition"):
        return None
    if calibration.get("forecastHorizonMs") != policy.get("forecastHorizonMs"):
        return None
    if not _positive_int(calibration.get("forecastHorizonMs")):
        return None

    sample_count = calibration.get("calibrationSampleCount")
    start = calibration.get("calibrationStartMs")
    end = calibration.get("calibrationEndMs")
    calibrated_at = calibration.get("calibratedAtMs")
    trained_through = calibration.get("trainedThroughMs")
    if not _positive_int(sample_count) or sample_count < policy["minCalibrationSamples"]:
        return None
    if not all(_positive_int(value) for value in (start, end, calibrated_at, trained_through)):
        return None
    if not (trained_through < start <= end <= calibrated_at <= report["decisionAtMs"]):
        return None
    if end - start < policy["minCalibrationPeriodMs"]:
        return None
    if now_ms - calibrated_at > policy["maxCalibrationAgeMs"]:
        return None

    evidence = calibration.get("evidence")
    if not isinstance(evidence, dict):
        return None
    if evidence.get("verificationStatus") != "SIGNATURE_VERIFIED":
        return None
    if evidence.get("registryStatus") != "ACTIVE":
        return None
    if evidence.get("trustedTimeStatus") != "VERIFIED":
        return None
    if evidence.get("oosEvidenceStatus") != "VERIFIED":
        return None
    manifest_digest = evidence.get("manifestDigest")
    if not isinstance(manifest_digest, str) or not _SHA256_RE.fullmatch(manifest_digest):
        return None
    return confidence, calibration, manifest_digest


def validate_ai_signal(report: dict, now_ms: int, policy: dict) -> dict:
    """Return a signal-only DTO; invalid input is converted to a stable WAIT result."""
    try:
        if not isinstance(report, dict):
            return _wait("AI_REPORT_INVALID")
        if not _is_int(report.get("schemaVersion")) or report.get("schemaVersion") != 1:
            return _wait("AI_REPORT_SCHEMA_INVALID")
        if report.get("source") != "AI_STRATEGY":
            return _wait("AI_REPORT_SOURCE_INVALID")
        action = report.get("action")
        if action not in _ALLOWED_ACTIONS:
            return _wait("AI_ACTION_INVALID")
        if action == "WAIT":
            return _wait("AI_WAIT_DIAGNOSTIC")
        if not _valid_market_report(report, now_ms):
            return _wait("AI_REPORT_INVALID_OR_STALE")
        confidence_min = _valid_policy(policy)
        if confidence_min is None:
            return _wait("AI_POLICY_INVALID")
        validated = _valid_calibration(report, policy, now_ms, confidence_min)
        if validated is None:
            return _wait("AI_CALIBRATION_UNAVAILABLE")
        confidence, calibration, manifest_digest = validated
        return {
            "schemaVersion": 1,
            "source": "AI_STRATEGY",
            "action": action,
            "reason": "AI_SIGNAL_VALIDATED",
            "signal": {
                "symbol": report["symbol"],
                "timeframe": report["timeframe"],
                "strategyVersion": report["strategyVersion"],
                "modelVersion": report["modelVersion"],
                "datasetVersion": report["datasetVersion"],
                "inputSnapshotId": report["inputSnapshotId"],
                "decisionAtMs": report["decisionAtMs"],
                "validUntilMs": report["validUntilMs"],
                "calibratedConfidence": format(confidence, "f"),
                "calibrationVersion": calibration["calibrationVersion"],
                "calibrationManifestDigest": manifest_digest,
            },
        }
    except Exception:
        # Untrusted report/policy objects must never leak input-derived exceptions.
        return _wait("AI_REPORT_INVALID")
