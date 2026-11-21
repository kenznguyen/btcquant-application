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
    mark_price: str
    candle_close_ms: int
    source_payload_sha256: str
    canonical_payload: str

    def __post_init__(self) -> None:
        _nonempty("source_id", self.source_id)
        _nonempty("source_snapshot_id", self.source_snapshot_id)
        _nonempty("dataset_version", self.dataset_version)
        if self.source_snapshot_id != "sha256:" + self.source_payload_sha256:
            raise ValueError("MARK_PROVENANCE_SNAPSHOT_HASH_MISMATCH")
        if (not isinstance(self.source_payload_sha256, str)
                or len(self.source_payload_sha256) != 64
                or any(c not in "0123456789abcdef" for c in self.source_payload_sha256)):
            raise ValueError("MARK_PROVENANCE_HASH_INVALID")
        if type(self.candle_close_ms) is not int or self.candle_close_ms < 0:
            raise ValueError("MARK_PROVENANCE_TIME_INVALID")
        if _canonical_price(self.mark_price) != self.mark_price:
            raise ValueError("MARK_PROVENANCE_PRICE_NOT_CANONICAL")
        if not isinstance(self.canonical_payload, str) or not self.canonical_payload:
            raise ValueError("MARK_PROVENANCE_PAYLOAD_REQUIRED")
        actual = hashlib.sha256(self.canonical_payload.encode("utf-8")).hexdigest()
        if actual != self.source_payload_sha256:
            raise ValueError("MARK_PROVENANCE_PAYLOAD_HASH_MISMATCH")


def build_market_mark_provenance(window: object, *, source_id: str) -> MarketMarkProvenance:
    """Hash the exact last candle selected by the account-mark calculation."""
    source = _nonempty("source_id", source_id)
    if not isinstance(window, dict):
        raise ValueError("MARK_SOURCE_WINDOW_INVALID")
    symbol, timeframe = window.get("symbol"), window.get("timeframe")
    dataset = _nonempty("dataset_version", window.get("datasetVersion"))
    if symbol != "BTCUSDT" or timeframe != "15m":
        raise ValueError("MARK_SOURCE_WINDOW_UNSUPPORTED")
    candles = window.get("candles")
    if not isinstance(candles, list) or not candles or not isinstance(candles[-1], dict):
        raise ValueError("MARK_SOURCE_CANDLE_MISSING")
    candle = candles[-1]
    if not _json_safe(candle):
        raise ValueError("MARK_SOURCE_CANDLE_NOT_CANONICAL_JSON")
    close_ms = candle.get("closeTimeMs")
    if type(close_ms) is not int or close_ms < 0:
        raise ValueError("MARK_SOURCE_CANDLE_TIME_INVALID")
    price = _canonical_price(candle.get("close"))
    payload = {
        "sourceId": source,
        "symbol": symbol,
        "timeframe": timeframe,
        "datasetVersion": dataset,
        "consumedCandle": candle,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return MarketMarkProvenance(
        source_id=source,
        source_snapshot_id="sha256:" + digest,
        dataset_version=dataset,
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
) -> MarketMarkProvenance:
    if not isinstance(provenance, MarketMarkProvenance):
        raise ValueError("TYPED_MARK_PROVENANCE_REQUIRED")
    if (_canonical_price(mark_price) != provenance.mark_price
            or type(candle_close_ms) is not int
            or candle_close_ms != provenance.candle_close_ms
            or dataset_version != provenance.dataset_version):
        raise ValueError("CONSUMED_MARK_PROVENANCE_MISMATCH")
    return provenance


__all__ = [
    "MarketMarkProvenance",
    "build_market_mark_provenance",
    "validate_consumed_mark",
]
