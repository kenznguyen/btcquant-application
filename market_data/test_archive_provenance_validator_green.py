"""Synthetic-only tests for the frozen T0 provenance validator V1 contract."""
from __future__ import annotations

import copy
import unittest
from dataclasses import FrozenInstanceError

from market_data.archive_provenance_validator import (
    ProvenanceValidationResult,
    derive_attempt_id,
    encode_t0enc1,
    validate_provenance,
)


def _valid_payload() -> dict[str, object]:
    inventory_objects: list[dict[str, str]] = []
    object_evidence: list[dict[str, object]] = []
    pairs: list[dict[str, object]] = []
    members: list[dict[str, object]] = []
    for index in range(202):
        zip_key = f"synthetic/{index:03d}.zip"
        sidecar_key = f"{zip_key}.CHECKSUM"
        inventory_objects.extend((
            {"object_key": zip_key, "object_kind": "ZIP", "paired_object_key": sidecar_key},
            {"object_key": sidecar_key, "object_kind": "CHECKSUM_SIDECAR", "paired_object_key": zip_key},
        ))
        object_evidence.extend((
            {"object_key": zip_key, "requested_key": zip_key, "object_kind": "ZIP", "verification_status": "VERIFIED"},
            {"object_key": sidecar_key, "requested_key": sidecar_key, "object_kind": "CHECKSUM_SIDECAR", "verification_status": "VERIFIED"},
        ))
        pair_id = f"pair1:{index:064x}"
        pairs.append({"pair_id": pair_id, "disposition": "VERIFIED", "member_count": 1})
        members.append({"member_id": f"mem1:{index:064x}", "pair_id": pair_id, "disposition": "VERIFIED"})

    natural_key = ("binance", "usdm", "BTCUSDT", "15m", 1_767_225_600_000)
    value_id = "cv1:" + "ab" * 32
    source_row_id = "row1:" + "cd" * 32
    candle = {
        "exchange": "binance", "market_type": "usdm", "symbol": "BTCUSDT",
        "timeframe": "15m", "open_time_ms": 1_767_225_600_000,
        "open": "100", "high": "101", "low": "99", "close": "100.5",
        "volume": "10", "available_at_ms": 1_767_226_500_000,
        "availability_kind": "BAR_CLOSE_BOUNDARY", "candle_value_id": value_id,
    }
    source_row = {"source_row_id": source_row_id, "disposition": "ACCEPTED",
                  "natural_key": natural_key, "candle_value_id": value_id}
    link = {"source_row_id": source_row_id, "natural_key": natural_key,
            "candle_value_id": value_id}
    return {
        "inventory": {"inventory_id": "synthetic-inventory", "objects": inventory_objects},
        "objects": object_evidence, "pairs": pairs, "members": members,
        "attempts": [], "source_rows": [source_row], "candles": [candle], "links": [link],
    }


