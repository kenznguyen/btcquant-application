"""Synthetic-only S1.2 adapter contract tests; no archive or filesystem I/O."""
from dataclasses import FrozenInstanceError
import unittest

from market_data.archive_staging_adapter import (
    AdapterValidationError,
    AttemptRecord,
    SourceRowRecord,
    PairRecord,
    derive_object_attempt_summary,
    project_attempt_record,
    project_pair_record,
    project_source_row_record,
    validate_sqlite_integer,
)


SHA = "a" * 64
SHA1 = "b" * 40


class SQLiteIntegerBoundaryTests(unittest.TestCase):
    def test_accepts_zero_and_maximum_signed_integer(self):
        self.assertEqual(validate_sqlite_integer(0, "count"), 0)
        self.assertEqual(validate_sqlite_integer((1 << 63) - 1, "count"), (1 << 63) - 1)

    def test_rejects_bool_negative_and_signed_integer_overflow(self):
        for value in (True, False, -1, 1 << 63):
            with self.subTest(value=value), self.assertRaises(AdapterValidationError) as caught:
                validate_sqlite_integer(value, "count")
            self.assertEqual(caught.exception.code, "SQLITE_INTEGER_OUT_OF_RANGE")


class ImmutableAdapterDTOTests(unittest.TestCase):
    def test_attempt_record_is_immutable(self):
        attempt = AttemptRecord(
            attempt_id="att1:" + SHA,
            object_id="obj1:" + SHA,
            attempt_number=1,
            workflow_run_id="synthetic-run-1",
            workflow_job_id="synthetic-job-1",
            workflow_event="workflow_dispatch",
            trigger_sha=SHA1,
            checkout_sha=SHA1,
            requested_key="synthetic/object.zip",
            expected_size_bytes=10,
            expected_sha256=SHA,
            started_at_utc="2026-11-22T00:00:00.000Z",
            finished_at_utc="2026-11-22T00:00:01.000Z",
            outcome="FAILED",
            failure_subtype="HTTP_FAILED",
            response_status=503,
            response_bytes_received=0,
            is_complete_object=0,
            partial_body_sha256=None,
            complete_object_sha256=None,
            failure_code="HTTP_STATUS_NOT_SUCCESS",
        )
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            attempt.outcome = "TRANSFERRED"


