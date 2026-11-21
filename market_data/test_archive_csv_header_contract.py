"""TDD coverage for the frozen T0_ARCHIVE_CSV_HEADER_V1 contract.

Synthetic CSV only: real-source schema evidence is recorded separately.
"""
import unittest

from market_data.archive_csv_parser import (
    ARCHIVE_CSV_HEADER_V1,
    ArchiveCsvError,
    parse_archive_csv,
    parse_archive_csv_document,
)

HEADER = ",".join(ARCHIVE_CSV_HEADER_V1)
ROW_1 = "1767225600000,90000.00,90100.00,89900.00,90050.00,12.345,1767226499999,1111111.23,42,5.678,510000.12,0"
ROW_2 = "1767226500000,90050.00,90200.00,90000.00,90150.00,10.000,1767227399999,901500.00,30,4.000,360000.00,0"


class ArchiveCsvHeaderContractTest(unittest.TestCase):
    def test_accepts_exact_header_and_reports_metadata(self):
        result = parse_archive_csv_document(HEADER + "\n" + ROW_1 + "\n", timeframe="15m")
        self.assertTrue(result.header_present)
        self.assertEqual(result.header_fields, ARCHIVE_CSV_HEADER_V1)
        self.assertEqual(result.data_row_count, 1)
        self.assertEqual(len(result.rows), 1)

    def test_header_and_headerless_documents_produce_identical_rows(self):
        with_header = parse_archive_csv_document(HEADER + "\n" + ROW_1 + "\n" + ROW_2, timeframe="15m")
        without_header = parse_archive_csv_document(ROW_1 + "\n" + ROW_2, timeframe="15m")
        self.assertEqual(with_header.rows, without_header.rows)
        self.assertTrue(with_header.header_present)
        self.assertFalse(without_header.header_present)

    def test_legacy_api_keeps_tuple_return_and_headerless_compatibility(self):
        self.assertEqual(parse_archive_csv(ROW_1, timeframe="15m"), (parse_archive_csv_document(ROW_1, timeframe="15m").rows[0],))

    def test_rejects_first_cell_only_header_match(self):
        partial = "open_time,open,high,low,close,volume,close_time,quote_volume,trades,taker_base,taker_quote,ignore"
        with self.assertRaises(ArchiveCsvError):
            parse_archive_csv_document(partial + "\n" + ROW_1, timeframe="15m")

    def test_rejects_missing_header_field(self):
        fields = list(ARCHIVE_CSV_HEADER_V1)
        fields.pop()
        with self.assertRaises(ArchiveCsvError):
            parse_archive_csv_document(",".join(fields) + "\n" + ROW_1, timeframe="15m")

    def test_rejects_extra_header_field(self):
        fields = list(ARCHIVE_CSV_HEADER_V1) + ["extra"]
        with self.assertRaises(ArchiveCsvError):
            parse_archive_csv_document(",".join(fields) + "\n" + ROW_1, timeframe="15m")

    def test_rejects_duplicate_header_field(self):
        fields = list(ARCHIVE_CSV_HEADER_V1)
        fields[1] = fields[0]
        with self.assertRaises(ArchiveCsvError):
            parse_archive_csv_document(",".join(fields) + "\n" + ROW_1, timeframe="15m")

    def test_rejects_reordered_header_fields(self):
        fields = list(ARCHIVE_CSV_HEADER_V1)
        fields[0], fields[1] = fields[1], fields[0]
        with self.assertRaises(ArchiveCsvError):
            parse_archive_csv_document(",".join(fields) + "\n" + ROW_1, timeframe="15m")

    def test_rejects_unsupported_aliases_case_and_whitespace(self):
        for changed in (
            HEADER.replace("count", "trades"),
            HEADER.replace("open_time", "OPEN_TIME"),
            HEADER.replace("open_time", " open_time"),
        ):
            with self.subTest(changed=changed):
                with self.assertRaises(ArchiveCsvError):
                    parse_archive_csv_document(changed + "\n" + ROW_1, timeframe="15m")

    def test_rejects_header_in_second_record(self):
        with self.assertRaises(ArchiveCsvError):
            parse_archive_csv_document(ROW_1 + "\n" + HEADER + "\n" + ROW_2, timeframe="15m")

    def test_rejects_repeated_header_in_body(self):
        with self.assertRaises(ArchiveCsvError):
            parse_archive_csv_document(HEADER + "\n" + ROW_1 + "\n" + HEADER, timeframe="15m")

    def test_rejects_header_only_document(self):
        with self.assertRaisesRegex(ArchiveCsvError, "at least one data row"):
            parse_archive_csv_document(HEADER + "\n", timeframe="15m")

    def test_rejects_blank_first_and_body_records(self):
        for document in ("\n" + ROW_1, ROW_1 + "\n\n" + ROW_2):
            with self.subTest(document=document):
                with self.assertRaises(ArchiveCsvError):
                    parse_archive_csv_document(document, timeframe="15m")

    def test_rejects_malformed_quoting_and_wrong_delimiter(self):
        for document in ('"unterminated', ROW_1.replace(",", ";")):
            with self.subTest(document=document):
                with self.assertRaises(ArchiveCsvError):
                    parse_archive_csv_document(document, timeframe="15m")

    def test_does_not_skip_malformed_data_as_a_header(self):
        malformed = "not-a-timestamp,90000,90100,89900,90050,12,1767226499999,100,42,5,50,0"
        with self.assertRaisesRegex(ArchiveCsvError, "open_time"):
            parse_archive_csv_document(malformed, timeframe="15m")


if __name__ == "__main__":
    unittest.main()
