"""Pure, deterministic validation helpers for T0 archive provenance V1.

This module deliberately performs no I/O. It validates caller-supplied evidence
mappings only; acquisition, persistence, archive parsing and database operations
belong to separately approved components.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import re
import struct


_ERROR_CODE_ORDER = (
    "PROVENANCE_INPUT_SHAPE_INVALID",
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
_REQUIRED_PAYLOAD_KEYS = (
    "inventory", "objects", "pairs", "members", "attempts",
    "source_rows", "candles", "links",
)
_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
_TIMEFRAME_INTERVAL_MS = {"15m": 900_000, "1h": 3_600_000}
_VALUE_FIELDS = (
    "open", "high", "low", "close", "volume", "available_at_ms", "availability_kind",
)


@dataclass(frozen=True, slots=True)
class ProvenanceValidationResult:
    """Immutable outcome of a provenance validation pass."""

    valid: bool
    error_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.valid) is not bool or not isinstance(self.error_codes, tuple):
            raise TypeError("invalid provenance validation result")
        if any(not isinstance(code, str) for code in self.error_codes):
            raise TypeError("error_codes must contain strings")
        if len(set(self.error_codes)) != len(self.error_codes):
            raise ValueError("error_codes must be unique")
        if any(code not in _ERROR_CODE_ORDER for code in self.error_codes):
            raise ValueError("error_codes must use stable V1 codes")
        if tuple(code for code in _ERROR_CODE_ORDER if code in self.error_codes) != self.error_codes:
            raise ValueError("error_codes must follow the V1 catalogue order")
        if self.valid is not (self.error_codes == ()):
            raise ValueError("valid must be true exactly when error_codes is empty")


def _encode_text(value: str) -> bytes:
    try:
        return value.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise ValueError("text is not valid UTF-8") from exc


def encode_t0enc1(domain: str, *fields: str | bytes | int | None) -> bytes:
    """Encode typed fields using the frozen T0ENC1 length-delimited framing."""
    if type(domain) is not str:
        raise TypeError("domain must be a string")
    if not domain:
        raise ValueError("domain must not be empty")
    domain_bytes = _encode_text(domain)
    if len(domain_bytes) > 0xFFFFFFFF:
        raise ValueError("domain is too long for T0ENC1")
    if len(fields) > 0xFFFFFFFF:
        raise ValueError("too many T0ENC1 fields")

    encoded_fields: list[bytes | None] = []
    for field in fields:
        if field is None:
            encoded_fields.append(None)
        elif type(field) is str:
            encoded_fields.append(_encode_text(field))
        elif type(field) is bytes:
            encoded_fields.append(field)
        elif type(field) is int:
            encoded_fields.append(str(field).encode("ascii"))
        else:
            raise TypeError("T0ENC1 fields must be str, bytes, int, or None")

    chunks = [b"T0ENC1\x00", struct.pack(">I", len(domain_bytes)), domain_bytes,
              struct.pack(">I", len(encoded_fields))]
    for value in encoded_fields:
        if value is None:
            chunks.extend((b"\x00", struct.pack(">Q", 0)))
        else:
            if len(value) > 0xFFFFFFFFFFFFFFFF:
                raise ValueError("field is too long for T0ENC1")
            chunks.extend((b"\x01", struct.pack(">Q", len(value)), value))
    return b"".join(chunks)


def derive_attempt_id(
    *,
    object_id: str,
    attempt_number: int,
    workflow_run_id: str,
    workflow_job_id: str,
    trigger_sha: str,
    requested_key: str,
) -> str:
    """Derive the stable, attempt-scoped ID specified by S1 §12.2."""
    if type(attempt_number) is not int:
        raise TypeError("attempt_number must be an integer, not bool")
    if not 1 <= attempt_number <= 0x7FFFFFFFFFFFFFFF:
        raise ValueError("attempt_number must be a positive signed-64-bit integer")
    values = (object_id, workflow_run_id, workflow_job_id, trigger_sha, requested_key)
    if any(type(value) is not str for value in values):
        raise TypeError("attempt identity fields must be strings")
    if any(not value for value in values):
        raise ValueError("attempt identity fields must not be empty")
    preimage = encode_t0enc1(
        "T0-ACQUISITION-ATTEMPT-V1", object_id, attempt_number,
        workflow_run_id, workflow_job_id, trigger_sha, requested_key,
    )
    return "att1:" + hashlib.sha256(preimage).hexdigest()


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and _SHA256_RE.fullmatch(value) is not None


def _paired_key(entry: Mapping[str, object]) -> object:
    for key in ("paired_object_key", "paired_sidecar_key", "paired_zip_key"):
        if key in entry:
            return entry[key]
    return None


def _inventory_is_complete(entries: list[Mapping[str, object]]) -> bool:
    if len(entries) != 404:
        return False
    keys: set[tuple[str, str]] = set()
    zip_entries: dict[str, Mapping[str, object]] = {}
    sidecar_entries: dict[str, Mapping[str, object]] = {}
    for entry in entries:
        key, kind = entry.get("object_key"), entry.get("object_kind")
        if not isinstance(key, str) or not key or kind not in ("ZIP", "CHECKSUM_SIDECAR"):
            return False
        identity = (key, kind)
        if identity in keys:
            return False
        keys.add(identity)
        if kind == "ZIP":
            zip_entries[key] = entry
        else:
            sidecar_entries[key] = entry
    if len(zip_entries) != 202 or len(sidecar_entries) != 202:
        return False
    paired: set[tuple[str, str]] = set()
    for zip_key, zip_entry in zip_entries.items():
        sidecar_key = _paired_key(zip_entry)
        if not isinstance(sidecar_key, str) or sidecar_key not in sidecar_entries:
            return False
        sidecar_entry = sidecar_entries[sidecar_key]
        if _paired_key(sidecar_entry) != zip_key:
            return False
        pair = (zip_key, sidecar_key)
        if pair in paired:
            return False
        paired.add(pair)
    return len(paired) == 202 and len({sidecar for _, sidecar in paired}) == 202


def _hashable_tuple(values: tuple[object, ...]) -> tuple[object, ...] | None:
    try:
        hash(values)
    except TypeError:
        return None
    return values


def _record_identity(record: Mapping[str, object]) -> tuple[object, ...] | None:
    natural_key = record.get("natural_key")
    natural_identity = None
    if isinstance(natural_key, (list, tuple)) and len(natural_key) == 5:
        natural_identity = _hashable_tuple(tuple(natural_key))
    names = ("exchange", "market_type", "symbol", "timeframe", "open_time_ms")
    direct_identity = None
    if all(name in record for name in names):
        direct_identity = _hashable_tuple(tuple(record[name] for name in names))
    if natural_identity is not None and direct_identity is not None:
        return natural_identity if natural_identity == direct_identity else None
    return natural_identity if natural_identity is not None else direct_identity


def _value_signature(record: Mapping[str, object]) -> tuple[object, ...] | None:
    if all(name in record for name in _VALUE_FIELDS):
        return _hashable_tuple(tuple(record[name] for name in _VALUE_FIELDS))
    value_id = record.get("candle_value_id")
    if isinstance(value_id, str):
        return ("candle_value_id", value_id)
    return None


def _input_shape_valid(payload: object) -> bool:
    if not isinstance(payload, Mapping):
        return False
    if any(key not in payload for key in _REQUIRED_PAYLOAD_KEYS):
        return False
    inventory = payload.get("inventory")
    if not isinstance(inventory, Mapping):
        return False
    inventory_objects = inventory.get("objects")
    if not isinstance(inventory_objects, (list, tuple)):
        return False
    if any(not isinstance(item, Mapping) for item in inventory_objects):
        return False
    for key in _REQUIRED_PAYLOAD_KEYS[1:]:
        collection = payload.get(key)
        if not isinstance(collection, (list, tuple)):
            return False
        if any(not isinstance(item, Mapping) for item in collection):
            return False
    return True


def validate_provenance(payload: Mapping[str, object]) -> ProvenanceValidationResult:
    """Validate the frozen V1 provenance surface without mutating or accessing I/O."""
    if not _input_shape_valid(payload):
        return ProvenanceValidationResult(False, ("PROVENANCE_INPUT_SHAPE_INVALID",))

    # Shape validation above narrows these values to the declared mapping/sequence types.
    inventory = payload["inventory"]  # type: ignore[index]
    inventory_entries = list(inventory["objects"])  # type: ignore[index]
    objects = list(payload["objects"])  # type: ignore[index]
    pairs = list(payload["pairs"])  # type: ignore[index]
    members = list(payload["members"])  # type: ignore[index]
    attempts = list(payload["attempts"])  # type: ignore[index]
    source_rows = list(payload["source_rows"])  # type: ignore[index]
    candles = list(payload["candles"])  # type: ignore[index]
    links = list(payload["links"])  # type: ignore[index]

    errors: set[str] = set()
    if not _inventory_is_complete(inventory_entries):
        errors.add("INVENTORY_OBJECT_SET_INCOMPLETE")

    allowlisted = {
        (entry.get("object_key"), entry.get("object_kind"))
        for entry in inventory_entries
        if isinstance(entry.get("object_key"), str)
        and entry.get("object_kind") in ("ZIP", "CHECKSUM_SIDECAR")
    }
    evidence_identities: list[tuple[str, str]] = []
    for evidence in objects:
        key, kind = evidence.get("object_key"), evidence.get("object_kind")
        if isinstance(key, str) and isinstance(kind, str):
            evidence_identities.append((key, kind))
        if (not isinstance(key, str) or kind not in ("ZIP", "CHECKSUM_SIDECAR")
                or (key, kind) not in allowlisted or evidence.get("requested_key") != key):
            errors.add("OBJECT_NOT_IN_APPROVED_INVENTORY")
        if evidence.get("verification_status") == "QUARANTINED":
            errors.add("QUARANTINED_EVIDENCE_PRESENT")
    if len(objects) != 404 or len(set(evidence_identities)) != 404 or set(evidence_identities) != allowlisted:
        errors.add("INVENTORY_OBJECT_SET_INCOMPLETE")

    for pair in pairs:
        if pair.get("disposition") == "QUARANTINED":
            errors.add("QUARANTINED_EVIDENCE_PRESENT")
    for member in members:
        if member.get("disposition") == "QUARANTINED":
            errors.add("QUARANTINED_EVIDENCE_PRESENT")

    for attempt in attempts:
        outcome = attempt.get("outcome")
        if outcome == "UNKNOWN":
            errors.add("ATTEMPT_OUTCOME_UNKNOWN")
        if outcome == "TRANSFERRED":
            complete_flag = attempt.get("is_complete_object")
            byte_count = attempt.get("response_bytes_received")
            digest = attempt.get("complete_object_sha256")
            finished = attempt.get("finished_at_utc")
            if (type(complete_flag) is not int or complete_flag != 1
                    or type(byte_count) is not int or byte_count < 0
                    or not _is_sha256(digest)
                    or not isinstance(finished, str) or not finished):
                errors.add("TRANSFERRED_ATTEMPT_INCOMPLETE")

    verified_members_by_pair: dict[object, list[Mapping[str, object]]] = {}
    for member in members:
        if member.get("disposition") == "VERIFIED":
            pair_key = member.get("pair_id")
            if not isinstance(pair_key, str) or not pair_key:
                continue
            verified_members_by_pair.setdefault(pair_key, []).append(member)
    for pair in pairs:
        if pair.get("disposition") == "VERIFIED":
            pair_id = pair.get("pair_id")
            if not isinstance(pair_id, str) or not pair_id:
                pair_id = None
            matching = verified_members_by_pair.get(pair_id, [])
            if type(pair.get("member_count")) is not int or pair.get("member_count") != 1 or len(matching) != 1:
                errors.add("VERIFIED_PAIR_MEMBER_CARDINALITY_INVALID")

    links_by_source: dict[object, list[Mapping[str, object]]] = {}
    for link in links:
        source_key = link.get("source_row_id")
        if not isinstance(source_key, str) or not source_key:
            continue
        links_by_source.setdefault(source_key, []).append(link)
    for source_row in source_rows:
        if source_row.get("disposition") != "ACCEPTED":
            continue
        source_id = source_row.get("source_row_id")
        if not isinstance(source_id, str) or not source_id:
            source_id = None
        matching = links_by_source.get(source_id, [])
        if len(matching) != 1:
            errors.add("ACCEPTED_SOURCE_ROW_LINK_CARDINALITY_INVALID")
            continue
        link = matching[0]
        source_identity = _record_identity(source_row)
        link_identity = _record_identity(link)
        source_value_id = source_row.get("candle_value_id")
        link_value_id = link.get("candle_value_id")
        if (source_identity is None or link_identity is None
                or source_identity != link_identity
                or not isinstance(source_value_id, str)
                or not source_value_id.startswith("cv1:")
                or not _is_sha256(source_value_id[4:])
                or source_value_id != link_value_id):
            errors.add("ACCEPTED_SOURCE_ROW_LINK_CARDINALITY_INVALID")

    values_by_identity: dict[tuple[object, ...], set[tuple[object, ...]]] = {}
    for candle in candles:
        identity = _record_identity(candle)
        signature = _value_signature(candle)
        if identity is None:
            if "natural_key" in candle or any(
                name in candle for name in ("exchange", "market_type", "symbol", "timeframe", "open_time_ms")
            ):
                errors.add("CANDLE_IDENTITY_VALUE_CONFLICT")
            continue
        if signature is None:
            continue
        values_by_identity.setdefault(identity, set()).add(signature)
    if any(len(signatures) > 1 for signatures in values_by_identity.values()):
        errors.add("CANDLE_IDENTITY_VALUE_CONFLICT")

    for candle in candles:
        timeframe = candle.get("timeframe")
        open_time = candle.get("open_time_ms")
        available_at = candle.get("available_at_ms")
        interval = _TIMEFRAME_INTERVAL_MS.get(timeframe) if isinstance(timeframe, str) else None
        if (candle.get("availability_kind") != "BAR_CLOSE_BOUNDARY"
                or interval is None or type(open_time) is not int or open_time < 0
                or type(available_at) is not int or available_at != open_time + interval):
            errors.add("CANDLE_AVAILABILITY_BOUNDARY_INVALID")

    ordered_errors = tuple(code for code in _ERROR_CODE_ORDER if code in errors)
    return ProvenanceValidationResult(not ordered_errors, ordered_errors)


__all__ = (
    "ProvenanceValidationResult",
    "encode_t0enc1",
    "derive_attempt_id",
    "validate_provenance",
)