class ProjectionCompatibilityTests(unittest.TestCase):
    def test_projects_physical_failed_subtype_to_unchanged_s3_failed_outcome(self):
        attempt = AttemptRecord(
            attempt_id="att1:" + SHA,
            object_id="obj1:" + SHA,
            attempt_number=1,
            workflow_run_id="synthetic-run-1",
            workflow_job_id="synthetic-job-1",
            workflow_event="workflow_dispatch",
            trigger_sha=SHA1,
            checkout_sha=SHA1,
            requested_key="synthetic/object.zip",
            expected_size_bytes=10,
            expected_sha256=SHA,
            started_at_utc="2026-11-22T00:00:00.000Z",
            finished_at_utc="2026-11-22T00:00:01.000Z",
            outcome="FAILED",
            failure_subtype="HTTP_FAILED",
            response_status=503,
            response_bytes_received=0,
            is_complete_object=0,
            partial_body_sha256=None,
            complete_object_sha256=None,
            failure_code="HTTP_STATUS_NOT_SUCCESS",
        )
        projected = project_attempt_record(attempt)
        self.assertEqual(projected["outcome"], "FAILED")
        self.assertNotIn("failure_subtype", projected)
        self.assertEqual(projected["expected_size_bytes"], 10)
        self.assertEqual(projected["expected_sha256"], SHA)

    def test_rejects_unknown_physical_attempt_outcome(self):
        values = dict(
            attempt_id="att1:" + SHA, object_id="obj1:" + SHA,
            attempt_number=1, workflow_run_id="r", workflow_job_id="j",
            workflow_event="workflow_dispatch", trigger_sha=SHA1, checkout_sha=SHA1,
            requested_key="x", expected_size_bytes=1, expected_sha256=SHA,
            started_at_utc="2026-11-22T00:00:00.000Z",
            finished_at_utc="2026-11-22T00:00:01.000Z",
            outcome="HTTP_FAILED", failure_subtype=None, response_status=503,
            response_bytes_received=0, is_complete_object=0,
            partial_body_sha256=None, complete_object_sha256=None,
            failure_code="HTTP_STATUS_NOT_SUCCESS",
        )
        with self.assertRaises(AdapterValidationError):
            project_attempt_record(AttemptRecord(**values))

    def test_projects_raw_fields_json_to_exact_twelve_string_array(self):
        raw_json = '["1000","1","2","0.5","1.5","10","1899","3","4","5","6","0"]'
        row = SourceRowRecord(
            source_row_id="row1:" + SHA, member_id="mem1:" + SHA,
            physical_record_ordinal=2, data_row_ordinal=1,
            raw_fields_json=raw_json, raw_row_digest=SHA,
            parser_contract_id="T0_ARCHIVE_CSV_HEADER_V1", parser_source_sha=SHA1,
            importer_contract_id="T0_ARCHIVE_IMPORTER_V1", importer_source_sha=SHA1,
            exchange="binance", market_type="usdm", symbol="BTCUSDT",
            timeframe="15m", open_time_ms=900,
            candle_value_id="cv1:" + SHA, disposition="ACCEPTED", rejection_code=None,
        )
        projected = project_source_row_record(row)
        self.assertEqual(projected["raw_fields"], [
            "1000", "1", "2", "0.5", "1.5", "10", "1899", "3", "4", "5", "6", "0"
        ])
        self.assertEqual(projected["importer_contract_id"], "T0_ARCHIVE_IMPORTER_V1")

    def test_rejects_noncanonical_or_non_twelve_field_raw_json(self):
        row = SourceRowRecord(
            source_row_id="row1:" + SHA, member_id="mem1:" + SHA,
            physical_record_ordinal=2, data_row_ordinal=1,
            raw_fields_json='[ "x" ]', raw_row_digest=SHA,
            parser_contract_id="T0_ARCHIVE_CSV_HEADER_V1", parser_source_sha=SHA1,
            importer_contract_id="T0_ARCHIVE_IMPORTER_V1", importer_source_sha=SHA1,
            exchange="binance", market_type="usdm", symbol="BTCUSDT",
            timeframe="15m", open_time_ms=900,
            candle_value_id="cv1:" + SHA, disposition="ACCEPTED", rejection_code=None,
        )
        with self.assertRaises(AdapterValidationError):
            project_source_row_record(row)

    def test_projects_candidate_member_count_without_renaming_s3_field(self):
        pair = PairRecord(
            pair_id="pair1:" + SHA, zip_object_id="obj1:" + SHA,
            sidecar_object_id="obj1:" + ("c" * 64),
            zip_size_bytes=100, zip_sha256=SHA, sidecar_size_bytes=20,
            sidecar_sha256="c" * 64, sidecar_asserted_zip_sha256=SHA,
            assertion_matches=1, zip_crc_ok=1, candidate_member_count=1,
            structural_ok=1, disposition="VERIFIED", failure_code=None,
        )
        projected = project_pair_record(pair)
        self.assertEqual(projected["member_count"], 1)
        self.assertNotIn("candidate_member_count", projected)

    def test_derives_object_attempt_count_and_successful_attempt_from_relations(self):
        object_id = "obj1:" + SHA
        attempts = (
            AttemptRecord(
                attempt_id="att1:" + SHA, object_id=object_id, attempt_number=1,
                workflow_run_id="r1", workflow_job_id="j1", workflow_event="workflow_dispatch",
                trigger_sha=SHA1, checkout_sha=SHA1, requested_key="x",
                expected_size_bytes=10, expected_sha256=SHA,
                started_at_utc="2026-11-22T00:00:00.000Z",
                finished_at_utc="2026-11-22T00:00:01.000Z",
                outcome="FAILED", failure_subtype="HTTP_FAILED", response_status=503,
                response_bytes_received=0, is_complete_object=0, partial_body_sha256=None,
                complete_object_sha256=None, failure_code="HTTP_STATUS_NOT_SUCCESS",
            ),
            AttemptRecord(
                attempt_id="att1:" + ("d" * 64), object_id=object_id, attempt_number=2,
                workflow_run_id="r2", workflow_job_id="j2", workflow_event="workflow_dispatch",
                trigger_sha=SHA1, checkout_sha=SHA1, requested_key="x",
                expected_size_bytes=10, expected_sha256=SHA,
                started_at_utc="2026-11-22T00:00:02.000Z",
                finished_at_utc="2026-11-22T00:00:03.000Z",
                outcome="TRANSFERRED", failure_subtype=None, response_status=200,
                response_bytes_received=10, is_complete_object=1, partial_body_sha256=None,
                complete_object_sha256=SHA, failure_code=None,
            ),
        )
        summary = derive_object_attempt_summary(
            object_id=object_id, attempts=attempts,
            successful_attempt_id="att1:" + ("d" * 64),
        )
        self.assertEqual(summary, {"attempt_count": 2, "successful_attempt_id": "att1:" + ("d" * 64)})

    def test_rejects_successful_attempt_relation_from_another_object(self):
        with self.assertRaises(AdapterValidationError):
            derive_object_attempt_summary(
                object_id="obj1:" + SHA,
                attempts=(),
                successful_attempt_id="att1:" + SHA,
            )


if __name__ == "__main__":
    unittest.main()


class CompleteDTOInventoryREDTests(unittest.TestCase):
    """F2 contract: all eleven physical relations have immutable DTOs."""

    def test_all_eleven_canonical_dto_types_exist_and_are_frozen_slotted(self):
        from dataclasses import is_dataclass
        import market_data.archive_staging_adapter as adapter

        names = (
            "RunEnvelope", "ObjectEvidence", "AttemptEvidence",
            "SuccessfulAttempt", "PairEvidence", "MemberCandidateEvidence",
            "SourceRowEvidence", "CandleEvidence", "CandleLinkEvidence",
            "FailureObservation", "RunEvent",
        )
        for name in names:
            with self.subTest(dto=name):
                dto = getattr(adapter, name, None)
                self.assertIsNotNone(dto, f"missing canonical DTO: {name}")
                self.assertTrue(is_dataclass(dto), f"{name} must be a dataclass")
                self.assertTrue(dto.__dataclass_params__.frozen, f"{name} must be frozen")
                self.assertTrue(hasattr(dto, "__slots__"), f"{name} must be slotted")


class ReadOnlyProjectionAPIRedTests(unittest.TestCase):
    def test_projection_entrypoint_accepts_only_caller_owned_connection(self):
        import inspect
        import market_data.archive_staging_adapter as adapter

        project = getattr(adapter, "project_staging_database", None)
        self.assertTrue(callable(project), "missing project_staging_database(connection)")
        parameters = tuple(inspect.signature(project).parameters.values())
        self.assertEqual(tuple(item.name for item in parameters), ("connection",))
        self.assertEqual(parameters[0].kind, inspect.Parameter.POSITIONAL_OR_KEYWORD)


