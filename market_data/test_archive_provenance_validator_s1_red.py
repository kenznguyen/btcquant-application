"""Deterministic synthetic S1 fixture and RED contract tests.

No archive files, filesystem, SQLite, network, Canonical T0, or runtime access.
The positive fixture check validates fixture construction independently of the
not-yet-implemented S1 validator extension. The eleven negative tests each
introduce one S1 defect and require its dedicated stable error code.
"""
from __future__ import annotations

import copy
import hashlib
import json
import unittest
from typing import Any

from market_data.archive_provenance_validator import (
    derive_attempt_id,
    encode_t0enc1,
    validate_provenance,
)

_INVENTORY_ID = "synthetic-s1-inventory-v1"
_RUN_ID = "synthetic-s1-run-v1"
_PARSER_SHA = "a" * 40
_IMPORTER_SHA = "d" * 40
_TRIGGER_SHA = "b" * 40
_CHECKOUT_SHA = "c" * 40
_ROW_COUNT = 202
_ZIP_BYTES = b"synthetic deterministic zip evidence"
_SIDECAR_BYTES = b"synthetic deterministic checksum sidecar"
_CSV_HEADER = "open_time,open,high,low,close,volume,close_time,quote_volume,trade_count,taker_buy_base,taker_buy_quote,ignore\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _enc_digest(domain: str, *fields: object) -> str:
    return hashlib.sha256(encode_t0enc1(domain, *fields)).hexdigest()


def _object_id(inventory_sha: str, key: str, kind: str) -> str:
    return "obj1:" + _enc_digest(
        "T0-ARCHIVE-OBJECT-V1", inventory_sha, key, kind
    )


def _attempt_id(object_id: str, key: str) -> str:
    return derive_attempt_id(
        object_id=object_id,
        attempt_number=1,
        workflow_run_id="run-1001",
        workflow_job_id="job-2001",
        trigger_sha=_TRIGGER_SHA,
        requested_key=key,
    )


def _decimal(value: int) -> str:
    return str(value)


def _refresh_candle_value_id(candle: dict[str, Any]) -> None:
    fields = (
        candle["exchange"], candle["market_type"], candle["symbol"],
        candle["timeframe"], candle["open_time_ms"], candle["open"],
        candle["high"], candle["low"], candle["close"], candle["volume"],
        candle["available_at_ms"], candle["availability_kind"],
    )
    candle["candle_value_id"] = "cv1:" + _enc_digest("T0-CANDLE-VALUE-V1", *fields)


def _sync_candle_value_id(payload: dict[str, Any], index: int) -> None:
    value_id = payload["candles"][index]["candle_value_id"]
    payload["source_rows"][index]["candle_value_id"] = value_id
    payload["links"][index]["candle_value_id"] = value_id


def _refresh_link_id(link: dict[str, Any]) -> None:
    link["link_id"] = "lnk1:" + _enc_digest(
        "T0-CANDLE-PROVENANCE-LINK-V1",
        link["exchange"], link["market_type"], link["symbol"],
        link["timeframe"], link["open_time_ms"], link["source_row_id"],
        link["duplicate_disposition"],
    )


def _refresh_source_row_identity(payload: dict[str, Any], index: int) -> None:
    row = payload["source_rows"][index]
    row["source_row_id"] = "row1:" + _enc_digest(
        "T0-SOURCE-ROW-V1", row["member_id"], row["physical_record_ordinal"],
        bytes.fromhex(row["raw_row_digest"]),
    )
    link = payload["links"][index]
    link["source_row_id"] = row["source_row_id"]
    _refresh_link_id(link)


