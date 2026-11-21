import unittest

from paper_execution.mark_provenance import (
    MarketMarkProvenance,
    build_market_mark_provenance,
    validate_consumed_mark,
)


class MarketMarkProvenanceTests(unittest.TestCase):
    def window(self):
        return {
            "symbol": "BTCUSDT",
            "timeframe": "15m",
            "datasetVersion": "sha256:" + "a" * 64,
            "candles": [
                {
                    "openTimeMs": 1_800_000_000_000,
                    "closeTimeMs": 1_800_000_900_000,
                    "open": "100",
                    "high": "102",
                    "low": "99",
                    "close": "101.25",
                    "volume": "12.5",
                }
            ],
        }

    def test_provenance_identifies_exact_consumed_candle_and_payload(self):
        provenance = build_market_mark_provenance(
            self.window(), source_id="T0_CANONICAL_MARKET_DATA"
        )
        self.assertIsInstance(provenance, MarketMarkProvenance)
        self.assertEqual(provenance.mark_price, "101.25")
        self.assertEqual(provenance.candle_close_ms, 1_800_000_900_000)
        self.assertEqual(provenance.dataset_version, "sha256:" + "a" * 64)
        self.assertTrue(provenance.source_snapshot_id.startswith("sha256:"))
        self.assertEqual(provenance.source_snapshot_id, "sha256:" + provenance.source_payload_sha256)

    def test_provenance_digest_is_deterministic_and_key_order_independent(self):
        original = self.window()
        reordered = {
            "candles": [dict(reversed(list(original["candles"][0].items())))],
            "datasetVersion": original["datasetVersion"],
            "timeframe": original["timeframe"],
            "symbol": original["symbol"],
        }
        first = build_market_mark_provenance(original, source_id="T0_CANONICAL_MARKET_DATA")
        second = build_market_mark_provenance(reordered, source_id="T0_CANONICAL_MARKET_DATA")
        self.assertEqual(first, second)

    def test_any_change_to_consumed_mark_or_dataset_changes_snapshot_identity(self):
        original = self.window()
        first = build_market_mark_provenance(original, source_id="T0_CANONICAL_MARKET_DATA")
        changed = self.window()
        changed["candles"][0]["close"] = "101.26"
        second = build_market_mark_provenance(changed, source_id="T0_CANONICAL_MARKET_DATA")
        self.assertNotEqual(first.source_snapshot_id, second.source_snapshot_id)
        changed_dataset = self.window()
        changed_dataset["datasetVersion"] = "sha256:" + "b" * 64
        third = build_market_mark_provenance(changed_dataset, source_id="T0_CANONICAL_MARKET_DATA")
        self.assertNotEqual(first.source_snapshot_id, third.source_snapshot_id)

    def test_missing_or_ambiguous_market_data_fails_closed(self):
        invalid = [
            {},
            {**self.window(), "datasetVersion": ""},
            {**self.window(), "candles": []},
            {**self.window(), "candles": [None]},
            {**self.window(), "symbol": "ETHUSDT"},
            {**self.window(), "timeframe": "1m"},
        ]
        for window in invalid:
            with self.subTest(window=window), self.assertRaises(ValueError):
                build_market_mark_provenance(window, source_id="T0_CANONICAL_MARKET_DATA")

    def test_consumed_mark_must_match_provenance_exactly(self):
        provenance = build_market_mark_provenance(
            self.window(), source_id="T0_CANONICAL_MARKET_DATA"
        )
        self.assertIs(
            validate_consumed_mark(
                provenance,
                mark_price="101.25",
                candle_close_ms=1_800_000_900_000,
                dataset_version="sha256:" + "a" * 64,
            ),
            provenance,
        )
        for changes in (
            {"mark_price": "101.26"},
            {"candle_close_ms": 1_800_000_900_001},
            {"dataset_version": "sha256:" + "b" * 64},
        ):
            values = {
                "mark_price": "101.25",
                "candle_close_ms": 1_800_000_900_000,
                "dataset_version": "sha256:" + "a" * 64,
            }
            values.update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_consumed_mark(provenance, **values)


if __name__ == "__main__":
    unittest.main()
