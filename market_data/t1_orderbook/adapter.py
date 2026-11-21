"""Transport-neutral adapter result; no HTTP, sockets, retries, or background work."""

from dataclasses import dataclass

from .contract import OrderbookSnapshot
from .errors import ContractError
from .validation import validate_payload


@dataclass(frozen=True, slots=True)
class Unavailable:
    reason: str = "NO_PAYLOAD"


@dataclass(frozen=True, slots=True)
class Rejected:
    code: str
    message: str


def consume_payload(payload: bytes | None, *, now_ms: int) -> OrderbookSnapshot | Unavailable | Rejected:
    """Validate an already-obtained payload without acquiring it from any transport."""
    if payload is None:
        return Unavailable()
    try:
        return validate_payload(payload, now_ms=now_ms)
    except ContractError as exc:
        return Rejected(code=exc.code.value, message=str(exc))
