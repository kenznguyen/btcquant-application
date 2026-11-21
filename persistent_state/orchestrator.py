"""Manual session orchestration over the existing persistent-state components.

The orchestrator prepares a session to READY. It never starts strategy workers.
RUNNING requires a separate authenticated operator approval and a fresh risk check.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from persistent_state.contracts import SessionRecord, SessionStatus
from persistent_state.evidence import (
    EvidenceBinding, OperatorResumeConfirmation, PreflightAttestation,
    ReadyEvidenceBundle, RestoreAttestation, RiskReadinessAttestation,
    validate_preflight_attestation,
)
from persistent_state.recovery import (
    RecoveryResult, Reducer, RecoveryValidationError, recover_repository_state,
)
from persistent_state.repository import FencingToken, StateRepository


@dataclass(frozen=True, slots=True)
class OperatorApproval:
    operator_id: str
    confirmation_id: str
    confirmed_at_ms: int
    risk_attestation: RiskReadinessAttestation

    def __post_init__(self) -> None:
        if not isinstance(self.operator_id, str) or not self.operator_id.strip():
            raise ValueError("operator_id must be non-empty")
        if not isinstance(self.confirmation_id, str) or not self.confirmation_id.strip():
            raise ValueError("confirmation_id must be non-empty")
        if type(self.confirmed_at_ms) is not int or self.confirmed_at_ms < 0:
            raise ValueError("confirmed_at_ms must be an integer >= 0")


@dataclass(frozen=True, slots=True)
class SessionStartResult:
    session: SessionRecord
    fencing_token: FencingToken
    recovery: RecoveryResult | None
    blocked_reason: str | None = None


PreflightProvider = Callable[[SessionRecord, FencingToken], PreflightAttestation]
RestoreAttestationProvider = Callable[[SessionRecord, FencingToken, RecoveryResult], RestoreAttestation]
RiskReadinessProvider = Callable[[SessionRecord, FencingToken], RiskReadinessAttestation]
Clock = Callable[[], int]


class SessionOrchestrator:
    """Coordinates preflight, deterministic recovery, READY evidence and manual Resume."""

    def __init__(
        self,
        repository: StateRepository,
        *,
        reducer: Reducer,
        preflight_provider: PreflightProvider,
        restore_attestation_provider: RestoreAttestationProvider,
        risk_readiness_provider: RiskReadinessProvider,
        clock_ms: Clock,
        operator_approval_verifier: Callable[[OperatorApproval], bool],
    ) -> None:
        self.repository = repository
        self.reducer = reducer
        self.preflight_provider = preflight_provider
        self.restore_attestation_provider = restore_attestation_provider
        self.risk_readiness_provider = risk_readiness_provider
        self.clock_ms = clock_ms
        if not callable(operator_approval_verifier):
            raise ValueError("operator_approval_verifier must be callable")
        self.operator_approval_verifier = operator_approval_verifier

    def _advance(self, token, expected, target, **kwargs):
        return self.repository.advance_session(
            token, expected_status=expected, new_status=target,
            at_ms=self.clock_ms(), **kwargs,
        )

    def start(self, session: SessionRecord) -> SessionStartResult:
        """Claim a new manual session and stop at READY; never auto-resume."""
        if not isinstance(session, SessionRecord) or session.status is not SessionStatus.START_REQUESTED:
            raise ValueError("start requires a START_REQUESTED SessionRecord")
        if session.initiator != "MANUAL":
            raise ValueError("session start must be explicitly initiated by MANUAL operator action")

        token = self.repository.claim_writer(session)
        self._advance(token, SessionStatus.START_REQUESTED, SessionStatus.PREFLIGHT)
        current = self.repository.get_session(session.session_id)
        try:
            preflight = self.preflight_provider(current, token)
            validate_preflight_attestation(
                current, fencing_generation=token.fencing_generation,
                preflight=preflight,
            )
        except Exception as exc:
            blocked = self._advance(token, SessionStatus.PREFLIGHT, SessionStatus.BLOCKED_PREFLIGHT)
            return SessionStartResult(
                session=blocked, fencing_token=token, recovery=None,
                blocked_reason=f"PREFLIGHT_BLOCKED:{type(exc).__name__}",
            )

        self._advance(
            token, SessionStatus.PREFLIGHT, SessionStatus.RESTORING,
            preflight_attestation=preflight,
        )
        current = self.repository.get_session(session.session_id)
        try:
            recovery = recover_repository_state(
                self.repository, session.account_scope_id, self.reducer,
            )
            restore = self.restore_attestation_provider(current, token, recovery)
            risk = self.risk_readiness_provider(current, token)
            bundle = ReadyEvidenceBundle(
                preflight=preflight, restore=restore, risk=risk,
            )
            ready = self.repository.advance_session(
                token, expected_status=SessionStatus.RESTORING,
                new_status=SessionStatus.READY, at_ms=self.clock_ms(),
                readiness_evidence=bundle,
            )
            return SessionStartResult(
                session=ready, fencing_token=token, recovery=recovery,
            )
        except Exception as exc:
            blocked = self._advance(token, SessionStatus.RESTORING, SessionStatus.BLOCKED_RESTORE)
            reason = "RESTORE_BLOCKED:" + (
                "RECOVERY_VALIDATION" if isinstance(exc, RecoveryValidationError)
                else type(exc).__name__
            )
            return SessionStartResult(
                session=blocked, fencing_token=token, recovery=None,
                blocked_reason=reason,
            )

    def prepare_resume(self, fencing_token: FencingToken) -> RiskReadinessAttestation:
        """Run a fresh risk check before presenting a Resume confirmation to the operator."""
        session = self.repository.get_session(fencing_token.session_id)
        if session.status is not SessionStatus.READY:
            raise ValueError("only a READY session can prepare Resume")
        risk = self.risk_readiness_provider(session, fencing_token)
        if not isinstance(risk, RiskReadinessAttestation) or not risk.passed:
            raise ValueError("fresh risk readiness attestation is required for Resume")
        if risk.kill_switch_latched or not risk.ledger_reconciled:
            raise ValueError("Kill Switch or unreconciled risk state blocks Resume")
        return risk

    def resume(self, fencing_token: FencingToken, approval: OperatorApproval) -> SessionRecord:
        """Enter RUNNING only after verified operator approval of a fresh risk check."""
        if not isinstance(approval, OperatorApproval):
            raise ValueError("explicit OperatorApproval is required; restart never resumes automatically")
        if not isinstance(approval.risk_attestation, RiskReadinessAttestation):
            raise ValueError("OperatorApproval must include the fresh risk attestation shown before confirmation")
        if not self.operator_approval_verifier(approval):
            raise PermissionError("operator approval was not authenticated")
        confirmation = OperatorResumeConfirmation(
            binding=approval.risk_attestation.binding,
            operator_id=approval.operator_id,
            confirmation_id=approval.confirmation_id,
            confirmed_at_ms=approval.confirmed_at_ms,
            risk_attestation=approval.risk_attestation,
        )
        return self.repository.advance_session(
            fencing_token, expected_status=SessionStatus.READY,
            new_status=SessionStatus.RUNNING, at_ms=self.clock_ms(),
            resume_confirmation=confirmation,
        )


__all__ = [
    "OperatorApproval", "SessionOrchestrator", "SessionStartResult",
]
