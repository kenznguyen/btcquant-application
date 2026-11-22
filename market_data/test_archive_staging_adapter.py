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
