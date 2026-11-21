import hashlib
import json
import unittest

from paper_execution.mark_provenance import (
    MarketMarkProvenance,
    build_market_mark_provenance,
    validate_consumed_mark,
)


class MarketMarkProvenanceTests(unittest.TestCase):
    def window(self):
        payload = {
            "exchange": "binance",
            "marketType": "USDT_PERPETUAL",
            "symbol": "BTCUSDT",
            "timeframe": "15m",
            "startMs": 1_800_000_000_000,
            "endMs": 1_800_000_900_000,
            "asOfMs": 1_800_000_900_000,
            "candles": [
                {
                    "openTimeMs": 1_800_000_000_000,
                    "closeTimeMs": 1_800_000_900_000,
                    "availableAtMs": 1_800_000_900_000,
                    "open": "100",
                    "high": "102",
                    "low": "99",
                    "close": "101.25",
                    "volume": "12.5",
                }
            ],
        }
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        return {
            **payload,
            "datasetVersion": "sha256:" + digest,
            "coverage": {"expected": 1, "returned": 1, "complete": True, "gaps": []},
        }

    def test_provenance_identifies_exact_consumed_candle_and_payload(self):
        provenance = build_market_mark_provenance(
            self.window(), source_id="T0_CANONICAL_MARKET_DATA"
        )
        self.assertIsInstance(provenance, MarketMarkProvenance)
        self.assertEqual(provenance.mark_price, "101.25")
        self.assertEqual(provenance.candle_close_ms, 1_800_000_900_000)
        self.assertEqual(provenance.dataset_version, self.window()["datasetVersion"])
        self.assertTrue(provenance.source_snapshot_id.startswith("sha256:"))
        self.assertEqual(provenance.source_snapshot_id, provenance.dataset_version)
        self.assertEqual(len(provenance.source_payload_sha256), 64)

    def test_provenance_digest_is_deterministic_and_key_order_independent(self):
        original = self.window()
        reordered = {
            "candles": [dict(reversed(list(original["candles"][0].items())))],
            "datasetVersion": original["datasetVersion"],
            "exchange": original["exchange"], "marketType": original["marketType"],
            "coverage": original["coverage"],
            "timeframe": original["timeframe"],
            "symbol": original["symbol"],
            "startMs": original["startMs"], "endMs": original["endMs"],
            "asOfMs": original["asOfMs"],
        }
        first = build_market_mark_provenance(original, source_id="T0_CANONICAL_MARKET_DATA")
        second = build_market_mark_provenance(reordered, source_id="T0_CANONICAL_MARKET_DATA")
        self.assertEqual(first, second)

    def test_dataset_snapshot_hash_and_consumed_mark_hash_are_distinct(self):
        provenance = build_market_mark_provenance(
            self.window(), source_id="T0_CANONICAL_MARKET_DATA"
        )
        self.assertEqual(provenance.source_snapshot_id, provenance.dataset_version)
        self.assertNotEqual(
            provenance.source_payload_sha256,
            provenance.dataset_version.removeprefix("sha256:"),
        )

    def test_tampered_window_cannot_reuse_the_original_dataset_version(self):
        changed = self.window()
        changed["candles"][0]["close"] = "101.26"
        with self.assertRaisesRegex(ValueError, "MARK_SOURCE_DATASET_VERSION_MISMATCH"):
            build_market_mark_provenance(
                changed, source_id="T0_CANONICAL_MARKET_DATA"
            )

    def test_noncanonical_source_id_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "MARK_SOURCE_ID_UNSUPPORTED"):
            build_market_mark_provenance(self.window(), source_id="OTHER_SOURCE")

    def test_missing_or_ambiguous_market_data_fails_closed(self):
        invalid = [
            {},
            {**self.window(), "datasetVersion": ""},
            {**self.window(), "candles": []},
            {**self.window(), "candles": [None]},
            {**self.window(), "symbol": "ETHUSDT"},
            {**self.window(), "timeframe": "1m"},
            {**self.window(), "coverage": {"expected": 1, "returned": 1, "complete": False, "gaps": []}},
            {**self.window(), "exchange": "okx"},
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
                dataset_version=self.window()["datasetVersion"],
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
                "dataset_version": self.window()["datasetVersion"],
            }
            values.update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_consumed_mark(provenance, **values)


if __name__ == "__main__":
    unittest.main()
