"""Offline parser contract tests using synthetic CSV only.

These tests do not establish compatibility with real Binance archive files.
"""
from dataclasses import FrozenInstanceError
from decimal import Decimal
from pathlib import Path
import unittest

from market_data.archive_csv_parser import ArchiveCsvError, parse_archive_csv

FIXTURES = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "t0"


class ArchiveCsvParserTest(unittest.TestCase):
    def test_parses_synthetic_m15_fixture_with_exact_decimals(self):
        text = (FIXTURES / "binance_um_btcusdt_m15_synthetic.csv").read_text(encoding="utf-8")
        rows = parse_archive_csv(text, timeframe="15m")

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].open_time_ms, 1767225600000)
        self.assertEqual(rows[0].open, Decimal("90000.00"))
        self.assertEqual(rows[0].volume, Decimal("12.345"))
        self.assertEqual(rows[0].source_close_time_ms, 1767226499999)
        self.assertEqual(rows[0].bar_close_boundary_ms, 1767226500000)
        self.assertEqual(rows[0].number_of_trades, 42)
        self.assertEqual(rows[0].raw_fields[11], "0")

    def test_parses_synthetic_h1_fixture(self):
        text = (FIXTURES / "binance_um_btcusdt_h1_synthetic.csv").read_text(encoding="utf-8")
        rows = parse_archive_csv(text, timeframe="1h")

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1].open_time_ms, 1767229200000)
        self.assertEqual(rows[1].bar_close_boundary_ms, 1767232800000)

    def test_returns_immutable_rows_and_preserves_all_source_fields(self):
        text = (FIXTURES / "binance_um_btcusdt_m15_synthetic.csv").read_text(encoding="utf-8")
        row = parse_archive_csv(text, timeframe="15m")[0]

        self.assertEqual(len(row.raw_fields), 12)
        self.assertEqual(row.quote_asset_volume, Decimal("1111111.23"))
        self.assertEqual(row.taker_buy_base_asset_volume, Decimal("5.678"))
        self.assertEqual(row.taker_buy_quote_asset_volume, Decimal("510000.12"))
        with self.assertRaises(FrozenInstanceError):
            row.open_time_ms = 1

    def test_rejects_header_row_instead_of_guessing_header_mode(self):
        with self.assertRaisesRegex(ArchiveCsvError, "row 1"):
            parse_archive_csv(
                "open_time,open,high,low,close,volume,close_time,quote_volume,trades,taker_base,taker_quote,ignore\n",
                timeframe="15m",
            )

    def test_rejects_wrong_column_count(self):
        with self.assertRaisesRegex(ArchiveCsvError, "12 fields"):
            parse_archive_csv("1,2,3\n", timeframe="15m")

    def test_rejects_blank_rows(self):
        with self.assertRaises(ArchiveCsvError):
            parse_archive_csv("\n", timeframe="15m")

    def test_rejects_unsupported_timeframe(self):
        with self.assertRaisesRegex(ArchiveCsvError, "timeframe"):
            parse_archive_csv("1,2,3", timeframe="4h")

    def test_rejects_non_integer_timestamp(self):
        text = (FIXTURES / "binance_um_btcusdt_m15_synthetic.csv").read_text(encoding="utf-8")
        malformed = text.replace("1767225600000,", "1767225600000.0,", 1)
        with self.assertRaisesRegex(ArchiveCsvError, "open_time"):
            parse_archive_csv(malformed, timeframe="15m")

    def test_rejects_unaligned_open_timestamp(self):
        text = (FIXTURES / "binance_um_btcusdt_m15_synthetic.csv").read_text(encoding="utf-8")
        malformed = text.replace("1767225600000,", "1767225600001,", 1)
        with self.assertRaisesRegex(ArchiveCsvError, "aligned"):
            parse_archive_csv(malformed, timeframe="15m")

    def test_rejects_incorrect_inclusive_close_timestamp(self):
        text = (FIXTURES / "binance_um_btcusdt_m15_synthetic.csv").read_text(encoding="utf-8")
        malformed = text.replace("1767226499999", "1767226500000", 1)
        with self.assertRaisesRegex(ArchiveCsvError, "close_time"):
            parse_archive_csv(malformed, timeframe="15m")

    def test_rejects_invalid_decimal_without_float_coercion(self):
        text = (FIXTURES / "binance_um_btcusdt_m15_synthetic.csv").read_text(encoding="utf-8")
        malformed = text.replace("90000.00", "NaN", 1)
        with self.assertRaisesRegex(ArchiveCsvError, "open"):
            parse_archive_csv(malformed, timeframe="15m")

    def test_rejects_non_finite_and_exponent_overflow_values(self):
        text = (FIXTURES / "binance_um_btcusdt_m15_synthetic.csv").read_text(encoding="utf-8")
        for invalid in ("Infinity", "1e999999", "9" * 129):
            malformed = text.replace("12.345", invalid, 1)
            with self.subTest(invalid=invalid[:16]):
                with self.assertRaises(ArchiveCsvError):
                    parse_archive_csv(malformed, timeframe="15m")

    def test_rejects_invalid_ohlc_envelope(self):
        text = (FIXTURES / "binance_um_btcusdt_m15_synthetic.csv").read_text(encoding="utf-8")
        malformed = text.replace("90100.00", "89900.00", 1)
        with self.assertRaisesRegex(ArchiveCsvError, "OHLC"):
            parse_archive_csv(malformed, timeframe="15m")

    def test_rejects_negative_volume(self):
        text = (FIXTURES / "binance_um_btcusdt_m15_synthetic.csv").read_text(encoding="utf-8")
        malformed = text.replace("12.345", "-12.345", 1)
        with self.assertRaisesRegex(ArchiveCsvError, "volume"):
            parse_archive_csv(malformed, timeframe="15m")

    def test_rejects_non_integer_trade_count(self):
        text = (FIXTURES / "binance_um_btcusdt_m15_synthetic.csv").read_text(encoding="utf-8")
        malformed = text.replace(",42,", ",42.0,", 1)
        with self.assertRaisesRegex(ArchiveCsvError, "number_of_trades"):
            parse_archive_csv(malformed, timeframe="15m")

    def test_rejects_taker_buy_volume_above_total(self):
        text = (FIXTURES / "binance_um_btcusdt_m15_synthetic.csv").read_text(encoding="utf-8")
        malformed = text.replace(",5.678,", ",99.678,", 1)
        with self.assertRaisesRegex(ArchiveCsvError, "taker_buy_base"):
            parse_archive_csv(malformed, timeframe="15m")

    def test_rejects_duplicate_and_out_of_order_timestamps(self):
        text = (FIXTURES / "binance_um_btcusdt_m15_synthetic.csv").read_text(encoding="utf-8")
        lines = text.splitlines()
        with self.assertRaisesRegex(ArchiveCsvError, "strictly increasing"):
            parse_archive_csv("\n".join([lines[1], lines[0]]) + "\n", timeframe="15m")

    def test_rejects_timestamp_outside_signed_64_bit_range(self):
        text = (FIXTURES / "binance_um_btcusdt_m15_synthetic.csv").read_text(encoding="utf-8")
        # The supplied open/close timestamps exceed the signed int64 contract.
        overflow_row = "9223372036854000000,1,2,1,2,1,9223372036854899999,2,1,1,1,0"
        with self.assertRaises(ArchiveCsvError):
            parse_archive_csv(overflow_row, timeframe="15m")

    def test_rejects_csv_syntax_errors(self):
        with self.assertRaises(ArchiveCsvError):
            parse_archive_csv('"unterminated', timeframe="15m")


if __name__ == "__main__":
    unittest.main()
