"""Pure metadata-only resource policy for synthetic archive intake.

This module deliberately performs no filesystem, archive, network, host-preflight,
or database I/O. Callers must enforce these decisions before performing I/O.
"""
from __future__ import annotations

import math
import re
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any


RESOURCE_LIMITS = MappingProxyType({
    "response_bytes_total": 100 * 1024 * 1024,
    "zip_body_bytes": 64 * 1024 * 1024,
    "member_compressed_bytes": 64 * 1024 * 1024,
    "sidecar_bytes": 64 * 1024,
    "zip_entry_count": 1024,
    "member_uncompressed_bytes": 256 * 1024 * 1024,
    "zip_uncompressed_bytes": 512 * 1024 * 1024,
    "run_uncompressed_bytes": 4 * 1024 * 1024 * 1024,
    "compression_ratio": 100,
    "member_path_bytes": 1024,
})

_REQUIRED_METADATA = frozenset({
    "response_bytes_total",
    "zip_body_bytes",
    "sidecar_bytes",
    "zip_entry_count",
    "member_uncompressed_bytes",
    "zip_uncompressed_bytes",
    "run_uncompressed_bytes",
    "member_compressed_bytes",
    "member_path",
})
_INTEGER_FIELDS = (
    "response_bytes_total",
    "zip_body_bytes",
    "sidecar_bytes",
    "zip_entry_count",
    "member_uncompressed_bytes",
    "zip_uncompressed_bytes",
    "run_uncompressed_bytes",
    "member_compressed_bytes",
)
_MAX_INTEGER = (1 << 63) - 1
_TRANSIENT_HTTP_STATUSES = frozenset({408, 429})
_ALLOWED_COMPRESSION_METHODS = frozenset({0, 8})  # ZIP_STORED and ZIP_DEFLATED
_DRIVE_PATH_RE = re.compile(r"^[A-Za-z]:")


def validate_resource_metadata(metadata: Mapping[str, Any]) -> tuple[str, ...]:
    """Return stable error codes for invalid or over-budget ZIP metadata.

    The function is fail-closed: malformed mappings, absent fields, booleans,
    floats, negative values and integers outside the supported signed range
    are rejected. It consumes caller-supplied metadata only.
    """
    if not isinstance(metadata, Mapping):
        return ("RESOURCE_METADATA_INVALID",)

    errors: set[str] = set()
    if not _REQUIRED_METADATA.issubset(metadata.keys()):
        errors.add("RESOURCE_METADATA_MISSING")
    if set(metadata.keys()) != _REQUIRED_METADATA:
        errors.add("RESOURCE_METADATA_FIELDS_INVALID")

    values: dict[str, int] = {}
    for field in _INTEGER_FIELDS:
        value = metadata.get(field)
        if type(value) is not int or value < 0 or value > _MAX_INTEGER:
            errors.add("RESOURCE_METADATA_INVALID")
        else:
            values[field] = value
            ceiling = RESOURCE_LIMITS.get(field)
            if ceiling is not None and value > ceiling:
                errors.add(field.upper() + "_EXCEEDED")

    path = metadata.get("member_path")
    if not isinstance(path, str) or not path:
        errors.add("MEMBER_PATH_INVALID")
    else:
        try:
            path_size = len(path.encode("utf-8"))
        except UnicodeEncodeError:
            errors.add("MEMBER_PATH_INVALID")
        else:
            if path_size > RESOURCE_LIMITS["member_path_bytes"]:
                errors.add("MEMBER_PATH_TOO_LONG")

    compressed = values.get("member_compressed_bytes")
    uncompressed = values.get("member_uncompressed_bytes")
    if compressed == 0 and uncompressed is not None and uncompressed > 0:
        errors.add("COMPRESSED_SIZE_INVALID")
    elif compressed is not None and compressed > 0 and uncompressed is not None:
        if uncompressed > compressed * RESOURCE_LIMITS["compression_ratio"]:
            errors.add("COMPRESSION_RATIO_EXCEEDED")

    return tuple(sorted(errors))


def classify_zip_member(
    metadata: Mapping[str, Any],
    seen_paths: tuple[str, ...] = (),
) -> str:
    """Classify a ZIP member from supplied metadata without opening an archive."""
    if not isinstance(metadata, Mapping):
        return "MEMBER_METADATA_INVALID"

    path = metadata.get("path")
    if not isinstance(path, str) or not path:
        return "INVALID_PATH"
    if "\x00" in path:
        return "NUL_PATH"
    if "\\" in path:
        return "BACKSLASH_PATH"
    if path.startswith("/") or path.startswith("//"):
        return "ABSOLUTE_PATH"
    if _DRIVE_PATH_RE.match(path):
        return "DRIVE_PATH"

    parts = path.split("/")
    if any(part == ".." for part in parts):
        return "PATH_TRAVERSAL"
    if any(part in ("", ".") for part in parts):
        return "INVALID_PATH"
    if path in seen_paths:
        return "DUPLICATE_PATH"

    if metadata.get("is_symlink") is True:
        return "SYMLINK"
    if metadata.get("encrypted") is True:
        return "ENCRYPTED"

    method = metadata.get("compression_method", 0)
    if type(method) is not int or method not in _ALLOWED_COMPRESSION_METHODS:
        return "UNSUPPORTED_COMPRESSION"

    if not path.lower().endswith(".csv"):
        return "UNSUPPORTED_MEMBER_TYPE"
    return "ACCEPT"


def retry_delay_seconds(
    attempt: int,
    status_code: int | None = None,
    transient_error: bool = False,
    retry_after_seconds: int | float | None = None,
) -> int | float | None:
    """Return bounded delay for a retry, or None when the failure is final."""
    if type(attempt) is not int or attempt < 1 or attempt >= 3:
        return None

    transient_status = (
        type(status_code) is int
        and (status_code in _TRANSIENT_HTTP_STATUSES or 500 <= status_code <= 599)
    )
    if not transient_error and not transient_status:
        return None

    if retry_after_seconds is not None:
        if (
            isinstance(retry_after_seconds, bool)
            or not isinstance(retry_after_seconds, (int, float))
            or not math.isfinite(retry_after_seconds)
            or retry_after_seconds < 0
            or retry_after_seconds > 10
        ):
            return None
        return retry_after_seconds

    return 2 if attempt == 1 else 10


def validate_concurrency(network_active: int, zip_active: int) -> bool:
    """Allow exactly one active network request and one ZIP operation."""
    return (
        type(network_active) is int
        and type(zip_active) is int
        and network_active == 1
        and zip_active == 1
    )


__all__ = (
    "RESOURCE_LIMITS",
    "classify_zip_member",
    "retry_delay_seconds",
    "validate_concurrency",
    "validate_resource_metadata",
)