class ReadOnlyStagingProjectionBehaviorTests(unittest.TestCase):
    @staticmethod
    def _connection_with_run(*, include_building_event=True):
        from hashlib import sha256
        from market_data.archive_staging_schema import (
            compute_schema_fingerprint, connect_staging_database,
        )

        connection = connect_staging_database(":memory:")
        inventory_bytes = b'{"synthetic":true}\\x00'
        manifest_json = "{}"
        connection.execute(
            """INSERT INTO reconstruction_run (
                singleton_key,run_id,inventory_id,inventory_blob_sha256,
                inventory_raw_bytes,label,parser_contract_id,parser_source_sha,
                importer_source_sha,schema_contract_id,schema_fingerprint_sha256,
                created_at_utc,coverage_manifest_json,coverage_manifest_sha256
            ) VALUES (1,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                "run1:" + "1" * 64,
                "inv1:" + "2" * 64,
                sha256(inventory_bytes).hexdigest(),
                inventory_bytes,
                "RECONSTRUCTED — PARTIAL COVERAGE",
                "T0_ARCHIVE_CSV_HEADER_V1",
                "3" * 40,
                "4" * 40,
                "T0_STAGING_SCHEMA_V2",
                compute_schema_fingerprint(),
                "2026-11-22T00:00:00.000Z",
                manifest_json,
                sha256(manifest_json.encode("utf-8")).hexdigest(),
            ),
        )
        if include_building_event:
            connection.execute(
                """INSERT INTO run_events (
                    run_id,event_seq,event_type,occurred_at_utc,reason_code,
                    candidate_snapshot_sha256,validator_payload_sha256
                ) VALUES (?,?,?, ?,NULL,NULL,NULL)""",
                (
                    "run1:" + "1" * 64, 1, "BUILDING",
                    "2026-11-22T00:00:00.000Z",
                ),
            )
        connection.commit()
        return connection, inventory_bytes

    def test_projects_run_and_empty_relations_without_opening_or_closing_connection(self):
        from unittest.mock import patch
        from market_data.archive_staging_adapter import project_staging_database

        connection, raw_bytes = self._connection_with_run()
        try:
            self.assertFalse(connection.in_transaction)
            with patch("sqlite3.connect", side_effect=AssertionError("implicit connect forbidden")):
                projection = project_staging_database(connection)
            self.assertEqual(projection.run.inventory_raw_bytes, raw_bytes)
            self.assertEqual(projection.run.run_id, "run1:" + "1" * 64)
            self.assertEqual(projection.run_events[0].event_type, "BUILDING")
            self.assertEqual(projection.objects, ())
            self.assertEqual(projection.attempts, ())
            self.assertFalse(connection.in_transaction)
            self.assertEqual(connection.execute("SELECT 1").fetchone()[0], 1)
        finally:
            connection.close()

    def test_rejects_initialized_schema_without_singleton_run_envelope(self):
        from market_data.archive_staging_adapter import (
            AdapterValidationError, project_staging_database,
        )
        from market_data.archive_staging_schema import connect_staging_database

        connection = connect_staging_database(":memory:")
        try:
            with self.assertRaises(AdapterValidationError) as caught:
                project_staging_database(connection)
            self.assertEqual(caught.exception.code, "RUN_ENVELOPE_CARDINALITY_INVALID")
        finally:
            connection.close()

    def test_rejects_run_without_initial_building_event(self):
        from market_data.archive_staging_adapter import (
            AdapterValidationError, project_staging_database,
        )

        connection, _ = self._connection_with_run(include_building_event=False)
        try:
            with self.assertRaises(AdapterValidationError) as caught:
                project_staging_database(connection)
            self.assertEqual(caught.exception.code, "INITIAL_BUILDING_EVENT_INVALID")
        finally:
            connection.close()


class StrictPhysicalDTOFieldTests(unittest.TestCase):
    def test_run_event_rejects_bool_and_zero_sequence(self):
        from market_data.archive_staging_adapter import RunEvent

        values = dict(
            run_id="run1:" + "1" * 64,
            event_seq=1,
            event_type="BUILDING",
            occurred_at_utc="2026-11-22T00:00:00.000Z",
            reason_code=None,
            candidate_snapshot_sha256=None,
            validator_payload_sha256=None,
        )
        for invalid in (True, 0, -1):
            with self.subTest(event_seq=invalid), self.assertRaises((TypeError, ValueError)):
                RunEvent(**{**values, "event_seq": invalid})

    def test_run_event_rejects_empty_required_text(self):
        from market_data.archive_staging_adapter import RunEvent

        with self.assertRaises((TypeError, ValueError)):
            RunEvent(
                run_id="", event_seq=1, event_type="BUILDING",
                occurred_at_utc="2026-11-22T00:00:00.000Z",
                reason_code=None, candidate_snapshot_sha256=None,
                validator_payload_sha256=None,
            )

    def test_run_envelope_rejects_bool_singleton_key_and_non_bytes_inventory(self):
        from market_data.archive_staging_adapter import RunEnvelope

        values = dict(
            singleton_key=1, run_id="run1:" + "1" * 64,
            inventory_id="inv1:" + "2" * 64, inventory_blob_sha256="a" * 64,
            inventory_raw_bytes=b"{}", label="RECONSTRUCTED — PARTIAL COVERAGE",
            parser_contract_id="T0_ARCHIVE_CSV_HEADER_V1", parser_source_sha="b" * 40,
            importer_source_sha="c" * 40, schema_contract_id="T0_STAGING_SCHEMA_V2",
            schema_fingerprint_sha256="d" * 64, created_at_utc="2026-11-22T00:00:00.000Z",
            coverage_manifest_json="{}", coverage_manifest_sha256="e" * 64,
        )
        with self.assertRaises((TypeError, ValueError)):
            RunEnvelope(**{**values, "singleton_key": True})
        with self.assertRaises((TypeError, ValueError)):
            RunEnvelope(**{**values, "inventory_raw_bytes": "{}"})


class S3V1ProjectionAndGraphREDTests(unittest.TestCase):
    @staticmethod
    def _minimal_projection(*, event_sequence=(1, 2)):
        import hashlib
        from market_data.archive_staging_adapter import (
            RunEnvelope, RunEvent, StagingProjection,
        )

        inventory_id = "inv1:" + "2" * 64
        inventory_raw = (
            '{"inventory_id":"' + inventory_id + '","objects":[]}'
        ).encode("utf-8")
        manifest_json = '{"manifest_version":"T0-COVERAGE-MANIFEST-V1"}'
        run = RunEnvelope(
            singleton_key=1, run_id="run1:" + "1" * 64,
            inventory_id=inventory_id,
            inventory_blob_sha256=hashlib.sha256(inventory_raw).hexdigest(),
            inventory_raw_bytes=inventory_raw,
            label="RECONSTRUCTED — PARTIAL COVERAGE",
            parser_contract_id="T0_ARCHIVE_CSV_HEADER_V1",
            parser_source_sha="a" * 40, importer_source_sha="b" * 40,
            schema_contract_id="T0_STAGING_SCHEMA_V2",
            schema_fingerprint_sha256="c" * 64,
            created_at_utc="2026-11-22T00:00:00.000Z",
            coverage_manifest_json=manifest_json,
            coverage_manifest_sha256=hashlib.sha256(manifest_json.encode()).hexdigest(),
        )
        events = (
            RunEvent(
                run_id=run.run_id, event_seq=event_sequence[0], event_type="BUILDING",
                occurred_at_utc="2026-11-22T00:00:00.000Z", reason_code=None,
                candidate_snapshot_sha256=None, validator_payload_sha256=None,
            ),
            RunEvent(
                run_id=run.run_id, event_seq=event_sequence[1], event_type="CANDIDATE",
                occurred_at_utc="2026-11-22T00:00:01.000Z", reason_code=None,
                candidate_snapshot_sha256="d" * 64, validator_payload_sha256=None,
            ),
        )
        return StagingProjection(
            run=run, objects=(), attempts=(), successful_attempts=(), pairs=(),
            members=(), source_rows=(), candles=(), links=(),
            failure_observations=(), run_events=events,
        )

    def test_builds_unchanged_s3_v1_collection_keys_and_s1_envelope(self):
        from market_data.archive_staging_adapter import build_s3_v1_payload

        projection = self._minimal_projection()
        payload = build_s3_v1_payload(projection)
        self.assertEqual(
            set(payload),
            {
                "inventory", "objects", "pairs", "members", "attempts",
                "source_rows", "candles", "links", "contract_version",
                "inventory_raw_bytes", "inventory_expected_sha256",
                "inventory_expected_id", "coverage_manifest", "run",
            },
        )
        self.assertEqual(payload["contract_version"], "T0_PROVENANCE_VALIDATOR_S1_V1")
        self.assertEqual(payload["inventory_raw_bytes"], projection.run.inventory_raw_bytes)
        self.assertEqual(payload["inventory_expected_id"], projection.run.inventory_id)
        self.assertEqual(payload["run"]["status"], "CANDIDATE")
        self.assertEqual(payload["run"]["schema_contract_id"], "T0_STAGING_SCHEMA_V2")
        self.assertEqual(payload["objects"], ())
        self.assertEqual(payload["attempts"], ())

    def test_graph_validator_rejects_noncontiguous_event_sequence(self):
        from market_data.archive_staging_adapter import validate_staging_graph

        result = validate_staging_graph(self._minimal_projection(event_sequence=(1, 3)))
        self.assertFalse(result.valid)
        self.assertIn("RUN_EVENT_SEQUENCE_INVALID", result.error_codes)


class CompleteS3V1ProjectionFixtureTests(unittest.TestCase):
    @staticmethod
    def _projection_from_valid_s1_fixture():
        import hashlib
        import json
        from market_data.archive_staging_adapter import (
            AttemptEvidence, CandleEvidence, CandleLinkEvidence,
            FailureObservation, MemberCandidateEvidence, ObjectEvidence,
            PairEvidence, RunEnvelope, RunEvent, SourceRowEvidence,
            StagingProjection, SuccessfulAttempt,
        )
        from market_data.archive_staging_schema import compute_schema_fingerprint
        from market_data.test_archive_provenance_validator_s1_red import build_valid_s1_fixture

        fixture = build_valid_s1_fixture()
        manifest_json = json.dumps(
            fixture["coverage_manifest"], ensure_ascii=False,
            sort_keys=True, separators=(",", ":"),
        )
        run_id = "run1:" + "e" * 64
        inventory_id = fixture["inventory_expected_id"]
        inventory_raw = fixture["inventory_raw_bytes"]
        run = RunEnvelope(
            singleton_key=1, run_id=run_id, inventory_id=inventory_id,
            inventory_blob_sha256=fixture["inventory_expected_sha256"],
            inventory_raw_bytes=inventory_raw,
            label="RECONSTRUCTED — PARTIAL COVERAGE",
            parser_contract_id="T0_ARCHIVE_CSV_HEADER_V1",
            parser_source_sha="a" * 40, importer_source_sha="d" * 40,
            schema_contract_id="T0_STAGING_SCHEMA_V2",
            schema_fingerprint_sha256=compute_schema_fingerprint(),
            created_at_utc="2026-11-22T00:00:00.000Z",
            coverage_manifest_json=manifest_json,
            coverage_manifest_sha256=hashlib.sha256(manifest_json.encode()).hexdigest(),
        )
        objects = tuple(ObjectEvidence(
            object_id=x["object_id"], inventory_id=x["inventory_id"],
            inventory_blob_sha256=x["inventory_blob_sha256"],
            inventory_entry_identity=x["inventory_entry_identity"],
            object_key=x["object_key"], object_kind=x["object_kind"],
            timeframe=x["timeframe"], partition=x["partition"], period=x["period"],
            paired_object_key=x["paired_object_key"], requested_key=x["requested_key"],
            expected_size_bytes=x["expected_size_bytes"], expected_sha256=x["expected_sha256"],
            measured_size_bytes=x["measured_size_bytes"], measured_sha256=x["measured_sha256"],
            response_bytes_total=x["response_bytes_total"], response_status=x["response_status"],
            local_relative_path=x["local_relative_path"], exclusive_create=x["exclusive_create"],
            retrieval_source=x["retrieval_source"], workflow_run_id=x["workflow_run_id"],
            workflow_job_id=x["workflow_job_id"], workflow_event=x["workflow_event"],
            trigger_sha=x["trigger_sha"], checkout_sha=x["checkout_sha"],
            retrieved_at_utc=x["retrieved_at_utc"],
            verification_status=x["verification_status"], failure_code=x["failure_code"],
        ) for x in fixture["objects"])
        attempts = tuple(AttemptEvidence(
            attempt_id=x["attempt_id"], object_id=x["object_id"],
            attempt_number=x["attempt_number"], workflow_run_id=x["workflow_run_id"],
            workflow_job_id=x["workflow_job_id"], workflow_event=x["workflow_event"],
            trigger_sha=x["trigger_sha"], checkout_sha=x["checkout_sha"],
            requested_key=x["requested_key"], expected_size_bytes=x["expected_size_bytes"],
            expected_sha256=x["expected_sha256"], started_at_utc=x["started_at_utc"],
            finished_at_utc=x["finished_at_utc"], outcome=x["outcome"],
            failure_subtype=None, response_status=x["response_status"],
            response_bytes_received=x["response_bytes_received"],
            is_complete_object=x["is_complete_object"],
            partial_body_sha256=x["partial_body_sha256"],
            complete_object_sha256=x["complete_object_sha256"], failure_code=x["failure_code"],
        ) for x in fixture["attempts"])
        successful = tuple(
            SuccessfulAttempt(object_id=x["object_id"], attempt_id=x["successful_attempt_id"])
            for x in fixture["objects"]
        )
        pairs = tuple(PairEvidence(
            pair_id=x["pair_id"], zip_object_id=x["zip_object_id"],
            sidecar_object_id=x["sidecar_object_id"],
            zip_size_bytes=x["measured_zip_size_bytes"], zip_sha256=x["measured_zip_sha256"],
            sidecar_size_bytes=x["measured_sidecar_size_bytes"],
            sidecar_sha256=x["measured_sidecar_sha256"],
            sidecar_asserted_zip_sha256=x["sidecar_asserted_zip_sha256"],
            assertion_matches=x["sidecar_assertion_matches"], zip_crc_ok=x["zip_crc_ok"],
            candidate_member_count=x["member_count"], structural_ok=x["structural_ok"],
            disposition=x["disposition"], failure_code=x["failure_code"],
        ) for x in fixture["pairs"])
        members = tuple(MemberCandidateEvidence(
            candidate_id="cand1:" + hashlib.sha256(x["member_id"].encode()).hexdigest(),
            member_id=x["member_id"], pair_id=x["pair_id"],
            central_directory_ordinal=1, member_path=x["member_path"],
            member_size_bytes=x["member_size_bytes"], member_sha256=x["member_sha256"],
            encoding=x["encoding"], bom_present=x["bom_present"], newline=x["newline"],
            delimiter=x["delimiter"], header_present=x["header_present"],
            header_contract_id=x["header_contract_id"], parser_contract_id=x["parser_contract_id"],
            parser_source_sha=x["parser_source_sha"], data_row_count=x["data_row_count"],
            first_open_time_ms=x["first_open_time_ms"], last_open_time_ms=x["last_open_time_ms"],
            disposition=x["disposition"], failure_code=x["failure_code"],
        ) for x in fixture["members"])
        rows = tuple(SourceRowEvidence(
            source_row_id=x["source_row_id"], member_id=x["member_id"],
            physical_record_ordinal=x["physical_record_ordinal"],
            data_row_ordinal=x["data_row_ordinal"], raw_fields_json=x["raw_fields_json"],
            raw_row_digest=x["raw_row_digest"], parser_contract_id=x["parser_contract_id"],
            parser_source_sha=x["parser_source_sha"], importer_contract_id=x["importer_contract_id"],
            importer_source_sha=x["importer_source_sha"], exchange=x["natural_key"][0],
            market_type=x["natural_key"][1], symbol=x["natural_key"][2],
            timeframe=x["natural_key"][3], open_time_ms=x["natural_key"][4],
            candle_value_id=x["candle_value_id"], disposition=x["disposition"],
            rejection_code=x["rejection_code"],
        ) for x in fixture["source_rows"])
        candles = tuple(CandleEvidence(
            exchange=x["exchange"], market_type=x["market_type"], symbol=x["symbol"],
            timeframe=x["timeframe"], open_time_ms=x["open_time_ms"],
            open=x["open"], high=x["high"], low=x["low"], close=x["close"],
            volume=x["volume"], available_at_ms=x["available_at_ms"],
            availability_kind=x["availability_kind"], candle_value_id=x["candle_value_id"],
        ) for x in fixture["candles"])
        links = tuple(CandleLinkEvidence(
            link_id=x["link_id"], exchange=x["exchange"], market_type=x["market_type"],
            symbol=x["symbol"], timeframe=x["timeframe"], open_time_ms=x["open_time_ms"],
            source_row_id=x["source_row_id"], candle_value_id=x["candle_value_id"],
            duplicate_disposition=x["duplicate_disposition"],
        ) for x in fixture["links"])
        events = (
            RunEvent(
                run_id=run_id, event_seq=1, event_type="BUILDING",
                occurred_at_utc="2026-11-22T00:00:00.000Z", reason_code=None,
                candidate_snapshot_sha256=None, validator_payload_sha256=None,
            ),
            RunEvent(
                run_id=run_id, event_seq=2, event_type="CANDIDATE",
                occurred_at_utc="2026-11-22T00:00:02.000Z", reason_code=None,
                candidate_snapshot_sha256="f" * 64, validator_payload_sha256=None,
            ),
        )
        return StagingProjection(
            run=run, objects=objects, attempts=attempts,
            successful_attempts=successful, pairs=pairs, members=members,
            source_rows=rows, candles=candles, links=links,
            failure_observations=(), run_events=events,
        )

    def test_complete_synthetic_physical_projection_passes_unchanged_s3_v1(self):
        from market_data.archive_staging_adapter import (
            build_s3_v1_payload, validate_staging_graph,
        )
        from market_data.archive_provenance_validator import validate_provenance

        projection = self._projection_from_valid_s1_fixture()
        payload = build_s3_v1_payload(projection)
        self.assertEqual(len(payload["inventory"]["objects"]), 404)
        self.assertEqual(len(payload["objects"]), 404)
        self.assertEqual(len(payload["attempts"]), 404)
        self.assertEqual(len(payload["pairs"]), 202)
        self.assertEqual(len(payload["members"]), 202)
        self.assertEqual(len(payload["source_rows"]), 202)
        self.assertEqual(len(payload["candles"]), 202)
        self.assertEqual(len(payload["links"]), 202)
        self.assertTrue(validate_provenance(payload).valid)
        graph_result = validate_staging_graph(projection)
        self.assertTrue(graph_result.valid, graph_result.error_codes)


class PopulatedSQLiteProjectionIntegrationTests(unittest.TestCase):
    def test_projects_populated_rows_from_all_eleven_relations_in_stable_order(self):
        import hashlib
        import json
        from market_data.archive_staging_adapter import project_staging_database
        from market_data.archive_staging_schema import (
            compute_schema_fingerprint, connect_staging_database,
        )

        connection = connect_staging_database(":memory:")
        run_id = "run1:" + "1" * 64
        inventory_id = "inv1:" + "2" * 64
        zip_key, sidecar_key = "synthetic/000.zip", "synthetic/000.zip.CHECKSUM"
        inventory_entries = [
            {"object_key": zip_key, "object_kind": "ZIP",
             "paired_object_key": sidecar_key, "timeframe": "15m",
             "partition": "synthetic", "period": "000"},
            {"object_key": sidecar_key, "object_kind": "CHECKSUM_SIDECAR",
             "paired_object_key": zip_key, "timeframe": "15m",
             "partition": "synthetic", "period": "000"},
        ]
        inventory_raw = json.dumps(
            {"inventory_id": inventory_id, "objects": inventory_entries},
            ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")
        inventory_sha = hashlib.sha256(inventory_raw).hexdigest()
        manifest_json = "{}"
        manifest_sha = hashlib.sha256(manifest_json.encode()).hexdigest()
        zip_id, sidecar_id = "obj1:" + "a" * 64, "obj1:" + "b" * 64
        zip_sha, sidecar_sha = "3" * 64, "4" * 64
        zip_attempt, sidecar_attempt = "att1:" + "5" * 64, "att1:" + "6" * 64
        pair_id = "pair1:" + "7" * 64
        candidate_id, member_id = "cand1:" + "8" * 64, "mem1:" + "9" * 64
        source_row_id, candle_value_id = "row1:" + "c" * 64, "cv1:" + "d" * 64
        link_id = "lnk1:" + "e" * 64
        raw_fields = ["0", "1", "2", "1", "2", "1", "899999", "0", "0", "0", "0", "0"]
        raw_fields_json = json.dumps(raw_fields, ensure_ascii=False, separators=(",", ":"))
        try:
            connection.execute(
                """INSERT INTO reconstruction_run (
                    singleton_key,run_id,inventory_id,inventory_blob_sha256,
                    inventory_raw_bytes,label,parser_contract_id,parser_source_sha,
                    importer_source_sha,schema_contract_id,schema_fingerprint_sha256,
                    created_at_utc,coverage_manifest_json,coverage_manifest_sha256
                ) VALUES (1,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    run_id, inventory_id, inventory_sha, inventory_raw,
                    "RECONSTRUCTED — PARTIAL COVERAGE", "T0_ARCHIVE_CSV_HEADER_V1",
                    "a" * 40, "b" * 40, "T0_STAGING_SCHEMA_V2",
                    compute_schema_fingerprint(), "2026-11-22T00:00:00.000Z",
                    manifest_json, manifest_sha,
                ),
            )
            connection.executemany(
                """INSERT INTO run_events (
                    run_id,event_seq,event_type,occurred_at_utc,reason_code,
                    candidate_snapshot_sha256,validator_payload_sha256
                ) VALUES (?,?,?,?,NULL,?,NULL)""",
                (
                    (run_id, 1, "BUILDING", "2026-11-22T00:00:00.000Z", None),
                    (run_id, 2, "CANDIDATE", "2026-11-22T00:00:01.000Z", "f" * 64),
                ),
            )
            object_rows = []
            for oid, key, kind, paired_key, digest, attempt_id in (
                (zip_id, zip_key, "ZIP", sidecar_key, zip_sha, zip_attempt),
                (sidecar_id, sidecar_key, "CHECKSUM_SIDECAR", zip_key, sidecar_sha, sidecar_attempt),
            ):
                object_rows.append((
                    oid, inventory_id, inventory_sha, "synthetic-entry-" + kind,
                    key, kind, "15m", "synthetic", "000", paired_key,
                    key, 10, digest, 10, digest, 10, 200,
                    "synthetic/" + kind.lower(), 1, "SYNTHETIC_FIXTURE",
                    "workflow-run-1", "workflow-job-1", "workflow_dispatch",
                    "a" * 40, "b" * 40, "2026-11-22T00:00:01.000Z",
                    "VERIFIED", None,
                ))
            connection.executemany(
                """INSERT INTO archive_objects (
                    object_id,inventory_id,inventory_blob_sha256,inventory_entry_identity,
                    object_key,object_kind,timeframe,partition,period,paired_object_key,
                    requested_key,expected_size_bytes,expected_sha256,measured_size_bytes,
                    measured_sha256,response_bytes_total,response_status,local_relative_path,
                    exclusive_create,retrieval_source,workflow_run_id,workflow_job_id,
                    workflow_event,trigger_sha,checkout_sha,retrieved_at_utc,
                    verification_status,failure_code
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                object_rows,
            )
            attempt_rows = []
            for aid, oid, key, digest in (
                (zip_attempt, zip_id, zip_key, zip_sha),
                (sidecar_attempt, sidecar_id, sidecar_key, sidecar_sha),
            ):
                attempt_rows.append((
                    aid, oid, 1, "workflow-run-1", "workflow-job-1",
                    "workflow_dispatch", "a" * 40, "b" * 40, key,
                    10, digest, "2026-11-22T00:00:00.000Z",
                    "2026-11-22T00:00:01.000Z", "TRANSFERRED", None,
                    200, 10, 1, None, digest, None,
                ))
            connection.executemany(
                """INSERT INTO acquisition_attempts (
                    attempt_id,object_id,attempt_number,workflow_run_id,workflow_job_id,
                    workflow_event,trigger_sha,checkout_sha,requested_key,expected_size_bytes,
                    expected_sha256,started_at_utc,finished_at_utc,outcome,failure_subtype,
                    response_status,response_bytes_received,is_complete_object,
                    partial_body_sha256,complete_object_sha256,failure_code
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                attempt_rows,
            )
            connection.executemany(
                "INSERT INTO object_successful_attempt (object_id,attempt_id) VALUES (?,?)",
                ((zip_id, zip_attempt), (sidecar_id, sidecar_attempt)),
            )
            connection.execute(
                """INSERT INTO archive_pairs (
                    pair_id,zip_object_id,sidecar_object_id,zip_size_bytes,zip_sha256,
                    sidecar_size_bytes,sidecar_sha256,sidecar_asserted_zip_sha256,
                    assertion_matches,zip_crc_ok,candidate_member_count,structural_ok,
                    disposition,failure_code
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,NULL)""",
                (pair_id, zip_id, sidecar_id, 10, zip_sha, 10, sidecar_sha,
                 zip_sha, 1, 1, 1, 1, "VERIFIED"),
            )
            connection.execute(
                """INSERT INTO csv_members (
                    candidate_id,member_id,pair_id,central_directory_ordinal,member_path,
                    member_size_bytes,member_sha256,encoding,bom_present,newline,delimiter,
                    header_present,header_contract_id,parser_contract_id,parser_source_sha,
                    data_row_count,first_open_time_ms,last_open_time_ms,disposition,failure_code
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,NULL)""",
                (candidate_id, member_id, pair_id, 1, "data/BTCUSDT-15m.csv",
                 100, "8" * 64, "UTF-8", 0, "LF", ",", 1,
                 "T0_ARCHIVE_CSV_HEADER_V1", "T0_ARCHIVE_CSV_HEADER_V1",
                 "a" * 40, 1, 0, 0, "VERIFIED"),
            )
            connection.execute(
                """INSERT INTO source_rows (
                    source_row_id,member_id,physical_record_ordinal,data_row_ordinal,
                    raw_fields_json,raw_row_digest,parser_contract_id,parser_source_sha,
                    importer_contract_id,importer_source_sha,exchange,market_type,symbol,
                    timeframe,open_time_ms,candle_value_id,disposition,rejection_code
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,NULL)""",
                (source_row_id, member_id, 2, 1, raw_fields_json, "f" * 64,
                 "T0_ARCHIVE_CSV_HEADER_V1", "a" * 40,
                 "T0_ARCHIVE_IMPORTER_V1", "b" * 40,
                 "binance", "usdm", "BTCUSDT", "15m", 0, candle_value_id, "ACCEPTED"),
            )
            connection.execute(
                """INSERT INTO candles (
                    exchange,market_type,symbol,timeframe,open_time_ms,open,high,low,
                    close,volume,available_at_ms,availability_kind,candle_value_id
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                ("binance", "usdm", "BTCUSDT", "15m", 0, "1", "2", "1",
                 "2", "1", 900000, "BAR_CLOSE_BOUNDARY", candle_value_id),
            )
            connection.execute(
                """INSERT INTO candle_provenance_links (
                    link_id,exchange,market_type,symbol,timeframe,open_time_ms,
                    source_row_id,candle_value_id,duplicate_disposition
                ) VALUES (?,?,?,?,?,?,?,?,?)""",
                (link_id, "binance", "usdm", "BTCUSDT", "15m", 0,
                 source_row_id, candle_value_id, "UNIQUE"),
            )
            connection.execute(
                """INSERT INTO failure_observations (
                    subject_kind,subject_id,failure_ordinal,failure_code,
                    failure_detail_code,observed_at_utc,evidence_sha256
                ) VALUES (?,?,?,?,?,?,?)""",
                ("RUN", run_id, 1, "SYNTHETIC_TEST_NOTE", "TEST_ONLY",
                 "2026-11-22T00:00:01.000Z", "1" * 64),
            )
            connection.commit()

            projection = project_staging_database(connection)
            self.assertEqual(projection.run.inventory_raw_bytes, inventory_raw)
            self.assertEqual([item.object_id for item in projection.objects], [zip_id, sidecar_id])
            self.assertEqual([item.attempt_id for item in projection.attempts], [zip_attempt, sidecar_attempt])
            self.assertEqual([item.object_id for item in projection.successful_attempts], [zip_id, sidecar_id])
            self.assertEqual(projection.pairs[0].zip_size_bytes, 10)
            self.assertEqual(projection.members[0].candidate_id, candidate_id)
            self.assertEqual(projection.source_rows[0].raw_fields_json, raw_fields_json)
            self.assertEqual(projection.candles[0].available_at_ms, 900000)
            self.assertEqual(projection.links[0].link_id, link_id)
            self.assertEqual(projection.failure_observations[0].failure_code, "SYNTHETIC_TEST_NOTE")
            self.assertEqual([item.event_seq for item in projection.run_events], [1, 2])
            self.assertFalse(connection.in_transaction)
            self.assertEqual(connection.execute("SELECT 1").fetchone()[0], 1)
        finally:
            connection.close()


class CoverageManifestAndRunLifecycleTests(unittest.TestCase):
    def test_s3_projection_rejects_noncanonical_coverage_manifest_json(self):
        import hashlib
        from dataclasses import replace
        from market_data.archive_staging_adapter import (
            AdapterValidationError, build_s3_v1_payload,
        )

        projection = S3V1ProjectionAndGraphREDTests._minimal_projection()
        noncanonical = '{"z":1,"a":2}'
        changed_run = replace(
            projection.run,
            coverage_manifest_json=noncanonical,
            coverage_manifest_sha256=hashlib.sha256(noncanonical.encode()).hexdigest(),
        )
        changed = replace(projection, run=changed_run)
        with self.assertRaises(AdapterValidationError) as caught:
            build_s3_v1_payload(changed)
        self.assertEqual(caught.exception.code, "COVERAGE_MANIFEST_NONCANONICAL")

    def test_validated_event_requires_validator_payload_digest(self):
        from dataclasses import replace
        from market_data.archive_staging_adapter import (
            RunEvent, validate_staging_graph,
        )

        projection = S3V1ProjectionAndGraphREDTests._minimal_projection()
        validated = RunEvent(
            run_id=projection.run.run_id, event_seq=3, event_type="VALIDATED",
            occurred_at_utc="2026-11-22T00:00:02.000Z", reason_code=None,
            candidate_snapshot_sha256="d" * 64, validator_payload_sha256=None,
        )
        changed = replace(projection, run_events=projection.run_events + (validated,))
        result = validate_staging_graph(changed)
        self.assertFalse(result.valid)
        self.assertIn("RUN_EVENT_TRANSITION_INVALID", result.error_codes)


    def test_validated_event_must_reference_same_candidate_snapshot(self):
        from dataclasses import replace
        from market_data.archive_staging_adapter import (
            RunEvent, validate_staging_graph,
        )

        projection = S3V1ProjectionAndGraphREDTests._minimal_projection()
        validated = RunEvent(
            run_id=projection.run.run_id, event_seq=3, event_type="VALIDATED",
            occurred_at_utc="2026-11-22T00:00:02.000Z", reason_code=None,
            candidate_snapshot_sha256="e" * 64, validator_payload_sha256="f" * 64,
        )
        changed = replace(projection, run_events=projection.run_events + (validated,))
        result = validate_staging_graph(changed)
        self.assertFalse(result.valid)
        self.assertIn("RUN_EVENT_TRANSITION_INVALID", result.error_codes)
