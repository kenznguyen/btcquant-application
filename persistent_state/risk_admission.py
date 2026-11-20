"""Common, fail-closed risk admission for Core and AI paper proposals."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, localcontext
from typing import Any

from persistent_state.contracts import RiskState, SessionStatus, StrategyId
from risk_policy import ORDER_MARGIN_BUDGET_PCT


_ACTIONS = frozenset({"ENTRY", "ADD", "DCA", "REDUCE", "EXIT"})


@dataclass(frozen=True, slots=True)
class RiskProposal:
    proposal_id: str
    account_scope_id: str
    strategy_id: StrategyId
    action_kind: str
    direction: str
    requested_margin_quote: Any

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
    session_status: SessionStatus
    risk_state: RiskState | None
    account_equity_quote: Any
    ledger_reconciled: bool
    shared_risk_engine_available: bool

    def __post_init__(self) -> None:
        if not isinstance(self.account_scope_id, str) or not self.account_scope_id.strip():
            raise ValueError("account_scope_id must be a non-empty string")
        try:
            status = self.session_status if isinstance(self.session_status, SessionStatus) else SessionStatus(self.session_status)
        except (TypeError, ValueError) as exc:
            raise ValueError("session_status is invalid") from exc
        object.__setattr__(self, "session_status", status)
        if not isinstance(self.ledger_reconciled, bool):
            raise ValueError("ledger_reconciled must be boolean")
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


class SharedRiskEngine:
    """One shared gate; neither strategy can bypass session, risk or Kill Switch checks."""

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
        if not context.ledger_reconciled:
            return self._deny("RISK_STATE_UNRECONCILED", risk_state)
        if risk_state.kill_switch_latched:
            return self._deny("KILL_SWITCH_LATCHED", risk_state)

        try:
            equity = _positive_decimal(context.account_equity_quote)
            requested_margin = _positive_decimal(proposal.requested_margin_quote)
            reserved_margin = Decimal(risk_state.reserved_margin_quote)
        except (InvalidOperation, TypeError, ValueError):
            return self._deny("RISK_INPUT_INVALID", risk_state)

        if reserved_margin > equity:
            return self._deny("RISK_STATE_UNRECONCILED", risk_state)
        with localcontext() as decimal_context:
            decimal_context.prec = 60
            order_limit = equity * self.order_margin_budget_pct
        if requested_margin > order_limit:
            return self._deny("ORDER_MARGIN_CAP_EXCEEDED", risk_state)
        return RiskAdmissionResult(
            allowed=True, reason_code=None,
            risk_policy_version=risk_state.risk_policy_version,
        )


__all__ = [
    "RiskAdmissionContext", "RiskAdmissionResult", "RiskProposal", "SharedRiskEngine",
]
