"""Common, fail-closed risk admission for Core and AI paper proposals."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, localcontext
from typing import Any

from persistent_state.account_risk import (
    AccountRiskSnapshot, validate_snapshot_binding,
)
from persistent_state.contracts import RiskState, SessionStatus, StrategyId
from persistent_state.risk_policy import VersionedRiskPolicy
from risk_policy import ORDER_MARGIN_BUDGET_PCT


_ACTIONS = frozenset({"ENTRY", "ADD", "DCA", "REDUCE", "EXIT"})
_NEW_EXPOSURE_ACTIONS = frozenset({"ENTRY", "ADD", "DCA"})


@dataclass(frozen=True, slots=True)
class RiskProposal:
    proposal_id: str
    account_scope_id: str
    strategy_id: StrategyId
    action_kind: str
    direction: str
    requested_margin_quote: Any
    requested_gross_exposure_quote: Any | None = None

    def __post_init__(self) -> None:
        for name in ("proposal_id", "account_scope_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        try:
            strategy = self.strategy_id if isinstance(self.strategy_id, StrategyId) else StrategyId(self.strategy_id)
        except (TypeError, ValueError) as exc:
            raise ValueError("strategy_id must be CORE or AI") from exc
        object.__setattr__(self, "strategy_id", strategy)
        if self.action_kind not in _ACTIONS:
            raise ValueError("action_kind is not supported")
        if self.direction not in {"LONG", "SHORT"}:
            raise ValueError("direction must be LONG or SHORT")


@dataclass(frozen=True, slots=True)
class RiskAdmissionContext:
    account_scope_id: str
    session_id: str
    fencing_generation: int
    session_status: SessionStatus
    risk_state: RiskState | None
    account_risk_snapshot: AccountRiskSnapshot | None
    risk_policy: VersionedRiskPolicy | None
    now_ms: int
    shared_risk_engine_available: bool

    def __post_init__(self) -> None:
        if not isinstance(self.account_scope_id, str) or not self.account_scope_id.strip():
            raise ValueError("account_scope_id must be a non-empty string")
        if not isinstance(self.session_id, str) or not self.session_id.strip():
            raise ValueError("session_id must be a non-empty string")
        if type(self.fencing_generation) is not int or self.fencing_generation < 1:
            raise ValueError("fencing_generation must be an integer >= 1")
        if type(self.now_ms) is not int or self.now_ms < 0:
            raise ValueError("now_ms must be an integer >= 0")
        try:
            status = self.session_status if isinstance(self.session_status, SessionStatus) else SessionStatus(self.session_status)
        except (TypeError, ValueError) as exc:
            raise ValueError("session_status is invalid") from exc
        object.__setattr__(self, "session_status", status)
        if not isinstance(self.shared_risk_engine_available, bool):
            raise ValueError("shared_risk_engine_available must be boolean")


@dataclass(frozen=True, slots=True)
class RiskAdmissionResult:
    allowed: bool
    reason_code: str | None
    risk_policy_version: str | None


def _positive_decimal(value: Any) -> Decimal:
    if not isinstance(value, str) or not value or len(value) > 128:
        raise ValueError("risk amounts must be exact decimal strings")
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("risk amount is invalid") from exc
    if not number.is_finite() or number <= 0:
        raise ValueError("risk amount must be finite and positive")
    return number


def _non_negative_decimal(value: str) -> Decimal:
    try:
        number = Decimal(value)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("risk amount is invalid") from exc
    if not number.is_finite() or number < 0:
        raise ValueError("risk amount must be finite and non-negative")
    return number


class SharedRiskEngine:
    """One account snapshot and one versioned policy gate for Core and AI."""

    def __init__(self, *, order_margin_budget_pct: Decimal = ORDER_MARGIN_BUDGET_PCT) -> None:
        try:
            budget = order_margin_budget_pct if isinstance(order_margin_budget_pct, Decimal) else Decimal(str(order_margin_budget_pct))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError("order margin budget must be a finite Decimal") from exc
        if not budget.is_finite() or budget <= 0 or budget > 1:
            raise ValueError("order margin budget must be in (0, 1]")
        self.order_margin_budget_pct = budget

    @staticmethod
    def _deny(reason: str, risk_state: RiskState | None = None) -> RiskAdmissionResult:
        return RiskAdmissionResult(
            allowed=False,
            reason_code=reason,
            risk_policy_version=None if risk_state is None else risk_state.risk_policy_version,
        )

    def evaluate(
        self,
        proposal: RiskProposal,
        context: RiskAdmissionContext,
    ) -> RiskAdmissionResult:
        if not isinstance(proposal, RiskProposal) or not isinstance(context, RiskAdmissionContext):
            return self._deny("RISK_INPUT_INVALID")
        if proposal.account_scope_id != context.account_scope_id:
            return self._deny("RISK_SCOPE_MISMATCH", context.risk_state)
        if context.session_status is not SessionStatus.RUNNING:
            return self._deny("SESSION_NOT_READY", context.risk_state)
        if not context.shared_risk_engine_available:
            return self._deny("RISK_ENGINE_UNAVAILABLE", context.risk_state)

        risk_state = context.risk_state
        if not isinstance(risk_state, RiskState):
            return self._deny("RISK_STATE_UNAVAILABLE")
        if risk_state.account_scope_id != context.account_scope_id:
            return self._deny("RISK_SCOPE_MISMATCH", risk_state)
        if risk_state.kill_switch_latched:
            return self._deny("KILL_SWITCH_LATCHED", risk_state)

        snapshot = context.account_risk_snapshot
        policy = context.risk_policy
        if not isinstance(snapshot, AccountRiskSnapshot):
            return self._deny("ACCOUNT_RISK_SNAPSHOT_UNAVAILABLE", risk_state)
        if not isinstance(policy, VersionedRiskPolicy):
            return self._deny("RISK_POLICY_UNAVAILABLE", risk_state)
        if risk_state.risk_policy_version != policy.version:
            return self._deny("RISK_POLICY_VERSION_MISMATCH", risk_state)
        if snapshot.quote_asset != policy.quote_asset:
            return self._deny("RISK_QUOTE_ASSET_MISMATCH", risk_state)

        try:
            validate_snapshot_binding(
                snapshot,
                account_scope_id=context.account_scope_id,
                session_id=context.session_id,
                fencing_generation=context.fencing_generation,
            )
        except (TypeError, ValueError):
            return self._deny("ACCOUNT_RISK_SNAPSHOT_INVALID", risk_state)

        if snapshot.generated_at_ms > context.now_ms or snapshot.as_of_ms > context.now_ms:
            return self._deny("ACCOUNT_RISK_SNAPSHOT_FUTURE", risk_state)
        if context.now_ms - snapshot.as_of_ms > policy.max_snapshot_age_ms:
            return self._deny("ACCOUNT_RISK_SNAPSHOT_STALE", risk_state)

        try:
            equity = _positive_decimal(snapshot.account_equity_quote)
            reserved_margin = _non_negative_decimal(snapshot.reserved_margin_quote)
            state_reserved_margin = _non_negative_decimal(risk_state.reserved_margin_quote)
            drawdown = _non_negative_decimal(snapshot.drawdown_quote)
            daily_loss = _non_negative_decimal(snapshot.daily_loss_quote)
            gross_exposure = _non_negative_decimal(snapshot.gross_exposure_quote)
            requested_margin = _positive_decimal(proposal.requested_margin_quote)
        except (InvalidOperation, TypeError, ValueError):
            return self._deny("RISK_INPUT_INVALID", risk_state)

        if reserved_margin != state_reserved_margin or reserved_margin > equity:
            return self._deny("RISK_STATE_UNRECONCILED", risk_state)

        is_new_exposure = proposal.action_kind in _NEW_EXPOSURE_ACTIONS
        if is_new_exposure:
            if drawdown > Decimal(policy.max_drawdown_quote):
                return self._deny("DRAWDOWN_LIMIT_EXCEEDED", risk_state)
            if daily_loss > Decimal(policy.max_daily_loss_quote):
                return self._deny("DAILY_LOSS_LIMIT_EXCEEDED", risk_state)
            try:
                requested_exposure = _positive_decimal(proposal.requested_gross_exposure_quote)
            except (InvalidOperation, TypeError, ValueError):
                return self._deny("RISK_INPUT_INVALID", risk_state)
            with localcontext() as decimal_context:
                decimal_context.prec = 60
                if gross_exposure + requested_exposure > Decimal(policy.max_gross_exposure_quote):
                    return self._deny("GROSS_EXPOSURE_LIMIT_EXCEEDED", risk_state)
                if reserved_margin + requested_margin > equity:
                    return self._deny("INSUFFICIENT_MARGIN_CAPACITY", risk_state)
                order_limit = equity * self.order_margin_budget_pct
            if requested_margin > order_limit:
                return self._deny("ORDER_MARGIN_CAP_EXCEEDED", risk_state)

        return RiskAdmissionResult(
            allowed=True, reason_code=None,
            risk_policy_version=policy.version,
        )


__all__ = [
    "RiskAdmissionContext", "RiskAdmissionResult", "RiskProposal", "SharedRiskEngine",
]
