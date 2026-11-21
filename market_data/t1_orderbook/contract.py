"""Immutable, transport-neutral T1 orderbook snapshot DTO."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OrderbookSnapshot:
    contract_version: str
    symbol: str
    market: str
    bids: tuple[tuple[str, str], ...]
    asks: tuple[tuple[str, str], ...]
    snapshot_last_update_id: int
    first_applied_u: int
    last_applied_u: int
    source_timestamp_ms: int
    observed_at_ms: int
    decision_watermark: int
    generation: int
    snapshot_id: str
    continuity: str
    freshness: str
    depth_bids: int
    depth_asks: int
    complete: bool
