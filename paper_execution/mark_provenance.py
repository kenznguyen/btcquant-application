"""Deterministic provenance for the exact market candle consumed as an account mark."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, DecimalException
import hashlib
import json


def _nonempty(name: str, value: object, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(f"{name} is required")
    return value


def _canonical_price(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("MARK_PRICE_MUST_BE_EXACT_DECIMAL_TEXT")
    try:
        number = Decimal(value)
    except (DecimalException, TypeError, ValueError):
        raise ValueError("MARK_PRICE_INVALID") from None
    if not number.is_finite() or number <= 0:
        raise ValueError("MARK_PRICE_INVALID")
    rendered = format(number, "f")
    return rendered.rstrip("0").rstrip(".") if "." in rendered else rendered


def _json_safe(value: object) -> bool:
    if value is None or type(value) in (str, int, bool):
        return True
    if isinstance(value, list):
        return all(_json_safe(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(key, str) and _json_safe(item) for key, item in value.items())
    # Binary floats are deliberately excluded from financial source payloads.
    return False


@dataclass(frozen=True, slots=True)
class MarketMarkProvenance:
    source_id: str
    source_snapshot_id: str
    dataset_version: str
    source_as_of_ms: int
    mark_price: str
    candle_close_ms: int
    source_payload_sha256: str
    canonical_payload: str

    def __post_init__(self) -> None:
        _nonempty("source_id", self.source_id)
        _nonempty("source_snapshot_id", self.source_snapshot_id)
        _nonempty("dataset_version", self.dataset_version)
        if (self.source_snapshot_id != self.dataset_version
                or len(self.source_snapshot_id) != 71
                or not self.source_snapshot_id.startswith("sha256:")):
            raise ValueError("MARK_PROVENANCE_SNAPSHOT_ID_MISMATCH")
        if (not isinstance(self.source_payload_sha256, str)
                or len(self.source_payload_sha256) != 64
                or any(c not in "0123456789abcdef" for c in self.source_payload_sha256)):
            raise ValueError("MARK_PROVENANCE_HASH_INVALID")
        if (type(self.candle_close_ms) is not int or self.candle_close_ms < 0
                or type(self.source_as_of_ms) is not int
                or self.source_as_of_ms < self.candle_close_ms):
            raise ValueError("MARK_PROVENANCE_TIME_INVALID")
        if _canonical_price(self.mark_price) != self.mark_price:
            raise ValueError("MARK_PROVENANCE_PRICE_NOT_CANONICAL")
        if not isinstance(self.canonical_payload, str) or not self.canonical_payload:
            raise ValueError("MARK_PROVENANCE_PAYLOAD_REQUIRED")
        try:
            payload = json.loads(self.canonical_payload)
            if (not isinstance(payload, dict)
                    or set(payload) != {"sourceId", "datasetVersion", "sourceWindow", "consumedCandle"}
                    or json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
                    != self.canonical_payload):
                raise ValueError("MARK_PROVENANCE_PAYLOAD_NOT_CANONICAL")
            source_window = payload["sourceWindow"]
            expected_fields = {
                "exchange", "marketType", "symbol", "timeframe",
                "startMs", "endMs", "asOfMs", "candles",
            }
            if not isinstance(source_window, dict) or set(source_window) != expected_fields:
                raise ValueError("MARK_PROVENANCE_SOURCE_WINDOW_INVALID")
            if (payload["sourceId"] != self.source_id
                    or source_window["exchange"] != "binance"
                    or source_window["marketType"] != "USDT_PERPETUAL"
                    or source_window["symbol"] != "BTCUSDT"
                    or source_window["timeframe"] != "15m"):
                raise ValueError("MARK_PROVENANCE_SOURCE_IDENTITY_INVALID")
            start, end, as_of = (
                source_window["startMs"], source_window["endMs"], source_window["asOfMs"]
            )
            if (type(start) is not int or type(end) is not int or type(as_of) is not int
                    or start < 0 or end <= start or as_of < end
                    or start % 900_000 or end % 900_000
                    or end - start > 2_000 * 900_000):
                raise ValueError("MARK_PROVENANCE_SOURCE_WINDOW_BOUNDS_INVALID")
            candles = source_window["candles"]
            expected_count = (end - start) // 900_000
            if not isinstance(candles, list) or len(candles) != expected_count or not candles:
                raise ValueError("MARK_PROVENANCE_SOURCE_COVERAGE_INVALID")
            for index, candle in enumerate(candles):
                if not isinstance(candle, dict) or not _json_safe(candle):
                    raise ValueError("MARK_PROVENANCE_SOURCE_CANDLE_INVALID")
                open_at = start + index * 900_000
                if (type(candle.get("openTimeMs")) is not int
                        or candle["openTimeMs"] != open_at
                        or type(candle.get("closeTimeMs")) is not int
                        or candle["closeTimeMs"] != open_at + 900_000
                        or type(candle.get("availableAtMs")) is not int
                        or candle["availableAtMs"] < candle["closeTimeMs"]
                        or candle["availableAtMs"] > as_of):
                    raise ValueError("MARK_PROVENANCE_SOURCE_SEQUENCE_INVALID")
            dataset_digest = hashlib.sha256(
                json.dumps(
                    source_window, sort_keys=True, separators=(",", ":"), allow_nan=False
                ).encode("utf-8")
            ).hexdigest()
            if (payload["datasetVersion"] != self.dataset_version
                    or self.dataset_version != "sha256:" + dataset_digest):
                raise ValueError("MARK_PROVENANCE_DATASET_HASH_MISMATCH")
            consumed = candles[-1]
            if (payload["consumedCandle"] != consumed
                    or _canonical_price(consumed.get("close")) != self.mark_price
                    or consumed.get("closeTimeMs") != self.candle_close_ms
                    or self.source_as_of_ms != as_of):
                raise ValueError("MARK_PROVENANCE_CONSUMED_CANDLE_MISMATCH")
        except (TypeError, KeyError, json.JSONDecodeError):
            raise ValueError("MARK_PROVENANCE_PAYLOAD_INVALID") from None
        actual = hashlib.sha256(self.canonical_payload.encode("utf-8")).hexdigest()
        if actual != self.source_payload_sha256:
            raise ValueError("MARK_PROVENANCE_PAYLOAD_HASH_MISMATCH")



def build_market_mark_provenance(window: object, *, source_id: str) -> MarketMarkProvenance:
    """Hash the exact last candle selected by the account-mark calculation."""
    source = _nonempty("source_id", source_id)
    if not isinstance(window, dict):
        raise ValueError("MARK_SOURCE_WINDOW_INVALID")
    symbol, timeframe = window.get("symbol"), window.get("timeframe")
    exchange, market_type = window.get("exchange"), window.get("marketType")
    coverage = window.get("coverage")
    if exchange != "binance" or market_type != "USDT_PERPETUAL":
        raise ValueError("MARK_SOURCE_VENUE_UNSUPPORTED")
    if source != "T0_CANONICAL_MARKET_DATA":
        raise ValueError("MARK_SOURCE_ID_UNSUPPORTED")
    start, end, as_of = window.get("startMs"), window.get("endMs"), window.get("asOfMs")
    if (type(start) is not int or type(end) is not int or type(as_of) is not int
            or start < 0 or end <= start or as_of < 0
            or start % 900_000 or end % 900_000
            or end - start > 2_000 * 900_000):
        raise ValueError("MARK_SOURCE_WINDOW_BOUNDS_INVALID")
    if not isinstance(coverage, dict) or coverage != {
        "expected": (end-start)//900_000,
        "returned": len(window.get("candles", [])) if isinstance(window.get("candles"), list) else -1,
        "complete": True,
        "gaps": [],
    }:
        raise ValueError("MARK_SOURCE_COVERAGE_INCOMPLETE")
    dataset = _nonempty("dataset_version", window.get("datasetVersion"))
    if (len(dataset) != 71 or not dataset.startswith("sha256:")
            or any(c not in "0123456789abcdef" for c in dataset[7:])):
        raise ValueError("MARK_SOURCE_DATASET_VERSION_INVALID")
    if symbol != "BTCUSDT" or timeframe != "15m":
        raise ValueError("MARK_SOURCE_WINDOW_UNSUPPORTED")
    candles = window.get("candles")
    expected_count = (end-start)//900_000
    if (not isinstance(candles, list) or len(candles) != expected_count
            or not candles or not isinstance(candles[-1], dict)):
        raise ValueError("MARK_SOURCE_CANDLE_MISSING")
    for index, item in enumerate(candles):
        if not isinstance(item, dict) or not _json_safe(item):
            raise ValueError("MARK_SOURCE_CANDLE_NOT_CANONICAL_JSON")
        expected_open = start + index * 900_000
        if (type(item.get("openTimeMs")) is not int
                or item.get("openTimeMs") != expected_open
                or type(item.get("closeTimeMs")) is not int
                or item.get("closeTimeMs") != expected_open + 900_000
                or type(item.get("availableAtMs")) is not int
                or item.get("availableAtMs") < item.get("closeTimeMs")
                or (as_of is not None and item.get("availableAtMs") > as_of)):
            raise ValueError("MARK_SOURCE_CANDLE_SEQUENCE_INVALID")
    dataset_payload = {
        key: window[key] for key in (
            "exchange", "marketType", "symbol", "timeframe",
            "startMs", "endMs", "asOfMs", "candles",
        )
    }
    if not _json_safe(dataset_payload):
        raise ValueError("MARK_SOURCE_DATASET_PAYLOAD_INVALID")
    dataset_digest = hashlib.sha256(
        json.dumps(dataset_payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()
    if dataset != "sha256:" + dataset_digest:
        raise ValueError("MARK_SOURCE_DATASET_VERSION_MISMATCH")
    candle = candles[-1]
    if not _json_safe(candle):
        raise ValueError("MARK_SOURCE_CANDLE_NOT_CANONICAL_JSON")
    close_ms = candle.get("closeTimeMs")
    if type(close_ms) is not int or close_ms < 0:
        raise ValueError("MARK_SOURCE_CANDLE_TIME_INVALID")
    price = _canonical_price(candle.get("close"))
    payload = {
        "sourceId": source,
        "datasetVersion": dataset,
        "sourceWindow": dataset_payload,
        "consumedCandle": candle,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return MarketMarkProvenance(
        source_id=source,
        source_snapshot_id=dataset,
        dataset_version=dataset,
        source_as_of_ms=as_of,
        mark_price=price,
        candle_close_ms=close_ms,
        source_payload_sha256=digest,
        canonical_payload=canonical,
    )


def validate_consumed_mark(
    provenance: MarketMarkProvenance,
    *,
    mark_price: object,
    candle_close_ms: object,
    dataset_version: object,
    observed_at_ms: object,
) -> MarketMarkProvenance:
    if not isinstance(provenance, MarketMarkProvenance):
        raise ValueError("TYPED_MARK_PROVENANCE_REQUIRED")
    if (_canonical_price(mark_price) != provenance.mark_price
            or type(candle_close_ms) is not int
            or candle_close_ms != provenance.candle_close_ms
            or dataset_version != provenance.dataset_version
            or type(observed_at_ms) is not int
            or provenance.source_as_of_ms > observed_at_ms):
        raise ValueError("CONSUMED_MARK_PROVENANCE_MISMATCH")
    return provenance


__all__ = [
    "MarketMarkProvenance",
    "build_market_mark_provenance",
    "validate_consumed_mark",
]