def _sync_raw_row_and_member(payload: dict[str, Any], index: int) -> None:
    row = payload["source_rows"][index]
    candle = payload["candles"][index]
    raw_fields = [
        str(candle["open_time_ms"]), candle["open"], candle["high"], candle["low"],
        candle["close"], candle["volume"], str(candle["open_time_ms"] + 899999),
        "0", "0", "0", "0", "0",
    ]
    row["raw_fields"] = raw_fields
    row["raw_fields_json"] = json.dumps(raw_fields, ensure_ascii=False, separators=(",", ":"))
    row["raw_row_digest"] = _enc_digest("T0-RAW-CSV-ROW-V1", *raw_fields)
    member = next(item for item in payload["members"] if item["member_id"] == row["member_id"])
    member_bytes = _CSV_HEADER.encode("utf-8") + (",".join(raw_fields) + "\n").encode("utf-8")
    member["member_size_bytes"] = len(member_bytes)
    member["member_sha256"] = _sha(member_bytes)
    member["member_id"] = "mem1:" + _enc_digest(
        "T0-CSV-MEMBER-V1", member["pair_id"], member["member_path"],
        bytes.fromhex(member["member_sha256"]),
    )
    row["member_id"] = member["member_id"]
    _refresh_source_row_identity(payload, index)


def _renumber_attempt_and_reference(payload: dict[str, Any], index: int, number: int) -> None:
    attempt = payload["attempts"][index]
    obj = next(item for item in payload["objects"] if item["object_id"] == attempt["object_id"])
    attempt["attempt_number"] = number
    attempt["attempt_id"] = derive_attempt_id(
        object_id=attempt["object_id"], attempt_number=number,
        workflow_run_id=attempt["workflow_run_id"],
        workflow_job_id=attempt["workflow_job_id"],
        trigger_sha=attempt["trigger_sha"], requested_key=attempt["requested_key"],
    )
    obj["successful_attempt_id"] = attempt["attempt_id"]


