"""Strict, bounded validation for untrusted T1 orderbook snapshot payloads."""

from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal, InvalidOperation
from typing import Any

from .contract import OrderbookSnapshot
from .errors import ContractError, ErrorCode
from .fixtures import canonical_snapshot_bytes

MAX_PAYLOAD_BYTES = 65_536
MAX_U64 = (1 << 64) - 1
FRESHNESS_MAX_AGE_MS = 2_000
MAX_FUTURE_SKEW_MS = 250
TOP_LEVEL_FIELDS = frozenset({
    "contractVersion", "symbol", "market", "bids", "asks",
    "snapshotLastUpdateId", "firstAppliedU", "lastAppliedU",
    "sourceTimestampMs", "observedAtMs", "decisionWatermark",
    "generation", "snapshotId", "continuity", "freshness", "depth", "complete",
})
DECIMAL_PATTERN = re.compile(r"(?:0|[1-9][0-9]*)(?:\\.[0-9]*[1-9])?\\Z", re.ASCII)
DIGEST_PATTERN = re.compile(r"sha256:[0-9a-f]{64}\\Z", re.ASCII)


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _fail(code: ErrorCode, message: str) -> None:
    raise ContractError(code, message)


def _uint(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= MAX_U64:
        _fail(ErrorCode.SCHEMA_MISMATCH, f"{field} must be an unsigned 64-bit JSON integer")
    return value


def _decimal(value: Any, field: str) -> Decimal:
    if not isinstance(value, str) or DECIMAL_PATTERN.fullmatch(value) is None:
        _fail(ErrorCode.INVALID_DECIMAL, f"{field} must be a canonical decimal string")
    try:
        number = Decimal(value)
    except InvalidOperation:
        _fail(ErrorCode.INVALID_DECIMAL, f"{field} is not a valid decimal")
    if not number.is_finite() or number <= 0:
        _fail(ErrorCode.INVALID_DECIMAL, f"{field} must be finite and greater than zero")
    return number


def _validate_levels(value: Any, side: str) -> tuple[tuple[str, str], ...]:
    if not isinstance(value, list) or len(value) < 20:
        _fail(ErrorCode.INVALID_BOOK, f"{side} must contain at least 20 levels")
    levels: list[tuple[str, str]] = []
    previous: Decimal | None = None
    for index, item in enumerate(value):
        if not isinstance(item, list) or len(item) != 2:
            _fail(ErrorCode.INVALID_BOOK, f"{side}[{index}] must be a two-element array")
        price = _decimal(item[0], f"{side}[{index}].price")
        _decimal(item[1], f"{side}[{index}].quantity")
        if previous is not None:
            ordered = price < previous if side == "bids" else price > previous
            if not ordered:
                _fail(ErrorCode.INVALID_BOOK, f"{side} prices must be strictly ordered without duplicates")
        previous = price
        levels.append((item[0], item[1]))
    return tuple(levels)


def validate_payload(payload: bytes, *, now_ms: int) -> OrderbookSnapshot:
    """Validate the complete payload and return an immutable DTO or raise ContractError.

    The caller supplies one captured evaluation timestamp. This function performs no I/O,
    clock reads, network access, retries, caching, or strategy/execution side effects.
    """
    if isinstance(now_ms, bool) or not isinstance(now_ms, int) or not 0 <= now_ms <= MAX_U64:
        raise ValueError("now_ms must be an unsigned 64-bit integer captured by the caller")
    if not isinstance(payload, bytes):
        _fail(ErrorCode.MALFORMED_JSON, "payload must be bytes")
    if len(payload) > MAX_PAYLOAD_BYTES:
        _fail(ErrorCode.PAYLOAD_TOO_LARGE, "payload exceeds 65536 bytes")
    try:
        decoded = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        _fail(ErrorCode.MALFORMED_JSON, f"invalid JSON payload: {exc}")
    if not isinstance(decoded, dict):
        _fail(ErrorCode.SCHEMA_MISMATCH, "payload root must be an object")
    if set(decoded) != TOP_LEVEL_FIELDS:
        missing = sorted(TOP_LEVEL_FIELDS - set(decoded))
        extra = sorted(set(decoded) - TOP_LEVEL_FIELDS)
        _fail(ErrorCode.SCHEMA_MISMATCH, f"top-level keys mismatch; missing={missing}, extra={extra}")

    if decoded["contractVersion"] != "T1_T2_ORDERBOOK_V1":
        _fail(ErrorCode.UNSUPPORTED_VERSION, "unsupported contractVersion")
    if decoded["symbol"] != "BTCUSDT" or decoded["market"] != "BINANCE_USDM_PERPETUAL":
        _fail(ErrorCode.SCHEMA_MISMATCH, "symbol or market does not match T1 BTCUSDT USD-M contract")

    integer_fields = (
        "snapshotLastUpdateId", "firstAppliedU", "lastAppliedU",
        "sourceTimestampMs", "observedAtMs", "decisionWatermark", "generation",
    )
    integers = {field: _uint(decoded[field], field) for field in integer_fields}
    if integers["generation"] == 0:
        _fail(ErrorCode.INVALID_SEQUENCE, "generation must be greater than zero")
    if integers["lastAppliedU"] < integers["firstAppliedU"]:
        _fail(ErrorCode.INVALID_SEQUENCE, "lastAppliedU must not be below firstAppliedU")
    if integers["decisionWatermark"] != integers["lastAppliedU"]:
        _fail(ErrorCode.INVALID_SEQUENCE, "decisionWatermark must equal lastAppliedU")

    source_age = now_ms - integers["sourceTimestampMs"]
    observed_age = now_ms - integers["observedAtMs"]
    if source_age < -MAX_FUTURE_SKEW_MS or observed_age < -MAX_FUTURE_SKEW_MS:
        _fail(ErrorCode.FUTURE_TIMESTAMP, "source or observed timestamp is too far in the future")
    if source_age > FRESHNESS_MAX_AGE_MS or observed_age > FRESHNESS_MAX_AGE_MS:
        _fail(ErrorCode.STALE_SNAPSHOT, "source or observed timestamp is older than 2000ms")

    if decoded["continuity"] != "VERIFIED":
        _fail(ErrorCode.INVALID_SEQUENCE, "continuity must be VERIFIED")
    if decoded["freshness"] != "FRESH":
        _fail(ErrorCode.STALE_SNAPSHOT, "freshness label must be FRESH")
    if decoded["complete"] is not True:
        _fail(ErrorCode.INVALID_BOOK, "complete must be boolean true")

    bids = _validate_levels(decoded["bids"], "bids")
    asks = _validate_levels(decoded["asks"], "asks")
    if Decimal(bids[0][0]) >= Decimal(asks[0][0]):
        _fail(ErrorCode.INVALID_BOOK, "best bid must be strictly below best ask")

    depth = decoded["depth"]
    if not isinstance(depth, dict) or set(depth) != {"bids", "asks"}:
        _fail(ErrorCode.SCHEMA_MISMATCH, "depth must contain exactly bids and asks")
    depth_bids = _uint(depth["bids"], "depth.bids")
    depth_asks = _uint(depth["asks"], "depth.asks")
    if depth_bids != len(bids) or depth_asks != len(asks):
        _fail(ErrorCode.INVALID_BOOK, "depth counts must equal level array lengths")

    snapshot_id = decoded["snapshotId"]
    if not isinstance(snapshot_id, str) or DIGEST_PATTERN.fullmatch(snapshot_id) is None:
        _fail(ErrorCode.DIGEST_MISMATCH, "snapshotId must use sha256:<64 lowercase hex>")
    unsigned = dict(decoded)
    unsigned.pop("snapshotId")
    expected_digest = "sha256:" + hashlib.sha256(canonical_snapshot_bytes(unsigned)).hexdigest()
    if not hashlib.compare_digest(snapshot_id, expected_digest):
        _fail(ErrorCode.DIGEST_MISMATCH, "snapshot digest does not match canonical payload")

    return OrderbookSnapshot(
        contract_version=decoded["contractVersion"],
        symbol=decoded["symbol"],
        market=decoded["market"],
        bids=bids,
        asks=asks,
        snapshot_last_update_id=integers["snapshotLastUpdateId"],
        first_applied_u=integers["firstAppliedU"],
        last_applied_u=integers["lastAppliedU"],
        source_timestamp_ms=integers["sourceTimestampMs"],
        observed_at_ms=integers["observedAtMs"],
        decision_watermark=integers["decisionWatermark"],
        generation=integers["generation"],
        snapshot_id=snapshot_id,
        continuity=decoded["continuity"],
        freshness=decoded["freshness"],
        depth_bids=depth_bids,
        depth_asks=depth_asks,
        complete=True,
    )
