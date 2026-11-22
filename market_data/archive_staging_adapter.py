"""Pure, immutable DTOs and S3/V1 projection helpers for S1.2.

This module performs no I/O. SQLite access belongs to the separately tested
staging repository adapter; archive acquisition is explicitly out of scope.
"""
from __future__ import annotations

from dataclasses import dataclass, fields
import json
import re
from typing import Any, Mapping, Sequence


MAX_SQLITE_INTEGER = (1 << 63) - 1
_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
_SHA1_RE = re.compile(r"[0-9a-f]{40}\Z")
_ATTEMPT_OUTCOMES = frozenset({"STARTED", "FAILED", "TRANSFERRED", "UNKNOWN"})
_FAILURE_SUBTYPES = frozenset({"HTTP_FAILED", "TRANSFER_FAILED", "VALIDATION_FAILED"})


class AdapterValidationError(ValueError):
    """Stable, fail-closed adapter validation error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def validate_sqlite_integer(value: object, field: str) -> int:
    """Validate an exact non-negative SQLite signed-64-bit INTEGER value."""
    if type(value) is not int or value < 0 or value > MAX_SQLITE_INTEGER:
        raise AdapterValidationError(
            "SQLITE_INTEGER_OUT_OF_RANGE",
            f"{field} must be an exact integer in [0, {MAX_SQLITE_INTEGER}]",
        )
    return value


def _required_text(value: object, field: str) -> str:
    if type(value) is not str or not value:
        raise AdapterValidationError("ADAPTER_FIELD_INVALID", f"{field} must be non-empty text")
    return value


def _sha(value: object, pattern: re.Pattern[str], field: str) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise AdapterValidationError("ADAPTER_DIGEST_INVALID", f"{field} has invalid digest syntax")
    return value


@dataclass(frozen=True, slots=True)
class AttemptRecord:
    attempt_id: str
    object_id: str
    attempt_number: int
    workflow_run_id: str
    workflow_job_id: str
    workflow_event: str
    trigger_sha: str
    checkout_sha: str
    requested_key: str
    expected_size_bytes: int
    expected_sha256: str
    started_at_utc: str
    finished_at_utc: str | None
    outcome: str
    failure_subtype: str | None
    response_status: int | None
    response_bytes_received: int
    is_complete_object: int
    partial_body_sha256: str | None
    complete_object_sha256: str | None
    failure_code: str | None


@dataclass(frozen=True, slots=True)
class SourceRowRecord:
    source_row_id: str
    member_id: str
    physical_record_ordinal: int
    data_row_ordinal: int
    raw_fields_json: str
    raw_row_digest: str
    parser_contract_id: str
    parser_source_sha: str
    importer_contract_id: str
    importer_source_sha: str
    exchange: str
    market_type: str
    symbol: str
    timeframe: str
    open_time_ms: int | None
    candle_value_id: str | None
    disposition: str
    rejection_code: str | None


@dataclass(frozen=True, slots=True)
class PairRecord:
    pair_id: str
    zip_object_id: str
    sidecar_object_id: str
    zip_size_bytes: int | None
    zip_sha256: str | None
    sidecar_size_bytes: int | None
    sidecar_sha256: str | None
    sidecar_asserted_zip_sha256: str | None
    assertion_matches: int | None
    zip_crc_ok: int | None
    candidate_member_count: int | None
    structural_ok: int | None
    disposition: str
    failure_code: str | None


def project_attempt_record(record: AttemptRecord) -> dict[str, object]:
    """Project one immutable physical attempt into the unchanged S3/V1 shape."""
    if not isinstance(record, AttemptRecord):
        raise AdapterValidationError("ADAPTER_RECORD_TYPE_INVALID", "attempt must be AttemptRecord")
    _required_text(record.attempt_id, "attempt_id")
    _required_text(record.object_id, "object_id")
    _required_text(record.workflow_run_id, "workflow_run_id")
    _required_text(record.workflow_job_id, "workflow_job_id")
    _required_text(record.requested_key, "requested_key")
    _sha(record.trigger_sha, _SHA1_RE, "trigger_sha")
    _sha(record.checkout_sha, _SHA1_RE, "checkout_sha")
    _sha(record.expected_sha256, _SHA256_RE, "expected_sha256")
    validate_sqlite_integer(record.attempt_number, "attempt_number")
    if record.attempt_number == 0:
        raise AdapterValidationError("ATTEMPT_HISTORY_INVALID", "attempt_number must be positive")
    validate_sqlite_integer(record.expected_size_bytes, "expected_size_bytes")
    validate_sqlite_integer(record.response_bytes_received, "response_bytes_received")
    if record.outcome not in _ATTEMPT_OUTCOMES:
        raise AdapterValidationError("ATTEMPT_OUTCOME_INVALID", "unsupported physical attempt outcome")
    if record.outcome == "FAILED":
        if record.failure_subtype not in _FAILURE_SUBTYPES or not record.failure_code:
            raise AdapterValidationError("ATTEMPT_FAILURE_INVALID", "FAILED requires a stable subtype and failure code")
    elif record.failure_subtype is not None:
        raise AdapterValidationError("ATTEMPT_FAILURE_INVALID", "failure_subtype is only valid for FAILED")
    _required_text(record.started_at_utc, "started_at_utc")
    if record.outcome == "STARTED":
        if record.finished_at_utc is not None:
            raise AdapterValidationError("ATTEMPT_TIME_INVALID", "STARTED must not have finished_at_utc")
    else:
        _required_text(record.finished_at_utc, "finished_at_utc")
    if record.is_complete_object not in (0, 1) or type(record.is_complete_object) is not int:
        raise AdapterValidationError("ATTEMPT_COMPLETION_INVALID", "is_complete_object must be integer 0 or 1")
    if record.outcome == "TRANSFERRED":
        if record.is_complete_object != 1 or record.complete_object_sha256 is None:
            raise AdapterValidationError("TRANSFERRED_ATTEMPT_INCOMPLETE", "TRANSFERRED requires complete object evidence")
        _sha(record.complete_object_sha256, _SHA256_RE, "complete_object_sha256")
        if record.partial_body_sha256 is not None:
            raise AdapterValidationError("ATTEMPT_DIGEST_INVALID", "complete transfer cannot use partial-body digest")
    elif record.is_complete_object != 0 or record.complete_object_sha256 is not None:
        raise AdapterValidationError("ATTEMPT_COMPLETION_INVALID", "non-TRANSFERRED attempt cannot claim a complete object")
    if record.partial_body_sha256 is not None:
        _sha(record.partial_body_sha256, _SHA256_RE, "partial_body_sha256")
    return {
        "attempt_id": record.attempt_id,
        "object_id": record.object_id,
        "attempt_number": record.attempt_number,
        "workflow_run_id": record.workflow_run_id,
        "workflow_job_id": record.workflow_job_id,
        "workflow_event": record.workflow_event,
        "trigger_sha": record.trigger_sha,
        "checkout_sha": record.checkout_sha,
        "requested_key": record.requested_key,
        "expected_size_bytes": record.expected_size_bytes,
        "expected_sha256": record.expected_sha256,
        "started_at_utc": record.started_at_utc,
        "finished_at_utc": record.finished_at_utc,
        "outcome": record.outcome,
        "response_status": record.response_status,
        "response_bytes_received": record.response_bytes_received,
        "is_complete_object": record.is_complete_object,
        "partial_body_sha256": record.partial_body_sha256,
        "complete_object_sha256": record.complete_object_sha256,
        "failure_code": record.failure_code,
    }


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def project_source_row_record(record: SourceRowRecord) -> dict[str, object]:
    """Project compact persisted raw_fields_json into the exact S3 raw_fields list."""
    if not isinstance(record, SourceRowRecord):
        raise AdapterValidationError("ADAPTER_RECORD_TYPE_INVALID", "source row must be SourceRowRecord")
    try:
        parsed = json.loads(record.raw_fields_json, object_pairs_hook=_reject_duplicate_json_keys)
    except (TypeError, json.JSONDecodeError, ValueError) as exc:
        raise AdapterValidationError("SOURCE_ROW_RAW_FIELDS_INVALID", "raw_fields_json is not strict JSON") from exc
    if (not isinstance(parsed, list) or len(parsed) != 12
            or any(type(item) is not str for item in parsed)):
        raise AdapterValidationError("SOURCE_ROW_RAW_FIELDS_INVALID", "raw_fields must be exactly twelve strings")
    canonical = json.dumps(parsed, ensure_ascii=False, separators=(",", ":"))
    if canonical != record.raw_fields_json:
        raise AdapterValidationError("SOURCE_ROW_RAW_FIELDS_INVALID", "raw_fields_json is not canonical compact JSON")
    if record.importer_contract_id != "T0_ARCHIVE_IMPORTER_V1":
        raise AdapterValidationError("SOURCE_ROW_CONTRACT_INVALID", "unsupported importer contract")
    if record.disposition == "ACCEPTED":
        if (record.exchange != "binance" or record.market_type != "usdm"
                or record.symbol != "BTCUSDT" or record.timeframe not in ("15m", "1h")
                or record.open_time_ms is None or record.candle_value_id is None
                or record.rejection_code is not None):
            raise AdapterValidationError("SOURCE_ROW_IDENTITY_INVALID", "accepted source row has invalid identity/value")
        validate_sqlite_integer(record.open_time_ms, "open_time_ms")
        _sha(record.parser_source_sha, _SHA1_RE, "parser_source_sha")
        _sha(record.importer_source_sha, _SHA1_RE, "importer_source_sha")
        if not record.candle_value_id.startswith("cv1:") or _SHA256_RE.fullmatch(record.candle_value_id[4:]) is None:
            raise AdapterValidationError("SOURCE_ROW_VALUE_INVALID", "candle_value_id is invalid")
    elif record.disposition == "REJECTED":
        if record.candle_value_id is not None or not record.rejection_code:
            raise AdapterValidationError("SOURCE_ROW_REJECTION_INVALID", "rejected row requires code and no candle value")
    else:
        raise AdapterValidationError("SOURCE_ROW_DISPOSITION_INVALID", "unsupported source-row disposition")
    return {
        "source_row_id": record.source_row_id,
        "member_id": record.member_id,
        "physical_record_ordinal": record.physical_record_ordinal,
        "data_row_ordinal": record.data_row_ordinal,
        "raw_fields": parsed,
        "raw_fields_json": record.raw_fields_json,
        "raw_row_digest": record.raw_row_digest,
        "parser_contract_id": record.parser_contract_id,
        "parser_source_sha": record.parser_source_sha,
        "importer_contract_id": record.importer_contract_id,
        "importer_source_sha": record.importer_source_sha,
        "exchange": record.exchange,
        "market_type": record.market_type,
        "symbol": record.symbol,
        "timeframe": record.timeframe,
        "open_time_ms": record.open_time_ms,
        "candle_value_id": record.candle_value_id,
        "disposition": record.disposition,
        "rejection_code": record.rejection_code,
    }


def project_pair_record(record: PairRecord) -> dict[str, object]:
    """Project physical candidate_member_count to S3 member_count."""
    if not isinstance(record, PairRecord):
        raise AdapterValidationError("ADAPTER_RECORD_TYPE_INVALID", "pair must be PairRecord")
    result = {
        "pair_id": record.pair_id,
        "zip_object_id": record.zip_object_id,
        "sidecar_object_id": record.sidecar_object_id,
        "zip_size_bytes": record.zip_size_bytes,
        "zip_sha256": record.zip_sha256,
        "sidecar_size_bytes": record.sidecar_size_bytes,
        "sidecar_sha256": record.sidecar_sha256,
        "sidecar_asserted_zip_sha256": record.sidecar_asserted_zip_sha256,
        "sidecar_assertion_matches": record.assertion_matches,
        "zip_crc_ok": record.zip_crc_ok,
        "member_count": record.candidate_member_count,
        "structural_ok": record.structural_ok,
        "disposition": record.disposition,
        "failure_code": record.failure_code,
    }
    if record.disposition == "VERIFIED":
        required = (
            record.zip_size_bytes, record.zip_sha256, record.sidecar_size_bytes,
            record.sidecar_sha256, record.sidecar_asserted_zip_sha256,
            record.assertion_matches, record.zip_crc_ok,
            record.candidate_member_count, record.structural_ok,
        )
        if any(value is None for value in required):
            raise AdapterValidationError("PAIR_PROJECTION_INCOMPLETE", "VERIFIED pair has missing evidence")
        if (record.assertion_matches != 1 or record.zip_crc_ok != 1
                or record.candidate_member_count != 1 or record.structural_ok != 1
                or record.failure_code is not None):
            raise AdapterValidationError("PAIR_PROJECTION_INVALID", "VERIFIED pair does not satisfy S3 profile")
    elif record.disposition == "QUARANTINED":
        if not record.failure_code:
            raise AdapterValidationError("PAIR_PROJECTION_INVALID", "QUARANTINED pair requires failure code")
    else:
        raise AdapterValidationError("PAIR_DISPOSITION_INVALID", "unsupported pair disposition")
    return result


def derive_object_attempt_summary(
    *, object_id: str, attempts: Sequence[AttemptRecord], successful_attempt_id: str | None
) -> dict[str, object]:
    """Derive object attempt_count and validate same-object successful relation."""
    _required_text(object_id, "object_id")
    if not isinstance(attempts, (tuple, list)):
        raise AdapterValidationError("ATTEMPT_HISTORY_INVALID", "attempts must be an ordered sequence")
    ordered = tuple(attempts)
    numbers: list[int] = []
    identifiers: set[str] = set()
    transferred: list[AttemptRecord] = []
    for attempt in ordered:
        if not isinstance(attempt, AttemptRecord) or attempt.object_id != object_id:
            raise AdapterValidationError("ATTEMPT_OBJECT_MISMATCH", "attempt belongs to another object")
        if attempt.attempt_id in identifiers:
            raise AdapterValidationError("ATTEMPT_ID_DUPLICATE", "attempt IDs must be unique")
        identifiers.add(attempt.attempt_id)
        numbers.append(validate_sqlite_integer(attempt.attempt_number, "attempt_number"))
        if attempt.outcome == "TRANSFERRED":
            transferred.append(attempt)
    if numbers != list(range(1, len(numbers) + 1)):
        raise AdapterValidationError("ATTEMPT_SEQUENCE_INVALID", "attempt numbers must be contiguous from one")
    if successful_attempt_id is None:
        if transferred:
            raise AdapterValidationError("SUCCESSFUL_ATTEMPT_RELATION_INVALID", "transferred attempt lacks success relation")
    else:
        matches = [item for item in transferred if item.attempt_id == successful_attempt_id]
        if len(transferred) != 1 or len(matches) != 1:
            raise AdapterValidationError("SUCCESSFUL_ATTEMPT_RELATION_INVALID", "success relation must reference the unique transferred attempt")
    return {"attempt_count": len(ordered), "successful_attempt_id": successful_attempt_id}



_NULLABLE_DTO_FIELDS = frozenset({
    "requested_key", "expected_size_bytes", "expected_sha256",
    "measured_size_bytes", "measured_sha256", "response_status",
    "local_relative_path", "exclusive_create", "retrieval_source",
    "workflow_run_id", "workflow_job_id", "workflow_event", "trigger_sha",
    "checkout_sha", "retrieved_at_utc", "failure_code", "finished_at_utc",
    "failure_subtype", "response_bytes_received", "partial_body_sha256",
    "complete_object_sha256", "zip_size_bytes", "zip_sha256",
    "sidecar_size_bytes", "sidecar_sha256", "sidecar_asserted_zip_sha256",
    "assertion_matches", "zip_crc_ok", "candidate_member_count", "structural_ok",
    "member_id", "member_path", "member_size_bytes", "member_sha256",
    "encoding", "bom_present", "newline", "delimiter", "header_present",
    "header_contract_id", "parser_contract_id", "parser_source_sha",
    "data_row_count", "first_open_time_ms", "last_open_time_ms",
    "exchange", "market_type", "symbol", "timeframe", "open_time_ms",
    "candle_value_id", "rejection_code", "failure_detail_code",
    "evidence_sha256", "reason_code", "candidate_snapshot_sha256",
    "validator_payload_sha256",
})
_INTEGER_DTO_FIELDS = frozenset({
    "singleton_key", "expected_size_bytes", "measured_size_bytes",
    "response_bytes_total", "response_status", "exclusive_create",
    "attempt_number", "response_bytes_received", "is_complete_object",
    "zip_size_bytes", "sidecar_size_bytes", "assertion_matches", "zip_crc_ok",
    "candidate_member_count", "structural_ok", "central_directory_ordinal",
    "member_size_bytes", "bom_present", "header_present", "data_row_count",
    "first_open_time_ms", "last_open_time_ms", "physical_record_ordinal",
    "data_row_ordinal", "open_time_ms", "available_at_ms", "failure_ordinal",
    "event_seq",
})
_POSITIVE_DTO_INTEGER_FIELDS = frozenset({
    "singleton_key", "attempt_number", "central_directory_ordinal",
    "physical_record_ordinal", "data_row_ordinal", "failure_ordinal", "event_seq",
})
_FLAG_DTO_INTEGER_FIELDS = frozenset({
    "exclusive_create", "is_complete_object", "assertion_matches", "zip_crc_ok",
    "structural_ok", "bom_present", "header_present",
})


class _StrictPhysicalDTO:
    __slots__ = ()

    def __post_init__(self) -> None:
        for item in fields(self):
            name = item.name
            value = getattr(self, name)
            if value is None:
                if name not in _NULLABLE_DTO_FIELDS:
                    raise TypeError(f"{name} may not be null")
                continue
            if name == "inventory_raw_bytes":
                if type(value) is not bytes:
                    raise TypeError("inventory_raw_bytes must be exact bytes")
                continue
            if name in _INTEGER_DTO_FIELDS:
                validate_sqlite_integer(value, name)
                if name in _POSITIVE_DTO_INTEGER_FIELDS and value == 0:
                    raise AdapterValidationError("DTO_INTEGER_INVALID", f"{name} must be positive")
                if name in _FLAG_DTO_INTEGER_FIELDS and value not in (0, 1):
                    raise AdapterValidationError("DTO_FLAG_INVALID", f"{name} must be 0 or 1")
                if name == "singleton_key" and value != 1:
                    raise AdapterValidationError("DTO_SINGLETON_INVALID", "singleton_key must equal 1")
                if name == "response_status" and not 100 <= value <= 599:
                    raise AdapterValidationError("DTO_HTTP_STATUS_INVALID", "response_status must be 100..599")
                continue
            if type(value) is not str:
                raise TypeError(f"{name} must be text")
            _required_text(value, name)
            if name.endswith("sha256") or name == "raw_row_digest":
                _sha(value, _SHA256_RE, name)
            elif name in {
                "parser_source_sha", "importer_source_sha", "trigger_sha", "checkout_sha"
            }:
                _sha(value, _SHA1_RE, name)


# Canonical S1.2 physical-row DTOs. These are deliberately distinct from the
# legacy S3-shaped records above: they preserve every physical schema column.
import sqlite3


@dataclass(frozen=True, slots=True)
class RunEnvelope(_StrictPhysicalDTO):
    singleton_key: int
    run_id: str
    inventory_id: str
    inventory_blob_sha256: str
    inventory_raw_bytes: bytes
    label: str
    parser_contract_id: str
    parser_source_sha: str
    importer_source_sha: str
    schema_contract_id: str
    schema_fingerprint_sha256: str
    created_at_utc: str
    coverage_manifest_json: str
    coverage_manifest_sha256: str


@dataclass(frozen=True, slots=True)
class ObjectEvidence(_StrictPhysicalDTO):
    object_id: str
    inventory_id: str
    inventory_blob_sha256: str
    inventory_entry_identity: str
    object_key: str
    object_kind: str
    timeframe: str
    partition: str
    period: str
    paired_object_key: str
    requested_key: str | None
    expected_size_bytes: int | None
    expected_sha256: str | None
    measured_size_bytes: int | None
    measured_sha256: str | None
    response_bytes_total: int
    response_status: int | None
    local_relative_path: str | None
    exclusive_create: int | None
    retrieval_source: str | None
    workflow_run_id: str | None
    workflow_job_id: str | None
    workflow_event: str | None
    trigger_sha: str | None
    checkout_sha: str | None
    retrieved_at_utc: str | None
    verification_status: str
    failure_code: str | None


@dataclass(frozen=True, slots=True)
class AttemptEvidence(_StrictPhysicalDTO):
    attempt_id: str
    object_id: str
    attempt_number: int
    workflow_run_id: str
    workflow_job_id: str
    workflow_event: str
    trigger_sha: str
    checkout_sha: str
    requested_key: str
    expected_size_bytes: int
    expected_sha256: str
    started_at_utc: str
    finished_at_utc: str | None
    outcome: str
    failure_subtype: str | None
    response_status: int | None
    response_bytes_received: int | None
    is_complete_object: int
    partial_body_sha256: str | None
    complete_object_sha256: str | None
    failure_code: str | None


@dataclass(frozen=True, slots=True)
class SuccessfulAttempt(_StrictPhysicalDTO):
    object_id: str
    attempt_id: str


@dataclass(frozen=True, slots=True)
class PairEvidence(_StrictPhysicalDTO):
    pair_id: str
    zip_object_id: str
    sidecar_object_id: str
    zip_size_bytes: int | None
    zip_sha256: str | None
    sidecar_size_bytes: int | None
    sidecar_sha256: str | None
    sidecar_asserted_zip_sha256: str | None
    assertion_matches: int | None
    zip_crc_ok: int | None
    candidate_member_count: int | None
    structural_ok: int | None
    disposition: str
    failure_code: str | None


@dataclass(frozen=True, slots=True)
class MemberCandidateEvidence(_StrictPhysicalDTO):
    candidate_id: str
    member_id: str | None
    pair_id: str
    central_directory_ordinal: int
    member_path: str | None
    member_size_bytes: int | None
    member_sha256: str | None
    encoding: str | None
    bom_present: int | None
    newline: str | None
    delimiter: str | None
    header_present: int | None
    header_contract_id: str | None
    parser_contract_id: str | None
    parser_source_sha: str | None
    data_row_count: int | None
    first_open_time_ms: int | None
    last_open_time_ms: int | None
    disposition: str
    failure_code: str | None


@dataclass(frozen=True, slots=True)
class SourceRowEvidence(_StrictPhysicalDTO):
    source_row_id: str
    member_id: str
    physical_record_ordinal: int
    data_row_ordinal: int
    raw_fields_json: str
    raw_row_digest: str
    parser_contract_id: str
    parser_source_sha: str
    importer_contract_id: str
    importer_source_sha: str
    exchange: str | None
    market_type: str | None
    symbol: str | None
    timeframe: str | None
    open_time_ms: int | None
    candle_value_id: str | None
    disposition: str
    rejection_code: str | None


@dataclass(frozen=True, slots=True)
class CandleEvidence(_StrictPhysicalDTO):
    exchange: str
    market_type: str
    symbol: str
    timeframe: str
    open_time_ms: int
    open: str
    high: str
    low: str
    close: str
    volume: str
    available_at_ms: int
    availability_kind: str
    candle_value_id: str


@dataclass(frozen=True, slots=True)
class CandleLinkEvidence(_StrictPhysicalDTO):
    link_id: str
    exchange: str
    market_type: str
    symbol: str
    timeframe: str
    open_time_ms: int
    source_row_id: str
    candle_value_id: str
    duplicate_disposition: str


@dataclass(frozen=True, slots=True)
class FailureObservation(_StrictPhysicalDTO):
    subject_kind: str
    subject_id: str
    failure_ordinal: int
    failure_code: str
    failure_detail_code: str | None
    observed_at_utc: str
    evidence_sha256: str | None


@dataclass(frozen=True, slots=True)
class RunEvent(_StrictPhysicalDTO):
    run_id: str
    event_seq: int
    event_type: str
    occurred_at_utc: str
    reason_code: str | None
    candidate_snapshot_sha256: str | None
    validator_payload_sha256: str | None


@dataclass(frozen=True, slots=True)
class StagingProjection:
    run: RunEnvelope
    objects: tuple[ObjectEvidence, ...]
    attempts: tuple[AttemptEvidence, ...]
    successful_attempts: tuple[SuccessfulAttempt, ...]
    pairs: tuple[PairEvidence, ...]
    members: tuple[MemberCandidateEvidence, ...]
    source_rows: tuple[SourceRowEvidence, ...]
    candles: tuple[CandleEvidence, ...]
    links: tuple[CandleLinkEvidence, ...]
    failure_observations: tuple[FailureObservation, ...]
    run_events: tuple[RunEvent, ...]


_RELATION_SPECS = (
    ("run_events", RunEvent,
     ("run_id", "event_seq", "event_type", "occurred_at_utc", "reason_code",
      "candidate_snapshot_sha256", "validator_payload_sha256"),
     "run_id,event_seq"),
    ("archive_objects", ObjectEvidence,
     ("object_id", "inventory_id", "inventory_blob_sha256", "inventory_entry_identity",
      "object_key", "object_kind", "timeframe", "partition", "period", "paired_object_key",
      "requested_key", "expected_size_bytes", "expected_sha256", "measured_size_bytes",
      "measured_sha256", "response_bytes_total", "response_status", "local_relative_path",
      "exclusive_create", "retrieval_source", "workflow_run_id", "workflow_job_id",
      "workflow_event", "trigger_sha", "checkout_sha", "retrieved_at_utc",
      "verification_status", "failure_code"),
     "object_id"),
    ("acquisition_attempts", AttemptEvidence,
     ("attempt_id", "object_id", "attempt_number", "workflow_run_id", "workflow_job_id",
      "workflow_event", "trigger_sha", "checkout_sha", "requested_key", "expected_size_bytes",
      "expected_sha256", "started_at_utc", "finished_at_utc", "outcome", "failure_subtype",
      "response_status", "response_bytes_received", "is_complete_object",
      "partial_body_sha256", "complete_object_sha256", "failure_code"),
     "object_id,attempt_number,attempt_id"),
    ("object_successful_attempt", SuccessfulAttempt,
     ("object_id", "attempt_id"), "object_id"),
    ("archive_pairs", PairEvidence,
     ("pair_id", "zip_object_id", "sidecar_object_id", "zip_size_bytes", "zip_sha256",
      "sidecar_size_bytes", "sidecar_sha256", "sidecar_asserted_zip_sha256",
      "assertion_matches", "zip_crc_ok", "candidate_member_count", "structural_ok",
      "disposition", "failure_code"), "pair_id"),
    ("csv_members", MemberCandidateEvidence,
     ("candidate_id", "member_id", "pair_id", "central_directory_ordinal", "member_path",
      "member_size_bytes", "member_sha256", "encoding", "bom_present", "newline",
      "delimiter", "header_present", "header_contract_id", "parser_contract_id",
      "parser_source_sha", "data_row_count", "first_open_time_ms", "last_open_time_ms",
      "disposition", "failure_code"),
     "pair_id,central_directory_ordinal,candidate_id"),
    ("source_rows", SourceRowEvidence,
     ("source_row_id", "member_id", "physical_record_ordinal", "data_row_ordinal",
      "raw_fields_json", "raw_row_digest", "parser_contract_id", "parser_source_sha",
      "importer_contract_id", "importer_source_sha", "exchange", "market_type", "symbol",
      "timeframe", "open_time_ms", "candle_value_id", "disposition", "rejection_code"),
     "member_id,physical_record_ordinal,source_row_id"),
    ("candles", CandleEvidence,
     ("exchange", "market_type", "symbol", "timeframe", "open_time_ms", "open", "high",
      "low", "close", "volume", "available_at_ms", "availability_kind", "candle_value_id"),
     "exchange,market_type,symbol,timeframe,open_time_ms"),
    ("candle_provenance_links", CandleLinkEvidence,
     ("link_id", "exchange", "market_type", "symbol", "timeframe", "open_time_ms",
      "source_row_id", "candle_value_id", "duplicate_disposition"),
     "source_row_id,link_id"),
    ("failure_observations", FailureObservation,
     ("subject_kind", "subject_id", "failure_ordinal", "failure_code",
      "failure_detail_code", "observed_at_utc", "evidence_sha256"),
     "subject_kind,subject_id,failure_ordinal"),
)


def _read_relation(
    connection: sqlite3.Connection, table: str, dto_type: type,
    columns: tuple[str, ...], order_by: str,
) -> tuple:
    sql = f"SELECT {', '.join(columns)} FROM {table} ORDER BY {order_by}"
    cursor = connection.execute(sql)
    names = tuple(item[0] for item in cursor.description)
    return tuple(dto_type(**dict(zip(names, row))) for row in cursor.fetchall())


def project_staging_database(connection: sqlite3.Connection) -> StagingProjection:
    """Read a complete immutable snapshot from a caller-owned connection only."""
    if not isinstance(connection, sqlite3.Connection):
        raise AdapterValidationError(
            "STAGING_CONNECTION_INVALID", "connection must be an open sqlite3.Connection"
        )
    from market_data.archive_staging_schema import verify_staging_database

    savepoint = "t0_adapter_projection"
    connection.execute(f"SAVEPOINT {savepoint}")
    try:
        if not verify_staging_database(connection):
            raise AdapterValidationError(
                "STAGING_SCHEMA_INVALID", "staging schema, fingerprint or integrity check failed"
            )
        run_columns = (
            "singleton_key", "run_id", "inventory_id", "inventory_blob_sha256",
            "inventory_raw_bytes", "label", "parser_contract_id", "parser_source_sha",
            "importer_source_sha", "schema_contract_id", "schema_fingerprint_sha256",
            "created_at_utc", "coverage_manifest_json", "coverage_manifest_sha256",
        )
        rows = connection.execute(
            f"SELECT {', '.join(run_columns)} FROM reconstruction_run ORDER BY singleton_key"
        ).fetchall()
        if len(rows) != 1:
            raise AdapterValidationError(
                "RUN_ENVELOPE_CARDINALITY_INVALID", "exactly one reconstruction run is required"
            )
        run = RunEnvelope(**dict(zip(run_columns, rows[0])))
        projected = {}
        for table, dto_type, columns, order_by in _RELATION_SPECS:
            projected[table] = _read_relation(
                connection, table, dto_type, columns, order_by
            )
        events = projected["run_events"]
        if (not events or events[0].run_id != run.run_id
                or events[0].event_seq != 1 or events[0].event_type != "BUILDING"
                or sum(1 for event in events if event.event_seq == 1) != 1):
            raise AdapterValidationError(
                "INITIAL_BUILDING_EVENT_INVALID",
                "exactly one initial BUILDING event at sequence 1 is required",
            )
        if any(event.run_id != run.run_id for event in events):
            raise AdapterValidationError(
                "RUN_EVENT_IDENTITY_INVALID", "run event references a different run"
            )
        connection.execute(f"RELEASE SAVEPOINT {savepoint}")
        return StagingProjection(
            run=run,
            objects=projected["archive_objects"],
            attempts=projected["acquisition_attempts"],
            successful_attempts=projected["object_successful_attempt"],
            pairs=projected["archive_pairs"],
            members=projected["csv_members"],
            source_rows=projected["source_rows"],
            candles=projected["candles"],
            links=projected["candle_provenance_links"],
            failure_observations=projected["failure_observations"],
            run_events=events,
        )
    except Exception:
        try:
            connection.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
            connection.execute(f"RELEASE SAVEPOINT {savepoint}")
        except sqlite3.Error:
            pass
        raise


__all__ = (
    "RunEnvelope", "ObjectEvidence", "AttemptEvidence", "SuccessfulAttempt",
    "PairEvidence", "MemberCandidateEvidence", "SourceRowEvidence",
    "CandleEvidence", "CandleLinkEvidence", "FailureObservation", "RunEvent",
    "StagingProjection", "project_staging_database",
)


@dataclass(frozen=True, slots=True)
class GraphValidationResult:
    valid: bool
    error_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.valid) is not bool or not isinstance(self.error_codes, tuple):
            raise TypeError("invalid graph validation result")
        if any(type(code) is not str or not code for code in self.error_codes):
            raise TypeError("graph error codes must be non-empty strings")
        if len(set(self.error_codes)) != len(self.error_codes):
            raise ValueError("graph error codes must be unique")
        if self.valid is not (not self.error_codes):
            raise ValueError("valid must be true exactly when error_codes is empty")


_GRAPH_ERROR_ORDER = (
    "PROJECTION_ENVELOPE_INVALID",
    "RUN_EVENT_SEQUENCE_INVALID",
    "RUN_EVENT_TRANSITION_INVALID",
    "RUN_EVENT_TIME_INVALID",
    "RUN_CANDIDATE_EVENT_INVALID",
    "ATTEMPT_GRAPH_INVALID",
    "SUCCESSFUL_ATTEMPT_GRAPH_INVALID",
    "PAIR_OBJECT_GRAPH_INVALID",
    "MEMBER_PAIR_GRAPH_INVALID",
    "SOURCE_ROW_MEMBER_GRAPH_INVALID",
    "CANDLE_LINK_GRAPH_INVALID",
    "FAILURE_OBSERVATION_ORPHAN",
    "FAILURE_OBSERVATION_SEQUENCE_INVALID",
)


def _strict_json_loads(raw: str | bytes, field: str) -> object:
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-standard JSON constant in {field}: {value}")

    try:
        return json.loads(
            raw, object_pairs_hook=_reject_duplicate_json_keys,
            parse_constant=reject_constant,
        )
    except (TypeError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise AdapterValidationError(
            "PROJECTION_JSON_INVALID", f"{field} is not strict JSON"
        ) from exc


def _dto_mapping(record: object, *, exclude: frozenset[str] = frozenset()) -> dict[str, object]:
    if not hasattr(record, "__dataclass_fields__"):
        raise AdapterValidationError("ADAPTER_RECORD_TYPE_INVALID", "projection row is not a DTO")
    return {
        item.name: getattr(record, item.name)
        for item in fields(record)
        if item.name not in exclude
    }


def build_s3_v1_payload(projection: StagingProjection) -> dict[str, object]:
    """Build the unchanged S3/V1 payload from an immutable physical-row snapshot."""
    if not isinstance(projection, StagingProjection):
        raise AdapterValidationError("PROJECTION_TYPE_INVALID", "projection must be StagingProjection")
    run = projection.run
    if hashlib.sha256(run.inventory_raw_bytes).hexdigest() != run.inventory_blob_sha256:
        raise AdapterValidationError(
            "INVENTORY_RAW_BYTES_INVALID", "inventory BLOB digest does not match run envelope"
        )
    if hashlib.sha256(run.coverage_manifest_json.encode("utf-8")).hexdigest() != run.coverage_manifest_sha256:
        raise AdapterValidationError(
            "COVERAGE_MANIFEST_DIGEST_INVALID", "coverage manifest digest does not match run envelope"
        )
    inventory = _strict_json_loads(run.inventory_raw_bytes, "inventory_raw_bytes")
    coverage_manifest = _strict_json_loads(run.coverage_manifest_json, "coverage_manifest_json")
    if not isinstance(inventory, dict) or inventory.get("inventory_id") != run.inventory_id:
        raise AdapterValidationError(
            "INVENTORY_IDENTITY_INVALID", "inventory bytes do not identify the run inventory"
        )
    if not isinstance(inventory.get("objects"), list) or not isinstance(coverage_manifest, dict):
        raise AdapterValidationError(
            "PROJECTION_ENVELOPE_INVALID", "inventory objects and coverage manifest must be JSON collections"
        )

    candidate_events = tuple(
        event for event in projection.run_events
        if event.run_id == run.run_id and event.event_type == "CANDIDATE"
    )
    if len(candidate_events) != 1:
        raise AdapterValidationError(
            "RUN_CANDIDATE_EVENT_INVALID", "exactly one immutable CANDIDATE event is required"
        )

    attempts_by_object: dict[str, list[AttemptEvidence]] = {}
    for attempt in projection.attempts:
        attempts_by_object.setdefault(attempt.object_id, []).append(attempt)
    success_by_object: dict[str, list[SuccessfulAttempt]] = {}
    for relation in projection.successful_attempts:
        success_by_object.setdefault(relation.object_id, []).append(relation)

    objects: list[dict[str, object]] = []
    for evidence in projection.objects:
        attempts = attempts_by_object.get(evidence.object_id, [])
        successes = success_by_object.get(evidence.object_id, [])
        if len(successes) > 1:
            raise AdapterValidationError(
                "SUCCESSFUL_ATTEMPT_GRAPH_INVALID", "object has multiple successful-attempt relations"
            )
        object_payload = _dto_mapping(evidence)
        object_payload["attempt_count"] = len(attempts)
        object_payload["successful_attempt_id"] = successes[0].attempt_id if successes else None
        objects.append(object_payload)

    attempts_payload = tuple(
        _dto_mapping(item, exclude=frozenset({"failure_subtype"}))
        for item in projection.attempts
    )
    pairs_payload = tuple({
        "pair_id": item.pair_id,
        "zip_object_id": item.zip_object_id,
        "sidecar_object_id": item.sidecar_object_id,
        "measured_zip_size_bytes": item.zip_size_bytes,
        "measured_zip_sha256": item.zip_sha256,
        "measured_sidecar_size_bytes": item.sidecar_size_bytes,
        "measured_sidecar_sha256": item.sidecar_sha256,
        "sidecar_asserted_zip_sha256": item.sidecar_asserted_zip_sha256,
        "sidecar_assertion_matches": item.assertion_matches,
        "zip_crc_ok": item.zip_crc_ok,
        "member_count": item.candidate_member_count,
        "structural_ok": item.structural_ok,
        "disposition": item.disposition,
        "failure_code": item.failure_code,
    } for item in projection.pairs)
    members_payload = tuple(
        _dto_mapping(item, exclude=frozenset({"candidate_id"}))
        for item in projection.members
    )

    rows_payload: list[dict[str, object]] = []
    for item in projection.source_rows:
        row = _dto_mapping(item)
        raw_fields = _strict_json_loads(item.raw_fields_json, "raw_fields_json")
        if (not isinstance(raw_fields, list) or len(raw_fields) != 12
                or any(type(value) is not str for value in raw_fields)
                or json.dumps(raw_fields, ensure_ascii=False, separators=(",", ":")) != item.raw_fields_json):
            raise AdapterValidationError(
                "SOURCE_ROW_RAW_FIELDS_INVALID", "raw_fields_json must be canonical twelve-string JSON"
            )
        row["raw_fields"] = raw_fields
        if all(value is not None for value in (
            item.exchange, item.market_type, item.symbol, item.timeframe, item.open_time_ms
        )):
            row["natural_key"] = (
                item.exchange, item.market_type, item.symbol, item.timeframe, item.open_time_ms
            )
        rows_payload.append(row)

    links_payload: list[dict[str, object]] = []
    for item in projection.links:
        link = _dto_mapping(item)
        link["natural_key"] = (
            item.exchange, item.market_type, item.symbol, item.timeframe, item.open_time_ms
        )
        links_payload.append(link)

    candidate = candidate_events[0]
    payload: dict[str, object] = {
        "inventory": inventory,
        "objects": tuple(objects),
        "pairs": pairs_payload,
        "members": members_payload,
        "attempts": attempts_payload,
        "source_rows": tuple(rows_payload),
        "candles": tuple(_dto_mapping(item) for item in projection.candles),
        "links": tuple(links_payload),
        "contract_version": "T0_PROVENANCE_VALIDATOR_S1_V1",
        "inventory_raw_bytes": run.inventory_raw_bytes,
        "inventory_expected_sha256": run.inventory_blob_sha256,
        "inventory_expected_id": run.inventory_id,
        "coverage_manifest": coverage_manifest,
        "run": {
            "run_id": run.run_id,
            "status": "CANDIDATE",
            "schema_contract_id": run.schema_contract_id,
        },
    }
    # Keep the event's immutable snapshot digest available to the graph gate,
    # without adding it to the unchanged public S3/V1 run envelope.
    if not candidate.candidate_snapshot_sha256:
        raise AdapterValidationError(
            "RUN_CANDIDATE_EVENT_INVALID", "CANDIDATE event lacks its snapshot digest"
        )
    return payload


def validate_staging_graph(projection: StagingProjection) -> GraphValidationResult:
    """Validate physical graph/lifecycle invariants plus the unchanged S3/V1 contract."""
    from datetime import datetime
    from market_data.archive_provenance_validator import (
        derive_attempt_id, encode_t0enc1, validate_provenance,
    )

    errors: set[str] = set()
    if not isinstance(projection, StagingProjection):
        return GraphValidationResult(False, ("PROJECTION_ENVELOPE_INVALID",))
    run_id = projection.run.run_id
    events = projection.run_events
    if not events or [item.event_seq for item in events] != list(range(1, len(events) + 1)):
        errors.add("RUN_EVENT_SEQUENCE_INVALID")
    if any(item.run_id != run_id for item in events):
        errors.add("RUN_EVENT_SEQUENCE_INVALID")
    if not events or events[0].event_type != "BUILDING":
        errors.add("RUN_EVENT_TRANSITION_INVALID")
    allowed = {
        "BUILDING": {"CANDIDATE", "QUARANTINED"},
        "CANDIDATE": {"VALIDATED", "QUARANTINED"},
        "QUARANTINED": set(),
        "VALIDATED": set(),
    }
    for previous, current in zip(events, events[1:]):
        if current.event_type not in allowed.get(previous.event_type, set()):
            errors.add("RUN_EVENT_TRANSITION_INVALID")
    if sum(item.event_type == "BUILDING" for item in events) != 1:
        errors.add("RUN_EVENT_TRANSITION_INVALID")
    candidate_events = [item for item in events if item.event_type == "CANDIDATE"]
    if len(candidate_events) != 1 or (events and events[-1].event_type not in ("CANDIDATE", "VALIDATED")):
        errors.add("RUN_CANDIDATE_EVENT_INVALID")
    parsed_times = []
    for event in events:
        try:
            timestamp = datetime.fromisoformat(event.occurred_at_utc.replace("Z", "+00:00"))
            if timestamp.tzinfo is None:
                raise ValueError("timezone required")
            parsed_times.append(timestamp)
        except (TypeError, ValueError):
            errors.add("RUN_EVENT_TIME_INVALID")
            parsed_times = []
            break
    if parsed_times and any(right < left for left, right in zip(parsed_times, parsed_times[1:])):
        errors.add("RUN_EVENT_TIME_INVALID")

    object_by_id = {item.object_id: item for item in projection.objects}
    object_by_key = {item.object_key: item for item in projection.objects}
    attempts_by_object: dict[str, list[AttemptEvidence]] = {}
    attempts_by_id = {}
    for attempt in projection.attempts:
        attempts_by_object.setdefault(attempt.object_id, []).append(attempt)
        if attempt.attempt_id in attempts_by_id:
            errors.add("ATTEMPT_GRAPH_INVALID")
        attempts_by_id[attempt.attempt_id] = attempt
    success_by_object: dict[str, list[SuccessfulAttempt]] = {}
    for relation in projection.successful_attempts:
        success_by_object.setdefault(relation.object_id, []).append(relation)
    for obj in projection.objects:
        history = sorted(attempts_by_object.get(obj.object_id, ()), key=lambda item: item.attempt_number)
        if not history or [item.attempt_number for item in history] != list(range(1, len(history) + 1)):
            errors.add("ATTEMPT_GRAPH_INVALID")
        for attempt in history:
            try:
                expected_id = derive_attempt_id(
                    object_id=attempt.object_id,
                    attempt_number=attempt.attempt_number,
                    workflow_run_id=attempt.workflow_run_id,
                    workflow_job_id=attempt.workflow_job_id,
                    trigger_sha=attempt.trigger_sha,
                    requested_key=attempt.requested_key,
                )
            except (TypeError, ValueError):
                expected_id = None
            if (expected_id != attempt.attempt_id or attempt.requested_key != obj.object_key
                    or attempt.expected_size_bytes != obj.expected_size_bytes
                    or attempt.expected_sha256 != obj.expected_sha256):
                errors.add("ATTEMPT_GRAPH_INVALID")
        successes = success_by_object.get(obj.object_id, [])
        transferred = [item for item in history if item.outcome == "TRANSFERRED"]
        if (len(successes) != 1 or len(transferred) != 1
                or successes[0].attempt_id != transferred[0].attempt_id):
            errors.add("SUCCESSFUL_ATTEMPT_GRAPH_INVALID")
        elif (transferred[0].response_bytes_received != obj.measured_size_bytes
              or transferred[0].complete_object_sha256 != obj.measured_sha256
              or transferred[0].is_complete_object != 1
              or obj.expected_size_bytes != obj.measured_size_bytes
              or obj.expected_sha256 != obj.measured_sha256):
            errors.add("SUCCESSFUL_ATTEMPT_GRAPH_INVALID")

    pair_by_id = {item.pair_id: item for item in projection.pairs}
    for pair in projection.pairs:
        zip_obj = object_by_id.get(pair.zip_object_id)
        sidecar_obj = object_by_id.get(pair.sidecar_object_id)
        if (zip_obj is None or sidecar_obj is None
                or zip_obj.object_kind != "ZIP"
                or sidecar_obj.object_kind != "CHECKSUM_SIDECAR"
                or zip_obj.paired_object_key != sidecar_obj.object_key
                or sidecar_obj.paired_object_key != zip_obj.object_key):
            errors.add("PAIR_OBJECT_GRAPH_INVALID")

    member_by_id = {item.member_id: item for item in projection.members if item.member_id is not None}
    for member in projection.members:
        if member.pair_id not in pair_by_id:
            errors.add("MEMBER_PAIR_GRAPH_INVALID")
        if member.member_id is not None and member.member_path is not None and member.member_sha256 is not None:
            expected_member_id = "mem1:" + hashlib.sha256(encode_t0enc1(
                "T0-CSV-MEMBER-V1", member.pair_id, member.member_path,
                bytes.fromhex(member.member_sha256),
            )).hexdigest()
            if member.member_id != expected_member_id:
                errors.add("MEMBER_PAIR_GRAPH_INVALID")

    row_by_id = {item.source_row_id: item for item in projection.source_rows}
    for row in projection.source_rows:
        if row.member_id not in member_by_id:
            errors.add("SOURCE_ROW_MEMBER_GRAPH_INVALID")
            continue
        try:
            raw_fields = _strict_json_loads(row.raw_fields_json, "raw_fields_json")
            if (not isinstance(raw_fields, list) or len(raw_fields) != 12
                    or any(type(value) is not str for value in raw_fields)
                    or json.dumps(raw_fields, ensure_ascii=False, separators=(",", ":")) != row.raw_fields_json):
                raise ValueError("raw fields invalid")
            raw_digest = hashlib.sha256(encode_t0enc1("T0-RAW-CSV-ROW-V1", *raw_fields)).hexdigest()
            expected_row_id = "row1:" + hashlib.sha256(encode_t0enc1(
                "T0-SOURCE-ROW-V1", row.member_id, row.physical_record_ordinal,
                bytes.fromhex(raw_digest),
            )).hexdigest()
            if raw_digest != row.raw_row_digest or expected_row_id != row.source_row_id:
                errors.add("SOURCE_ROW_MEMBER_GRAPH_INVALID")
        except (AdapterValidationError, TypeError, ValueError):
            errors.add("SOURCE_ROW_MEMBER_GRAPH_INVALID")

    candle_by_natural = {
        (item.exchange, item.market_type, item.symbol, item.timeframe, item.open_time_ms): item
        for item in projection.candles
    }
    links_by_source: dict[str, list[CandleLinkEvidence]] = {}
    for link in projection.links:
        links_by_source.setdefault(link.source_row_id, []).append(link)
        row = row_by_id.get(link.source_row_id)
        natural = (link.exchange, link.market_type, link.symbol, link.timeframe, link.open_time_ms)
        candle = candle_by_natural.get(natural)
        if (row is None or candle is None or row.candle_value_id != candle.candle_value_id
                or link.candle_value_id != candle.candle_value_id
                or (row.exchange, row.market_type, row.symbol, row.timeframe, row.open_time_ms) != natural):
            errors.add("CANDLE_LINK_GRAPH_INVALID")
    for row in projection.source_rows:
        if row.disposition == "ACCEPTED" and len(links_by_source.get(row.source_row_id, ())) != 1:
            errors.add("CANDLE_LINK_GRAPH_INVALID")
    for natural, candle in candle_by_natural.items():
        grouped = [
            link for link in projection.links
            if (link.exchange, link.market_type, link.symbol, link.timeframe, link.open_time_ms) == natural
        ]
        if not grouped:
            errors.add("CANDLE_LINK_GRAPH_INVALID")
            continue
        ordered = sorted(grouped, key=lambda item: item.source_row_id.encode("utf-8"))
        if any(
            item.duplicate_disposition != ("UNIQUE" if index == 0 else "IDENTICAL_DUPLICATE")
            for index, item in enumerate(ordered)
        ):
            errors.add("CANDLE_LINK_GRAPH_INVALID")

    subject_ids = {
        "RUN": {run_id},
        "OBJECT": set(object_by_id),
        "ATTEMPT": set(attempts_by_id),
        "PAIR": set(pair_by_id),
        "MEMBER": set(member_by_id),
        "SOURCE_ROW": set(row_by_id),
        "CANDLE": {item.candle_value_id for item in projection.candles},
        "LINK": {item.link_id for item in projection.links},
    }
    failure_groups: dict[tuple[str, str], list[int]] = {}
    for item in projection.failure_observations:
        key = (item.subject_kind, item.subject_id)
        if item.subject_id not in subject_ids.get(item.subject_kind, set()):
            errors.add("FAILURE_OBSERVATION_ORPHAN")
        failure_groups.setdefault(key, []).append(item.failure_ordinal)
    for ordinals in failure_groups.values():
        if sorted(ordinals) != list(range(1, len(ordinals) + 1)):
            errors.add("FAILURE_OBSERVATION_SEQUENCE_INVALID")

    try:
        payload = build_s3_v1_payload(projection)
        validation = validate_provenance(payload)
        errors.update(validation.error_codes)
    except AdapterValidationError:
        errors.add("PROJECTION_ENVELOPE_INVALID")

    ordered_errors = tuple(
        code for code in _GRAPH_ERROR_ORDER if code in errors
    )
    # Preserve the existing validator's frozen V1/S1 error ordering first.
    from market_data.archive_provenance_validator import _ERROR_CODE_ORDER
    ordered_errors = tuple(
        code for code in _ERROR_CODE_ORDER if code in errors
    ) + ordered_errors
    return GraphValidationResult(not ordered_errors, ordered_errors)


def project_staging_s3_v1_payload(connection: sqlite3.Connection) -> dict[str, object]:
    """Project and accept only a candidate snapshot that passes both graph and S3/V1 validation."""
    projection = project_staging_database(connection)
    result = validate_staging_graph(projection)
    if not result.valid:
        raise AdapterValidationError(
            "STAGING_GRAPH_INVALID", ",".join(result.error_codes)
        )
    return build_s3_v1_payload(projection)


__all__ = __all__ + (
    "GraphValidationResult", "build_s3_v1_payload",
    "validate_staging_graph", "project_staging_s3_v1_payload",
)
