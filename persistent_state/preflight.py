"""Pure, fixture-driven BTCUSDT M15/H1 session preflight validation."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re

from persistent_state.contracts import canonical_json


INTERVAL_MS = {"15m": 15 * 60_000, "1h": 60 * 60_000}


M15_MAX_LAG_MS = 20 * 60_000
H1_MAX_LAG_MS = 70 * 60_000
APPROVED_SOURCE = "ccxt.binanceusdm"
APPROVED_EXCHANGE = "binance"
APPROVED_MARKET_TYPE = "USDT_PERPETUAL"
APPROVED_SYMBOL = "BTCUSDT"
_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class MarketDataPreflightResult:
    status: str
    reasons: tuple[str, ...]
    as_of_ms: int | None
    snapshot_id: str | None
    dataset_versions_json: str | None
    candle_ranges_json: str | None


def _integer(value) -> bool:
    return type(value) is int and value >= 0


def _decimal(value, *, allow_zero=False) -> Decimal:
    if not isinstance(value, str) or not value or len(value) > 128:
        raise ValueError("decimal values must be bounded strings")
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("decimal value is invalid") from exc
    if not number.is_finite() or number < 0 or (not allow_zero and number == 0):
        raise ValueError("decimal value is outside the accepted range")
    if len(number.as_tuple().digits) > 40 or not -30 <= number.as_tuple().exponent <= 30:
        raise ValueError("decimal precision is outside the accepted range")
    return number


def _validate_snapshot(snapshot, timeframe, as_of_ms, required_count):
    reasons = []
    if not isinstance(snapshot, dict):
        return ["SNAPSHOT_INVALID"], None
    interval = INTERVAL_MS[timeframe]
    identity = {
        "exchange": APPROVED_EXCHANGE,
        "marketType": APPROVED_MARKET_TYPE,
        "symbol": APPROVED_SYMBOL,
        "timeframe": timeframe,
    }
    for key, expected in identity.items():
        if snapshot.get(key) != expected:
            reasons.append("MARKET_IDENTITY_INVALID")
            break
    if snapshot.get("source") != APPROVED_SOURCE:
        reasons.append("UNAPPROVED_DATA_SOURCE")
    version = snapshot.get("datasetVersion")
    if not isinstance(version, str) or not _SHA256.fullmatch(version):
        reasons.append("DATASET_VERSION_INVALID")
    if snapshot.get("asOfMs") != as_of_ms:
        reasons.append("SNAPSHOT_AS_OF_MISMATCH")

    coverage = snapshot.get("coverage")
    candles = snapshot.get("candles")
    if (
        isinstance(coverage, dict)
        and coverage.get("complete") is True
        and isinstance(candles, list)
        and len(candles) < required_count
    ):
        reasons.append("INSUFFICIENT_LOOKBACK")
    elif (
        not isinstance(coverage, dict)
        or coverage.get("complete") is not True
        or coverage.get("expected") != required_count
        or coverage.get("returned") != required_count
        or coverage.get("gaps") not in ([], None)
        or not isinstance(candles, list)
        or len(candles) != required_count
    ):
        reasons.append("INCOMPLETE_LOOKBACK")

    if not isinstance(candles, list) or len(candles) != required_count:
        return reasons, None

    start_ms, end_ms = snapshot.get("startMs"), snapshot.get("endMs")
    if (
        not _integer(start_ms) or not _integer(end_ms)
        or start_ms % interval or end_ms % interval
        or end_ms - start_ms != required_count * interval
    ):
        reasons.append("CANDLE_RANGE_INVALID")
        return reasons, None

    previous_close = None
    for candle in candles:
        if not isinstance(candle, dict):
            reasons.append("CANDLE_INVALID")
            break
        if any(candle.get(key) != value for key, value in identity.items()):
            reasons.append("CANDLE_IDENTITY_INVALID")
            break
        if candle.get("source") != APPROVED_SOURCE:
            reasons.append("UNAPPROVED_DATA_SOURCE")
            break
        open_ms, close_ms, available_ms = (
            candle.get("openTimeMs"), candle.get("closeTimeMs"), candle.get("availableAtMs")
        )
        if (
            not _integer(open_ms) or not _integer(close_ms) or not _integer(available_ms)
            or open_ms % interval or close_ms != open_ms + interval
            or available_ms < close_ms + 100 or available_ms > as_of_ms
            or candle.get("isClosed") is not True
            or candle.get("availabilityKind") != "FIRST_OBSERVED"
            or candle.get("quality") != "VALIDATED"
        ):
            reasons.append("CANDLE_NOT_CLOSED_OR_INVALID")
            break
        if previous_close is not None and open_ms != previous_close:
            reasons.append("CANDLE_SEQUENCE_INVALID")
            break
        try:
            opening = _decimal(candle.get("open"))
            high = _decimal(candle.get("high"))
            low = _decimal(candle.get("low"))
            close = _decimal(candle.get("close"))
            _decimal(candle.get("volume"), allow_zero=True)
            if low > high or not low <= opening <= high or not low <= close <= high:
                raise ValueError("OHLC bounds are inconsistent")
        except (TypeError, ValueError):
            reasons.append("CANDLE_OHLCV_INVALID")
            break
        previous_close = close_ms

    if candles:
        if candles[0].get("openTimeMs") != start_ms or candles[-1].get("closeTimeMs") != end_ms:
            reasons.append("CANDLE_RANGE_INVALID")
        latest_open = candles[-1].get("openTimeMs")
        if not _integer(latest_open):
            reasons.append("CANDLE_NOT_CLOSED_OR_INVALID")
        else:
            max_lag = M15_MAX_LAG_MS if timeframe == "15m" else H1_MAX_LAG_MS
            age_ms = as_of_ms - latest_open
            if age_ms < 0 or age_ms > max_lag:
                reasons.append("STALE_MARKET_DATA")

    return list(dict.fromkeys(reasons)), {
        "datasetVersion": version,
        "startMs": start_ms,
        "endMs": end_ms,
        "count": required_count,
    }


def validate_market_data_preflight(
    m15_snapshot,
    h1_snapshot,
    *,
    as_of_ms: int,
    required_lookback: dict[str, int],
) -> MarketDataPreflightResult:
    """Validate immutable M15/H1 fixtures against the approved closed-candle contract."""
    reasons = []
    if not _integer(as_of_ms):
        return MarketDataPreflightResult(
            "BLOCKED_PREFLIGHT", ("INVALID_PREFLIGHT_CLOCK",), None, None, None, None,
        )
    if (
        not isinstance(required_lookback, dict)
        or set(required_lookback) != {"15m", "1h"}
        or any(type(required_lookback.get(tf)) is not int or required_lookback[tf] < 1
               for tf in ("15m", "1h"))
    ):
        return MarketDataPreflightResult(
            "BLOCKED_PREFLIGHT", ("INVALID_LOOKBACK_POLICY",), as_of_ms, None, None, None,
        )

    m15_reasons, m15_range = _validate_snapshot(
        m15_snapshot, "15m", as_of_ms, required_lookback["15m"],
    )
    h1_reasons, h1_range = _validate_snapshot(
        h1_snapshot, "1h", as_of_ms, required_lookback["1h"],
    )
    reasons.extend(m15_reasons)
    reasons.extend(h1_reasons)

    if isinstance(m15_snapshot, dict) and isinstance(h1_snapshot, dict):
        for key in ("exchange", "marketType", "symbol", "source"):
            if m15_snapshot.get(key) != h1_snapshot.get(key):
                reasons.append("DATA_SOURCE_MISMATCH")
                break

    if reasons or m15_range is None or h1_range is None:
        return MarketDataPreflightResult(
            "BLOCKED_PREFLIGHT", tuple(dict.fromkeys(reasons or ["PREFLIGHT_INVALID"])),
            as_of_ms, None, None, None,
        )

    versions = {"15m": m15_range["datasetVersion"], "1h": h1_range["datasetVersion"]}
    ranges = {
        "15m": {"startMs": m15_range["startMs"], "endMs": m15_range["endMs"],
                "count": m15_range["count"]},
        "1h": {"startMs": h1_range["startMs"], "endMs": h1_range["endMs"],
               "count": h1_range["count"]},
    }
    snapshot_identity = {
        "source": APPROVED_SOURCE, "exchange": APPROVED_EXCHANGE,
        "marketType": APPROVED_MARKET_TYPE, "symbol": APPROVED_SYMBOL,
        "asOfMs": as_of_ms, "datasetVersions": versions, "candleRanges": ranges,
    }
    snapshot_id = "sha256:" + hashlib.sha256(
        canonical_json(snapshot_identity).encode("utf-8")
    ).hexdigest()
    return MarketDataPreflightResult(
        "READY", (), as_of_ms, snapshot_id,
        canonical_json(versions), canonical_json(ranges),
    )


__all__ = [
    "APPROVED_SOURCE", "H1_MAX_LAG_MS", "M15_MAX_LAG_MS",
    "MarketDataPreflightResult", "validate_market_data_preflight",
]
