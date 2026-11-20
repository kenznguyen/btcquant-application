"""Pure, versioned contracts for the application-owned paper state.

This module performs validation only. It does not open files, create databases,
read market data, or perform trading actions.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum
import hashlib
import json
import re
from typing import Any


CONTRACT_SCHEMA_VERSION = 1
_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_DECIMAL_RE = re.compile(r"^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")


class StrategyId(str, Enum):
    CORE = "CORE"
    AI = "AI"


class SessionStatus(str, Enum):
    IDLE = "IDLE"
    START_REQUESTED = "START_REQUESTED"
    PREFLIGHT = "PREFLIGHT"
    RESTORING = "RESTORING"
    READY = "READY"
    RUNNING = "RUNNING"
    CHECKPOINTING = "CHECKPOINTING"
    CLOSED = "CLOSED"
    BLOCKED_PREFLIGHT = "BLOCKED_PREFLIGHT"
    BLOCKED_RESTORE = "BLOCKED_RESTORE"
    INTERRUPTED = "INTERRUPTED"
    FAILED_PERSISTENCE = "FAILED_PERSISTENCE"
    ABORTED = "ABORTED"


def _nonempty(name: str, value: Any, *, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(f"{name} must be a non-empty string of at most {maximum} characters")
    return value


def _integer(name: str, value: Any, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def _optional_integer(name: str, value: Any, *, minimum: int = 0) -> int | None:
    if value is None:
        return None
    return _integer(name, value, minimum=minimum)


def _strategy(value: StrategyId | str) -> StrategyId:
    try:
        return value if isinstance(value, StrategyId) else StrategyId(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("strategy_id must be CORE or AI") from exc


def _schema_version(value: int) -> int:
    _integer("schema_version", value, minimum=1)
    if value != CONTRACT_SCHEMA_VERSION:
        raise ValueError(f"unsupported schema_version: {value}")
    return value


def _decimal(name: str, value: Any, *, minimum: Decimal | None = None,
             allow_negative: bool = False) -> str:
    if not isinstance(value, str) or not _DECIMAL_RE.fullmatch(value):
        raise ValueError(f"{name} must be an exact decimal string")
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{name} must be a finite decimal") from exc
    if not number.is_finite():
        raise ValueError(f"{name} must be a finite decimal")
    if not allow_negative and number < 0:
        raise ValueError(f"{name} must not be negative")
    if minimum is not None and number < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    return value


def _sha256(name: str, value: Any) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{name} must use sha256:<64 lowercase hex characters>")
    return value


def _reject_binary_floats(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("binary floating-point values are not valid persisted state")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("canonical JSON object keys must be strings")
            _reject_binary_floats(item)
    elif isinstance(value, list):
        for item in value:
            _reject_binary_floats(item)


def canonical_json(value: Any) -> str:
    """Return deterministic JSON for an object payload without binary floats."""
    if not isinstance(value, dict):
        raise ValueError("canonical JSON payload must be an object")
    try:
        _reject_binary_floats(value)
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False, allow_nan=False,
        )
    except TypeError as exc:
        raise ValueError("payload must contain JSON-compatible values") from exc


def _canonical_json_object(name: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be canonical JSON text")
    try:
        parsed = json.loads(
            value,
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be valid JSON") from exc
    if not isinstance(parsed, dict) or canonical_json(parsed) != value:
        raise ValueError(f"{name} must be a canonical JSON object")
    return parsed


def _validate_versions(name: str, value: Any, *, values_must_be_strings: bool) -> dict[str, Any]:
    parsed = _canonical_json_object(name, value)
    if not parsed:
        raise ValueError(f"{name} must not be empty")
    for key, item in parsed.items():
        _nonempty(f"{name} key", key)
        if values_must_be_strings:
            _nonempty(f"{name}[{key}]", item)
        else:
            _integer(f"{name}[{key}]", item)
    return parsed


@dataclass(frozen=True, slots=True)
class SessionRecord:
    session_id: str
    account_scope_id: str
    status: SessionStatus
    started_at_ms: int
    initiator: str
    source_snapshot_id: str
    config_hash: str
    code_version: str
    last_committed_event_sequence: int
    ended_at_ms: int | None = None
    stop_requested_at_ms: int | None = None
    schema_version: int = CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _nonempty("session_id", self.session_id)
        _nonempty("account_scope_id", self.account_scope_id)
        try:
            status = self.status if isinstance(self.status, SessionStatus) else SessionStatus(self.status)
        except (TypeError, ValueError) as exc:
            raise ValueError("status is not a supported session lifecycle state") from exc
        object.__setattr__(self, "status", status)
        _integer("started_at_ms", self.started_at_ms)
        _nonempty("initiator", self.initiator)
        _nonempty("source_snapshot_id", self.source_snapshot_id)
        _sha256("config_hash", self.config_hash)
        _nonempty("code_version", self.code_version)
        _integer("last_committed_event_sequence", self.last_committed_event_sequence)
        _optional_integer("ended_at_ms", self.ended_at_ms)
        _optional_integer("stop_requested_at_ms", self.stop_requested_at_ms)
        if status is SessionStatus.CLOSED and self.ended_at_ms is None:
            raise ValueError("CLOSED session requires ended_at_ms")
        if self.ended_at_ms is not None and self.ended_at_ms < self.started_at_ms:
            raise ValueError("ended_at_ms cannot precede started_at_ms")
        if self.stop_requested_at_ms is not None and self.stop_requested_at_ms < self.started_at_ms:
            raise ValueError("stop_requested_at_ms cannot precede started_at_ms")
        if status is SessionStatus.CHECKPOINTING and self.stop_requested_at_ms is None:
            raise ValueError("CHECKPOINTING session requires stop_requested_at_ms")
        _schema_version(self.schema_version)


@dataclass(frozen=True, slots=True)
class EventRecord:
    event_id: str
    account_scope_id: str
    session_id: str
    event_sequence: int
    aggregate_version: int
    event_type: str
    strategy_id: StrategyId | None
    strategy_version: str | None
    created_at_ms: int
    recorded_at_ms: int
    payload_json: str
    market_snapshot_id: str | None = None
    candle_open_time_ms: int | None = None
    aggregate_id: str | None = None
    schema_version: int = CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in ("event_id", "account_scope_id", "session_id", "event_type"):
            _nonempty(name, getattr(self, name))
        if self.strategy_id is None:
            if self.strategy_version is not None:
                raise ValueError("strategy_version requires strategy_id")
        else:
            object.__setattr__(self, "strategy_id", _strategy(self.strategy_id))
            _nonempty("strategy_version", self.strategy_version)
        _integer("event_sequence", self.event_sequence, minimum=1)
        _integer("aggregate_version", self.aggregate_version, minimum=1)
        _integer("created_at_ms", self.created_at_ms)
        _integer("recorded_at_ms", self.recorded_at_ms)
        if self.recorded_at_ms < self.created_at_ms:
            raise ValueError("recorded_at_ms cannot precede created_at_ms")
        _canonical_json_object("payload_json", self.payload_json)
        if self.market_snapshot_id is not None:
            _nonempty("market_snapshot_id", self.market_snapshot_id)
        if self.aggregate_id is not None:
            _nonempty("aggregate_id", self.aggregate_id)
        _optional_integer("candle_open_time_ms", self.candle_open_time_ms)
        _schema_version(self.schema_version)


@dataclass(frozen=True, slots=True)
class StrategyState:
    account_scope_id: str
    strategy_id: StrategyId
    strategy_version: str
    last_evaluated_candle_open_time_ms: int | None
    cooldown_until_ms: int | None
    eligibility_state: str
    state_json: str
    schema_version: int = CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _nonempty("account_scope_id", self.account_scope_id)
        object.__setattr__(self, "strategy_id", _strategy(self.strategy_id))
        _nonempty("strategy_version", self.strategy_version)
        _optional_integer("last_evaluated_candle_open_time_ms", self.last_evaluated_candle_open_time_ms)
        _optional_integer("cooldown_until_ms", self.cooldown_until_ms)
        if self.cooldown_until_ms is not None:
            if self.last_evaluated_candle_open_time_ms is None:
                raise ValueError("cooldown requires a last evaluated candle")
            if self.cooldown_until_ms < self.last_evaluated_candle_open_time_ms:
                raise ValueError("cooldown cannot precede the last evaluated candle")
        _nonempty("eligibility_state", self.eligibility_state)
        _canonical_json_object("state_json", self.state_json)
        _schema_version(self.schema_version)


@dataclass(frozen=True, slots=True)
class PositionLedger:
    account_scope_id: str
    ledger_id: str
    strategy_id: StrategyId
    position_id: str
    symbol: str
    side: str
    status: str
    quantity: str
    average_entry_price: str
    realized_pnl_quote: str
    fees_quote: str
    aggregate_version: int
    schema_version: int = CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in ("account_scope_id", "ledger_id", "position_id", "symbol"):
            _nonempty(name, getattr(self, name))
        object.__setattr__(self, "strategy_id", _strategy(self.strategy_id))
        if self.side not in {"LONG", "SHORT"}:
            raise ValueError("side must be LONG or SHORT")
        if self.status not in {"OPEN", "CLOSED"}:
            raise ValueError("status must be OPEN or CLOSED")
        quantity = Decimal(_decimal("quantity", self.quantity))
        _decimal("average_entry_price", self.average_entry_price)
        _decimal("realized_pnl_quote", self.realized_pnl_quote, allow_negative=True)
        _decimal("fees_quote", self.fees_quote)
        if self.status == "OPEN" and (quantity <= 0 or Decimal(self.average_entry_price) <= 0):
            raise ValueError("OPEN position requires positive quantity and average entry price")
        if self.status == "CLOSED" and quantity != 0:
            raise ValueError("CLOSED position must have zero quantity")
        _integer("aggregate_version", self.aggregate_version, minimum=1)
        _schema_version(self.schema_version)


@dataclass(frozen=True, slots=True)
class SmartDCAState:
    account_scope_id: str
    strategy_id: StrategyId
    position_id: str
    dca_level: int
    max_dca_levels: int
    cumulative_added_quantity: str
    cumulative_added_notional_quote: str
    next_eligible_level: int | None
    next_trigger_price: str | None
    last_dca_event_id: str | None
    policy_version: str
    schema_version: int = CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _nonempty("account_scope_id", self.account_scope_id)
        strategy = _strategy(self.strategy_id)
        object.__setattr__(self, "strategy_id", strategy)
        if strategy is not StrategyId.CORE:
            raise ValueError("SmartDCAState is owned by Strategy Core only")
        _nonempty("position_id", self.position_id)
        _integer("max_dca_levels", self.max_dca_levels, minimum=1)
        _integer("dca_level", self.dca_level)
        if self.dca_level > self.max_dca_levels:
            raise ValueError("dca_level cannot exceed max_dca_levels")
        added_quantity = Decimal(_decimal("cumulative_added_quantity", self.cumulative_added_quantity))
        added_notional = Decimal(_decimal("cumulative_added_notional_quote", self.cumulative_added_notional_quote))
        if (self.dca_level == 0) != (added_quantity == 0 and added_notional == 0):
            raise ValueError("DCA level and cumulative additions do not reconcile")
        if (added_quantity == 0) != (added_notional == 0):
            raise ValueError("DCA quantity and notional must both be zero or positive")
        _optional_integer("next_eligible_level", self.next_eligible_level, minimum=1)
        if self.dca_level == self.max_dca_levels and self.next_eligible_level is not None:
            raise ValueError("no next DCA level is allowed after the configured maximum")
        if self.next_eligible_level is not None and self.next_eligible_level != self.dca_level + 1:
            raise ValueError("next_eligible_level must be the next sequential DCA level")
        if self.next_eligible_level is None:
            if self.next_trigger_price is not None:
                raise ValueError("next_trigger_price requires next_eligible_level")
        else:
            if self.next_trigger_price is None:
                raise ValueError("next DCA level requires next_trigger_price")
            _decimal("next_trigger_price", self.next_trigger_price, minimum=Decimal("0.0000000001"))
        if self.dca_level == 0 and self.last_dca_event_id is not None:
            raise ValueError("level zero cannot reference a DCA event")
        if self.dca_level > 0:
            _nonempty("last_dca_event_id", self.last_dca_event_id)
        _nonempty("policy_version", self.policy_version)
        _schema_version(self.schema_version)


@dataclass(frozen=True, slots=True)
class RiskState:
    account_scope_id: str
    kill_switch_latched: bool
    kill_switch_reason: str | None
    risk_policy_version: str
    reserved_margin_quote: str
    aggregate_version: int
    schema_version: int = CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _nonempty("account_scope_id", self.account_scope_id)
        if not isinstance(self.kill_switch_latched, bool):
            raise ValueError("kill_switch_latched must be boolean")
        if self.kill_switch_latched:
            _nonempty("kill_switch_reason", self.kill_switch_reason)
        elif self.kill_switch_reason is not None:
            raise ValueError("unlatched Kill Switch cannot retain a reason")
        _nonempty("risk_policy_version", self.risk_policy_version)
        _decimal("reserved_margin_quote", self.reserved_margin_quote)
        _integer("aggregate_version", self.aggregate_version, minimum=1)
        _schema_version(self.schema_version)


def derive_idempotency_key(
    *, account_scope_id: str, ledger_id: str, strategy_id: StrategyId | str,
    strategy_version: str, market_snapshot_id: str, candle_open_time_ms: int,
    action_kind: str, action_ordinal: int,
) -> str:
    dimensions = {
        "account_scope_id": _nonempty("account_scope_id", account_scope_id),
        "ledger_id": _nonempty("ledger_id", ledger_id),
        "strategy_id": _strategy(strategy_id).value,
        "strategy_version": _nonempty("strategy_version", strategy_version),
        "market_snapshot_id": _nonempty("market_snapshot_id", market_snapshot_id),
        "candle_open_time_ms": _integer("candle_open_time_ms", candle_open_time_ms),
        "action_kind": _nonempty("action_kind", action_kind),
        "action_ordinal": _integer("action_ordinal", action_ordinal),
    }
    encoded = canonical_json(dimensions).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class IdempotencyClaim:
    idempotency_key: str
    payload_hash: str
    account_scope_id: str
    ledger_id: str
    strategy_id: StrategyId
    strategy_version: str
    market_snapshot_id: str
    candle_open_time_ms: int
    action_kind: str
    action_ordinal: int
    outcome_event_id: str | None = None
    schema_version: int = CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _sha256("idempotency_key", self.idempotency_key)
        _sha256("payload_hash", self.payload_hash)
        object.__setattr__(self, "strategy_id", _strategy(self.strategy_id))
        expected = derive_idempotency_key(
            account_scope_id=self.account_scope_id, ledger_id=self.ledger_id,
            strategy_id=self.strategy_id, strategy_version=self.strategy_version,
            market_snapshot_id=self.market_snapshot_id,
            candle_open_time_ms=self.candle_open_time_ms,
            action_kind=self.action_kind, action_ordinal=self.action_ordinal,
        )
        if self.idempotency_key != expected:
            raise ValueError("idempotency_key does not match its logical intent dimensions")
        if self.outcome_event_id is not None:
            _nonempty("outcome_event_id", self.outcome_event_id)
        _schema_version(self.schema_version)


@dataclass(frozen=True, slots=True)
class Checkpoint:
    checkpoint_id: str
    account_scope_id: str
    session_id: str
    schema_version: int
    covered_event_sequence: int
    aggregate_versions_json: str
    payload_json: str
    payload_checksum: str
    created_at_ms: int
    source_snapshot_id: str
    strategy_versions_json: str
    config_hash: str

    def __post_init__(self) -> None:
        for name in ("checkpoint_id", "account_scope_id", "session_id", "source_snapshot_id"):
            _nonempty(name, getattr(self, name))
        _schema_version(self.schema_version)
        _integer("covered_event_sequence", self.covered_event_sequence)
        _integer("created_at_ms", self.created_at_ms)
        _validate_versions("aggregate_versions_json", self.aggregate_versions_json,
                           values_must_be_strings=False)
        _validate_versions("strategy_versions_json", self.strategy_versions_json,
                           values_must_be_strings=True)
        _canonical_json_object("payload_json", self.payload_json)
        _sha256("payload_checksum", self.payload_checksum)
        expected = "sha256:" + hashlib.sha256(self.payload_json.encode("utf-8")).hexdigest()
        if self.payload_checksum != expected:
            raise ValueError("checkpoint payload checksum mismatch")
        _sha256("config_hash", self.config_hash)


__all__ = [
    "CONTRACT_SCHEMA_VERSION", "Checkpoint", "EventRecord", "IdempotencyClaim",
    "PositionLedger", "RiskState", "SessionRecord", "SessionStatus",
    "SmartDCAState", "StrategyId", "StrategyState", "canonical_json",
    "derive_idempotency_key",
]
