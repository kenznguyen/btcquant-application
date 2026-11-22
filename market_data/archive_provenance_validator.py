"""Pure, deterministic validation helpers for T0 archive provenance V1.

This module deliberately performs no I/O. It validates caller-supplied evidence
mappings only; acquisition, persistence, archive parsing and database operations
belong to separately approved components.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import json
import re
import struct
from decimal import Decimal, InvalidOperation


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


def _validate_v1(payload: Mapping[str, object]) -> ProvenanceValidationResult:
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



_S1_VERSION = "T0_PROVENANCE_VALIDATOR_S1_V1"
_S1_ENVELOPE_KEYS = frozenset({"inventory_raw_bytes", "inventory_expected_sha256", "inventory_expected_id", "coverage_manifest", "run"})
_DECIMAL_RE = re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]*[1-9])?\Z")
_SHA1_RE = re.compile(r"[0-9a-f]{40}\Z")
_S1_CODE_ORDER = _ERROR_CODE_ORDER[10:]


def _strict_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_json_constant(value):
    raise ValueError("non-standard JSON constant: " + value)


def _s1_hash(domain, *fields):
    return hashlib.sha256(encode_t0enc1(domain, *fields)).hexdigest()


def _s1_id(prefix, domain, *fields):
    return prefix + _s1_hash(domain, *fields)


def _is_nonnegative_int(value):
    return type(value) is int and value >= 0


def _is_positive_int(value):
    return type(value) is int and value > 0


def _is_text(value):
    return type(value) is str and bool(value)


def _decimal_value(value):
    if type(value) is not str or _DECIMAL_RE.fullmatch(value) is None:
        return None
    try:
        number = Decimal(value)
    except InvalidOperation:
        return None
    return number if number.is_finite() else None


def _s1_validate(payload, errors):
    raw, expected_sha, expected_id = (payload.get("inventory_raw_bytes"),
                                      payload.get("inventory_expected_sha256"),
                                      payload.get("inventory_expected_id"))
    parsed = None
    raw_ok = type(raw) is bytes and _is_sha256(expected_sha)
    if raw_ok:
        raw_ok = hashlib.sha256(raw).hexdigest() == expected_sha
        try:
            parsed = json.loads(raw.decode("utf-8", errors="strict"),
                                object_pairs_hook=_strict_json_object,
                                parse_constant=_reject_json_constant)
            raw_ok = raw_ok and isinstance(parsed, dict)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError):
            raw_ok = False
    if not _is_text(expected_id) or not isinstance(parsed, dict) or parsed.get("inventory_id") != expected_id:
        raw_ok = False
    if not raw_ok:
        errors.add("INVENTORY_RAW_BYTES_INVALID")

    inventory = payload.get("inventory")
    supplied = inventory.get("objects") if isinstance(inventory, Mapping) else None
    raw_entries = parsed.get("objects") if isinstance(parsed, Mapping) else None
    inv_ok = raw_ok and isinstance(raw_entries, list) and isinstance(supplied, (list, tuple))
    if inv_ok:
        inv_ok = list(raw_entries) == list(supplied)
    keys, zips, sidecars = {}, {}, {}
    if inv_ok:
        for entry in raw_entries:
            if not isinstance(entry, Mapping):
                inv_ok = False
                break
            key, kind = entry.get("object_key"), entry.get("object_kind")
            if not _is_text(key) or key in keys or kind not in ("ZIP", "CHECKSUM_SIDECAR"):
                inv_ok = False
                break
            keys[key] = entry
            (zips if kind == "ZIP" else sidecars)[key] = entry
        if len(raw_entries) != 404 or len(zips) != 202 or len(sidecars) != 202:
            inv_ok = False
        paired = set()
        for zip_key, entry in zips.items():
            sidecar_key = entry.get("paired_object_key")
            sidecar = sidecars.get(sidecar_key) if isinstance(sidecar_key, str) else None
            if sidecar is None or sidecar.get("paired_object_key") != zip_key or sidecar_key in paired:
                inv_ok = False
                break
            paired.add(sidecar_key)
        if len(paired) != 202:
            inv_ok = False
    if not inv_ok:
        errors.add("INVENTORY_OBJECT_SET_MISMATCH")

    names = ("objects", "attempts", "pairs", "members", "source_rows", "candles", "links")
    groups = [payload.get(name) for name in names]
    if any(not isinstance(group, (list, tuple)) for group in groups):
        errors.add("RUN_ACCEPTANCE_INVARIANT_INVALID")
        return
    objects, attempts, pairs, members, rows, candles, links = [list(group) for group in groups]
    if any(not isinstance(item, Mapping) for group in groups for item in group):
        errors.add("RUN_ACCEPTANCE_INVARIANT_INVALID")
        return

    object_by_key, object_by_id, object_bad = {}, {}, False
    inventory_sha = expected_sha if _is_sha256(expected_sha) else ""
    for obj in objects:
        key, kind = obj.get("object_key"), obj.get("object_kind")
        if not _is_text(key) or key in object_by_key:
            object_bad = True
            continue
        object_by_key[key] = obj
        oid = _s1_id("obj1:", "T0-ARCHIVE-OBJECT-V1", inventory_sha, key, kind if isinstance(kind, str) else "")
        entry = keys.get(key)
        if raw_ok and (obj.get("object_id") != oid or obj.get("inventory_id") != expected_id
                       or obj.get("inventory_blob_sha256") != inventory_sha):
            object_bad = True
        if inv_ok and (entry is None or entry.get("object_kind") != kind):
            object_bad = True
        if inv_ok and entry is not None and any(obj.get(field) != entry.get(field)
                                                 for field in ("paired_object_key", "timeframe", "partition", "period")):
            object_bad = True
        if (not _is_nonnegative_int(obj.get("expected_size_bytes"))
                or not _is_nonnegative_int(obj.get("measured_size_bytes"))
                or not _is_sha256(obj.get("expected_sha256"))
                or not _is_sha256(obj.get("measured_sha256"))
                or obj.get("expected_size_bytes") != obj.get("measured_size_bytes")
                or obj.get("expected_sha256") != obj.get("measured_sha256")
                or obj.get("verification_status") != "VERIFIED"
                or type(obj.get("response_status")) is not int
                or not 200 <= obj.get("response_status") <= 299
                or not _is_text(obj.get("local_relative_path"))
                or type(obj.get("exclusive_create")) is not int or obj.get("exclusive_create") != 1
                or obj.get("failure_code") is not None):
            object_bad = True
        object_by_id[str(obj.get("object_id"))] = obj
    if len(objects) != 404 or len(object_by_key) != 404 or (inv_ok and set(object_by_key) != set(keys)):
        object_bad = True

    attempts_by_object, attempt_ids, attempt_bad = {}, set(), False
    for attempt in attempts:
        oid, aid = attempt.get("object_id"), attempt.get("attempt_id")
        if not _is_text(oid):
            attempt_bad = True
            continue
        attempts_by_object.setdefault(oid, []).append(attempt)
        if not _is_text(aid) or aid in attempt_ids:
            attempt_bad = True
        else:
            attempt_ids.add(aid)
    for obj in objects:
        oid = obj.get("object_id")
        history = attempts_by_object.get(oid, [])
        history.sort(key=lambda item: item.get("attempt_number") if type(item.get("attempt_number")) is int else -1)
        if not history or [a.get("attempt_number") for a in history] != list(range(1, len(history) + 1)):
            attempt_bad = True
        transferred = []
        for attempt in history:
            try:
                aid = derive_attempt_id(object_id=oid, attempt_number=attempt.get("attempt_number"),
                    workflow_run_id=attempt.get("workflow_run_id"), workflow_job_id=attempt.get("workflow_job_id"),
                    trigger_sha=attempt.get("trigger_sha"), requested_key=attempt.get("requested_key"))
            except (TypeError, ValueError):
                aid = None
            if aid != attempt.get("attempt_id") or attempt.get("requested_key") != obj.get("requested_key"):
                attempt_bad = True
            if not _is_text(attempt.get("started_at_utc")):
                attempt_bad = True
            if attempt.get("outcome") == "TRANSFERRED":
                transferred.append(attempt)
                if (not _is_text(attempt.get("finished_at_utc"))
                        or type(attempt.get("is_complete_object")) is not int or attempt.get("is_complete_object") != 1
                        or attempt.get("response_bytes_received") != obj.get("measured_size_bytes")
                        or attempt.get("complete_object_sha256") != obj.get("measured_sha256")
                        or attempt.get("expected_size_bytes") != obj.get("expected_size_bytes")
                        or attempt.get("expected_sha256") != obj.get("expected_sha256")):
                    attempt_bad = True
            elif attempt.get("outcome") in ("FAILED", "UNKNOWN", "STARTED"):
                if attempt.get("is_complete_object") == 1 or attempt.get("outcome") == "UNKNOWN":
                    attempt_bad = True
            else:
                attempt_bad = True
        if (len(transferred) != 1 or (transferred and obj.get("successful_attempt_id") != transferred[0].get("attempt_id"))
                or len(history) != obj.get("attempt_count")):
            attempt_bad = True
    if len(attempts) != 404 or len(attempt_ids) != len(attempts):
        attempt_bad = True
    if object_bad:
        errors.add("OBJECT_MEASUREMENT_INVALID")
    if attempt_bad:
        errors.add("OBJECT_ATTEMPT_HISTORY_INVALID")

    pair_by_id, pair_bad = {}, False
    for pair in pairs:
        pid = pair.get("pair_id")
        if not _is_text(pid) or pid in pair_by_id:
            pair_bad = True
            continue
        pair_by_id[pid] = pair
        zo, so = object_by_id.get(pair.get("zip_object_id")), object_by_id.get(pair.get("sidecar_object_id"))
        if zo is None or so is None:
            pair_bad = True
            continue
        if (zo.get("object_kind") != "ZIP" or so.get("object_kind") != "CHECKSUM_SIDECAR"
                or zo.get("paired_object_key") != so.get("object_key")
                or so.get("paired_object_key") != zo.get("object_key")
                or pid != _s1_id("pair1:", "T0-ARCHIVE-PAIR-V1", zo.get("object_id"), so.get("object_id"))
                or pair.get("measured_zip_size_bytes") != zo.get("measured_size_bytes")
                or pair.get("measured_zip_sha256") != zo.get("measured_sha256")
                or pair.get("measured_sidecar_size_bytes") != so.get("measured_size_bytes")
                or pair.get("measured_sidecar_sha256") != so.get("measured_sha256")
                or pair.get("sidecar_asserted_zip_sha256") != zo.get("measured_sha256")
                or pair.get("sidecar_assertion_matches") != 1 or pair.get("zip_crc_ok") != 1
                or pair.get("structural_ok") != 1 or pair.get("disposition") != "VERIFIED"):
            pair_bad = True
    if len(pairs) != 202 or len(pair_by_id) != 202:
        pair_bad = True

    members_by_pair, member_by_id, member_bad = {}, {}, False
    for member in members:
        pid, mid = member.get("pair_id"), member.get("member_id")
        members_by_pair.setdefault(pid, []).append(member)
        if not _is_text(mid) or mid in member_by_id:
            member_bad = True
        else:
            member_by_id[mid] = member
        msha = member.get("member_sha256")
        expected_mid = _s1_id("mem1:", "T0-CSV-MEMBER-V1", pid, member.get("member_path"),
                              bytes.fromhex(msha) if _is_sha256(msha) else b"")
        if (mid != expected_mid or not _is_text(member.get("member_path"))
                or not _is_nonnegative_int(member.get("member_size_bytes")) or not _is_sha256(msha)
                or member.get("encoding") != "UTF-8" or type(member.get("bom_present")) is not int or member.get("bom_present") != 0
                or member.get("newline") != "LF" or member.get("delimiter") != ","
                or type(member.get("header_present")) is not int or member.get("header_present") != 1
                or member.get("header_contract_id") != "T0_ARCHIVE_CSV_HEADER_V1"
                or member.get("parser_contract_id") != "T0_ARCHIVE_CSV_HEADER_V1"
                or not isinstance(member.get("parser_source_sha"), str) or _SHA1_RE.fullmatch(member.get("parser_source_sha", "")) is None
                or not _is_positive_int(member.get("data_row_count"))
                or not _is_nonnegative_int(member.get("first_open_time_ms"))
                or not _is_nonnegative_int(member.get("last_open_time_ms"))
                or member.get("first_open_time_ms") > member.get("last_open_time_ms")
                or member.get("disposition") != "VERIFIED"):
            member_bad = True
    if len(members) != 202 or len(member_by_id) != 202:
        member_bad = True
    for pid, pair in pair_by_id.items():
        if pair.get("member_count") != 1 or len(members_by_pair.get(pid, [])) != 1:
            member_bad = True
    if pair_bad:
        errors.add("ARCHIVE_PAIR_EVIDENCE_INVALID")
    if member_bad:
        errors.add("CSV_MEMBER_EVIDENCE_INVALID")

    rows_by_member, row_by_id, row_bad = {}, {}, False
    for row in rows:
        mid, rid = row.get("member_id"), row.get("source_row_id")
        rows_by_member.setdefault(mid, []).append(row)
        if not _is_text(rid) or rid in row_by_id:
            row_bad = True
        else:
            row_by_id[rid] = row
        raw_fields, raw_json = row.get("raw_fields"), row.get("raw_fields_json")
        raw_ok = isinstance(raw_fields, list) and len(raw_fields) == 12 and all(type(x) is str for x in raw_fields)
        if raw_ok:
            canonical = json.dumps(raw_fields, ensure_ascii=False, separators=(",", ":"))
            try:
                parsed_fields = json.loads(raw_json) if type(raw_json) is str else None
            except (json.JSONDecodeError, TypeError):
                parsed_fields = None
            raw_ok = parsed_fields == raw_fields and raw_json == canonical
        if not raw_ok:
            row_bad = True
            continue
        digest = _s1_hash("T0-RAW-CSV-ROW-V1", *raw_fields)
        physical, ordinal = row.get("physical_record_ordinal"), row.get("data_row_ordinal")
        member = member_by_id.get(mid)
        if (digest != row.get("raw_row_digest") or member is None
                or not _is_positive_int(physical) or not _is_positive_int(ordinal) or physical != ordinal + 1
                or row.get("disposition") != "ACCEPTED" or row.get("rejection_code") is not None
                or row.get("parser_contract_id") != "T0_ARCHIVE_CSV_HEADER_V1"
                or row.get("parser_source_sha") != (member.get("parser_source_sha") if member else None)
                or row.get("importer_contract_id") != "T0_ARCHIVE_IMPORTER_V1"
                or not isinstance(row.get("importer_source_sha"), str)
                or _SHA1_RE.fullmatch(row.get("importer_source_sha", "")) is None):
            row_bad = True
        if member is not None:
            expected_rid = _s1_id("row1:", "T0-SOURCE-ROW-V1", mid,
                                 physical if type(physical) is int else -1, bytes.fromhex(digest))
            if rid != expected_rid:
                row_bad = True
    if len(rows) != 202 or len(row_by_id) != 202:
        row_bad = True
    for mid, member in member_by_id.items():
        group = rows_by_member.get(mid, [])
        ordinals = sorted(r.get("data_row_ordinal") for r in group if type(r.get("data_row_ordinal")) is int)
        physicals = sorted(r.get("physical_record_ordinal") for r in group if type(r.get("physical_record_ordinal")) is int)
        if (len(group) != member.get("data_row_count") or ordinals != list(range(1, len(group) + 1))
                or physicals != list(range(2, len(group) + 2))):
            row_bad = True
    if row_bad:
        errors.add("SOURCE_ROW_PROVENANCE_INVALID")

    candles_by_natural, candle_by_value = {}, {}
    candle_bad, digest_bad = False, False
    for candle in candles:
        identity = _record_identity(candle)
        if identity is None or len(identity) != 5:
            candle_bad = True
            continue
        candles_by_natural.setdefault(identity, []).append(candle)
        fields = tuple(candle.get(name) for name in (
            "exchange", "market_type", "symbol", "timeframe", "open_time_ms",
            "open", "high", "low", "close", "volume", "available_at_ms", "availability_kind"))
        value_id = candle.get("candle_value_id")
        if value_id != _s1_id("cv1:", "T0-CANDLE-VALUE-V1", *fields):
            digest_bad = True
        if isinstance(value_id, str):
            candle_by_value[value_id] = candle
        tf, open_time = candle.get("timeframe"), candle.get("open_time_ms")
        interval = _TIMEFRAME_INTERVAL_MS.get(tf) if isinstance(tf, str) else None
        if (candle.get("exchange") != "binance" or candle.get("market_type") != "usdm"
                or candle.get("symbol") != "BTCUSDT" or interval is None
                or not _is_nonnegative_int(open_time) or open_time % interval != 0
                or not _is_nonnegative_int(candle.get("available_at_ms"))
                or candle.get("availability_kind") != "BAR_CLOSE_BOUNDARY"
                or candle.get("available_at_ms") != open_time + interval):
            candle_bad = True
        vals = [_decimal_value(candle.get(name)) for name in ("open", "high", "low", "close", "volume")]
        if any(v is None for v in vals):
            candle_bad = True
        else:
            op, high, low, close, volume = vals
            if op <= 0 or high <= 0 or low <= 0 or close <= 0 or volume < 0 or low > min(op, close) or high < max(op, close):
                candle_bad = True
        for row in rows:
            if row.get("natural_key") == identity:
                raw = row.get("raw_fields")
                if (not isinstance(raw, list) or len(raw) != 12
                        or raw[:6] != [str(open_time), candle.get("open"), candle.get("high"),
                                      candle.get("low"), candle.get("close"), candle.get("volume")]
                        or raw[6] != str(open_time + interval - 1 if interval else -1)):
                    row_bad = True
    if len(candles) != 202 or len(candles_by_natural) != 202:
        candle_bad = True
    if digest_bad:
        errors.add("CANDLE_VALUE_DIGEST_INVALID")
    if candle_bad:
        errors.add("CANDLE_OHLCV_CONSTRAINT_INVALID")
    if row_bad:
        errors.add("SOURCE_ROW_PROVENANCE_INVALID")

    links_by_source, links_by_natural, link_bad = {}, {}, False
    for link in links:
        source_id = link.get("source_row_id")
        if not _is_text(source_id):
            link_bad = True
            continue
        links_by_source.setdefault(source_id, []).append(link)
        identity = _record_identity(link)
        if identity is None:
            link_bad = True
            continue
        links_by_natural.setdefault(identity, []).append(link)
        expected_lid = _s1_id("lnk1:", "T0-CANDLE-PROVENANCE-LINK-V1",
            link.get("exchange"), link.get("market_type"), link.get("symbol"),
            link.get("timeframe"), link.get("open_time_ms"), source_id,
            link.get("duplicate_disposition"))
        row = row_by_id.get(source_id)
        candle_group = candles_by_natural.get(identity, [])
        if (link.get("link_id") != expected_lid
                or link.get("duplicate_disposition") not in ("UNIQUE", "IDENTICAL_DUPLICATE")
                or row is None or row.get("disposition") != "ACCEPTED"
                or row.get("natural_key") != identity or not candle_group
                or row.get("candle_value_id") not in {c.get("candle_value_id") for c in candle_group}
                or link.get("candle_value_id") != row.get("candle_value_id")):
            link_bad = True
    if len(links) != 202 or len(links_by_source) != 202:
        link_bad = True
    for rid in row_by_id:
        if len(links_by_source.get(rid, [])) != 1:
            link_bad = True
    for grouped in links_by_natural.values():
        ordered = sorted(grouped, key=lambda item: str(item.get("source_row_id")).encode("utf-8"))
        for index, link in enumerate(ordered):
            if link.get("duplicate_disposition") != ("UNIQUE" if index == 0 else "IDENTICAL_DUPLICATE"):
                link_bad = True
    if set(candles_by_natural) != set(links_by_natural):
        link_bad = True
    if link_bad:
        errors.add("CANDLE_PROVENANCE_LINK_INVALID")

    manifest, run = payload.get("coverage_manifest"), payload.get("run")
    run_bad = not isinstance(manifest, Mapping) or not isinstance(run, Mapping)
    if isinstance(manifest, Mapping):
        expected_counts = {
            "expected_object_count": len(objects), "expected_pair_count": len(pairs),
            "expected_member_count": len(members), "expected_row_count": len(rows),
            "expected_candle_count": len(candles), "expected_link_count": len(links)}
        if manifest.get("manifest_version") != "T0-COVERAGE-MANIFEST-V1":
            run_bad = True
        for name, actual in expected_counts.items():
            if not _is_nonnegative_int(manifest.get(name)) or manifest.get(name) != actual:
                run_bad = True
        for name in ("approved_gaps", "approved_extras"):
            entries = manifest.get(name)
            if not isinstance(entries, list):
                run_bad = True
                continue
            seen = set()
            for entry in entries:
                if not isinstance(entry, Mapping) or set(entry) != {"timeframe", "open_time_ms", "reason", "evidence_ref"}:
                    run_bad = True
                    continue
                tf, timestamp = entry.get("timeframe"), entry.get("open_time_ms")
                interval = _TIMEFRAME_INTERVAL_MS.get(tf) if isinstance(tf, str) else None
                if (interval is None or not _is_nonnegative_int(timestamp) or timestamp % interval != 0
                        or not _is_text(entry.get("reason")) or not _is_text(entry.get("evidence_ref"))):
                    run_bad = True
                marker = (tf, timestamp, entry.get("reason"), entry.get("evidence_ref"))
                if marker in seen:
                    run_bad = True
                seen.add(marker)
    if isinstance(run, Mapping):
        if (run.get("schema_contract_id") != "T0_STAGING_SCHEMA_V2"
                or run.get("status") != "CANDIDATE" or not _is_text(run.get("run_id"))):
            run_bad = True
    if len(objects) != 404 or len(pairs) != 202 or len(members) != 202:
        run_bad = True
    if any(code in errors for code in _S1_CODE_ORDER[:-1]):
        run_bad = True
    if run_bad:
        errors.add("RUN_ACCEPTANCE_INVARIANT_INVALID")


def validate_provenance(payload: Mapping[str, object]) -> ProvenanceValidationResult:
    """Dispatch legacy V1 and explicit S1 payloads; never silently downgrade."""
    if not isinstance(payload, Mapping):
        return _validate_v1(payload)
    version = payload.get("contract_version")
    has_s1_claim = any(key in payload for key in _S1_ENVELOPE_KEYS)
    if version is None and not has_s1_claim:
        return _validate_v1(payload)
    base = _validate_v1(payload)
    errors = set(base.error_codes)
    if version != _S1_VERSION or not _S1_ENVELOPE_KEYS.issubset(payload.keys()):
        errors.add("RUN_ACCEPTANCE_INVARIANT_INVALID")
    else:
        _s1_validate(payload, errors)
    ordered = tuple(code for code in _ERROR_CODE_ORDER if code in errors)
    return ProvenanceValidationResult(not ordered, ordered)


__all__ = (
    "ProvenanceValidationResult",
    "encode_t0enc1",
    "derive_attempt_id",
    "validate_provenance",
)
