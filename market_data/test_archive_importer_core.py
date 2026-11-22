"""Synthetic-only tests for the in-memory archive importer core.

No archive, filesystem, network, database or exchange I/O is permitted here.
"""
from dataclasses import FrozenInstanceError
from decimal import Decimal
import unittest

from market_data.archive_csv_parser import ArchiveKlineRow, parse_archive_csv
from market_data.archive_importer_core import (
    ImportBatchError,
    RowDisposition,
    calculate_coverage,
    normalize_archive_rows,
)


M15 = 15 * 60 * 1000
H1 = 60 * 60 * 1000
BASE = 1_767_225_600_000


def parsed_row(open_time_ms=BASE, *, open_price="90000.00", close="90000.00", ignore="0"):
    close_time_ms = open_time_ms + M15 - 1
    csv_row = (
        f"{open_time_ms},{open_price},90100.00,89900.00,{close},12.345,"
        f"{close_time_ms},1111111.23,42,5.678,510000.12,{ignore}"
    )
    return parse_archive_csv(csv_row, timeframe="15m")[0]


def parsed_h1_row(open_time_ms=BASE):
    close_time_ms = open_time_ms + H1 - 1
    csv_row = (
        f"{open_time_ms},90000.00,90100.00,89900.00,90000.00,12.345,"
        f"{close_time_ms},1111111.23,42,5.678,510000.12,0"
    )
    return parse_archive_csv(csv_row, timeframe="1h")[0]


def normalize(rows, *, timeframe="15m", source_ref="fixture://synthetic.csv"):
    return normalize_archive_rows(
        tuple(rows),
        exchange="binance",
        market_type="usd_m",
        symbol="BTCUSDT",
        timeframe=timeframe,
        source_ref=source_ref,
    )


class ImporterCoreNormalizationTests(unittest.TestCase):
    def test_normalizes_explicit_identity_and_preserves_exact_source_values(self):
        source = parsed_row()
        result = normalize([source])

        self.assertFalse(result.quarantined)
        self.assertEqual(len(result.candidates), 1)
        candidate = result.candidates[0]
        self.assertEqual(
            candidate.identity,
            ("binance", "usd_m", "BTCUSDT", "15m", BASE),
        )
        self.assertEqual(candidate.open, Decimal("90000.00"))
        self.assertEqual(candidate.volume, Decimal("12.345"))
        self.assertEqual(candidate.raw_fields, source.raw_fields)
        self.assertEqual(candidate.bar_close_boundary_ms, BASE + M15)
        self.assertNotIn("FIRST_OBSERVED", candidate.__dataclass_fields__)

    def test_candidate_and_nested_source_references_are_immutable(self):
        candidate = normalize([parsed_row()]).candidates[0]
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            candidate.open_time_ms = BASE + M15
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            candidate.source_refs[0].row_ordinal = 99

    def test_assigns_one_based_row_ordinals_and_opaque_source_reference(self):
        result = normalize(
            [parsed_row(), parsed_row(BASE + M15)],
            source_ref="opaque:archive-member-7",
        )

        refs = [candidate.source_refs[0] for candidate in result.candidates]
        self.assertEqual(
            [(ref.source_ref, ref.row_ordinal) for ref in refs],
            [("opaque:archive-member-7", 1), ("opaque:archive-member-7", 2)],
        )

    def test_same_identity_and_same_payload_is_one_candidate_with_both_refs(self):
        row = parsed_row()
        result = normalize([row, row], source_ref="opaque:duplicate")

        self.assertFalse(result.quarantined)
        self.assertEqual(len(result.candidates), 1)
        self.assertEqual(
            [ref.row_ordinal for ref in result.candidates[0].source_refs],
            [1, 2],
        )
        self.assertEqual(
            [item.disposition for item in result.row_results],
            [RowDisposition.ACCEPTED, RowDisposition.IDENTICAL_DUPLICATE],
        )
        self.assertEqual(result.accounting.source_row_count, 2)
        self.assertEqual(result.accounting.accepted_count, 1)
        self.assertEqual(result.accounting.identical_duplicate_count, 1)
        self.assertEqual(result.accounting.rejected_count, 0)
        self.assertEqual(result.accounting.conflicting_count, 0)

    def test_same_identity_with_different_raw_payload_quarantines_entire_batch(self):
        first = parsed_row()
        conflicting = parsed_row(ignore="different")
        unrelated = parsed_row(BASE + M15)
        result = normalize([first, conflicting, unrelated])

        self.assertTrue(result.quarantined)
        self.assertEqual(result.candidates, ())
        self.assertEqual(
            [item.disposition for item in result.row_results],
            [
                RowDisposition.CONFLICTING,
                RowDisposition.CONFLICTING,
                RowDisposition.ACCEPTED,
            ],
        )
        self.assertEqual(result.accounting.source_row_count, 3)
        self.assertEqual(result.accounting.accepted_count, 1)
        self.assertEqual(result.accounting.conflicting_count, 2)
        self.assertEqual(
            result.accounting.accepted_count
            + result.accounting.identical_duplicate_count
            + result.accounting.rejected_count
            + result.accounting.conflicting_count,
            result.accounting.source_row_count,
        )

    def test_normalizes_valid_h1_rows_with_explicit_timeframe(self):
        result = normalize([parsed_h1_row()], timeframe="1h")

        self.assertFalse(result.quarantined)
        self.assertEqual(result.candidates[0].identity, ("binance", "usd_m", "BTCUSDT", "1h", BASE))
        self.assertEqual(result.candidates[0].bar_close_boundary_ms, BASE + H1)

    def test_candidate_order_is_stable_when_input_batch_order_changes(self):
        rows = [parsed_row(BASE + M15), parsed_row(BASE)]
        result = normalize(rows)

        self.assertEqual(
            [candidate.open_time_ms for candidate in result.candidates],
            [BASE, BASE + M15],
        )

    def test_decimal_text_variants_with_equal_normalized_values_are_identical_duplicates(self):
        first = parsed_row(open_price="90000.00")
        second = parsed_row(open_price="90000.0")
        result = normalize([first, second])

        self.assertFalse(result.quarantined)
        self.assertEqual(len(result.candidates), 1)
        self.assertEqual(result.accounting.identical_duplicate_count, 1)
        self.assertEqual(result.candidates[0].open, Decimal("90000.00"))
        self.assertEqual(result.candidates[0].source_refs[0].row_ordinal, 1)
        self.assertEqual(result.candidates[0].source_refs[1].row_ordinal, 2)
        self.assertNotEqual(first.raw_fields, second.raw_fields)

    def test_rejects_row_identity_not_aligned_to_explicit_timeframe(self):
        with self.assertRaises(ImportBatchError):
            normalize([parsed_row(BASE + M15)], timeframe="1h")

    def test_payload_equality_does_not_collapse_distinct_open_time_identity(self):
        first = parsed_row()
        second = parsed_row(BASE + M15)
        result = normalize([first, second])

        self.assertFalse(result.quarantined)
        self.assertEqual(len(result.candidates), 2)
        self.assertNotEqual(result.candidates[0].identity, result.candidates[1].identity)

    def test_rejects_empty_or_whitespace_identity_fields(self):
        for field, value in (
            ("exchange", ""),
            ("market_type", "  "),
            ("symbol", ""),
        ):
            kwargs = {
                "exchange": "binance",
                "market_type": "usd_m",
                "symbol": "BTCUSDT",
                "timeframe": "15m",
                "source_ref": "opaque",
            }
            kwargs[field] = value
            with self.subTest(field=field), self.assertRaises(ImportBatchError):
                normalize_archive_rows((parsed_row(),), **kwargs)

    def test_rejects_unsupported_timeframe_and_non_row_input(self):
        with self.assertRaises(ImportBatchError):
            normalize([parsed_row()], timeframe="4h")
        with self.assertRaises(ImportBatchError):
            normalize([object()])

    def test_empty_source_reference_is_rejected(self):
        with self.assertRaises(ImportBatchError):
            normalize([parsed_row()], source_ref=" ")