class ProvenanceValidatorGreenTest(unittest.TestCase):
    def test_synthetic_inventory_fixture_has_no_v1_catalogue_errors(self) -> None:
        result = validate_provenance(_valid_payload())
        self.assertEqual(result, ProvenanceValidationResult(True, ()))

    def test_input_shape_rejects_non_mapping_missing_keys_and_bad_collections(self) -> None:
        self.assertEqual(validate_provenance(None).error_codes, ("PROVENANCE_INPUT_SHAPE_INVALID",))
        payload = _valid_payload()
        del payload["links"]
        self.assertEqual(validate_provenance(payload).error_codes, ("PROVENANCE_INPUT_SHAPE_INVALID",))
        payload = _valid_payload()
        payload["attempts"] = {}
        self.assertEqual(validate_provenance(payload).error_codes, ("PROVENANCE_INPUT_SHAPE_INVALID",))
        payload = _valid_payload()
        payload["candles"] = ["not-a-mapping"]
        self.assertEqual(validate_provenance(payload).error_codes, ("PROVENANCE_INPUT_SHAPE_INVALID",))

    def test_t0enc1_matches_fixed_framing_vector(self) -> None:
        expected = (
            b"T0ENC1\x00" + (1).to_bytes(4, "big") + b"D" + (3).to_bytes(4, "big")
            + b"\x01" + (2).to_bytes(8, "big") + b"ab"
            + b"\x00" + (0).to_bytes(8, "big")
            + b"\x01" + (1).to_bytes(8, "big") + b"7"
        )
        self.assertEqual(encode_t0enc1("D", "ab", None, 7), expected)

    def test_t0enc1_rejects_invalid_domain_types_bool_and_surrogate_text(self) -> None:
        for domain in (None, b"D", ""):
            with self.subTest(domain=domain), self.assertRaises((TypeError, ValueError)):
                encode_t0enc1(domain)  # type: ignore[arg-type]
        for value in (True, 1.5, bytearray(b"x"), object()):
            with self.subTest(value=type(value).__name__), self.assertRaises(TypeError):
                encode_t0enc1("D", value)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            encode_t0enc1("\ud800")

    def test_attempt_id_changes_when_each_framed_argument_changes(self) -> None:
        args = dict(object_id="obj1:" + "01" * 32, attempt_number=1,
                    workflow_run_id="run-1", workflow_job_id="job-1",
                    trigger_sha="22" * 20, requested_key="data/example.zip")
        original = derive_attempt_id(**args)
        self.assertEqual(original, derive_attempt_id(**args))
        self.assertEqual(original, "att1:15d3ea7cd0e93dc2037b8558f1b6b645ef0869bf7dc8c39fb517a09178037bb8")
        for key, value in (("object_id", "obj1:" + "02" * 32),
                           ("attempt_number", 2), ("workflow_run_id", "run-2"),
                           ("workflow_job_id", "job-2"), ("trigger_sha", "33" * 20),
                           ("requested_key", "data/other.zip")):
            with self.subTest(field=key):
                self.assertNotEqual(original, derive_attempt_id(**{**args, key: value}))

    def test_attempt_id_rejects_bool_empty_strings_and_out_of_range_numbers(self) -> None:
        args = dict(object_id="obj", attempt_number=1, workflow_run_id="run",
                    workflow_job_id="job", trigger_sha="sha", requested_key="key")
        for value in (True, 0, -1, 2**63):
            with self.subTest(attempt_number=value), self.assertRaises((TypeError, ValueError)):
                derive_attempt_id(**{**args, "attempt_number": value})
        for key in ("object_id", "workflow_run_id", "workflow_job_id", "trigger_sha", "requested_key"):
            with self.subTest(field=key), self.assertRaises(ValueError):
                derive_attempt_id(**{**args, key: ""})

    def test_error_aggregation_is_deduplicated_ordered_and_permutation_invariant(self) -> None:
        payload = _valid_payload()
        payload["objects"][0]["verification_status"] = "QUARANTINED"  # type: ignore[index]
        payload["objects"].append({"object_key": "not-allowlisted", "requested_key": "not-allowlisted", "object_kind": "ZIP"})  # type: ignore[union-attr]
        payload["attempts"] = [
            {"outcome": "UNKNOWN"}, {"outcome": "UNKNOWN"},
            {"outcome": "TRANSFERRED", "is_complete_object": 1,
             "response_bytes_received": 5, "complete_object_sha256": None},
        ]
        payload["pairs"][0]["member_count"] = 0  # type: ignore[index]
        payload["members"] = [m for m in payload["members"] if m["pair_id"] != payload["pairs"][0]["pair_id"]]  # type: ignore[index]
        payload["links"] = []
        payload["candles"].append({  # type: ignore[union-attr]
            "natural_key": ("binance", "usdm", "BTCUSDT", "15m", 1_767_225_600_000),
            "candle_value_id": "cv1:" + "ef" * 32,
        })
        payload["candles"][0]["available_at_ms"] -= 1  # type: ignore[index]
        expected = (
            "INVENTORY_OBJECT_SET_INCOMPLETE",
            "OBJECT_NOT_IN_APPROVED_INVENTORY",
            "QUARANTINED_EVIDENCE_PRESENT",
            "ATTEMPT_OUTCOME_UNKNOWN",
            "TRANSFERRED_ATTEMPT_INCOMPLETE",
            "VERIFIED_PAIR_MEMBER_CARDINALITY_INVALID",
            "ACCEPTED_SOURCE_ROW_LINK_CARDINALITY_INVALID",
            "CANDLE_IDENTITY_VALUE_CONFLICT",
            "CANDLE_AVAILABILITY_BOUNDARY_INVALID",
        )
        result = validate_provenance(payload)
        self.assertEqual(result.error_codes, expected)
        self.assertFalse(result.valid)
        permuted = copy.deepcopy(payload)
        for key in ("objects", "pairs", "members", "attempts", "source_rows", "candles", "links"):
            permuted[key].reverse()  # type: ignore[union-attr]
        self.assertEqual(validate_provenance(permuted).error_codes, expected)
        reordered_mapping = dict(reversed(list(payload.items())))
        self.assertEqual(validate_provenance(reordered_mapping).error_codes, expected)

    def test_same_value_id_does_not_hide_conflicting_normalized_values(self) -> None:
        payload = _valid_payload()
        second = copy.deepcopy(payload["candles"][0])
        second["close"] = "100.6"
        payload["candles"].append(second)
        self.assertIn("CANDLE_IDENTITY_VALUE_CONFLICT", validate_provenance(payload).error_codes)

    def test_unhashable_semantic_fields_fail_closed_without_raising(self) -> None:
        payload = _valid_payload()
        payload["objects"][0]["object_key"] = {"unexpected": "mapping"}
        payload["pairs"][0]["pair_id"] = []
        payload["source_rows"][0]["source_row_id"] = []
        result = validate_provenance(payload)
        self.assertFalse(result.valid)
        self.assertIn("OBJECT_NOT_IN_APPROVED_INVENTORY", result.error_codes)
        self.assertIn("VERIFIED_PAIR_MEMBER_CARDINALITY_INVALID", result.error_codes)
        self.assertIn("ACCEPTED_SOURCE_ROW_LINK_CARDINALITY_INVALID", result.error_codes)

    def test_duplicate_error_sources_emit_one_code_and_result_is_immutable(self) -> None:
        payload = _valid_payload()
        payload["attempts"] = [{"outcome": "UNKNOWN"}, {"outcome": "UNKNOWN"}]
        before = copy.deepcopy(payload)
        result = validate_provenance(payload)
        self.assertEqual(result.error_codes.count("ATTEMPT_OUTCOME_UNKNOWN"), 1)
        self.assertEqual(payload, before)
        with self.assertRaises(FrozenInstanceError):
            result.valid = True  # type: ignore[misc]
        self.assertIsInstance(result.error_codes, tuple)
        with self.assertRaises(ValueError):
            ProvenanceValidationResult(False, ("ATTEMPT_OUTCOME_UNKNOWN", "ATTEMPT_OUTCOME_UNKNOWN"))
        with self.assertRaises(ValueError):
            ProvenanceValidationResult(False, ("NOT_A_V1_CODE",))
        with self.assertRaises(ValueError):
            ProvenanceValidationResult(False, ("CANDLE_AVAILABILITY_BOUNDARY_INVALID", "INVENTORY_OBJECT_SET_INCOMPLETE"))


if __name__ == "__main__":
    unittest.main()
