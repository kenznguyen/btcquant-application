import unittest
from datetime import datetime, timezone

from market_data.rest_tail_validator import validate_klines

CUTOFF = int(datetime(2026, 11, 20, 8, 2, 15, 852000, tzinfo=timezone.utc).timestamp() * 1000)
START = int(datetime(2026, 11, 19, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)


def kline(open_ms, interval_ms, *, high="102", low="99", volume="10", trades=3):
    return [
        open_ms, "100", high, low, "101", volume,
        open_ms + interval_ms - 1, "1000", trades, "4", "400", "0",
    ]


class RestTailValidatorTest(unittest.TestCase):
    def validate(self, rows, interval_ms, raw_count, closed_count):
        return validate_klines(
            rows,
            interval_ms=interval_ms,
            cutoff_ms=CUTOFF,
            expected_raw_rows=raw_count,
            expected_closed_rows=closed_count,
            expected_start_ms=START,
        )

    def test_filters_forming_m15_candle_and_validates_closed_grid(self):
        interval = 15 * 60 * 1000
        rows = [kline(START + i * interval, interval) for i in range(129)]
        result = self.validate(rows, interval, 129, 128)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["forming_rows_excluded"], 1)
        self.assertEqual(result["closed_rows"], 128)
        self.assertEqual(result["gaps"], [])

    def test_filters_forming_h1_candle(self):
        interval = 60 * 60 * 1000
        rows = [kline(START + i * interval, interval) for i in range(33)]
        result = self.validate(rows, interval, 33, 32)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["forming_rows_excluded"], 1)

    def test_rejects_duplicate_open_time(self):
        interval = 15 * 60 * 1000
        rows = [kline(START + i * interval, interval) for i in range(129)]
        rows[2] = rows[1]
        result = self.validate(rows, interval, 129, 128)
        self.assertFalse(result["ok"])
        self.assertTrue(any("duplicate" in error for error in result["errors"]))

    def test_detects_missing_interval(self):
        interval = 15 * 60 * 1000
        rows = [kline(START + i * interval, interval) for i in range(129) if i != 4]
        result = self.validate(rows, interval, 129, 128)
        self.assertTrue(any("gap" in error for error in result["errors"]))

    def test_rejects_bad_ohlc_envelope(self):
        interval = 15 * 60 * 1000
        rows = [kline(START + i * interval, interval) for i in range(129)]
        rows[0] = kline(START, interval, high="99.5")
        result = self.validate(rows, interval, 129, 128)
        self.assertTrue(any("OHLC" in error for error in result["errors"]))

    def test_rejects_wrong_close_timestamp(self):
        interval = 15 * 60 * 1000
        rows = [kline(START + i * interval, interval) for i in range(129)]
        rows[0][6] += 1
        result = self.validate(rows, interval, 129, 128)
        self.assertTrue(any("closeTime" in error for error in result["errors"]))

    def test_rejects_non_finite_numeric_value(self):
        interval = 15 * 60 * 1000
        rows = [kline(START + i * interval, interval) for i in range(129)]
        rows[0][5] = "NaN"
        result = self.validate(rows, interval, 129, 128)
        self.assertTrue(any("finite" in error for error in result["errors"]))

    def test_rejects_unaligned_open_time(self):
        interval = 15 * 60 * 1000
        rows = [kline(START + i * interval, interval) for i in range(129)]
        rows[0][0] += 1
        result = self.validate(rows, interval, 129, 128)
        self.assertTrue(any("aligned" in error for error in result["errors"]))

    def test_rejects_negative_volume_and_invalid_trade_count(self):
        interval = 15 * 60 * 1000
        rows = [kline(START + i * interval, interval) for i in range(129)]
        rows[0][5] = "-1"
        rows[0][8] = -1
        result = self.validate(rows, interval, 129, 128)
        self.assertTrue(any("volume must be >= 0" in error for error in result["errors"]))
        self.assertTrue(any("trades must be a non-negative integer" in error for error in result["errors"]))

    def test_rejects_wrong_raw_row_count(self):
        interval = 15 * 60 * 1000
        rows = [kline(START + i * interval, interval) for i in range(128)]
        result = self.validate(rows, interval, 129, 128)
        self.assertTrue(any("raw row count" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
