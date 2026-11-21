"""Immutable account-level risk evidence and its Provider boundary.

This module is pure: it performs no I/O and selects no account data source.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Protocol


_SCHEMA_VERSION = 1
_NON_NEGATIVE_DECIMAL = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")
_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
_QUOTE_ASSET = re.compile(r"^[A-Z][A-Z0-9]{1,11}$")


def _nonempty(name: str, value: object, *, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(f"{name} must be a non-empty string of at most {maximum} characters")
    return value


def _timestamp(name: str, value: object) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be an integer >= 0")
    return value


def _decimal(name: str, value: object, *, positive: bool = False) -> str:
    if not isinstance(value, str) or len(value) > 128 or not _NON_NEGATIVE_DECIMAL.fullmatch(value):
        raise ValueError(f"{name} must be a canonical non-negative decimal string")
    if positive and value.strip("0.") == "":
        raise ValueError(f"{name} must be strictly positive")
    return value


@dataclass(frozen=True, slots=True)
class AccountRiskProvenance:
    """Verifiable lineage for the exact source payload used to build a snapshot."""

    provider_id: str
    source_id: str
    source_snapshot_id: str
    source_version: str
    source_payload_sha256: str

    def __post_init__(self) -> None:
        _nonempty("provider_id", self.provider_id)
        _nonempty("source_id", self.source_id)
        _nonempty("source_snapshot_id", self.source_snapshot_id)
        _nonempty("source_version", self.source_version)
        if not isinstance(self.source_payload_sha256, str) or not _SHA256.fullmatch(
            self.source_payload_sha256
        ):
            raise ValueError("source_payload_sha256 must use sha256:<64 lowercase hex characters>")


@dataclass(frozen=True, slots=True)
class AccountRiskSnapshot:
    """One internally consistent account-level risk snapshot.

    Monetary values are exact quote-asset decimal strings. Loss fields are
    non-negative magnitudes; gross exposure never nets LONG against SHORT.
    """

    snapshot_id: str
    schema_version: int
    account_scope_id: str
    session_id: str
    fencing_generation: int
    generated_at_ms: int
    as_of_ms: int
    quote_asset: str
    account_equity_quote: str
    gross_exposure_quote: str
    reserved_margin_quote: str
    drawdown_quote: str
    daily_loss_quote: str
    provenance: AccountRiskProvenance
    verified: bool
    ledger_reconciled: bool

    def __post_init__(self) -> None:
        _nonempty("snapshot_id", self.snapshot_id)
        if type(self.schema_version) is not int or self.schema_version != _SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal supported version {_SCHEMA_VERSION}")
        _nonempty("account_scope_id", self.account_scope_id)
        _nonempty("session_id", self.session_id)
        if type(self.fencing_generation) is not int or self.fencing_generation < 1:
            raise ValueError("fencing_generation must be an integer >= 1")
        generated = _timestamp("generated_at_ms", self.generated_at_ms)
        as_of = _timestamp("as_of_ms", self.as_of_ms)
        if as_of > generated:
            raise ValueError("as_of_ms cannot be later than generated_at_ms")
        if not isinstance(self.quote_asset, str) or not _QUOTE_ASSET.fullmatch(self.quote_asset):
            raise ValueError("quote_asset must be an uppercase asset code")
        _decimal("account_equity_quote", self.account_equity_quote, positive=True)
        for field in (
            "gross_exposure_quote", "reserved_margin_quote",
            "drawdown_quote", "daily_loss_quote",
        ):
            _decimal(field, getattr(self, field))
        if not isinstance(self.provenance, AccountRiskProvenance):
            raise ValueError("typed AccountRiskProvenance is required")
        if type(self.verified) is not bool:
            raise ValueError("verified must be boolean")
        if type(self.ledger_reconciled) is not bool:
            raise ValueError("ledger_reconciled must be boolean")


class AccountRiskSnapshotProvider(Protocol):
    """Read-only port; implementations must fail closed on unavailable evidence."""

    def read_snapshot(
        self,
        *,
        account_scope_id: str,
        session_id: str,
        fencing_generation: int,
    ) -> AccountRiskSnapshot:
        """Return a snapshot bound to the exact account, session and fencing generation."""
        ...


__all__ = [
    "AccountRiskProvenance",
    "AccountRiskSnapshot",
    "AccountRiskSnapshotProvider",
]
