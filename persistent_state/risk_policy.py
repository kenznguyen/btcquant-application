"""Immutable, explicitly versioned account risk thresholds.

No production thresholds are defined here. A trusted configuration source must
construct this policy and supply every limit before admission can be evaluated.
"""
from __future__ import annotations

from dataclasses import dataclass
import re


_NON_NEGATIVE_DECIMAL = re.compile(r"^(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?$")
_ASSET = re.compile(r"^[A-Z][A-Z0-9]{1,11}$")


def _decimal_limit(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or len(value) > 128
        or not _NON_NEGATIVE_DECIMAL.fullmatch(value)
    ):
        raise ValueError(f"{name} must be an exact non-negative decimal string")
    return value


@dataclass(frozen=True, slots=True)
class VersionedRiskPolicy:
    """Complete quote-denominated risk limits; never populated with defaults."""

    version: str
    quote_asset: str
    max_snapshot_age_ms: int
    max_drawdown_quote: str
    max_daily_loss_quote: str
    max_gross_exposure_quote: str

    def __post_init__(self) -> None:
        if not isinstance(self.version, str) or not self.version.strip() or len(self.version) > 128:
            raise ValueError("risk policy version must be non-empty")
        if not isinstance(self.quote_asset, str) or not _ASSET.fullmatch(self.quote_asset):
            raise ValueError("quote_asset must be an uppercase asset code")
        if type(self.max_snapshot_age_ms) is not int or self.max_snapshot_age_ms <= 0:
            raise ValueError("max_snapshot_age_ms must be an integer greater than zero")
        for name in (
            "max_drawdown_quote", "max_daily_loss_quote",
            "max_gross_exposure_quote",
        ):
            _decimal_limit(name, getattr(self, name))


__all__ = ["VersionedRiskPolicy"]
