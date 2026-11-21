"""Strict offline parser for the provisional 12-column Binance USD-M Kline CSV mapping.

This module performs no file, database, network, archive or exchange I/O.
Synthetic-fixture compatibility is not evidence of real archive compatibility.
"""
from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

INTERVALS_MS = {
    "15m": 15 * 60 * 1000,
    "1h": 60 * 60 * 1000,
}
MAX_INTEGER = (1 << 63) - 1
MAX_NUMERIC_TOKEN_LENGTH = 128
_INTEGER_RE = re.compile(r"(?:0|[1-9][0-9]*)\Z")
_DECIMAL_RE = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?\Z")


class ArchiveCsvError(ValueError):
    """Raised when a CSV document violates the provisional archive row contract."""


@dataclass(frozen=True, slots=True)
class ArchiveKlineRow:
    """One validated row; Decimal fields retain the exact source decimal value."""

    open_time_ms: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    source_close_time_ms: int
    quote_asset_volume: Decimal
    number_of_trades: int
    taker_buy_base_asset_volume: Decimal
    taker_buy_quote_asset_volume: Decimal
    ignore: str
    bar_close_boundary_ms: int
    raw_fields: tuple[str, ...]


def _parse_integer(value: str, field: str, row_number: int) -> int:
    if len(value) > MAX_NUMERIC_TOKEN_LENGTH or not _INTEGER_RE.fullmatch(value):
        raise ArchiveCsvError(f"row {row_number}: {field} must be a non-negative integer")
    parsed = int(value)
    if parsed > MAX_INTEGER:
        raise ArchiveCsvError(f"row {row_number}: {field} exceeds signed 64-bit range")
    return parsed


def _parse_decimal(value: str, field: str, row_number: int) -> Decimal:
    if len(value) > MAX_NUMERIC_TOKEN_LENGTH or not _DECIMAL_RE.fullmatch(value):
        raise ArchiveCsvError(f"row {row_number}: {field} is not a finite plain decimal")
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ArchiveCsvError(f"row {row_number}: {field} is not a valid decimal") from exc
    if not parsed.is_finite():
        raise ArchiveCsvError(f"row {row_number}: {field} must be finite")
    return parsed


def parse_archive_csv(text: str, *, timeframe: str) -> tuple[ArchiveKlineRow, ...]:
    """Parse headerless 12-column CSV using an explicitly selected timeframe.

    The parser validates source close_time as Binance-style inclusive milliseconds,
    then exposes the exclusive bar-close boundary as source_close_time_ms + 1.
    It intentionally does not infer CSV format variants or silently skip rows.
    """
    if not isinstance(text, str):
        raise ArchiveCsvError("CSV input must be text")
    try:
        interval_ms = INTERVALS_MS[timeframe]
    except (KeyError, TypeError) as exc:
        raise ArchiveCsvError(f"unsupported timeframe: {timeframe!r}") from exc

    reader = csv.reader(io.StringIO(text, newline=""), strict=True)
    parsed_rows: list[ArchiveKlineRow] = []
    previous_open_time: int | None = None

    try:
        for row in reader:
            row_number = reader.line_num
            if len(row) != 12:
                raise ArchiveCsvError(
                    f"row {row_number}: expected exactly 12 fields, got {len(row)}"
                )

            open_time_ms = _parse_integer(row[0], "open_time", row_number)
            source_close_time_ms = _parse_integer(row[6], "close_time", row_number)
            if open_time_ms % interval_ms:
                raise ArchiveCsvError(f"row {row_number}: open_time is not timeframe-aligned")
            if source_close_time_ms != open_time_ms + interval_ms - 1:
                raise ArchiveCsvError(
                    f"row {row_number}: close_time does not match inclusive timeframe boundary"
                )
            if previous_open_time is not None and open_time_ms <= previous_open_time:
                raise ArchiveCsvError(
                    f"row {row_number}: open_time values must be strictly increasing"
                )
            previous_open_time = open_time_ms

            open_price = _parse_decimal(row[1], "open", row_number)
            high = _parse_decimal(row[2], "high", row_number)
            low = _parse_decimal(row[3], "low", row_number)
            close_price = _parse_decimal(row[4], "close", row_number)
            volume = _parse_decimal(row[5], "volume", row_number)
            quote_volume = _parse_decimal(row[7], "quote_asset_volume", row_number)
            trades = _parse_integer(row[8], "number_of_trades", row_number)
            taker_base = _parse_decimal(row[9], "taker_buy_base_asset_volume", row_number)
            taker_quote = _parse_decimal(row[10], "taker_buy_quote_asset_volume", row_number)

            if min(open_price, high, low, close_price) <= 0:
                raise ArchiveCsvError(f"row {row_number}: OHLC prices must be > 0")
            if high < max(open_price, close_price, low) or low > min(
                open_price, close_price, high
            ):
                raise ArchiveCsvError(f"row {row_number}: OHLC envelope is invalid")
            if min(volume, quote_volume, taker_base, taker_quote) < 0:
                raise ArchiveCsvError(f"row {row_number}: volume fields must be >= 0")
            if taker_base > volume:
                raise ArchiveCsvError(
                    f"row {row_number}: taker_buy_base_asset_volume exceeds volume"
                )
            if taker_quote > quote_volume:
                raise ArchiveCsvError(
                    f"row {row_number}: taker_buy_quote_asset_volume exceeds quote_asset_volume"
                )

            parsed_rows.append(
                ArchiveKlineRow(
                    open_time_ms=open_time_ms,
                    open=open_price,
                    high=high,
                    low=low,
                    close=close_price,
                    volume=volume,
                    source_close_time_ms=source_close_time_ms,
                    quote_asset_volume=quote_volume,
                    number_of_trades=trades,
                    taker_buy_base_asset_volume=taker_base,
                    taker_buy_quote_asset_volume=taker_quote,
                    ignore=row[11],
                    bar_close_boundary_ms=source_close_time_ms + 1,
                    raw_fields=tuple(row),
                )
            )
    except csv.Error as exc:
        raise ArchiveCsvError(f"invalid CSV syntax near row {reader.line_num}: {exc}") from exc

    if not parsed_rows:
        raise ArchiveCsvError("CSV must contain at least one data row")
    return tuple(parsed_rows)
