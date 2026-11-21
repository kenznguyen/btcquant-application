"""Synthetic-only S1 coverage RED tests for Provenance Validator S1 amendment.

These tests intentionally target the extended S1 evidence envelope. They do not
access archive bytes, files, SQLite, network, workflows, Canonical T0 or runtime.
The validator implementation is not extended by this test-only increment.
"""
from __future__ import annotations

import hashlib
import json
import unittest

from market_data.archive_provenance_validator import validate_provenance
from market_data.test_archive_provenance_validator_green import _valid_payload


def _s1_payload() -> dict[str, object]:
    payload = _valid_payload()
    inventory = payload["inventory"]
    assert isinstance(inventory, dict)
    raw_inventory = json.dumps(
        {"inventory_id": "synthetic-inventory", "objects": inventory["objects"]},
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    payload.update({
        "contract_version": "T0_PROVENANCE_VALIDATOR_S1_V1",
        "inventory_raw_bytes": raw_inventory,
        "inventory_expected_sha256": hashlib.sha256(raw_inventory).hexdigest(),
        "inventory_expected_id": "synthetic-inventory",
        "coverage_manifest": {"approved_gaps": [], "approved_extras": []},
        "run": {
            "run_id": "synthetic-run",
            "status": "CANDIDATE",
            "schema_contract_id": "T0_STAGING_SCHEMA_V2",
        },
    })
    return payload


class ProvenanceValidatorS1RedTest(unittest.TestCase):
    def assert_code(self, payload: dict[str, object], code: str) -> None:
        result = validate_provenance(payload)
        self.assertFalse(result.valid)
        self.assertIn(code, result.error_codes)

    def test_valid_s1_synthetic_envelope_is_accepted(self) -> None:
        result = validate_provenance(_s1_payload())
        self.assertTrue(result.valid, result.error_codes)
        self.assertEqual(result.error_codes, ())

    def test_inventory_raw_bytes_digest_is_pinned(self) -> None:
        payload = _s1_payload()
        payload["inventory_raw_bytes"] = b'{"inventory_id":"tampered","objects":[]}'
        self.assert_code(payload, "INVENTORY_RAW_BYTES_INVALID")

    def test_inventory_rejects_duplicate_json_keys_and_invalid_utf8(self) -> None:
        for raw in (
            b'{"inventory_id":"a","inventory_id":"b","objects":[]}',
            b'\xff\xfe',
        ):
            with self.subTest(raw=raw):
                payload = _s1_payload()
                payload["inventory_raw_bytes"] = raw
                payload["inventory_expected_sha256"] = hashlib.sha256(raw).hexdigest()
                self.assert_code(payload, "INVENTORY_RAW_BYTES_INVALID")

    def test_raw_inventory_and_supplied_inventory_entries_must_match(self) -> None:
        payload = _s1_payload()
        payload["inventory_raw_bytes"] = b'{"inventory_id":"synthetic-inventory","objects":[]}'
        payload["inventory_expected_sha256"] = hashlib.sha256(payload["inventory_raw_bytes"]).hexdigest()
        self.assert_code(payload, "INVENTORY_OBJECT_SET_MISMATCH")

    def test_verified_object_requires_complete_measured_identity(self) -> None:
        payload = _s1_payload()
        objects = payload["objects"]
        assert isinstance(objects, list)
        objects[0].update({
            "measured_size_bytes": None,
            "measured_sha256": None,
            "response_status": 200,
            "local_relative_path": "objects/example.zip",
            "exclusive_create": 1,
        })
        self.assert_code(payload, "OBJECT_MEASUREMENT_INVALID")

    def test_attempt_history_requires_contiguous_attempt_numbers_and_valid_success_reference(self) -> None:
        payload = _s1_payload()
        payload["attempts"] = [{
            "object_id": "obj1:" + "01" * 32,
            "attempt_id": "att1:" + "02" * 32,
            "attempt_number": 2,
            "outcome": "TRANSFERRED",
            "response_bytes_received": 10,
            "is_complete_object": 1,
            "complete_object_sha256": "ab" * 32,
            "finished_at_utc": "2026-11-22T00:00:00.000Z",
        }]
        self.assert_code(payload, "OBJECT_ATTEMPT_HISTORY_INVALID")

    def test_pair_requires_sidecar_assertion_crc_and_structure_evidence(self) -> None:
        payload = _s1_payload()
        pairs = payload["pairs"]
        assert isinstance(pairs, list)
        pairs[0].update({
            "zip_object_key": "synthetic/000.zip",
            "sidecar_object_key": "synthetic/000.zip.CHECKSUM",
            "sidecar_asserted_sha256": "00" * 32,
            "zip_crc_ok": 0,
            "structural_ok": 1,
            "disposition": "VERIFIED",
        })
        self.assert_code(payload, "ARCHIVE_PAIR_EVIDENCE_INVALID")

    def test_verified_member_requires_full_parser_and_header_evidence(self) -> None:
        payload = _s1_payload()
        members = payload["members"]
        assert isinstance(members, list)
        members[0].update({
            "member_path": "../unsafe.csv",
            "member_size_bytes": -1,
            "member_sha256": "invalid",
            "encoding": "latin-1",
            "delimiter": ";",
            "parser_contract_id": "unknown",
            "parser_source_sha": "not-a-sha",
            "header_present": 1,
            "header_contract_id": "unknown",
        })
        self.assert_code(payload, "CSV_MEMBER_EVIDENCE_INVALID")

    def test_source_rows_require_contiguous_ordinals_raw_fields_and_digest(self) -> None:
        payload = _s1_payload()
        rows = payload["source_rows"]
        assert isinstance(rows, list)
        rows[0].update({
            "member_id": "mem1:" + "00" * 32,
            "physical_record_ordinal": 3,
            "data_row_ordinal": 1,
            "header_present": 1,
            "raw_fields": ["only-one-field"],
            "raw_row_digest": "invalid",
            "parser_contract_id": "unknown",
            "parser_source_sha": "bad",
            "importer_source_sha": "bad",
        })
        self.assert_code(payload, "SOURCE_ROW_PROVENANCE_INVALID")

    def test_candle_value_id_must_be_recomputed_from_normalized_values(self) -> None:
        payload = _s1_payload()
        candles = payload["candles"]
        assert isinstance(candles, list)
        candles[0]["candle_value_id"] = "cv1:" + "00" * 32
        self.assert_code(payload, "CANDLE_VALUE_DIGEST_INVALID")

    def test_candle_ohlcv_and_timeframe_semantics_are_enforced(self) -> None:
        payload = _s1_payload()
        candles = payload["candles"]
        assert isinstance(candles, list)
        candles[0].update({
            "open": "NaN",
            "high": "1",
            "low": "2",
            "close": "0",
            "volume": "-1",
            "open_time_ms": 1,
            "available_at_ms": 1,
        })
        self.assert_code(payload, "CANDLE_OHLCV_CONSTRAINT_INVALID")

    def test_every_candle_and_accepted_row_requires_exact_matching_link(self) -> None:
        payload = _s1_payload()
        payload["links"] = []
        self.assert_code(payload, "CANDLE_PROVENANCE_LINK_INVALID")

    def test_global_run_acceptance_requires_exact_s1_cardinalities_and_candidate_state(self) -> None:
        payload = _s1_payload()
        payload["run"] = {
            "run_id": "synthetic-run",
            "status": "VALIDATED",
            "schema_contract_id": "wrong-schema",
        }
        self.assert_code(payload, "RUN_ACCEPTANCE_INVARIANT_INVALID")

    def test_all_new_codes_aggregate_once_in_contract_order(self) -> None:
        payload = _s1_payload()
        payload["inventory_raw_bytes"] = b'{"bad":'
        payload["inventory_expected_sha256"] = "0" * 64
        payload["coverage_manifest"] = {}
        payload["run"] = {"status": "VALIDATED", "schema_contract_id": "wrong"}
        result = validate_provenance(payload)
        expected = (
            "INVENTORY_RAW_BYTES_INVALID",
            "INVENTORY_OBJECT_SET_MISMATCH",
            "OBJECT_MEASUREMENT_INVALID",
            "OBJECT_ATTEMPT_HISTORY_INVALID",
            "ARCHIVE_PAIR_EVIDENCE_INVALID",
            "CSV_MEMBER_EVIDENCE_INVALID",
            "SOURCE_ROW_PROVENANCE_INVALID",
            "CANDLE_VALUE_DIGEST_INVALID",
            "CANDLE_OHLCV_CONSTRAINT_INVALID",
            "CANDLE_PROVENANCE_LINK_INVALID",
            "RUN_ACCEPTANCE_INVARIANT_INVALID",
        )
        self.assertFalse(result.valid)
        self.assertEqual(tuple(code for code in result.error_codes if code in expected), expected)


if __name__ == "__main__":
    unittest.main()
