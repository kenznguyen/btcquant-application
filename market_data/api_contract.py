"""Shared read-only Candle API 1.1.0 parsing and freshness contract."""

from urllib.parse import parse_qs

from market_data.store import INTERVAL_MS


MAX_API_CANDLES = 2000
VOLUME_UNIT = "BTC_BASE_ASSET"
DATA_SOURCE = "ccxt.binanceusdm"


def _freshness(candles, timeframe, evaluation_time_ms, coverage_complete, evaluation_anchor):
    """Evaluate freshness only for a contiguous, closed, first-observed candle grid."""
    if not isinstance(timeframe, str) or timeframe not in INTERVAL_MS:
        raise ValueError("Unsupported timeframe")
    if type(evaluation_time_ms) is not int or evaluation_time_ms < 0:
        raise ValueError("Invalid evaluation timestamp")
    if not isinstance(candles, (list, tuple)):
        raise ValueError("Invalid candle collection")
    if evaluation_anchor not in {"AS_OF", "GENERATED_AT"}:
        raise ValueError("Invalid evaluation anchor")

    interval = INTERVAL_MS[timeframe]
    latest_expected = (evaluation_time_ms // interval) * interval - interval
    latest = candles[-1] if candles else None
    latest_is_mapping = isinstance(latest, dict)
    base = {
        "latestExpectedOpenTimeMs": latest_expected,
        "latestReturnedOpenTimeMs": latest.get("openTimeMs") if latest_is_mapping else None,
        "latestCloseTimeMs": latest.get("closeTimeMs") if latest_is_mapping else None,
        "latestAvailableAtMs": latest.get("availableAtMs") if latest_is_mapping else None,
        "evaluationTimeMs": evaluation_time_ms,
        "evaluationAnchor": evaluation_anchor,
        "observationAgeMs": None,
        "closeLagMs": None,
        "timestampValid": False,
        "fresh": False,
        "evaluable": False,
    }
    if not candles or not latest_is_mapping:
        return base

    timestamp_valid = True
    previous_open = None
    for candle in candles:
        if not isinstance(candle, dict):
            timestamp_valid = False
            break
        open_time = candle.get("openTimeMs")
        close_time = candle.get("closeTimeMs")
        available_at = candle.get("availableAtMs")
        valid = all(
            type(value) is int and value >= 0
            for value in (open_time, close_time, available_at)
        )
        if valid:
            valid = (
                open_time % interval == 0
                and close_time == open_time + interval
                and available_at >= close_time
                and available_at <= evaluation_time_ms
                and (
                    previous_open is None
                    or open_time == previous_open + interval
                )
            )
        if not valid:
            timestamp_valid = False
            break
        previous_open = open_time

    open_time = latest.get("openTimeMs")
    close_time = latest.get("closeTimeMs")
    available_at = latest.get("availableAtMs")
    if type(available_at) is int and available_at >= 0:
        base["observationAgeMs"] = evaluation_time_ms - available_at
    if type(close_time) is int and close_time >= 0:
        base["closeLagMs"] = evaluation_time_ms - close_time

    close_lag = base["closeLagMs"]
    fresh = bool(
        timestamp_valid
        and type(open_time) is int
        and open_time == latest_expected
        and type(close_lag) is int
        and 0 <= close_lag < interval
    )
    base["timestampValid"] = timestamp_valid
    base["fresh"] = fresh
    base["evaluable"] = bool(
        coverage_complete is True and timestamp_valid and fresh
    )
    return base

def candle_query(query):
    if len(query) > 2048:
        raise ValueError("Query too long")
    params = parse_qs(query, keep_blank_values=True, strict_parsing=True, max_num_fields=5)
    required = {"symbol", "timeframe", "startMs", "endMs"}
    if not required <= params.keys() or params.keys() - required - {"asOfMs"} or any(len(v) != 1 for v in params.values()):
        raise ValueError("Invalid parameters")
    values = {key: value[0] for key, value in params.items()}
    if values["symbol"] != "BTCUSDT" or values["timeframe"] not in INTERVAL_MS:
        raise ValueError("Unsupported market")

    def integer(key):
        value = values[key]
        if not value.isascii() or not value.isdigit() or len(value) > 19:
            raise ValueError("Invalid time")
        number = int(value)
        if not 0 <= number < 2**63 - 1:
            raise ValueError("Invalid time")
        return number

    start, end = integer("startMs"), integer("endMs")
    step = INTERVAL_MS[values["timeframe"]]
    if start % step or end % step or not 0 < end - start <= MAX_API_CANDLES * step:
        raise ValueError("Invalid or oversized window")
    return dict(symbol=values["symbol"], timeframe=values["timeframe"], start_ms=start,
                end_ms=end, as_of_ms=integer("asOfMs") if "asOfMs" in values else None)
