"""Deterministic synthetic fixtures; never exchange or production evidence."""

import hashlib
import json
from typing import Any

SYNTHETIC_FIXTURE = True


def canonical_snapshot_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def synthetic_valid_payload(now_ms: int = 10_000) -> dict[str, Any]:
    bids = [[f"{100 - index}.25", "1.5"] for index in range(20)]
    asks = [[f"{101 + index}.25", "2.5"] for index in range(20)]
    payload: dict[str, Any] = {
        "contractVersion": "T1_T2_ORDERBOOK_V1",
        "symbol": "BTCUSDT",
        "market": "BINANCE_USDM_PERPETUAL",
        "bids": bids,
        "asks": asks,
        "snapshotLastUpdateId": 100,
        "firstAppliedU": 100,
        "lastAppliedU": 120,
        "sourceTimestampMs": now_ms - 100,
        "observedAtMs": now_ms - 50,
        "decisionWatermark": 120,
        "generation": 1,
        "snapshotId": "",
        "continuity": "VERIFIED",
        "freshness": "FRESH",
        "depth": {"bids": 20, "asks": 20},
        "complete": True,
    }
    unsigned = dict(payload)
    unsigned.pop("snapshotId")
    payload["snapshotId"] = "sha256:" + hashlib.sha256(
        canonical_snapshot_bytes(unsigned)
    ).hexdigest()
    return payload
