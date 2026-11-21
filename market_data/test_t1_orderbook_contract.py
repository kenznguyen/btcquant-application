"""Synthetic acceptance tests for the T1 Orderbook V1 consumer contract.

All fixtures in this module are deterministic and synthetic; they are not exchange evidence.
"""
import hashlib
import json
import unittest

from market_data.t1_orderbook.validation import validate_payload
from market_data.t1_orderbook.errors import ContractError, ErrorCode
from market_data.t1_orderbook.fixtures import SYNTHETIC_FIXTURE, synthetic_valid_payload
from market_data.t1_orderbook.adapter import Rejected, Unavailable, consume_payload


NOW_MS = 10_000
SYNTHETIC_FIXTURE = True


def _canonical_bytes(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def valid_payload():
    return synthetic_valid_payload(NOW_MS)

def encode(payload):
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class T1OrderbookContractTest(unittest.TestCase):
    def accept(self, payload=None):
        return validate_payload(encode(payload if payload is not None else valid_payload()), now_ms=NOW_MS)

    def reject(self, payload, code=None):
        with self.assertRaises(ContractError) as caught:
            self.accept(payload)
        if code is not None:
            self.assertEqual(caught.exception.code, code)

    def test_accepts_exact_v1_payload_with_all_17_fields(self):
        self.assertTrue(SYNTHETIC_FIXTURE)
        snapshot = self.accept()
        self.assertEqual(snapshot.symbol, "BTCUSDT")
        self.assertEqual(len(snapshot.bids), 20)
        self.assertEqual(len(snapshot.asks), 20)

    def test_rejects_unknown_contract_version(self):
        p = valid_payload(); p["contractVersion"] = "T1_T2_ORDERBOOK_V2"
        self.reject(p, ErrorCode.UNSUPPORTED_VERSION)

    def test_rejects_wrong_symbol_or_market(self):
        for field, value in (("symbol", "ETHUSDT"), ("market", "BINANCE_SPOT")):
            p = valid_payload(); p[field] = value
            self.reject(p)

    def test_rejects_missing_each_required_top_level_field(self):
        for field in valid_payload():
            p = valid_payload(); del p[field]
            with self.subTest(field=field):
                self.reject(p)

    def test_rejects_any_unknown_top_level_or_nested_field(self):
        p = valid_payload(); p["unexpected"] = 1
        self.reject(p)
        p = valid_payload(); p["depth"]["extra"] = 1
        self.reject(p)

    def test_rejects_duplicate_json_object_keys(self):
        raw = encode(valid_payload()).decode()
        raw = raw.replace('"symbol":"BTCUSDT"', '"symbol":"BTCUSDT","symbol":"BTCUSDT"', 1)
        with self.assertRaises(ContractError) as caught:
            validate_payload(raw.encode(), now_ms=NOW_MS)
        self.assertEqual(caught.exception.code, ErrorCode.MALFORMED_JSON)

    def test_rejects_non_object_root_and_trailing_json_data(self):
        for raw in (b"[]", encode(valid_payload()) + b" {}"):
            with self.subTest(raw=raw[:8]):
                with self.assertRaises(ContractError):
                    validate_payload(raw, now_ms=NOW_MS)

    def test_rejects_malformed_or_truncated_json(self):
        with self.assertRaises(ContractError):
            validate_payload(b'{"contractVersion":', now_ms=NOW_MS)

    def test_rejects_extremely_nested_json_without_leaking_parser_error(self):
        raw = b"[" * 2000 + b"0" + b"]" * 2000
        with self.assertRaises(ContractError):
            validate_payload(raw, now_ms=NOW_MS)

    def test_rejects_payload_over_65536_bytes_before_decode(self):
        with self.assertRaises(ContractError) as caught:
            validate_payload(b" " * 65537, now_ms=NOW_MS)
        self.assertEqual(caught.exception.code, ErrorCode.PAYLOAD_TOO_LARGE)

    def test_rejects_boolean_or_float_where_unsigned_integer_is_required(self):
        for value in (True, 1.0):
            p = valid_payload(); p["generation"] = value
            self.reject(p)

    def test_rejects_negative_or_overflowed_unsigned_integer(self):
        for value in (-1, 2**64):
            p = valid_payload(); p["generation"] = value
            self.reject(p)

    def test_rejects_numeric_price_or_quantity_instead_of_string_tuple(self):
        p = valid_payload(); p["bids"][0][0] = 100.25
        self.reject(p)

    def test_rejects_tuple_with_missing_or_extra_elements(self):
        for level in (["100.25"], ["100.25", "1.5", "extra"]):
            p = valid_payload(); p["bids"][0] = level
            self.reject(p)

    def test_accepts_canonical_decimal_strings_without_float_rounding(self):
        p = valid_payload(); p["bids"][0][0] = "100.000000000000000001"
        p["bids"][1][0] = "99.999999999999999999"
        p["asks"][0][0] = "101.000000000000000001"
        p["snapshotId"] = ""
        unsigned = dict(p); unsigned.pop("snapshotId")
        p["snapshotId"] = "sha256:" + hashlib.sha256(_canonical_bytes(unsigned)).hexdigest()
        snapshot = self.accept(p)
        self.assertEqual(snapshot.bids[0][0], "100.000000000000000001")

    def test_rejects_empty_signed_exponent_whitespace_and_non_ascii_decimal(self):
        for value in ("", "-1", "+1", "1e2", " 1", "١٢"):
            p = valid_payload(); p["bids"][0][1] = value
            self.reject(p)

    def test_rejects_leading_zero_and_fraction_with_trailing_zero(self):
        for value in ("010.2", "10.20", "0.0"):
            p = valid_payload(); p["bids"][0][1] = value
            self.reject(p)

    def test_rejects_zero_or_negative_price_and_quantity(self):
        for field, value in (("price", "0"), ("price", "-1"), ("quantity", "0"), ("quantity", "-1")):
            p = valid_payload()
            p["bids"][0][0 if field == "price" else 1] = value
            self.reject(p)

    def test_rejects_bid_levels_not_strictly_descending(self):
        p = valid_payload(); p["bids"][1][0] = p["bids"][0][0]
        self.reject(p)

    def test_rejects_ask_levels_not_strictly_ascending(self):
        p = valid_payload(); p["asks"][1][0] = p["asks"][0][0]
        self.reject(p)

    def test_rejects_duplicate_bid_or_ask_price(self):
        for side in ("bids", "asks"):
            p = valid_payload(); p[side][1][0] = p[side][0][0]
            self.reject(p)

    def test_rejects_locked_or_crossed_spread(self):
        p = valid_payload(); p["asks"][0][0] = p["bids"][0][0]
        self.reject(p)

    def test_rejects_fewer_than_20_levels_on_either_side(self):
        for side in ("bids", "asks"):
            p = valid_payload(); p[side].pop(); p["depth"][side] -= 1
            self.reject(p)

    def test_rejects_depth_count_mismatch(self):
        p = valid_payload(); p["depth"]["bids"] = 19
        self.reject(p)

    def test_requires_nonzero_generation(self):
        p = valid_payload(); p["generation"] = 0
        self.reject(p)

    def test_requires_decision_watermark_equal_last_applied_u(self):
        p = valid_payload(); p["decisionWatermark"] = 119
        self.reject(p)

    def test_rejects_last_applied_u_below_first_applied_u(self):
        p = valid_payload(); p["lastAppliedU"] = 99
        p["decisionWatermark"] = 99
        self.reject(p)

    def test_rejects_source_timestamp_older_than_2000ms(self):
        p = valid_payload(); p["sourceTimestampMs"] = NOW_MS - 2001
        self.reject(p)

    def test_rejects_observed_timestamp_older_than_2000ms(self):
        p = valid_payload(); p["observedAtMs"] = NOW_MS - 2001
        self.reject(p)

    def test_rejects_source_or_observed_timestamp_more_than_250ms_in_future(self):
        for field in ("sourceTimestampMs", "observedAtMs"):
            p = valid_payload(); p[field] = NOW_MS + 251
            self.reject(p)

    def test_uses_one_fixed_evaluation_time_for_all_freshness_checks(self):
        p = valid_payload()
        p["sourceTimestampMs"] = NOW_MS - 2000
        p["observedAtMs"] = NOW_MS - 2000
        p["snapshotId"] = ""
        unsigned = dict(p); unsigned.pop("snapshotId")
        p["snapshotId"] = "sha256:" + hashlib.sha256(_canonical_bytes(unsigned)).hexdigest()
        self.assertEqual(self.accept(p).symbol, "BTCUSDT")

    def test_rejects_snapshot_digest_mismatch(self):
        p = valid_payload(); p["bids"][0][1] = "9.5"
        self.reject(p, ErrorCode.DIGEST_MISMATCH)

    def test_matches_canonical_snapshot_digest_golden_vectors(self):
        self.assertEqual(valid_payload()["snapshotId"], "sha256:7aae6cf204f5a3aaeffcdd5a2569812339187c3e19567beef8b72ecd9b18473e")
        self.assertEqual(self.accept().snapshot_id, valid_payload()["snapshotId"])

    def test_rejects_non_verified_continuity_and_non_fresh_label(self):
        for field, value in (("continuity", "UNKNOWN"), ("freshness", "STALE")):
            p = valid_payload(); p[field] = value
            self.reject(p)

    def test_rejects_wrong_depth_shape_and_non_boolean_complete(self):
        p = valid_payload(); p["depth"] = {"bids": 20}
        self.reject(p)
        p = valid_payload(); p["complete"] = 1
        self.reject(p)

    def test_returns_immutable_validated_snapshot_only_after_all_checks_pass(self):
        from dataclasses import FrozenInstanceError
        snapshot = self.accept()
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            snapshot.symbol = "ETHUSDT"

    def test_preserves_exact_decimal_text_through_dto_round_trip(self):
        p = valid_payload(); p["bids"][0][0] = "100.123456789012345678"
        p["snapshotId"] = ""
        unsigned = dict(p); unsigned.pop("snapshotId")
        p["snapshotId"] = "sha256:" + hashlib.sha256(_canonical_bytes(unsigned)).hexdigest()
        self.assertEqual(self.accept(p).bids[0][0], "100.123456789012345678")

    def test_rejects_non_bytes_input_and_missing_evaluation_time(self):
        with self.assertRaises(ContractError):
            validate_payload(None, now_ms=NOW_MS)
        with self.assertRaises((TypeError, ValueError)):
            validate_payload(encode(valid_payload()), now_ms=None)

    def test_adapter_returns_typed_unavailable_without_payload(self):
        result = consume_payload(None, now_ms=NOW_MS)
        self.assertEqual(result, Unavailable())

    def test_adapter_returns_typed_rejection_for_invalid_payload(self):
        result = consume_payload(b"not-json", now_ms=NOW_MS)
        self.assertIsInstance(result, Rejected)
        self.assertEqual(result.code, ErrorCode.MALFORMED_JSON.value)

    def test_adapter_returns_validated_snapshot_for_valid_payload(self):
        result = consume_payload(encode(valid_payload()), now_ms=NOW_MS)
        self.assertEqual(result.symbol, "BTCUSDT")


if __name__ == "__main__":
    unittest.main()