class ImporterCoreCoverageTests(unittest.TestCase):
    def test_calculates_expected_observed_and_missing_on_half_open_grid(self):
        report = calculate_coverage(
            timeframe="15m",
            start_open_time_ms=BASE,
            end_open_time_ms=BASE + 4 * M15,
            observed_open_times=(BASE, BASE + 2 * M15),
        )

        self.assertEqual(report.expected_count, 4)
        self.assertEqual(report.observed_count, 2)
        self.assertEqual(report.missing_open_times, (BASE + M15, BASE + 3 * M15))
        self.assertEqual(report.out_of_range_open_times, ())

    def test_end_boundary_is_excluded_from_expected_grid(self):
        report = calculate_coverage(
            timeframe="15m",
            start_open_time_ms=BASE,
            end_open_time_ms=BASE + 2 * M15,
            observed_open_times=(BASE, BASE + M15, BASE + 2 * M15),
        )

        self.assertEqual(report.expected_open_times, (BASE, BASE + M15))
        self.assertEqual(report.out_of_range_open_times, (BASE + 2 * M15,))

    def test_deduplicates_observed_open_times_for_coverage_counts(self):
        report = calculate_coverage(
            timeframe="1h",
            start_open_time_ms=BASE,
            end_open_time_ms=BASE + 2 * H1,
            observed_open_times=(BASE, BASE, BASE + H1),
        )

        self.assertEqual(report.expected_count, 2)
        self.assertEqual(report.observed_count, 2)
        self.assertEqual(report.missing_open_times, ())

    def test_reports_out_of_range_values_without_treating_them_as_observed(self):
        report = calculate_coverage(
            timeframe="15m",
            start_open_time_ms=BASE,
            end_open_time_ms=BASE + 2 * M15,
            observed_open_times=(BASE - M15, BASE, BASE + 3 * M15),
        )

        self.assertEqual(report.observed_open_times, (BASE,))
        self.assertEqual(
            report.out_of_range_open_times,
            (BASE - M15, BASE + 3 * M15),
        )

    def test_rejects_empty_half_open_range(self):
        with self.assertRaises(ImportBatchError):
            calculate_coverage(
                timeframe="15m",
                start_open_time_ms=BASE,
                end_open_time_ms=BASE,
                observed_open_times=(),
            )

    def test_rejects_invalid_timeframe_bounds_and_unaligned_timestamps(self):
        cases = (
            {"timeframe": "4h", "start_open_time_ms": BASE, "end_open_time_ms": BASE + M15},
            {"timeframe": "15m", "start_open_time_ms": BASE + 1, "end_open_time_ms": BASE + M15},
            {"timeframe": "15m", "start_open_time_ms": BASE + M15, "end_open_time_ms": BASE},
            {"timeframe": "15m", "start_open_time_ms": -M15, "end_open_time_ms": 0},
        )
        for kwargs in cases:
            with self.subTest(kwargs=kwargs), self.assertRaises(ImportBatchError):
                calculate_coverage(**kwargs, observed_open_times=())

    def test_rejects_unaligned_or_non_integer_observed_timestamps(self):
        for value in (BASE + 1, True, "1767225600000"):
            with self.subTest(value=value), self.assertRaises(ImportBatchError):
                calculate_coverage(
                    timeframe="15m",
                    start_open_time_ms=BASE,
                    end_open_time_ms=BASE + M15,
                    observed_open_times=(value,),
                )


if __name__ == "__main__":
    unittest.main()