def build_valid_s1_fixture() -> dict[str, Any]:
    """Build 404 objects, 202 pairs/members/rows/candles/links and 404 attempts."""
    inventory_entries: list[dict[str, str]] = []
    for index in range(_ROW_COUNT):
        zip_key = f"synthetic/btcusdt/15m/{index:03d}.zip"
        sidecar_key = zip_key + ".CHECKSUM"
        inventory_entries.extend((
            {"object_key": zip_key, "object_kind": "ZIP",
             "paired_object_key": sidecar_key, "timeframe": "15m",
             "partition": "synthetic", "period": f"{index:03d}"},
            {"object_key": sidecar_key, "object_kind": "CHECKSUM_SIDECAR",
             "paired_object_key": zip_key, "timeframe": "15m",
             "partition": "synthetic", "period": f"{index:03d}"},
        ))
    inventory_entries.sort(key=lambda item: item["object_key"].encode("utf-8"))
    raw_inventory = json.dumps(
        {"inventory_id": _INVENTORY_ID, "objects": inventory_entries},
        ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    inventory_sha = _sha(raw_inventory)

    objects: list[dict[str, Any]] = []
    attempts: list[dict[str, Any]] = []
    pairs: list[dict[str, Any]] = []
    members: list[dict[str, Any]] = []
    source_rows: list[dict[str, Any]] = []
    candles: list[dict[str, Any]] = []
    links: list[dict[str, Any]] = []

    for index in range(_ROW_COUNT):
        zip_key = f"synthetic/btcusdt/15m/{index:03d}.zip"
        sidecar_key = zip_key + ".CHECKSUM"
        zip_sha, sidecar_sha = _sha(_ZIP_BYTES), _sha(_SIDECAR_BYTES)
        zip_id = _object_id(inventory_sha, zip_key, "ZIP")
        sidecar_id = _object_id(inventory_sha, sidecar_key, "CHECKSUM_SIDECAR")
        pair_id = "pair1:" + _enc_digest(
            "T0-ARCHIVE-PAIR-V1", zip_id, sidecar_id
        )
        open_time = 1767225600000 + index * 900000
        open_value = _decimal(10000 + index)
        high_value = _decimal(10002 + index)
        low_value = _decimal(9999 + index)
        close_value = _decimal(10001 + index)
        volume_value = "1"
        available_at = open_time + 900000
        raw_fields = [
            str(open_time), open_value, high_value, low_value, close_value,
            volume_value, str(available_at - 1), "0", "0", "0", "0", "0",
        ]
        member_path = f"data/BTCUSDT-15m-{index:03d}.csv"
        member_bytes = _CSV_HEADER.encode("utf-8") + (",".join(raw_fields) + "\n").encode("utf-8")
        member_sha = _sha(member_bytes)
        member_id = "mem1:" + _enc_digest(
            "T0-CSV-MEMBER-V1", pair_id, member_path, bytes.fromhex(member_sha)
        )

        for key, kind, object_id, body, digest in (
            (zip_key, "ZIP", zip_id, _ZIP_BYTES, zip_sha),
            (sidecar_key, "CHECKSUM_SIDECAR", sidecar_id, _SIDECAR_BYTES, sidecar_sha),
        ):
            attempt_id = _attempt_id(object_id, key)
            objects.append({
                "object_id": object_id, "inventory_id": _INVENTORY_ID,
                "inventory_blob_sha256": inventory_sha,
                "inventory_entry_identity": key, "object_key": key,
                "object_kind": kind, "timeframe": "15m",
                "partition": "synthetic", "period": f"{index:03d}",
                "paired_object_key": sidecar_key if kind == "ZIP" else zip_key,
                "expected_size_bytes": len(body), "expected_sha256": digest,
                "measured_size_bytes": len(body), "measured_sha256": digest,
                "retrieval_source": "SYNTHETIC_FIXTURE",
                "requested_key": key, "workflow_run_id": "run-1001",
                "workflow_job_id": "job-2001", "workflow_event": "workflow_dispatch",
                "trigger_sha": _TRIGGER_SHA, "checkout_sha": _CHECKOUT_SHA,
                "attempt_count": 1, "retrieved_at_utc": "2026-11-22T00:00:00.000Z",
                "response_bytes_total": len(body), "response_status": 200,
                "local_relative_path": f"synthetic/{index:03d}/{kind.lower()}",
                "exclusive_create": 1, "verification_status": "VERIFIED",
                "successful_attempt_id": attempt_id, "failure_code": None,
                "failure_detail_code": None,
            })
            attempts.append({
                "attempt_id": attempt_id, "object_id": object_id,
                "attempt_number": 1, "requested_key": key,
                "workflow_run_id": "run-1001", "workflow_job_id": "job-2001",
                "workflow_event": "workflow_dispatch", "trigger_sha": _TRIGGER_SHA,
                "checkout_sha": _CHECKOUT_SHA,
                "started_at_utc": "2026-11-22T00:00:00.000Z",
                "finished_at_utc": "2026-11-22T00:00:01.000Z",
                "outcome": "TRANSFERRED", "response_status": 200,
                "response_bytes_received": len(body), "is_complete_object": 1,
                "partial_body_sha256": None, "complete_object_sha256": digest,
                "expected_size_bytes": len(body), "expected_sha256": digest,
                "failure_code": None,
            })

        pairs.append({
            "pair_id": pair_id, "zip_object_id": zip_id,
            "sidecar_object_id": sidecar_id,
            "measured_zip_size_bytes": len(_ZIP_BYTES),
            "measured_zip_sha256": zip_sha,
            "measured_sidecar_size_bytes": len(_SIDECAR_BYTES),
            "measured_sidecar_sha256": sidecar_sha,
            "sidecar_asserted_zip_sha256": zip_sha,
            "sidecar_assertion_matches": 1, "zip_crc_ok": 1,
            "member_count": 1, "structural_ok": 1, "disposition": "VERIFIED",
            "failure_code": None,
        })
        members.append({
            "member_id": member_id, "pair_id": pair_id,
            "member_path": member_path, "member_size_bytes": len(member_bytes),
            "member_sha256": member_sha, "encoding": "UTF-8",
            "bom_present": 0, "newline": "LF", "delimiter": ",",
            "header_present": 1, "header_contract_id": "T0_ARCHIVE_CSV_HEADER_V1",
            "parser_contract_id": "T0_ARCHIVE_CSV_HEADER_V1",
            "parser_source_sha": _PARSER_SHA, "data_row_count": 1,
            "first_open_time_ms": 1767225600000 + index * 900000,
            "last_open_time_ms": 1767225600000 + index * 900000,
            "disposition": "VERIFIED", "failure_code": None,
        })

        raw_digest = _enc_digest("T0-RAW-CSV-ROW-V1", *raw_fields)
        source_row_id = "row1:" + _enc_digest(
            "T0-SOURCE-ROW-V1", member_id, 2, bytes.fromhex(raw_digest)
        )
        value_fields = (
            "binance", "usdm", "BTCUSDT", "15m", open_time,
            open_value, high_value, low_value, close_value, volume_value,
            available_at, "BAR_CLOSE_BOUNDARY",
        )
        candle_value_id = "cv1:" + _enc_digest("T0-CANDLE-VALUE-V1", *value_fields)
        natural_key = ("binance", "usdm", "BTCUSDT", "15m", open_time)
        source_rows.append({
            "source_row_id": source_row_id, "member_id": member_id,
            "physical_record_ordinal": 2, "data_row_ordinal": 1,
            "raw_fields": raw_fields,
            "raw_fields_json": json.dumps(raw_fields, ensure_ascii=False, separators=(",", ":")),
            "raw_row_digest": raw_digest,
            "parser_contract_id": "T0_ARCHIVE_CSV_HEADER_V1",
            "parser_source_sha": _PARSER_SHA,
            "importer_contract_id": "T0_ARCHIVE_IMPORTER_V1",
            "importer_source_sha": _IMPORTER_SHA,
            "natural_key": natural_key, "candle_value_id": candle_value_id,
            "disposition": "ACCEPTED", "rejection_code": None,
        })
        candles.append({
            "exchange": "binance", "market_type": "usdm", "symbol": "BTCUSDT",
            "timeframe": "15m", "open_time_ms": open_time,
            "open": open_value, "high": high_value, "low": low_value,
            "close": close_value, "volume": volume_value,
            "available_at_ms": available_at,
            "availability_kind": "BAR_CLOSE_BOUNDARY",
            "candle_value_id": candle_value_id,
        })
        duplicate_disposition = "UNIQUE"
        link_id = "lnk1:" + _enc_digest(
            "T0-CANDLE-PROVENANCE-LINK-V1",
            "binance", "usdm", "BTCUSDT", "15m", open_time,
            source_row_id, duplicate_disposition,
        )
        links.append({
            "link_id": link_id, "exchange": "binance", "market_type": "usdm",
            "symbol": "BTCUSDT", "timeframe": "15m", "open_time_ms": open_time,
            "source_row_id": source_row_id, "candle_value_id": candle_value_id,
            "duplicate_disposition": duplicate_disposition,
            "natural_key": natural_key,
        })

    return {
        "contract_version": "T0_PROVENANCE_VALIDATOR_S1_V1",
        "inventory": {"inventory_id": _INVENTORY_ID, "objects": inventory_entries},
        "inventory_raw_bytes": raw_inventory,
        "inventory_expected_sha256": inventory_sha,
        "inventory_expected_id": _INVENTORY_ID,
        "coverage_manifest": {
            "manifest_version": "T0-COVERAGE-MANIFEST-V1",
            "approved_gaps": [], "approved_extras": [],
            "expected_object_count": 404, "expected_pair_count": 202,
            "expected_member_count": 202, "expected_row_count": 202,
            "expected_candle_count": 202, "expected_link_count": 202,
        },
        "run": {
            "run_id": _RUN_ID, "status": "CANDIDATE",
            "schema_contract_id": "T0_STAGING_SCHEMA_V2",
        },
        "objects": objects, "pairs": pairs, "members": members,
        "attempts": attempts, "source_rows": source_rows,
        "candles": candles, "links": links,
    }


def assert_valid_fixture_shape(test: unittest.TestCase, payload: dict[str, Any]) -> None:
    """Check deterministic fixture completeness without calling the S1 validator."""
    test.assertEqual(payload["contract_version"], "T0_PROVENANCE_VALIDATOR_S1_V1")
    test.assertEqual(hashlib.sha256(payload["inventory_raw_bytes"]).hexdigest(),
                     payload["inventory_expected_sha256"])
    parsed_inventory = json.loads(payload["inventory_raw_bytes"].decode("utf-8"))
    test.assertEqual(parsed_inventory["inventory_id"], payload["inventory_expected_id"])
    test.assertEqual(parsed_inventory["objects"], payload["inventory"]["objects"])
    test.assertEqual(payload["coverage_manifest"]["manifest_version"], "T0-COVERAGE-MANIFEST-V1")
    test.assertEqual(payload["coverage_manifest"]["expected_object_count"], 404)
    test.assertEqual(payload["coverage_manifest"]["expected_pair_count"], 202)
    test.assertEqual(payload["coverage_manifest"]["expected_member_count"], 202)
    test.assertEqual(payload["coverage_manifest"]["expected_row_count"], 202)
    test.assertEqual(payload["coverage_manifest"]["expected_candle_count"], 202)
    test.assertEqual(payload["coverage_manifest"]["expected_link_count"], 202)
    test.assertEqual(payload["run"]["status"], "CANDIDATE")
    test.assertEqual(payload["run"]["schema_contract_id"], "T0_STAGING_SCHEMA_V2")
    test.assertEqual(len(payload["inventory"]["objects"]), 404)
    test.assertEqual(len(payload["objects"]), 404)
    test.assertEqual(len(payload["attempts"]), 404)
    test.assertEqual(len(payload["pairs"]), 202)
    test.assertEqual(len(payload["members"]), 202)
    test.assertEqual(len(payload["source_rows"]), 202)
    test.assertEqual(len(payload["candles"]), 202)
    test.assertEqual(len(payload["links"]), 202)
    test.assertEqual(len({item["object_id"] for item in payload["objects"]}), 404)
    test.assertEqual(len({item["pair_id"] for item in payload["pairs"]}), 202)
    test.assertEqual(len({item["member_id"] for item in payload["members"]}), 202)
    test.assertEqual(len({item["source_row_id"] for item in payload["source_rows"]}), 202)
    test.assertEqual(len({item["link_id"] for item in payload["links"]}), 202)
    test.assertEqual(len({item["attempt_id"] for item in payload["attempts"]}), 404)
    object_by_id = {item["object_id"]: item for item in payload["objects"]}
    attempt_by_id = {item["attempt_id"]: item for item in payload["attempts"]}
    pair_by_id = {item["pair_id"]: item for item in payload["pairs"]}
    member_by_id = {item["member_id"]: item for item in payload["members"]}
    candle_by_value = {item["candle_value_id"]: item for item in payload["candles"]}
    for obj in payload["objects"]:
        test.assertEqual(
            obj["object_id"],
            _object_id(payload["inventory_expected_sha256"], obj["object_key"], obj["object_kind"]),
        )
        test.assertEqual(obj["expected_size_bytes"], obj["measured_size_bytes"])
        test.assertEqual(obj["expected_sha256"], obj["measured_sha256"])
        test.assertEqual(obj["response_status"], 200)
        test.assertEqual(obj["response_bytes_total"], obj["measured_size_bytes"])
        test.assertEqual(obj["attempt_count"], 1)
        test.assertEqual(obj["exclusive_create"], 1)
        test.assertTrue(obj["local_relative_path"])
        attempt = attempt_by_id[obj["successful_attempt_id"]]
        test.assertEqual(attempt["attempt_id"], _attempt_id(obj["object_id"], obj["requested_key"]))
        test.assertEqual(attempt["object_id"], obj["object_id"])
        test.assertEqual(attempt["outcome"], "TRANSFERRED")
        test.assertEqual(attempt["complete_object_sha256"], obj["measured_sha256"])
        test.assertEqual(attempt["response_bytes_received"], obj["measured_size_bytes"])
        test.assertEqual(attempt["expected_size_bytes"], obj["expected_size_bytes"])
        test.assertEqual(attempt["expected_sha256"], obj["expected_sha256"])
    for pair in payload["pairs"]:
        test.assertEqual(
            pair["pair_id"],
            "pair1:" + _enc_digest("T0-ARCHIVE-PAIR-V1", pair["zip_object_id"], pair["sidecar_object_id"]),
        )
        test.assertEqual(pair["member_count"], 1)
        test.assertEqual(pair["zip_crc_ok"], 1)
        test.assertEqual(pair["structural_ok"], 1)
        test.assertEqual(object_by_id[pair["zip_object_id"]]["verification_status"], "VERIFIED")
        test.assertEqual(object_by_id[pair["sidecar_object_id"]]["verification_status"], "VERIFIED")
        test.assertEqual(
            object_by_id[pair["zip_object_id"]]["paired_object_key"],
            object_by_id[pair["sidecar_object_id"]]["object_key"],
        )
        test.assertEqual(
            object_by_id[pair["sidecar_object_id"]]["paired_object_key"],
            object_by_id[pair["zip_object_id"]]["object_key"],
        )
        test.assertEqual(pair["sidecar_asserted_zip_sha256"], pair["measured_zip_sha256"])
    for member in payload["members"]:
        test.assertIn(member["pair_id"], pair_by_id)
        source_row = next(row for row in payload["source_rows"] if row["member_id"] == member["member_id"])
        member_bytes = _CSV_HEADER.encode("utf-8") + (",".join(source_row["raw_fields"]) + "\n").encode("utf-8")
        test.assertEqual(member["member_size_bytes"], len(member_bytes))
        test.assertEqual(member["member_sha256"], _sha(member_bytes))
        test.assertEqual(
            member["member_id"],
            "mem1:" + _enc_digest(
                "T0-CSV-MEMBER-V1", member["pair_id"], member["member_path"],
                bytes.fromhex(member["member_sha256"]),
            ),
        )
        test.assertEqual(member["encoding"], "UTF-8")
        test.assertEqual(member["bom_present"], 0)
        test.assertEqual(member["newline"], "LF")
        test.assertEqual(member["delimiter"], ",")
        test.assertEqual(member["header_present"], 1)
        test.assertRegex(member["parser_source_sha"], r"^[0-9a-f]{40}$")
        test.assertEqual(member["disposition"], "VERIFIED")
        test.assertEqual(member["data_row_count"], 1)
    for row, link in zip(payload["source_rows"], payload["links"]):
        test.assertIn(row["member_id"], member_by_id)
        test.assertEqual(link["source_row_id"], row["source_row_id"])
        test.assertEqual(
            link["link_id"],
            "lnk1:" + _enc_digest(
                "T0-CANDLE-PROVENANCE-LINK-V1",
                link["exchange"], link["market_type"], link["symbol"],
                link["timeframe"], link["open_time_ms"], link["source_row_id"],
                link["duplicate_disposition"],
            ),
        )
        test.assertEqual(link["duplicate_disposition"], "UNIQUE")
        test.assertEqual(link["natural_key"], row["natural_key"])
        test.assertEqual(link["candle_value_id"], row["candle_value_id"])
        test.assertIn(row["candle_value_id"], candle_by_value)
        candle = candle_by_value[row["candle_value_id"]]
        test.assertEqual(row["natural_key"], (
            candle["exchange"], candle["market_type"], candle["symbol"],
            candle["timeframe"], candle["open_time_ms"],
        ))
        test.assertEqual(row["raw_fields"][6], str(candle["available_at_ms"] - 1))
        test.assertEqual(row["disposition"], "ACCEPTED")
        test.assertEqual(len(row["raw_fields"]), 12)
        test.assertEqual(row["physical_record_ordinal"], row["data_row_ordinal"] + 1)
        test.assertEqual(row["raw_fields_json"], json.dumps(row["raw_fields"], ensure_ascii=False, separators=(",", ":")))
        test.assertEqual(row["raw_row_digest"], _enc_digest("T0-RAW-CSV-ROW-V1", *row["raw_fields"]))
        test.assertEqual(
            row["source_row_id"],
            "row1:" + _enc_digest(
                "T0-SOURCE-ROW-V1", row["member_id"], row["physical_record_ordinal"],
                bytes.fromhex(row["raw_row_digest"]),
            ),
        )
        test.assertRegex(row["parser_source_sha"], r"^[0-9a-f]{40}$")
        test.assertRegex(row["importer_source_sha"], r"^[0-9a-f]{40}$")
        test.assertTrue(row["importer_contract_id"])
    for candle in payload["candles"]:
        test.assertEqual(candle["available_at_ms"], candle["open_time_ms"] + 900000)
        test.assertEqual(candle["availability_kind"], "BAR_CLOSE_BOUNDARY")
        value_fields = (
            candle["exchange"], candle["market_type"], candle["symbol"],
            candle["timeframe"], candle["open_time_ms"], candle["open"],
            candle["high"], candle["low"], candle["close"], candle["volume"],
            candle["available_at_ms"], candle["availability_kind"],
        )
        expected_value_id = "cv1:" + _enc_digest("T0-CANDLE-VALUE-V1", *value_fields)
        test.assertEqual(candle["candle_value_id"], expected_value_id)


class ProvenanceValidatorS1RedTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = build_valid_s1_fixture()
        assert_valid_fixture_shape(self, self.payload)

    def assert_s1_error(
        self, code: str, *, legacy_codes: tuple[str, ...] = (),
    ) -> None:
        result = validate_provenance(self.payload)
        self.assertFalse(result.valid)
        # V1 diagnostics retain their order; S3 diagnostics follow the V1 catalogue.
        # A failed local invariant may additionally invalidate global run acceptance.
        expected = legacy_codes + (code,)
        if code != "RUN_ACCEPTANCE_INVARIANT_INVALID":
            expected += ("RUN_ACCEPTANCE_INVARIANT_INVALID",)
        self.assertEqual(
            tuple(item for item in result.error_codes if item in expected),
            expected,
        )
        allowed = set(expected)
        if code != "RUN_ACCEPTANCE_INVARIANT_INVALID":
            allowed.add("RUN_ACCEPTANCE_INVARIANT_INVALID")
        self.assertTrue(set(result.error_codes).issubset(allowed))

    def test_complete_s1_fixture_is_deterministic_and_structurally_valid(self) -> None:
        second = build_valid_s1_fixture()
        self.assertEqual(self.payload, second)
        assert_valid_fixture_shape(self, second)
        self.assertEqual(self.payload["inventory_expected_sha256"],
                         hashlib.sha256(self.payload["inventory_raw_bytes"]).hexdigest())

    def test_inventory_raw_bytes_invalid_isolated(self) -> None:
        self.payload["inventory_raw_bytes"] = b"\xff"
        self.payload["inventory_expected_sha256"] = hashlib.sha256(b"\xff").hexdigest()
        self.assert_s1_error("INVENTORY_RAW_BYTES_INVALID")

    def test_inventory_object_set_mismatch_isolated(self) -> None:
        self.payload["inventory"]["objects"].pop()
        self.assert_s1_error(
            "INVENTORY_OBJECT_SET_MISMATCH",
            legacy_codes=("INVENTORY_OBJECT_SET_INCOMPLETE", "OBJECT_NOT_IN_APPROVED_INVENTORY"),
        )

    def test_object_measurement_invalid_isolated(self) -> None:
        # Isolate HTTP response validity; measured bytes and successful attempt stay aligned.
        self.payload["objects"][0]["response_status"] = 302
        self.assert_s1_error("OBJECT_MEASUREMENT_INVALID")

    def test_object_attempt_history_invalid_isolated(self) -> None:
        # Keep the ID and successful-attempt pointer internally valid; only sequence
        # contiguity is broken because the sole attempt begins at ordinal 2.
        _renumber_attempt_and_reference(self.payload, 0, 2)
        self.assert_s1_error("OBJECT_ATTEMPT_HISTORY_INVALID")

    def test_archive_pair_evidence_invalid_isolated(self) -> None:
        # Isolate CRC evidence; sidecar assertion and measured hashes remain aligned.
        self.payload["pairs"][0]["zip_crc_ok"] = 0
        self.assert_s1_error("ARCHIVE_PAIR_EVIDENCE_INVALID")

    def test_csv_member_evidence_invalid_isolated(self) -> None:
        self.payload["members"][0]["parser_source_sha"] = "not-a-sha"
        self.assert_s1_error("CSV_MEMBER_EVIDENCE_INVALID")

    def test_source_row_provenance_invalid_isolated(self) -> None:
        # Isolate the physical/data ordinal offset for a header-present CSV.
        self.payload["source_rows"][0]["physical_record_ordinal"] = 1
        _refresh_source_row_identity(self.payload, 0)
        self.assert_s1_error("SOURCE_ROW_PROVENANCE_INVALID")

    def test_candle_value_digest_invalid_isolated(self) -> None:
        # Propagate the forged ID through row and link so only tuple recomputation
        # can detect the mismatch.
        self.payload["candles"][0]["candle_value_id"] = "cv1:" + "0" * 64
        _sync_candle_value_id(self.payload, 0)
        self.assert_s1_error("CANDLE_VALUE_DIGEST_INVALID")

    def test_candle_ohlcv_constraint_invalid_isolated(self) -> None:
        self.payload["candles"][0]["high"] = "1"
        self.payload["candles"][0]["low"] = "2"
        _sync_raw_row_and_member(self.payload, 0)
        _refresh_candle_value_id(self.payload["candles"][0])
        _sync_candle_value_id(self.payload, 0)
        self.assert_s1_error("CANDLE_OHLCV_CONSTRAINT_INVALID")

    def test_candle_provenance_link_invalid_isolated(self) -> None:
        # Keep row/candle references connected; isolate an unsupported disposition.
        self.payload["links"][0]["duplicate_disposition"] = "UNCLASSIFIED"
        _refresh_link_id(self.payload["links"][0])
        self.assert_s1_error("CANDLE_PROVENANCE_LINK_INVALID")

    def test_run_acceptance_invariant_invalid_isolated(self) -> None:
        self.payload["run"]["schema_contract_id"] = "WRONG_SCHEMA"
        self.assert_s1_error("RUN_ACCEPTANCE_INVARIANT_INVALID")

    def test_aggregate_new_codes_are_ordered_and_deduplicated(self) -> None:
        # Disjoint records prevent one mutation from masking another.
        self.payload["inventory_expected_sha256"] = "0" * 64
        self.payload["inventory"]["objects"].pop()
        self.payload["objects"][0]["response_status"] = 302
        _renumber_attempt_and_reference(self.payload, 4, 2)
        self.payload["pairs"][3]["zip_crc_ok"] = 0
        self.payload["members"][5]["parser_source_sha"] = "invalid"
        self.payload["source_rows"][0]["physical_record_ordinal"] = 1
        _refresh_source_row_identity(self.payload, 0)

        self.payload["candles"][1]["candle_value_id"] = "cv1:" + "0" * 64
        _sync_candle_value_id(self.payload, 1)

        self.payload["candles"][2]["high"] = "1"
        self.payload["candles"][2]["low"] = "2"
        _sync_raw_row_and_member(self.payload, 2)
        _refresh_candle_value_id(self.payload["candles"][2])
        _sync_candle_value_id(self.payload, 2)

        self.payload["links"][3]["duplicate_disposition"] = "UNCLASSIFIED"
        _refresh_link_id(self.payload["links"][3])
        self.payload["run"]["schema_contract_id"] = "WRONG"

        result = validate_provenance(self.payload)
        expected_s3 = (
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
        selected = tuple(code for code in result.error_codes if code in expected_s3)
        self.assertEqual(selected, expected_s3)
        self.assertEqual(len(selected), len(set(selected)))
        self.assertEqual(
            result.error_codes,
            (
                "INVENTORY_OBJECT_SET_INCOMPLETE",
                "OBJECT_NOT_IN_APPROVED_INVENTORY",
                *expected_s3,
            ),
        )
        self.assertFalse(result.valid)


if __name__ == "__main__":
    unittest.main()
