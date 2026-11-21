"""Stable typed failures for the T1 orderbook consumer boundary."""

from enum import Enum


class ErrorCode(str, Enum):
    PAYLOAD_TOO_LARGE = "PAYLOAD_TOO_LARGE"
    MALFORMED_JSON = "MALFORMED_JSON"
    UNSUPPORTED_VERSION = "UNSUPPORTED_VERSION"
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"
    INVALID_DECIMAL = "INVALID_DECIMAL"
    INVALID_BOOK = "INVALID_BOOK"
    INVALID_SEQUENCE = "INVALID_SEQUENCE"
    STALE_SNAPSHOT = "STALE_SNAPSHOT"
    FUTURE_TIMESTAMP = "FUTURE_TIMESTAMP"
    DIGEST_MISMATCH = "DIGEST_MISMATCH"


class ContractError(ValueError):
    """A fail-closed rejection at the untrusted T1 payload boundary."""

    def __init__(self, code: ErrorCode, message: str) -> None:
        self.code = code
        super().__init__(message)
