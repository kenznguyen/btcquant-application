"""Offline, read-only validator for Binance USD-M kline JSON arrays.

This module never performs network access and never opens or writes a database.
"""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

INTERVALS = {
    "15m": 15 * 60 * 1000,
    "1h": 60 * 60 * 1000,
}
EXPECTED_START_MS = 1795046400000  # 2026-11-19T00:00:00Z
DEFAULT_CUTOFF_MS = 1795161735852  # 2026-11-20T08:02:15.852Z
EXPECTED_RAW_ROWS = {"15m": 129, "1h": 33}
EXPECTED_CLOSED_ROWS = {"15m": 128, "1h": 32}


def _is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _parse_decimal(
    value: Any, field: str, row_number: int, errors: list[str]
) -> Decimal | None:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        errors.append(f"row {row_number}: {field} is not a decimal")
        return None
    if not number.is_finite():
        errors.append(f"row {row_number}: {field} must be finite")
        return None
    return number


def validate_klines(
    rows: Any,
    *,
    interval_ms: int,
    cutoff_ms: int,
    expected_raw_rows: int,
    expected_closed_rows: int,
    expected_start_ms: int = EXPECTED_START_MS,
) -> dict[str, Any]:
    """Validate Binance's 12-field kline rows and exclude candles not closed by cutoff."""
    errors: list[str] = []
    gaps: list[int] = []

    if interval_ms <= 0 or cutoff_ms <= 0 or expected_raw_rows < 0 or expected_closed_rows < 0:
        return {
            "ok": False,
            "errors": ["interval, cutoff, and expected row counts must be positive/non-negative"],
            "gaps": [],
        }
    if not isinstance(rows, list):
        return {"ok": False, "errors": ["payload must be a JSON array"], "gaps": []}

    if len(rows) != expected_raw_rows:
        errors.append(f"raw row count {len(rows)} != expected {expected_raw_rows}")

    parsed: list[tuple[int, int, int]] = []
    seen: set[int] = set()
    previous_open: int | None = None

    for index, row in enumerate(rows, start=1):
        if not isinstance(row, list) or len(row) != 12:
            errors.append(f"row {index}: expected Binance kline array with 12 fields")
            continue

        open_ms, close_ms = row[0], row[6]
        if not _is_integer(open_ms):
            errors.append(f"row {index}: openTime must be an integer millisecond timestamp")
            continue
        if not _is_integer(close_ms):
            errors.append(f"row {index}: closeTime must be an integer millisecond timestamp")
            continue

        if open_ms in seen:
            errors.append(f"row {index}: duplicate openTime {open_ms}")
        seen.add(open_ms)
        if previous_open is not None and open_ms <= previous_open:
            errors.append(f"row {index}: openTime is not strictly increasing")
        previous_open = open_ms

        if open_ms % interval_ms != 0:
            errors.append(f"row {index}: openTime is not aligned to interval grid")
        if close_ms != open_ms + interval_ms - 1:
            errors.append(f"row {index}: closeTime does not match interval boundary")
        if open_ms < expected_start_ms:
            errors.append(f"row {index}: openTime precedes expected start")
        if open_ms >= cutoff_ms:
            errors.append(f"row {index}: openTime is at or beyond retrieval cutoff")

        names = (
            "open", "high", "low", "close", "volume", "quoteVolume",
            "takerBuyBaseVolume", "takerBuyQuoteVolume",
        )
        positions = (1, 2, 3, 4, 5, 7, 9, 10)
        values: dict[str, Decimal] = {}
        for name, position in zip(names, positions):
            value = _parse_decimal(row[position], name, index, errors)
            if value is None:
                continue
            values[name] = value
            if name in {"open", "high", "low", "close"} and value <= 0:
                errors.append(f"row {index}: {name} price must be > 0")
            elif name not in {"open", "high", "low", "close"} and value < 0:
                errors.append(f"row {index}: {name} must be >= 0")

        if all(key in values for key in ("open", "high", "low", "close")):
            open_price, high, low, close_price = (
                values[key] for key in ("open", "high", "low", "close")
            )
            if high < max(open_price, close_price, low) or low > min(
                open_price, close_price, high
            ):
                errors.append(f"row {index}: OHLC envelope is invalid")

        trades = row[8]
        if not _is_integer(trades) or trades < 0:
            errors.append(f"row {index}: trades must be a non-negative integer")

        if "volume" in values and "takerBuyBaseVolume" in values:
            if values["takerBuyBaseVolume"] > values["volume"]:
                errors.append(f"row {index}: taker buy base volume exceeds total volume")
        if "quoteVolume" in values and "takerBuyQuoteVolume" in values:
            if values["takerBuyQuoteVolume"] > values["quoteVolume"]:
                errors.append(f"row {index}: taker buy quote volume exceeds total quote volume")

        parsed.append((index, open_ms, close_ms))

    # Binance closeTime is inclusive; a candle is closed only when closeTime < cutoff.
    closed = [(number, open_ms, close_ms) for number, open_ms, close_ms in parsed
              if close_ms < cutoff_ms]
    forming = [(number, open_ms, close_ms) for number, open_ms, close_ms in parsed
               if close_ms >= cutoff_ms]

    if len(closed) != expected_closed_rows:
        errors.append(f"closed row count {len(closed)} != expected {expected_closed_rows}")

    expected_last_closed = ((cutoff_ms - interval_ms) // interval_ms) * interval_ms
    closed_times = [open_ms for _, open_ms, _ in closed]
    closed_set = set(closed_times)
    for expected_time in range(
        expected_start_ms, expected_last_closed + 1, interval_ms
    ):
        if expected_time not in closed_set:
            gaps.append(expected_time)
    if gaps:
        errors.append(f"gap detected: {len(gaps)} missing interval(s)")

    if closed_times:
        if closed_times[0] != expected_start_ms:
            errors.append("first closed candle does not match expected start")
        if closed_times[-1] != expected_last_closed:
            errors.append("last closed candle does not match expected cutoff boundary")

    return {
        "ok": not errors,
        "raw_rows": len(rows),
        "closed_rows": len(closed),
        "forming_rows_excluded": len(forming),
        "first_closed_open_ms": closed_times[0] if closed_times else None,
        "last_closed_open_ms": closed_times[-1] if closed_times else None,
        "gaps": gaps,
        "errors": errors,
    }


def _load_json(path: str) -> Any:
    # Read-only input: this function never creates or modifies files.
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m15", required=True, help="Path to saved M15 response JSON")
    parser.add_argument("--h1", required=True, help="Path to saved H1 response JSON")
    parser.add_argument("--cutoff-ms", type=int, default=DEFAULT_CUTOFF_MS)
    args = parser.parse_args(argv)

    reports: dict[str, Any] = {}
    for interval, path in (("15m", args.m15), ("1h", args.h1)):
        try:
            payload = _load_json(path)
            reports[interval] = validate_klines(
                payload,
                interval_ms=INTERVALS[interval],
                cutoff_ms=args.cutoff_ms,
                expected_raw_rows=EXPECTED_RAW_ROWS[interval],
                expected_closed_rows=EXPECTED_CLOSED_ROWS[interval],
            )
        except (OSError, json.JSONDecodeError) as exc:
            reports[interval] = {
                "ok": False,
                "errors": [f"cannot read JSON input: {exc}"],
            }

    print(json.dumps(reports, indent=2, sort_keys=True))
    return 0 if all(report.get("ok") for report in reports.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
