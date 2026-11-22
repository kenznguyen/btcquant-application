"""Pure in-memory normalization and coverage for validated archive kline rows.

This module intentionally performs no filesystem, archive, network, database,
clock, environment or exchange I/O. It does not assign FIRST_OBSERVED.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Iterable

from market_data.archive_csv_parser import ArchiveKlineRow, INTERVALS_MS


class ImportBatchError(ValueError):
    """Raised when importer-core inputs violate the explicit batch contract."""


class RowDisposition(str, Enum):
    ACCEPTED = "accepted"
    IDENTICAL_DUPLICATE = "identical_duplicate"
    REJECTED = "rejected"
    CONFLICTING = "conflicting"


@dataclass(frozen=True, slots=True)
class SourceRowReference:
    """Opaque caller-supplied source reference and one-based row ordinal."""

    source_ref: str
    row_ordinal: int


@dataclass(frozen=True, slots=True)
class ImportCandidate:
    """Immutable normalized candidate retaining the parser's exact source data."""

    identity: tuple[str, str, str, str, int]
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
    source_refs: tuple[SourceRowReference, ...]


@dataclass(frozen=True, slots=True)
class ImportRowResult:
    """One and only one disposition for a source row."""

    source_ref: str
    row_ordinal: int
    identity: tuple[str, str, str, str, int]
    disposition: RowDisposition


@dataclass(frozen=True, slots=True)
class RowAccounting:
    source_row_count: int
    accepted_count: int
    identical_duplicate_count: int
    rejected_count: int
    conflicting_count: int


@dataclass(frozen=True, slots=True)
class ImportBatchResult:
    candidates: tuple[ImportCandidate, ...]
    row_results: tuple[ImportRowResult, ...]
    accounting: RowAccounting
    quarantined: bool


@dataclass(frozen=True, slots=True)
class CoverageReport:
    timeframe: str
    start_open_time_ms: int
    end_open_time_ms: int
    expected_open_times: tuple[int, ...]
    observed_open_times: tuple[int, ...]
    missing_open_times: tuple[int, ...]
    out_of_range_open_times: tuple[int, ...]

    @property
    def expected_count(self) -> int:
        return len(self.expected_open_times)

    @property
    def observed_count(self) -> int:
        return len(self.observed_open_times)


def _required_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ImportBatchError(f"{field} must be a non-empty string")
    return value


def _interval(timeframe: object) -> int:
    if not isinstance(timeframe, str) or timeframe not in INTERVALS_MS:
        raise ImportBatchError(f"unsupported timeframe: {timeframe!r}")
    return INTERVALS_MS[timeframe]


