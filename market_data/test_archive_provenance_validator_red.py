"""S2 synthetic-only RED contract for the archive provenance validator.

No archive, network, SQLite, importer or Canonical T0 access.
Expected future API: encode_t0enc1, derive_attempt_id, validate_provenance.
"""
import importlib
import unittest

MODULE = "market_data.archive_provenance_validator"


class ProvenanceValidatorRedTest(unittest.TestCase):
    def setUp(self):
        # Intentionally absent until a separately approved GREEN increment.
        self.validator = importlib.import_module(MODULE)

    def test_t0enc1_frames_domain_and_fields(self):
        encode = self.validator.encode_t0enc1
        self.assertNotEqual(encode("D", "ab", "c"), encode("D", "a", "bc"))
        self.assertTrue(encode("D", "x").startswith(b"T0ENC1\x00"))

    def test_t0enc1_distinguishes_null_and_empty(self):
        encode = self.validator.encode_t0enc1
        self.assertNotEqual(encode("D", None), encode("D", ""))

    def test_attempt_id_is_deterministic_and_attempt_scoped(self):
        derive = self.validator.derive_attempt_id
        args = dict(object_id="obj1:" + "01" * 32, attempt_number=1,
                    workflow_run_id="run-1", workflow_job_id="job-1",
                    trigger_sha="22" * 20, requested_key="data/example.zip")
        first = derive(**args)
        self.assertEqual(first, derive(**args))
        self.assertRegex(first, r"^att1:[0-9a-f]{64}$")
        self.assertNotEqual(first, derive(**{**args, "attempt_number": 2}))

    def test_missing_inventory_objects_fail_closed(self):
        result = self.validator.validate_provenance({
            "inventory": {"inventory_id": "synthetic-inventory", "objects": []},
            "objects": [], "pairs": [], "members": [], "attempts": [],
            "source_rows": [], "candles": [], "links": [],
        })
        self.assertFalse(result.valid)
        self.assertIn("INVENTORY_OBJECT_SET_INCOMPLETE", result.error_codes)

    def test_object_requested_key_must_match_allowlisted_key(self):
        result = self.validator.validate_provenance({
            "inventory": {"objects": [{"object_key": "approved.zip", "object_kind": "ZIP"}]},
            "objects": [{"object_key": "other.zip", "requested_key": "other.zip",
                         "object_kind": "ZIP", "verification_status": "VERIFIED"}],
            "pairs": [], "members": [], "attempts": [], "source_rows": [],
            "candles": [], "links": [],
        })
        self.assertFalse(result.valid)
        self.assertIn("OBJECT_NOT_IN_APPROVED_INVENTORY", result.error_codes)

    def test_quarantined_object_can_preserve_incomplete_measurements(self):
        result = self.validator.validate_provenance({
            "inventory": {"objects": []},
            "objects": [{"object_key": "failed.zip", "requested_key": "failed.zip",
                         "verification_status": "QUARANTINED",
                         "measured_size_bytes": None, "measured_sha256": None,
                         "response_bytes_total": 128, "response_status": 503,
                         "local_relative_path": None, "exclusive_create": None,
                         "failure_code": "HTTP_FAILED"}],
            "pairs": [], "members": [], "attempts": [], "source_rows": [],
            "candles": [], "links": [],
        })
        self.assertFalse(result.valid)
        self.assertIn("QUARANTINED_EVIDENCE_PRESENT", result.error_codes)

    def test_unknown_attempt_is_not_a_successful_transfer(self):
        result = self.validator.validate_provenance({
            "inventory": {"objects": []}, "objects": [], "pairs": [], "members": [],
            "attempts": [{"outcome": "UNKNOWN", "response_bytes_received": 64,
                          "is_complete_object": 0, "partial_body_sha256": "44" * 32,
                          "complete_object_sha256": None}],
            "source_rows": [], "candles": [], "links": [],
        })
        self.assertFalse(result.valid)
        self.assertIn("ATTEMPT_OUTCOME_UNKNOWN", result.error_codes)

    def test_transferred_attempt_requires_complete_object_digest(self):
        result = self.validator.validate_provenance({
            "inventory": {"objects": []}, "objects": [], "pairs": [], "members": [],
            "attempts": [{"outcome": "TRANSFERRED", "response_bytes_received": 64,
                          "is_complete_object": 1, "partial_body_sha256": "44" * 32,
                          "complete_object_sha256": None}],
            "source_rows": [], "candles": [], "links": [],
        })
        self.assertFalse(result.valid)
        self.assertIn("TRANSFERRED_ATTEMPT_INCOMPLETE", result.error_codes)

    def test_verified_pair_requires_exactly_one_verified_csv_member(self):
        result = self.validator.validate_provenance({
            "inventory": {"objects": []}, "objects": [],
            "pairs": [{"disposition": "VERIFIED", "member_count": 0}],
            "members": [], "attempts": [], "source_rows": [], "candles": [], "links": [],
        })
        self.assertFalse(result.valid)
        self.assertIn("VERIFIED_PAIR_MEMBER_CARDINALITY_INVALID", result.error_codes)

    def test_accepted_source_row_requires_matching_provenance_link(self):
        result = self.validator.validate_provenance({
            "inventory": {"objects": []}, "objects": [], "pairs": [], "members": [],
            "attempts": [],
            "source_rows": [{"disposition": "ACCEPTED", "source_row_id": "row1:" + "11" * 32,
                             "raw_fields": ["x"] * 12, "raw_row_digest": "22" * 32}],
            "candles": [], "links": [],
        })
        self.assertFalse(result.valid)
        self.assertIn("ACCEPTED_SOURCE_ROW_LINK_CARDINALITY_INVALID", result.error_codes)

    def test_conflicting_values_for_one_candle_identity_quarantine(self):
        result = self.validator.validate_provenance({
            "inventory": {"objects": []}, "objects": [], "pairs": [], "members": [],
            "attempts": [], "source_rows": [],
            "candles": [
                {"natural_key": ["binance", "usdm", "BTCUSDT", "15m", 1000],
                 "candle_value_id": "cv1:" + "11" * 32},
                {"natural_key": ["binance", "usdm", "BTCUSDT", "15m", 1000],
                 "candle_value_id": "cv1:" + "22" * 32},
            ],
            "links": [],
        })
        self.assertFalse(result.valid)
        self.assertIn("CANDLE_IDENTITY_VALUE_CONFLICT", result.error_codes)

    def test_bar_close_boundary_uses_exclusive_interval_end(self):
        result = self.validator.validate_provenance({
            "inventory": {"objects": []}, "objects": [], "pairs": [], "members": [],
            "attempts": [], "source_rows": [],
            "candles": [{"exchange": "binance", "market_type": "usdm",
                         "symbol": "BTCUSDT", "timeframe": "15m",
                         "open_time_ms": 1767225600000,
                         "available_at_ms": 1767226499999,
                         "availability_kind": "BAR_CLOSE_BOUNDARY"}],
            "links": [],
        })
        self.assertFalse(result.valid)
        self.assertIn("CANDLE_AVAILABILITY_BOUNDARY_INVALID", result.error_codes)


if __name__ == "__main__":
    unittest.main()