def _timestamp(value: object, field: str, interval_ms: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ImportBatchError(f"{field} must be a non-negative integer")
    if value % interval_ms:
        raise ImportBatchError(f"{field} must be timeframe-aligned")
    return value


def _normalized_payload(row: ArchiveKlineRow) -> tuple[object, ...]:
    """Return semantic payload fields; Decimal equality ignores lexical scale."""
    return (
        row.open,
        row.high,
        row.low,
        row.close,
        row.volume,
        row.source_close_time_ms,
        row.quote_asset_volume,
        row.number_of_trades,
        row.taker_buy_base_asset_volume,
        row.taker_buy_quote_asset_volume,
        row.ignore,
        row.bar_close_boundary_ms,
    )


def _candidate(
    row: ArchiveKlineRow,
    identity: tuple[str, str, str, str, int],
    refs: tuple[SourceRowReference, ...],
) -> ImportCandidate:
    return ImportCandidate(
        identity=identity,
        open_time_ms=row.open_time_ms,
        open=row.open,
        high=row.high,
        low=row.low,
        close=row.close,
        volume=row.volume,
        source_close_time_ms=row.source_close_time_ms,
        quote_asset_volume=row.quote_asset_volume,
        number_of_trades=row.number_of_trades,
        taker_buy_base_asset_volume=row.taker_buy_base_asset_volume,
        taker_buy_quote_asset_volume=row.taker_buy_quote_asset_volume,
        ignore=row.ignore,
        bar_close_boundary_ms=row.bar_close_boundary_ms,
        raw_fields=row.raw_fields,
        source_refs=refs,
    )


def normalize_archive_rows(
    rows: Iterable[ArchiveKlineRow],
    *,
    exchange: str,
    market_type: str,
    symbol: str,
    timeframe: str,
    source_ref: str,
) -> ImportBatchResult:
    """Normalize validated rows and reconcile duplicates without side effects.

    A differing payload under the same identity marks all rows for that identity
    as conflicting and quarantines the entire batch. No candidate is released
    from a quarantined batch.
    """
    exchange = _required_text(exchange, "exchange")
    market_type = _required_text(market_type, "market_type")
    symbol = _required_text(symbol, "symbol")
    timeframe = _required_text(timeframe, "timeframe")
    source_ref = _required_text(source_ref, "source_ref")
    _interval(timeframe)

    try:
        source_rows = tuple(rows)
    except TypeError as exc:
        raise ImportBatchError("rows must be an iterable of ArchiveKlineRow") from exc

    if any(not isinstance(row, ArchiveKlineRow) for row in source_rows):
        raise ImportBatchError("every input row must be an ArchiveKlineRow")

    # Keep first-seen identity order while grouping all source occurrences.
    grouped: dict[
        tuple[str, str, str, str, int],
        list[tuple[int, ArchiveKlineRow, SourceRowReference]],
    ] = {}
    row_identities: list[tuple[str, str, str, str, int]] = []
    for ordinal, row in enumerate(source_rows, start=1):
        open_time_ms = _timestamp(
            row.open_time_ms, "row.open_time_ms", INTERVALS_MS[timeframe]
        )
        identity = (exchange, market_type, symbol, timeframe, open_time_ms)
        ref = SourceRowReference(source_ref=source_ref, row_ordinal=ordinal)
        grouped.setdefault(identity, []).append((ordinal - 1, row, ref))
        row_identities.append(identity)

    dispositions = [RowDisposition.REJECTED] * len(source_rows)
    candidates: list[ImportCandidate] = []
    quarantined = False

    for identity, occurrences in grouped.items():
        payloads = {_normalized_payload(row) for _, row, _ in occurrences}
        if len(payloads) > 1:
            quarantined = True
            for index, _, _ in occurrences:
                dispositions[index] = RowDisposition.CONFLICTING
            continue

        first_index, first_row, _ = occurrences[0]
        dispositions[first_index] = RowDisposition.ACCEPTED
        for index, _, _ in occurrences[1:]:
            dispositions[index] = RowDisposition.IDENTICAL_DUPLICATE

        refs = tuple(ref for _, _, ref in occurrences)
        candidates.append(_candidate(first_row, identity, refs))

    candidates.sort(key=lambda candidate: candidate.identity)

    row_results = tuple(
        ImportRowResult(
            source_ref=source_ref,
            row_ordinal=index,
            identity=row_identities[index - 1],
            disposition=dispositions[index - 1],
        )
        for index in range(1, len(source_rows) + 1)
    )
    counts = {
        disposition: sum(item is disposition for item in dispositions)
        for disposition in RowDisposition
    }
    accounting = RowAccounting(
        source_row_count=len(source_rows),
        accepted_count=counts[RowDisposition.ACCEPTED],
        identical_duplicate_count=counts[RowDisposition.IDENTICAL_DUPLICATE],
        rejected_count=counts[RowDisposition.REJECTED],
        conflicting_count=counts[RowDisposition.CONFLICTING],
    )

    if sum(
        (
            accounting.accepted_count,
            accounting.identical_duplicate_count,
            accounting.rejected_count,
            accounting.conflicting_count,
        )
    ) != accounting.source_row_count:
        raise AssertionError("internal row accounting invariant violated")

    return ImportBatchResult(
        candidates=() if quarantined else tuple(candidates),
        row_results=row_results,
        accounting=accounting,
        quarantined=quarantined,
    )


def calculate_coverage(
    *,
    timeframe: str,
    start_open_time_ms: int,
    end_open_time_ms: int,
    observed_open_times: Iterable[int],
) -> CoverageReport:
    """Report facts on an explicit UTC-aligned half-open timeframe grid."""
    interval_ms = _interval(timeframe)
    start = _timestamp(start_open_time_ms, "start_open_time_ms", interval_ms)
    end = _timestamp(end_open_time_ms, "end_open_time_ms", interval_ms)
    if end <= start:
        raise ImportBatchError("coverage bounds must define a non-empty half-open range")

    try:
        supplied = tuple(observed_open_times)
    except TypeError as exc:
        raise ImportBatchError("observed_open_times must be iterable") from exc

    validated = {
        _timestamp(value, "observed_open_time_ms", interval_ms)
        for value in supplied
    }
    expected = tuple(range(start, end, interval_ms))
    expected_set = set(expected)
    observed = tuple(sorted(value for value in validated if value in expected_set))
    missing = tuple(value for value in expected if value not in validated)
    out_of_range = tuple(sorted(value for value in validated if value not in expected_set))

    return CoverageReport(
        timeframe=timeframe,
        start_open_time_ms=start,
        end_open_time_ms=end,
        expected_open_times=expected,
        observed_open_times=observed,
        missing_open_times=missing,
        out_of_range_open_times=out_of_range,
    )
